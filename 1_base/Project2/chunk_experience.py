"""
chunk_experience.py
--------------------------
LLM agent tool to chunk experience.
"""
from expchunk_model import ExperienceChunks
from get_llm_model import get_model

# ─────────────────────────────────────────────────────────────────────────────
# PROMPT
# ─────────────────────────────────────────────────────────────────────────────

CHUNKING_SYSTEM_PROMPT = """You are a career experience analyst. 
Output only raw JSON — no markdown fences, no explanation, no commentary."""

CHUNKING_USER_PROMPT = """\
A user has provided their raw professional experience below. 
Restructure it into topic-based chunks following the schema exactly.

## Schema

Return a JSON object with exactly two top-level keys:

{{
  "chunks": {{
    "<snake_case_key>": {{
      "label": "<Human Readable Label>",
      "keywords": ["<keyword>", ...],   // 8-12 items
      "content": ["<bullet string>", ...]
    }}
  }},
  "topic_map": {{
    "<topic phrase>": ["<chunk_key>", ...]   // 2-4 keys per phrase
  }}
}}

## Content rules

- Each content item is a plain bullet string (no leading "- ").
- Sub-section headings inside a chunk are prefixed exactly: "HEADING: Title"
- Preserve every metric, tool name, and outcome exactly as stated.
- Remove filler language, emotions, and internal monologue.
- Use past tense, active voice throughout.
- If an achievement spans multiple themes, include it in all relevant chunks.
- Include handed-over or failed initiatives — state what was built and the outcome, 
  no negative framing.
- topic_map keys must only reference keys that exist in chunks.
- Minimum 5 chunks.
- max content size is 500 words

## Input

{experience_text}"""


def build_prompt(experience_text: str) -> tuple[str, str]:
    """Returns (system_prompt, user_prompt) ready to pass to your LLM call."""
    return (
        CHUNKING_SYSTEM_PROMPT,
        CHUNKING_USER_PROMPT.format(experience_text=experience_text),
    )


# ─────────────────────────────────────────────────────────────────────────────
# FULL PIPELINE EXAMPLE
# ─────────────────────────────────────────────────────────────────────────────
def chunk_experience(
        experience_text: str,
        model_name,  # your LLM client
        name: str | None = None,
) -> ExperienceChunks:
    """
    Full pipeline: prompt → LLM → parse → validate → (optionally save).

    Args:
        experience_text: Raw experience string from the user.
        model_name: llm model to use for chunking
        name: If provided, saves the validated JSON to a path with this name.

    Returns:
        Validated ExperienceChunks instance.
    """
    system_prompt, user_prompt = build_prompt(experience_text)
    messages = [{"role": "system", "content": system_prompt}] + [{"role": "user", "content": user_prompt}]
    llm_client, model_name = get_model(model_name)
    response = llm_client.chat.completions.parse(model=model_name, messages=messages,
                                                 response_format=ExperienceChunks, max_completion_tokens=8192)
    result = response.choices[0].message.parsed

    if name:
        result.save(name)

    return result


# ─────────────────────────────────────────────────────────────────────────────
# USAGE DEMO
# ─────────────────────────────────────────────────────────────────────────────

def test():
    from experience_retriever import get_chunks_for_topic
    with open("docs/saradag/experience.txt", "r", encoding="utf-8") as f:
        final_text = f.read()
    raw_experience = final_text

    #chunks = chunk_experience(raw_experience, model_name="deepseek", name="saradag")

    # Retrieve for a specific interview question
    print(get_chunks_for_topic("saradag", "developer productivity", max_chunks=2))

    # Inject full context into agent system prompt
    # full_context = chunks.get_all_chunks_formatted()

    # Reload from disk later
    # reloaded = ExperienceChunks.load("saradag")


#from dotenv import load_dotenv

#load_dotenv()
#test()
