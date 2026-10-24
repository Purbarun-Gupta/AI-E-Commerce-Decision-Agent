from pathlib import Path
import html

import pandas as pd
import streamlit as st
from Pages.ai_agent import render_ai_agent
from Pages.analytics import render_analytics
from Pages.inventory import render_inventory
from Pages.knowledge_assistant import render_knowledge_assistant
from api import api_post, api_get

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

def fetch_data(endpoint):
    data = api_get(endpoint)

    if isinstance(data, dict) and "error" in data:
        return None

    return data

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

    with st.spinner("Analyzing your business data..."):
        result = api_post(
            "/api/agent/ask",
            {"question": question}
        )

    if not isinstance(result, dict) or "error" in result:
        st.error("AI backend request failed")
        st.json(result if isinstance(result, dict) else {"result": str(result)})

        answer = "The AI request failed. See the error details above."
    else:
        answer = result.get(
            "answer",
            "The backend returned no answer."
        )

        route = result.get("route")

        if route:
            answer = f"**Route: {route}**\n\n{answer}"

        knowledge = result.get("knowledge")

        if knowledge and knowledge.get("sources"):
            answer += "\n\n**Sources:**\n"

            for source in knowledge["sources"]:
                name = source.get("source", "Unknown document")
                page = source.get("page", "Unknown")
                answer += f"\n- {name} — page {page}"

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
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

    
    business_summary = fetch_data("/api/analytics/summary")
    inventory_data = fetch_data("/api/analytics/inventory-risk")
    low_stock_data = fetch_data("/api/analytics/low-stock")

    section_header(
        "BUSINESS SNAPSHOT",
        "Your business at a glance",
        "Live metrics retrieved from your business database.",
    )

    if business_summary is None:
        st.error("Unable to load business analytics. Check that Flask is running.")
    else:
        total_revenue = business_summary.get("total_revenue")
        total_orders = business_summary.get("total_orders")

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            value = money_inr(total_revenue) if total_revenue is not None else "N/A"
            metric_card("TOTAL REVENUE", value, "From completed business analytics", "01")

        with c2:
            value = f"{total_orders:,}" if total_orders is not None else "N/A"
            metric_card("TOTAL ORDERS", value, "Recorded orders", "02")

        with c3:
            if isinstance(inventory_data, list):
                product_count = len(inventory_data)
                metric_card(
                    "INVENTORY PRODUCTS",
                    product_count,
                    "Products returned by inventory-risk analytics",
                    "03",
                )
            else:
                metric_card(
                    "INVENTORY PRODUCTS",
                    "N/A",
                    "Inventory data unavailable",
                    "03",
                )

        with c4:
            if isinstance(low_stock_data, list):
                metric_card(
                    "LOW-STOCK PRODUCTS",
                    len(low_stock_data),
                    "Products returned by low-stock analytics",
                    "04",
                )
            else:
                metric_card(
                    "LOW-STOCK PRODUCTS",
                    "N/A",
                    "Low-stock data unavailable",
                    "04",
                )


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
    render_ai_agent()

# =========================================================
# INVENTORY
# =========================================================
elif selected_section == "Inventory":
    render_inventory()

# =========================================================
# ANALYTICS
# =========================================================
elif selected_section == "Analytics":
    render_analytics()

# =========================================================
# KNOWLEDGE ASSISTANT
# =========================================================
elif selected_section == "Knowledge Assistant":
    render_knowledge_assistant()
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
