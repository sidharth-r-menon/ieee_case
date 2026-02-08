# Robot Workcell Design Agent

An AI-powered agent for automated robotic workcell design using the Anthropic skills pattern with progressive disclosure and executable skill scripts.

## 🎯 Overview

This agent enables end-to-end robotic workcell design from natural language:

```
Natural Language → Interpret Requirements → Select Components → Optimize Placement
                → Simulate in Genesis → Validate & Execute Motion → Return Design
```

### Key Features

- **🤖 Streamlit Chat UI** - Interactive chat interface with real-time pipeline status
- **⚡ Anthropic Skills Pattern** - Agent loads skills and executes their Python scripts
- **📚 Progressive Disclosure** - Skills load on-demand to conserve context
- **🎨 3-Stage Pipeline** - Interpretation → Optimization → Validation
- **📦 9 Specialized Skills** - Each skill contains executable Python scripts
- **🦾 Multi-Robot Support** - 7+ robot models (UR3/5/10, Franka Panda, ABB IRB1200, KUKA KR3, Fanuc M20)
- **📊 Physics Simulation** - Genesis-based 3D simulation with collision detection
- **🧠 Smart Optimization** - PSO (Particle Swarm Optimization) via PySwarms for component placement
- **☁️ Azure OpenAI** - Powered by GPT-4o

## 🏗️ Architecture

### Anthropic Skills Pattern

This project follows the **Anthropic skills pattern** where:

1. **Agent loads skill instructions** using `load_skill_tool(skill_name)`
2. **Skill SKILL.md contains workflow instructions** telling agent how to execute
3. **Agent runs Python scripts** in the skill's `scripts/` folder via terminal
4. **Scripts output JSON** which agent parses and uses to continue

**No hardcoded execution tools** - the agent dynamically discovers and executes skill scripts based on loaded instructions.

### Skill Tools (Progressive Disclosure)

Three levels of access:
- **Level 1**: Skill metadata in system prompt (name, description, stage)
- **Level 2**: Load full instructions via `load_skill_tool(skill_name)` → reads SKILL.md
- **Level 3**: Access specific files via `read_skill_file_tool(skill_name, file_path)`

Available tools:
- `load_skill_tool(skill_name)` - Load full SKILL.md workflow instructions
- `read_skill_file_tool(skill_name, file_path)` - Read specific resource files
- `list_skill_files_tool(skill_name)` - List available files in skill directory

### Project Structure

```
robot_workcell_agent/
├── streamlit_app.py          # 🎨 Streamlit chat UI (RECOMMENDED)
├── .env                       # 🔑 Azure OpenAI credentials
├── requirements.txt           # 📦 Dependencies
├── src/
│   ├── agent.py              # Main Pydantic AI agent (uses skill_tools only)
│   ├── skill_toolset.py      # Progressive disclosure tools
│   ├── skill_loader.py       # Skill discovery from filesystem
│   ├── skill_tools.py        # Skill loading implementation
│   ├── providers.py          # Azure OpenAI configuration
│   ├── settings.py           # Environment-based settings
│   ├── prompts.py            # Minimal system prompt (~59 lines)
│   └── dependencies.py       # Dependency injection
├── skills/                   # 9 skills (Anthropic pattern)
│   ├── request_interpreter/  # Stage 1 - NL → JSON
│   │   ├── SKILL.md         # Workflow instructions
│   │   ├── scripts/
│   │   │   └── interpret_request.py
│   ├── gap_resolver/         # Stage 1 - Identify missing info
│   │   ├── SKILL.md
│   │   ├── scripts/
│   │   │   └── resolve_gaps.py
│   │   └── references/
│   │       └── common_gaps.md
│   ├── robot_selector/       # Stage 1 - Select optimal robot
│   │   ├── SKILL.md
│   │   ├── scripts/
│   │   │   └── select_robot.py
│   │   └── references/
│   │       ├── abb_irb1200.md
│   │       ├── franka_emika_panda.md
│   │       ├── kuka_kr3.md
│   │       ├── ur10.md
│   │       ├── ur3.md
│   │       ├── ur5.md
│   ├── sku_analyser/         # Stage 1 - Asset database lookup
│   │   ├── SKILL.md
│   │   ├── scripts/
│   │   │   └── analyze_sku.py
│   │   └── references/
│   │       └── object_database.md
│   ├── region_proposer/      # Stage 2 - Define spatial zones
│   │   ├── SKILL.md
│   │   ├── scripts/
│   │   │   └── propose_regions.py
│   │   └── references/
│   │       └── region_templates.md
│   ├── placement_solver/     # Stage 2 - PSO optimization (PySwarms)
│   │   ├── SKILL.md
│   │   ├── scripts/
│   │   │   └── solve_placement.py
│   │   └── references/
│   │       ├── ik_guidelines.md
│   │       └── pso_configuration.md
│   ├── genesis_scene_builder/# Stage 3 - Build Genesis simulation
│   │   ├── SKILL.md
│   │   ├── scripts/
│   │   │   └── build_scene.py
│   │   └── references/
│   │       ├── asset_organization.md
│   │       └── genesis_api_reference.md
│   ├── simulation_validator/ # Stage 3 - Physics validation
│   │   ├── SKILL.md
│   │   ├── scripts/
│   │   │   └── validate.py
│   │   └── references/
│   └── motion_primitives/    # Runtime - Motion execution
│       ├── SKILL.md
│       └── scripts/
│           ├── approach.py
│           ├── grasp.py
│           ├── lift.py
│           ├── move.py
│           ├── place.py
│           ├── release.py
│           ├── retreat.py
│           └── return_home.py
    # ...existing code...
└── tests/                    # Unit and integration tests
```

