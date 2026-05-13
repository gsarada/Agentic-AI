import gradio as gr
from dotenv import load_dotenv
from dataprocessing_helper import process_candidate_data
from interview_agent import interview_agent_chat
from candidate_agent import candidate_agent_chat

load_dotenv(override=True)
personas = {"Candidate Agent": "You interview me", "Interview Agent": "I will interview you"}

def is_valid_state(state, mode):
    print(f"State - {state}, mode- {mode}")
    if not state:
        return False, "Enter candidate name, upload linkedin profile or resume, " \
                      "experience summary and job description and then select mode to proceed"
    if state.get("exp_summary") is None and state.get("profile_text") is None:
        return False, "Upload atleast one of profile or experience summary to proceed"
    if mode == "Interview Agent" and state.get("job_description") is None:
        return False, "Upload Job description to proceed"
    return True, ""

with gr.Blocks() as demo:

    # Shared onboarding section
    with gr.Sidebar():

        name = gr.Textbox(label="Name")

        linkedin = gr.File(
            label="Upload LinkedIn Profile or Resume",
            file_types=[".pdf"],
            height=110
        )

        experience_summary = gr.File(
            label="Experience Summary in your own words",
            file_types=[".pdf", ".txt"],
            height=110
        )

        job_description = gr.File(
            label="Upload Job Description",
            file_types=[".txt"],
            height=110
        )

        submit_btn = gr.Button("Submit")

        onboarding_status = gr.Markdown()

    # Shared app state
    app_state = gr.State({})

    # Process onboarding data
    submit_btn.click(
        fn=process_candidate_data,
        inputs=[
            name,
            linkedin,
            experience_summary,
            job_description
        ],
        outputs=[
            onboarding_status,
            app_state
        ]
    )

    mode = gr.Radio(["Candidate Agent", "Interviewer Agent"], label="Select Agent")

    @gr.render(inputs=[app_state, mode])
    def dynamic_interface(state, selection):
        status, reason = is_valid_state(state, selection)

        # Candidate Persona Agent
        if status and selection == "Candidate Agent":
            gr.ChatInterface(
                fn=candidate_agent_chat,
                additional_inputs=app_state
            )
        elif status and selection == "Interviewer Agent":
            gr.ChatInterface(
                fn=interview_agent_chat,
                additional_inputs=app_state,
                chatbot=gr.Chatbot(
                    value=[
                        {
                            "role":"assistant",
                            "content": interview_agent_chat("Start interview", [], app_state)
                        }
                    ]
                )
            )
        else:
             gr.Markdown(reason)

demo.launch()
