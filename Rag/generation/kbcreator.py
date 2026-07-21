import asyncio
from dotenv import load_dotenv
from get_llm_model import get_model
from tenacity import retry, wait_exponential
from prompts import (
    employees_prompt, products_prompt, contract_prompt, company_prompt
)
from agents import (
    Agent, Runner, trace, OpenAIChatCompletionsModel
)
from agents.mcp import MCPServerStdio
from pathlib import Path

load_dotenv(override=True)
HERE = Path(__file__).resolve().parent.parent
KB_PATH = HERE / "knowledge-base"
wait = wait_exponential(multiplier=1, min=10, max=240)

deepseek_client, d_model_name = get_model("deepseek")
llama_client, l_model_name = get_model("groq-llama")
qwen_client, q_model_name = get_model("qwen")
openai_client, o_model_name = get_model("groq")
gemini_client, g_model_name = get_model("gemini")


qwen_model = OpenAIChatCompletionsModel(model=q_model_name, openai_client=qwen_client)
llama_model = OpenAIChatCompletionsModel(model=l_model_name, openai_client=llama_client)
deepseek_model = OpenAIChatCompletionsModel(model=d_model_name, openai_client=deepseek_client)
openai_model = OpenAIChatCompletionsModel(model=o_model_name, openai_client=openai_client)
gemini_model = OpenAIChatCompletionsModel(model=g_model_name, openai_client=gemini_client)

async def create_content():
    with trace("kbcreate trace"):
        try:
            async with MCPServerStdio(
                    name="Filesystem Server via npx",
                    params={
                        "command": "npx",
                        "args": ["-y", "@modelcontextprotocol/server-filesystem", str(KB_PATH)],
                    },
            ) as server:
                company_agent = Agent(name="Corporate Communicator", instructions=company_prompt, model=qwen_model, mcp_servers=[server])
                products_agent = Agent(name="Product Manager", instructions=products_prompt, model=openai_model, mcp_servers=[server])
                employee_agent = Agent(name="HR Partner", instructions=employees_prompt, model=openai_model, mcp_servers=[server])
                contract_agent = Agent(name="Business Partner", instructions=contract_prompt, model=llama_model, mcp_servers=[server])
                #await Runner.run(company_agent, "Create company documents"),
                #await Runner.run(products_agent, "Create product documents"),
                #await Runner.run(employee_agent, "Create employee documents"),
                await Runner.run(contract_agent, "Create contracts documents")

        except Exception as e:
            print(f"Exception {e} occurred")
        finally:
            await server.cleanup()


asyncio.run(create_content())
