import asyncio
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from  get_llm_model import get_model
from publisher import create_post
from prompts import (
    analyst_prompt,
    storyteller_prompt, researcher_prompt, main_editor_prompt, publisher_agent_prompt, guardrail_prompt
)
from agents import (
    Agent, Runner, trace, function_tool, OpenAIChatCompletionsModel,
    handoff, input_guardrail, GuardrailFunctionOutput
)

load_dotenv(override=True)

deepseek_client, d_model_name = get_model("deepseek")
llama_client, l_model_name = get_model("llama")
qwen_client, q_model_name = get_model("qwen")
openai_client, o_model_name = get_model("groq")
gemini_client, g_model_name = get_model("gemini")


qwen_model = OpenAIChatCompletionsModel(model=q_model_name, openai_client=qwen_client)
llama_model = OpenAIChatCompletionsModel(model=l_model_name, openai_client=llama_client)
deepseek_model = OpenAIChatCompletionsModel(model=d_model_name, openai_client=deepseek_client)
openai_model = OpenAIChatCompletionsModel(model=o_model_name, openai_client=openai_client)
gemini_model = OpenAIChatCompletionsModel(model=g_model_name, openai_client=gemini_client)

analyst_agent = Agent(name="Analyst Blogger", instructions=analyst_prompt, model=qwen_model)
storyteller_agent = Agent(name="Story Telling Blogger", instructions=storyteller_prompt, model=llama_model)
researcher_agent = Agent(name="Research Blogger", instructions=researcher_prompt, model=deepseek_model)

analyst_agent_tool = analyst_agent.as_tool(tool_name="analyst_agent_tool",
                                           tool_description="An expert Data Analyst and Industry Researcher turned technical blogger creating blog content on a given topic")
storyteller_agent_tool = storyteller_agent.as_tool(tool_name="storyteller_agent_tool",
                                                   tool_description="A creative essayist and a warm, conversational blogger creating blog content on a given topic")
researcher_agent_tool = researcher_agent.as_tool(tool_name="researcher_agent_tool",
                                                 tool_description="A bold thought leader, contrarian strategist, and minimalist writer creating blog content on a given topic")

# Define the exact payload the Editor must pass to the Publisher
class PublicationPayload(BaseModel):
    content: str = Field(description="The finalized, synthesized masterclass Markdown article content from the Chief Editor.")

class InvalidTopic(BaseModel):
    is_invalid_topic: bool
    reasoning: str

input_guardrail_agent = Agent(name="input_guardrail_agent", instructions=guardrail_prompt,
                              model=llama_model, output_type=InvalidTopic)

@input_guardrail
async def guardrail_against_topic(ctx, agent, message):
    result = await Runner.run(input_guardrail_agent, message, context=ctx)
    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.is_invalid_topic,)
@function_tool
async def generate_draft_blogs(topic: str):
    """ Generate a single merged string of three versions of blogs by calling three agents parallely"""
    results = await asyncio.gather(
        Runner.run(analyst_agent, topic),
        Runner.run(storyteller_agent, topic),
        Runner.run(researcher_agent, topic),
    )
    outputs = [f"### {result.last_agent.name}\n{result.final_output}" for result in results]
    draft_blogs = "\n".join(outputs)
    return draft_blogs


@function_tool(needs_approval=True)
def publish_to_blogger(title: str, content: str):
    print(f"Title - {title}")
    print(f"Content - {content}")
    post_url = create_post(title, content)
    return post_url

def log_final_markdown_content(ctx, input: str):
    print(f"Handoff triggered! content: {input}")


publisher_agent = Agent(name="publisher", instructions=publisher_agent_prompt, model=gemini_model,
                        tools=[publish_to_blogger])

editor_agent = Agent(name="Chief Editor", instructions=main_editor_prompt, model=openai_model,
                     # model_settings=ModelSettings(
                     #     parallel_tool_calls=True
                     # ),
                     # tools=[analyst_agent_tool, storyteller_agent_tool, researcher_agent_tool],
                     input_guardrails=[guardrail_against_topic],
                     tools=[generate_draft_blogs],
                     handoffs=[handoff(publisher_agent, input_type=PublicationPayload, on_handoff=log_final_markdown_content)],
                     handoff_description="Call publisher to hand off the finalized, synthesized markdown blog article for deployment and publication."
                )

# print(publisher_agent)
# print(editor_agent)

async def blog(topic: str):
    with trace("blogger trace"):
        result = await Runner.run(editor_agent, f"Topic - {topic}")
        if result.interruptions:
            state = result.to_state()
            for interruption in result.interruptions:
                approve = input("Do you want to continue to publish? Yes or No")
                if approve == "Yes":
                    state.approve(interruption)
                else:
                    reason = input("Please provide reason you do not want to publish")
                    state.reject(interruption, rejection_message=reason)
            result = await Runner.run(editor_agent, state)
        print(result.final_output)

topic = input("Please enter the topic")
asyncio.run(blog(topic))