### Skill Structure

Each skill follows the Anthropic pattern:
```
skills/skill_name/
├── SKILL.md              # Workflow instructions with YAML frontmatter
│                         # Contains: when to use, how to execute scripts,
│                         # how to parse output, what to do next
└── scripts/              # Executable Python scripts
    └── *.py              # Script reads JSON from stdin, outputs JSON to stdout
```

**Example workflow:**
1. Agent loads `request_interpreter` skill: `load_skill_tool("request_interpreter")`
2. SKILL.md says: "Run `python scripts/interpret_request.py` and send input as JSON via stdin"
3. Agent executes script, sending JSON input via stdin
4. Script outputs JSON to stdout (never prints logs)
5. Agent parses JSON and continues to next skill

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.11+
- Conda environment
- Azure OpenAI access with GPT-4o deployment

### 2. Configure Azure OpenAI

Edit `.env` and add your credentials:

```bash
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-12-01-preview
AZURE_OPENAI_DEPLOYMENT=gpt-4o
```

### 3. Install Dependencies

```bash
cd d:\GitHub\ieee_case\robot_workcell_agent
pip install -r requirements.txt
```

### 4. Run the Agent

**Option A: Streamlit Chat UI (Recommended)**
```bash
streamlit run streamlit_app.py
```

Open your browser to `http://localhost:8501` and start chatting!


## 💬 Usage Examples

### Example 1: Simple Pick-and-Place Cell

**You**: *"I need a workcell with a UR5 robot to sort apples and oranges into boxes on a table"*

**Agent Workflow** (Anthropic Skills Pattern):
1. Loads `request_interpreter` skill: `load_skill_tool("request_interpreter")`
2. Reads workflow instructions from SKILL.md
3. Executes: `python scripts/interpret_request.py --text "I need a workcell with a UR5..."` → extracts UR5, apples, oranges, boxes, table
4. Loads `gap_resolver` skill and runs `scripts/resolve_gaps.py` → identifies missing dimensions
5. Asks you 8-10 natural questions about missing info
6. Updates scene data with your answers
7. Loads `robot_selector` skill, runs `scripts/select_robot.py` → confirms UR5 is suitable
8. Loads `sku_analyser` skill, runs `scripts/analyze_sku.py` for each item → gets dimensions from database
9. Loads `placement_solver` skill
10. Runs `scripts/propose_regions.py` → defines input/output zones
11. Runs `scripts/solve_placement.py --algorithm pso` → PSO optimization with PySwarms (30 particles, 100 iterations)
12. **Asks for your confirmation** before proceeding to Stage 3
13. Loads `genesis_scene_builder` skill, runs `scripts/build_scene.py` → spawns robot, table, objects in Genesis
14. Loads `simulation_validator` skill, runs `scripts/validate_simulation.py` → checks stability, collisions, IK
15. Runs motion primitive scripts to simulate pick-and-place
16. Returns complete design summary with validation report

