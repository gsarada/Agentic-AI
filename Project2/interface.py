import gradio as gr
from dotenv import load_dotenv
from dataprocessing_helper import process_candidate_data, process_jd
from interview_agent import interview_agent_chat
from candidate_agent import candidate_agent_chat

load_dotenv(override=True)

with gr.Blocks() as demo:

    # Shared onboarding section
    with gr.Row():

        name = gr.Textbox(label="Name")

        linkedin = gr.File(
            label="Upload LinkedIn Profile or Resume",
            file_types=[".pdf"]
        )

        experience_summary = gr.File(
            label="Experience Summary in your own words",
            file_types=[".pdf", ".txt"]
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
            experience_summary
        ],
        outputs=[
            onboarding_status,
            app_state
        ]
    )

    # Main tabs
    with gr.Tabs():

        # Candidate Persona Agent
        with gr.Tab("Candidate Agent"):

            candidate_chat = gr.ChatInterface(
                fn=candidate_agent_chat
            )

        # Interview Simulator
        with gr.Tab("Interview Agent"):

            jd_upload = gr.File(
                label="Upload Job Description",
                file_types=[".pdf", ".txt"]
            )

            jd_status = gr.Markdown()

            jd_upload.upload(
                fn=process_jd,
                inputs=[jd_upload, app_state],
                outputs=[jd_status, app_state]
            )

            interview_chat = gr.ChatInterface(
                fn=interview_agent_chat,
                chatbot=gr.Chatbot(
                    value=[
                        {
                            "role":"assistant",
                            "content": interview_agent_chat("Start interview", [])
                        }
                    ]
                )
            )
