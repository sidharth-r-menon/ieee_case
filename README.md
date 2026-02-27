# Robot Workcell Design Agent

An AI-powered agent for automated robotic workcell design using the Anthropic skills pattern with **progressive disclosure** and executable skill scripts. Includes a multi-pipeline evaluation framework for benchmarking agent design strategies.

---

## Project Structure

```
robot_workcell_agent/
├── streamlit_app.py          # Streamlit chat UI
├── pyproject.toml            # Project metadata & dependencies
├── .env                      # API credentials (git-ignored)
├── src/
│   ├── agent.py              # Pydantic AI agent (skill tools only)
│   ├── skill_toolset.py      # Progressive disclosure + execution tools
│   ├── skill_loader.py       # Skill discovery from filesystem
│   ├── skill_tools.py        # load / read / list skill implementations
│   ├── providers.py          # Azure OpenAI / Qwen LLM configuration
│   ├── settings.py           # Environment-based settings (dataclass)
│   ├── schemas.py            # Pydantic schemas: Stage1Output, etc.
│   ├── prompts.py            # System prompt with 3-stage workflow
│   ├── runtime.py            # Agent runtime orchestration
│   └── dependencies.py       # Dependency injection
├── skills/
│   ├── request_interpreter/  # Stage 1 – NL → structured JSON
│   │   ├── SKILL.md
│   │   ├── scripts/interpret_request.py
│   │   └── references/
│   │       ├── gap_analysis_guide.md
│   │       ├── standard_objects.md
│   │       ├── robot_selection_guide.md
│   │       └── robots/{ur5,ur3,ur10,franka_emika_panda,kuka_kr3}.md
│   ├── placement_solver/     # Stage 2 – Deterministic layout optimization
│   │   ├── SKILL.md
│   │   └── scripts/solve_placement.py
│   ├── genesis_scene_builder/# Stage 3 – Physics scene + 6-phase trajectory
│   │   ├── SKILL.md
│   │   └── scripts/build_and_execute.py
│   └── simulation_validator/ # DEPRECATED – trajectory integrated into build_and_execute
│       ├── SKILL.md
│       └── scripts/execute_and_validate.py
├── comparisons/              # 4-pipeline evaluation framework
│   ├── evaluation/
│   │   ├── harness.py        # CLI entry point + report generator
│   │   └── ours_pipeline.py  # "Ours (Full)" pipeline wrapper
│   ├── naive_llm/            # Baseline: single zero-shot LLM call
│   ├── langchain_tools/      # LangChain: tool calling + RAG
│   ├── skills_no_disclosure/ # Skills loaded upfront, no progressive disclosure
│   └── shared/
│       ├── validators.py     # Stage 1/2/3 semantic validators
│       ├── stage_scripts.py  # Subprocess wrappers for skill scripts
│       ├── evidence_logger.py# Structured per-iteration logging
│       ├── test_prompts.py   # 100 standardized palletizing prompts
│       └── config.py         # Paths, timeouts, logging config
└── tests/
```

**External asset directories** (at repository root):
```
mujoco_menagerie/             # 60+ robot MJCF/URDF models (Google DeepMind)
workcell_components/
├── boxes/                    # cardboard_box.xml, medium_box.xml, small_box.xml
├── conveyors/                # conveyor_belt.xml
├── pallets/                  # euro_pallet.xml
├── pedestals/                # robot_pedestal.xml
├── tables/                   # workbench.xml
└── robots/universal_robots_ur5e/  # ur5e_with_suction.xml + mesh assets
```

---

## Quick Start

### Prerequisites
- Python 3.11+, GPU recommended for Stage 3 Genesis simulation
- Azure OpenAI (GPT-4o) **or** a locally-served Qwen3-14B endpoint

### Configure credentials

```bash
# robot_workcell_agent/.env
MODEL_PROVIDER=azure
AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-12-01-preview
AZURE_OPENAI_DEPLOYMENT=gpt-4o

# Optional – local Qwen LoRA endpoint
# MODEL_PROVIDER=qwen
# QWEN_BASE_MODEL=Qwen/Qwen3-14B
# QWEN_API_BASE_URL=http://localhost:8000/v1
# QWEN_API_KEY=sk-no-key-required
# QWEN_TEMPERATURE=0.6
# QWEN_TOP_P=0.95
# QWEN_MAX_TOKENS=8192
```

### Install & run

```bash
cd robot_workcell_agent
pip install -r requirements.txt

# Streamlit chat UI
streamlit run streamlit_app.py   # → http://localhost:8501
```

