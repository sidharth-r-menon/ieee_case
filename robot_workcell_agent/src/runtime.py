"""Runtime executor for skill scripts.

This is the core runtime system that executes scripts from skills/*/scripts/.
Scripts communicate via stdin/stdout using JSON format.

For long-running scripts (like genesis_scene_builder), uses Popen to read
stdout without waiting for the process to terminate.

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

# Skills that run continuously (simulation loop) - use Popen instead of run
LONG_RUNNING_SKILLS = {"genesis_scene_builder"}


def run_skill_script(
    skill_name: str,
    script_name: str,
    args: Optional[Dict[str, Any]] = None,
    timeout: int = 900
) -> Dict[str, Any]:
    """
    Execute a skill script with JSON input/output via stdin/stdout.

    For normal scripts: uses subprocess.run (blocking).
    For long-running scripts (genesis): uses Popen to read JSON output
    without waiting for the process to terminate (it keeps running).

    Args:
        skill_name: Name of the skill (e.g., "request_interpreter")
        script_name: Name of the script without .py (e.g., "interpret_request")
        args: Dictionary of arguments to pass to script via stdin
        timeout: Maximum execution time in seconds

    Returns:
        Dictionary parsed from script's JSON stdout
    """

    # Script name mapping for genesis_scene_builder
    if skill_name == "genesis_scene_builder" and script_name == "build_genesis_scene":
        logger.warning("Redirecting build_genesis_scene to build_and_execute for genesis_scene_builder.")
        script_name = "build_and_execute"

    script_path = SKILLS_DIR / skill_name / "scripts" / f"{script_name}.py"

    if not script_path.exists():
        logger.error(
            f"script_not_found: skill={skill_name}, script={script_name}, "
            f"path={script_path}"
        )
        raise FileNotFoundError(f"Script not found: {script_path}")

    input_json = json.dumps(args or {})

    logger.info(
        f"executing_script: skill={skill_name}, script={script_name}, "
        f"args_size={len(input_json)}"
    )
    
    # Log the full input for debugging
    logger.info(f"\n{'='*80}\n📥 SCRIPT INPUT: {skill_name}/{script_name}\n{'-'*80}")
    logger.info(f"{json.dumps(args or {}, indent=2)}")
    logger.info(f"{'='*80}\n")

    # Use Popen for long-running scripts (genesis simulation loop)
    if skill_name in LONG_RUNNING_SKILLS:
        return _run_long_running_script(skill_name, script_name, script_path, input_json, timeout)
    else:
        return _run_short_script(skill_name, script_name, script_path, input_json, timeout)


def _run_short_script(
    skill_name: str,
    script_name: str,
    script_path: Path,
    input_json: str,
    timeout: int
) -> Dict[str, Any]:
    """Run a script that terminates after producing output."""
    import os
    child_env = os.environ.copy()
    child_env["PYTHONIOENCODING"] = "utf-8"
    try:
        process = subprocess.run(
            [sys.executable, str(script_path)],
            input=input_json,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=timeout,
            check=True,
            env=child_env
        )

        result = json.loads(process.stdout)
        
        logger.info(f"\n{'='*80}\n📤 SCRIPT OUTPUT: {skill_name}/{script_name}\n{'-'*80}")
        logger.info(f"{json.dumps(result, indent=2)}")
        logger.info(f"{'='*80}\n")

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
            f"exit_code={e.returncode}, stderr={e.stderr[:500]}"
        )
        try:
            error_data = json.loads(e.stdout)
            return error_data
        except:
            raise

    except json.JSONDecodeError:
        logger.error(
            f"script_invalid_json: skill={skill_name}, script={script_name}, "
            f"stdout={process.stdout[:200]}"
        )
        raise RuntimeError(
            f"Script {script_name} did not output valid JSON. "
            f"Stdout: {process.stdout[:200]}"
        )


def _run_long_running_script(
    skill_name: str,
    script_name: str,
    script_path: Path,
    input_json: str,
    timeout: int
) -> Dict[str, Any]:
    """
    Run a long-running script (e.g., genesis simulation).
    
    For genesis_scene_builder:
    - Launches in a SEPARATE TERMINAL WINDOW (Windows: new console)
    - This decouples Genesis from the agent's terminal
    - User can see Genesis logs in its own window
    - Agent logs stay clean in the main window
    
    Uses Popen to:
    1. Send JSON input via stdin
    2. Read JSON output from stdout using a thread (readline blocks on Windows)
    3. Let the process continue running in background (simulation loop)
    """
    import threading
    import queue
    import time
    import platform
    
    logger.info(f"🚀 Starting long-running script: {skill_name}/{script_name}")
    logger.info(f"📦 Input JSON length: {len(input_json)} chars")
    
    # Determine if we should launch in a separate terminal window
    # For genesis_scene_builder, we want a separate window so user can see the viewer
    launch_in_new_window = (skill_name == "genesis_scene_builder")
    
    try:
        # Configure subprocess creation flags for separate window
        creation_flags = 0
        if launch_in_new_window and platform.system() == 'Windows':
            # CREATE_NEW_CONSOLE: Creates a new console window
            creation_flags = subprocess.CREATE_NEW_CONSOLE
            logger.info(f"🪟 Launching Genesis in a NEW TERMINAL WINDOW")
        
        import os
        # Set UTF-8 encoding for the subprocess to handle Genesis Unicode box-drawing chars
        child_env = os.environ.copy()
        child_env["PYTHONIOENCODING"] = "utf-8"
        
        process = subprocess.Popen(
            [sys.executable, "-u", str(script_path)],  # -u for unbuffered
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            bufsize=0,  # Unbuffered
            creationflags=creation_flags,  # Separate window on Windows
            env=child_env
        )
        logger.info(f"📝 Process started (PID: {process.pid}), sending input...")
        
        # Start stderr logging thread IMMEDIATELY
        stderr_lines = []
        def _log_stderr():
            """Capture stderr in real-time."""
            try:
                for line in process.stderr:
                    if line.strip():
                        # Downgrade all '[genesis]' and normal print lines to INFO unless they contain error/fail/exception
                        lower_line = line.lower()
                        if '[genesis]' in line or not line.startswith('Traceback'):
                            if ('error' in lower_line or 'fail' in lower_line or 'exception' in lower_line):
                                logger.error(f"🔴 genesis_stderr: {line.strip()}")
                            else:
                                logger.info(f"🔵 genesis_log: {line.strip()}")
                        else:
                            logger.error(f"🔴 genesis_stderr: {line.strip()}")
                        stderr_lines.append(line)
            except Exception as e:
                logger.error(f"Error in stderr thread: {e}")
        
        stderr_thread = threading.Thread(target=_log_stderr, daemon=True)
        stderr_thread.start()
        logger.debug(f"🧵 stderr logging thread started")
        
        # Send input and close stdin
        try:
            process.stdin.write(input_json)
            process.stdin.close()
            logger.info(f"✅ Input sent to process, waiting for output...")
        except Exception as e:
            logger.error(f"❌ Failed to send input to process: {e}")
            # Give stderr thread time to capture any error messages
            time.sleep(0.5)
            if stderr_lines:
                logger.error(f"📋 Captured stderr before input failure:")
                for line in stderr_lines:
                    logger.error(f"   {line.strip()}")
            raise
        # Use a thread to read stdout because readline() blocks on Windows
        # and prevents timeout checking in the main thread
        output_queue = queue.Queue()
        error_event = threading.Event()
        def _read_stdout():
            """Read stdout line by line in a background thread."""
            try:
                logger.info(f"🔍 stdout reader thread started, listening for JSON output...")
                output_lines = []
                brace_count = 0
                json_started = False
                line_count = 0
                for line in process.stdout:
                    line_count += 1
                    if not line:
                        logger.debug(f"🔍 Got empty line, breaking")
                        break
                    
                    # Log all lines for debugging (limit to first 150 chars)
                    logger.info(f"🔍 stdout line {line_count}: {line[:150].strip()}")
                    
                    # Track JSON braces to know when we have complete output
                    for char in line:
                        if char == '{':
                            if not json_started:
                                json_started = True
                                logger.info(f"🎯 JSON output started at line {line_count}")
                            brace_count += 1
                        elif char == '}':
                            brace_count -= 1
                    
                    # Only collect lines once JSON has started (skip Genesis logs)
                    if json_started:
                        output_lines.append(line)
                    
                    # Complete JSON object received
                    if json_started and brace_count == 0:
                        logger.info(f"✅ Complete JSON received ({len(output_lines)} lines, {len(''.join(output_lines))} chars)")
                        output_queue.put(('json', ''.join(output_lines)))
                        return
                # Process ended before giving us JSON
                logger.warning(f"⚠️  stdout ended after {line_count} lines without complete JSON")
                output_queue.put(('eof', ''.join(output_lines)))
            except Exception as e:
                logger.error(f"❌ Error in stdout reader thread: {e}")
                output_queue.put(('error', str(e)))
        reader_thread = threading.Thread(target=_read_stdout, daemon=True)
        reader_thread.start()
        logger.info(f"🧵 Reader thread started, waiting up to {timeout}s for output...")
        try:
            msg_type, msg_data = output_queue.get(timeout=timeout)
            logger.info(f"📦 Received message from queue: type={msg_type}, data_len={len(msg_data)})")
        except queue.Empty:
            # Timeout - no output received in time
            logger.error(f"")
            logger.error(f"={'='*80}")
            logger.error(f"⏱️  TIMEOUT ERROR: No output after {timeout}s")
            logger.error(f"={'='*80}")
            
            # Give stderr thread time to finish capturing
            time.sleep(0.5)
            
            # Check if process is still running
            poll_result = process.poll()
            if poll_result is None:
                logger.error(f"❌ Process still running (PID: {process.pid}) - killing...")
                process.kill()
            else:
                logger.error(f"❌ Process exited with code: {poll_result}")
            
            # Show any stderr that was captured
            if stderr_lines:
                logger.error(f"")
                logger.error(f"📋 STDERR OUTPUT ({len(stderr_lines)} lines):")
                logger.error(f"{'-'*80}")
                for line in stderr_lines:
                    logger.error(f"   {line.strip()}")
                logger.error(f"{'-'*80}")
            else:
                logger.error(f"📋 No stderr output captured")
            
            logger.error(f"")
            logger.error(f"💡 TROUBLESHOOTING:")
            logger.error(f"   1. Check if Genesis SDK is installed: pip list | grep genesis")
            logger.error(f"   2. Check if MJCF/URDF paths exist and are readable")
            logger.error(f"   3. Check if graphics drivers support GPU backend")
            logger.error(f"   4. Try running script manually: python {script_path}")
            logger.error(f"   5. Check script input is valid JSON (logged above)")
            logger.error(f"={'='*80}")
            
            raise subprocess.TimeoutExpired(cmd=str(script_path), timeout=timeout)
        
        if msg_type == 'eof':
            # Process ended before producing complete JSON
            logger.error(f"")
            logger.error(f"={'='*80}")
            logger.error(f"❌ SCRIPT ENDED WITHOUT COMPLETE JSON OUTPUT")
            logger.error(f"={'='*80}")
            logger.error(f"Partial stdout ({len(msg_data)} chars):")
            logger.error(f"{msg_data[:500]}")
            
            if stderr_lines:
                logger.error(f"")
                logger.error(f"📋 STDERR OUTPUT ({len(stderr_lines)} lines):")
                logger.error(f"{'-'*80}")
                for line in stderr_lines[:50]:  # First 50 lines
                    logger.error(f"   {line.strip()}")
                logger.error(f"{'-'*80}")
            
            logger.error(f"={'='*80}")
            raise RuntimeError(
                f"Genesis process ended before producing output. "
                f"Check stderr above for details."
            )
        
        if msg_type == 'error':
            raise RuntimeError(f"Error reading genesis stdout: {msg_data}")
        
        # msg_type == 'json'
        stdout_text = msg_data
        result = json.loads(stdout_text)
        
        logger.info(f"\n{'='*80}\n📤 SCRIPT OUTPUT: {skill_name}/{script_name}\n{'-'*80}")
        logger.info(f"{json.dumps(result, indent=2)}")
        logger.info(f"{'='*80}\n")
        
        logger.info(
            f"script_success: skill={skill_name}, script={script_name}, "
            f"output_size={len(stdout_text)}, process_pid={process.pid} (still running)"
        )
        
        # Log special message for Genesis
        if skill_name == "genesis_scene_builder":
            logger.info(f"")
            logger.info(f"{'='*80}")
            logger.info(f"✅ GENESIS VIEWER IS RUNNING IN SEPARATE WINDOW")
            logger.info(f"{'='*80}")
            logger.info(f"Process ID: {process.pid}")
            logger.info(f"The Genesis viewer window should now be visible on your desktop.")
            logger.info(f"Genesis logs are shown in its dedicated terminal window.")
            logger.info(f"The scene will stay active until:")
            logger.info(f"  1. User closes the Genesis viewer window")
            logger.info(f"  2. Trajectory execution takes over")
            logger.info(f"  3. User presses Ctrl+C in the Genesis terminal")
            logger.info(f"{'='*80}")
            logger.info(f"")
        
        # stderr is already being logged by the thread started earlier
        
        return result
        
    except json.JSONDecodeError:
        stdout_text = msg_data if 'msg_data' in dir() else ""
        logger.error(
            f"script_invalid_json: skill={skill_name}, script={script_name}, "
            f"stdout={stdout_text[:200]}"
        )
        # Only kill process if it's NOT genesis (we want genesis viewer to stay open even on error)
        if 'process' in locals() and skill_name != "genesis_scene_builder":
            process.kill()
        raise RuntimeError(
            f"Script {script_name} did not output valid JSON. "
            f"Stdout: {stdout_text[:200]}"
        )
    except subprocess.TimeoutExpired:
        raise
    except Exception as e:
        # Only kill process if it's NOT genesis (we want genesis viewer to stay open for debugging)
        if 'process' in locals() and skill_name != "genesis_scene_builder":
            try:
                process.kill()
            except:
                pass
        raise


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
