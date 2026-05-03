"""Shared validators and helpers for the signals-contract package."""
import json
from typing import Any


def _parse_json_string(v: Any) -> Any:
    """Tolerate publishers that double-encode JSONB as strings.

    Some upstream paths (e.g. ad-hoc psql republish via NOTIFY, or a
    producer that json.dumps()'d a dict before passing to a JSONB-codec
    column) produce a string where a dict is expected. We try once to
    parse, fall back to passing the string through if it's not JSON.
    """
    if isinstance(v, str):
        try:
            return json.loads(v)
        except json.JSONDecodeError:
            return v
    return v
