import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from get_llm_model import get_model
sys.path.append(str(Path(__file__).resolve().parent.parent))
from implementation.ingest import fetch_documents
from prompts import (
    gentest_prompt,
)
from agents import (
    Agent, Runner, OpenAIChatCompletionsModel
)
from agents.mcp import MCPServerStdio
from openai import RateLimitError
from tenacity import retry, wait_random_exponential, stop_after_attempt, retry_if_exception_type

load_dotenv(override=True)
HERE = Path(__file__).resolve().parent.parent
EVAL_PATH = HERE / "evaluation"

llama_client, l_model_name = get_model("groq")
llama_model = OpenAIChatCompletionsModel(model=l_model_name, openai_client=llama_client)

def chunk_documents(doc_list, chunk_size=5):
    for i in range(30, len(doc_list), chunk_size):
        print(f"processing documents {i} to {i+chunk_size-1}")
        yield doc_list[i:i + chunk_size]

@retry(
    stop=stop_after_attempt(4),
    wait=wait_random_exponential(min=10, max=50),
    retry=retry_if_exception_type(RateLimitError),
    reraise=True
)
async def create_tests():
    testdata = ""
    try:
            documents = fetch_documents()
            file_path = EVAL_PATH / "tests.jsonl"

            async with MCPServerStdio(
                    name="Filesystem Server via npx",
                    params={
                        "command": "npx",
                        "args": ["-y", "@modelcontextprotocol/server-filesystem", str(EVAL_PATH)],
                    },
            ) as server:
                for batch in chunk_documents(documents):
                    documents_text = "\n".join([f"{doc['text']}" for doc in batch])
                    system_prompt = gentest_prompt.replace("DOCUMENT_TEXT", documents_text)
                    testdata_agent = Agent(name="Retrieval Test Data Generator", instructions=system_prompt, model=llama_model, mcp_servers=[server])

                    await Runner.run(testdata_agent, f"Create test data and write to jsonl file")
                    #print(f"-------------\n {result} -----------\n")
                    #testdata += result.final_output


            #with open(file_path, "w") as f:
                #f.write(testdata)

    except Exception as e:
        print(f"Exception {e} occurred")
    finally:
        await server.cleanup()

asyncio.run(create_tests())