---

## 3-Stage Pipeline

### Stage 1 – Request Interpretation

Agent loads `request_interpreter` skill (progressive disclosure), reads reference guides, then executes:

```bash
python skills/request_interpreter/scripts/interpret_request.py   # stdin: prompt JSON
```

Reference guides loaded on-demand:
- `gap_analysis_guide.md` – identifies missing required info  
- `robot_selection_guide.md` + `robots/*.md` – robot selection based on payload / reach  
- `standard_objects.md` – dimension inference for common objects  

**Stage 1 JSON output** (stored via `submit_stage1_json` tool):
```jsonc
{
  "robot_selection": { "model": "ur5e", "payload_kg": 5.0, "reach_mm": 850 },
  "workcell_components": [
    { "component_type": "pedestal", "name": "robot_pedestal", "dimensions": [0.6,0.6,0.5] },
    { "component_type": "conveyor", "name": "belt_conveyor",  "dimensions": [2.0,0.64,0.82] },
    { "component_type": "pallet",   "name": "euro_pallet",    "dimensions": [1.2,0.8,0.15] },
    { "component_type": "carton",   "name": "cardboard_carton","dimensions": [0.3,0.3,0.3] }
  ],
  "throughput_requirement": { "items_per_hour": 120, "cycle_time_seconds": 30 },
  "spatial_reasoning": { "zones": [...] }
}
```

### Stage 2 – Layout Optimization

Deterministic solver via `layout_generator.py`:

```bash
python skills/placement_solver/scripts/solve_placement.py   # stdin: Stage 1 JSON
```

- Robot pedestal always at origin [0, 0, 0]  
- Components distributed in reachable zones (front-left, front-right, side)  
- Collision detection + IK reachability validation  
- Output: 3D XYZ positions for every component

### Stage 3 – Genesis Simulation

```bash
python skills/genesis_scene_builder/scripts/build_and_execute.py   # stdin: merged JSON
```

Pre-processing before script launch:
- `prepare_genesis_input()` – merges Stage 1 + Stage 2, auto-adds `execute_trajectory=True`, `z_lift=0.4`, motion targets  
- `fix_genesis_paths()` – resolves keyword-based component names to absolute MJCF paths on disk  

**6-phase trajectory** inside Genesis (`gs.gpu` backend):

| Phase | Action |
|-------|--------|
| 1 Approach | Move above source object |
| 2 Grasp | Lower + close gripper |
| 3 Lift | Raise to safe height (z_lift = 0.4 m) |
| 4 Transfer | Move above target location |
| 5 Place | Lower to placement position |
| 6 Retreat | Open gripper, return home |

---

## Evaluation Framework (`comparisons/`)

Benchmarks four pipeline variants on **100 standardised prompts** across 3 complexity tiers.

### Test Prompts

All prompts are pick-and-place palletizing variants:

| Tier | IDs | Description |
|------|-----|-------------|
| Low | P01–P25 | All specs explicit (robot, dims, throughput) |
| Medium | P26–P65 | Partial specs; values must be inferred |
| High | P66–P100 | Vague, conflicting, or multi-constraint inputs |

### Four Pipeline Variants

| Pipeline | Tools | Skills | Progressive Disclosure | State Machine |
|----------|-------|--------|----------------------|---------------|
| `naive_llm` | ✗ | ✗ | ✗ | ✗ |
| `langchain_tools` | ✓ | ✗ | ✗ | ✗ |
| `skills_no_disclosure` | ✓ | ✓ | ✗ | ✗ |
| `ours_full` | ✓ | ✓ | ✓ | ✓ |

### Stage Validators (`shared/validators.py`)

All four pipelines are evaluated against identical semantic checks.

#### Stage 1 – 6 checks (all must pass)

| # | Check | Rule |
|---|-------|------|
| 1 | Pydantic schema | `Stage1Output.model_validate()` succeeds |
| 2 | Throughput consistency | `cycle_time_seconds` within ±10% of `3600 / items_per_hour` |
| 3 | Payload adequacy | `robot_selection.payload_kg ≥ task_specification.weight_kg` |
| 4 | Required components | All four types present: pedestal + conveyor + pallet + carton/object |
| 5 | MJCF path namespace | Every path starts with `workcell_components/` or a known robot directory |
| 6 | Spatial zone completeness | `spatial_reasoning.zones` has ≥ 2 entries with ≥ 1 pickup zone and ≥ 1 placement zone |

