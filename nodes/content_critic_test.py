from gen.messages_pb2 import ContentDraft
from nodes.content_critic import content_critic


class _NoOpLogger:
    def debug(self, msg: str, **attrs) -> None: pass
    def info(self, msg: str, **attrs) -> None: pass
    def warn(self, msg: str, **attrs) -> None: pass
    def error(self, msg: str, **attrs) -> None: pass


class _NoOpSecrets:
    def get(self, name: str):
        return "", False


def test_content_critic_missing_secret():
    """Without a secret, the node should return an error in feedback and score 0."""
    log = _NoOpLogger()
    secrets = _NoOpSecrets()
    draft = ContentDraft(
        topic="Rust async",
        requirements="500 words",
        content="Rust has an async runtime...",
        iteration=1,
    )
    result = content_critic(log, secrets, draft)
    assert isinstance(result, ContentDraft)
    assert "ANTHROPIC_API_KEY" in result.feedback
    assert result.quality_score == 0
    assert result.approved is False
    assert result.content == draft.content
