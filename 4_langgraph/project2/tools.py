import asyncio
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import SerpAPIWrapper, WikipediaAPIWrapper
from langchain_mcp_adapters.client import MultiServerMCPClient
import httpx
from langchain.tools import tool
from langchain_core.tools import Tool
from logger import logger

@tool
def search(query: str) -> str:
    """Use for:
    - latest information
    - news
    - current facts
    - information that changes over time
    Preferred over wiki for recent information."""
    serper = SerpAPIWrapper()
    return serper.run(query)

@tool
def email(sub: str, content: str) -> str:
    """Sends email notification with the given subject and content"""
    return "Email sent successfully"

@tool
def request_human_help(instructions: str) -> str:
    """Ask the user to do something in the browser window that you cannot do yourself, such as logging into a site,
    approving two factor authentication, passing a captcha. Explain exactly what you need them to do. The run pauses until
     they complete it"""
    return "The user says it is done. Continue with the task"

def get_wiki_tool():
    wikipedia = WikipediaAPIWrapper()
    wiki_tool = WikipediaQueryRun(api_wrapper=wikipedia)
    wiki_tool.description = """
        Use ONLY for encyclopedic and historical information.
        
        Good examples:
        - Explain Kubernetes
        - History of Linux
        - What is Reinforcement Learning
        
        DO NOT USE for:
        - Latest news
        - Current events
        - URLs
        - Website interaction
        - Real-time information
        
        Prefer Search for recent information.
        Prefer Playwright for URLs.
        """
    return wiki_tool

def mcp_connections(sandbox: str) -> dict:
    return {
        "playwright": {
            "transport": "http",
            "url": "http://localhost:3000/mcp"
        },
        "filesystem": {
            "transport": "stdio",
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", sandbox]
        },
    }

def get_mcp_client():
    # Configure a massive timeout window for heavy browser operations
    client = MultiServerMCPClient(mcp_connections("sandbox"))
    return client

def get_all_tools():
    wiki_tool = get_wiki_tool()
    tools = [search, email, wiki_tool, request_human_help]
    return tools