#### Stage 2 – 4 checks

| # | Check | Rule |
|---|-------|------|
| 1 | Status success | Solver returns `status: success` |
| 2 | Position validity | Every component has a valid `[x, y, z]` list |
| 3 | Both motion targets present | `motion_targets` includes both `pick_target_xyz` and `place_target_xyz` |
| 4 | Layout spread | Pick–place distance ≥ 0.8 m; pick z ≥ 0.3 m |

#### Stage 3 – 4 checks (raw agent JSON, evaluated before path-fixing)

| # | Check | Rule |
|---|-------|------|
| 1 | Component count | At least 3 components in scene list |
| 2 | Robot present | One component with `component_type == "robot"` |
| 3 | Robot URDF exists | Robot's `urdf_path` resolves to an existing file under `mujoco_menagerie/` |
| 4 | Trajectory parameters | `execute_trajectory=True` and both pick/place targets populated |

### Tool Hit / Miss Tracking

`EvidenceLogger` records every tool/skill call per iteration:

- **Hit** – correct tool called at the correct stage with valid arguments  
- **Miss** – wrong tool, skipped stage, or invalid arguments  

Hit/miss rates appear in **Table 2** of the comparison report.

### Running the Evaluation

```bash
cd robot_workcell_agent

# Quick smoke-test
python -m comparisons.evaluation.harness --pipelines langchain_tools --prompts 3

# Full run – all 4 pipelines, 100 prompts
python -m comparisons.evaluation.harness --pipelines all --prompts 100

# Filter by complexity tier
python -m comparisons.evaluation.harness --complexity low --prompts 25

# Batch mode to avoid rate limits
python -m comparisons.evaluation.harness --prompts 20 --offset 0
python -m comparisons.evaluation.harness --prompts 20 --offset 20 --resume

# Alternative entry point (identical results):
python -m comparisons.run_all --pipelines all --prompts 100
```

> **Note:** Both `python -m comparisons.evaluation.harness` and `python -m comparisons.run_all` are valid entry points for running the evaluation. The `run_all` module is a wrapper that calls the harness, so all options and report outputs are identical.

### Report Output

```
comparisons/logs/
├── reports/
│   ├── comparison_report_YYYYMMDD_HHMMSS.md    # Markdown tables (Tables 1–3)
│   └── raw_summaries_YYYYMMDD_HHMMSS.json      # Full numeric data
├── langchain_tools/
│   ├── langchain_tools_*.json                   # Per-iteration structured evidence
│   └── langchain_tools_*.log                    # Human-readable text log
└── ours_full/ ...
```

Three tables are generated:

- **Table 1** – Success rate by stage (S1 / S2 / S3 / Avg) for all four pipelines  
- **Table 2** – Tool hit & miss counts per stage (pipelines with tools only)  
- **Table 3** – LLM API calls and token usage (total + per-iteration averages)

---

## Settings Reference

| Variable | Required when | Description |
|----------|--------------|-------------|
| `MODEL_PROVIDER` | always | `azure` or `qwen` |
| `AZURE_OPENAI_API_KEY` | azure | Azure key |
| `AZURE_OPENAI_ENDPOINT` | azure | Azure endpoint URL |
| `AZURE_OPENAI_DEPLOYMENT` | azure | Deployment name (default `gpt-4o`) |
| `QWEN_BASE_MODEL` | qwen | HuggingFace model ID |
| `QWEN_API_BASE_URL` | qwen | Local vLLM / OpenAI-compat base URL |
| `QWEN_API_KEY` | qwen | API key (`sk-no-key-required` for local) |
| `QWEN_TEMPERATURE` | qwen | Sampling temperature |
| `QWEN_TOP_P` | qwen | Top-p sampling |
| `QWEN_MAX_TOKENS` | qwen | Max output tokens |

All Qwen settings are read from environment only (no code defaults).

---

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| Skills as files, not code | Agent reads SKILL.md and runs scripts via subprocess – no hardcoded tool logic |
| Progressive disclosure | Only the currently-needed skill is loaded into context, keeping token usage low |
| Deterministic Stage 2 | Layout solver is a pure Python script; agent cannot hallucinate component positions |
| Shared validators | All four comparison pipelines validate against identical semantic rules – fair comparison |
| stdin/stdout JSON protocol | Scripts are language-agnostic and independently testable |
| Evidence logger | Every API call, tool use, validation result, and timing persisted for full reproducibility |
