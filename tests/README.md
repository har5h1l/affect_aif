# Test Suite

Tests in this directory cover the supported package and CLI surface.

The default verification flow is:

```bash
ruff check .
ruff format --check .
python -m pytest
python -m mypy
```

Archived prototypes and exploratory scripts are intentionally excluded from the default test surface.
