"""Skill loader for discovering and managing robot workcell design skills."""

import logging
from pathlib import Path
from typing import Dict, List, Optional

import yaml
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class SkillMetadata(BaseModel):
    """Skill metadata from YAML frontmatter."""

    name: str = Field(..., description="Unique skill identifier")
    description: str = Field(..., description="Brief description for agent discovery")
    version: str = Field(default="1.0.0", description="Skill version")
    author: str = Field(default="", description="Skill author")
    skill_path: Path = Field(..., description="Path to skill directory")
    stage: Optional[str] = Field(default=None, description="Pipeline stage (1, 2, or 3)")


class SkillLoader:
    """Loads and manages skills from filesystem."""

    def __init__(self, skills_dir: Path) -> None:
        """
        Initialize skill loader.

        Args:
            skills_dir: Directory containing flat skill structure (skills/skill_name/SKILL.md)
        """
        self.skills_dir = skills_dir
        self.skills: Dict[str, SkillMetadata] = {}

    def discover_skills(self) -> List[SkillMetadata]:
        """
        Scan skills directory for SKILL.md files in flat structure.

        Returns:
            List of discovered skill metadata
        """
        discovered_skills = []

        if not self.skills_dir.exists():
            logger.warning(f"skills_dir_not_found: path={self.skills_dir}")
            return discovered_skills

        # Scan direct subdirectories for SKILL.md files (flat structure)
        for skill_dir in self.skills_dir.iterdir():
            if not skill_dir.is_dir():
                continue
            
            skill_md = skill_dir / "SKILL.md"
            if not skill_md.exists():
                continue

            metadata = self._parse_skill_metadata(skill_md, skill_dir)
            if metadata:
                discovered_skills.append(metadata)
                logger.info(f"skill_discovered: name={metadata.name}, stage={metadata.stage}, version={metadata.version}")

        # Build skills dictionary
        for skill in discovered_skills:
            self.skills[skill.name] = skill

        logger.info(f"skill_discovery_complete: total_count={len(discovered_skills)}")
        return discovered_skills

    def _parse_skill_metadata(
        self, skill_md: Path, skill_dir: Path
    ) -> Optional[SkillMetadata]:
        """
        Parse YAML frontmatter from SKILL.md.

        Args:
            skill_md: Path to SKILL.md
            skill_dir: Path to skill directory

        Returns:
            SkillMetadata if parsing succeeds, None otherwise
        """
        try:
            content = skill_md.read_text(encoding="utf-8")

            # Extract YAML frontmatter
            if not content.startswith("---"):
                logger.warning(f"skill_missing_frontmatter: file={skill_md}")
                return None

            parts = content.split("---", 2)
            if len(parts) < 3:
                logger.warning(f"skill_invalid_frontmatter: file={skill_md}")
                return None

            # Parse YAML
            frontmatter = yaml.safe_load(parts[1])
            if not isinstance(frontmatter, dict):
                logger.warning(f"skill_invalid_yaml: file={skill_md}")
                return None

            # Extract required fields
            if "name" not in frontmatter or "description" not in frontmatter:
                logger.warning(f"skill_missing_required_fields: file={skill_md}")
                return None

            # Get stage from frontmatter (optional)
            stage = frontmatter.get("stage")

            return SkillMetadata(
                name=frontmatter["name"],
                description=frontmatter["description"],
                version=frontmatter.get("version", "1.0.0"),
                author=frontmatter.get("author", ""),
                skill_path=skill_dir,
                stage=stage,
            )

        except yaml.YAMLError as e:
            logger.exception(f"skill_yaml_parse_error: file={skill_md}, error={str(e)}")
            return None
        except Exception as e:
            logger.error(f"skill_parse_error: file={skill_md}, error={str(e)}")
            return None

    def get_skill_metadata_prompt(self) -> str:
        """
        Generate system prompt section with skill metadata.

        Returns:
            Formatted skill metadata for system prompt
        """
        if not self.skills:
            return "No skills available."

        # Group skills by stage
        stage_1_skills = []
        stage_2_skills = []
        stage_3_skills = []
        other_skills = []

        for skill in self.skills.values():
            if skill.stage == "1":
                stage_1_skills.append(skill)
            elif skill.stage == "2":
                stage_2_skills.append(skill)
            elif skill.stage == "3":
                stage_3_skills.append(skill)
            else:
                # Handle None or any other value
                other_skills.append(skill)

        lines = [
            f"Available Skills (EXACTLY {len(self.skills)} — NO OTHERS EXIST):",
            "⚠️ There are NO domain-specific skills (no palletizer, assembler, welder, etc).",
            "⚠️ Do NOT attempt to load any skill not listed here.",
        ]
        lines.append("")

        if stage_1_skills:
            lines.append("## Stage 1: Interpretation & Analysis")
            for skill in stage_1_skills:
                lines.append(f"- **{skill.name}**: {skill.description}")
            lines.append("")

        if stage_2_skills:
            lines.append("## Stage 2: Spatial Optimization")
            for skill in stage_2_skills:
                lines.append(f"- **{skill.name}**: {skill.description}")
            lines.append("")

        if stage_3_skills:
            lines.append("## Stage 3: Validation")
            for skill in stage_3_skills:
                lines.append(f"- **{skill.name}**: {skill.description}")
            lines.append("")

        if other_skills:
            lines.append("## Other Skills")
            for skill in other_skills:
                lines.append(f"- **{skill.name}**: {skill.description}")
            lines.append("")

        return "\n".join(lines)
