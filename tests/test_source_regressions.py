from pathlib import Path


def test_studionet_release_does_not_use_unsupported_event_emission():
    """v0.1.0 demonstrated that these event encodings fail on StudioNet."""
    source = (Path(__file__).parents[1] / "contracts" / "specguard.py").read_text(encoding="utf-8")
    assert "gl.Event" not in source
    assert ".emit()" not in source


def test_settlement_debits_before_the_single_transfer_dispatch_point():
    """The contract-controlled half of async child-transfer safety is static."""
    source = (Path(__file__).parents[1] / "contracts" / "specguard.py").read_text(encoding="utf-8")
    settlement = source[source.index("    def _settle("):source.index("    @gl.public.write\n    def settle_approved")]
    assert settlement.index("guard.deposit = u256(0)") < settlement.index("_send_gen(recipient, amount)")
    assert source.count(".emit_transfer(") == 1
