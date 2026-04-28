"""Round-trip + tolerance tests for the canonical Signal model."""
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from signals_contract import Signal


def _base_signal_dict() -> dict:
    return {
        "id": "11111111-1111-1111-1111-111111111111",
        "strategy_id": "22222222-2222-2222-2222-222222222222",
        "research_config_id": "33333333-3333-3333-3333-333333333333",
        "strategy_git_sha": "abc123",
        "research_config_version": 1,
        "asset": "BTC",
        "direction": "long",
        "confidence": 0.7,
        "published_at": datetime(2026, 4, 28, 9, 0, tzinfo=UTC).isoformat(),
    }


def test_minimal_signal_parses():
    s = Signal.model_validate(_base_signal_dict())
    assert s.asset == "BTC"
    assert s.direction == "long"
    assert s.confidence == 0.7
    assert s.risk_score is None
    assert s.payload == {}
    assert s.source_article_ids == []


def test_confidence_bounds_enforced():
    base = _base_signal_dict()
    base["confidence"] = 1.1
    with pytest.raises(ValidationError):
        Signal.model_validate(base)

    base["confidence"] = -0.1
    with pytest.raises(ValidationError):
        Signal.model_validate(base)


def test_direction_literal_enforced():
    base = _base_signal_dict()
    base["direction"] = "sideways"
    with pytest.raises(ValidationError):
        Signal.model_validate(base)


def test_payload_string_is_parsed_as_json_object():
    base = _base_signal_dict()
    base["payload"] = '{"reasoning": "Fed dovish"}'
    s = Signal.model_validate(base)
    assert s.payload == {"reasoning": "Fed dovish"}


def test_risk_score_string_is_parsed_as_json_object():
    base = _base_signal_dict()
    base["risk_score"] = '{"narrative_age": 0.4}'
    s = Signal.model_validate(base)
    assert s.risk_score == {"narrative_age": 0.4}


def test_payload_invalid_json_passes_through_unchanged():
    base = _base_signal_dict()
    base["payload"] = "not json at all"
    # The validator returns non-JSON strings unchanged, but pydantic then
    # rejects because payload must be a dict. That's the right behavior:
    # tolerate ad-hoc JSON-encoded dicts but don't accept arbitrary strings.
    with pytest.raises(ValidationError):
        Signal.model_validate(base)


def test_unknown_fields_are_ignored():
    base = _base_signal_dict()
    base["future_field_that_does_not_exist_yet"] = "anything"
    s = Signal.model_validate(base)  # extra='ignore' is pydantic v2 default
    assert s.asset == "BTC"


def test_poly_market_slug_as_asset():
    base = _base_signal_dict()
    base["asset"] = "russia-ukraine-ceasefire-before-gta-vi-554"
    s = Signal.model_validate(base)
    assert s.asset.startswith("russia-ukraine")


def test_round_trip_dump_and_reparse():
    s = Signal.model_validate(_base_signal_dict())
    dumped = s.model_dump(mode="json")
    s2 = Signal.model_validate(dumped)
    assert s2 == s
