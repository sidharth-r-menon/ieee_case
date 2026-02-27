"""
Metrics computation for comparison tables.

Provides functions to compute Table 1 (success rate) and Table 2 (tool hit/miss)
from evidence logger JSON files, including for retrospective analysis.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


def load_evidence_json(json_path: str) -> Dict[str, Any]:
    """Load an evidence JSON log file."""
    return json.loads(Path(json_path).read_text(encoding="utf-8"))


def compute_table1_from_evidence(evidence_files: Dict[str, str]) -> Dict[str, Dict[str, float]]:
    """
    Compute Table 1 (success rate per stage) from evidence JSON files.

    Args:
        evidence_files: Dict mapping pipeline_name → JSON log file path.

    Returns:
        Dict mapping pipeline_name → {stage1, stage2, stage3, avg, overall}.
    """
    table1 = {}

    for pipeline_name, json_path in evidence_files.items():
        try:
            data = load_evidence_json(json_path)
            records = data.get("records", [])
            n = max(len(records), 1)

            s1 = sum(1 for r in records if r.get("stage1_success")) / n
            s2 = sum(1 for r in records if r.get("stage2_success")) / n
            s3 = sum(1 for r in records if r.get("stage3_success")) / n
            overall = sum(1 for r in records if r.get("overall_success")) / n
            avg = (s1 + s2 + s3) / 3

            table1[pipeline_name] = {
                "stage1": s1,
                "stage2": s2,
                "stage3": s3,
                "avg": avg,
                "overall": overall,
                "n": len(records),
            }
        except Exception as e:
            logger.error(f"Error loading {pipeline_name}: {e}")
            table1[pipeline_name] = {"stage1": 0, "stage2": 0, "stage3": 0, "avg": 0, "overall": 0, "n": 0}

    return table1


def compute_table2_from_evidence(evidence_files: Dict[str, str]) -> Dict[str, Dict[str, Any]]:
    """
    Compute Table 2 (tool hit/miss per stage) from evidence JSON files.

    Args:
        evidence_files: Dict mapping pipeline_name → JSON log file path.

    Returns:
        Dict mapping pipeline_name → {stage1_hits, stage1_misses, ...}.
    """
    table2 = {}

    for pipeline_name, json_path in evidence_files.items():
        try:
            data = load_evidence_json(json_path)
            records = data.get("records", [])

            stage_stats = {
                "1": {"hits": 0, "misses": 0, "total": 0},
                "2": {"hits": 0, "misses": 0, "total": 0},
                "3": {"hits": 0, "misses": 0, "total": 0},
            }

            for record in records:
                for sr in record.get("stage_results", []):
                    stage = sr.get("stage", "?")
                    if stage not in stage_stats:
                        continue
                    for tc in sr.get("tool_calls", []):
                        stage_stats[stage]["total"] += 1
                        if tc.get("is_appropriate") and tc.get("success"):
                            stage_stats[stage]["hits"] += 1
                        else:
                            stage_stats[stage]["misses"] += 1

            # Compute hit rates
            for s in stage_stats.values():
                s["hit_rate"] = s["hits"] / s["total"] if s["total"] > 0 else 0.0

            total_hits = sum(s["hits"] for s in stage_stats.values())
            total_all = sum(s["total"] for s in stage_stats.values())
            avg_hit_rate = total_hits / total_all if total_all > 0 else 0.0

            table2[pipeline_name] = {
                "stage1": stage_stats["1"],
                "stage2": stage_stats["2"],
                "stage3": stage_stats["3"],
                "avg_hit_rate": avg_hit_rate,
                "n": len(records),
            }
        except Exception as e:
            logger.error(f"Error loading {pipeline_name}: {e}")
            table2[pipeline_name] = {
                "stage1": {"hits": 0, "misses": 0, "total": 0, "hit_rate": 0},
                "stage2": {"hits": 0, "misses": 0, "total": 0, "hit_rate": 0},
                "stage3": {"hits": 0, "misses": 0, "total": 0, "hit_rate": 0},
                "avg_hit_rate": 0, "n": 0,
            }

    return table2


def print_table1(table1: Dict[str, Dict[str, float]]):
    """Print Table 1 to console."""
    NAMES = {
        "naive_llm": "Naïve LLM (Zero-Shot)",
        "langchain_tools": "LangChain (Tools + RAG)",
        "skills_no_disclosure": "Skills (No Disclosure)",
        "ours_full": "Ours (Full Pipeline)",
    }

    print("\n" + "=" * 72)
    print("TABLE 1: Pipeline Success Rate (per stage)")
    print("=" * 72)
    print(f"{'Implementation':<30} {'Stage 1':>8} {'Stage 2':>8} {'Stage 3':>8} {'Avg':>8} {'N':>4}")
    print("-" * 72)

    for name, stats in table1.items():
        fn = NAMES.get(name, name)
        print(
            f"{fn:<30} "
            f"{stats['stage1']:>7.1%} "
            f"{stats['stage2']:>7.1%} "
            f"{stats['stage3']:>7.1%} "
            f"{stats['avg']:>7.1%} "
            f"{stats['n']:>4}"
        )
    print("=" * 72)


def print_table2(table2: Dict[str, Dict[str, Any]]):
    """Print Table 2 to console."""
    NAMES = {
        "langchain_tools": "LangChain (Tools + RAG)",
        "skills_no_disclosure": "Skills (No Disclosure)",
        "ours_full": "Ours (Full Pipeline)",
    }

    print("\n" + "=" * 90)
    print("TABLE 2: Tool/Skill Hit & Miss (per stage)")
    print("=" * 90)
    print(f"{'Implementation':<25} {'S1 Hit':>6} {'S1 Miss':>7} {'S2 Hit':>6} {'S2 Miss':>7} {'S3 Hit':>6} {'S3 Miss':>7} {'Avg HR':>7}")
    print("-" * 90)

    for name, stats in table2.items():
        if name == "naive_llm":
            continue
        fn = NAMES.get(name, name)
        s1 = stats["stage1"]
        s2 = stats["stage2"]
        s3 = stats["stage3"]
        print(
            f"{fn:<25} "
            f"{s1['hits']:>6} {s1['misses']:>7} "
            f"{s2['hits']:>6} {s2['misses']:>7} "
            f"{s3['hits']:>6} {s3['misses']:>7} "
            f"{stats['avg_hit_rate']:>6.1%}"
        )
    print("=" * 90)


def generate_latex_tables(table1, table2) -> str:
    """Generate LaTeX-formatted tables for paper inclusion."""
    lines = []

    # Table 1
    lines.append("% Table 1: Pipeline Success Rate")
    lines.append("\\begin{table}[h]")
    lines.append("\\centering")
    lines.append("\\caption{Pipeline Success Rate by Stage}")
    lines.append("\\label{tab:success_rate}")
    lines.append("\\begin{tabular}{lcccc}")
    lines.append("\\toprule")
    lines.append("Implementation & Stage 1 & Stage 2 & Stage 3 & Avg \\\\")
    lines.append("\\midrule")

    NAMES = {
        "naive_llm": "Na\\\"ive LLM",
        "langchain_tools": "LangChain",
        "skills_no_disclosure": "Skills (No PD)",
        "ours_full": "\\textbf{Ours}",
    }

    for name, stats in table1.items():
        fn = NAMES.get(name, name)
        lines.append(
            f"{fn} & {stats['stage1']:.1%} & {stats['stage2']:.1%} "
            f"& {stats['stage3']:.1%} & {stats['avg']:.1%} \\\\"
        )

    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    lines.append("\\end{table}")
    lines.append("")

    # Table 2
    lines.append("% Table 2: Tool Hit/Miss Rate")
    lines.append("\\begin{table}[h]")
    lines.append("\\centering")
    lines.append("\\caption{Tool/Skill Hit \\& Miss Rate by Stage}")
    lines.append("\\label{tab:tool_usage}")
    lines.append("\\begin{tabular}{lccccccc}")
    lines.append("\\toprule")
    lines.append("Implementation & S1 H & S1 M & S2 H & S2 M & S3 H & S3 M & Avg HR \\\\")
    lines.append("\\midrule")

    for name, stats in table2.items():
        if name == "naive_llm":
            continue
        fn = NAMES.get(name, name)
        s1, s2, s3 = stats["stage1"], stats["stage2"], stats["stage3"]
        lines.append(
            f"{fn} & {s1['hits']} & {s1['misses']} "
            f"& {s2['hits']} & {s2['misses']} "
            f"& {s3['hits']} & {s3['misses']} "
            f"& {stats['avg_hit_rate']:.1%} \\\\"
        )

    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    lines.append("\\end{table}")

    return "\n".join(lines)


def compute_table3_from_evidence(evidence_files: Dict[str, str]) -> Dict[str, Dict[str, Any]]:
    """
    Compute Table 3 (LLM API calls and token usage) from evidence JSON files.

    Returns:
        Dict mapping pipeline_name → {total_api_calls, total_tokens, avg_api_calls, avg_tokens, n}.
    """
    table3 = {}
    for pipeline_name, json_path in evidence_files.items():
        try:
            data = load_evidence_json(json_path)
            # Prefer top-level totals written by _save_json
            totals = data.get("llm_usage_totals", {})
            records = data.get("records", [])
            n = max(len(records), 1)

            if totals:
                total_calls = totals.get("total_api_calls", 0)
                total_tokens = totals.get("total_tokens", 0)
                total_prompt = totals.get("total_tokens_prompt", 0)
                total_comp   = totals.get("total_tokens_completion", 0)
            else:
                # Fall back to summing per-record fields
                total_calls  = sum(r.get("api_calls", 0)          for r in records)
                total_prompt = sum(r.get("tokens_prompt", 0)      for r in records)
                total_comp   = sum(r.get("tokens_completion", 0)  for r in records)
                total_tokens = sum(r.get("tokens_total", 0)       for r in records)

            table3[pipeline_name] = {
                "total_api_calls":        total_calls,
                "total_tokens":           total_tokens,
                "total_tokens_prompt":    total_prompt,
                "total_tokens_completion": total_comp,
                "avg_api_calls_per_iter": round(total_calls  / n, 1),
                "avg_tokens_per_iter":    round(total_tokens / n, 1),
                "n": len(records),
            }
        except Exception as e:
            logger.error(f"Error loading {pipeline_name} for table3: {e}")
            table3[pipeline_name] = {
                "total_api_calls": 0, "total_tokens": 0,
                "total_tokens_prompt": 0, "total_tokens_completion": 0,
                "avg_api_calls_per_iter": 0.0, "avg_tokens_per_iter": 0.0,
                "n": 0,
            }
    return table3


def print_table3(table3: Dict[str, Dict[str, Any]]):
    """Print Table 3 (API calls + token usage) to console."""
    NAMES = {
        "naive_llm":            "Naïve LLM (Zero-Shot)",
        "langchain_tools":      "LangChain (Tools + RAG)",
        "skills_no_disclosure": "Skills (No Disclosure)",
        "ours_full":            "Ours (Full Pipeline)",
    }
    print("\n" + "=" * 80)
    print("TABLE 3: LLM API Calls and Token Usage")
    print("=" * 80)
    print(f"{'Implementation':<28} {'API Calls':>10} {'Avg/Iter':>9} {'Total Tok':>11} {'Avg Tok/Iter':>13} {'N':>4}")
    print("-" * 80)
    for name, stats in table3.items():
        fn = NAMES.get(name, name)
        print(
            f"{fn:<28} "
            f"{stats['total_api_calls']:>10} "
            f"{stats['avg_api_calls_per_iter']:>9.1f} "
            f"{stats['total_tokens']:>11} "
            f"{stats['avg_tokens_per_iter']:>13.0f} "
            f"{stats['n']:>4}"
        )
    print("=" * 80)
