import os
from dotenv import load_dotenv
from openai import OpenAI
import json
from rich.console import Console

todos, completed = [], []
def create_todos(descriptions):
    print(len(descriptions))
    for desc in descriptions:
        print(desc)
        todos.append(desc)
    print(todos)
    completed.extend([{"completed": False, "description": ""}] * len(descriptions))
    return get_todos()

def get_todos():
    result = ""
    for index, desc in enumerate(todos):
        if completed[index].get("completed"):
            result += f"[green][strike]Todo-{index+1}: {desc}[/strike][/green]\n"
        else:
            result += f"Todo-{index+1}: {desc}\n"
    Console().print(result)
    return result

def mark_complete(index, completion_notes):
    if 1 <= index <= len(todos):
        completed[index-1]["completed"] = True
        completed[index-1]["completion_notes"] = completion_notes
        print(completed[index-1])
    else:
        print(f"No item at index {index-1}")
    return get_todos()

def handle_tool_calls(tool_calls):
    results = []
    for tool_call in tool_calls:
        tool_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        print(f"Tool name: {tool_name}, tool args - {arguments}")
        tool = globals().get(tool_name)
        result = tool(**arguments) if tool else {}

        results.append({"role": "tool", "content": json.dumps(result), "tool_call_id": tool_call.id})
    return results

create_todos_json = {
    "name": "create_todos",
    "description": "Add new todos from a list of descriptions and return the full list",
    "parameters": {
        "type": "object",
        "properties": {
            "descriptions": {
                'type': 'array',
                'items': {'type': 'string'},
                'title': 'Descriptions'
            }
        },
        "required": ["descriptions"],
        "additionalProperties": False
    },
}

mark_complete_json = {
    "name": "mark_complete",
    "description": "Mark complete the todo at the given position (starting from 1) and return the full list",
    "parameters": {
        "type": "object",
        "properties": {
            "index": {
                "type": "integer",
                "description": "Index of the todo item to be marked as complete"
            },
            "completion_notes": {
                "type": "string",
                "description": "Completion notes for the todo item"
            },
        },
        "required": ["index", "completion_notes"],
        "additionalProperties": False
    },
}

tools = [{"type": "function", "function": create_todos_json},
         {"type": "function", "function": mark_complete_json}]


system_message = """
You are given a problem to solve, by using your todo tools to plan a list of steps, then carrying out each step in turn.
Now use the todo list tools, create a plan, carry out the steps, and reply with the solution.
If any quantity isn't provided in the question, then include a step to come up with a reasonable estimate.
Provide your solution in Rich console markup without code blocks.
Do not ask the user questions or clarification; respond only with the answer after using your tools.
"""
user_message = """"
A train leaves Boston at 2:00 pm traveling 60 mph.
Another train leaves New York at 3:00 pm traveling 80 mph toward Boston.
When do they meet?
"""

def loop():
    messages = [{"role": "system", "content": system_message}, {"role": "user", "content": user_message}]
    api_key = os.getenv("GROQ_API_KEY")
    openai = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
    done = False
    while not done:
        response = openai.chat.completions.create(model="openai/gpt-oss-120b", messages=messages, tools=tools)
        message = response.choices[0].message
        print(message)
        # If the LLM wants to call a tool, we do that!
        if message.tool_calls:
            tool_calls = message.tool_calls
            results = handle_tool_calls(tool_calls)
            messages.append(message)
            messages.extend(results)
        else:
            done = True
    return message.content

load_dotenv(override=True)
answer = loop()
Console().print(answer)
