from enum import Enum
from interview_agent import interview_agent_chat
from candidate_agent import candidate_agent_chat


max_rounds = 1
class Personas(Enum):
    CANDIDATE = "Candidate",
    INTERVIEWER = "Interviewer"


def has_user_data(state, mode):
    print(f"State - {state}, mode- {mode}")
    if state.get("name", "") == "":
        return False, "I will need your details before I can start. Please provide your name. Use sidebar"
    if state.get("profile_text") is None:
        return False, "Please upload your linked profile or resume. Use sidebar"
    if state.get("exp_summary") is None:
        return False, "Would you like to provide your experience summary?. Use sidebar"
    if mode is None:
        return False, "Thank you, I have your details. Please choose the persona you want me to assume. Use sidebar"
    if mode == Personas.INTERVIEWER.name and state.get("job_description") is None:
        return False, "Upload Job description. Use sidebar"
    return True, None

def has_reached_limits(state, mode):
    interview_agent_rounds = state["interview_agent"]["rounds"]
    candidate_agent_rounds = state["candidate_agent"]["rounds"]
    if (mode == Personas.INTERVIEWER.name and
        interview_agent_rounds == max_rounds) or \
            (mode == Personas.CANDIDATE.name and
             candidate_agent_rounds == max_rounds):
        return False, "You have reached limits. Please try again later"
    return True, ""


def chat(message, history, state):
    mode = state.get("persona")
    status, reason = has_user_data(state, mode)
    if not status:
        return reason, state
    status, reason = has_reached_limits(state, mode)
    if not status:
        return reason, state
    if mode == Personas.INTERVIEWER.name:
        response, state = interview_agent_chat(message, history, state)
    elif mode == Personas.CANDIDATE.name:
        response, state = candidate_agent_chat(message, history, state)
    return response, state
