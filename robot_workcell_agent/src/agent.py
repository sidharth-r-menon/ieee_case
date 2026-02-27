"""Main robot workcell design agent implementation with progressive disclosure."""

import logging
from pydantic_ai import Agent, RunContext
from pydantic import BaseModel

from pydantic_ai.settings import ModelSettings
from src.providers import get_llm_model
from src.dependencies import AgentDependencies
from src.prompts import MAIN_SYSTEM_PROMPT, STAGE1_HINT, STAGE2_HINT, STAGE3_HINT
from src.skill_toolset import skill_tools
from src.settings import load_settings

# Initialize settings
_settings = load_settings()

# Configure Logfire only if token is present
if _settings.logfire_token:
    try:
        import logfire

        logfire.configure(
            token=_settings.logfire_token,
            send_to_logfire='if-token-present',
            service_name=_settings.logfire_service_name,
            environment=_settings.logfire_environment,
            console=logfire.ConsoleOptions(show_project_link=False),
        )
        logfire.instrument_pydantic_ai()
        logfire.instrument_httpx(capture_all=True)
        logger = logging.getLogger(__name__)
        logger.info(f"logfire_enabled: service={_settings.logfire_service_name}")
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.warning(f"logfire_initialization_failed: {str(e)}")
else:
    logger = logging.getLogger(__name__)
    logger.info("logfire_disabled: token not provided")


class AgentState(BaseModel):
    """Minimal shared state for the robot workcell design agent."""
    pass


# For Qwen/local provider: inject generation params so pydantic-ai passes them on every call.
# GPT-4o ignores these (Azure sets its own defaults); Qwen needs explicit max_tokens >> 512.
_model_settings: ModelSettings | None = None
if _settings.model_provider.lower() == "qwen":
    _model_settings = ModelSettings(
        temperature=_settings.qwen_temperature,
        max_tokens=_settings.qwen_max_tokens,
        top_p=_settings.qwen_top_p,
    )

# Create the robot workcell design agent
workcell_agent = Agent(
    get_llm_model(),
    deps_type=AgentDependencies,
    system_prompt="",  # Dynamically generated with skill metadata
    toolsets=[skill_tools],  # Skills + runtime executor (run_skill_script_tool)
    model_settings=_model_settings,
)


@workcell_agent.system_prompt
async def get_system_prompt(ctx: RunContext[AgentDependencies]) -> str:
    """
    Generate stage-aware system prompt with skill metadata.

    Implements Level 1 progressive disclosure (skill names + descriptions only)
    AND stage-aware context injection (only the current stage's workflow hint
    is included, avoiding the per-call cost of repeating all 3 stage workflows).
    """
    await ctx.deps.initialize()

    skill_metadata = ""
    if ctx.deps.skill_loader:
        skill_metadata = ctx.deps.skill_loader.get_skill_metadata_prompt()
        # Escape curly braces in skill_metadata to prevent format() KeyError
        skill_metadata = skill_metadata.replace('{', '{{').replace('}', '}}')

    # Detect current pipeline stage and inject only the relevant workflow hint.
    # This prevents all 3 stage workflows from being repeated on every API call.
    stage1_done = getattr(ctx.deps, 'stage1_result', None) is not None
    stage2_done = getattr(ctx.deps, 'stage2_result', None) is not None

    if stage2_done:
        stage_hint = STAGE3_HINT
    elif stage1_done:
        stage_hint = STAGE2_HINT
    else:
        stage_hint = STAGE1_HINT

    full_prompt = MAIN_SYSTEM_PROMPT.format(
        skill_metadata=skill_metadata,
        stage_hint=stage_hint,
    )

    # Inject evaluation-mode override — OVERRIDES any "wait for user" instructions
    if getattr(ctx.deps, 'evaluation_mode', False):
        full_prompt += (
            "\n\n"
            "## ⚡ EVALUATION MODE — ALL CONFIRMATIONS DISABLED ⚡\n"
            "No user is present. Proceed immediately through all stages without stopping:\n"
            "1. Call `submit_stage1_json` → on success, immediately call "
            "`run_skill_script_tool('placement_solver', 'solve_placement', <stage1_data>)`.\n"
            "2. After placement → immediately call `prepare_genesis_input()` then "
            "`fix_genesis_paths(result)`. Generate ZERO text between tool calls.\n"
            "3. Do NOT call `load_skill_tool`, `read_skill_file_tool`, or genesis build tools.\n"
        )

    logger.debug(
        f"\n{'='*80}\n🔧 SYSTEM PROMPT (stage={'3' if stage2_done else '2' if stage1_done else '1'})\n"
        f"Length: {len(full_prompt)} chars\n{'='*80}"
    )

    return full_prompt
