import asyncio
from io import BytesIO
import requests
from PIL import Image
from dotenv import load_dotenv
from IPython.display import display, Markdown
from pydantic import BaseModel, Field
from typing import Literal
from autogen_agentchat.messages import TextMessage, MultiModalMessage
from autogen_core import Image as AGImage
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.tools.langchain import LangChainToolAdapter
from autogen_agentchat.agents import AssistantAgent
from autogen_core import CancellationToken
from autogen_core.tools import FunctionTool
from langchain_community.agent_toolkits import FileManagementToolkit
from langchain_community.utilities import SerpAPIWrapper
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.tools.mcp import StdioServerParams, mcp_server_tools

system_prompt = """You are an expert real estate research assistant specialized in agricultural land investments. Your task is to find and evaluate agricultural land listings near Hyderabad, India, within a 100 km radius.
1. Search Parameters
  When executing searches, you must strictly apply the following constraints:
  Location: Within a 100km radius of Hyderabad, Telangana, India or the location specified by user.
  Property Type: Agricultural land / farmland.
  Connectivity: Must have good road connectivity (e.g., facing or near National Highways, State Highways, or blacktop/tar roads).
  Timeframe: Listings must have been posted or updated within the last 48 hours.
2. Evaluation & Filtering
    Once listings are retrieved, analyze them based on the following criteria:
    Prevailing Market Rates: Compare the asking price with current real estate market trends for that specific mandal/district (e.g., Rangareddy, Medak, Yadadri Bhuvanagiri, Mahabubnagar).
    Feasibility: Reject listings with obvious red flags (e.g., landlocked, lacking clear access, severely overpriced).
3. Output Requirements
    Select the top 5 most appropriate listings that offer the best value based on prevailing rates. Present your findings in a clear, scannable format with the following details for each:
    Title: Brief description of the property (e.g., "5-Acre Farmland in Shadnagar").
    Location & Distance: Exact village/mandal and distance from Hyderabad (in km).
    Price: Price per acre or total price.
    Road Connectivity: Description of the approach road (e.g., 40ft Tar Road frontage).
    Justification: Why this is a good option based on prevailing area rates.Source/Link: 
    The date of the listing and a markdown link to the original source.Always maintain a professional, objective, and analytical tone. Base your data on up-to-date real estate trends and newly indexed search results."""
class ImageDescription(BaseModel):
    scene: str = Field(description="Briefly, the overall scene of the image")
    message: str = Field(description="The point that the image is trying to convey")
    style: str = Field(description="The artistic style of the image")
    orientation: Literal["portrait", "landscape", "square"] = Field(description="The orientation of the image")

async def image_reader(img_url):
    pil_image = Image.open(BytesIO(requests.get(img_url).content))
    img = AGImage(pil_image)
    multi_modal_message = MultiModalMessage(content=["Describe the content of this image in detail", img], source="User")
    model_client = OpenAIChatCompletionClient(model="gpt-4o-mini")

    describer = AssistantAgent(
        name="image_analyser",
        model_client=model_client,
        system_message="You are good at describing images",
        output_content_type=ImageDescription
    )

    response = await describer.on_messages([multi_modal_message], cancellation_token=CancellationToken())
    reply = response.chat_message.content
    print(f"ImageDescription: {reply}")

def search(query: str) -> str:
    """Use for:
    - latest information
    - news
    - current facts
    - information that changes over time
    """
    serper = SerpAPIWrapper()
    return serper.run(query)

async def agent_with_tools(message):
    search_tool = FunctionTool(
        func=search,
        description="Use to search for latest/current information.",
        strict=True  # <--- This solves the error
    )
    autogen_tools = [search_tool]
    file_mgmt_tools = FileManagementToolkit(root_dir="sandbox").get_tools()
    autogen_tools += [LangChainToolAdapter(tool) for tool in file_mgmt_tools]

    model_client = OpenAIChatCompletionClient(model="gpt-4o-mini")
    user_msg = TextMessage(content=message, source="User")
    search_agent = AssistantAgent(
        name="real_agent",
        model_client=model_client,
        system_message=system_prompt,
        tools=autogen_tools,
        reflect_on_tool_use=True
    )

    response = await search_agent.on_messages([user_msg], cancellation_token=CancellationToken())
    for message in response.inner_messages:
        print(message.content)
    display(Markdown(response.chat_message.content))
    message = TextMessage(content="OK proceed", source="user")
    result = await search_agent.on_messages([message], cancellation_token=CancellationToken())
    for message in result.inner_messages:
        print(message.content)
    display(Markdown(result.chat_message.content))

async def agent_team(source, dest):
    model_client = OpenAIChatCompletionClient(model="gpt-4o-mini")
    prompt = f"Find a two-way non-stop flight from {source} to {dest} in Dec 2026."
    search_tool = FunctionTool(
        func=search,
        description="Use to search for latest/current information.",
        strict=True  # <--- This solves the error
    )
    primary_agent = AssistantAgent(
        "primary",
        model_client=model_client,
        tools=[search_tool],
        system_message="You are a helpful AI research assistant who looks for promising and optimal deals on flights. Incorporate any feedback you receive. Ensure specific dates and trip requirements such are source and destination and one way or round trip are addressed. Output should contain airlines, departure/arrival times, trip price, lugguage allowance, meal included or not. Provide flight booking suggestions and optimal/feasible alternatives where possible",
    )

    evaluation_agent = AssistantAgent(
        "evaluator",
        model_client=model_client,
        system_message="You are an evaluator validating the responses from primary agent for the user query. If not satisfactory provide constructive feedback.Ensure you do not add 'APPROVE' when you have feedback. If response is satisfactory or all your feedback is addressed respond with 'APPROVE'. ",
    )

    text_termination = TextMentionTermination("APPROVE")

    team = RoundRobinGroupChat([primary_agent, evaluation_agent], termination_condition=text_termination,
                               max_turns=5, emit_team_events=True)
    async for message in team.run_stream(task=prompt, cancellation_token=CancellationToken(),
                                        output_task_messages=True):
        print(f"{message}\n\n")


async def agent_with_mcp_tool():
    fetch_mcp_server = StdioServerParams(command="uvx", args=["mcp-server-fetch",
                                                              "--ignore-robots-txt"], read_timeout_seconds=30)
    fetcher = await mcp_server_tools(fetch_mcp_server)

    # Create an agent that can use the fetch tool.
    model_client = OpenAIChatCompletionClient(model="gpt-4o-mini")
    agent = AssistantAgent(name="fetcher", model_client=model_client, tools=fetcher, reflect_on_tool_use=True)

    # Let the agent fetch the content of a URL and summarize it.
    result = await agent.run(task="Review https://www.linkedin.com/in/sarada-gummadi/  and summarize what you learn. Reply in Markdown.")
    print(result.messages[-1].content)


async def main(option):
    if option == "AW_SO":
     await image_reader("https://mitsloan.mit.edu/sites/default/files/styles/article_header_desktop/public/2026-02/agentic-ai-dobi.jpg.webp?h=7691f918&itok=VpvW7VKx")
    elif option == "AW_T":
        await agent_with_tools("Get me property listings around Hyderabad")
    elif option == "A_T":
        await agent_team("SIN", "HYD")
    elif option == "AW_MCP":
        await agent_with_mcp_tool()

if __name__ == "__main__":
    load_dotenv(override=True)
    asyncio.run(main("AW_MCP"))
