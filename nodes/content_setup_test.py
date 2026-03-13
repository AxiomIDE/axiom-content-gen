from gen.messages_pb2 import ContentSpec, ContentDraft
from nodes.content_setup import content_setup


class _NoOpLogger:
    def debug(self, msg: str, **attrs) -> None: pass
    def info(self, msg: str, **attrs) -> None: pass
    def warn(self, msg: str, **attrs) -> None: pass
    def error(self, msg: str, **attrs) -> None: pass


class _NoOpSecrets:
    def get(self, name: str):
        return "", False


def test_content_setup_copies_fields():
    log = _NoOpLogger()
    secrets = _NoOpSecrets()
    spec = ContentSpec(topic="Rust async", requirements="500 words, beginner audience")
    draft = content_setup(log, secrets, spec)
    assert isinstance(draft, ContentDraft)
    assert draft.topic == "Rust async"
    assert draft.requirements == "500 words, beginner audience"
    assert draft.content == ""
    assert draft.feedback == ""
    assert draft.quality_score == 0
    assert draft.iteration == 0
    assert draft.approved is False
