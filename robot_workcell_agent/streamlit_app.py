"""
Streamlit Chat UI for the Robot Workcell Design Agent.

Run:
    cd robot_workcell_agent
    streamlit run streamlit_app.py
"""

import asyncio
import logging
import uuid
from pathlib import Path
import json

import streamlit as st

# ── Must be the FIRST Streamlit call ─────────────────────────────
st.set_page_config(
    page_title="Robot Workcell Design Agent",
    page_icon="🤖",
    layout="wide",
)

# ── Enhanced Logging ──────────────────────────────────────────────
from src.logging_config import setup_logging, log_workflow_step

# Setup comprehensive logging
LOG_FILE = setup_logging(level="DEBUG", enable_debug=True)
logger = logging.getLogger(__name__)

logger.info("Streamlit app started")


# ── Helpers ──────────────────────────────────────────────────────

def _get_event_loop() -> asyncio.AbstractEventLoop:
    """Return (or create) a reusable event-loop for async agent calls."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            raise RuntimeError
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop


def _run_async(coro):
    """Run an async coroutine from synchronous Streamlit code."""
    loop = _get_event_loop()
    return loop.run_until_complete(coro)


# ── Lazy-import agent pieces (only once) ────────────────────────

@st.cache_resource(show_spinner="Loading agent …")
def _load_agent():
    """Import and return (workcell_agent, AgentDependencies class)."""
    from src.agent import workcell_agent
    from src.dependencies import AgentDependencies
    return workcell_agent, AgentDependencies


# ── Session-state bootstrap ─────────────────────────────────────

def _init_session():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "deps" not in st.session_state:
        _, AgentDependencies = _load_agent()
        deps = AgentDependencies(session_id=str(uuid.uuid4()))
        _run_async(deps.initialize())
        st.session_state.deps = deps
        logger.info(
            "session_init: skills=%d  session=%s",
            len(deps.skill_loader.skills),
            deps.session_id,
        )
    if "stage_status" not in st.session_state:
        st.session_state.stage_status = {}


# ── Sidebar ──────────────────────────────────────────────────────

def _render_sidebar():
    with st.sidebar:
        st.header("Pipeline Status")
        deps = st.session_state.deps
        stage = deps.current_stage or "not_started"

        # Stage indicators
        stages = [
            ("Stage 1 — Requirements", "1"),
            ("Stage 2 — Placement", "2"),
            ("Stage 3 — Simulation", "3"),
        ]
        for label, s_id in stages:
            if stage.startswith(s_id):
                if "complete" in stage:
                    st.markdown(f"✅  **{label}**")
                else:
                    st.markdown(f"🔄  **{label}**")
            elif stage > s_id or "complete" in stage:
                st.markdown(f"✅  **{label}**")
            else:
                st.markdown(f"⬜  **{label}**")

        # ── Requirements Schema (live view) ─────────────────────
        st.divider()
        st.subheader("Collected Requirements")
        reqs = deps.design_context.get("requirements")
        if reqs:
            # Key fields
            task = reqs.get("task_type", "—")
            st.markdown(f"**Task:** {task}")

            objs = reqs.get("objects", [])
            if objs:
                for obj in objs:
                    name = obj.get("name", "?")
                    dims = obj.get("dimensions_m")
                    wt = obj.get("weight_kg")
                    qty = obj.get("quantity", "?")
                    d_str = f"{[round(x*100,1) for x in dims]} cm" if dims else "?"
                    w_str = f"{wt} kg" if wt else "?"
                    st.markdown(f"- **{name}** x{qty} — {d_str}, {w_str}")
            else:
                st.caption("_No objects yet_")

            robot = deps.design_context.get("selected_robot")
            if robot:
                st.markdown(f"**Robot:** {robot.get('model_id', '?')} "
                            f"({robot.get('max_payload_kg', '?')}kg payload, "
                            f"{robot.get('max_reach_m', '?')}m reach)")
            else:
                st.caption("_Robot not yet selected_")

            ws = reqs.get("workspace", {})
            tw = ws.get("table_width_m")
            td = ws.get("table_depth_m")
            if tw and td:
                st.markdown(f"**Table:** {tw}m x {td}m")

            # Full JSON in expander
            with st.expander("Full Requirements JSON", expanded=False):
                st.json(reqs)
        else:
            st.caption("_No data yet — start a conversation._")

        # ── Design context (other keys) ─────────────────────────
        st.divider()
        st.subheader("Design Context")
        ctx = deps.design_context
        hidden_keys = {"requirements", "genesis_engine", "spawn_tools"}
        shown = {k: v for k, v in ctx.items() if k not in hidden_keys}
        if shown:
            for k, v in shown.items():
                with st.expander(k, expanded=False):
                    if isinstance(v, (dict, list)):
                        st.json(v)
                    else:
                        st.text(str(v))
        else:
            st.caption("_No additional context yet._")

        st.divider()
        if st.button("🔄 Reset Session", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()


# ── Main chat area ───────────────────────────────────────────────

def _render_chat():
    st.title("🤖 Robot Workcell Design Agent")
    st.caption(
        "Describe the robotic workcell you need in plain English. "
        "The agent will interpret, optimise, simulate, and validate the design."
    )
    
    # Show log file location
    st.info(f"📝 Detailed logs are being saved to: `{LOG_FILE}`")

    # Replay chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input
    if prompt := st.chat_input("e.g. I need a pick-and-place cell for sorting 3 types of fruit …"):
        # Show user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Run agent
        with st.chat_message("assistant"):
            with st.spinner("Thinking …"):
                reply = _run_agent(prompt)
            st.markdown(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})

        # Sidebar refreshes automatically on rerun


def _run_agent(user_input: str) -> str:
    """Invoke the Pydantic-AI agent and return the response text."""
    from src.logging_config import log_llm_interaction, log_workflow_step
    
    agent, _ = _load_agent()
    deps = st.session_state.deps
    
    # Log this interaction
    log_workflow_step(f"User input", user_input)

    # Build message history for multi-turn
    from pydantic_ai.messages import ModelRequest, ModelResponse, TextPart, UserPromptPart
    message_history = []
    for msg in st.session_state.messages[:-1]:  # exclude current user msg
        if msg["role"] == "user":
            message_history.append(
                ModelRequest(parts=[UserPromptPart(content=msg["content"])])
            )
        else:
            message_history.append(
                ModelResponse(parts=[TextPart(content=msg["content"])])
            )

    try:
        logger.debug(f"Calling agent with {len(message_history)} previous messages")
        result = _run_async(
            agent.run(
                user_input,
                deps=deps,
                message_history=message_history if message_history else None,
            )
        )
        
        # Log the response
        response_text = result.output
        log_llm_interaction(user_input, response_text)
        logger.info(f"Agent response length: {len(response_text)} chars")
        
        # Check if this looks like Stage 1 JSON
        if "stage_1_complete" in response_text.lower() or "```json" in response_text:
            logger.info("🎯 Detected possible Stage 1 JSON output in response")
            
        return response_text
    except Exception as exc:
        logger.exception("agent_run_error")
        return f"⚠️ Agent error: {exc}"



# ── Entrypoint ───────────────────────────────────────────────────

def main():
    _init_session()
    _render_sidebar()
    _render_chat()


if __name__ == "__main__":
    main()
else:
    # Streamlit executes the module top-level
    main()
