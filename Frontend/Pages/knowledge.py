import streamlit as st
from pathlib import Path


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Knowledge | CommerceAI",
    page_icon="📚",
    layout="wide",
)


# ============================================================
# LOAD CSS
# ============================================================

def load_css():

    css_path = (
        Path(__file__).parent.parent
        / "assets"
        / "style.css"
    )

    if css_path.exists():

        with open(css_path, "r", encoding="utf-8") as file:

            st.markdown(
                f"<style>{file.read()}</style>",
                unsafe_allow_html=True
            )


load_css()


# ============================================================
# HEADER
# ============================================================

st.html(
    """
    <div class="page-header">

        <div>

            <div class="page-kicker">
                KNOWLEDGE INTELLIGENCE
            </div>

            <h1 class="page-title">
                Knowledge Center
            </h1>

            <p class="page-description">
                Search company policies, operational documents
                and business knowledge through AI-powered retrieval.
            </p>

        </div>

        <div class="page-header-icon">
            📚
        </div>

    </div>
    """
)


# ============================================================
# SEARCH HEADER
# ============================================================

st.html(
    """
    <div class="section-header">

        <div>

            <div class="section-kicker">
                AI KNOWLEDGE SEARCH
            </div>

            <div class="section-title">
                Search company knowledge
            </div>

            <div class="section-description-left">
                Ask about returns, cancellation, shipping,
                warranty and other company policies.
            </div>

        </div>

        <div class="ai-search-badge">
            AI SEARCH
        </div>

    </div>
    """
)


# ============================================================
# SEARCH
# ============================================================

question = st.text_input(
    "Search knowledge",
    placeholder=(
        "e.g. Can I cancel my order after it has been dispatched?"
    ),
    label_visibility="collapsed",
)


search_clicked = st.button(
    "Search knowledge",
    use_container_width=False,
)


# ============================================================
# QUICK QUESTIONS
# ============================================================

st.html(
    """
    <div class="quick-search-label">
        Popular searches
    </div>
    """
)


q1, q2, q3, q4 = st.columns(4)


quick_questions = [
    "Return policy",
    "Order cancellation",
    "Shipping policy",
    "Warranty policy",
]


for index, text in enumerate(quick_questions):

    columns = [q1, q2, q3, q4]

    with columns[index]:

        if st.button(
            text,
            key=f"quick_{index}",
            use_container_width=True,
        ):

            question = text
            search_clicked = True


# ============================================================
# SEARCH RESULT
# ============================================================

if search_clicked and question.strip():

    query = question.lower()

    if "return" in query:

        answer = (
            "The company knowledge base contains information "
            "about return eligibility, return conditions "
            "and applicable return procedures."
        )

        source = "Croma Cancellation & Returns Policy"

    elif "cancel" in query:

        answer = (
            "The company policy contains cancellation guidelines, "
            "including information related to cancellation "
            "requests after dispatch."
        )

        source = "Croma Cancellation & Returns Policy"

    elif "shipping" in query:

        answer = (
            "The knowledge base contains shipping and delivery "
            "guidelines covering order fulfilment and delivery."
        )

        source = "Croma Shipping Policy"

    elif "warranty" in query:

        answer = (
            "The knowledge base contains warranty information "
            "covering warranty eligibility, coverage and support."
        )

        source = "Croma Warranty Policy"

    else:

        answer = (
            "This question can be answered by the RAG knowledge "
            "retrieval system once the frontend is connected "
            "to the Flask agent."
        )

        source = "Company Knowledge Base"


    st.html(
        """
        <div class="section-header">

            <div>

                <div class="section-kicker">
                    AI RESPONSE
                </div>

                <div class="section-title">
                    Knowledge result
                </div>

            </div>

        </div>
        """
    )


    st.html(
        f"""
        <div class="knowledge-answer-card">

            <div class="answer-label">
                AI ANSWER
            </div>

            <div class="answer-content">
                {answer}
            </div>

            <div class="answer-source">

                <span>
                    Source
                </span>

                <strong>
                    {source}
                </strong>

            </div>

        </div>
        """
    )


# ============================================================
# CATEGORIES
# ============================================================

st.html(
    """
    <div class="section-header">

        <div>

            <div class="section-kicker">
                EXPLORE
            </div>

            <div class="section-title">
                Knowledge categories
            </div>

        </div>

        <div class="section-description">
            Browse the main knowledge areas available
            to the AI assistant.
        </div>

    </div>
    """
)


col1, col2, col3 = st.columns(3)


with col1:

    st.html(
        """
        <div class="knowledge-category-card">

            <div class="category-icon">
                ↩
            </div>

            <div class="category-title">
                Returns & Cancellations
            </div>

            <div class="category-description">
                Return eligibility, cancellation rules,
                refunds and customer policies.
            </div>

            <div class="category-footer">
                Return policies →
            </div>

        </div>
        """
    )


with col2:

    st.html(
        """
        <div class="knowledge-category-card">

            <div class="category-icon">
                🚚
            </div>

            <div class="category-title">
                Shipping & Delivery
            </div>

            <div class="category-description">
                Shipping policies, delivery guidelines,
                fulfilment and order movement.
            </div>

            <div class="category-footer">
                Shipping policies →
            </div>

        </div>
        """
    )


with col3:

    st.html(
        """
        <div class="knowledge-category-card">

            <div class="category-icon">
                🛡
            </div>

            <div class="category-title">
                Warranty & Support
            </div>

            <div class="category-description">
                Warranty coverage, eligibility,
                product support and service information.
            </div>

            <div class="category-footer">
                Warranty policies →
            </div>

        </div>
        """
    )


# ============================================================
# DOCUMENT LIBRARY
# ============================================================

st.html(
    """
    <div class="section-header">

        <div>

            <div class="section-kicker">
                DOCUMENT LIBRARY
            </div>

            <div class="section-title">
                Indexed knowledge
            </div>

        </div>

        <div class="document-count">
            9 documents
        </div>

    </div>
    """
)


documents = [
    ("Croma Cancellation & Returns Policy", "Returns & cancellations"),
    ("Croma FAQ", "General information"),
    ("Croma Privacy Policy", "Company policy"),
    ("Croma Shipping Policy", "Shipping & delivery"),
    ("Croma Terms & Conditions", "Legal & policy"),
    ("Croma Warranty Policy", "Warranty & support"),
    ("SAP Inventory Management", "Inventory operations"),
    ("SAP Reorder Management", "Inventory operations"),
    ("SAP Order Management", "Order operations"),
]


for document_name, category in documents:

    st.html(
        f"""
        <div class="document-card">

            <div class="document-left">

                <div class="document-icon">
                    📄
                </div>

                <div>

                    <div class="document-name">
                        {document_name}
                    </div>

                    <div class="document-category">
                        {category}
                    </div>

                </div>

            </div>

            <div class="document-status">
                <span class="indexed-dot"></span>
                Indexed
            </div>

        </div>
        """
    )


# ============================================================
# FOOTER
# ============================================================

st.html(
    """
    <div class="main-footer">

        CommerceAI
        <span>•</span>
        Knowledge Intelligence

    </div>
    """
)