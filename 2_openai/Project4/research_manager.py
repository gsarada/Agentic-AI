import gradio as gr
from dotenv import load_dotenv
from research_agents import run

load_dotenv(override=True)

with gr.Blocks(theme=gr.themes.Default(primary_hue="sky")) as ui:
    gr.Markdown("#Deep Research")
    query = gr.Textbox(label="What topic would you like to research?")
    run_button = gr.Button("Run", variant="primary")
    report = gr.Markdown(label="Report")

    run_button.click(fn=run, inputs=query, outputs=report)
    query.submit(fn=run, inputs=query, outputs=report)

ui.launch(inbrowser=True)
