# Script Inventory

## Responsibility

This directory contains the supported CLI entry points around the package code.

## Core Supported Workflow

These wrappers define the stable end-user workflow documented in `docs/operations/cli.md`:

- `experiment/run.py`
- `experiment/smoke.py`
- `experiment/inspect.py`
- `experiment/preliminary.py`
- `analysis/analyze.py`
- `analysis/summarize.py`
- `analysis/visualize.py`
- `analysis/model_comparison.py`
- `benchmark/analyze.py`
- `benchmark/run.py`

## Internal Notes

- These scripts are intentionally thin and defer real work to the package modules.
- There are no supported top-level `scripts/*.py` entry points; use the grouped paths above.
