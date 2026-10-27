
import streamlit as st
import requests
from api import api_post


def _extract_answer(result):
    """Find an answer in common Flask response structures."""

    if isinstance(result, str):
        return result.strip() or None

    if not isinstance(result, dict):
        return None

    # Check direct answer fields first.
    answer_keys = (
        "answer",
        "response",
        "reply",
        "output",
        "text",
        "content",
    )

    for key in answer_keys:
        value = result.get(key)

        if isinstance(value, str) and value.strip():
            return value.strip()

        if isinstance(value, dict):
            nested = _extract_answer(value)
            if nested:
                return nested

    # Check common nested response containers.
    for key in ("data", "result", "knowledge"):
        value = result.get(key)

        if isinstance(value, dict):
            nested = _extract_answer(value)
            if nested:
                return nested

        elif isinstance(value, str) and value.strip():
            return value.strip()

    return None


def _extract_sources(result):
    """Extract source documents from common response structures."""

    if not isinstance(result, dict):
        return []

    knowledge = result.get("knowledge")

    if isinstance(knowledge, dict):
        sources = knowledge.get("sources")
        if isinstance(sources, list):
            return sources

    sources = result.get("sources", result.get("documents"))

    if isinstance(sources, list):
        return sources

    for key in ("data", "result"):
        nested = result.get(key)

        if isinstance(nested, dict):
            sources = _extract_sources(nested)
            if sources:
                return sources

    return []


def _format_sources(sources):
    """Create a readable, de-duplicated source list."""

    lines = []
    seen = set()

    for source in sources:
        if isinstance(source, str):
            name, page = source, None

        elif isinstance(source, dict):
            name = (
                source.get("source")
                or source.get("document")
                or source.get("filename")
                or source.get("file_name")
                or source.get("title")
                or "Unknown document"
            )

            page = (
                source.get("page")
                or source.get("page_number")
                or source.get("page_num")
            )

        else:
            continue

        key = (str(name).strip(), str(page))

        if key in seen:
            continue

        seen.add(key)

        label = str(name).strip()

        if page is not None:
            label += f" — page {page}"

        lines.append(f"- {label}")

    return lines


def _backend_error(result):
    """Return a useful error when the API reports a failure."""

    if not isinstance(result, dict):
        return None

    if result.get("error"):
        return str(
            result.get("details")
            or result.get("error")
        )

    if result.get("success") is False:
        return str(
            result.get("details")
            or result.get("message")
            or "The backend reported that the request failed."
        )

    return None


