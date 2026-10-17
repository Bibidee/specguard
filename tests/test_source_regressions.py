from pathlib import Path


def test_studionet_release_does_not_use_unsupported_event_emission():
    """v0.1.0 demonstrated that these event encodings fail on StudioNet."""
    source = (Path(__file__).parents[1] / "contracts" / "specguard.py").read_text(encoding="utf-8")
    assert "gl.Event" not in source
    assert ".emit()" not in source
