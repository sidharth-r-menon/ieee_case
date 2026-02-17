"""
Pydantic schemas for validating workcell design outputs.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator


class ObjectSpecification(BaseModel):
    """Specification for an object to be manipulated."""
    name: str = Field(..., description="Object name (e.g., 'carton', 'bottle')")
    sku_id: str = Field(..., description="Unique identifier for this object type")
    dimensions: List[float] = Field(..., description="[length, width, height] in meters", min_length=3, max_length=3)
    weight_kg: float = Field(..., gt=0, description="Weight in kilograms")
    material: str = Field(..., description="Material type (e.g., 'cardboard', 'plastic')")
    quantity: int = Field(default=1, ge=1, description="Number of this object type")
    
    @field_validator('dimensions')
    @classmethod
    def validate_dimensions(cls, v):
        if len(v) != 3:
            raise ValueError("Dimensions must be [length, width, height]")
        if any(d <= 0 for d in v):
            raise ValueError("All dimensions must be positive")
        return v


class RobotSelection(BaseModel):
    """Selected robot with justification."""
    model: str = Field(..., description="Robot model name (e.g., 'ur5', 'franka_panda')")
    manufacturer: str = Field(..., description="Manufacturer name")
    payload_kg: float = Field(..., gt=0, description="Maximum payload in kg")
    reach_m: float = Field(..., gt=0, description="Maximum reach in meters")
    justification: str = Field(..., min_length=50, description="Why this robot was selected (min 50 chars)")
    urdf_path: Optional[str] = Field(None, description="Path to robot URDF file if available")


class WorkcellComponent(BaseModel):
    """A component in the workcell (conveyor, table, pallet, etc)."""
    name: str = Field(..., description="Component name (e.g., 'conveyor_1', 'pallet_station')")
    component_type: str = Field(..., description="Type: 'conveyor', 'table', 'pallet', 'bin', 'fence', 'pedestal', 'carton'")
    mjcf_path: str = Field(..., description="Path to MJCF file in workcell_components/")
    position: Optional[List[float]] = Field(None, description="[x, y, z] position in meters - filled by placement_solver")
    orientation: Optional[List[float]] = Field(None, description="[x, y, z, w] quaternion - filled by placement_solver")
    dimensions: List[float] = Field(..., description="[length, width, height] in meters - REQUIRED for collision detection", min_length=3, max_length=3)
    
    @field_validator('mjcf_path')
    @classmethod
    def validate_mjcf_path(cls, v):
        if not v.endswith('.xml'):
            raise ValueError("MJCF path must end with .xml")
        return v
    
    @field_validator('dimensions')
    @classmethod
    def validate_dimensions(cls, v):
        if len(v) != 3:
            raise ValueError("Dimensions must be [length, width, height]")
        if any(d <= 0 for d in v):
            raise ValueError("All dimensions must be positive")
        return v


class SpatialZone(BaseModel):
    """A spatial zone in the workcell."""
    zone_name: str = Field(..., description="Zone identifier (e.g., 'input_zone', 'output_zone')")
    zone_type: str = Field(..., description="'input', 'output', 'robot', 'buffer', 'maintenance'")
    center_position: List[float] = Field(..., description="[x, y, z] center in meters", min_length=3, max_length=3)
    radius_m: float = Field(..., gt=0, description="Zone radius in meters")


class SpatialReasoning(BaseModel):
    """Spatial layout reasoning."""
    zones: List[SpatialZone] = Field(..., min_length=1, description="Defined spatial zones")
    material_flow: str = Field(..., min_length=30, description="How materials flow through workcell")
    accessibility: str = Field(..., min_length=30, description="Robot accessibility analysis")
    reasoning: str = Field(..., min_length=50, description="Overall spatial design reasoning")


class Constraint(BaseModel):
    """A constraint on the workcell design."""
    constraint_type: str = Field(..., description="'safety', 'space', 'throughput', 'environmental'")
    description: str = Field(..., min_length=10, description="Constraint description")
    value: Optional[Any] = Field(None, description="Constraint value if quantifiable")


class Stage1Output(BaseModel):
    """Complete Stage 1 output schema - Requirements gathering result."""
    
    stage_1_complete: bool = Field(..., description="Must be True when outputting this schema")
    
    task_objective: str = Field(
        ..., 
        min_length=50, 
        description="Clear description of the task objective (min 50 chars)"
    )
    
    task_specification: ObjectSpecification = Field(
        ...,
        description="Primary object being manipulated"
    )
    
    additional_objects: List[ObjectSpecification] = Field(
        default_factory=list,
        description="Additional objects if any"
    )
    
    robot_selection: RobotSelection = Field(
        ...,
        description="Selected robot with full specifications"
    )
    
    workcell_components: List[WorkcellComponent] = Field(
        ...,
        min_length=1,
        description="All workcell components (conveyor, tables, pallets, etc)"
    )
    
    spatial_reasoning: SpatialReasoning = Field(
        ...,
        description="Spatial layout analysis and reasoning"
    )
    
    throughput_requirement: Dict[str, Any] = Field(
        ...,
        description="{'items_per_hour': X, 'cycle_time_seconds': Y}"
    )
    
    constraints: List[Constraint] = Field(
        default_factory=list,
        description="Design constraints"
    )
    
    missing_info: List[str] = Field(
        default_factory=list,
        description="Must be empty list when stage_1_complete=True"
    )
    
    @field_validator('missing_info')
    @classmethod
    def validate_missing_info(cls, v, info):
        if info.data.get('stage_1_complete') and len(v) > 0:
            raise ValueError("missing_info must be empty when stage_1_complete=True")
        return v


# Export the main schema
__all__ = ['Stage1Output', 'ObjectSpecification', 'RobotSelection', 'WorkcellComponent', 
           'SpatialReasoning', 'Constraint']
