# Test Suite

## Responsibility

Tests in this directory cover the supported package, CLI, benchmark, and compatibility surface.

## Verification Flow

```bash
ruff check .
ruff format --check .
python -m pytest
python -m mypy
```

## Internal / Compatibility Notes

- The suite includes explicit checks for the supported import surface and legacy compatibility shims.
- Archived prototypes and exploratory scripts are intentionally excluded from the default test surface.
