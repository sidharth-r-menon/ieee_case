"""
Structured evidence logger for comparison evaluations.

Captures every step of each pipeline iteration with timestamps,
inputs, outputs, and validation results for reproducibility.
"""

import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict

logger = logging.getLogger(__name__)


@dataclass
class ToolCall:
    """Record of a single tool/skill invocation."""
    timestamp: str
    tool_name: str
    stage: str  # "1", "2", "3"
    args_summary: str
    success: bool
    duration_s: float
    error: Optional[str] = None
    is_appropriate: bool = True  # Was this the right tool for the situation?


@dataclass
class StageResult:
    """Result of one pipeline stage."""
    stage: str
    success: bool
    message: str
    duration_s: float
    output_data: Optional[Dict[str, Any]] = None
    validation_details: Optional[Dict[str, Any]] = None
    tool_calls: List[ToolCall] = field(default_factory=list)


@dataclass
class IterationRecord:
    """Complete record of one pipeline iteration."""
    iteration_id: int
    pipeline_name: str
    prompt_id: str
    prompt_text: str
    start_time: str
    end_time: Optional[str] = None
    total_duration_s: float = 0.0
    stage_results: List[StageResult] = field(default_factory=list)
    overall_success: bool = False

    # Per-stage success flags for easy tabulation
    stage1_success: bool = False
    stage2_success: bool = False
    stage3_success: bool = False

    # Tool usage summary
    total_tool_calls: int = 0
    tool_hits: int = 0
    tool_misses: int = 0

    # LLM usage
    api_calls: int = 0
    tokens_prompt: int = 0
    tokens_completion: int = 0
    tokens_total: int = 0


