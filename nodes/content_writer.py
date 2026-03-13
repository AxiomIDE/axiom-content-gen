from gen.messages_pb2 import ContentDraft
from gen.axiom_logger import AxiomLogger, AxiomSecrets


def content_writer(log: AxiomLogger, secrets: AxiomSecrets, input: ContentDraft) -> ContentDraft:
    """Writes or rewrites content using an LLM.

    On the first pass (iteration == 0) produces a fresh draft from the topic and
    requirements. On subsequent passes incorporates the critic's feedback to
    improve the existing content. Increments the iteration counter each time.
    """
    import anthropic

    api_key, ok = secrets.get("ANTHROPIC_API_KEY")
    if not ok:
        log.error("content_writer: ANTHROPIC_API_KEY secret not found")
        return ContentDraft(
            topic=input.topic,
            requirements=input.requirements,
            content="Error: ANTHROPIC_API_KEY secret not registered.",
            feedback=input.feedback,
            quality_score=input.quality_score,
            iteration=input.iteration,
            approved=False,
        )

    client = anthropic.Anthropic(api_key=api_key)
    iteration = input.iteration + 1

    if input.iteration == 0:
        system = (
            "You are an expert content writer. Write clear, engaging, well-structured content "
            "that precisely matches the given topic and requirements."
        )
        prompt = (
            f"Write content on the following topic.\n\n"
            f"Topic: {input.topic}\n"
            f"Requirements: {input.requirements}\n\n"
            f"Produce only the final content — no preamble, no meta-commentary."
        )
        log.info("content_writer: writing first draft", topic=input.topic, iteration=iteration)
    else:
        system = (
            "You are an expert content writer. Revise the draft below to address the critic's "
            "feedback while keeping the original intent and requirements."
        )
        prompt = (
            f"Revise the following content based on the critic's feedback.\n\n"
            f"Topic: {input.topic}\n"
            f"Requirements: {input.requirements}\n\n"
            f"--- Current draft ---\n{input.content}\n\n"
            f"--- Critic feedback (iteration {input.iteration}) ---\n{input.feedback}\n\n"
            f"Produce only the revised content — no preamble, no meta-commentary."
        )
        log.info("content_writer: revising draft", topic=input.topic, iteration=iteration, score=input.quality_score)

    message = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=1024,
        system=system,
        messages=[{"role": "user", "content": prompt}],
    )
    content = message.content[0].text.strip()
    log.info("content_writer: draft ready", iteration=iteration, length=len(content))

    return ContentDraft(
        topic=input.topic,
        requirements=input.requirements,
        content=content,
        feedback=input.feedback,
        quality_score=input.quality_score,
        iteration=iteration,
        approved=False,
    )
