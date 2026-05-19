from enum import Enum
from interview_agent import interview_agent_chat
from candidate_agent import candidate_agent_chat


max_rounds = 1
class Personas(Enum):
    CANDIDATE = "Candidate",
    INTERVIEWER = "Interviewer"


def has_user_data(state):
    #print(f"State - {state}")
    if state.get("name", "") == "":
        return False, "I will need your details before I can start. Please provide your name. Use sidebar"
    if state.get("profile_text") is None:
        return False, "Please upload your linked profile or resume. Use sidebar"
    if state.get("exp_summary") is None:
        return False, "Please provide your experience summary so the answers/evaluations are more accurate. Use sidebar"
    if state.get("job_description") is None:
        return False, "Please upload Job description. Use sidebar"
    if state.get("persona") is None:
        return False, "Thank you, I have your details. Please choose the persona you want me to assume."

    return True, None

def has_reached_limits(state):
    interview_agent_rounds = state["interview_agent"]["rounds"]
    candidate_agent_rounds = state["candidate_agent"]["rounds"]
    if (state.get("persona") == Personas.INTERVIEWER.name and
        interview_agent_rounds == max_rounds) or \
            (state.get("persona") == Personas.CANDIDATE.name and
             candidate_agent_rounds == max_rounds):
        return False, "Sorry, we have reached API tokens limit. Please try again later"
    return True, ""


def chat(message, history, state):
    mode = state.get("persona")
    status, reason = has_user_data(state)
    if not status:
        return reason, state
    status, reason = has_reached_limits(state)
    if not status:
        return reason, state
    if mode == Personas.INTERVIEWER.name:
        response, state = interview_agent_chat(message, history, state)
    elif mode == Personas.CANDIDATE.name:
        response, state = candidate_agent_chat(message, history, state)
    return response, state
