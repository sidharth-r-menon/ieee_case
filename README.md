# Robot Workcell Design Agent

An AI-powered agent for automated robotic workcell design using the Anthropic skills pattern with progressive disclosure and executable skill scripts.

## 🎯 Overview

This agent enables end-to-end robotic workcell design from natural language:

```
Natural Language → Interpret Requirements → Optimize Layout Placement → Build & Execute Simulation
```

### Key Features

- **🤖 Streamlit Chat UI** - Interactive chat interface with real-time pipeline status
- **⚡ Anthropic Skills Pattern** - Agent loads skills and executes their Python scripts
- **📚 Progressive Disclosure** - Skills load on-demand to conserve context
- **🎨 3-Stage Pipeline** - Request Interpretation → Layout Optimization → Genesis Simulation
- **📦 4 Core Skills** - Streamlined architecture with executable Python scripts
- **🦾 Multi-Robot Support** - 25+ robot models from mujoco_menagerie (UR series, Franka, Kinova, KUKA, etc.)
- **📊 Physics Simulation** - Genesis GPU-accelerated simulation with automatic trajectory execution
- **🧠 Deterministic Layout** - layout_generator.py with collision detection and reachability analysis
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
│   ├── skill_toolset.py      # Progressive disclosure + execution tools
│   ├── skill_loader.py       # Skill discovery from filesystem
│   ├── skill_tools.py        # Skill loading implementation
│   ├── providers.py          # Azure OpenAI configuration
│   ├── settings.py           # Environment-based settings
│   ├── prompts.py            # System prompt with 3-stage workflow
│   └── dependencies.py       # Dependency injection
├── skills/                   # 3 active skills (streamlined pipeline)
│   ├── request_interpreter/  # Stage 1 - NL → JSON with reference guides
│   │   ├── SKILL.md         # Workflow instructions
│   │   ├── scripts/
│   │   │   └── interpret_request.py
│   │   └── references/      # Consolidated Stage 1 guidance
│   │       ├── gap_analysis_guide.md    # What info is required
│   │       ├── standard_objects.md      # Common object dimensions
│   │       ├── robot_selection_guide.md # Robot selection logic
│   │       └── robots/                   # Robot specifications
│   │           ├── franka_emika_panda.md
│   │           ├── kuka_kr3.md
│   │           ├── ur10.md
│   │           ├── ur3.md
│   │           └── ur5.md
│   ├── placement_solver/     # Stage 2 - Deterministic layout optimization
│   │   ├── SKILL.md
│   │   ├── scripts/
│   │   │   └── solve_placement.py  # Uses layout_generator.py
│   │   └── references/
│   │       ├── ik_guidelines.md
│   │       └── pso_configuration.md
│   └── genesis_scene_builder/# Stage 3 - Build scene + execute trajectory
│       ├── SKILL.md
│       ├── scripts/
│       │   └── build_and_execute.py  # Combined build + 6-phase trajectory
│       └── references/
│           ├── asset_organization.md
│           └── genesis_api_reference.md
└── tests/                    # Unit and integration tests
```

### External Asset Directories

```
mujoco_menagerie/             # Robot URDFs and MuJoCo models
├── franka_emika_panda/      # Franka Panda robot (7-DOF, 3kg payload, 855mm reach)
├── franka_fr3/              # Franka FR3
├── universal_robots_ur5e/   # UR5e (5kg payload, 850mm reach)
├── universal_robots_ur10e/  # UR10e (10kg payload, 1300mm reach)
├── kuka_iiwa_14/            # KUKA iiwa 14 (14kg payload)
├── kinova_gen3/             # Kinova Gen3
├── unitree_z1/              # Unitree Z1
└── ... (25+ robot models)   # See mujoco_menagerie/ for full list

