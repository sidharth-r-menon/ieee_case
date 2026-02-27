#!/usr/bin/env python3
"""
Master runner for comparison evaluation.

Usage:
    cd robot_workcell_agent

    # Run all pipelines with 100 prompts (dry-run, no Genesis GPU):
    python -m comparisons.run_all

    # ── Batched runs (rate-limit friendly) ───────────────────────────────
    # Batch 1 – prompts 1-20:
    python -m comparisons.run_all --offset 0  --prompts 20

    # Batch 2 – prompts 21-40 (accumulates into summary with --resume):
    python -m comparisons.run_all --offset 20 --prompts 20 --resume

    # Batch 3 – prompts 41-60:
    python -m comparisons.run_all --offset 40 --prompts 20 --resume

    # --resume automatically finds the latest JSON log for each pipeline
    # and merges the prior records so aggregate stats cover ALL batches.

    # ── Other options ────────────────────────────────────────────────────
    # Run specific pipelines only:
    python -m comparisons.run_all --pipelines naive_llm langchain_tools

    # Run with Genesis simulation (requires GPU):
    python -m comparisons.run_all --enable-genesis

    # Run only low-complexity prompts:
    python -m comparisons.run_all --complexity low

    # Individual pipeline runners:
    python -m comparisons.run_all --pipelines naive_llm             --prompts 100
    python -m comparisons.run_all --pipelines langchain_tools       --prompts 100
    python -m comparisons.run_all --pipelines skills_no_disclosure  --prompts 100
    python -m comparisons.run_all --pipelines ours_full             --prompts 100
"""

from comparisons.evaluation.harness import main

if __name__ == "__main__":
    main()
