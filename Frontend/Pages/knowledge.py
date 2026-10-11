
import streamlit as st
import pandas as pd
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
        css = css_path.read_text(encoding="utf-8")
        st.markdown(
            f"<style>{css}</style>",
            unsafe_allow_html=True,
        )


load_css()


# ============================================================
# KNOWLEDGE DATA
# ============================================================

documents = [
    {
        "Document": "Croma Cancellation & Returns Policy",
        "Category": "Returns & Cancellations",
        "Type": "Policy",
        "Status": "Indexed",
    },
    {
        "Document": "Croma FAQ",
        "Category": "General Information",
        "Type": "FAQ",
        "Status": "Indexed",
    },
    {
        "Document": "Croma Privacy Policy",
        "Category": "Company Policy",
        "Type": "Policy",
        "Status": "Indexed",
    },
    {
        "Document": "Croma Shipping Policy",
        "Category": "Shipping & Delivery",
        "Type": "Policy",
        "Status": "Indexed",
    },
    {
        "Document": "Croma Terms & Conditions",
        "Category": "Legal & Policy",
        "Type": "Legal",
        "Status": "Indexed",
    },
    {
        "Document": "Croma Warranty Policy",
        "Category": "Warranty & Support",
        "Type": "Policy",
        "Status": "Indexed",
    },
    {
        "Document": "SAP Inventory Management",
        "Category": "Inventory Operations",
        "Type": "Operations",
        "Status": "Indexed",
    },
    {
        "Document": "SAP Reorder Management",
        "Category": "Inventory Operations",
        "Type": "Operations",
        "Status": "Indexed",
    },
    {
        "Document": "SAP Order Management",
        "Category": "Order Operations",
        "Type": "Operations",
        "Status": "Indexed",
    },
]

df = pd.DataFrame(documents)


# ============================================================
# PAGE HEADER
# ============================================================

