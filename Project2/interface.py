import gradio as gr
from dotenv import load_dotenv
from enum import Enum
from dataprocessing_helper import process_candidate_data
from interview_agent import interview_agent_chat
from candidate_agent import candidate_agent_chat

load_dotenv(override=True)

class Personas(Enum):
    CANDIDATE = "Candidate Persona"
    INTERVIEWER = "Interviewer Persona"

def is_valid_state(state, mode):
    print(f"State - {state}, mode- {mode}")
    if state.get("name", "") == "":
        return False, "## Name is mandatory"
    if mode is None:
        return False, "## Select agent persona"
    if state.get("exp_summary") is None and state.get("profile_text") is None:
        return False, "## Upload atleast one of profile or experience summary to proceed"
    if mode == Personas.INTERVIEWER.name and state.get("job_description") is None:
        return False, "## Upload Job description to proceed"
    return True, ""

with gr.Blocks() as demo:

    # Shared app state
    app_state = gr.State({"interview_agent": {"rounds": 0, "questions": 0},
                          "candidate_agent": {"rounds": 0, "answers": 0}})

    # Shared onboarding section
    with gr.Sidebar():
        onboarding_status = gr.Markdown()

        name = gr.Textbox(label="Name")

        linkedin = gr.File(
            label="Upload LinkedIn Profile or Resume",
            file_types=[".pdf"],
            height=110
        )

        experience_summary = gr.File(
            label="Upload Experience Summary",
            file_types=[".pdf", ".txt"],
            height=110
        )

        job_description = gr.File(
            label="Upload Job Description",
            file_types=[".txt"],
            height=110
        )

        submit_btn = gr.Button("Submit")
        mode = gr.Radio([Personas.CANDIDATE.name, Personas.INTERVIEWER.name], label="Select Agent Persona")

    # Process onboarding data
    submit_btn.click(
        fn=process_candidate_data,
        inputs=[
            name,
            linkedin,
            experience_summary,
            job_description,
            app_state
        ],
        outputs=[
            onboarding_status,
            app_state
        ]
    )

    gr.Markdown("# Welcome to RoleCraft AI - An adaptive AI interview platform ")

    dynamic_area = gr.Column()
    @gr.render(inputs=[mode, app_state])
    def dynamic_interface(selection, state):
        status, reason = is_valid_state(state, selection)
        print(f"Status- {status}, Reason- {reason}")
        # Candidate Persona Agent
        if status and selection == Personas.CANDIDATE.name:
            gr.ChatInterface(
                fn=candidate_agent_chat,
                additional_inputs=app_state,
                additional_outputs=app_state
            )
        elif status and selection == Personas.INTERVIEWER.name:
            gr.ChatInterface(
                fn=interview_agent_chat,
                additional_inputs=app_state,
                additional_outputs=app_state,
            )
        else:
            gr.Markdown(reason)

demo.launch()
