# CLI Helpers

## Responsibility

This package contains shared utilities for the supported command-line wrappers in `scripts/`.

## Public Surface

The package-level import surface is `affect_aif.cli`. It re-exports:

- `filter_primary_runs`
- `load_results_table`
- `slugify_name`

## Key Modules

- `common.py`: shared results-loading and slug utilities

## Internal / Compatibility Notes

- The CLI helpers are intentionally small and are meant to be consumed by the supported scripts rather than by ad hoc shell entry points.
