# Test Suite

## Responsibility

Tests in this directory cover the supported package, CLI, benchmark, and analysis surface.

## Verification Flow

```bash
ruff check .
ruff format --check .
python -m pytest
python -m mypy
```

## Internal Notes

- The suite includes explicit checks for the supported import surface.
- Exploratory scripts are intentionally excluded from the default test surface.
