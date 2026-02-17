"""Enhanced logging configuration for Robot Workcell Design Agent.

Provides detailed logging of LLM interactions, script executions, and workflow progression.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

# Create logs directory
LOGS_DIR = Path(__file__).parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Generate timestamped log file
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_FILE = LOGS_DIR / f"agent_{timestamp}.log"


def setup_logging(level: str = "INFO", enable_debug: bool = False):
    """
    Configure comprehensive logging for the agent.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        enable_debug: If True, enables DEBUG level for all loggers
    """
    # Map string level to logging constant
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    if enable_debug:
        numeric_level = logging.DEBUG
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        fmt="%(asctime)s  %(name)-30s  %(levelname)-8s  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    simple_formatter = logging.Formatter(
        fmt="%(asctime)s  %(levelname)-8s  %(message)s",
        datefmt="%H:%M:%S"
    )
    
    # Console handler (INFO and above, simple format)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    
    # File handler (DEBUG and above, detailed format)
    file_handler = logging.FileHandler(LOG_FILE, mode='a', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    root_logger.handlers.clear()  # Remove any existing handlers
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    # Configure package loggers
    for logger_name in ['src', 'robot_workcell_agent', '__main__']:
        pkg_logger = logging.getLogger(logger_name)
        pkg_logger.setLevel(numeric_level)
        pkg_logger.propagate = True
    
    # Suppress noisy third-party loggers
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('httpcore').setLevel(logging.WARNING)
    logging.getLogger('openai').setLevel(logging.WARNING)
    
    # Log initialization
    logger = logging.getLogger(__name__)
    logger.info("="*80)
    logger.info(f"ROBOT WORKCELL DESIGN AGENT - Session started")
    logger.info(f"Log file: {LOG_FILE}")
    logger.info(f"Log level: {logging.getLevelName(numeric_level)}")
    logger.info("="*80)
    
    return LOG_FILE


def log_stage_1_json(json_data: dict, logger: Optional[logging.Logger] = None):
    """
    Log Stage 1 JSON output prominently.
    
    Args:
        json_data: The Stage 1 JSON dictionary
        logger: Optional logger instance
    """
    import json
    
    if logger is None:
        logger = logging.getLogger(__name__)
    
    separator = "="*80
    
    logger.info("")
    logger.info(separator)
    logger.info("📋 STAGE 1 COMPLETE - Requirements JSON")
    logger.info(separator)
    logger.info(json.dumps(json_data, indent=2, ensure_ascii=False))
    logger.info(separator)
    logger.info("")


def log_llm_interaction(prompt: str, response: str, logger: Optional[logging.Logger] = None):
    """
    Log LLM prompt and response.
    
    Args:
        prompt: The prompt sent to the LLM
        response: The response from the LLM
        logger: Optional logger instance
    """
    if logger is None:
        logger = logging.getLogger(__name__)
    
    logger.debug("="*80)
    logger.debug("🤖 LLM INTERACTION")
    logger.debug("-"*80)
    logger.debug("PROMPT:")
    logger.debug(prompt[:1000] + "..." if len(prompt) > 1000 else prompt)
    logger.debug("-"*80)
    logger.debug("RESPONSE:")
    logger.debug(response[:1000] + "..." if len(response) > 1000 else response)
    logger.debug("="*80)


def log_workflow_step(step: str, details: str = "", logger: Optional[logging.Logger] = None):
    """
    Log a workflow step prominently.
    
    Args:
        step: Step name/description
        details: Additional details
        logger: Optional logger instance
    """
    if logger is None:
        logger = logging.getLogger(__name__)
    
    logger.info(f"▶️  {step}")
    if details:
        logger.info(f"   {details}")
