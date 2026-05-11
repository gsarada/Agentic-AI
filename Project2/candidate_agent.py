from pydantic import BaseModel
from tools import tools, handle_tool_calls
from get_llm_model import get_model

class Evaluation(BaseModel):
    acceptable: bool
    reasoning: str
    feedback: str

name = "saradag"
eval_model = "gemini"
run_model = "ollama-local"

def chat_system_prompt():
    system_prompt = f"""You are acting as {name}, responding to questions on {name}'s personal website. \
    Your role is to represent {name} accurately and compellingly to potential employers or collaborators.
    ## Your context (use this as your ONLY source of truth)
    ### Experience summary: 
    Use your get_chunks_for_topic tool to get relevant experience chunks.
    ### LinkedIn profile:
            {profile}
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

def evaluator_system_prompt():
    system_prompt = f"""You are a strict evaluator assessing whether an AI agent answered an interview or profile question on behalf of {name}.
    ## Evaluation context
    ### Experience summary:
    {experience}
    ### LinkedIn profile:
    {profile} 
    ---
    ## Evaluation criteria (check ALL of these) 
    1. **Grounding** — Does every specific claim (metric, tool, initiative, outcome) appear in the context above? Flag \
    any figure or fact not present in the context as a hallucination, even if it sounds plausible.    
    2. **Specificity** — Does the answer cite at least 2 named, concrete examples from the context (e.g. a specific \
    project, metric, or initiative)? Reject answers that only use generic cloud/tech leadership language.
    3. **Missed context** — Are there stronger, more relevant examples in the provided context that the agent failed to use? If yes, list them explicitly.  
    4. **Persona** — Does the agent speak in first person, open without filler phrases, and avoid ending with questions back to the user?
    5. **Accuracy** — Does the answer stay within what {name} has actually done? No inflated claims, no role or scope beyond what's documented.
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

def run(message, history):
    history = [{"role": h["role"], "content": h["content"]} for h in history]
    messages = [{"role": "system", "content": chat_system_prompt()}] + history + [{"role": "user", "content": message}]
    openai, model_name = get_model(run_model)
    done = False
    while not done:
        response = openai.chat.completions.create(model=model_name, messages=messages, tools=tools)
        finish_reason = response.choices[0].finish_reason

        # If the LLM wants to call a tool, we do that!

        if finish_reason == "tool_calls":
            message = response.choices[0].message
            tool_calls = message.tool_calls
            results = handle_tool_calls(tool_calls)
            messages.append(message)
            messages.extend(results)
        else:
            done = True
    return response.choices[0].message.content
def rerun(reply, message, history, eval_response):
    updated_system_prompt = chat_system_prompt() + f"""The user asked:{message}.--- You gave this answer which was rejected:{reply}---
    ## Why it was rejected Reasoning: {eval_response.reasoning}--- Feedback: {eval_response.feedback}"""
    messages = [{"role": "system", "content": updated_system_prompt}] + history + [{"role": "user", "content": message}]
    openai, model_name = get_model(run_model)
    done = False
    while not done:
        response = openai.chat.completions.create(model=model_name, messages=messages, tools=tools)
        finish_reason = response.choices[0].finish_reason

        # If the LLM wants to call a tool, we do that!

        if finish_reason == "tool_calls":
            message = response.choices[0].message
            tool_calls = message.tool_calls
            results = handle_tool_calls(tool_calls)
            messages.append(message)
            messages.extend(results)
        else:
            done = True
    return response.choices[0].message.content

def evaluate(reply, message, history):
    messages = [{"role": "system", "content": evaluator_system_prompt()}] + \
               [{"role": "user", "content": evaluator_user_prompt(reply, message, history)}]
    openai, model_name = get_model(eval_model)
    done = False
    while not done:
        response = openai.chat.completions.parse(model=model_name, messages=messages, response_format=Evaluation)
        finish_reason = response.choices[0].finish_reason

        # If the LLM wants to call a tool, we do that!

        if finish_reason == "tool_calls":
            message = response.choices[0].message
            tool_calls = message.tool_calls
            results = handle_tool_calls(tool_calls)
            messages.append(message)
            messages.extend(results)
        else:
            done = True
    return response.choices[0].message.parsed

def candidate_agent_chat(message, history):
    reply = run(message, history)
    print(f'Chat Reply - {reply}')

    eval_response = evaluate(reply, message, history)
    print(f'Evaluation result - {eval_response}')
    if not eval_response.acceptable:
        print(f'Feedback - {eval_response.reasoning}')
        reply = rerun(reply, message, history, eval_response)
    else:
        print('The response is valid')
    return reply

demo = gr.ChatInterface(chat, title='Know about my experience')

if __name__ == "__main__":
    # ONLY the launch command goes here
    demo.launch()
