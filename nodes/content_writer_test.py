from gen.messages_pb2 import ContentDraft
from nodes.content_writer import content_writer


class _NoOpLogger:
    def debug(self, msg: str, **attrs) -> None: pass
    def info(self, msg: str, **attrs) -> None: pass
    def warn(self, msg: str, **attrs) -> None: pass
    def error(self, msg: str, **attrs) -> None: pass


class _NoOpSecrets:
    def get(self, name: str):
        return "", False


def test_content_writer_missing_secret():
    """Without a secret, the node should return an error message in content."""
    log = _NoOpLogger()
    secrets = _NoOpSecrets()
    draft = ContentDraft(topic="Rust async", requirements="500 words", iteration=0)
    result = content_writer(log, secrets, draft)
    assert isinstance(result, ContentDraft)
    assert "ANTHROPIC_API_KEY" in result.content
    assert result.topic == "Rust async"
    assert result.approved is False
