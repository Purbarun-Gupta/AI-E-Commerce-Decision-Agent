import streamlit as st
from pathlib import Path


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="CommerceAI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# LOAD CSS
# ============================================================

def load_css():
    css_path = Path(__file__).parent / "assets" / "style.css"

    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as file:
            css = file.read()

        st.markdown(
            f"<style>{css}</style>",
            unsafe_allow_html=True
        )
    else:
        st.warning(
            f"style.css was not found at: {css_path}"
        )


load_css()


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "recent_questions" not in st.session_state:
    st.session_state.recent_questions = []


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.html(
        """
        <div class="sidebar-brand">

            <div class="brand-icon">
                ✦
            </div>

            <div>
                <div class="brand-title">
                    CommerceAI
                </div>

                <div class="brand-subtitle">
                    Decision Intelligence
                </div>
            </div>

        </div>
        """
    )

    st.divider()

    st.html(
        """
        <div class="sidebar-section-title">
            WORKSPACE
        </div>
        """
    )

    st.html(
        """
        <div class="sidebar-info-card">

            <div class="sidebar-info-icon">
                ◈
            </div>

            <div>
                <div class="sidebar-info-title">
                    AI Decision Assistant
                </div>

                <div class="sidebar-info-text">
                    Ask questions about sales,
                    inventory, products and policies.
                </div>
            </div>

        </div>
        """
    )

    st.divider()

    if st.button(
        "＋  New Conversation",
        use_container_width=True
    ):
        st.session_state.messages = []
        st.rerun()

    st.html(
        """
        <div class="sidebar-section-title">
            RECENT QUESTIONS
        </div>
        """
    )

    if st.session_state.recent_questions:

        for question in st.session_state.recent_questions[-5:]:
            st.caption(question)

    else:

        st.caption(
            "Your recent questions will appear here."
        )

    st.divider()

    st.html(
        """
        <div class="sidebar-footer">

            <div class="sidebar-footer-title">
                CommerceAI
            </div>

            <div class="sidebar-footer-text">
                AI-powered e-commerce decision intelligence
            </div>

            <div class="sidebar-version">
                Version 1.0
            </div>

        </div>
        """
    )


# ============================================================
# MAIN HERO
# ============================================================

st.html(
    """
    <div class="hero-container">

        <div class="hero-eyebrow">
            AI DECISION ASSISTANT
        </div>

        <h1 class="hero-title">
            Ask your business anything.
        </h1>

        <p class="hero-description">
            Get intelligent answers about sales, inventory,
            products, profitability and company policies.
        </p>

        <div class="ai-status">
            <span class="status-dot"></span>
            AI Assistant Ready
        </div>

    </div>
    """
)


# ============================================================
# HERO BADGE
# ============================================================

st.html(
    """
    <div class="hero-badge">
        ✦ Intelligent Business Analysis
    </div>
    """
)


# ============================================================
# FEATURE CARDS
# ============================================================

col1, col2, col3 = st.columns(3)

with col1:

    st.html(
        """
        <div class="feature-card">

            <div class="feature-icon">
                ◈
            </div>

            <div class="feature-title">
                Business Analytics
            </div>

            <div class="feature-description">
                Understand revenue, orders,
                profitability and sales trends.
            </div>

        </div>
        """
    )


with col2:

    st.html(
        """
        <div class="feature-card">

            <div class="feature-icon">
                ◇
            </div>

            <div class="feature-title">
                Inventory Intelligence
            </div>

            <div class="feature-description">
                Identify low-stock products,
                inventory risks and reorder opportunities.
            </div>

        </div>
        """
    )


with col3:

    st.html(
        """
        <div class="feature-card">

            <div class="feature-icon">
                ✦
            </div>

            <div class="feature-title">
                Company Knowledge
            </div>

            <div class="feature-description">
                Search policies, shipping,
                returns, warranty and operational documents.
            </div>

        </div>
        """
    )


# ============================================================
# SUGGESTED QUESTIONS
# ============================================================

st.html(
    """
    <div class="suggestions-header">
        <div class="suggestions-title">
            Try asking
        </div>

        <div class="suggestions-subtitle">
            Explore your business with natural language
        </div>
    </div>
    """
)


suggestions = [
    "What is our total revenue?",
    "Which products are performing best?",
    "Which products have inventory risk?",
    "Can I cancel an order after it has been dispatched?",
]


suggestion_cols = st.columns(2)

for index, question in enumerate(suggestions):

    with suggestion_cols[index % 2]:

        if st.button(
            question,
            key=f"suggestion_{index}",
            use_container_width=True,
        ):

            st.session_state.messages.append(
                {
                    "role": "user",
                    "content": question,
                }
            )

            st.session_state.recent_questions.append(
                question
            )

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": (
                        "Your AI assistant is ready. "
                        "The backend agent can be connected "
                        "to this interface next."
                    ),
                }
            )

            st.rerun()


# ============================================================
# CHAT HISTORY
# ============================================================

if st.session_state.messages:

    st.html(
        """
        <div class="chat-section-title">
            Conversation
        </div>
        """
    )

    for message in st.session_state.messages:

        if message["role"] == "user":

            st.chat_message("user").write(
                message["content"]
            )

        else:

            st.chat_message("assistant").write(
                message["content"]
            )


# ============================================================
# CHAT INPUT
# ============================================================

question = st.chat_input(
    "Ask anything about your e-commerce business..."
)


if question:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    st.session_state.recent_questions.append(
        question
    )

    response = (
        "Your question has been received. "
        "The Flask AI agent can be connected here "
        "to provide database and RAG-powered answers."
    )

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response,
        }
    )

    st.rerun()


# ============================================================
# FOOTER
# ============================================================

st.html(
    """
    <div class="main-footer">

        <div>
            CommerceAI
        </div>

        <div>
            AI-powered e-commerce decision intelligence
        </div>

    </div>
    """
)