st.markdown(
    """
    <div class="knowledge-page-header">
        <div>
            <div class="knowledge-eyebrow">
                KNOWLEDGE INTELLIGENCE
            </div>
            <h1>Knowledge Center</h1>
            <p>
                Find company policies, operational documents,
                and business information in one place.
            </p>
        </div>
        <div class="knowledge-header-icon">📚</div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# KNOWLEDGE OVERVIEW
# ============================================================

st.markdown(
    """
    <div class="knowledge-stats">
        <div class="knowledge-stat">
            <div class="stat-label">TOTAL DOCUMENTS</div>
            <div class="stat-value">9</div>
            <div class="stat-note">Available in the library</div>
        </div>
        <div class="knowledge-stat">
            <div class="stat-label">KNOWLEDGE AREAS</div>
            <div class="stat-value">6+</div>
            <div class="stat-note">Policies and operations</div>
        </div>
        <div class="knowledge-stat">
            <div class="stat-label">INDEXING STATUS</div>
            <div class="stat-value">Ready</div>
            <div class="stat-note">Sample document status</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SEARCH SECTION
# ============================================================

st.markdown(
    """
    <div class="knowledge-section-heading">
        <div class="knowledge-eyebrow">AI KNOWLEDGE SEARCH</div>
        <h2>What would you like to know?</h2>
        <p>
            Search policies and operational information using
            a question or a keyword.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# Keep the search query in session state so quick searches work
if "knowledge_query" not in st.session_state:
    st.session_state.knowledge_query = ""

if "knowledge_submitted" not in st.session_state:
    st.session_state.knowledge_submitted = False


def select_question(question):
    st.session_state.knowledge_query = question
    st.session_state.knowledge_submitted = True


with st.form("knowledge_search_form"):
    question = st.text_input(
        "Search company knowledge",
        key="knowledge_query",
        placeholder=(
            "e.g. Can I cancel my order after dispatch?"
        ),
        label_visibility="collapsed",
    )

    search_col, hint_col = st.columns([1, 3])

    with search_col:
        search_clicked = st.form_submit_button(
            "⌕  Search knowledge",
            use_container_width=True,
        )

    with hint_col:
        st.markdown(
            '<div class="search-hint">'
            'Search returns, cancellation, shipping, warranty '
            'and other topics.'
            '</div>',
            unsafe_allow_html=True,
        )


st.markdown(
    '<div class="popular-search-label">POPULAR SEARCHES</div>',
    unsafe_allow_html=True,
)

quick_cols = st.columns(4)

quick_questions = [
    "Return policy",
    "Order cancellation",
    "Shipping policy",
    "Warranty policy",
]

for index, quick_question in enumerate(quick_questions):
    with quick_cols[index]:
        st.button(
            quick_question,
            key=f"knowledge_quick_{index}",
            use_container_width=True,
            on_click=select_question,
            args=(quick_question,),
        )


# ============================================================
# SEARCH RESULT
# ============================================================

if search_clicked:
    st.session_state.knowledge_submitted = True

if st.session_state.knowledge_submitted:
    query = st.session_state.knowledge_query.strip().lower()

    if query:
        if "return" in query or "refund" in query:
            answer = (
                "The document library includes the Croma "
                "Cancellation & Returns Policy. Refer to the "
                "official document for return eligibility, "
                "conditions, and refund procedures."
            )
            source = "Croma Cancellation & Returns Policy"

        elif "cancel" in query:
            answer = (
                "The document library includes cancellation "
                "guidelines. Check the Croma Cancellation & "
                "Returns Policy for the applicable conditions, "
                "including any rules relating to dispatch."
            )
            source = "Croma Cancellation & Returns Policy"

        elif "shipping" in query or "delivery" in query:
            answer = (
                "The Croma Shipping Policy is listed in the "
                "document library. Consult the document for "
                "the applicable shipping and delivery guidance."
            )
            source = "Croma Shipping Policy"

        elif "warranty" in query or "support" in query:
            answer = (
                "The Croma Warranty Policy is listed in the "
                "document library. Consult the document for "
                "warranty coverage, eligibility, and support "
                "information."
            )
            source = "Croma Warranty Policy"

        elif "inventory" in query or "reorder" in query:
            answer = (
                "The library includes SAP Inventory Management "
                "and SAP Reorder Management documents for "
                "inventory-related operations."
            )
            source = "SAP Inventory Management / SAP Reorder Management"

        elif "order" in query:
            answer = (
                "The library includes SAP Order Management. "
                "Consult the source document for order-related "
                "operational information."
            )
            source = "SAP Order Management"

        else:
            answer = (
                "The current page uses sample keyword-based "
                "responses. Connect your Flask agent and RAG "
                "retrieval pipeline to answer questions using "
                "the actual indexed document contents."
            )
            source = "Company Knowledge Base"

        st.markdown(
            """
            <div class="knowledge-section-heading result-heading">
                <div class="knowledge-eyebrow">SEARCH RESPONSE</div>
                <h2>Knowledge result</h2>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="knowledge-answer-card">
                <div class="answer-topline">
                    <span class="answer-indicator"></span>
                    <span class="answer-label">KNOWLEDGE RESPONSE</span>
                </div>
                <div class="answer-content">{answer}</div>
                <div class="answer-source">
                    <span>Source document</span>
                    <strong>📄 {source}</strong>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# KNOWLEDGE CATEGORIES
# ============================================================

st.markdown(
    """
    <div class="knowledge-section-heading">
        <div class="knowledge-eyebrow">EXPLORE THE LIBRARY</div>
        <h2>Knowledge categories</h2>
        <p>Browse the main areas covered by your documents.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

category_columns = st.columns(3)

categories = [
    {
        "icon": "↩",
        "title": "Returns & Cancellations",
        "description": (
            "Return policies, cancellation guidelines, "
            "refunds and customer conditions."
        ),
        "count": "2 related documents",
    },
    {
        "icon": "↗",
        "title": "Shipping & Delivery",
        "description": (
            "Shipping policies, delivery guidelines "
            "and order fulfilment information."
        ),
        "count": "1 related document",
    },
    {
        "icon": "✓",
        "title": "Warranty & Support",
        "description": (
            "Warranty policies, coverage information "
            "and product support guidance."
        ),
        "count": "1 related document",
    },
]

for index, category in enumerate(categories):
    with category_columns[index]:
        st.markdown(
            f"""
            <div class="knowledge-category-card">
                <div class="category-icon">{category["icon"]}</div>
                <div class="category-title">{category["title"]}</div>
                <div class="category-description">
                    {category["description"]}
                </div>
                <div class="category-count">{category["count"]}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# DOCUMENT LIBRARY TABLE
# ============================================================

st.markdown(
    """
    <div class="knowledge-section-heading document-heading">
        <div class="knowledge-eyebrow">DOCUMENT LIBRARY</div>
        <h2>Indexed documents</h2>
        <p>
            Search and filter the documents available in the
            knowledge library.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# Search and category filters
filter_col, category_col, status_col = st.columns([2, 1.5, 1])

with filter_col:
    document_search = st.text_input(
        "Search documents",
        placeholder="Search by document name or keyword...",
        key="document_search",
    )

with category_col:
    selected_category = st.selectbox(
        "Category",
        options=["All categories"] + sorted(df["Category"].unique()),
        key="document_category_filter",
    )

with status_col:
    selected_status = st.selectbox(
        "Status",
        options=["All statuses"] + sorted(df["Status"].unique()),
        key="document_status_filter",
    )


filtered_df = df.copy()

if document_search.strip():
    search_text = document_search.strip()

    matches = (
        filtered_df["Document"].str.contains(
            search_text, case=False, na=False
        )
        | filtered_df["Category"].str.contains(
            search_text, case=False, na=False
        )
        | filtered_df["Type"].str.contains(
            search_text, case=False, na=False
        )
    )

    filtered_df = filtered_df[matches]

if selected_category != "All categories":
    filtered_df = filtered_df[
        filtered_df["Category"] == selected_category
    ]

if selected_status != "All statuses":
    filtered_df = filtered_df[
        filtered_df["Status"] == selected_status
    ]


st.markdown(
    f"""
    <div class="document-table-summary">
        <span>Showing <strong>{len(filtered_df)}</strong>
        of <strong>{len(df)}</strong> documents</span>
        <span class="table-status-note">
            ● Document status shown from configured page data
        </span>
    </div>
    """,
    unsafe_allow_html=True,
)


# Use a native Streamlit table for sorting and a cleaner layout.
# Hide the dataframe index and format the status column.
st.dataframe(
    filtered_df,
    use_container_width=True,
    hide_index=True,
    height=365,
    column_config={
        "Document": st.column_config.TextColumn(
            "Document name",
            help="Name of the knowledge document",
            width="large",
        ),
        "Category": st.column_config.TextColumn(
            "Category",
            width="medium",
        ),
        "Type": st.column_config.TextColumn(
            "Document type",
            width="small",
        ),
        "Status": st.column_config.TextColumn(
            "Indexing status",
            width="small",
        ),
    },
)


if filtered_df.empty:
    st.info(
        "No documents match your filters. "
        "Try a different search term or category."
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="knowledge-footer">
        <span>CommerceAI</span>
        <span class="footer-divider">•</span>
        <span>Knowledge Intelligence</span>
    </div>
    """,
    unsafe_allow_html=True,
)
