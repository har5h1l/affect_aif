#!/usr/bin/env bash
################################################################################
# affect_aif — Main Entry Point
#
# Interactive menu and pipeline orchestrator for running experiments,
# analysis, and tests. Follows the thin orchestrator pattern.
#
# Usage:
#   ./run.sh                          # Interactive menu
#   ./run.sh --test                   # Run all tests
#   ./run.sh --experiment <config>    # Run single experiment
#   ./run.sh --analyze <results.csv>  # Analyze results
#   ./run.sh --pipeline <config>      # Full pipeline: test → experiment → analyze
#   ./run.sh --smoke [config]         # Quick smoke test (5 seeds, 50 rounds)
#
# Exit codes: 0 = success, 1 = failure
################################################################################

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ── Environment Setup ────────────────────────────────────────────────────────

setup_venv() {
    if [ -f ".venv/bin/activate" ]; then
        source .venv/bin/activate
    elif [ -f ".envrc" ]; then
        eval "$(direnv export bash 2>/dev/null)" || true
    fi
}

check_python() {
    if ! command -v python &>/dev/null; then
        echo "ERROR: python not found. Activate your venv first."
        exit 1
    fi
}

setup_venv
check_python

# ── Helpers ──────────────────────────────────────────────────────────────────

run_tests() {
    echo "══════════════════════════════════════════════════════"
    echo "  Running tests"
    echo "══════════════════════════════════════════════════════"
    python -m pytest tests/ -v
    echo ""
    echo "✓ All tests passed"
}

run_experiment() {
    local config="$1"
    local output_dir="${2:-results}"
    local batch_name
    batch_name="$(basename "$config" .json)"

    echo "══════════════════════════════════════════════════════"
    echo "  Running experiment: $config"
    echo "══════════════════════════════════════════════════════"
    python scripts/run_experiment.py \
        --config "$config" \
        --output-dir "$output_dir" \
        --batch-name "$batch_name"
    echo ""
    echo "✓ Experiment complete: $output_dir/$batch_name/"
}

run_analysis() {
    local results="$1"
    local output_dir
    output_dir="$(dirname "$results")/figures"

    echo "══════════════════════════════════════════════════════"
    echo "  Analyzing: $results"
    echo "══════════════════════════════════════════════════════"
    python scripts/run_analysis.py \
        --results "$results" \
        --output-dir "$output_dir"
    echo ""
    echo "✓ Analysis complete: $output_dir/"
}

run_smoke() {
    local config="${1:-affect_aif/configs/default.json}"

    echo "══════════════════════════════════════════════════════"
    echo "  Smoke test: $config (5 seeds, 50 rounds)"
    echo "══════════════════════════════════════════════════════"
    python scripts/run_preliminary.py \
        --replications 5 \
        --output results/smoke_test.csv \
        --config "$config" 2>/dev/null || \
    python scripts/run_preliminary.py \
        --replications 5 \
        --output results/smoke_test.csv
    echo ""
    echo "✓ Smoke test complete"
}

run_pipeline() {
    local config="$1"
    local batch_name
    batch_name="$(basename "$config" .json)"
    local slug
    slug="$(echo "$batch_name" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/_/g')"

    echo "══════════════════════════════════════════════════════"
    echo "  Full Pipeline: $config"
    echo "══════════════════════════════════════════════════════"
    echo ""

    echo "[1/3] Tests"
    run_tests
    echo ""

    echo "[2/3] Experiment"
    run_experiment "$config"
    echo ""

    echo "[3/3] Analysis"
    run_analysis "results/$batch_name/$slug/results.csv"
    echo ""

    echo "══════════════════════════════════════════════════════"
    echo "  ✓ Pipeline complete"
    echo "══════════════════════════════════════════════════════"
}

show_menu() {
    echo ""
    echo "══════════════════════════════════════════════════════"
    echo "  affect_aif — Research Pipeline"
    echo "══════════════════════════════════════════════════════"
    echo ""
    echo "  Tests:"
    echo "    1. Run all tests"
    echo ""
    echo "  Experiments:"
    echo "    2. Run default experiment"
    echo "    3. Run betrayal stress experiment"
    echo "    4. Run graded trust experiment"
    echo "    5. Run custom config"
    echo ""
    echo "  Analysis:"
    echo "    6. Analyze results file"
    echo ""
    echo "  Pipeline:"
    echo "    7. Full pipeline (default)"
    echo "    8. Full pipeline (betrayal stress)"
    echo "    9. Smoke test"
    echo ""
    echo "    0. Exit"
    echo ""
    echo "══════════════════════════════════════════════════════"
    read -rp "  Select option: " choice

    case "$choice" in
        1) run_tests ;;
        2) run_experiment "affect_aif/configs/default.json" ;;
        3) run_experiment "affect_aif/configs/betrayal_stress.json" ;;
        4) run_experiment "affect_aif/configs/graded_trust.json" ;;
        5)
            read -rp "  Config path: " config_path
            run_experiment "$config_path"
            ;;
        6)
            read -rp "  Results CSV path: " results_path
            run_analysis "$results_path"
            ;;
        7) run_pipeline "affect_aif/configs/default.json" ;;
        8) run_pipeline "affect_aif/configs/betrayal_stress.json" ;;
        9) run_smoke ;;
        0) exit 0 ;;
        *) echo "  Invalid option." ;;
    esac
}

# ── CLI Dispatch ─────────────────────────────────────────────────────────────

case "${1:-}" in
    --test)
        run_tests
        ;;
    --experiment)
        [ -z "${2:-}" ] && { echo "Usage: $0 --experiment <config.json>"; exit 1; }
        run_experiment "$2"
        ;;
    --analyze)
        [ -z "${2:-}" ] && { echo "Usage: $0 --analyze <results.csv>"; exit 1; }
        run_analysis "$2"
        ;;
    --pipeline)
        [ -z "${2:-}" ] && { echo "Usage: $0 --pipeline <config.json>"; exit 1; }
        run_pipeline "$2"
        ;;
    --smoke)
        run_smoke "${2:-}"
        ;;
    --help|-h)
        echo "Usage: $0 [--test|--experiment <config>|--analyze <csv>|--pipeline <config>|--smoke [config]]"
        echo ""
        echo "Options:"
        echo "  (no args)              Interactive menu"
        echo "  --test                 Run all tests"
        echo "  --experiment <config>  Run experiment with config JSON"
        echo "  --analyze <csv>        Analyze results CSV"
        echo "  --pipeline <config>    Full pipeline: test → run → analyze"
        echo "  --smoke [config]       Quick smoke test (5 seeds)"
        echo "  --help                 Show this help"
        ;;
    "")
        while true; do
            show_menu
            echo ""
            read -rp "  Press Enter to continue..." _
        done
        ;;
    *)
        echo "Unknown option: $1"
        echo "Run '$0 --help' for usage."
        exit 1
        ;;
esac
