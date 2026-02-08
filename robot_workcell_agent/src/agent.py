"""Main robot workcell design agent implementation with progressive disclosure."""

import logging
from pydantic_ai import Agent, RunContext
from pydantic import BaseModel

from src.providers import get_llm_model
from src.dependencies import AgentDependencies
from src.prompts import MAIN_SYSTEM_PROMPT
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


# Create the robot workcell design agent
workcell_agent = Agent(
    get_llm_model(),
    deps_type=AgentDependencies,
    system_prompt="",  # Dynamically generated with skill metadata
    toolsets=[skill_tools],  # Skills + runtime executor (run_skill_script_tool)
)


@workcell_agent.system_prompt
async def get_system_prompt(ctx: RunContext[AgentDependencies]) -> str:
    """
    Generate system prompt with skill metadata.

    This dynamically injects skill metadata into the system prompt,
    implementing Level 1 of progressive disclosure.
    """
    await ctx.deps.initialize()

    skill_metadata = ""
    if ctx.deps.skill_loader:
        skill_metadata = ctx.deps.skill_loader.get_skill_metadata_prompt()

    return MAIN_SYSTEM_PROMPT.format(skill_metadata=skill_metadata)
