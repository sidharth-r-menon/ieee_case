"""Runtime executor for skill scripts.

This is the core runtime system that executes scripts from skills/*/scripts/.
Scripts communicate via stdin/stdout using JSON format.

Pattern inspired by Anthropic custom skills and coleam00/custom-agent-with-skills.
"""

import subprocess
import json
import sys
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Skills directory (configurable via settings)
SKILLS_DIR = Path(__file__).parent.parent / "skills"


def run_skill_script(
    skill_name: str,
    script_name: str,
    args: Optional[Dict[str, Any]] = None,
    timeout: int = 30
) -> Dict[str, Any]:
    """
    Execute a skill script with JSON input/output via stdin/stdout.

    This is the core runtime capability - the single execution primitive
    that enables all skill scripts to run.

    Args:
        skill_name: Name of the skill (e.g., "request_interpreter")
        script_name: Name of the script without .py (e.g., "interpret_request")
        args: Dictionary of arguments to pass to script via stdin
        timeout: Maximum execution time in seconds

    Returns:
        Dictionary parsed from script's JSON stdout

    Raises:
        FileNotFoundError: Script doesn't exist
        subprocess.TimeoutExpired: Script exceeded timeout
        json.JSONDecodeError: Script output wasn't valid JSON
        subprocess.CalledProcessError: Script exited with non-zero code
    """
    script_path = SKILLS_DIR / skill_name / "scripts" / f"{script_name}.py"

    if not script_path.exists():
        logger.error(
            f"script_not_found: skill={skill_name}, script={script_name}, "
            f"path={script_path}"
        )
        raise FileNotFoundError(f"Script not found: {script_path}")

    # Prepare input JSON
    input_json = json.dumps(args or {})

    logger.info(
        f"executing_script: skill={skill_name}, script={script_name}, "
        f"args_size={len(input_json)}"
    )

    try:
        # Execute script with JSON via stdin
        process = subprocess.run(
            [sys.executable, str(script_path)],
            input=input_json,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=True
        )

        # Parse JSON output from stdout
        result = json.loads(process.stdout)

        logger.info(
            f"script_success: skill={skill_name}, script={script_name}, "
            f"output_size={len(process.stdout)}"
        )

        return result

    except subprocess.TimeoutExpired:
        logger.error(
            f"script_timeout: skill={skill_name}, script={script_name}, "
            f"timeout={timeout}s"
        )
        raise

    except subprocess.CalledProcessError as e:
        logger.error(
            f"script_error: skill={skill_name}, script={script_name}, "
            f"exit_code={e.returncode}, stderr={e.stderr[:200]}"
        )
        # Try to return error info if script printed JSON error
        try:
            error_data = json.loads(e.stdout)
            return error_data
        except:
            raise

    except json.JSONDecodeError as e:
        logger.error(
            f"script_invalid_json: skill={skill_name}, script={script_name}, "
            f"stdout={process.stdout[:200]}"
        )
        raise RuntimeError(
            f"Script {script_name} did not output valid JSON. "
            f"Stdout: {process.stdout[:200]}"
        )


def list_skill_scripts(skill_name: str) -> list[str]:
    """
    List available scripts for a skill.

    Args:
        skill_name: Name of the skill

    Returns:
        List of script names (without .py extension)
    """
    scripts_dir = SKILLS_DIR / skill_name / "scripts"

    if not scripts_dir.exists():
        logger.warning(f"scripts_dir_not_found: skill={skill_name}")
        return []

    scripts = [
        f.stem for f in scripts_dir.glob("*.py")
        if f.name != "__init__.py"
    ]

    logger.info(f"listed_scripts: skill={skill_name}, count={len(scripts)}")
    return scripts
