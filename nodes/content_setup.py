from gen.messages_pb2 import ContentSpec, ContentDraft
from gen.axiom_logger import AxiomLogger, AxiomSecrets


def content_setup(log: AxiomLogger, secrets: AxiomSecrets, input: ContentSpec) -> ContentDraft:
    """Initialises a ContentDraft from a ContentSpec with empty content and zero scores.

    This node acts as the entry point to the write-critique loop. It copies the
    topic and requirements into a fresh ContentDraft so that ContentWriter has a
    well-typed input on the first iteration.
    """
    log.info("content_setup: initialising draft", topic=input.topic)
    return ContentDraft(
        topic=input.topic,
        requirements=input.requirements,
        content="",
        feedback="",
        quality_score=0,
        iteration=0,
        approved=False,
    )