class EvidenceLogger:
    """
        # Ensure every stage is counted for hit/miss, even if no tool call was made
        stages_present = set()
        for sr in self._current_record.stage_results:
            stages_present.add(sr.stage)
        
        for stage in ["1", "2", "3"]:
            if stage not in stages_present:
                # Add a dummy StageResult with a miss
                sr = StageResult(
                    stage=stage,
                    success=False,
                    message="No tool call made for this stage (auto-miss)",
                    duration_s=0.0,
                    output_data=None,
                    validation_details=None,
                    tool_calls=[ToolCall(
                        timestamp=datetime.now().isoformat(),
                        tool_name="<none>",
                        stage=stage,
                        args_summary="",
                        success=False,
                        duration_s=0.0,
                        error="No tool call made",
                        is_appropriate=False,
                    )]
                )
                self._current_record.stage_results.append(sr)
                if stage == "1":
                    self._current_record.stage1_success = False
                elif stage == "2":
                    self._current_record.stage2_success = False
                elif stage == "3":
                    self._current_record.stage3_success = False
    Captures structured evidence for a comparison pipeline run.

    Writes two outputs:
    - JSON log file with full structured data
    - Human-readable text log for quick inspection

    Pass ``resume_from`` (path to a prior JSON log) to accumulate statistics
    across multiple batched runs.  The prior records are counted in the summary
    but not re-written to the new log file.
    """

    def __init__(self, pipeline_name: str, logs_dir: Path,
                 resume_from: Optional[Path] = None):
        self.pipeline_name = pipeline_name
        self.logs_dir = logs_dir
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.json_path = self.logs_dir / f"{pipeline_name}_{timestamp}.json"
        self.text_path = self.logs_dir / f"{pipeline_name}_{timestamp}.log"

        self.records: List[IterationRecord] = []
        self._current_record: Optional[IterationRecord] = None
        self._current_stage: Optional[StageResult] = None
        self._stage_start: float = 0.0
        self._iter_start: float = 0.0

        # Prior-run counts loaded from a resume JSON log.
        self._prior: Optional[Dict[str, Any]] = None
        if resume_from and Path(resume_from).exists():
            self._load_prior(Path(resume_from))

        # Setup text file handler
        self._file_handler = logging.FileHandler(self.text_path, encoding="utf-8")
        self._file_handler.setFormatter(
            logging.Formatter("%(asctime)s  %(levelname)-8s  %(message)s", "%H:%M:%S")
        )
        self._logger = logging.getLogger(f"evidence.{pipeline_name}")
        self._logger.addHandler(self._file_handler)
        self._logger.setLevel(logging.DEBUG)
        self._logger.propagate = False

    def _load_prior(self, path: Path):
        """Load prior-run records and pre-aggregate their counts for get_summary()."""
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception as e:
            logger.warning(f"Could not load resume file {path}: {e}")
            return

        records = data.get("records", [])
        tool_stats = {
            "1": {"hits": 0, "misses": 0},
            "2": {"hits": 0, "misses": 0},
            "3": {"hits": 0, "misses": 0},
        }
        for r in records:
            for sr in r.get("stage_results", []):
                stage = sr.get("stage", "?")
                if stage in tool_stats:
                    for tc in sr.get("tool_calls", []):
                        if tc.get("is_appropriate") and tc.get("success"):
                            tool_stats[stage]["hits"] += 1
                        else:
                            tool_stats[stage]["misses"] += 1

        self._prior = {
            "n":       len(records),
            "s1":      sum(1 for r in records if r.get("stage1_success")),
            "s2":      sum(1 for r in records if r.get("stage2_success")),
            "s3":      sum(1 for r in records if r.get("stage3_success")),
            "overall": sum(1 for r in records if r.get("overall_success")),
            "tool_stats": tool_stats,
            "api_calls":          sum(r.get("api_calls", 0)          for r in records),
            "tokens_prompt":      sum(r.get("tokens_prompt", 0)      for r in records),
            "tokens_completion":  sum(r.get("tokens_completion", 0)  for r in records),
            "tokens_total":       sum(r.get("tokens_total", 0)       for r in records),
            "source": str(path),
        }
        logger.info(f"Resuming from {path.name} – loaded {self._prior['n']} prior record(s)")

    # ── Iteration lifecycle ──────────────────────────────────────

    def start_iteration(self, iteration_id: int, prompt_id: str, prompt_text: str):
        """Begin tracking a new iteration."""
        self._iter_start = time.time()
        self._current_record = IterationRecord(
            iteration_id=iteration_id,
            pipeline_name=self.pipeline_name,
            prompt_id=prompt_id,
            prompt_text=prompt_text,
            start_time=datetime.now().isoformat(),
        )
        self._log(f"\n{'='*80}")
        self._log(f"ITERATION {iteration_id} | Prompt: {prompt_id}")
        self._log(f"Pipeline: {self.pipeline_name}")
        self._log(f"{'='*80}")
        self._log(f"Prompt: {prompt_text[:200]}...")

    def end_iteration(self):
        """Finalize the current iteration record."""
        if not self._current_record:
            return

        self._current_record.end_time = datetime.now().isoformat()
        self._current_record.total_duration_s = time.time() - self._iter_start

        # Compute per-stage success
        for sr in self._current_record.stage_results:
            if sr.stage == "1":
                self._current_record.stage1_success = sr.success
            elif sr.stage == "2":
                self._current_record.stage2_success = sr.success
            elif sr.stage == "3":
                self._current_record.stage3_success = sr.success

        self._current_record.overall_success = (
            self._current_record.stage1_success
            and self._current_record.stage2_success
            and self._current_record.stage3_success
        )

        # Tool usage summary
        all_calls = []
        for sr in self._current_record.stage_results:
            all_calls.extend(sr.tool_calls)
        self._current_record.total_tool_calls = len(all_calls)
        self._current_record.tool_hits = sum(1 for c in all_calls if c.is_appropriate)
        self._current_record.tool_misses = sum(1 for c in all_calls if not c.is_appropriate)

        self.records.append(self._current_record)

        self._log(f"\n--- Iteration {self._current_record.iteration_id} Summary ---")
        self._log(f"Overall: {'PASS' if self._current_record.overall_success else 'FAIL'}")
        self._log(f"S1={self._current_record.stage1_success} S2={self._current_record.stage2_success} S3={self._current_record.stage3_success}")
        self._log(f"Duration: {self._current_record.total_duration_s:.1f}s")
        self._log(f"Tool calls: {self._current_record.total_tool_calls} (hits={self._current_record.tool_hits}, misses={self._current_record.tool_misses})")
        self._log(
            f"LLM usage: {self._current_record.api_calls} API call(s), "
            f"{self._current_record.tokens_total} tokens "
            f"(prompt={self._current_record.tokens_prompt}, "
            f"completion={self._current_record.tokens_completion})"
        )

        # Flush JSON after every iteration
        self._save_json()

    # ── Stage lifecycle ──────────────────────────────────────────

    def start_stage(self, stage: str):
        """Begin tracking a stage."""
        self._stage_start = time.time()
        self._current_stage = StageResult(
            stage=stage, success=False, message="", duration_s=0.0
        )
        self._log(f"\n--- Stage {stage} ---")

    def end_stage(self, success: bool, message: str,
                  output_data: Dict[str, Any] = None,
                  validation_details: Dict[str, Any] = None):
        """Finalize a stage."""
        if not self._current_stage:
            return

        self._current_stage.success = success
        self._current_stage.message = message
        self._current_stage.duration_s = time.time() - self._stage_start
        self._current_stage.output_data = output_data
        self._current_stage.validation_details = validation_details

        if self._current_record:
            self._current_record.stage_results.append(self._current_stage)

        status = "PASS" if success else "FAIL"
        self._log(f"Stage {self._current_stage.stage}: {status} ({self._current_stage.duration_s:.1f}s) – {message}")

    # ── LLM usage tracking ──────────────────────────────────────

    def log_llm_usage(self, api_calls: int, prompt_tokens: int, completion_tokens: int):
        """Record LLM API call and token counts for the current iteration."""
        if not self._current_record:
            return
        self._current_record.api_calls += api_calls
        self._current_record.tokens_prompt += prompt_tokens
        self._current_record.tokens_completion += completion_tokens
        self._current_record.tokens_total += prompt_tokens + completion_tokens
        self._log(
            f"  LLM usage: +{api_calls} call(s), "
            f"+{prompt_tokens} prompt tok, +{completion_tokens} completion tok"
        )

    # ── Tool call tracking ───────────────────────────────────────

    def log_tool_call(self, tool_name: str, stage: str, args_summary: str,
                      success: bool, duration_s: float, error: str = None,
                      is_appropriate: bool = True):
        """Record a tool/skill invocation."""
        call = ToolCall(
            timestamp=datetime.now().isoformat(),
            tool_name=tool_name,
            stage=stage,
            args_summary=args_summary[:200],
            success=success,
            duration_s=duration_s,
            error=error,
            is_appropriate=is_appropriate,
        )
        if self._current_stage:
            self._current_stage.tool_calls.append(call)

        status = "OK" if success else "FAIL"
        appropriate = "" if is_appropriate else " [INAPPROPRIATE]"
        self._log(f"  Tool: {tool_name} → {status} ({duration_s:.2f}s){appropriate}")

    # ── Utility ──────────────────────────────────────────────────

    def _log(self, msg: str):
        self._logger.info(msg)

    def _save_json(self):
        """Write all records to JSON."""
        total_api   = sum(r.api_calls         for r in self.records)
        total_tok   = sum(r.tokens_total      for r in self.records)
        total_prom  = sum(r.tokens_prompt     for r in self.records)
        total_comp  = sum(r.tokens_completion for r in self.records)
        n = max(len(self.records), 1)
        data = {
            "pipeline": self.pipeline_name,
            "generated_at": datetime.now().isoformat(),
            "total_iterations": len(self.records),
            "llm_usage_totals": {
                "total_api_calls":        total_api,
                "total_tokens":           total_tok,
                "total_tokens_prompt":    total_prom,
                "total_tokens_completion": total_comp,
                "avg_api_calls_per_iter": round(total_api / n, 1),
                "avg_tokens_per_iter":    round(total_tok  / n, 1),
            },
            "records": [asdict(r) for r in self.records],
        }
        self.json_path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")

    def get_summary(self) -> Dict[str, Any]:
        """Return aggregate summary statistics, merging any prior-run data."""
        p = self._prior or {
            "n": 0, "s1": 0, "s2": 0, "s3": 0, "overall": 0,
            "tool_stats": {
                "1": {"hits": 0, "misses": 0},
                "2": {"hits": 0, "misses": 0},
                "3": {"hits": 0, "misses": 0},
            },
            "api_calls": 0,
            "tokens_prompt": 0,
            "tokens_completion": 0,
            "tokens_total": 0,
        }

        n_new = len(self.records)
        n = max(n_new + p["n"], 1)

        s1      = sum(1 for r in self.records if r.stage1_success)      + p["s1"]
        s2      = sum(1 for r in self.records if r.stage2_success)      + p["s2"]
        s3      = sum(1 for r in self.records if r.stage3_success)      + p["s3"]
        overall = sum(1 for r in self.records if r.overall_success)     + p["overall"]

        # Per-stage tool stats
        stage_tool_stats = {
            "1": {"hits": p["tool_stats"]["1"]["hits"], "misses": p["tool_stats"]["1"]["misses"]},
            "2": {"hits": p["tool_stats"]["2"]["hits"], "misses": p["tool_stats"]["2"]["misses"]},
            "3": {"hits": p["tool_stats"]["3"]["hits"], "misses": p["tool_stats"]["3"]["misses"]},
        }
        for r in self.records:
            # Stage 1 and 2: count hits/misses as before
            for sr in r.stage_results:
                if sr.stage in ("1", "2"):
                    found_hit = any(tc.is_appropriate for tc in sr.tool_calls)
                    if found_hit:
                        stage_tool_stats[sr.stage]["hits"] += 1
                    else:
                        stage_tool_stats[sr.stage]["misses"] += 1
            # Stage 3: count a hit if any appropriate tool was called (consistent with S1/S2)
            stage3_calls = [sr for sr in r.stage_results if sr.stage == "3"]
            if stage3_calls:
                found_hit = any(tc.is_appropriate for tc in stage3_calls[0].tool_calls)
                if found_hit:
                    stage_tool_stats["3"]["hits"] += 1
                else:
                    stage_tool_stats["3"]["misses"] += 1

        # LLM usage totals
        total_api_calls       = sum(r.api_calls        for r in self.records) + p.get("api_calls", 0)
        total_tokens_prompt   = sum(r.tokens_prompt    for r in self.records) + p.get("tokens_prompt", 0)
        total_tokens_comp     = sum(r.tokens_completion for r in self.records) + p.get("tokens_completion", 0)
        total_tokens          = sum(r.tokens_total     for r in self.records) + p.get("tokens_total", 0)

        summary = {
            "pipeline": self.pipeline_name,
            "iterations": n,
            "stage1_success_rate": s1 / n,
            "stage2_success_rate": s2 / n,
            "stage3_success_rate": s3 / n,
            "overall_success_rate": overall / n,
            "avg_success_rate": (s1 + s2 + s3) / (3 * n),
            "tool_stats_by_stage": stage_tool_stats,
            "llm_usage": {
                "total_api_calls":        total_api_calls,
                "total_tokens":           total_tokens,
                "total_tokens_prompt":    total_tokens_prompt,
                "total_tokens_completion": total_tokens_comp,
                "avg_api_calls_per_iter": total_api_calls / n,
                "avg_tokens_per_iter":    total_tokens / n,
            },
            "json_log": str(self.json_path),
            "text_log": str(self.text_path),
        }
        if self._prior:
            summary["resumed_from"] = self._prior["source"]
            summary["prior_iterations"] = self._prior["n"]
            summary["new_iterations"] = n_new
        return summary
