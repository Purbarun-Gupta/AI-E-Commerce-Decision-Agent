import streamlit as st
from pathlib import Path

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="CommerceAI",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# LOAD CSS
# ============================================================

css_path = Path(__file__).parent / "assets" / "style.css"

if css_path.exists():
    css = css_path.read_text(encoding="utf-8")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
else:
    st.warning(f"CSS file not found: {css_path}")

# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "recent_questions" not in st.session_state:
    st.session_state.recent_questions = []

if "pending_question" not in st.session_state:
    st.session_state.pending_question = None


def submit_question(question):
    """Demo response handler. Connect the Flask agent here later."""
    question = question.strip()

    if not question:
        return

    st.session_state.messages.append({
        "role": "user",
        "content": question,
    })

    if question not in st.session_state.recent_questions:
        st.session_state.recent_questions.append(question)

    # Placeholder response until the Flask agent is connected.
    response = (
        "Your question has been received. The AI backend can be connected "
        "here to provide answers from your business database and knowledge base."
    )

    st.session_state.messages.append({
        "role": "assistant",
        "content": response,
    })


# ============================================================
# SIDEBAR — SIMPLE AND COMPACT
# ============================================================

with st.sidebar:

    if st.button(
        "＋  New conversation",
        key="new_conversation",
        use_container_width=True,
    ):
        st.session_state.messages = []
        st.session_state.pending_question = None
        st.rerun()

    st.markdown(
        '<div class="sidebar-section-title">RECENT QUESTIONS</div>',
        unsafe_allow_html=True,
    )

    recent_questions = list(
        dict.fromkeys(reversed(st.session_state.recent_questions))
    )[:6]

    if recent_questions:
        for index, recent in enumerate(recent_questions):
            label = recent if len(recent) <= 32 else recent[:29] + "..."

            if st.button(
                label,
                key=f"recent_question_{index}",
                use_container_width=True,
                help=recent,
            ):
                st.session_state.pending_question = recent
                st.rerun()
    else:
        st.markdown(
            '<div class="sidebar-empty">'
            'Your recent questions will appear here.'
            '</div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        """
        <div class="sidebar-footer">
            <span class="sidebar-status-dot"></span>
            <span>Decision assistant</span>
            <span class="sidebar-version">v1.0</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("""
        <div class="sidebar-logo">
            <div class="logo-icon">✦</div>
            <div>
                <div class="logo-title">Commerce_Ai</div>
                <div class="logo-subtitle">INTELLIGENT COMMERCE</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    


# ============================================================
# HANDLE SELECTED RECENT QUESTION
# ============================================================

if st.session_state.pending_question:
    selected_question = st.session_state.pending_question
    st.session_state.pending_question = None
    submit_question(selected_question)
    st.rerun()


# ============================================================
# WELCOME SCREEN OR CONVERSATION
# ============================================================

if not st.session_state.messages:

    st.markdown(
        """
        <div class="welcome-container">
            <div class="welcome-icon">✦</div>
            <h1>How can I help you today?</h1>
            <p>
                Ask about sales, inventory, product performance or company policies.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="suggestions-title">SUGGESTED QUESTIONS</div>',
        unsafe_allow_html=True,
    )

    left_col, right_col = st.columns(2, gap="small")

    with left_col:
        if st.button(
            "↗  What is our total revenue?",
            key="suggestion_revenue",
            use_container_width=True,
        ):
            submit_question("What is our total revenue?")
            st.rerun()

        if st.button(
            "↗  Which products have inventory risk?",
            key="suggestion_inventory",
            use_container_width=True,
        ):
            submit_question("Which products have inventory risk?")
            st.rerun()

    with right_col:
        if st.button(
            "↗  Which products are performing best?",
            key="suggestion_products",
            use_container_width=True,
        ):
            submit_question("Which products are performing best?")
            st.rerun()

        if st.button(
            "↗  Can I cancel a dispatched order?",
            key="suggestion_policy",
            use_container_width=True,
        ):
            submit_question(
                "Can I cancel an order after it has been dispatched?"
            )
            st.rerun()

else:

    st.markdown(
        '<div class="conversation-label">Conversation</div>',
        unsafe_allow_html=True,
    )

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


# ============================================================
# CHAT INPUT
# ============================================================

question = st.chat_input(
    "Message your business assistant...",
    key="main_chat_input",
)

if question:
    submit_question(question)
    st.rerun()