from gen.messages_pb2 import ContentDraft
from gen.axiom_logger import AxiomLogger, AxiomSecrets


_SYSTEM = (
    "You are an exceptionally demanding content editor at a top-tier publication. "
    "Your standards are high and you do not flatter writers. Evaluate the draft strictly "
    "against the requirements and provide specific, actionable feedback. "
    "Respond in the following format exactly:\n\n"
    "SCORE: <integer 1-10>\n"
    "FEEDBACK: <two or three sentences identifying concrete weaknesses and exactly what must change>\n\n"
    "Scoring rules:\n"
    "- First drafts (iteration 1) may score at most 6, no matter how good they appear. "
    "There is always room to improve structure, specificity, or voice.\n"
    "- A score of 9 or above means the content is approved. Reserve this for truly polished work "
    "that needs no further revision.\n"
    "- Scores of 7–8 mean the writing is decent but still has clear gaps to address.\n"
    "- Never give empty praise. Every score must be accompanied by at least one concrete improvement."
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

    approved = score >= 9
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
