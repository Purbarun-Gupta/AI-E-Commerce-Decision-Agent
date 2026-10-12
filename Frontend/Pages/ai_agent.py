
from pathlib import Path
import streamlit as st

st.set_page_config(
    page_title="AI Agent | CommerceAI",
    page_icon="💬",
    layout="wide",
)

BASE_DIR = Path(__file__).resolve().parent.parent
CSS_PATH = BASE_DIR / "assets" / "style.css"

if CSS_PATH.exists():
    st.markdown(
        f"<style>{CSS_PATH.read_text(encoding='utf-8')}</style>",
        unsafe_allow_html=True,
    )

if "messages" not in st.session_state:
    st.session_state.messages = []
if "recent_questions" not in st.session_state:
    st.session_state.recent_questions = []
if "pending_question" not in st.session_state:
    st.session_state.pending_question = None


def demo_answer(question):
    q = question.lower()

    if "revenue" in q or "sales" in q:
        return (
            "I can help analyze revenue and sales performance. "
            "Connect your business database to calculate actual totals, "
            "compare periods, and identify the strongest sales drivers."
        )
    if "inventory" in q or "stock" in q or "reorder" in q:
        return (
            "Inventory analysis can identify low-stock products, "
            "compare stock against reorder thresholds, and suggest "
            "replenishment quantities. Connect your inventory database "
            "to use live figures."
        )
    if "profit" in q or "profitable" in q or "margin" in q:
        return (
            "Profitability analysis should compare sales revenue with "
            "product costs and margins. Connect your sales and cost data "
            "to rank products using actual profit figures."
        )
    if "policy" in q or "cancel" in q or "warranty" in q:
        return (
            "Use the Knowledge Assistant page to search the sample policy "
            "library. For verified answers, connect your document retrieval "
            "pipeline to the indexed source documents."
        )

    return (
        "I have received your question. This is the local demo mode, "
        "so no live database or document retrieval is being called yet. "
        "Connect your AI backend to return data-backed business answers."
    )


def send_question(question):
    question = (question or "").strip()
    if not question:
        return

    st.session_state.messages.append(
        {"role": "user", "content": question}
    )

    if question not in st.session_state.recent_questions:
        st.session_state.recent_questions.append(question)

    # Demo response only: deliberately no Flask request.
    answer = demo_answer(question)
    st.session_state.messages.append(
        {"role": "assistant", "content": answer}
    )


# Recent questions at the bottom of the shared sidebar.
with st.sidebar:
    st.markdown("---")
    st.markdown("#### Recent chats")

    if st.button(
        "＋ New chat",
        key="ai_new_chat",
        use_container_width=True,
    ):
        st.session_state.messages = []
        st.session_state.pending_question = None
        st.rerun()

    recent = list(dict.fromkeys(reversed(st.session_state.recent_questions)))[:8]

    if recent:
        for i, item in enumerate(recent):
            label = item if len(item) <= 35 else item[:32] + "..."
            if st.button(
                label,
                key=f"recent_{i}",
                help=item,
                use_container_width=True,
            ):
                st.session_state.pending_question = item
                st.rerun()
    else:
        st.caption("Your questions will appear here.")

if st.session_state.pending_question:
    selected = st.session_state.pending_question
    st.session_state.pending_question = None
    send_question(selected)

st.markdown(
    """
    <div class="chat-page-header">
        <div>
            <div class="page-kicker">COMMERCEAI WORKSPACE</div>
            <h1>AI Business Agent</h1>
            <p>
                Ask about sales, profitability, inventory, or company policies.
            </p>
        </div>
        <div class="demo-pill">Demo mode</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Scrollable conversation area.
chat_area = st.container()

with chat_area:
    if not st.session_state.messages:
        st.markdown(
            """
            <div class="chat-welcome">
                <div class="chat-welcome-icon">✦</div>
                <h2>What would you like to know?</h2>
                <p>
                    Ask a business question or start with one of these suggestions.
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
        for i, prompt in enumerate(suggestions):
            target = left if i % 2 == 0 else right
            with target:
                if st.button(
                    prompt,
                    key=f"suggestion_{i}",
                    use_container_width=True,
                ):
                    send_question(prompt)
                    st.rerun()
    else:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

question = st.chat_input(
    "Message CommerceAI...",
    key="ai_chat_input",
)

if question:
    send_question(question)
    st.rerun()
