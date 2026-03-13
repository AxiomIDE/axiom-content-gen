from gen.messages_pb2 import ContentDraft
from gen.axiom_logger import AxiomLogger, AxiomSecrets


_SYSTEM = (
    "You are a sharp content critic. Evaluate the draft against the requirements and "
    "provide specific, actionable feedback. Respond in the following format exactly:\n\n"
    "SCORE: <integer 1-10>\n"
    "FEEDBACK: <one or two sentences of specific improvement suggestions>\n\n"
    "A score of 8 or above means the content is approved and ready to publish. "
    "Be honest and demanding — only award 8+ when the content truly meets all requirements."
)


def content_critic(log: AxiomLogger, secrets: AxiomSecrets, input: ContentDraft) -> ContentDraft:
    """Scores content quality 1-10 and provides specific improvement feedback.

    Calls the Anthropic API to evaluate the draft against the original topic and
    requirements. Sets approved=true when quality_score reaches 8 or above, which
    signals the loop condition to stop iterating.
    """
    import anthropic

    api_key, ok = secrets.get("ANTHROPIC_API_KEY")
    if not ok:
        log.error("content_critic: ANTHROPIC_API_KEY secret not found")
        return ContentDraft(
            topic=input.topic,
            requirements=input.requirements,
            content=input.content,
            feedback="Error: ANTHROPIC_API_KEY secret not registered.",
            quality_score=0,
            iteration=input.iteration,
            approved=False,
        )

    client = anthropic.Anthropic(api_key=api_key)

    prompt = (
        f"Evaluate the following content against the topic and requirements.\n\n"
        f"Topic: {input.topic}\n"
        f"Requirements: {input.requirements}\n\n"
        f"--- Draft (iteration {input.iteration}) ---\n{input.content}"
    )

    log.info("content_critic: evaluating draft", topic=input.topic, iteration=input.iteration)
    message = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=256,
        system=_SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    )
    response = message.content[0].text.strip()

    score = 0
    feedback = response
    for line in response.splitlines():
        line = line.strip()
        if line.startswith("SCORE:"):
            try:
                score = int(line.split(":", 1)[1].strip())
            except ValueError:
                pass
        elif line.startswith("FEEDBACK:"):
            feedback = line.split(":", 1)[1].strip()

    approved = score >= 8
    log.info("content_critic: evaluation done", iteration=input.iteration, score=score, approved=approved)

    return ContentDraft(
        topic=input.topic,
        requirements=input.requirements,
        content=input.content,
        feedback=feedback,
        quality_score=score,
        iteration=input.iteration,
        approved=approved,
    )