### Example 2: Assembly Cell

**You**: *"Design an assembly workcell with two robots for car door assembly"*

**Agent Workflow**:
1. Interprets request via `scripts/interpret_request.py` → needs 2 robots, assembly task, car door parts
2. Runs `scripts/resolve_gaps.py` → identifies missing parts list, dimensions
3. Asks gaps → "What types of parts are being assembled?" (fasteners, panels, etc.)
4. Runs `scripts/select_robot.py` → suggests ABB IRB1200 (precision, fast) for both positions
5. Runs `scripts/analyze_sku.py` → looks up parts in asset database
6. Runs `scripts/propose_regions.py` → assembly zone + 2 parts storage zones
7. Runs `scripts/solve_placement.py` → PSO with dual-robot reachability constraints
8. Builds scene via `scripts/build_scene.py` → spawns 2 robots, work table, parts
9. Validates via `scripts/validate_simulation.py` → checks no collisions between robot workspaces
10. Returns summary with coordinates and validation report

## 📊 Pipeline Stages

### Stage 1: Interpretation & Analysis

| Skill | Python Script | Purpose |
|-------|--------------------------|---------|
| **request_interpreter** | `scripts/interpret_request.py` | Parse natural language → structured JSON |
| **gap_resolver** | `scripts/resolve_gaps.py` | Identify missing info (critical/important/optional) |
| **robot_selector** | `scripts/select_robot.py` | Choose from 7 robots based on payload/reach/task |
| **sku_analyser** | `scripts/analyze_sku.py` | Look up assets (20+ items: fruits, boxes, primitives) |

### Stage 2: Spatial Optimization

| Skill | Python Script | Purpose |
|-------|---------------|---------|
| **region_proposer** | `scripts/propose_regions.py` | Define zones (robot base, input, output, assembly, storage) |
| **placement_solver** | `scripts/solve_placement.py` | PSO optimization via PySwarms: minimize reach distance + avoid collisions |

### Stage 3: Validation

| Skill | Python Script | Purpose |
|-------|--------------------------|---------|
| **genesis_scene_builder** | `scripts/build_scene.py` | Spawn robot + objects in Genesis physics engine |
| **simulation_validator** | `scripts/validate.py` | Check stability, collisions, IK reachability |
| **motion_primitives** | `scripts/approach.py`, `grasp.py`, etc. | Motion sequences: approach, grasp, lift, move, place, release, retreat, return_home |

## 🎨 Streamlit UI Features

The Streamlit app (`streamlit_app.py`) provides:

- **Chat Interface** - Natural language interaction with the agent
- **Pipeline Status Sidebar** - Live tracking of Stage 1/2/3 progress
- **Skill Browser** - View all 9 available skills with descriptions
- **Design Context** - Inspect scene data, layout, validation results in real-time
- **Multi-Turn Conversations** - Maintains conversation history
- **Session Management** - Reset session to start fresh


## 🗄️ Data Resources

### Robot Database (7 models)

| Model | Payload | Reach | Use Cases |
|-------|---------|-------|-----------|
| Franka Panda | 3 kg | 0.855 m | Lab, precision, collaborative |
| UR3 | 3 kg | 0.500 m | Compact, assembly, small parts |
| UR5 | 5 kg | 0.850 m | General purpose, versatile |
| UR10 | 10 kg | 1.300 m | Heavy, palletizing |
| ABB IRB1200 | 7 kg | 0.900 m | Assembly, fast |
| KUKA KR3 | 3 kg | 0.635 m | Precision, electronics |
| Fanuc M20 | 20 kg | 1.811 m | Heavy, palletizing |

### Asset Database (20+ items)

**Fruits**: apple, orange  
**Containers**: box, small box, large box, bin  
**Bottles**: bottle (500ml)  
**Primitives**: cube, cylinder, sphere  
**Furniture**: table, workbench, shelf, conveyor  