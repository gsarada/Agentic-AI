from dotenv import load_dotenv
import os
import sqlite3
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.runnables import RunnableConfig
from IPython.display import Image, display
import gradio as gr
from langchain_openai import ChatOpenAI
from typing import TypedDict, Annotated
from langchain_core.tools import tool
from langchain_community.utilities import SerpAPIWrapper

# 1. define tools
load_dotenv()

system_prompt = """You are a helpful assistant. 
You have access to a web search tool and email tool. 

CRITICAL RULES FOR TOOL USE:
1. ONLY use the search tool if the user asks about current events, facts you do not know, or complex information requiring external verification.
2. DO NOT use the search tool for casual greetings (e.g., "hi", "hello"), pleasantries, or general knowledge that you already know.
3. If the user's intent is clear and you know the answer, respond directly without tools.
4. Use email tool only when user asks to notify"""

@tool
def search(query: str) -> str:
    """Searches the web for the query and returns the response"""
    serper = SerpAPIWrapper()
    return serper.run(query)

@tool
def email(sub: str, content: str) -> str:
    """Sends email notification with the given subject and content"""
    return "Email sent successfully"

# 2. Define state
class State(TypedDict):
    messages: Annotated[list, add_messages]

# 4. Define nodes
llm = ChatOpenAI(model="llama3.2", base_url="http://127.0.0.1:11434/v1", api_key="ollama")
llm_with_tools = llm.bind_tools([search, email])

def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke([{"role": "system", "content": system_prompt}]+state["messages"])]}

def build_graph():
    #3 Start the graph builder with the state
    graph_builder = StateGraph(State)


    #5 Add Nodes
    graph_builder.add_node("chatbot", chatbot)
    graph_builder.add_node("tools", ToolNode([search, email])) # This is required to perform the tool call

    # 5. Add edges
    graph_builder.add_edge(START, "chatbot")
    # tools_condition implicitly checks if the llm response contains tool_calls and is set to true
    graph_builder.add_conditional_edges("chatbot", tools_condition, {"tools", END})
    graph_builder.add_edge("tools", "chatbot")

    # The state holds only the conversations of single super-step (one complete run of the graph). So have to init memory
    #memory = MemorySaver()
    db_path = "memory.db"
    conn = sqlite3.connect(db_path)
    memory = SqliteSaver(conn)
    graph = graph_builder.compile(checkpointer=memory)

    display(Image(graph.get_graph(xray=True).draw_mermaid_png()))
    return graph

graph = build_graph()


def chat(user_input: str, history, thread_id):
    #this is to associate each session/conversation with a unique thread id so we can replay or time travel
    config = {"configurable": {"thread_id": thread_id}}
    response = graph.invoke({"messages": [{"role": "user", "content": user_input}]}, config=config)
    return response["messages"][-1].content

def get_history_string(thread_id:str):
    config: RunnableConfig = {"configurable": {"thread_id": thread_id}}
    try:
        # Retrieve state history using LangGraph's built-in method
        history = graph.get_state_history(config)

        # Format the history into a human-readable text block
        formatted_history = []
        for i, snapshot in enumerate(history):
            state_data = snapshot.next # Node info or checkpointer details
            values = snapshot.config["configurable"]
            formatted_history.append(
                f"--- Snapshot {i} ---\n"
                f"Checkpoint ID: {values.get('thread_ts')}\n"
                f"Next Nodes: {snapshot.next}\n"
                f"State Values:\n{snapshot.values}\n"
            )
        return "\n".join(formatted_history)
    except Exception as e:
        return f"Error retrieving history: {str(e)}"

thread_id = str(os.urandom(16).hex())
with gr.Blocks() as demo:

    with gr.Row():
        history_box = gr.Textbox(label="LangGraph State History", lines=20, interactive=False)

    refresh_btn = gr.Button("Refresh State History")

    # Update text box on button click
    refresh_btn.click(
        fn=get_history_string,
        inputs=[thread_id],
        outputs=[history_box]
    )
    gr.ChatInterface(chat, additional_inputs=[thread_id])

demo.launch()
