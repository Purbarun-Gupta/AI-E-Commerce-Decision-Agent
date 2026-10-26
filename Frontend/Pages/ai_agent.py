
import streamlit as st
from api import api_post


def send_question(question):
    """Send a question to the Flask AI agent and save the response."""
    question = (question or "").strip()

    if not question:
        return

    # Save the user's message.
    st.session_state.messages.append({
        "role": "user",
        "content": question,
    })

    # Save the question in recent history.
    recent = st.session_state.recent_questions

    if question not in recent:
        recent.append(question)

    st.session_state.recent_questions = recent[-20:]

    # Call the existing Flask backend.
    try:
        with st.spinner("Analyzing your business data..."):
            result = api_post(
                "/api/agent/ask",
                {"question": question},
            )

        if not isinstance(result, dict) or "error" in result:
            error_details = result

            if isinstance(result, dict):
                error_details = result.get(
                    "details",
                    result.get("error", "Unknown backend error"),
                )

            st.session_state.ai_agent_error = error_details

            st.session_state.messages.append({
                "role": "assistant",
                "content": (
                    "I couldn't retrieve an answer. "
                    "Please check the backend error details above."
                ),
            })
            return

        answer = result.get(
            "answer",
            "The backend returned no answer.",
        )

        # Show the route selected by the backend, if available.
        route = result.get("route")
        if route:
            answer = f"**Route: {route}**\n\n{answer}"

        # Include RAG sources when the backend returns them.
        knowledge = result.get("knowledge")

        if isinstance(knowledge, dict):
            sources = knowledge.get("sources", [])

            if sources:
                answer += "\n\n**Sources:**\n"

                for source in sources:
                    if isinstance(source, dict):
                        name = source.get(
                            "source",
                            "Unknown document",
                        )
                        page = source.get("page", "Unknown")
                        answer += f"\n- {name} — page {page}"

        st.session_state.messages.append({
            "role": "assistant",
            "content": str(answer),
        })

    except Exception as exc:
        st.session_state.messages.append({
            "role": "assistant",
            "content": (
                "The request to the AI backend failed. "
                "Check your Flask server and API configuration."
            ),
        })
        st.session_state.ai_agent_error = str(exc)


def render_ai_agent():
    """Render the AI Agent page."""

    # Initialize shared state without overwriting existing conversations.
    defaults = {
        "messages": [],
        "recent_questions": [],
        "pending_question": None,
        "ai_agent_error": None,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    # Handle a question selected from the shared sidebar.
    pending = st.session_state.pending_question

    if pending:
        st.session_state.pending_question = None
        send_question(pending)
        st.rerun()

    st.markdown(
        """
        <div class="chat-page-header">
            <div>
                <div class="page-kicker">COMMERCEAI WORKSPACE</div>
                <h1>AI Business Agent</h1>
                <p>
                    Ask about sales, profitability, inventory,
                    or company policies.
                </p>
            </div>
            <div class="demo-pill">AI Agent</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Display any backend error details for debugging.
    error = st.session_state.ai_agent_error

    if error:
        with st.expander("Backend error details"):
            st.write(error)

        st.session_state.ai_agent_error = None

    # Empty conversation: show welcome screen and suggestions.
    if not st.session_state.messages:
        st.markdown(
            """
            <div class="chat-welcome">
                <div class="chat-welcome-icon">✦</div>
                <h2>What would you like to know?</h2>
                <p>
                    Ask a business question or start with
                    one of these suggestions.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        suggestions = [
            "What is our total revenue?",
            "Which products are most profitable?",
            "Which products have inventory risks?",
            "How can we improve profitability?",
        ]

        left, right = st.columns(2, gap="small")

        for i, suggestion in enumerate(suggestions):
            target = left if i % 2 == 0 else right

            with target:
                if st.button(
                    suggestion,
                    key=f"ai_suggestion_{i}",
                    use_container_width=True,
                ):
                    send_question(suggestion)
                    st.rerun()

    # Display conversation history.
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input.
    question = st.chat_input(
        "Message CommerceAI...",
        key="ai_chat_input",
    )

    if question:
        send_question(question)
        st.rerun()
