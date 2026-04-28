"""Shared signal contract for the2357.com stack.

The `Signal` model is the canonical wire format produced by news-consolidator
on Redis channels (`signals:trading`, `signals:poly`, `signals:critical`,
`signals:new`) and consumed by trading-agent, poly-agent, and pa-agent.

Versioning policy (semver):
- PATCH: docs, validators, no field changes.
- MINOR: new optional field, or new validator that only loosens parsing.
- MAJOR: any breaking shape change. Pin to a specific tag in consumers'
  pyproject.toml so a major bump can't silently land on next image build.

Producers MUST emit fields in the canonical schema. Consumers MUST tolerate
unknown future fields (pydantic's default extra='ignore' covers this).
"""
from signals_contract.signal import Signal

__all__ = ["Signal"]
__version__ = "0.1.0"
