
from pathlib import Path
import os

import pandas as pd
import requests
import streamlit as st


def _backend_url():
    return os.getenv("BACKEND_URL", "http://127.0.0.1:5000").rstrip("/")


def _get_json(endpoint, timeout=20):
    """GET a Flask endpoint and return (JSON, error)."""
    try:
        response = requests.get(
            f"{_backend_url()}/{endpoint.lstrip('/')}",
            timeout=timeout,
        )
        try:
            payload = response.json()
        except ValueError:
            return None, "Backend returned a non-JSON response."

        if not response.ok:
            detail = payload.get("error") if isinstance(payload, dict) else None
            return None, detail or f"Request failed (HTTP {response.status_code})."

        return payload, None

    except requests.exceptions.RequestException:
        return None, "Could not connect to Flask. Check that the backend is running."


def _ask_rag(question):
    """Send the question to the existing Flask agent/RAG endpoint."""
    try:
        response = requests.post(
            f"{_backend_url()}/api/agent/ask",
            json={"question": question},
            timeout=180,
        )

        try:
            payload = response.json()
        except ValueError:
            return None, "Backend returned a non-JSON response."

        if not response.ok:
            detail = payload.get("error") if isinstance(payload, dict) else None
            return None, detail or f"Question request failed (HTTP {response.status_code})."

        if not isinstance(payload, dict):
            return None, "Backend returned an unexpected response format."

        if payload.get("error"):
            return None, str(payload["error"])

        return payload, None

    except requests.exceptions.Timeout:
        return None, "The request timed out. Please try again."
    except requests.exceptions.RequestException:
        return None, "Could not connect to Flask. Check that the backend is running."


def _answer_from_result(result):
    """Safely extract the answer from the Flask agent response."""

    if isinstance(result, str):
        return result.strip() or None

    if not isinstance(result, dict):
        return None

    for key in ("answer", "response", "reply", "message", "output", "result"):
        value = result.get(key)

        if isinstance(value, str) and value.strip():
            return value.strip()

        if isinstance(value, dict):
            for nested_key in ("answer", "response", "text", "content"):
                nested = value.get(nested_key)

                if isinstance(nested, str) and nested.strip():
                    return nested.strip()

    knowledge = result.get("knowledge")

    if isinstance(knowledge, dict):
        value = knowledge.get("answer") or knowledge.get("response")

        if isinstance(value, str) and value.strip():
            return value.strip()

    elif isinstance(knowledge, str) and knowledge.strip():
        return knowledge.strip()

    return None



def _render_formatted_answer(answer):
    """Render structured RAG answers with clear visual hierarchy."""
    import re

    if not answer:
        st.info("No answer was returned.")
        return

    section_pattern = re.compile(
        r"(?i)\b(KEY FINDING|EVIDENCE|RECOMMENDED ACTION|REASON)\s*:"
    )

    matches = list(section_pattern.finditer(answer))

    # Keep ordinary responses readable if no known headings are present.
    if not matches:
        st.markdown(answer)
        return

    intro = answer[:matches[0].start()].strip()
    if intro:
        st.markdown(intro)

    sections = {}

    for index, match in enumerate(matches):
        start = match.end()
        end = (
            matches[index + 1].start()
            if index + 1 < len(matches)
            else len(answer)
        )

        label = match.group(1).upper()
        content = answer[start:end].strip()

        if content:
            sections.setdefault(label, []).append(content)

    if sections.get("KEY FINDING"):
        st.markdown("#### 🎯 Key finding")
        for content in sections["KEY FINDING"]:
            st.markdown(content)

    if sections.get("EVIDENCE"):
        st.markdown("#### 📌 Supporting evidence")

        for content in sections["EVIDENCE"]:
            # Preserve bullets and numbered lists already in the answer.
            lines = [
                line.strip()
                for line in content.splitlines()
                if line.strip()
            ]

            if len(lines) > 1:
                for line in lines:
                    st.markdown(line)
            else:
                st.markdown(content)

    if sections.get("RECOMMENDED ACTION"):
        st.markdown("#### 💡 Recommended action")

        for content in sections["RECOMMENDED ACTION"]:
            with st.container(border=True):
                st.markdown(content)

    if sections.get("REASON"):
        st.markdown("#### 📝 Why this matters")
        for content in sections["REASON"]:
            st.markdown(content)


def _render_explore_further():
    """Show suggested follow-up questions below the answer."""
    st.markdown("#### 🔎 Explore Further")

    suggestions = [
        "What exceptions apply to this policy?",
        "How can we improve checkout communication?",
    ]

    col1, col2 = st.columns(2)

    with col1:
        st.button(
            suggestions[0],
            key="explore_policy_exceptions",
            use_container_width=True,
            on_click=set_knowledge_query,
            args=(suggestions[0],),
        )

    with col2:
        st.button(
            suggestions[1],
            key="explore_checkout_communication",
            use_container_width=True,
            on_click=set_knowledge_query,
            args=(suggestions[1],),
        )

