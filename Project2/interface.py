import gradio as gr
from dotenv import load_dotenv
from dataprocessing_helper import process_candidate_data
from orchestrating_agent import Personas, chat

load_dotenv(override=True)

def init(mode):
    print(f"Mode - {mode}")
    value = [{"role": "assistant", "content": "Welcome! Please submit your details in the sidebar and then choose persona"}]
    if mode == Personas.INTERVIEWER.name:
        value = [{"role": "assistant", "content": "I will now act as your interview panel. Type 'Start Interview' and submit to begin."}]
    elif mode == Personas.CANDIDATE.name:
        value = [{"role": "assistant", "content": "I will now be wearing your hat :-). Ask your questions as an Interviewer."}]
    return value
def set_mode(mode, state):
    state["persona"] = mode
    value = init(mode)
    return state, value

with gr.Blocks() as demo:
    # Shared app state
    app_state = gr.State({"interview_agent": {"rounds": 0, "questions": 0},
                          "candidate_agent": {"rounds": 0, "answers": 0}, "persona": None})

    # Shared onboarding section
    with gr.Sidebar():
        onboarding_status = gr.Markdown()

        name = gr.Textbox(label="Name")

        linkedin = gr.MultimodalTextbox(
            value="Enter text..",
            sources="upload",
            file_types=[".pdf"],
            label="Upload Profile/Resume",
            submit_btn=False
        )

        experience_summary = gr.MultimodalTextbox(
            value="Enter text..",
            sources="upload",
            file_types=[".txt"],
            label="Upload experience summary",
            submit_btn=False
        )

        job_description = gr.MultimodalTextbox(
            value="Enter text..",
            sources="upload",
            file_types=[".txt"],
            label="Upload Job Description",
            submit_btn=False
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

    chatInterface = gr.ChatInterface(
        fn=chat,
        additional_inputs=[app_state],
        additional_outputs=[app_state],
        chatbot=gr.Chatbot(
            value=init(mode.value)
        ),
        fill_height=True,
        title="Welcome to RoleCraft AI - An adaptive AI interview platform"
    )

    mode.change(
        fn=set_mode,
        inputs=[mode, app_state],
        outputs=[
            app_state,
            chatInterface.chatbot
        ]
    )

demo.launch()
