from pathlib import Path
import html

import pandas as pd
import streamlit as st

# =========================================================
# CONFIGURATION
# =========================================================
st.set_page_config(
    page_title="CommerceAI | Business Intelligence",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = Path(__file__).resolve().parent
CSS_PATH = BASE_DIR / "assets" / "style.css"

if CSS_PATH.exists():
    st.markdown(
        f"<style>{CSS_PATH.read_text(encoding='utf-8')}</style>",
        unsafe_allow_html=True,
    )
else:
    st.warning(
        "Stylesheet not found. Create assets/style.css "
        "using the CSS provided below."
    )

# Hide Streamlit's default multipage navigation.
# Keep the custom CommerceAI navigation below.
st.markdown(
    """
    <style>
        [data-testid="stSidebarNav"] {
            display: none !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# SESSION STATE
# =========================================================
defaults = {
    "active_section": "Home",
    "messages": [],
    "recent_questions": [],
    "knowledge_result": None,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# =========================================================
# DEMO DATA
# Replace these examples with database/API data later.
# =========================================================
inventory_df = pd.DataFrame([
    {
        "Product": "Smart Watch",
        "SKU": "ELEC-001",
        "Category": "Wearables",
        "Stock": 42,
        "Reorder Level": 20,
        "Unit Price": 4500,
    },
    {
        "Product": "USB-C Cable",
        "SKU": "ACC-002",
        "Category": "Accessories",
        "Stock": 68,
        "Reorder Level": 25,
        "Unit Price": 350,
    },
    {
        "Product": "Smartphone",
        "SKU": "ELEC-003",
        "Category": "Mobiles",
        "Stock": 31,
        "Reorder Level": 15,
        "Unit Price": 24999,
    },
    {
        "Product": "Laptop Stand",
        "SKU": "ACC-004",
        "Category": "Accessories",
        "Stock": 55,
        "Reorder Level": 20,
        "Unit Price": 1200,
    },
    {
        "Product": "HDMI Cable",
        "SKU": "ACC-005",
        "Category": "Accessories",
        "Stock": 19,
        "Reorder Level": 20,
        "Unit Price": 500,
    },
    {
        "Product": "Webcam",
        "SKU": "ELEC-006",
        "Category": "Electronics",
        "Stock": 14,
        "Reorder Level": 18,
        "Unit Price": 2200,
    },
])

def stock_status(row):
    if row["Stock"] <= 0:
        return "Out of stock"
    if row["Stock"] <= row["Reorder Level"]:
        return "Reorder"
    if row["Stock"] <= row["Reorder Level"] * 1.5:
        return "Monitor"
    return "Healthy"

inventory_df["Status"] = inventory_df.apply(stock_status, axis=1)
inventory_df["Stock Value"] = (
    inventory_df["Stock"] * inventory_df["Unit Price"]
)

documents_df = pd.DataFrame([
    ["Croma Cancellation & Returns Policy", "Returns & Cancellations", "Policy", "Indexed"],
    ["Croma FAQ", "General Information", "FAQ", "Indexed"],
    ["Croma Privacy Policy", "Company Policy", "Policy", "Indexed"],
    ["Croma Shipping Policy", "Shipping & Delivery", "Policy", "Indexed"],
    ["Croma Terms & Conditions", "Legal & Policy", "Legal", "Indexed"],
    ["Croma Warranty Policy", "Warranty & Support", "Policy", "Indexed"],
    ["SAP Inventory Management", "Inventory Operations", "Operations", "Indexed"],
    ["SAP Reorder Management", "Inventory Operations", "Operations", "Indexed"],
    ["SAP Order Management", "Order Operations", "Operations", "Indexed"],
], columns=["Document", "Category", "Type", "Status"])

months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
revenue = [1.42, 1.65, 1.82, 1.95, 2.31, 2.67]
orders = [6, 8, 7, 9, 10, 10]

total_products = len(inventory_df)
inventory_value = int(inventory_df["Stock Value"].sum())
reorder_count = int(
    inventory_df["Status"].isin(["Reorder", "Out of stock"]).sum()
)
monitor_count = int((inventory_df["Status"] == "Monitor").sum())

# =========================================================
# HELPERS
# =========================================================
def money_inr(value):
    return f"₹{value:,.0f}"

def section_header(eyebrow, title, description):
    st.markdown(
        f"""
        <div class="section-heading">
            <div class="eyebrow">{html.escape(eyebrow)}</div>
            <h1>{html.escape(title)}</h1>
            <p>{html.escape(description)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

def metric_card(label, value, note, number):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-index">{number}</div>
            <div class="metric-label">{html.escape(label)}</div>
            <div class="metric-value">{html.escape(str(value))}</div>
            <div class="metric-note">{html.escape(note)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def answer_question(question):
    """Demo answer logic; replace with your Flask/RAG agent."""
    q = question.lower()

    if any(word in q for word in ["revenue", "sales", "profit"]):
        return (
            "The sample analytics dashboard reports total revenue of "
            "₹12.35M and total profit of ₹1.84M. These are demonstration "
            "figures, not live database results."
        )

    if any(word in q for word in ["inventory", "stock", "reorder"]):
        items = inventory_df[
            inventory_df["Status"].isin(["Reorder", "Out of stock"])
        ]["Product"].tolist()
        return (
            f"{len(items)} products need replenishment review: "
            f"{', '.join(items)}. Check the Inventory section for "
            "current sample stock levels."
        )

    if any(word in q for word in ["best product", "top product", "performing"]):
        return (
            "The sample product list includes Smart Watch, USB-C Cable, "
            "Smartphone, Laptop Stand, and HDMI Cable. Connect your sales "
            "database to rank products using actual revenue or units sold."
        )

    if any(word in q for word in ["cancel", "return", "refund"]):
        return (
            "The knowledge library includes the Croma Cancellation & "
            "Returns Policy. Review the source document for the applicable "
            "eligibility, dispatch, and refund conditions."
        )

    if any(word in q for word in ["shipping", "delivery", "warranty"]):
        return (
            "The knowledge library contains shipping and warranty policy "
            "documents. Search the Knowledge Assistant for the relevant "
            "source. This demo does not yet retrieve the full document text."
        )

    return (
        "I've received your question. This interface currently uses "
        "demonstration responses. Connect your Flask agent and retrieval "
        "pipeline to answer from your actual business data."
    )

def send_question(question):
    question = question.strip()
    if not question:
        return

    st.session_state.messages.append({
        "role": "user",
        "content": question,
    })

    recent = st.session_state.recent_questions
    if question not in recent:
        recent.append(question)

    st.session_state.recent_questions = recent[-20:]

    response = answer_question(question)
    st.session_state.messages.append({
        "role": "assistant",
        "content": response,
    })

# =========================================================
# PERMANENT LEFT SIDEBAR
# All navigation lives here. No st.Page or pages/ files.
# =========================================================
with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="brand-symbol">✦</div>
            <div>
                <div class="brand-name">CommerceAI</div>
                <div class="brand-caption">BUSINESS INTELLIGENCE</div>
            </div>
        </div>
        <div class="sidebar-label">WORKSPACE</div>
        """,
        unsafe_allow_html=True,
    )

    sections = [
        "Home",
        "AI Agent",
        "Inventory",
        "Analytics",
        "Knowledge Assistant",
    ]

    section_icons = {
        "Home": "⌂",
        "AI Agent": "✳",
        "Inventory": "▤",
        "Analytics": "▥",
        "Knowledge Assistant": "▧",
    }

    current_index = sections.index(st.session_state.active_section)

    selected_section = st.radio(
        "Navigation",
        options=sections,
        index=current_index,
        format_func=lambda item: f"{section_icons[item]}   {item}",
        key="main_navigation",
        label_visibility="collapsed",
    )

    st.session_state.active_section = selected_section

    st.markdown(
        """
        <div class="sidebar-spacer"></div>
        <div class="sidebar-status">
            <span class="status-dot"></span>
            <span>Workspace ready</span>
            <span class="version-tag">DEMO</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Recent chats appear only while AI Agent is selected.
    if selected_section == "AI Agent":
        st.markdown(
            '<div class="sidebar-label recent-label">RECENT QUESTIONS</div>',
            unsafe_allow_html=True,
        )

        recent_questions = list(reversed(st.session_state.recent_questions))

        if recent_questions:
            for index, recent in enumerate(recent_questions[:8]):
                button_label = (
                    recent if len(recent) <= 35 else recent[:32] + "..."
                )
                if st.button(
                    button_label,
                    key=f"recent_chat_{index}",
                    use_container_width=True,
                    help=recent,
                ):
                    send_question(recent)
                    st.rerun()
        else:
            st.markdown(
                '<div class="sidebar-empty">'
                'Your recent questions will appear here.'
                '</div>',
                unsafe_allow_html=True,
            )

        if st.button(
            "＋  New conversation",
            key="new_ai_conversation",
            use_container_width=True,
        ):
            st.session_state.messages = []
            st.rerun()

# =========================================================
# HOME
# =========================================================
if selected_section == "Home":
    st.markdown(
        """
        <section class="hero">
            <div class="eyebrow">YOUR BUSINESS, IN FOCUS</div>
            <h1>Clarity for every<br>business decision.</h1>
            <p>
                Explore your commerce performance, identify inventory
                risks, and find operational knowledge from one workspace.
            </p>
            <div class="hero-foot">
                <span class="status-dot"></span>
                Your CommerceAI workspace
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    section_header(
        "BUSINESS SNAPSHOT",
        "Your business at a glance",
        "Illustrative figures from the current sample data.",
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("TOTAL REVENUE", "₹12.35M", "Sample analytics figure", "01")
    with c2:
        metric_card("TOTAL ORDERS", "50", "Sample order volume", "02")
    with c3:
        metric_card("INVENTORY PRODUCTS", total_products, "Listed sample products", "03")
    with c4:
        metric_card("REORDER ALERTS", reorder_count, "Items to review", "04")

    st.markdown(
        """
        <div class="home-note">
            <div class="home-note-title">Where would you like to start?</div>
            <div class="home-note-copy">
                Use the left navigation to chat with the AI Agent, inspect
                inventory, review business analytics, or search company
                documents in the Knowledge Assistant.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# =========================================================
# AI AGENT
# =========================================================
elif selected_section == "AI Agent":
    section_header(
        "COMMERCEAI ASSISTANT",
        "What can I help you understand?",
        "Ask about revenue, inventory, product performance, or company policies.",
    )

    st.markdown(
        '<div class="chat-context">BUSINESS ASSISTANT · DEMO MODE</div>',
        unsafe_allow_html=True,
    )

    if not st.session_state.messages:
        st.markdown(
            """
            <div class="chat-welcome">
                <div class="chat-welcome-icon">✳</div>
                <h2>Start with a business question</h2>
                <p>
                    Ask a clear question. Your conversation will stay
                    available as you explore the dashboard.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="suggestions-label">TRY ASKING</div>',
            unsafe_allow_html=True,
        )

        suggestions = [
            "What is our total revenue?",
            "Which products have inventory risk?",
            "Which products are performing best?",
            "Can I cancel a dispatched order?",
        ]

        suggestion_cols = st.columns(2)
        for index, suggestion in enumerate(suggestions):
            with suggestion_cols[index % 2]:
                if st.button(
                    suggestion,
                    key=f"ai_suggestion_{index}",
                    use_container_width=True,
                ):
                    send_question(suggestion)
                    st.rerun()

    for message_index, message in enumerate(st.session_state.messages):
        with st.chat_message(
            message["role"],
            avatar="✦" if message["role"] == "assistant" else "●",
        ):
            st.markdown(message["content"])

    prompt = st.chat_input(
        "Message CommerceAI...",
        key="ai_agent_chat_input",
    )

    if prompt:
        send_question(prompt)
        st.rerun()

# =========================================================
# INVENTORY
# =========================================================
elif selected_section == "Inventory":
    section_header(
        "INVENTORY INTELLIGENCE",
        "Inventory overview",
        "Monitor stock levels, identify supply risks, and review replenishment needs.",
    )

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        metric_card("TOTAL PRODUCTS", total_products, "Products listed", "01")
    with k2:
        metric_card("REORDER REQUIRED", reorder_count, "At or below threshold", "02")
    with k3:
        metric_card("STOCK TO MONITOR", monitor_count, "Approaching threshold", "03")
    with k4:
        metric_card("INVENTORY VALUE", money_inr(inventory_value), "Listed stock value", "04")

    st.markdown('<div class="subsection-title">Product inventory</div>', unsafe_allow_html=True)

    f1, f2, f3 = st.columns([2, 1, 1])
    with f1:
        inventory_search = st.text_input(
            "Search products",
            placeholder="Search product or SKU...",
            key="inventory_search",
        )
    with f2:
        category_options = ["All categories"] + sorted(inventory_df["Category"].unique().tolist())
        inventory_category = st.selectbox(
            "Category",
            category_options,
            key="inventory_category",
        )
    with f3:
        status_options = ["All statuses", "Healthy", "Monitor", "Reorder", "Out of stock"]
        inventory_status = st.selectbox(
            "Status",
            status_options,
            key="inventory_status",
        )

    filtered_inventory = inventory_df.copy()

    if inventory_search.strip():
        term = inventory_search.strip()
        filtered_inventory = filtered_inventory[
            filtered_inventory["Product"].str.contains(term, case=False, na=False)
            | filtered_inventory["SKU"].str.contains(term, case=False, na=False)
        ]

    if inventory_category != "All categories":
        filtered_inventory = filtered_inventory[
            filtered_inventory["Category"] == inventory_category
        ]

    if inventory_status != "All statuses":
        filtered_inventory = filtered_inventory[
            filtered_inventory["Status"] == inventory_status
        ]

    inventory_display = filtered_inventory.copy()
    inventory_display["Unit Price"] = inventory_display["Unit Price"].map(money_inr)
    inventory_display["Stock Value"] = inventory_display["Stock Value"].map(money_inr)

    st.caption(f"Showing {len(filtered_inventory)} of {len(inventory_df)} products")

    st.dataframe(
        inventory_display[
            ["Product", "SKU", "Category", "Stock", "Reorder Level", "Status", "Unit Price", "Stock Value"]
        ],
        use_container_width=True,
        hide_index=True,
        height=290,
    )

    st.markdown('<div class="subsection-title">Reorder recommendations</div>', unsafe_allow_html=True)

    reorder_df = inventory_df[
        inventory_df["Status"].isin(["Reorder", "Out of stock"])
    ]

    if reorder_df.empty:
        st.success("No products currently require replenishment.")
    else:
        for _, item in reorder_df.iterrows():
            suggested = max(
                int(item["Reorder Level"]) * 2 - int(item["Stock"]),
                int(item["Reorder Level"]),
            )
            st.markdown(
                f"""
                <div class="recommendation-card">
                    <div>
                        <div class="recommendation-title">{html.escape(item["Product"])}</div>
                        <div class="muted-copy">
                            SKU {html.escape(item["SKU"])} · {html.escape(item["Category"])}
                        </div>
                        <div class="muted-copy">
                            Current stock: {int(item["Stock"])} ·
                            Reorder threshold: {int(item["Reorder Level"])}
                        </div>
                    </div>
                    <div class="recommendation-quantity">
                        <span>Suggested top-up</span>
                        <strong>{suggested} units</strong>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

# =========================================================
# ANALYTICS
# =========================================================
elif selected_section == "Analytics":
    section_header(
        "BUSINESS INTELLIGENCE",
        "Analytics overview",
        "Review revenue trends, order activity, and product performance.",
    )

    a1, a2, a3, a4 = st.columns(4)
    with a1:
        metric_card("TOTAL REVENUE", "₹12.35M", "Sample figure", "01")
    with a2:
        metric_card("TOTAL ORDERS", "50", "Sample figure", "02")
    with a3:
        metric_card("AVERAGE ORDER VALUE", "₹246.9K", "Revenue divided by orders", "03")
    with a4:
        metric_card("TOTAL PROFIT", "₹1.84M", "Sample figure", "04")

    chart_left, chart_right = st.columns([1.6, 1])

    with chart_left:
        st.markdown('<div class="subsection-title">Revenue performance</div>', unsafe_allow_html=True)
        revenue_df = pd.DataFrame({"Month": months, "Revenue (₹M)": revenue})
        st.line_chart(revenue_df.set_index("Month"), use_container_width=True)

    with chart_right:
        st.markdown('<div class="subsection-title">Monthly order activity</div>', unsafe_allow_html=True)
        orders_df = pd.DataFrame({"Month": months, "Orders": orders})
        st.bar_chart(orders_df.set_index("Month"), use_container_width=True)

    st.markdown('<div class="subsection-title">Top performing products</div>', unsafe_allow_html=True)

    products_df = pd.DataFrame({
        "Product": ["Smart Watch", "USB-C Cable", "Smartphone", "Laptop Stand", "HDMI Cable"],
        "Units Sold": [28, 27, 26, 23, 23],
    })

    st.dataframe(products_df, use_container_width=True, hide_index=True)

    st.markdown('<div class="subsection-title">Category revenue</div>', unsafe_allow_html=True)

    category_df = pd.DataFrame({
        "Category": ["Accessories", "Computers", "Electronics"],
        "Revenue (₹)": [5187386, 4271033, 2887490],
    })

    st.bar_chart(category_df.set_index("Category"), use_container_width=True)

# =========================================================
# KNOWLEDGE ASSISTANT
# =========================================================
elif selected_section == "Knowledge Assistant":
    section_header(
        "KNOWLEDGE INTELLIGENCE",
        "Knowledge assistant",
        "Search the sample policy and operations library.",
    )

    st.markdown(
        """
        <div class="knowledge-intro">
            Search the available document titles and get a sample
            guidance response. Full-document retrieval is not connected yet.
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("knowledge_search_form"):
        knowledge_query = st.text_input(
            "Search company knowledge",
            placeholder="e.g. Can I cancel an order after dispatch?",
        )
        knowledge_submit = st.form_submit_button(
            "Search knowledge",
            use_container_width=True,
        )

    quick_cols = st.columns(4)
    quick_searches = [
        "Return policy",
        "Order cancellation",
        "Shipping policy",
        "Warranty policy",
    ]

    for index, query in enumerate(quick_searches):
        with quick_cols[index]:
            if st.button(query, key=f"knowledge_quick_{index}", use_container_width=True):
                st.session_state.knowledge_result = query
                st.rerun()

    if knowledge_submit and knowledge_query.strip():
        st.session_state.knowledge_result = knowledge_query.strip()

    query_to_answer = st.session_state.knowledge_result

    if query_to_answer:
        q = query_to_answer.lower()

        if "return" in q or "refund" in q or "cancel" in q:
            source = "Croma Cancellation & Returns Policy"
            answer = (
                "The document library lists the Croma Cancellation & Returns "
                "Policy. Consult the original document for eligibility, "
                "dispatch conditions, and refund procedures."
            )
        elif "shipping" in q or "delivery" in q:
            source = "Croma Shipping Policy"
            answer = (
                "The library includes the Croma Shipping Policy. Review the "
                "source document for applicable shipping and delivery rules."
            )
        elif "warranty" in q or "support" in q:
            source = "Croma Warranty Policy"
            answer = (
                "The Croma Warranty Policy is available in the sample library. "
                "Consult the document for coverage and support conditions."
            )
        elif "inventory" in q or "reorder" in q or "stock" in q:
            source = "SAP Inventory Management / SAP Reorder Management"
            answer = (
                "The library includes SAP inventory and reorder management "
                "documents for operational guidance."
            )
        elif "order" in q:
            source = "SAP Order Management"
            answer = (
                "The library lists SAP Order Management. Consult the original "
                "document for order-operation guidance."
            )
        else:
            source = "Company Knowledge Base"
            answer = (
                "The current version provides sample keyword-based responses. "
                "Connect your document retrieval pipeline to answer from "
                "the full indexed content."
            )

        st.markdown(
            f"""
            <div class="answer-card">
                <div class="eyebrow">SEARCH RESULT</div>
                <h3>{html.escape(source)}</h3>
                <p>{html.escape(answer)}</p>
                <div class="muted-copy">
                    Demonstration response · Verify details in the source document
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown('<div class="subsection-title">Document library</div>', unsafe_allow_html=True)

    doc_filter_col, doc_category_col, doc_status_col = st.columns([2, 1.5, 1])

    with doc_filter_col:
        doc_search = st.text_input(
            "Search documents",
            placeholder="Search document name or category...",
            key="doc_search",
        )
    with doc_category_col:
        doc_categories = ["All categories"] + sorted(documents_df["Category"].unique().tolist())
        doc_category = st.selectbox(
            "Document category",
            doc_categories,
            key="doc_category",
        )
    with doc_status_col:
        doc_status = st.selectbox(
            "Document status",
            ["All statuses", "Indexed"],
            key="doc_status",
        )

    filtered_docs = documents_df.copy()

    if doc_search.strip():
        term = doc_search.strip()
        filtered_docs = filtered_docs[
            filtered_docs["Document"].str.contains(term, case=False, na=False)
            | filtered_docs["Category"].str.contains(term, case=False, na=False)
            | filtered_docs["Type"].str.contains(term, case=False, na=False)
        ]

    if doc_category != "All categories":
        filtered_docs = filtered_docs[filtered_docs["Category"] == doc_category]

    if doc_status != "All statuses":
        filtered_docs = filtered_docs[filtered_docs["Status"] == doc_status]

    st.caption(f"Showing {len(filtered_docs)} of {len(documents_df)} documents")

    st.dataframe(
        filtered_docs,
        use_container_width=True,
        hide_index=True,
        height=320,
    )

# =========================================================
# FOOTER
# =========================================================
st.markdown(
    """
    <div class="app-footer">
        <span>CommerceAI</span>
        <span class="footer-separator">•</span>
        <span>Business Intelligence Workspace</span>
    </div>
    """,
    unsafe_allow_html=True,
)
