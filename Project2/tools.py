import json

get_chunks_for_topic_json = {
    "name": "get_chunks_for_topic",
    "description": "Use this tool to get the experience chunks relevant to the user question",
    "parameters": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Person name the agent is representing or interviewing"
            },
            "question": {
                "type": "string",
                "description": "The question asked by user"
            },
            "max_chunks": {
                "type": ["number", "null"],
                "description": "Max number of chunks to be returned. Default is 3"
            },
        },
        "required": ["name", "question", "max_chunks"],
        "additionalProperties": False
    },
    "strict": True
}

get_all_chunks_formatted_json = {
    "name": "get_all_chunks_formatted",
    "description": "Use this tool to get all the experience chunks of the person",
    "parameters": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Person name the agent is representing or interviewing"
            },
        },
        "required": ["name"],
        "additionalProperties": False
    },
    "strict": True
}

tools = [{"type": "function", "function": get_chunks_for_topic_json},
         {"type": "function", "function": get_all_chunks_formatted_json}]

def handle_tool_calls(tool_calls):
    results = []
    for tool_call in tool_calls:
        tool_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        print(f"Tool called: {tool_name}", flush=True)

        tool = globals().get(tool_name)
        result = tool(**arguments) if tool else {}

        results.append({"role": "tool", "content": json.dumps(result), "tool_call_id": tool_call.id})
    return results
