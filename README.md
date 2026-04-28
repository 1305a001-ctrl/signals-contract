# signals-contract

Shared pydantic `Signal` model — the canonical wire format on Redis between
news-consolidator (producer) and trading-agent / poly-agent / pa-agent
(consumers).

## Why this exists

Three separate consumer services each had their own copy of the same
pydantic `Signal` class. Field changes had to be coordinated by hand across
3 repos, with nothing enforcing they stayed in sync. This package is the
single source of truth.

## Usage

In a consumer's `pyproject.toml`:

```toml
dependencies = [
    "signals-contract @ https://github.com/1305a001-ctrl/signals-contract/archive/refs/tags/v0.1.0.tar.gz",
]
```

Pin to a tag (not `main`) so a contract change can't silently land at next
image build.

```python
from signals_contract import Signal

signal = Signal.model_validate(redis_message_json)
```

## Versioning

Semver:

- **PATCH** — docs, tests, validator behaviour with no field changes
- **MINOR** — new optional field, looser parsing
- **MAJOR** — breaking shape change

When a major bump lands, every consumer's `pyproject.toml` pin must be
updated intentionally — the producer (news-consolidator) and consumers
should redeploy together.

## Tests

```bash
pip install -e '.[dev]'
pytest -q
ruff check .
```
