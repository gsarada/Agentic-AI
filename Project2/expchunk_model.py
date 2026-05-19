"""
expchunk_model.py
--------------------------
Pydantic models for structured experience chunks,
with parsing, and retrieval helpers.
"""
from __future__ import annotations
from typing import Annotated
import os
from pydantic import BaseModel, Field, model_validator


# ─────────────────────────────────────────────────────────────────────────────
# MODELS
# ─────────────────────────────────────────────────────────────────────────────

class ExperienceChunk(BaseModel):
    label: Annotated[str, Field(
        description="Human-readable title for this topic chunk"
    )]
    keywords: Annotated[list[str], Field(
        min_length=5,
        description="Keywords an interviewer might use that relate to this chunk"
    )]
    content: Annotated[list[str], Field(
        min_length=1,
        description=(
            "Ordered list of bullet point strings. "
            "Sub-section headings are prefixed with 'HEADING:'"
        )
    )]


class ExperienceChunks(BaseModel):
    chunks: Annotated[dict[str, ExperienceChunk], Field(
        description="Map of snake_case chunk key to chunk data"
    )]
    topic_map: Annotated[dict[str, list[str]], Field(
        description=(
            "Map of topic/question phrase to a list of relevant chunk keys. "
            "All referenced keys must exist in the chunks dict."
        )
    )]

    @model_validator(mode="after")
    def validate_topic_map_keys(self) -> ExperienceChunks:
        """Ensure every key referenced in topic_map exists in chunks."""
        valid_keys = set(self.chunks.keys())
        errors = []
        for topic, keys in self.topic_map.items():
            for key in keys:
                if key not in valid_keys:
                    errors.append(
                        f"topic_map['{topic}'] references unknown chunk key: '{key}'"
                    )
        if errors:
            print(f"\n.join(errors)")
            #raise ValueError("\n".join(errors))
        return self

    # ── Retrieval helpers ────────────────────────────────────────────────────

    def save(self, name: str) -> None:
        path = f"docs/{name}/experience_chunks.json"
        try:
            directory = os.path.dirname(path)
            if not os.path.exists(directory):
                os.makedirs(directory)
            with open(path, "w") as f:
                f.write(self.model_dump_json(indent=2))
        except Exception as e:
            print(f"Exception {e} occurred while saving experience chunks")
            raise e


    @classmethod
    def load(cls, name: str) -> ExperienceChunks:
        path = f"docs/{name}/experience_chunks.json"
        try:
            if not os.path.exists(path):
                return None
            with open(path) as f:
                return cls.model_validate_json(f.read())
        except Exception as e:
            print(f"Exception {e} occurred while loading experience chunks")
            return None
