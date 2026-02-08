"""Skill tools as a reusable FunctionToolset for progressive disclosure."""

import json
import subprocess
from typing import Dict, Any, Optional
from pydantic_ai.toolsets import FunctionToolset
from pydantic_ai import RunContext
from src.dependencies import AgentDependencies
from src.skill_tools import load_skill, read_skill_file, list_skill_files
from src.runtime import run_skill_script

# Create the skill tools toolset
skill_tools = FunctionToolset()


@skill_tools.tool
async def load_skill_tool(
    ctx: RunContext[AgentDependencies],
    skill_name: str
) -> str:
    """
    Load the full instructions for a skill (Level 2 progressive disclosure).

    Use this tool when you need to access the detailed instructions
    for a skill. Based on the skill descriptions in your system prompt,
    identify which skill is relevant and load its full instructions.

    Args:
        ctx: Agent runtime context with dependencies
        skill_name: Name of the skill to load (e.g., "interpreter", "placement_solver")

    Returns:
        Full skill instructions from SKILL.md
    """
    return await load_skill(ctx, skill_name)


@skill_tools.tool
async def read_skill_file_tool(
    ctx: RunContext[AgentDependencies],
    skill_name: str,
    file_path: str
) -> str:
    """
    Read a specific file from a skill's directory (Level 3 progressive disclosure).

    Use this tool when you need to access scripts, configuration files,
    or other resources within a skill's directory.

    Args:
        ctx: Agent runtime context with dependencies
        skill_name: Name of the skill
        file_path: Relative path to file within skill directory (e.g., "scripts/interpret_request.py")

    Returns:
        File contents
    """
    return await read_skill_file(ctx, skill_name, file_path)


@skill_tools.tool
async def list_skill_files_tool(
    ctx: RunContext[AgentDependencies],
    skill_name: str,
    directory: str = ""
) -> str:
    """
    List files available in a skill's directory.

    Use this tool to explore what resources are available within a skill
    before loading them. Useful for discovering scripts, documentation, etc.

    Args:
        ctx: Agent runtime context with dependencies
        skill_name: Name of the skill
        directory: Optional subdirectory to list (e.g., "scripts")

    Returns:
        Formatted list of available files
    """
    return await list_skill_files(ctx, skill_name, directory)


@skill_tools.tool
def run_skill_script_tool(
    ctx: RunContext[AgentDependencies],
    skill_name: str,
    script_name: str,
    args: Optional[Dict[str, Any]] = None
) -> str:
    """
    Execute a skill script (CORE RUNTIME CAPABILITY).

    This is the primary execution primitive - it runs Python scripts from
    skills/*/scripts/ with JSON input/output via stdin/stdout.

    Use this tool when SKILL.md instructs you to execute a specific script.
    Only call scripts that are explicitly documented in the skill's instructions.

    Args:
        ctx: Agent runtime context with dependencies
        skill_name: Name of the skill (e.g., "request_interpreter")
        script_name: Name of the script without .py extension (e.g., "interpret_request")
        args: Dictionary of arguments to pass to the script

    Returns:
        JSON string with script results

    Example:
        To interpret a user request:
        result = run_skill_script_tool(
            ctx,
            skill_name="request_interpreter",
            script_name="interpret_request",
            args={"text": "I need a pick and place system"}
        )
    """
    try:
        result = run_skill_script(skill_name, script_name, args or {})
        return json.dumps(result, indent=2)
    except FileNotFoundError as e:
        return json.dumps({
            "error": "script_not_found",
            "message": str(e),
            "skill": skill_name,
            "script": script_name
        }, indent=2)
    except subprocess.TimeoutExpired:
        return json.dumps({
            "error": "timeout",
            "message": f"Script exceeded 30 second timeout",
            "skill": skill_name,
            "script": script_name
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "error": "execution_failed",
            "message": str(e),
            "skill": skill_name,
            "script": script_name
        }, indent=2)
