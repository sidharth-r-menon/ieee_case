"""Command-line interface for Robot Workcell Design Agent."""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt

from src_old.agent import workcell_agent
from src.dependencies import AgentDependencies

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

console = Console()


async def run_agent(user_input: str, deps: AgentDependencies) -> str:
    """
    Run the workcell agent with user input.

    Args:
        user_input: User's question or request
        deps: Agent dependencies

    Returns:
        Agent's response
    """
    try:
        result = await workcell_agent.run(user_input, deps=deps)
        return result.data
    except Exception as e:
        logger.exception(f"agent_error: {str(e)}")
        return f"Error: {str(e)}"


async def interactive_mode():
    """Run the agent in interactive mode."""
    console.print(
        Panel(
            "[bold blue]Robot Workcell Design Agent[/bold blue]\n\n"
            "This agent helps you design robotic workcells using a 3-stage pipeline:\n"
            "• Stage 1: Interpretation & Analysis\n"
            "• Stage 2: Spatial Optimization\n"
            "• Stage 3: Validation\n\n"
            "Type 'exit' or 'quit' to end the session.",
            style="blue",
        )
    )

    # Initialize dependencies
    deps = AgentDependencies()
    await deps.initialize()

    console.print(
        f"\n[bold green]✓[/bold green] Agent initialized with "
        f"{len(deps.skill_loader.skills)} skills\n"
    )

    # Show available skills
    console.print("[bold]Available Skills:[/bold]")
    for skill_name in sorted(deps.skill_loader.skills.keys()):
        skill = deps.skill_loader.skills[skill_name]
        stage_info = f" [Stage {skill.stage}]" if skill.stage else ""
        console.print(f"  • {skill_name}{stage_info}: {skill.description}")
    console.print()

    # Interactive loop
    while True:
        try:
            # Get user input
            user_input = Prompt.ask("\n[bold cyan]You[/bold cyan]")

            if user_input.lower() in ["exit", "quit"]:
                console.print("[bold yellow]Goodbye![/bold yellow]")
                break

            if not user_input.strip():
                continue

            # Show thinking indicator
            console.print("\n[bold magenta]Agent[/bold magenta] (thinking...)")

            # Run agent
            response = await run_agent(user_input, deps)

            # Display response
            console.print(f"\n[bold magenta]Agent[/bold magenta]:")
            console.print(Markdown(response))

        except KeyboardInterrupt:
            console.print("\n[bold yellow]Interrupted. Goodbye![/bold yellow]")
            break
        except Exception as e:
            console.print(f"\n[bold red]Error:[/bold red] {str(e)}")
            logger.exception("interactive_mode_error")


async def single_query_mode(query: str):
    """
    Run the agent with a single query.

    Args:
        query: User's question or request
    """
    console.print(
        Panel(
            "[bold blue]Robot Workcell Design Agent[/bold blue]\n\n"
            "Processing your request...",
            style="blue",
        )
    )

    # Initialize dependencies
    deps = AgentDependencies()
    await deps.initialize()

    console.print(
        f"\n[bold green]✓[/bold green] Agent initialized with "
        f"{len(deps.skill_loader.skills)} skills\n"
    )

    # Run agent
    console.print(f"[bold cyan]Query:[/bold cyan] {query}\n")
    response = await run_agent(query, deps)

    # Display response
    console.print(f"[bold magenta]Response:[/bold magenta]")
    console.print(Markdown(response))


def main():
    """Main entry point for CLI."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Robot Workcell Design Agent - AI-powered workcell design assistant"
    )
    parser.add_argument(
        "query",
        nargs="?",
        help="Single query to process (optional, omit for interactive mode)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging",
    )

    args = parser.parse_args()

    # Configure logging level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    # Run in appropriate mode
    if args.query:
        asyncio.run(single_query_mode(args.query))
    else:
        asyncio.run(interactive_mode())


if __name__ == "__main__":
    main()
