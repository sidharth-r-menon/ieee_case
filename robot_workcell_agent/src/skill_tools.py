"""Progressive disclosure tools for robot workcell design skills."""

import logging
from typing import TYPE_CHECKING
from pathlib import Path

from pydantic_ai import RunContext

if TYPE_CHECKING:
    from src.dependencies import AgentDependencies

logger = logging.getLogger(__name__)


async def load_skill(
    ctx: RunContext["AgentDependencies"],
    skill_name: str,
) -> str:
    """
    Load the full instructions for a skill (Level 2 progressive disclosure).

    This tool implements Level 2 of the progressive disclosure pattern.
    When the agent decides a skill is needed based on Level 1 metadata,
    it calls this tool to get the full instructions from SKILL.md.

    Args:
        ctx: Agent runtime context with dependencies
        skill_name: Name of the skill to load

    Returns:
        Full skill instructions from SKILL.md (body only, without frontmatter)
    """
    skill_loader = ctx.deps.skill_loader

    if skill_loader is None:
        logger.error("load_skill_failed: skill_loader not initialized")
        return "Error: Skill loader not initialized. Please try again."

    if skill_name not in skill_loader.skills:
        available = list(skill_loader.skills.keys())
        logger.warning(f"load_skill_not_found: skill_name={skill_name}, available={available}")
        return f"Error: Skill '{skill_name}' not found. Available skills: {available}"

    skill = skill_loader.skills[skill_name]
    skill_md = skill.skill_path / "SKILL.md"

    try:
        content = skill_md.read_text(encoding="utf-8")

        # Strip YAML frontmatter - return only body
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                body = parts[2].strip()
                logger.info(f"load_skill_success: skill_name={skill_name}, body_length={len(body)}")
                return body

        # No frontmatter, return as-is
        logger.info(f"load_skill_success: skill_name={skill_name}, content_length={len(content)}")
        return content

    except Exception as e:
        logger.exception(f"load_skill_error: skill_name={skill_name}, error={str(e)}")
        return f"Error loading skill '{skill_name}': {str(e)}"


async def read_skill_file(
    ctx: RunContext["AgentDependencies"],
    skill_name: str,
    file_path: str,
) -> str:
    """
    Read a specific file from a skill's directory (Level 3 progressive disclosure).

    This implements Level 3 of progressive disclosure - loading specific
    resource files like scripts, configuration files, or documentation.

    Args:
        ctx: Agent runtime context with dependencies
        skill_name: Name of the skill
        file_path: Relative path to file within skill directory

    Returns:
        File contents or error message
    """
    skill_loader = ctx.deps.skill_loader

    if skill_loader is None:
        logger.error("read_skill_file_failed: skill_loader not initialized")
        return "Error: Skill loader not initialized. Please try again."

    if skill_name not in skill_loader.skills:
        available = list(skill_loader.skills.keys())
        logger.warning(f"read_skill_file_not_found: skill_name={skill_name}, available={available}")
        return f"Error: Skill '{skill_name}' not found. Available skills: {available}"

    skill = skill_loader.skills[skill_name]
    target_file = skill.skill_path / file_path

    # Security: Prevent directory traversal
    try:
        resolved_target = target_file.resolve()
        resolved_skill_path = skill.skill_path.resolve()

        if not resolved_target.is_relative_to(resolved_skill_path):
            logger.warning(
                f"read_skill_file_security_violation: skill_name={skill_name}, "
                f"file_path={file_path}, resolved={resolved_target}"
            )
            return f"Error: Invalid file path. File must be within skill directory."

    except Exception as e:
        logger.error(f"read_skill_file_path_error: skill_name={skill_name}, file_path={file_path}")
        return f"Error: Invalid file path: {str(e)}"

    # Read file
    try:
        if not target_file.exists():
            logger.warning(
                f"read_skill_file_not_found: skill_name={skill_name}, file_path={file_path}"
            )
            return f"Error: File '{file_path}' not found in skill '{skill_name}'."

        content = target_file.read_text(encoding="utf-8")
        logger.info(
            f"read_skill_file_success: skill_name={skill_name}, file_path={file_path}, "
            f"content_length={len(content)}"
        )
        return content

    except Exception as e:
        logger.exception(
            f"read_skill_file_error: skill_name={skill_name}, file_path={file_path}, error={str(e)}"
        )
        return f"Error reading file '{file_path}': {str(e)}"


async def list_skill_files(
    ctx: RunContext["AgentDependencies"],
    skill_name: str,
    directory: str = "",
) -> str:
    """
    List files available in a skill's directory.

    This tool helps the agent discover what resources are available
    within a skill before loading them. Useful when the agent needs
    to explore what documentation or scripts are available.

    Args:
        ctx: Agent runtime context with dependencies
        skill_name: Name of the skill to list files from
        directory: Optional subdirectory to list (e.g., "scripts")

    Returns:
        Formatted list of available files
    """
    skill_loader = ctx.deps.skill_loader

    if skill_loader is None:
        logger.error("list_skill_files_failed: skill_loader not initialized")
        return "Error: Skill loader not initialized. Please try again."

    if skill_name not in skill_loader.skills:
        available = list(skill_loader.skills.keys())
        logger.warning(
            f"list_skill_files_not_found: skill_name={skill_name}, available={available}"
        )
        return f"Error: Skill '{skill_name}' not found. Available skills: {available}"

    skill = skill_loader.skills[skill_name]
    target_dir = skill.skill_path / directory if directory else skill.skill_path

    # Security: Prevent directory traversal
    try:
        resolved_target = target_dir.resolve()
        resolved_skill_path = skill.skill_path.resolve()

        if not resolved_target.is_relative_to(resolved_skill_path):
            logger.warning(
                f"list_skill_files_security_violation: skill_name={skill_name}, "
                f"directory={directory}"
            )
            return "Error: Invalid directory path."

    except Exception as e:
        logger.error(
            f"list_skill_files_path_error: skill_name={skill_name}, directory={directory}"
        )
        return f"Error: Invalid directory path: {str(e)}"

    # List files
    try:
        if not target_dir.exists():
            logger.warning(
                f"list_skill_files_not_found: skill_name={skill_name}, directory={directory}"
            )
            return f"Error: Directory '{directory}' not found in skill '{skill_name}'."

        if not target_dir.is_dir():
            logger.warning(
                f"list_skill_files_not_directory: skill_name={skill_name}, directory={directory}"
            )
            return f"Error: '{directory}' is not a directory."

        files = []
        dirs = []

        for item in sorted(target_dir.iterdir()):
            relative_path = item.relative_to(skill.skill_path)
            if item.is_dir():
                dirs.append(f"📁 {relative_path}/")
            else:
                files.append(f"📄 {relative_path}")

        result_lines = [f"Files in skill '{skill_name}'" + (f"/{directory}" if directory else "") + ":"]
        result_lines.extend(dirs)
        result_lines.extend(files)

        result = "\n".join(result_lines)
        logger.info(
            f"list_skill_files_success: skill_name={skill_name}, directory={directory}, "
            f"file_count={len(files)}, dir_count={len(dirs)}"
        )
        return result

    except Exception as e:
        logger.exception(
            f"list_skill_files_error: skill_name={skill_name}, directory={directory}, "
            f"error={str(e)}"
        )
        return f"Error listing files: {str(e)}"
