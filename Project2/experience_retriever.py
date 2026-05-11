from expchunk_model import ExperienceChunks

def get_chunks_for_topic(name: str, topic: str, max_chunks: int = 3) -> str:
    """
    Return formatted content for chunks relevant to the given topic string.
    Falls back to all chunks if no topic_map match is found.
    """
    topic_lower = topic.lower()
    matched: list[str] = []

    exp = ExperienceChunks.load(name)

    for keyword, keys in exp.topic_map.items():
        if keyword.lower() in topic_lower:
            for key in keys:
                if key not in matched:
                    matched.append(key)

    if not matched:
        matched = list(exp.chunks.keys())

    output = []
    for key in matched[:max_chunks]:
        chunk = exp.chunks[key]
        lines = "\n".join(
            f"\n**{line[8:].strip()}**"
            if line.startswith("HEADING:")
            else f"- {line}"
            for line in chunk.content
        )
        output.append(f"### {chunk.label}\n{lines}")

    return "\n\n".join(output)

def get_all_chunks_formatted(name: str) -> str:
    """Return all chunks as a single formatted string for full-context injection."""
    output = []
    exp = ExperienceChunks.load(name)
    for chunk in exp.chunks.values():
        lines = "\n".join(
            f"\n**{line[8:].strip()}**"
            if line.startswith("HEADING:")
            else f"- {line}"
            for line in chunk.content
        )
        output.append(f"### {chunk.label}\n{lines}")
    return "\n\n".join(output)
