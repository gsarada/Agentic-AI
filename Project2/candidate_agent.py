from pydantic import BaseModel
from tools import tools, handle_tool_calls
from get_llm_model import get_model, default_chat_model, default_eval_model

class Evaluation(BaseModel):
    acceptable: bool
    reasoning: list[str]
    feedback: list[str]

def chat_system_prompt(state):
    name = state.get("name")
    system_prompt = f"""You are acting as {name}, responding to questions on {name}'s personal website. \
    Your role is to represent {name} accurately and compellingly to potential employers or collaborators.
    ## Your context (use this as your ONLY source of truth)
    ### Experience summary: 
     {state.get("exp_summary")}
    ### LinkedIn profile:
     {state.get("profile_text")}
    ---
    ## Rules you must follow
    **Grounding:** Every answer must be built around specific examples, initiatives, metrics, or stories \
    from the context above. Do not use generic industry language as a substitute for real experience. \
    If a specific example exists in the context, use it. If it does not, say so honestly.
    **No hallucination:** Do not invent numbers, frameworks, tool names, or outcomes that are not \
    present in the context. If the question touches an area not covered in the context, say: \
    "That's not something I have direct experience with, but related to that I did..." and pivot to the closest real experience.
    **Answer structure:** 
    - Open directly with the most relevant experience or result — no filler phrases like "Great question" or "As {name}, I'm happy to share..."
    - Lead with impact (metric or outcome), then explain how it was achieved
    - Keep answers to 150–250 words unless the question explicitly needs more detail
    - Never end an answer with a question back to the interviewer    
    **Tone:** Speak in first person. Be direct, confident, and specific — 
    like a senior executive who knows their work well and doesn't need to pad answers.
    
    With this context, respond to the user's question, always staying in character as {name}."""
    return system_prompt

def evaluator_system_prompt(state):
    system_prompt = f"""You are a strict evaluator assessing whether an AI agent answered an interview or profile question on behalf of {state.get("name")}.
    ## Evaluation context
    ### Experience summary:
    {state.get("exp_summary")}
    ### LinkedIn profile:
    {state.get("profile_text")} 
    ---
    ## Evaluation criteria (check ALL of these) 
    1. **Grounding** — Does every specific claim (metric, tool, initiative, outcome) appear in the context above? Flag \
    any figure or fact not present in the context as a hallucination, even if it sounds plausible.    
    2. **Specificity** — Does the answer cite at least 2 named, concrete examples from the context (e.g. a specific \
    project, metric, or initiative)? Reject answers that only use generic cloud/tech leadership language.
    3. **Missed context** — Are there stronger, more relevant examples in the provided context that the agent failed to use? If yes, list them explicitly.  
    4. **Persona** — Does the agent speak in first person, open without filler phrases, and avoid ending with questions back to the user?
    5. **Accuracy** — Does the answer stay within what {state.get("name")} has actually done? No inflated claims, no role or scope beyond what's documented.
    6. **Utility** — Did the agent directly answer the question asked?
    ---

    ## Output format (always return this exact structure)
    
    ````json
    {{
      "acceptable": true or false,
      "reasoning": ["list any fabricated facts or figures, or empty list"],
      "feedback": ["specific, actionable instructions for the retry — reference exact context details"]
    }}
    ```"""
    return system_prompt
def evaluator_user_prompt(reply, message, history):
    user_prompt = f"""Conversation history:
    {history}
    User's question:
    {message}
    Agent's response:
    {reply}
    --- 
    Evaluate the response strictly against the criteria. Point the agent to the specific story, metric, or initiative from the context 
    it should use. Do not approve a response that relies on generic language where specific context exists."""
    return user_prompt

def run(message, history, state):
    history = [{"role": h["role"], "content": h["content"]} for h in history]
    messages = [{"role": "system", "content": chat_system_prompt(state)}] + history + [{"role": "user", "content": message}]
    openai, model_name = get_model(default_chat_model)
    done = False
    while not done:
        response = openai.chat.completions.create(model=model_name, messages=messages)
        message = response.choices[0].message

        # If the LLM wants to call a tool, we do that!

        if message.tool_calls:
            tool_calls = message.tool_calls
            results = handle_tool_calls(tool_calls)
            messages.append(message)
            messages.extend(results)
        else:
            done = True
    return message.content
def rerun(reply, message, history, eval_response, state):
    updated_system_prompt = chat_system_prompt(state) + f"""The user asked:{message}.--- You gave this answer which was rejected:{reply}---
    ## Why it was rejected Reasoning: {eval_response.reasoning}--- Feedback: {eval_response.feedback}"""
    messages = [{"role": "system", "content": updated_system_prompt}] + history + [{"role": "user", "content": message}]
    openai, model_name = get_model(default_chat_model)
    done = False
    while not done:
        response = openai.chat.completions.create(model=model_name, messages=messages)
        message = response.choices[0].message

        # If the LLM wants to call a tool, we do that!

        if message.tool_calls:
            tool_calls = message.tool_calls
            results = handle_tool_calls(tool_calls)
            messages.append(message)
            messages.extend(results)
        else:
            done = True
    return message.content

def evaluate(reply, message, history, state):
    messages = [{"role": "system", "content": evaluator_system_prompt(state)}] + \
               [{"role": "user", "content": evaluator_user_prompt(reply, message, history)}]
    openai, model_name = get_model(default_eval_model)
    done = False
    while not done:
        response = openai.chat.completions.parse(model=model_name, messages=messages, response_format=Evaluation)
        message = response.choices[0].message

        # If the LLM wants to call a tool, we do that!

        if message.tool_calls:
            tool_calls = message.tool_calls
            results = handle_tool_calls(tool_calls)
            messages.append(message)
            messages.extend(results)
        else:
            done = True
    return message.parsed

max_rounds = 1
def candidate_agent_chat(message, history, state):
    print(f"State in candidate agent - {state}")
    rounds = state["candidate_agent"]["rounds"]
    if rounds == max_rounds:
        reply = "You have reached limits. Please try again tomorrow", state
    reply = run(message, history, state)
    print(f'Chat Reply - {reply}')

    eval_response = evaluate(reply, message, history, state)
    print(f'Evaluation result - {eval_response}')
    if not eval_response.acceptable:
        print(f'Feedback - {eval_response.reasoning}')
        reply = rerun(reply, message, history, eval_response, state)
    else:
        print('The response is valid')
    return reply, state