def _render_ai_agent_styles():
    st.markdown(
        """
        <style>
        /* Use the available screen width */
        .block-container {
            max-width: 100% !important;
            padding: 2rem 3rem !important;
        }

        /* Page header */
        .chat-page-header h1 {
            font-size: 2.7rem !important;
            line-height: 1.2 !important;
        }

        .chat-page-header p {
            font-size: 1.15rem !important;
            line-height: 1.8 !important;
        }

        /* Welcome section */
        .chat-welcome {
            padding: 2rem 1rem !important;
            text-align: center;
        }

        .chat-welcome h2 {
            font-size: 2rem !important;
        }

        .chat-welcome p {
            font-size: 1.1rem !important;
            line-height: 1.8 !important;
        }

        .suggestions-label {
            font-size: 0.9rem !important;
            font-weight: 700;
            letter-spacing: 0.1em;
            margin: 1rem 0;
        }

        /* Chat response text */
        [data-testid="stChatMessage"] {
            padding: 1.2rem 1.4rem !important;
            border-radius: 14px !important;
            margin-bottom: 1rem !important;
        }

        [data-testid="stChatMessage"] p,
        [data-testid="stChatMessage"] li {
            font-size: 18px !important;
            line-height: 1.85 !important;
        }

        [data-testid="stChatMessage"] h1,
        [data-testid="stChatMessage"] h2,
        [data-testid="stChatMessage"] h3,
        [data-testid="stChatMessage"] ul,
        [data-testid="stChatMessage"] ol,
        [data-testid="stChatMessage"] table {
            max-width: 100%;
        }

        [data-testid="stChatMessage"] table {
            width: 100%;
            border-collapse: collapse;
        }

        [data-testid="stChatMessage"] th,
        [data-testid="stChatMessage"] td {
            padding: 0.65rem;
            text-align: left;
        }

        [data-testid="stChatMessage"] h1 {
            font-size: 30px !important;
        }

        [data-testid="stChatMessage"] h2 {
            font-size: 26px !important;
        }

        [data-testid="stChatMessage"] h3 {
            font-size: 22px !important;
        }

        /* Buttons */
        .stButton button {
            min-height: 45px;
            font-size: 16px !important;
            border-radius: 9px !important;
        }

        /* Chat input */
        [data-testid="stChatInput"] textarea {
            font-size: 17px !important;
        }

        /* Mobile spacing */
        @media (max-width: 700px) {
            .block-container {
                padding: 1rem !important;
            }

            [data-testid="stChatMessage"] p,
            [data-testid="stChatMessage"] li {
                font-size: 16px !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

def send_question(question):
    """Send a question to Flask and save the conversation."""

    question = (question or "").strip()

    if not question:
        return

    # Clear the previous diagnostic message.
    st.session_state.ai_agent_error = None

    # Save the user's message.
    st.session_state.messages.append({
        "role": "user",
        "content": question,
    })

    # Keep recent questions for the sidebar.
    recent = st.session_state.recent_questions

    if question not in recent:
        recent.append(question)

    st.session_state.recent_questions = recent[-20:]

    try:
        with st.spinner("CommerceAI is thinking..."):
            result = api_post(
                "/api/agent/ask",
                {"question": question},
            )

        # Handle explicit backend errors.
        error = _backend_error(result)

        if error:
            st.session_state.ai_agent_error = error

            st.session_state.messages.append({
                "role": "assistant",
                "content": (
                    "I'm having trouble retrieving that information "
                    "right now. Please check the backend details below "
                    "and try again."
                ),
            })
            return

        if not isinstance(result, (dict, str)):
            st.session_state.ai_agent_error = (
                "Unexpected API response type: "
                f"{type(result).__name__}"
            )

            st.session_state.messages.append({
                "role": "assistant",
                "content": (
                    "I received an unexpected response from the "
                    "business intelligence service."
                ),
            })
            return

        answer = _extract_answer(result)

        if not answer:
            keys = (
                ", ".join(result.keys())
                if isinstance(result, dict)
                else "plain string response"
            )

            st.session_state.ai_agent_error = (
                "The API response did not contain a recognizable "
                f"answer. Response fields: {keys}"
            )

            answer = (
                "I couldn't find an answer in the service response. "
                "Please check the backend response format."
            )

        # Add source references to the same assistant message.
        sources = _format_sources(_extract_sources(result))

        if sources:
            answer += "\n\n---\n\n### 📚 Sources\n\n" + "\n".join(sources)

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
        })


    except requests.exceptions.ConnectionError as exc:
        st.session_state.ai_agent_error = (
            "Connection to the backend was interrupted. "
            "Check that Flask is running and inspect the backend terminal. "
            f"Details: {exc}"
        )

        st.session_state.messages.append({
            "role": "assistant",
            "content": (
                "I couldn't reach the business intelligence service. "
                "Please try again in a moment."
            ),
        })

    except Exception as exc:
        st.session_state.ai_agent_error = (
            f"{type(exc).__name__}: {exc}"
        )

        st.session_state.messages.append({
            "role": "assistant",
            "content": (
                "An unexpected error occurred while processing "
                "your question. Check the backend error details."
            ),
        })


def render_ai_agent():
    """Render the CommerceAI conversational interface."""

    _render_ai_agent_styles()

    defaults = {
        "messages": [],
        "recent_questions": [],
        "pending_question": None,
        "ai_agent_error": None,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    # Process questions selected from the shared sidebar.
    pending = st.session_state.pending_question

    if pending:
        st.session_state.pending_question = None
        send_question(pending)
        st.rerun()

    # Header.
    st.markdown(
        """
        <div class="chat-page-header">
            <div class="page-kicker">COMMERCEAI WORKSPACE</div>
            <h1>AI Business Agent</h1>
            <p>
                Your business assistant for sales, profitability,
                inventory, and company policies.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Show backend diagnostics when an error occurs.
    if st.session_state.ai_agent_error:
        with st.expander("Backend error details", expanded=True):
            st.code(str(st.session_state.ai_agent_error))

    # Welcome screen for an empty conversation.
    if not st.session_state.messages:
        st.markdown(
            """
            <div class="chat-welcome">
                <div class="chat-welcome-icon">✦</div>
                <h2>How can I help you today?</h2>
                <p>
                    Ask a question about your business or select
                    a suggestion to get started.
                </p>
            </div>
            <div class="suggestions-label">SUGGESTED QUESTIONS</div>
            """,
            unsafe_allow_html=True,
        )

        suggestions = [
            "What is our total revenue?",
            "Which products are most profitable?",
            "Which products have inventory risks?",
            "How can we improve profitability?",
        ]

        left, right = st.columns(2, gap="medium")

        for index, suggestion in enumerate(suggestions):
            target = left if index % 2 == 0 else right

            with target:
                if st.button(
                    suggestion,
                    key=f"ai_suggestion_{index}",
                    width="stretch",
                ):
                    send_question(suggestion)
                    st.rerun()

    # Render conversation exactly once.
    for message in st.session_state.messages:
        role = message.get("role", "assistant")
        content = message.get("content", "")

        if role not in ("user", "assistant"):
            role = "assistant"

        with st.chat_message(role):
            st.markdown(
                content,
                unsafe_allow_html=False,
    )

    # One chat input, at the bottom of the page.
    question = st.chat_input(
        "Message CommerceAI...",
        key="ai_chat_input",
    )

    if question:
        send_question(question)
        st.rerun()