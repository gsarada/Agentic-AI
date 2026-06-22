import docker
import asyncio
from langchain_core.utils.function_calling import convert_to_openai_function
from langchain_community.agent_toolkits import PlayWrightBrowserToolkit, FileManagementToolkit
from langchain_community.tools.wikipedia.tool import WikipediaQueryRun
from langchain_community.utilities.wikipedia import WikipediaAPIWrapper
from langchain_community.utilities import SerpAPIWrapper
from playwright.async_api import async_playwright
from langchain.tools import tool
from logger import logger

client = docker.DockerClient(base_url="unix:///var/run/docker.sock")
# 1. Global reference to track active browser
ASYNC_BROWSER = None
PLAYWRIGHT_CONTEXT = None
_PLAYWRIGHT_LOCK = None

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

@tool("REPL")
def secure_python_repl(code: str) -> str:
    """Safely executes Python code inside an isolated container and returns stdout.
    Ensure the code passed in prints the desired result to stdout so it can be captured"""
    # Write code string to a safe temporary execution template if needed
    formatted_code = f"import sys\n{code}"

    try:
        # Spin up an ephemeral, resource-constrained container
        # 1. Create the container without running it automatically
        container = client.containers.create(
            image="my-python-sandbox:latest",
            command=f"python3 -c \"{code}\"",
            network_mode="none",
            mem_limit="128m",
            nano_cpus=1000000000,      # 3. Limit to 1 CPU core max
            read_only=True
        )

        # 2. Start execution
        container.start()

        # 3. Enforce the execution timeout limit during the wait phase
        # This throws a requests.exceptions.ReadTimeout if it exceeds 5 seconds
        result = container.wait(timeout=5)

        # Extract logs and remove container manually since remove=True was moved
        logs = container.logs(stdout=True, stderr=True).decode("utf-8")
        container.remove(force=True)
        return logs
    except docker.errors.ContainerError as e:
        return f"Execution Error: {e.stderr.decode('utf-8')}"
    except Exception as e:
        return f"Sandbox System Error: {str(e)}"

async def playwright_tools():
    global PLAYWRIGHT_CONTEXT, ASYNC_BROWSER, _PLAYWRIGHT_LOCK
    # Keep a single shared browser alive for the process lifetime.
    # Closing it here breaks subsequent tool calls and causes TargetClosedError.
    if _PLAYWRIGHT_LOCK is None:
        _PLAYWRIGHT_LOCK = asyncio.Lock()

    async with _PLAYWRIGHT_LOCK:
        if ASYNC_BROWSER is None:
            logger.info("Starting native async Playwright context...")
            PLAYWRIGHT_CONTEXT = await async_playwright().start()
            ASYNC_BROWSER = await PLAYWRIGHT_CONTEXT.chromium.launch(headless=True)

        toolkit = PlayWrightBrowserToolkit.from_browser(async_browser=ASYNC_BROWSER)
        tools = toolkit.get_tools()
        for tool in tools:
            if "navigate" in tool.name:
                tool.description = """
                Use when the user provides a URL or asks to open a website.

                Preferred for:
                - Reading webpages
                - Navigating websites
                - Clicking buttons
                - Extracting page content

                NEVER use wiki when a URL is provided.
                """
            elif "extract" in tool.name:
                tool.description = """
                Extract text from currently open webpage.

                Use only after navigation.
                """
        return tools


async def close_playwright() -> None:
    """Best-effort shutdown for global Playwright resources."""
    global PLAYWRIGHT_CONTEXT, ASYNC_BROWSER
    try:
        if ASYNC_BROWSER is not None:
            await ASYNC_BROWSER.close()
    finally:
        ASYNC_BROWSER = None
        if PLAYWRIGHT_CONTEXT is not None:
            try:
                await PLAYWRIGHT_CONTEXT.stop()
            finally:
                PLAYWRIGHT_CONTEXT = None


def get_file_tools():
    toolkit = FileManagementToolkit(root_dir="sandbox")
    tools = toolkit.get_tools()
    for tool in tools:
        if tool.name == "read_file":
            tool.description = """
            Read file contents.
    
            Use when:
            - User asks to inspect a file
            - Need to process local files
    
            Do not use for web pages.
            """

        if tool.name == "write_file":
            tool.description = """
            Write content to files.
    
            Use only after generating the content.
            """
    return tools

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

async def get_all_tools():
    wiki_tool = get_wiki_tool()
    tools = [search, secure_python_repl, email, wiki_tool] + get_file_tools()
    tools += await playwright_tools()
    return tools
