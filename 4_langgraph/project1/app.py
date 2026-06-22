import gradio as gr
import asyncio
from dotenv import load_dotenv
from assistants import Assistants
import tools
from logger import logger

async def init():
    try:
        load_dotenv(override=True)
        assistant = Assistants()
        await assistant.setup()
        return assistant
    except Exception as e:
        logger.error(f"Exception {e} occured.")
        raise e


async def process_message(assistant, message, success_criteria, history):
    results = await assistant.run(message, success_criteria, history)
    return results


async def reset():
    new_assistant = Assistants()
    await new_assistant.setup()
    return "", "", None, new_assistant


def free_resources(assistant):
    logger.info("Cleaning up")
    try:
        if assistant:
            assistant.cleanup()
    except Exception as e:
        logger.error(f"Exception during cleanup: {e}")


with gr.Blocks(title="CoWorker",) as ui:
    gr.Markdown("## Personal Co-Worker")
    assistant = gr.State(delete_callback=free_resources)

    with gr.Row():
        chatbot = gr.Chatbot(label="Conversation", height=800)
    with gr.Group():
        with gr.Row():
            message = gr.Textbox(show_label=False, placeholder="Your request to the Assistant")
        with gr.Row():
            success_criteria = gr.Textbox(
                show_label=False, placeholder="What is your success criteria?"
            )
    with gr.Row():
        reset_button = gr.Button("Reset", variant="stop")
        go_button = gr.Button("Go!", variant="primary")

    ui.load(init, [], [assistant])
    message.submit(
        process_message, [assistant, message, success_criteria, chatbot], [chatbot]
    )
    success_criteria.submit(
        process_message, [assistant, message, success_criteria, chatbot], [chatbot]
    )
    go_button.click(
        process_message, [assistant, message, success_criteria, chatbot], [chatbot]
    )
    reset_button.click(reset, [], [message, success_criteria, chatbot, assistant])

if __name__ == "__main__":
    try:
        ui.launch(theme=gr.themes.Default(primary_hue="emerald"))
    except KeyboardInterrupt:
        logger.error("\n[Ctrl+C] Gradio server stopping...")
    except Exception as e:
        logger.error("\n Exiting due to error {e}")
    finally:
        # 3. This block is GUARANTEED to run when the terminal process exits via Ctrl+C
        if tools.ASYNC_BROWSER or tools.PLAYWRIGHT_CONTEXT:
            logger.info("Cleaning up Playwright structures...")
            loop = asyncio.get_event_loop()
            loop.run_until_complete(tools.close_playwright())
        gr.close_all()