workcell_components/          # Workcell structural components (MJCF format)
├── carton/                  # Carton boxes (various sizes)
│   └── carton.xml
├── conveyor/                # Belt conveyors
│   └── conveyor.xml
├── pallet/                  # Standard pallets
│   └── pallet.xml
├── pedestal/                # Robot pedestals
│   └── pedestal.xml
├── table/                   # Work tables
│   └── table.xml
└── ... (more components)    # Bins, shelves, racks, etc.
```

**Key Notes**:
- **mujoco_menagerie/**: Contains robot URDF files from Google DeepMind's MuJoCo Menagerie project. Each robot folder has a `scene.xml` that references the URDF.
- **workcell_components/**: Custom-built MJCF component files for workcell infrastructure. These are referenced by genesis_scene_builder when building the simulation.
- Both directories are accessed during Stage 3 (genesis_scene_builder) to construct the complete scene.

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

### Example 1: Simple Palletizing Cell

**You**: *"I need a workcell with a UR5 robot to palletize cartons from a conveyor onto a pallet"*

**Agent Workflow** (3-Stage Pipeline):

**Stage 1 - Request Interpretation**:
1. Loads `request_interpreter` skill via `load_skill_tool("request_interpreter")`
2. Loads reference guides: `gap_analysis_guide.md`, `standard_objects.md`, `robot_selection_guide.md`
3. Executes: `run_skill_script_tool("request_interpreter", "interpret_request", {...})`
4. Asks clarifying questions about missing critical info (e.g., carton dimensions, pallet size)
5. Outputs structured JSON with robot (UR5), components (conveyor, carton, pallet, pedestal)
6. Calls `submit_stage1_json(validated_dict)` to store Stage 1 result
7. **Asks: "Proceed to Stage 2 (layout optimization)?"** → **Waits for confirmation**

**Stage 2 - Layout Optimization**:
1. Loads `placement_solver` skill
2. Retrieves Stage 1 data via `get_stage1_data()` 
3. Executes: `run_skill_script_tool("placement_solver", "solve_placement", stage1_data)`
4. layout_generator.py calculates deterministic layout:
   - Robot pedestal at origin [0, 0, 0]
   - Conveyor in robot's front-left reachable zone
   - Pallet in robot's front-right reachable zone  
   - Component placement based on robot reach envelope
5. Outputs optimized positions for all components
6. **Asks: "Does this layout look correct? Proceed to Stage 3 (simulation)?"** → **Waits for confirmation**

**Stage 3 - Genesis Simulation**:
1. Loads `genesis_scene_builder` skill
2. Calls `prepare_genesis_input()` to merge Stage 1 + Stage 2 data (**auto-adds trajectory parameters**)
3. Calls `fix_genesis_paths()` to resolve absolute file paths for robot URDFs and component MJCFs
4. Executes: `run_skill_script_tool("genesis_scene_builder", "build_and_execute", fixed_data)`
5. build_and_execute.py:
   - Spawns robot from mujoco_menagerie/ (e.g., `universal_robots_ur5e/scene.xml`)
   - Spawns components from workcell_components/ (e.g., `conveyor/conveyor.xml`, `pallet/pallet.xml`)
   - Executes **6-phase trajectory**:
     1. **Approach**: Move to above carton on conveyor
     2. **Grasp**: Lower to carton, close gripper
     3. **Lift**: Raise carton to safe height (z_lift=0.4m)
     4. **Transfer**: Move to above pallet
     5. **Place**: Lower to pallet placement position
     6. **Retreat**: Open gripper, return to home position
6. Simulation runs in Genesis (gs.gpu backend) with automatic trajectory execution
7. Returns complete design with component coordinates

**Total Time**: ~30-60 seconds end-to-end

### Example 2: Multi-Component Assembly Cell

**You**: *"Design a workcell with a Franka Panda to assemble products, picking parts from a table and placing them in a bin"*

**Agent Workflow**:

**Stage 1**: Interprets request → identifies robot (Franka Panda), components (table, bin, parts) → asks for part details (dimensions, quantities) → outputs Stage 1 JSON → waits for confirmation

**Stage 2**: Optimizes layout → robot pedestal at origin, table in reachable zone, bin nearby → validates collision-free placement → waits for confirmation

**Stage 3**: Builds scene in Genesis → loads Franka Panda from `mujoco_menagerie/franka_emika_panda/` → loads table and bin from `workcell_components/` → executes pick-and-place trajectory → returns design

## 📊 Pipeline Stages

### Stage 1: Request Interpretation

| Skill | Python Script | Purpose |
|-------|--------------------------|---------|
| **request_interpreter** | `scripts/interpret_request.py` | Parse natural language → structured JSON with robot selection, component identification, and gap analysis |

**Reference Guides** (loaded automatically):
- `gap_analysis_guide.md` - Identifies missing critical/important/optional information
- `standard_objects.md` - Common object dimensions (cartons, pallets, tables, etc.)
- `robot_selection_guide.md` - Robot selection logic based on payload, reach, task type
- `robots/*.md` - Detailed specifications for 5 robot models (Franka Panda, UR3/5/10, KUKA KR3)

**Output**: Stage 1 JSON containing:
- Robot specification (model, payload, reach)
- Workcell components (type, name, dimensions, material)
- Task description
- Validation status

### Stage 2: Layout Optimization

| Skill | Python Script | Purpose |
|-------|---------------|---------|
| **placement_solver** | `scripts/solve_placement.py` | Deterministic layout calculation via layout_generator.py: robot pedestal at origin, components in reachable zones with collision avoidance |

**Algorithm**: layout_generator.py (deterministic, not PSO)
- **Robot Base**: Always at origin [0, 0, 0]
- **Component Placement**: Distributed in zones around robot (front-left, front-right, side)
- **Constraints**: Collision detection, reachability analysis, IK validation
- **Output**: Optimized 3D coordinates for all components

### Stage 3: Genesis Simulation

| Skill | Python Script | Purpose |
|-------|--------------------------|---------|
| **genesis_scene_builder** | `scripts/build_and_execute.py` | Spawn robot + components in Genesis AND execute 6-phase trajectory (approach → grasp → lift → transfer → place → retreat) |

**Execution Flow**:
1. **prepare_genesis_input()**: Merges Stage 1 + Stage 2 data, **auto-adds trajectory parameters** (execute_trajectory=True, motion_targets, z_lift=0.4)
2. **fix_genesis_paths()**: Resolves absolute file paths for robot URDFs (from mujoco_menagerie/) and component MJCFs (from workcell_components/)
3. **build_and_execute.py**: 
   - Spawns robot entity (e.g., `mujoco_menagerie/universal_robots_ur5e/scene.xml`)
   - Spawns component entities (e.g., `workcell_components/pallet/pallet.xml`)
   - Executes trajectory using Genesis IK solver
   - Returns completion status

**Trajectory Phases**:
1. **Approach**: Move end-effector above source object
2. **Grasp**: Lower to object, close gripper
3. **Lift**: Raise to safe height (z_lift=0.4m by default)
4. **Transfer**: Move to above target location  
5. **Place**: Lower to target position
6. **Retreat**: Open gripper, return to home position

**Simulation Backend**: Genesis (gs.gpu) - GPU-accelerated physics with automatic IK solving

## 🎨 Streamlit UI Features

The Streamlit app (`streamlit_app.py`) provides:

- **Chat Interface** - Natural language interaction with the agent
- **Pipeline Status Sidebar** - Live tracking of Stage 1/2/3 progress
- **Skill Browser** - View all 3 active skills with descriptions
- **Design Context** - Inspect scene data, layout, validation results in real-time
- **Multi-Turn Conversations** - Maintains conversation history
- **Session Management** - Reset session to start fresh


## 🗄️ Data Resources

### Robot Database (mujoco_menagerie)

The `mujoco_menagerie/` directory contains 60+ robot models from Google DeepMind's MuJoCo Menagerie project. Common manipulation robots for workcells include:

**Industrial Collaborative Robots**:
- **franka_emika_panda** - 7-DOF, 3kg payload, 855mm reach - Precision manipulation, research, assembly
- **franka_fr3** - 7-DOF, 3kg payload, 855mm reach - Latest Franka model
- **universal_robots_ur5e** - 6-DOF, 5kg payload, 850mm reach - General purpose, versatile
- **universal_robots_ur10e** - 6-DOF, 10kg payload, 1300mm reach - Heavy payload, palletizing
- **kuka_iiwa_14** - 7-DOF, 14kg payload, 820mm reach - High precision, assembly
- **kinova_gen3** - 7-DOF, 2kg payload, 902mm reach - Research, assistive robotics
- **rethink_robotics_sawyer** - 7-DOF, 4kg payload, 1260mm reach - Collaborative tasks
- **ufactory_xarm7** - 7-DOF, 3.5kg payload, 700mm reach - Compact workcells
- **unitree_z1** - 6-DOF, 3kg payload, 750mm reach - Lightweight manipulation

**Grippers & End-Effectors**:
- **robotiq_2f85** - 2-finger parallel gripper (85mm stroke)
- **shadow_hand** - 5-finger dexterous hand (24-DOF)
- **leap_hand** - Anthropomorphic hand
- **umi_gripper** - Universal Manipulation Interface gripper

Each robot folder contains:
- `scene.xml` - Main MuJoCo model file (referenced by genesis_scene_builder)
- `*.urdf` / `*.xml` - Robot description files
- `assets/` - Mesh files, textures

**Full list**: See `mujoco_menagerie/` directory for all 60+ models including humanoids, quadrupeds, mobile robots, and drones.

### Workcell Components (workcell_components)

Custom-built MJCF component library for workcell infrastructure:

**Containers & Storage**:
- **carton/** - Cardboard cartons (various sizes for palletizing tasks)
- **pallet/** - Standard shipping pallets (1200x800mm, 1200x1000mm)
- **bin/** - Storage bins

**Conveyor Systems**:
- **conveyor/** - Belt conveyors for material handling

**Work Surfaces**:
- **table/** - Work tables
- **pedestal/** - Robot mounting pedestals

Each component folder contains:
- `component_name.xml` - MJCF model file with collision geometry
- Dimension specifications integrated into XML

**Usage**: genesis_scene_builder loads these components during Stage 3 scene construction.  