def _sources_from_result(result):
    """Safely extract RAG source documents."""

    if not isinstance(result, dict):
        return []

    knowledge = result.get("knowledge")

    if isinstance(knowledge, dict):
        sources = knowledge.get("sources")

        if isinstance(sources, list):
            return sources

    for key in ("sources", "documents"):
        sources = result.get(key)

        if isinstance(sources, list):
            return sources

    return []


def _source_record(source):
    """Convert a RAG source into a document-library row."""

    if isinstance(source, str):
        name = source
        page = None
    elif isinstance(source, dict):
        name = (
            source.get("source")
            or source.get("document")
            or source.get("filename")
            or source.get("file_name")
            or source.get("title")
        )
        page = source.get("page")
    else:
        return None

    if not name:
        return None

    from pathlib import Path

    return {
        "Document": str(name),
        "Category": "Company Policies" if "croma" in str(name).lower()
                    or "terms" in str(name).lower()
                    else "Operational Documents",
        "Type": Path(str(name)).suffix.lstrip(".").upper() or "Document",
        "Status": (
            f"Retrieved by RAG · Page {page}"
            if page is not None
            else "Retrieved by RAG"
        ),
    }



def _normalise_rows(payload):
    """Accept common list wrappers from analytics endpoints."""
    if isinstance(payload, list):
        return payload

    if isinstance(payload, dict):
        for key in ("data", "products", "items", "results", "inventory"):
            if isinstance(payload.get(key), list):
                return payload[key]

    return []


def set_knowledge_query(query):
    st.session_state["knowledge_query"] = query
    st.session_state["knowledge_pending_query"] = query


