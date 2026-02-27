"""
Standardized test prompts for comparison evaluation.

All 100 prompts are variations of the core palletizing theme:
    "Design a robotic pick-and-place palletizing system that transfers
     cartons from a conveyor to a pallet."

Complexity levels:
  low    (P01–P25): All specs explicit – robot, dims, throughput all given.
  medium (P26–P65): Partial specs; some values must be inferred.
  high   (P66–P100): Vague, conflicting, or multi-constraint prompts.
"""

from dataclasses import dataclass
from typing import List


@dataclass
class TestPrompt:
    """A standardized test prompt for evaluation."""
    id: str
    description: str
    prompt: str
    complexity: str  # "low", "medium", "high"
    expected_robot: str  # Expected robot model for validation
    expected_components: List[str]  # Expected component types


# ──────────────────────────────────────────────────────────────────────
# LOW COMPLEXITY – P01–P25 (all specs given explicitly)
# ──────────────────────────────────────────────────────────────────────

TEST_PROMPTS = [
    # ── LOW COMPLEXITY P01–P25 ─────────────────────────────────────────
    TestPrompt(
        id="P01",
        description="UR5 carton palletizing – standard dims",
        prompt=(
            "Design a pick-and-place palletizing workcell using a UR5 robot. "
            "The task is to pick standard cardboard cartons (0.30 m x 0.30 m x 0.30 m, 2.5 kg each) "
            "from an industrial conveyor belt and place them onto a euro pallet. "
            "The robot is mounted on a standard pedestal (0.60 m x 0.60 m x 0.50 m). "
            "Conveyor: 2.0 m x 0.64 m x 0.82 m. Euro pallet: 1.2 m x 0.8 m x 0.15 m. "
            "Target throughput: 120 cartons per hour (30 s cycle time). "
            "Safety fencing is required around the workcell."
        ),
        complexity="low",
        expected_robot="ur5",
        expected_components=["pedestal", "conveyor", "pallet", "carton"],
    ),
    TestPrompt(
        id="P02",
        description="UR5e medium-box palletizing – 100/hr",
        prompt=(
            "I need a palletizing station with a UR5e robot to stack medium boxes "
            "(0.40 m x 0.30 m x 0.25 m, 3.0 kg) from a conveyor belt onto a euro pallet. "
            "Mount the robot on a pedestal (0.60 m x 0.60 m x 0.50 m). "
            "Conveyor: 2.0 m x 0.64 m x 0.82 m. Pallet: 1.2 m x 0.8 m x 0.15 m. "
            "Throughput: 100 boxes per hour (36 s cycle time)."
        ),
        complexity="low",
        expected_robot="ur5e",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P03",
        description="UR10e heavy carton palletizing – 60/hr",
        prompt=(
            "Set up a pick-and-place palletizing station using a UR10e robot to transfer "
            "heavy cartons (0.50 m x 0.40 m x 0.35 m, 8.0 kg) from a conveyor to a euro pallet. "
            "Robot on pedestal (0.60 m x 0.60 m x 0.50 m). "
            "Conveyor: 2.0 m x 0.64 m x 0.82 m. Pallet: 1.2 m x 0.8 m x 0.15 m. "
            "Throughput: 60 cartons per hour. Safety fencing required."
        ),
        complexity="low",
        expected_robot="ur10e",
        expected_components=["pedestal", "conveyor", "pallet", "carton"],
    ),
    TestPrompt(
        id="P04",
        description="Franka Panda light carton palletizing – 200/hr",
        prompt=(
            "Design a palletizing workcell with a Franka Emika Panda robot. "
            "Pick small cartons (0.20 m x 0.15 m x 0.12 m, 0.8 kg) from a conveyor "
            "and place them onto a euro pallet. "
            "Pedestal: 0.60 m x 0.60 m x 0.50 m. "
            "Conveyor: 2.0 m x 0.64 m x 0.82 m. Pallet: 1.2 m x 0.8 m x 0.15 m. "
            "Target: 200 cartons per hour (18 s cycle time)."
        ),
        complexity="low",
        expected_robot="panda",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P05",
        description="UR5 tall carton palletizing – 90/hr",
        prompt=(
            "Design a palletizing cell with a UR5 robot for transferring tall cartons "
            "(0.30 m x 0.20 m x 0.45 m, 3.5 kg) from a conveyor to a euro pallet. "
            "Robot on standard pedestal (0.60 m x 0.60 m x 0.50 m). "
            "Conveyor: 2.0 m x 0.64 m x 0.82 m. Pallet: 1.2 m x 0.8 m x 0.15 m. "
            "Throughput: 90 items per hour (40 s cycle time)."
        ),
        complexity="low",
        expected_robot="ur5",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P06",
        description="UR5e flat carton palletizing – 150/hr",
        prompt=(
            "Set up a palletizing system with a UR5e robot to move flat cartons "
            "(0.60 m x 0.40 m x 0.10 m, 2.0 kg) from a conveyor to a euro pallet. "
            "Robot pedestal: 0.60 m x 0.60 m x 0.50 m. "
            "Conveyor: 2.0 m x 0.64 m x 0.82 m. Pallet: 1.2 m x 0.8 m x 0.15 m. "
            "Target: 150 cartons per hour (24 s cycle time)."
        ),
        complexity="low",
        expected_robot="ur5e",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P07",
        description="UR10e large carton palletizing – 45/hr",
        prompt=(
            "Create a palletizing workcell using a UR10e robot to palletize large cartons "
            "(0.60 m x 0.50 m x 0.40 m, 10.0 kg) from a conveyor belt. "
            "Pedestal: 0.60 m x 0.60 m x 0.50 m. "
            "Conveyor: 2.0 m x 0.64 m x 0.82 m. Pallet: 1.2 m x 0.8 m x 0.15 m. "
            "Throughput: 45 cartons per hour (80 s cycle time). Safety fencing included."
        ),
        complexity="low",
        expected_robot="ur10e",
        expected_components=["pedestal", "conveyor", "pallet", "carton"],
    ),
    TestPrompt(
        id="P08",
        description="UR5 mini carton palletizing – 240/hr",
        prompt=(
            "Build a high-throughput palletizing cell with a UR5 robot. "
            "Pick mini cartons (0.15 m x 0.15 m x 0.15 m, 1.0 kg) from a conveyor "
            "onto a euro pallet. Robot on pedestal (0.60 m x 0.60 m x 0.50 m). "
            "Conveyor: 2.0 m x 0.64 m x 0.82 m. Pallet: 1.2 m x 0.8 m x 0.15 m. "
            "Throughput: 240 items per hour (15 s cycle time)."
        ),
        complexity="low",
        expected_robot="ur5",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P09",
        description="UR5e standard carton palletizing – 120/hr with fencing",
        prompt=(
            "Design a carton palletizing workcell using a UR5e robot. "
            "Cartons: 0.35 m x 0.25 m x 0.20 m, 2.2 kg. "
            "Robot on pedestal. Conveyor input, euro pallet output. "
            "Standard component sizes: pedestal 0.60x0.60x0.50 m, "
            "conveyor 2.0x0.64x0.82 m, pallet 1.2x0.8x0.15 m. "
            "120 cartons per hour. Safety fence required."
        ),
        complexity="low",
        expected_robot="ur5e",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P10",
        description="UR5 carton palletizing – explicit MJCF refs 100/hr",
        prompt=(
            "Design a pick-and-place palletizing cell: UR5 robot on pedestal, "
            "picking cardboard cartons (0.30 m x 0.30 m x 0.30 m, 2.5 kg) from a conveyor, "
            "placing on euro pallet. "
            "Pedestal: 0.60x0.60x0.50 m. Conveyor: 2.0x0.64x0.82 m. Pallet: 1.2x0.8x0.15 m. "
            "Need 100 cartons/hour throughput. Safety fencing required."
        ),
        complexity="low",
        expected_robot="ur5",
        expected_components=["pedestal", "conveyor", "pallet", "carton"],
    ),
    TestPrompt(
        id="P11",
        description="UR5 carton palletizing – 80/hr low duty",
        prompt=(
            "Build a palletizing system with a UR5 robot. "
            "Cartons: 0.30 m x 0.30 m x 0.30 m, 2.5 kg. "
            "Conveyor to euro pallet transfer. "
            "Pedestal: 0.60x0.60x0.50 m. Conveyor: 2.0x0.64x0.82 m. Pallet: 1.2x0.8x0.15 m. "
            "Throughput: 80 cartons per hour (45 s cycle)."
        ),
        complexity="low",
        expected_robot="ur5",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P12",
        description="UR10e carton palletizing – 72/hr with safety",
        prompt=(
            "Set up a palletizing station with a UR10e robot for carton handling. "
            "Cartons: 0.45 m x 0.35 m x 0.30 m, 6.5 kg. Robotic transfer from conveyor to pallet. "
            "Pedestal: 0.60x0.60x0.50 m. Conveyor: 2.0x0.64x0.82 m. Pallet: 1.2x0.8x0.15 m. "
            "Throughput target: 72 cartons per hour (50 s cycle). Safety fence included."
        ),
        complexity="low",
        expected_robot="ur10e",
        expected_components=["pedestal", "conveyor", "pallet", "carton"],
    ),
    TestPrompt(
        id="P13",
        description="UR5e carton palletizing – 108/hr medium duty",
        prompt=(
            "Design a palletizing workcell with UR5e robot. "
            "Task: pick cartons (0.32 m x 0.28 m x 0.22 m, 2.8 kg) from conveyor and "
            "stack them on a euro pallet. "
            "Standard pedestal, conveyor (2.0x0.64x0.82 m), pallet (1.2x0.8x0.15 m). "
            "108 cartons/hour (33 s cycle time)."
        ),
        complexity="low",
        expected_robot="ur5e",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P14",
        description="UR5 narrow carton palletizing – 130/hr",
        prompt=(
            "Create a palletizing cell with UR5 robot. "
            "Cartons: 0.40 m x 0.15 m x 0.25 m, 2.0 kg — narrow orientation. "
            "Pick from conveyor, place on euro pallet. "
            "Pedestal: 0.60x0.60x0.50 m. Conveyor: 2.0x0.64x0.82 m. Pallet: 1.2x0.8x0.15 m. "
            "Throughput: 130 cartons/hour."
        ),
        complexity="low",
        expected_robot="ur5",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P15",
        description="Franka Panda very light carton – 250/hr",
        prompt=(
            "Design a high-speed palletizing workcell using a Franka Emika Panda robot. "
            "Pick very light cartons (0.18 m x 0.14 m x 0.10 m, 0.5 kg) from a conveyor "
            "onto a euro pallet. "
            "Pedestal: 0.60x0.60x0.50 m. Conveyor: 2.0x0.64x0.82 m. Pallet: 1.2x0.8x0.15 m. "
            "Target throughput: 250 cartons/hour (14 s cycle)."
        ),
        complexity="low",
        expected_robot="panda",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P16",
        description="UR5 square carton palletizing – 110/hr single-layer",
        prompt=(
            "Set up a single-layer palletizing cell with a UR5 robot. "
            "Square cartons: 0.30 m x 0.30 m x 0.20 m, 2.0 kg. "
            "Conveyor to euro pallet. Standard component sizes. "
            "Pedestal 0.60x0.60x0.50, conveyor 2.0x0.64x0.82, pallet 1.2x0.8x0.15 m. "
            "110 cartons/hour throughput."
        ),
        complexity="low",
        expected_robot="ur5",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P17",
        description="UR10e extra-heavy carton – 30/hr",
        prompt=(
            "Build a palletizing station using a UR10e robot for extra-heavy cartons "
            "(0.50 m x 0.50 m x 0.40 m, 9.5 kg). Transfer from conveyor to euro pallet. "
            "Pedestal: 0.60x0.60x0.50 m. Conveyor: 2.0x0.64x0.82 m. Pallet: 1.2x0.8x0.15 m. "
            "Throughput: 30 cartons/hour (120 s cycle). Safety fence required."
        ),
        complexity="low",
        expected_robot="ur10e",
        expected_components=["pedestal", "conveyor", "pallet", "carton"],
    ),
    TestPrompt(
        id="P18",
        description="UR5e rectangular carton – 95/hr",
        prompt=(
            "Design a palletizing workcell with UR5e robot for rectangular cartons "
            "(0.50 m x 0.25 m x 0.20 m, 3.2 kg). Conveyor input to pallet output. "
            "All standard industrial component sizes. 95 cartons/hour (38 s cycle)."
        ),
        complexity="low",
        expected_robot="ur5e",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P19",
        description="UR5 cube carton palletizing – 100/hr",
        prompt=(
            "Create a carton palletizing cell using a UR5 robot. "
            "Cube cartons: 0.25 m x 0.25 m x 0.25 m, 1.8 kg each. "
            "Conveyor to euro pallet. Robot on standard pedestal. "
            "Standard conveyor and pallet dimensions. 100 cartons per hour."
        ),
        complexity="low",
        expected_robot="ur5",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P20",
        description="UR10e carton palletizing – 55/hr medium-heavy",
        prompt=(
            "Design a palletizing system with UR10e robot. "
            "Cartons: 0.45 m x 0.40 m x 0.30 m, 9.0 kg. "
            "Conveyor to euro pallet. Pedestal: 0.60x0.60x0.50 m. "
            "Conveyor: 2.0x0.64x0.82 m. Pallet: 1.2x0.8x0.15 m. "
            "55 cartons per hour. Safety fencing required."
        ),
        complexity="low",
        expected_robot="ur10e",
        expected_components=["pedestal", "conveyor", "pallet", "carton"],
    ),
    TestPrompt(
        id="P21",
        description="UR5 slim carton palletizing – 180/hr",
        prompt=(
            "Set up palletizing workcell with UR5 robot. "
            "Slim cartons: 0.40 m x 0.10 m x 0.30 m, 1.5 kg. Conveyor to euro pallet. "
            "Pedestal and standard conveyor/pallet sizes. 180 cartons/hour (20 s cycle)."
        ),
        complexity="low",
        expected_robot="ur5",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P22",
        description="Franka Panda medium carton – 150/hr",
        prompt=(
            "Design a palletizing cell using a Franka Panda robot for medium cartons "
            "(0.25 m x 0.20 m x 0.18 m, 1.2 kg). Conveyor to euro pallet transfer. "
            "Standard pedestal, conveyor, and pallet. 150 items per hour throughput."
        ),
        complexity="low",
        expected_robot="panda",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P23",
        description="UR5e wide carton palletizing – 85/hr",
        prompt=(
            "Build a palletizing cell with UR5e robot. "
            "Wide cartons: 0.60 m x 0.30 m x 0.20 m, 4.0 kg. "
            "Conveyor to pallet. Pedestal 0.60x0.60x0.50 m, "
            "conveyor 2.0x0.64x0.82 m, pallet 1.2x0.8x0.15 m. "
            "Target: 85 cartons/hour (42 s cycle)."
        ),
        complexity="low",
        expected_robot="ur5e",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P24",
        description="UR5 tall narrow carton palletizing – 75/hr",
        prompt=(
            "Create a workcell using a UR5 robot for palletizing tall narrow cartons "
            "(0.15 m x 0.15 m x 0.50 m, 2.0 kg). Transfer from conveyor to euro pallet. "
            "Standard pedestal, conveyor, and pallet. 75 cartons/hour throughput."
        ),
        complexity="low",
        expected_robot="ur5",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P25",
        description="UR10e oversized carton palletizing – 40/hr",
        prompt=(
            "Design a palletizing workcell with a UR10e robot for oversized cartons "
            "(0.70 m x 0.50 m x 0.35 m, 11.0 kg). Conveyor to euro pallet. "
            "Pedestal: 0.60x0.60x0.50 m. Conveyor: 2.0x0.64x0.82 m. Pallet: 1.2x0.8x0.15 m. "
            "40 cartons per hour. Safety fencing required."
        ),
        complexity="low",
        expected_robot="ur10e",
        expected_components=["pedestal", "conveyor", "pallet", "carton"],
    ),

    # ── MEDIUM COMPLEXITY P26–P65 ──────────────────────────────────────
    TestPrompt(
        id="P26",
        description="Carton palletizing – robot determined by payload",
        prompt=(
            "Design a palletizing system that moves cartons (0.30 m x 0.30 m x 0.30 m, 4.5 kg) "
            "from a conveyor belt to a pallet. "
            "Select the most cost-effective robot with adequate payload capacity. "
            "Standard industrial component sizes. Throughput: 100 cartons/hour."
        ),
        complexity="medium",
        expected_robot="ur5e",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P27",
        description="Palletizing – carton weight borderline for UR5",
        prompt=(
            "I need a palletizing robot to transfer cartons (0.35 m x 0.28 m x 0.22 m, 4.8 kg) "
            "from a conveyor to a pallet. The robot should be a UR5 or similar. "
            "Standard-size conveyor and euro pallet. 90 cartons per hour."
        ),
        complexity="medium",
        expected_robot="ur5",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P28",
        description="Palletizing – throughput not given",
        prompt=(
            "Design a robotic palletizing workcell with a UR5e robot. "
            "Cartons: 0.35 m x 0.25 m x 0.20 m, 3.0 kg. "
            "Conveyor to euro pallet. Standard component sizes. "
            "Normal industrial throughput expected."
        ),
        complexity="medium",
        expected_robot="ur5e",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P29",
        description="Palletizing – no carton dimensions given",
        prompt=(
            "Set up a carton palletizing station using a UR5 robot. "
            "Cartons are standard grocery-sized and weigh around 2 kg. "
            "Pick from an industrial conveyor and place on a standard pallet. "
            "Target: 120 cartons per hour."
        ),
        complexity="medium",
        expected_robot="ur5",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P30",
        description="Palletizing – no robot specified",
        prompt=(
            "Design a robotic palletizing system that moves standard cardboard cartons "
            "(0.30 m x 0.30 m x 0.30 m, 2.5 kg) from a conveyor belt onto a pallet. "
            "I don't know which robot to use — please recommend one and justify. "
            "Standard industrial layout. 120 cartons/hour."
        ),
        complexity="medium",
        expected_robot="ur5",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P31",
        description="Palletizing – minimal info infer all specs",
        prompt=(
            "I need a robot to move boxes from a conveyor to a pallet for palletizing."
        ),
        complexity="medium",
        expected_robot="ur5",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P32",
        description="Palletizing – carton described by size analogy",
        prompt=(
            "Build a palletizing workcell. The cartons are roughly the size of a shoebox "
            "and weigh about 1.5 kg. A robot should pick them from a conveyor and "
            "stack them on a pallet. Throughput: 150 items/hour."
        ),
        complexity="medium",
        expected_robot="ur5",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P33",
        description="Palletizing – ambiguous robot name 'UR series'",
        prompt=(
            "Design a palletizing system with a UR-series robot. "
            "Cartons: 0.30 m x 0.30 m x 0.30 m, 3.0 kg. Conveyor to pallet. "
            "Standard workcell layout. 100 items per hour."
        ),
        complexity="medium",
        expected_robot="ur5",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P34",
        description="Palletizing – pallet size not given",
        prompt=(
            "Create a carton palletizing cell using a UR5e robot. "
            "Cartons: 0.30 m x 0.25 m x 0.20 m, 2.5 kg. "
            "Pick from a standard conveyor, place on a pallet (standard industrial size). "
            "100 cartons per hour throughput."
        ),
        complexity="medium",
        expected_robot="ur5e",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P35",
        description="Palletizing – weight slightly over UR5 payload",
        prompt=(
            "Design a palletizing workcell using a UR5 robot (payload 5 kg). "
            "Cartons weigh 5.5 kg and are 0.35 m x 0.30 m x 0.25 m. "
            "Transfer from conveyor to euro pallet. 80 items/hour."
        ),
        complexity="medium",
        expected_robot="ur5",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P36",
        description="Palletizing – conveyor length not given",
        prompt=(
            "Set up a palletizing station with a UR5 robot. "
            "Pick standard cartons (0.30 m x 0.30 m x 0.30 m, 2.5 kg) from a conveyor belt "
            "and place on a euro pallet. Standard pallet dimensions. 120 items/hr."
        ),
        complexity="medium",
        expected_robot="ur5",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P37",
        description="Palletizing – high throughput constraint",
        prompt=(
            "Design a palletizing system to achieve 300 cartons per hour. "
            "Cartons: 0.25 m x 0.20 m x 0.15 m, 1.5 kg. "
            "Pick from conveyor, stack on pallet. Choose the best robot."
        ),
        complexity="medium",
        expected_robot="ur5",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P38",
        description="Palletizing – compact robot for small cartons",
        prompt=(
            "I want a compact palletizing cell for very small cartons "
            "(0.15 m x 0.10 m x 0.10 m, 0.8 kg). Conveyor to pallet. "
            "Standard pedestal and pallet. 200 cartons/hour."
        ),
        complexity="medium",
        expected_robot="ur5",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P39",
        description="Palletizing – fragile cartons gentle handling",
        prompt=(
            "Design a palletizing workcell for fragile cartons "
            "(0.30 m x 0.25 m x 0.20 m, 2.0 kg). "
            "The robot must handle them gently with low acceleration. "
            "Pick from conveyor, place on pallet. UR5 robot. "
            "Throughput: 80 cartons/hour."
        ),
        complexity="medium",
        expected_robot="ur5",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P40",
        description="Palletizing – no pedestal height given",
        prompt=(
            "Build a carton palletizing workcell with a UR5e robot. "
            "Cartons: 0.30 m x 0.30 m x 0.30 m, 2.5 kg. "
            "Robot on a standard-height pedestal. Conveyor and pallet standard sizes. "
            "120 cartons/hour throughput."
        ),
        complexity="medium",
        expected_robot="ur5e",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P41",
        description="Palletizing – food-grade environment",
        prompt=(
            "Design a palletizing system for a food production line. "
            "Sealed cartons (0.30 m x 0.20 m x 0.15 m, 1.5 kg) come in on a conveyor "
            "and must be transferred to a pallet. Use a hygienic-grade robot suitable "
            "for food environments. Throughput: 200 cartons/hour."
        ),
        complexity="medium",
        expected_robot="ur5",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P42",
        description="Palletizing – cold-store environment",
        prompt=(
            "Set up a carton palletizing workcell for a cold-storage warehouse (-5 degrees C). "
            "Cartons: 0.35 m x 0.25 m x 0.20 m, 3.0 kg. "
            "UR5e robot, conveyor to pallet. Standard industrial sizes. "
            "100 cartons/hour."
        ),
        complexity="medium",
        expected_robot="ur5e",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P43",
        description="Palletizing – mixed carton sizes average dims",
        prompt=(
            "Design a robotic palletizing system for mixed-size cartons. "
            "Average size: 0.30 m x 0.28 m x 0.22 m, average weight 2.5 kg. "
            "UR5 robot, conveyor to euro pallet. 100 cartons/hour."
        ),
        complexity="medium",
        expected_robot="ur5",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P44",
        description="Palletizing – cost optimization requested",
        prompt=(
            "Design the most cost-effective palletizing workcell to transfer cartons "
            "(0.30 m x 0.30 m x 0.25 m, 2.0 kg) from a conveyor to a pallet. "
            "Budget is limited, so choose an economical robot. 120 cartons/hour."
        ),
        complexity="medium",
        expected_robot="ur5",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P45",
        description="Palletizing – dual conveyor input",
        prompt=(
            "Build a palletizing workcell with a UR10e robot. "
            "Two conveyor belts feed cartons (0.40 m x 0.30 m x 0.25 m, 5.0 kg). "
            "Robot alternates between both conveyors and stacks cartons on a euro pallet. "
            "Combined throughput: 120 cartons/hour."
        ),
        complexity="medium",
        expected_robot="ur10e",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P46",
        description="Palletizing – collaborative no safety fencing",
        prompt=(
            "Design a collaborative palletizing cell for a warehouse. "
            "Cartons: 0.35 m x 0.30 m x 0.25 m, 3.0 kg. "
            "The robot must work safely alongside humans — no safety fencing. "
            "Conveyor to euro pallet. 90 items/hour."
        ),
        complexity="medium",
        expected_robot="ur5e",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P47",
        description="Palletizing – shift-based throughput spec",
        prompt=(
            "I need a palletizing system that can handle 960 cartons in an 8-hour shift "
            "(0.30 m x 0.25 m x 0.20 m, 2.5 kg each). "
            "UR5 robot, conveyor to pallet. Standard components."
        ),
        complexity="medium",
        expected_robot="ur5",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P48",
        description="Palletizing – throughput in metric tonnes/hr",
        prompt=(
            "Design a palletizing workcell that can move 3 metric tonnes of cartons per hour. "
            "Each carton is 0.40 m x 0.35 m x 0.25 m and weighs 5.0 kg. "
            "UR10e robot, conveyor to pallet. Standard layout."
        ),
        complexity="medium",
        expected_robot="ur10e",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P49",
        description="Palletizing – robot arm reach constraint",
        prompt=(
            "Build a palletizing cell with limited reach. "
            "The conveyor and pallet must both be within 0.85 m of the robot base. "
            "Cartons: 0.30 m x 0.30 m x 0.25 m, 2.5 kg. "
            "Choose a suitable robot with adequate reach. 100 items/hour."
        ),
        complexity="medium",
        expected_robot="ur5",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P50",
        description="Palletizing – narrow aisle constraint",
        prompt=(
            "Design a palletizing workcell for a narrow aisle (max 1.5 m wide). "
            "Cartons: 0.30 m x 0.25 m x 0.20 m, 2.0 kg. "
            "UR5 robot on pedestal, conveyor to pallet. 100 cartons/hour."
        ),
        complexity="medium",
        expected_robot="ur5",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P51",
        description="Palletizing – elevated pallet on turntable",
        prompt=(
            "Create a palletizing workcell where the euro pallet is elevated on a turntable "
            "(0.15 m high). Cartons: 0.30 m x 0.30 m x 0.30 m, 2.5 kg. "
            "UR5e robot, conveyor input. 120 cartons/hour."
        ),
        complexity="medium",
        expected_robot="ur5e",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P52",
        description="Palletizing – fully automated unattended",
        prompt=(
            "Design a fully automated unattended palletizing system for night shift. "
            "Cartons: 0.35 m x 0.25 m x 0.20 m, 3.0 kg. "
            "UR5e robot. Conveyor feeds automatically. Auto pallet exchange. "
            "120 cartons/hour."
        ),
        complexity="medium",
        expected_robot="ur5e",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P53",
        description="Palletizing – imperial units input",
        prompt=(
            "Set up a palletizing workcell. Cartons are 12 x 10 x 8 inches and weigh 5 lbs. "
            "UR5 robot on pedestal, pick from conveyor, place on pallet. 100 items/hour."
        ),
        complexity="medium",
        expected_robot="ur5",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P54",
        description="Palletizing – ergonomic improvement automation",
        prompt=(
            "We want to automate a manual palletizing task to reduce ergonomic injuries. "
            "Workers currently stack cartons (0.35 m x 0.30 m x 0.25 m, 4.0 kg) "
            "from a conveyor onto wood pallets at 80 items/hour. "
            "Replace with a robotic system using a UR5e or similar."
        ),
        complexity="medium",
        expected_robot="ur5e",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P55",
        description="Palletizing – e-commerce warehouse scenario",
        prompt=(
            "Design an e-commerce palletizing workcell. "
            "Mixed cartons averaging 0.30 m x 0.25 m x 0.20 m, approx 2.5 kg. "
            "Conveyor-fed robot picks and palletizes. Peak throughput: 200 boxes/hour. "
            "Space-efficient layout required."
        ),
        complexity="medium",
        expected_robot="ur5",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P56",
        description="Palletizing – pharmaceutical light cartons",
        prompt=(
            "Design a palletizing system for pharmaceutical cartons "
            "(0.20 m x 0.15 m x 0.10 m, 0.5 kg). "
            "Conveyor to pallet transfer. Clean-room compatible robot. "
            "Throughput: 300 cartons/hour."
        ),
        complexity="medium",
        expected_robot="panda",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P57",
        description="Palletizing – automotive parts cartons",
        prompt=(
            "Build a palletizing cell for automotive-parts cartons "
            "(0.45 m x 0.35 m x 0.30 m, 7.5 kg). "
            "Heavy-duty robot required. Conveyor to pallet. "
            "60 cartons/hour minimum throughput."
        ),
        complexity="medium",
        expected_robot="ur10e",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P58",
        description="Palletizing – retail distribution center",
        prompt=(
            "Set up a palletizing system for a retail distribution center. "
            "Cartons: 0.40 m x 0.30 m x 0.25 m, 4.0 kg. "
            "Robot should transfer from roller conveyor to pallet efficiently. "
            "UR5e preferred. 100 cartons/hour."
        ),
        complexity="medium",
        expected_robot="ur5e",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P59",
        description="Palletizing – beverage cartons",
        prompt=(
            "Design a palletizing workcell for beverage cartons "
            "(0.30 m x 0.20 m x 0.25 m, 4.5 kg). "
            "Conveyor to euro pallet. Choose appropriate robot. "
            "Throughput: 80 cartons/hour."
        ),
        complexity="medium",
        expected_robot="ur5e",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P60",
        description="Palletizing – partial conveyor description",
        prompt=(
            "Create a robotic palletizing cell. Cartons weigh 3.0 kg and are roughly "
            "30 cm x 25 cm x 20 cm. A belt conveyor delivers them to the robot pick point. "
            "UR5e robot on pedestal. Pallet standard euro size. 100 cartons/hour."
        ),
        complexity="medium",
        expected_robot="ur5e",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P61",
        description="Palletizing – FMCG grocery distribution",
        prompt=(
            "Design a palletizing system for an FMCG grocery distribution center. "
            "Mixed cartons (average 0.30 m x 0.25 m x 0.20 m, 2.5 kg). "
            "Automated palletizing from conveyor to pallet. 150 cartons/hour. "
            "Recommend robot and workcell layout."
        ),
        complexity="medium",
        expected_robot="ur5",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P62",
        description="Palletizing – seasonal peak throughput variation",
        prompt=(
            "Build a palletizing workcell that handles normal 100 cartons/hour but "
            "peaks at 180 during holiday season. "
            "Cartons: 0.30 m x 0.25 m x 0.20 m, 2.0 kg. "
            "UR5 robot, conveyor to pallet."
        ),
        complexity="medium",
        expected_robot="ur5",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P63",
        description="Palletizing – floor-mounted robot no pedestal",
        prompt=(
            "Design a palletizing workcell where the UR5e robot is floor-mounted rather than "
            "on a pedestal. Cartons: 0.30 m x 0.25 m x 0.20 m, 2.5 kg. "
            "Conveyor to pallet. 120 cartons/hour."
        ),
        complexity="medium",
        expected_robot="ur5e",
        expected_components=["conveyor", "pallet"],
    ),
    TestPrompt(
        id="P64",
        description="Palletizing – spec via cycle time only",
        prompt=(
            "I need a palletizing robot cell with a 25-second cycle time. "
            "Cartons: 0.30 m x 0.25 m x 0.20 m, 2.5 kg. "
            "Conveyor to pallet. Good industrial robot."
        ),
        complexity="medium",
        expected_robot="ur5",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P65",
        description="Palletizing – pallet at different height than conveyor",
        prompt=(
            "Build a palletizing workcell. The conveyor is at 0.82 m height, and the "
            "pallet surface is at 0.15 m. A UR5e robot must bridge this height difference. "
            "Cartons: 0.30 m x 0.25 m x 0.20 m, 2.5 kg. 100 items/hour."
        ),
        complexity="medium",
        expected_robot="ur5e",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),

    # ── HIGH COMPLEXITY P66–P100 ───────────────────────────────────────
    TestPrompt(
        id="P66",
        description="Vague – just robot to move boxes to pallet",
        prompt=(
            "I need a robot to move boxes from a conveyor to a pallet."
        ),
        complexity="high",
        expected_robot="ur5",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P67",
        description="Conflicting – UR5 but weight exceeds payload",
        prompt=(
            "Design a workcell using a UR5 robot (payload 5 kg) to palletize "
            "steel ingot cartons (0.30 m x 0.30 m x 0.30 m, 12 kg). "
            "Conveyor to pallet. 100 items/hour."
        ),
        complexity="high",
        expected_robot="ur5",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P68",
        description="Conflicting – unreachable throughput for single robot",
        prompt=(
            "Design a palletizing workcell for 1000 cartons/hour with a single UR5. "
            "Cartons: 0.30 m x 0.25 m x 0.20 m, 2.0 kg. Standard layout."
        ),
        complexity="high",
        expected_robot="ur5",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P69",
        description="Palletizing – multi-SKU sorting to separate pallets",
        prompt=(
            "Design a palletizing workcell that handles three carton SKUs: "
            "small (0.20x0.15x0.12 m, 0.8 kg), medium (0.30x0.25x0.20 m, 2.5 kg), "
            "and large (0.45x0.35x0.30 m, 6.0 kg). "
            "All arrive on the same conveyor. Robot sorts them to separate pallets. "
            "Total throughput: 150 cartons/hour across all SKUs."
        ),
        complexity="high",
        expected_robot="ur10e",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P70",
        description="Palletizing – described using warehouse KPIs",
        prompt=(
            "Automate our palletizing bottleneck. We process 2000 cartons per 8-hour shift. "
            "Each carton is roughly 30 cm cube and weighs about 3 kg. "
            "Current manual process uses a roller conveyor and euro pallets. "
            "Design a robotic solution that replaces two workers."
        ),
        complexity="high",
        expected_robot="ur5",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P71",
        description="Palletizing – colloquial description",
        prompt=(
            "We want to automate the loading dock. Guys are putting boxes one by one "
            "from the conveyor onto pallets. The boxes are medium-size, maybe 3 kg each. "
            "We want a robot arm to do this automatically. Around 100 boxes an hour."
        ),
        complexity="high",
        expected_robot="ur5",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P72",
        description="Palletizing – cobot collaborative request",
        prompt=(
            "Design a palletizing system using a cobot. "
            "Cartons: 0.30 m x 0.25 m x 0.20 m, 2.5 kg. "
            "Conveyor to pallet. Collaborative, safe for human proximity. "
            "100 cartons/hour."
        ),
        complexity="high",
        expected_robot="ur5e",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P73",
        description="Palletizing – AI-guided placement request",
        prompt=(
            "Design a next-generation palletizing workcell where the robot uses "
            "AI to decide optimal carton placement on the pallet for maximum density. "
            "Cartons: 0.30 m x 0.25 m x 0.20 m, 2.5 kg. UR5e robot. 100 cartons/hour."
        ),
        complexity="high",
        expected_robot="ur5e",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P74",
        description="Palletizing – Panda but weight over payload",
        prompt=(
            "I want a Franka Panda palletizing cell to transfer heavy cartons "
            "(0.40 m x 0.35 m x 0.30 m, 8.0 kg) from a conveyor onto a pallet. "
            "The Panda has a 3 kg payload — flag any issues. 80 items/hour."
        ),
        complexity="high",
        expected_robot="panda",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P75",
        description="Palletizing – zero-info brief",
        prompt=(
            "Palletizing robot cell needed."
        ),
        complexity="high",
        expected_robot="ur5",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P76",
        description="Palletizing – narrative paragraph style",
        prompt=(
            "Our factory produces packaged goods that come off the production line on a "
            "roller conveyor. At the end of the line, a worker manually stacks the "
            "packages onto wood pallets. The packages are cardboard boxes, roughly "
            "30 cm x 25 cm x 20 cm and about 2.5 kg each. We do about 120 boxes an hour. "
            "We need to automate this with a robot arm."
        ),
        complexity="high",
        expected_robot="ur5",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P77",
        description="Palletizing – multiple competing throughput specs",
        prompt=(
            "Design a palletizing workcell. We need 100 cartons/hour average but "
            "sometimes up to 200 cartons/hour during peaks. "
            "Cartons: 0.30 m x 0.25 m x 0.20 m, 2.5 kg. UR5 robot. Conveyor to pallet."
        ),
        complexity="high",
        expected_robot="ur5",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P78",
        description="Palletizing – unusual pallet size",
        prompt=(
            "Build a palletizing workcell with a UR5 robot. "
            "Cartons: 0.30 m x 0.30 m x 0.25 m, 2.5 kg. "
            "Destination is an unusual-sized pallet: 0.9 m x 0.7 m x 0.12 m. "
            "Conveyor input. 100 cartons/hour."
        ),
        complexity="high",
        expected_robot="ur5",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P79",
        description="Palletizing – mixed language input",
        prompt=(
            "We need to automate our palletierstation. "
            "Cartons are approximately 30 x 25 x 20 cm, weight approximately 2.5 kg. "
            "A UR5 robot should pick cartons from the conveyor onto the pallet. "
            "120 cartons per hour."
        ),
        complexity="high",
        expected_robot="ur5",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P80",
        description="Palletizing – spec by industry analogy",
        prompt=(
            "Design a palletizing workcell similar to those used in Amazon fulfillment centers. "
            "Standard cardboard boxes from a conveyor onto a pallet. "
            "UR5e robot. Target 150 items per hour."
        ),
        complexity="high",
        expected_robot="ur5e",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P81",
        description="Palletizing – outdoor IP65 rated environment",
        prompt=(
            "Design a robust outdoor palletizing workcell (IP65 rating) for a port terminal. "
            "Cartons: 0.40 m x 0.35 m x 0.30 m, 5.0 kg. "
            "UR10e robot, conveyor to pallet. 80 cartons/hour. "
            "Must operate in temperatures from -10 C to 45 C."
        ),
        complexity="high",
        expected_robot="ur10e",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P82",
        description="Conflicting – incorrectly specified robot reach",
        prompt=(
            "Build a palletizing cell with a UR5 robot (reach 0.5 m). "
            "Cartons: 0.30 m x 0.25 m x 0.20 m, 2.5 kg. "
            "Conveyor 1.5 m from robot base, pallet 1.2 m from robot base. "
            "120 cartons/hour."
        ),
        complexity="high",
        expected_robot="ur5",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P83",
        description="Palletizing – brand mention no specific model",
        prompt=(
            "We already have a Universal Robots arm available. "
            "Just set up a workcell where it grabs boxes from the conveyor and puts them on a pallet. "
            "Boxes are 3 kg max. Around 100 pieces per hour."
        ),
        complexity="high",
        expected_robot="ur5",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P84",
        description="Palletizing – spec as production rate not cycle time",
        prompt=(
            "Our packaging line produces 2 cartons per minute. "
            "We need a robot to palletize them continuously. "
            "Cartons: 0.30 m x 0.25 m x 0.20 m, 2.0 kg. "
            "Recommend a robot and design the palletizing workcell."
        ),
        complexity="high",
        expected_robot="ur5",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P85",
        description="Palletizing – simulation before hardware purchase",
        prompt=(
            "Before purchasing hardware, I would like to simulate a palletizing workcell. "
            "UR5 robot, standard cardboard cartons (0.30 m x 0.25 m x 0.20 m, 2.5 kg), "
            "conveyor to euro pallet. 120 items per hour. Please design and simulate it."
        ),
        complexity="high",
        expected_robot="ur5",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P86",
        description="Palletizing – constraints only no explicit specs",
        prompt=(
            "Design a palletizing workcell with the following constraints: "
            "max footprint 3 m x 3 m, max cycle time 30 s, carton weight under 5 kg. "
            "Conveyor input, pallet output. Choose appropriate robot."
        ),
        complexity="high",
        expected_robot="ur5",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P87",
        description="Palletizing – sustainability energy-efficient focus",
        prompt=(
            "Design an energy-efficient robotic palletizing workcell for a sustainable factory. "
            "Cartons: 0.30 m x 0.25 m x 0.20 m, 2.0 kg (recycled cardboard). "
            "UR5e robot. Minimize energy consumption. 100 cartons/hour."
        ),
        complexity="high",
        expected_robot="ur5e",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P88",
        description="Palletizing – ROI question embedded",
        prompt=(
            "We want to automate palletizing to save costs. Two workers currently stack "
            "cartons (0.30 m x 0.25 m x 0.20 m, 2.5 kg) from a conveyor at 100/hour. "
            "Design a UR5e robotic palletizing cell and estimate ROI."
        ),
        complexity="high",
        expected_robot="ur5e",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P89",
        description="Palletizing – brick-layer stacking pattern",
        prompt=(
            "Design a palletizing workcell that stacks cartons in a brick-layer pattern "
            "to maximise pallet stability. Cartons: 0.30 m x 0.25 m x 0.20 m, 2.5 kg. "
            "UR5 robot, conveyor to euro pallet. 100 cartons/hour."
        ),
        complexity="high",
        expected_robot="ur5",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P90",
        description="Palletizing – vacuum suction gripper specified",
        prompt=(
            "Build a palletizing workcell with a UR5 robot and vacuum suction gripper. "
            "Pick smooth-surfaced cartons (0.35 m x 0.30 m x 0.25 m, 3.0 kg) from a conveyor "
            "onto a euro pallet. 100 cartons/hour. Safety fence required."
        ),
        complexity="high",
        expected_robot="ur5",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P91",
        description="Palletizing – spec in CAD coordinate notation",
        prompt=(
            "Robotic palletiser. Robot: UR5e. Pick point: (0, -0.8, 0.82). "
            "Place point: (1.2, 0.8, 0.15). Cartons 300x250x200 mm, 2.5 kg. "
            "120 pcs/hr. Standard pedestal."
        ),
        complexity="high",
        expected_robot="ur5e",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P92",
        description="Palletizing – vague boxes on belt",
        prompt=(
            "Automate palletizing boxes with a robot. Boxes come on a belt, robot puts them on pallet."
        ),
        complexity="high",
        expected_robot="ur5",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P93",
        description="Palletizing – mislabelled as de-palletizing",
        prompt=(
            "We need to palletize cartons arriving from the production line conveyor. "
            "Someone called this de-palletizing but what we mean is: robot picks cartons "
            "from the conveyor and stacks them on a pallet. "
            "Cartons: 0.30 m x 0.25 m x 0.20 m, 2.5 kg. UR5e. 100/hour."
        ),
        complexity="high",
        expected_robot="ur5e",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P94",
        description="Conflicting – incorrect physics description",
        prompt=(
            "Design a palletizing workcell with a UR5. "
            "Cartons weigh 2.5 kg normally. Robot picks from conveyor to pallet. "
            "120 cartons/hour. Standard pedestal and industrial conveyor."
        ),
        complexity="high",
        expected_robot="ur5",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P95",
        description="Palletizing – request given as JSON",
        prompt=(
            '{"task": "palletizing", "robot": "UR5", "payload_kg": 2.5, '
            '"carton_dims_m": [0.30, 0.25, 0.20], "throughput_per_hour": 120, '
            '"source": "conveyor", "destination": "euro pallet"}'
        ),
        complexity="high",
        expected_robot="ur5",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P96",
        description="Palletizing – part of larger warehouse system",
        prompt=(
            "We are building a full automated warehouse. As part of it, we need a "
            "palletizing station where a robot takes cartons from the end of a conveyor "
            "and loads them onto pallets. Cartons: 0.30 x 0.25 x 0.20 m, 2.5 kg. "
            "UR5e. Around 100/hour."
        ),
        complexity="high",
        expected_robot="ur5e",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P97",
        description="Palletizing – exactly one robot arm constraint",
        prompt=(
            "Design a palletizing system using exactly one robot arm. No gantries, no SCARA. "
            "Standard cartons (0.30 m x 0.25 m x 0.20 m, 2.5 kg) from conveyor to pallet. "
            "As high a throughput as possible."
        ),
        complexity="high",
        expected_robot="ur5",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P98",
        description="Palletizing – non-existent robot model requested",
        prompt=(
            "I'd like to use a UR7 robot for palletizing cartons (0.30 m x 0.25 m x 0.20 m, 2.5 kg) "
            "from a conveyor to a pallet. 120 cartons/hour."
        ),
        complexity="high",
        expected_robot="ur5",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P99",
        description="Conflicting – cycle time vs throughput mismatch",
        prompt=(
            "Design a palletizing cell with UR5 robot. "
            "Throughput required: 200 cartons/hour (which is 18 s per carton), "
            "but cycle time must be 60 s. Cartons: 0.30 m x 0.25 m x 0.20 m, 2.5 kg. "
            "Conveyor to pallet."
        ),
        complexity="high",
        expected_robot="ur5",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
    TestPrompt(
        id="P100",
        description="Palletizing – maximum complexity multi-constraint",
        prompt=(
            "Design a complete robotic palletizing workcell for a multi-product beverage factory. "
            "The system must handle carton sizes ranging from small (0.20x0.15x0.12 m, 0.8 kg) "
            "to large (0.50x0.40x0.35 m, 8.0 kg), all arriving on the same conveyor belt. "
            "The robot must identify carton type and stack accordingly on one of two pallets. "
            "Peak throughput: 200 cartons/hour. Available budget allows one robot. "
            "Floor space: 4 m x 4 m maximum. Safety fencing required. "
            "The robot should also handle pallet-full detection and alert the operator. "
            "Suggest the best robot model and justify the choice."
        ),
        complexity="high",
        expected_robot="ur10e",
        expected_components=["pedestal", "conveyor", "pallet"],
    ),
]


def get_test_prompts(count: int = None, complexity: str = None, offset: int = 0) -> List[TestPrompt]:
    """
    Get test prompts, optionally filtered and sliced.

    Args:
        count: Max number of prompts to return after applying offset.
        complexity: Filter by complexity level.
        offset: Number of prompts to skip from the start (for batched runs).
                E.g. offset=20, count=20 → runs P21-P40.

    Returns:
        List of TestPrompt instances.
    """
    prompts = TEST_PROMPTS
    if complexity:
        prompts = [p for p in prompts if p.complexity == complexity]
    if offset:
        prompts = prompts[offset:]
    if count:
        prompts = prompts[:count]
    return prompts
