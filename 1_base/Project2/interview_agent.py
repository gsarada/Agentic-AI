from tools import tools, handle_tool_calls
from get_llm_model import get_model, default_eval_model, default_chat_model

max_questions = 3

def interview_system_prompt(state):
    system_prompt = f"""You are a highly experienced technical interviewer and hiring manager. Your role is to conduct a realistic professional interview based on:
    - the provided job description 
    - the candidate's profile and experience
    - previous interview responses
    
    Your objective: Interview the candidate named {state.get("name")} based on job description and candidate experience
    
    Interview behavior:
    - Ask one question at a time.
    - Ask concise but meaningful questions.
    - Adapt questions dynamically based on previous answers.
    - Ask follow-up questions when answers are vague or shallow.
    - Increase depth if the candidate demonstrates strong expertise.
    - Keep the interview realistic and conversational.

    Rules:
    - Maintain interviewer professionalism.
    - Prioritize questions relevant to the job description.
    - Avoid repeating topics already covered sufficiently.
    - Balance technical, behavioral, architecture, leadership, and delivery questions.
    - Avoid answer evaluation. Only provide next question

    Question selection priorities: 1. Core skills from the job description 2. Candidate’s strongest experience areas
    3. Gaps between profile and job requirements 4. Real-world decision making 5. Tradeoff analysis 6. Leadership and influence

    You have access to:
    - Candidate profile:
        {state.get("profile_text")}
    - Candidate experience:
        {state.get("exp_summary")}
    - Job description:
        {state.get("job_description")}
    Output:
    question: str
    """
    return system_prompt

def evaluator_system_prompt(state):
    system_prompt = f"""You are an expert interview evaluation system. Your job is to evaluate a candidate's - {state.get("name")} interview answers objectively against:
    - job description
    - candidate profile
    - industry expectations
    Your objectives: 1. Assess technical depth 2. Assess leadership and ownership 3. Assess communication clarity 4. Assess problem-solving ability 5. Assess alignment with the job description
    
    You must score each answer and provide actionable feedback.
    Evaluation dimensions: 1. Technical Depth 2. Clarity & Structure 3. Relevance to Question 4. Ownership & Impact
    5. Decision Making 6. Communication Quality 7. Alignment with Job Requirements
    Scoring:
    - Rate each dimension from 1-10
    - Provide an overall score
    - Explain reasoning briefly
    Important:
    - Evaluate based on expected level for the role.
    - Consider whether the answer demonstrates real experience.
    - Penalize vague, generic, or theoretical answers.
    - Reward tradeoffs, metrics, ownership, and business impact.
    - Use the candidate profile to determine whether stronger examples SHOULD have been provided.
    Also provide:
    1. Strengths in the answer
    2. Weaknesses/gaps
    3. Suggested improved answer
    
    JOB DESCRIPTION:
    {state.get("job_description")}
    CANDIDATE PROFILE:
    {state.get("profile_text")}
    Candidate experience:
    {state.get("exp_summary")}
    ## Output format (always return this exact structure)
    ````json
    {{
      "candidate_level": "weak | medium | strong, based on the overall_score for each question",
      "evaluation": [
        {{
          "question": "Question being evaluated",
          "overall_score": "1 to 10 based on dimensions rating",
          "dimensions": {{
            "technical_depth": "1 to 10",
            "clarity": "1 to 10",
            "ownership": "1 to 10",
            "communication": "1 to 10",
            "relevance": "1 to 10"
          }},
          "strengths": [
            "Good ownership demonstration",
            "Used real production example"
          ],
          "weaknesses": [
            "Missing measurable impact",
            "Did not explain architecture constraints deeply"
          ],
          "suggestion": [
            "Suggested improved answer not more than 50 words"
          ]
        }}
      ]
    }}
    ```"""
    return system_prompt

def evaluator_user_prompt(history):
    user_prompt = f""" Conversation history:
    {history}
    Evaluate the response strictly against the criteria. Evaluate for each question, answer pair available in the history """
    return user_prompt

def run(message, history, state):
    history = [{"role": h["role"], "content": h["content"]} for h in history]
    print(f"Interview run method history - {history}")
    messages = [{"role": "system", "content": interview_system_prompt(state)}] + history + [{"role": "user", "content": message}]
    openai, model_name = get_model(default_chat_model)
    done = False
    while not done:
        response = openai.chat.completions.create(model=model_name, messages=messages)
        message = response.choices[0].message
        print(f'run Reply - {message}')

        # If the LLM wants to call a tool, we do that!

        if message.tool_calls:
            tool_calls = message.tool_calls
            results = handle_tool_calls(tool_calls)
            messages.append(message)
            messages.extend(results)
        else:
            done = True
    return message.content
def evaluate(history, message, state):
    conversation = [{"role": h["role"], "content": h["content"]} for h in history] + \
                    [{"role": "user", "content": message}]
    print(f"Interview evaluate method history - {history}")
    messages = [{"role": "system", "content": evaluator_system_prompt(state)}] + \
               [{"role": "user", "content": evaluator_user_prompt(conversation)}]
    openai, model_name = get_model(default_eval_model)
    response = openai.chat.completions.create(model=model_name, messages=messages)
    return response.choices[0].message.content

questions = ["Let's begin the interview. Can you start by telling me a little about yourself and why you're interested in this leadership position at our organization? Please elaborate on your background, experience, and qualifications for the role",
        "That's excellent, Sarada. It sounds like you have a wealth of experience in driving and delivering enterprise-scale multi-cloud platforms, with a strong focus on compliance, regulatory requirements, and business value. Your achievements at JPMorgan Chase & Co., such as enabling 700+ GenAI production use cases and driving cost optimization initiatives, are particularly noteworthy.\n\nI'd like to drill down further into your experience with DevOps and platform engineering. Can you tell me about a specific challenge you faced in your previous role, and how you led your team to overcome it? For example, what was the problem, and how did you go about solving it?",
        "It sounds like you effectively managed a complex initiative with limited clarity, unclear timelines, and a new technology framework that the team was not familiar with. You demonstrated strong leadership skills by setting clear requirements, prioritizing controls, and engaging with stakeholders to achieve consensus.\n\nYour approach of establishing recurring meetings, analyzing priorities, and proposing a solution was prudent. By adopting a BDD (Behavior-Driven Development) framework, you successfully guided your team through the transition.\n\nThe fact that you were able to deliver results within tight timelines and establish the platform as production-ready is impressive. It's clear that you effectively managed risk and uncertainty in this high-pressure situation.\n\nCan you tell me more about how you ensured that the controls and policies were adequate for the business requirements, given the complexity of regulatory environments? How did you balance the need for control with the potential impact on business operations?" ]

def interview_agent_chat(message, history, state):
    questions_asked = state["interview_agent"]["questions"]
    rounds = state["interview_agent"]["rounds"]
    index = state.get("interview_agent").get("index", 0)
    print(f"rounds - {rounds}, questions_asked - {questions_asked}")
    if questions_asked == 0:
        index = len(history) - 1
        state["interview_agent"]["index"] = index
    if questions_asked == max_questions:
        eval_response = evaluate(history[index:], message, state)
        print(f'Evaluation result - {eval_response}')
        state["interview_agent"]["questions"] = 0
        state["interview_agent"]["rounds"] = rounds + 1
        response = f"###Thanks for answering the questions. We will conclude the interview now. Below is the evaluation of your answers \n {eval_response}"
    else:
        reply = run(message, history[index:], state)
        #reply = questions[questions_asked]
        state["interview_agent"]["questions"] = questions_asked + 1
        response = reply
    print(f"Reply = {response}")
    return response, state
