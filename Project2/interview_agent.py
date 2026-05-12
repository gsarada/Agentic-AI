from pydantic import BaseModel
from typing import List
from tools import tools, handle_tool_calls
from get_llm_model import get_model, default_eval_model, default_chat_model

class Dimension(BaseModel):
    technical_depth: int
    clarity: int
    ownership: int
    communication: int
    relevance: int

class QuestionEvaluation(BaseModel):
    question: str
    overall_score: int
    dimensions: Dimension
    strengths: List[str]
    weaknesses: List[str]
    suggestion: str

class InterviewEvaluation(BaseModel):
    candidate_level: str
    evaluation: List[QuestionEvaluation]

# Global interview state
interview_state = {
    "no_of_questions_asked": 0,
    "started": False
}

def interview_system_prompt(state):
    system_prompt = f"""You are a highly experienced technical interviewer and hiring manager. Your role is to conduct a realistic professional interview based on:
    - the provided job description 
    - the candidate's profile and experience
    - previous interview responses
    
    Your objective: Interview the candidate named {state.get("candidate_name")} based on job description and candidate experience
    
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

    Question selection priorities: 1. Core skills from the job description 2. Candidate’s strongest experience areas
    3. Gaps between profile and job requirements 4. Real-world decision making 5. Tradeoff analysis 6. Leadership and influence

    You have access to:
    - Candidate profile:
        {state.get("linkedin_text")}
    - Candidate experience:
        {state.get("exp_text")}
    - Job description:
        {state.get("job_description")}
    Output:
    question: str
    """
    return system_prompt

def evaluator_system_prompt(state):
    system_prompt = f"""You are an expert interview evaluation system. Your job is to evaluate a candidate's - {state.get("candidate_name")} interview answers objectively against:
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
    {state.get("linkedin_text")}
    Candidate experience:
    {state.get("exp_text")}
    ## Output format (always return this exact structure)
    ````json
    {{
      "candidate_level": "weak | medium | strong",
      "evaluation": [
        {{
          "question": "Question being evaluated",
          "overall_score": "1 to 10",
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

def run(message, history):
    history = [{"role": h["role"], "content": h["content"]} for h in history]
    messages = [{"role": "system", "content": interview_system_prompt()}] + history + [{"role": "user", "content": message}]
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
    return response.choices[0].message.content
def evaluate(history, message, state):
    conversation = [{"role": h["role"], "content": h["content"]} for h in history] + \
                    [{"role": "user", "content": message}]

    messages = [{"role": "system", "content": evaluator_system_prompt(state)}] + \
               [{"role": "user", "content": evaluator_user_prompt(conversation)}]
    openai, model_name = get_model(default_eval_model)
    done = False
    response = openai.chat.completions.parse(model=model_name, messages=messages, response_format=InterviewEvaluation)
    return response.choices[0].message.parsed

questions = ["Let's begin the interview. Can you start by telling me a little about yourself and why you're interested in this leadership position at our organization? Please elaborate on your background, experience, and qualifications for the role",
        "That's excellent, Sarada. It sounds like you have a wealth of experience in driving and delivering enterprise-scale multi-cloud platforms, with a strong focus on compliance, regulatory requirements, and business value. Your achievements at JPMorgan Chase & Co., such as enabling 700+ GenAI production use cases and driving cost optimization initiatives, are particularly noteworthy.\n\nI'd like to drill down further into your experience with DevOps and platform engineering. Can you tell me about a specific challenge you faced in your previous role, and how you led your team to overcome it? For example, what was the problem, and how did you go about solving it?",
        "It sounds like you effectively managed a complex initiative with limited clarity, unclear timelines, and a new technology framework that the team was not familiar with. You demonstrated strong leadership skills by setting clear requirements, prioritizing controls, and engaging with stakeholders to achieve consensus.\n\nYour approach of establishing recurring meetings, analyzing priorities, and proposing a solution was prudent. By adopting a BDD (Behavior-Driven Development) framework, you successfully guided your team through the transition.\n\nThe fact that you were able to deliver results within tight timelines and establish the platform as production-ready is impressive. It's clear that you effectively managed risk and uncertainty in this high-pressure situation.\n\nCan you tell me more about how you ensured that the controls and policies were adequate for the business requirements, given the complexity of regulatory environments? How did you balance the need for control with the potential impact on business operations?" ]
def interview_agent_chat(message, history, state):
    print(message)
    if not interview_state["started"]:
        interview_state['started'] = True
    runs = interview_state["no_of_questions_asked"]
    print(f"Runs - {runs}")
    if runs == 3:
        eval_response = evaluate(history, message, state)
        print(f'Evaluation result - {eval_response}')
        return str(eval_response)
    else:
        #reply = run(message, history, state)
        reply = questions[runs]
        interview_state["no_of_questions_asked"] = interview_state["no_of_questions_asked"] + 1
        if runs == 3:
            reply = reply
        return reply
