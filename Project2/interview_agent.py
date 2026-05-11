from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List
from tools import tools, handle_tool_calls
from get_llm_model import get_model
from pypdf import PdfReader
import gradio as gr

load_dotenv(override=True)
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

name = "saradag"
eval_model = "gemini"
run_model = "ollama-local"

def load_file(filename, base_path='docs'):
    ext = filename.split('.')[-1]
    final_text = ""
    if ext == 'pdf':
        reader = PdfReader(f"{base_path}/{name}/{filename}")
        for page in reader.pages:
            text = page.extract_text()
            if text:
                final_text += text
    else:
        with open(f"{base_path}/{name}/{filename}", "r", encoding="utf-8") as f:
            final_text = f.read()
    return final_text

profile = load_file('Profile.pdf')
job_description = load_file('jd.txt')

def interview_system_prompt():
    system_prompt = f"""You are a highly experienced technical interviewer and hiring manager. Your role is to conduct a realistic professional interview based on:
    - the provided job description 
    - the candidate's profile and experience
    - previous interview responses
    
    Your objective: Interview the candidate based on job description and candidate experience
    
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
        {profile}
    - Candidate experience:
        Use your get_all_chunks_formatted tool to get user experience
    - Job description:
        {job_description}
    """
    return system_prompt

def evaluator_system_prompt():
    system_prompt = f"""You are an expert interview evaluation system. Your job is to evaluate a candidate's - {name} interview answers objectively against:
    - job description
    - candidate profile
    - industry expectations
    Your objectives: 1. Assess technical depth 2. Assess leadership and ownership 3. Assess communication clarity 4. Assess problem-solving ability
    5. Assess alignment with the job description
    
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
    {job_description}
    CANDIDATE PROFILE:
    Use your get_all_chunks_formatted tool to get all experience chunks.
    ## Output format (always return this exact structure)
    ````json
    {{
     "candidate_level" : "weak | medium | strong",
     [ 
        {
          "Question" : Question being evaluated
          "overall_score": "7",
          "dimensions": {
            "technical_depth": "7",
            "clarity": "5",
            "ownership": "6",
            "communication": "7",
            "relevance": "8"
          },
          "strengths": [ 1 or 2 strengths
            Example "Good ownership demonstration",
            "Used real production example",
            "Explained tradeoffs clearly"
          ],
          "weaknesses": [ 1 or 2 weaknesses
            Example "Missing measurable impact",
            "Did not explain architecture constraints deeply"
          ],
          "suggestion": ["Suggested improved answer not more than 50 words"]
          },
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
    print(messages)
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
def evaluate(history):
    messages = [{"role": "system", "content": evaluator_system_prompt()}] + \
               [{"role": "user", "content": evaluator_user_prompt(history)}]
    openai, model_name = get_model(eval_model)
    done = False
    response = openai.chat.completions.parse(model=model_name, messages=messages, response_format=InterviewEvaluation)
    return response.choices[0].message.parsed

def chat(message, history):
    if not interview_state["started"]:
        message = "Start the interview"
        interview_state['started'] = True
    runs = interview_state["no_of_questions_asked"]
    if runs <= 3:
        reply = run(message, history)
        interview_state["no_of_questions_asked"] = interview_state["no_of_questions_asked"] + 1
        print(f'Chat Reply - {reply}')
        if runs == 3:
            reply = reply + "\n I will now evaluate your responses and provide the analysis"
        return reply
    else:
        eval_response = evaluate(history)
        print(f'Evaluation result - {eval_response}')
        return eval_response


demo = gr.ChatInterface(
        fn=chat, title='Interview Simulator'
    )

if __name__ == "__main__":
    # ONLY the launch command goes here
    demo.launch()