def render_knowledge_assistant():
    """Render the Knowledge Assistant page."""

    # LOAD STYLES
    BASE_DIR = Path(__file__).resolve().parent.parent
    CSS_PATH = BASE_DIR / "assets" / "style.css"

    if CSS_PATH.exists():
        st.markdown(
            f"<style>{CSS_PATH.read_text(encoding='utf-8')}</style>",
            unsafe_allow_html=True,
        )
    
    # INCREASE KNOWLEDGE ASSISTANT TEXT SIZE
    st.markdown(
        """
        <style>
        /* Improve readability of answer text */
        .stMarkdown p {
            font-size: 19px;
            line-height: 1.8;
        }

        .stMarkdown li {
            font-size: 19px;
            line-height: 1.8;
        }

        .stMarkdown h4 {
            font-size: 25px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # SESSION STATE
    if "knowledge_source_records" not in st.session_state:
        st.session_state.knowledge_source_records = {}

    if "knowledge_search_result" not in st.session_state:
        st.session_state.knowledge_search_result = None

    if "knowledge_search_error" not in st.session_state:
        st.session_state.knowledge_search_error = None

    # PAGE HEADER
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

    # DOCUMENTS RETURNED BY RAG
    source_df = pd.DataFrame(
        list(st.session_state.knowledge_source_records.values()),
        columns=["Document", "Category", "Type", "Status"],
    )

    # LIVE BACKEND CHECK
    summary, summary_error = _get_json("/api/analytics/summary")
    inventory_payload, inventory_error = _get_json(
        "/api/analytics/inventory-risk"
    )

    inventory_rows = _normalise_rows(inventory_payload)

    # METRIC CARDS
    a, b, c = st.columns(3)

    metric_values = [
        (
            a,
            "TOTAL DOCUMENTS",
            str(source_df["Document"].nunique())
            if not source_df.empty else "0",
            "Distinct source documents returned by RAG",
        ),
        (
            b,
            "KNOWLEDGE AREAS",
            str(source_df["Category"].nunique())
            if not source_df.empty else "0",
            "Areas represented in retrieved source metadata",
        ),
        (
            c,
            "INDEXING STATUS",
            "Connected"
            if not inventory_error and isinstance(summary, dict)
            else "Unavailable",
            "Live backend connection status; not an index audit",
        ),
    ]

    for col, label, value, note in metric_values:
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

    if summary_error or inventory_error:
        with st.expander("Live data connection details"):
            if summary_error:
                st.warning(f"Analytics summary: {summary_error}")
            if inventory_error:
                st.warning(f"Inventory analytics: {inventory_error}")

    # KNOWLEDGE SEARCH
    st.markdown("## Search company knowledge")

    if "knowledge_query" not in st.session_state:
        st.session_state.knowledge_query = ""

    with st.form("knowledge_search"):
        query = st.text_input(
            "Ask a question or enter a keyword",
            key="knowledge_query",
            placeholder="e.g. Can I cancel my order after dispatch?",
        )

        submitted = st.form_submit_button(
            "Search knowledge",
            type="primary",
        )

    # QUICK SEARCH BUTTONS
    # QUICK SEARCH BUTTONS
    quick_cols = st.columns(4)

    quick_queries = [
        "Return policy",
        "Order cancellation",
        "Shipping policy",
        "Warranty policy",
    ]

    for i, item in enumerate(quick_queries):
        with quick_cols[i]:
            st.button(
                item,
                key=f"knowledge_quick_{i}",
                use_container_width=True,
                on_click=set_knowledge_query,
                args=(item,),
            )

    # PROCESS QUICK SEARCH OR FORM SUBMISSION
    pending_query = st.session_state.pop(
        "knowledge_pending_query", None
    )

    question_to_ask = pending_query or (
        query.strip() if submitted else ""
    )

    # CALL THE EXISTING RAG BACKEND
    if question_to_ask:
        with st.spinner("Searching the RAG knowledge base..."):
            result, error = _ask_rag(question_to_ask)

        st.session_state.knowledge_search_result = result
        st.session_state.knowledge_search_error = error

        if result:
            for source in _sources_from_result(result):
                record = _source_record(source)

                if record:
                    st.session_state.knowledge_source_records[
                        record["Document"]
                    ] = record

            source_df = pd.DataFrame(
                list(st.session_state.knowledge_source_records.values()),
                columns=["Document", "Category", "Type", "Status"],
            )

    
    # DISPLAY SEARCH RESPONSE
    result = st.session_state.knowledge_search_result
    error = st.session_state.knowledge_search_error

    if error:
        st.markdown("### Search response")
        st.error(error)

    elif result:
        answer = _answer_from_result(result)

        st.markdown("### Search response")

        if answer:
            _render_formatted_answer(answer)
            _render_explore_further()
        else:
            st.warning(
                "The agent returned a response, but no answer field "
                "was found. Check the JSON returned by ask_agent() "
                "in ai/agent.py."
            )

        route = result.get("route")

        if route:
            st.caption(f"Response route: {route}")

        sources = _sources_from_result(result)

        if sources:
            st.markdown("#### Sources")

            unique_sources = []
            seen_sources = set()

            for source in sources:
                if isinstance(source, str):
                    name = source
                    page = None

                elif isinstance(source, dict):
                    name = (
                        source.get("source")
                        or source.get("document")
                        or source.get("filename")
                        or source.get("file_name")
                        or source.get("title")
                        or "Unknown source"
                    )

                    page = (
                        source.get("page")
                        or source.get("page_number")
                        or source.get("page_num")
                    )
                else:
                    continue

                key = (str(name).strip(), str(page))

                if key not in seen_sources:
                    seen_sources.add(key)
                    unique_sources.append((name, page))

            for index, (name, page) in enumerate(
                unique_sources, start=1
            ):
                label = f"{index}. {name}"

                if page is not None:
                    label += f" — page {page}"

                st.markdown(f"- {label}")

    # DOCUMENT LIBRARY
    st.markdown("## Document library")

    f1, f2, f3 = st.columns([2, 1.5, 1])

    with f1:
        search = st.text_input(
            "Search documents",
            placeholder="Name, category, or type",
            key="knowledge_document_search",
        )

    if source_df.empty:
        categories = []
        statuses = []
    else:
        categories = sorted(
            source_df["Category"].dropna().unique().tolist()
        )
        statuses = sorted(
            source_df["Status"].dropna().unique().tolist()
        )

    with f2:
        category = st.selectbox(
            "Category",
            ["All categories"] + categories,
            key="knowledge_category",
        )

    with f3:
        status = st.selectbox(
            "Status",
            ["All statuses"] + statuses,
            key="knowledge_status",
        )

    filtered = source_df.copy()

    if not filtered.empty and search.strip():
        term = search.strip()

        filtered = filtered[
            filtered["Document"].str.contains(
                term, case=False, na=False
            )
            | filtered["Category"].str.contains(
                term, case=False, na=False
            )
            | filtered["Type"].str.contains(
                term, case=False, na=False
            )
        ]

    if not filtered.empty and category != "All categories":
        filtered = filtered[filtered["Category"] == category]

    if not filtered.empty and status != "All statuses":
        filtered = filtered[filtered["Status"] == status]

    st.caption(
        f"Showing {len(filtered)} of {len(source_df)} "
        "source documents returned by RAG searches"
    )

    if source_df.empty:
        st.info(
            "No RAG source documents have been returned yet. Search for "
            "a policy above to populate this table with the actual source "
            "documents returned by your backend. This page does not "
            "invent a document list."
        )

        st.dataframe(
            pd.DataFrame(
                columns=["Document", "Category", "Type", "Status"]
            ),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.dataframe(
            filtered,
            use_container_width=True,
            hide_index=True,
        )
