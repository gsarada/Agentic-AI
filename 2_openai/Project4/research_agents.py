import asyncio
import time, datetime
import os
import random
from dotenv import load_dotenv
from get_llm_model import get_model
from openai import RateLimitError, OpenAIError
from agents.exceptions import MaxTurnsExceeded
from agents import (
    Agent, WebSearchTool, ModelSettings,
    OpenAIResponsesModel, OpenAIChatCompletionsModel, Runner, trace,
    gen_trace_id, AgentToolStreamEvent, function_tool
)
from research_models import SearchPlan, Report, SearchQueries
from instructions import PLANNER_INSTRUCTIONS, WRITER_INSTRUCTIONS, SEARCH_INSTRUCTIONS

load_dotenv(override=True)
deepseek_client, d_model_name = get_model("deepseek")
llama_client, l_model_name = get_model("llama")
openai_client, o_model_name = get_model("openai")
groq_client, g_model_name = get_model("groq")


llama_model = OpenAIChatCompletionsModel(model=l_model_name, openai_client=llama_client)
deepseek_model = OpenAIChatCompletionsModel(model=d_model_name, openai_client=deepseek_client)
openai_model = OpenAIResponsesModel(model=o_model_name, openai_client=openai_client)
groq_model = OpenAIChatCompletionsModel(model=g_model_name, openai_client=groq_client)


async def handle_stream(event: AgentToolStreamEvent) -> None:
    print(f"{event}")
    if event.type == "raw_response_event" and event.data.type == "response.output_text.delta":
        # This is your actual text token chunk
        print(event.data.delta, end="", flush=True)
    if event.type == "run_item_stream_event":
        item = event.data
        # Check if the item is a message tool call or final text block
        if hasattr(item, 'content') and item.content:
            for block in item.content:
                if block.type == "text":
                    print(f"\n[Message Block]: {block.text.value}")
                elif block.type == "tool_call":
                    print(f"\n[Tool Executed]: {block.tool_call.name} with args {block.tool_call.arguments}")
    if event.type == "agent_updated_stream_event":
        # Extract metadata about the active agent
        active_agent_name = event.data.name
        print(f"\n[System Alert] Active agent switched to: {active_agent_name}")

@function_tool
def writer_tool(report: dict):
    print(f"Report content received - {report}")
    content = report.content if report.content else ""
    file_path = f"docs/report-{datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')}"
    directory = os.path.dirname(file_path)
    try:
        # Create the directory if it doesn't exist
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(file_path, "wb", encoding="utf-8") as f:
            f.write(content)
    except Exception as e:
        print("Unable to write to file")

search_agent = Agent(name="Search Agent", instructions=SEARCH_INSTRUCTIONS,
                     tools=[WebSearchTool(search_context_size="low")], model=openai_model,
                     model_settings=ModelSettings(tool_choice="required")
                )

planner_agent = Agent(name="Planner Agent",
                      instructions=PLANNER_INSTRUCTIONS, model=deepseek_model, output_type=SearchPlan)

planner_tool = planner_agent.as_tool(tool_name="planner_tool",
                                     tool_description="A tool returning search queries to retrieve results",
                                     on_stream=handle_stream)

search_tool = search_agent.as_tool(tool_name="search_tool", parameters=SearchQueries,
                                   tool_description="A tool which returns a summary given a search query",
                                   max_turns=2,
                                   on_stream=handle_stream)

writer_agent = Agent(name="Writer Agent", instructions=WRITER_INSTRUCTIONS,
                     tools=[planner_tool, search_tool, writer_tool],
                     model_settings=ModelSettings(tool_choice="auto"),
                     model=groq_model,
                     #output_type=Report
                )

async def run(query:str, max_retries=5, initial_delay=2):
    retries = 0
    delay = initial_delay

    while retries < max_retries:
        try:
            with trace(workflow_name="research", trace_id=gen_trace_id()):
                stream = Runner.run_streamed(writer_agent, input=query)
                async for event in stream.stream_events():
                    if event.type == "raw_response_event" and event.data.type == "response.output_text.delta":
                        # Print the text chunk immediately
                        print(event.data.delta, end="", flush=True)
                    # yield chunk
        except RateLimitError as e:
            retries += 1
            if retries >= max_retries:
                print(f"[CRITICAL] Rate limit hit {max_retries} times. Aborting.")
                raise e

            # Calculate exponential backoff: delay * 2^retries
            # Add Jitter: randomized variance +/- 20% to prevent concurrent collision
            jitter = random.uniform(0.8, 1.2)
            sleep_time = delay * (2 ** (retries - 1)) * jitter
            print(f"[RateLimit] Hit 429. Backing off. Sleeping for {sleep_time:.2f}s...")

            time.sleep(sleep_time)
        except MaxTurnsExceeded as e:
            print("[System Warning]: The agent hit the tool execution ceiling before finishing.")
            # Extract the partial context items or raw messages processed before the crash
            partial_history = e.run_context if hasattr(e, 'run_context') else "Loop truncated."
        except OpenAIError as other_error:
            # Handle non-rate-limit API failures immediately without heavy backing off
            print(f"[API Error] Non-rate-limit exception: {other_error}")
            raise other_error

query = input("What topic would you like to research: ")
asyncio.run(run(query))
