
from pathlib import Path
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Knowledge Assistant | CommerceAI",
    page_icon="📚",
    layout="wide",
)

BASE_DIR = Path(__file__).resolve().parent.parent
CSS_PATH = BASE_DIR / "assets" / "style.css"
if CSS_PATH.exists():
    st.markdown(
        f"<style>{CSS_PATH.read_text(encoding='utf-8')}</style>",
        unsafe_allow_html=True,
    )

documents = [
    {"Document": "Croma Cancellation & Returns Policy", "Category": "Returns & Cancellations", "Type": "Policy", "Status": "Indexed"},
    {"Document": "Croma FAQ", "Category": "General Information", "Type": "FAQ", "Status": "Indexed"},
    {"Document": "Croma Privacy Policy", "Category": "Company Policy", "Type": "Policy", "Status": "Indexed"},
    {"Document": "Croma Shipping Policy", "Category": "Shipping & Delivery", "Type": "Policy", "Status": "Indexed"},
    {"Document": "Croma Terms & Conditions", "Category": "Legal & Policy", "Type": "Legal", "Status": "Indexed"},
    {"Document": "Croma Warranty Policy", "Category": "Warranty & Support", "Type": "Policy", "Status": "Indexed"},
    {"Document": "SAP Inventory Management", "Category": "Inventory Operations", "Type": "Operations", "Status": "Indexed"},
    {"Document": "SAP Reorder Management", "Category": "Inventory Operations", "Type": "Operations", "Status": "Indexed"},
    {"Document": "SAP Order Management", "Category": "Order Operations", "Type": "Operations", "Status": "Indexed"},
]
df = pd.DataFrame(documents)

st.markdown(
    """
    <div class="page-header">
        <div>
            <div class="page-kicker">KNOWLEDGE INTELLIGENCE</div>
            <h1 class="page-title">Knowledge Assistant</h1>
            <p class="page-description">
                Search company policies and operational documents.
            </p>
        </div>
        <div class="page-header-icon">📚</div>
    </div>
    """,
    unsafe_allow_html=True,
)

a, b, c = st.columns(3)
for col, label, value, note in [
    (a, "TOTAL DOCUMENTS", "9", "Listed in the sample library"),
    (b, "KNOWLEDGE AREAS", "6+", "Policies and operations"),
    (c, "INDEXING STATUS", "Ready", "Sample status"),
]:
    with col:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value}</div>
                <div class="metric-note">{note}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("## Search company knowledge")

if "knowledge_query" not in st.session_state:
    st.session_state.knowledge_query = ""

with st.form("knowledge_search"):
    query = st.text_input(
        "Ask a question or enter a keyword",
        key="knowledge_query",
        placeholder="e.g. Can I cancel my order after dispatch?",
    )
    submitted = st.form_submit_button("Search knowledge", type="primary")

quick_cols = st.columns(4)
quick_queries = [
    "Return policy", "Order cancellation", "Shipping policy", "Warranty policy"
]
for i, item in enumerate(quick_queries):
    with quick_cols[i]:
        if st.button(item, key=f"knowledge_quick_{i}", use_container_width=True):
            st.session_state.knowledge_query = item
            st.session_state.knowledge_submitted = True
            st.rerun()

if submitted:
    st.session_state.knowledge_submitted = True

if st.session_state.get("knowledge_submitted", False):
    q = st.session_state.knowledge_query.strip().lower()

    if q:
        if "return" in q or "refund" in q:
            answer = "The sample library lists the Croma Cancellation & Returns Policy. Consult the source document for eligibility and refund procedures."
            source = "Croma Cancellation & Returns Policy"
        elif "cancel" in q:
            answer = "The sample library lists cancellation guidance in the Croma Cancellation & Returns Policy. Check the document for applicable conditions."
            source = "Croma Cancellation & Returns Policy"
        elif "shipping" in q or "delivery" in q:
            answer = "The Croma Shipping Policy is listed in the library. Consult the document for shipping and delivery guidance."
            source = "Croma Shipping Policy"
        elif "warranty" in q or "support" in q:
            answer = "The Croma Warranty Policy is listed in the library. Consult it for warranty coverage and support information."
            source = "Croma Warranty Policy"
        elif "inventory" in q or "reorder" in q:
            answer = "The library lists SAP Inventory Management and SAP Reorder Management for inventory-related operations."
            source = "SAP Inventory Management / SAP Reorder Management"
        elif "order" in q:
            answer = "The library lists SAP Order Management. Consult the document for order-related operational information."
            source = "SAP Order Management"
        else:
            answer = "This is a sample keyword search. Connect document retrieval to answer using the actual contents of your indexed files."
            source = "Company Knowledge Base"

        st.markdown("### Search response")
        with st.container(border=True):
            st.markdown(answer)
            st.caption(f"Source: {source}")

st.markdown("## Document library")

f1, f2, f3 = st.columns([2, 1.5, 1])
with f1:
    search = st.text_input("Search documents", placeholder="Name, category, or type")
with f2:
    category = st.selectbox(
        "Category",
        ["All categories"] + sorted(df["Category"].unique().tolist()),
    )
with f3:
    status = st.selectbox(
        "Status",
        ["All statuses"] + sorted(df["Status"].unique().tolist()),
    )

filtered = df.copy()
if search.strip():
    term = search.strip()
    filtered = filtered[
        filtered["Document"].str.contains(term, case=False, na=False)
        | filtered["Category"].str.contains(term, case=False, na=False)
        | filtered["Type"].str.contains(term, case=False, na=False)
    ]
if category != "All categories":
    filtered = filtered[filtered["Category"] == category]
if status != "All statuses":
    filtered = filtered[filtered["Status"] == status]

st.caption(f"Showing {len(filtered)} of {len(df)} documents")
st.dataframe(filtered, use_container_width=True, hide_index=True)
