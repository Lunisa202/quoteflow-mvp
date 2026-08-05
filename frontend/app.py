"""QuoteFlow - Streamlit Frontend Application."""

import streamlit as st
import requests
from datetime import datetime

# Configuration
API_URL = "http://localhost:8000/api/v1"

st.set_page_config(
    page_title="QuoteFlow - AndesPro Industrial",
    page_icon="📋",
    layout="wide",
)


# --- API Helpers ---

def api_get(endpoint: str):
    """Make GET request to API."""
    try:
        response = requests.get(f"{API_URL}{endpoint}", timeout=30)
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error("⚠️ Cannot connect to API. Make sure the backend is running.")
        return None
    except Exception as e:
        st.error(f"API Error: {e}")
        return None


def api_post(endpoint: str, data: dict):
    """Make POST request to API."""
    try:
        response = requests.post(f"{API_URL}{endpoint}", json=data, timeout=60)
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error("⚠️ Cannot connect to API. Make sure the backend is running.")
        return None
    except Exception as e:
        st.error(f"API Error: {e}")
        return None


# --- Sidebar Navigation ---

st.sidebar.title("📋 QuoteFlow")
st.sidebar.markdown("**AndesPro Industrial**")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    ["📝 New Request", "📊 Dashboard", "🔍 Quote Details"],
)


# --- Page: New Request ---

if page == "📝 New Request":
    st.title("📝 New Quotation Request")
    st.markdown("Submit a quotation request in natural language.")

    with st.form("quote_form"):
        col1, col2 = st.columns([1, 2])

        with col1:
            client_id = st.selectbox(
                "Client ID",
                ["CLI-001", "CLI-002", "CLI-003", "CLI-004", "OTHER"],
                help="Select the client identifier",
            )
            if client_id == "OTHER":
                client_id = st.text_input("Enter Client ID")

        with col2:
            raw_text = st.text_area(
                "Request (natural language)",
                height=150,
                placeholder="e.g., I need 20 HX-200 helmets for our Arequipa plant. We're Gold clients. Need delivery next week with 8% discount.",
            )

        submitted = st.form_submit_button("🚀 Submit Request", use_container_width=True)

        if submitted:
            if not client_id or not raw_text:
                st.warning("Please fill in both client ID and request text.")
            else:
                with st.spinner("Processing quotation request..."):
                    result = api_post("/quotes", {
                        "client_id": client_id,
                        "raw_text": raw_text,
                    })

                if result and result.get("success"):
                    data = result["data"]
                    status = data.get("status", "unknown")

                    if status == "completed":
                        st.success("✅ Quotation completed!")
                    elif status == "needs_approval":
                        st.warning("⏸️ Quotation requires human approval.")
                    elif status == "needs_clarification":
                        st.info("❓ Additional information needed.")
                    elif status == "blocked":
                        st.error("🚫 Quote blocked.")
                    else:
                        st.info(f"Status: {status}")

                    st.json(data)
                elif result:
                    st.error(f"Error: {result.get('error', {}).get('message', 'Unknown error')}")

    # Example requests
    st.markdown("---")
    st.markdown("### 💡 Example Requests")

    examples = [
        {
            "title": "Standard Quote (Gold Client)",
            "client": "CLI-001",
            "text": "Necesito 20 cascos modelo HX-200 para la planta de Arequipa. Somos clientes Gold. Requiero entrega la próxima semana y un 8% de descuento.",
        },
        {
            "title": "High-Value Quote (Needs Approval)",
            "client": "CLI-003",
            "text": "Need 5 WL-100 welding machines and 3 CP-750 compressors for our Piura facility. Requesting 12% discount on the total order.",
        },
        {
            "title": "Incomplete Request (Needs Clarification)",
            "client": "CLI-002",
            "text": "I need some safety equipment for our new project.",
        },
    ]

    for ex in examples:
        with st.expander(ex["title"]):
            st.code(f"Client: {ex['client']}\n{ex['text']}")


# --- Page: Dashboard ---

elif page == "📊 Dashboard":
    st.title("📊 Quotation Dashboard")

    if st.button("🔄 Refresh"):
        st.rerun()

    result = api_get("/quotes")

    if result and result.get("success"):
        quotes = result["data"]

        if not quotes:
            st.info("No quotation requests yet. Create one from the sidebar.")
        else:
            # Status summary
            statuses = {}
            for q in quotes:
                s = q.get("status", "unknown")
                statuses[s] = statuses.get(s, 0) + 1

            cols = st.columns(len(statuses))
            status_colors = {
                "completed": "🟢",
                "needs_approval": "🟡",
                "needs_clarification": "🔵",
                "blocked": "🔴",
                "processing": "⏳",
                "rejected": "❌",
                "error": "💥",
            }
            for i, (status, count) in enumerate(statuses.items()):
                with cols[i]:
                    icon = status_colors.get(status, "⚪")
                    st.metric(f"{icon} {status.replace('_', ' ').title()}", count)

            st.markdown("---")

            # Quotes table
            for q in quotes:
                status = q.get("status", "unknown")
                icon = status_colors.get(status, "⚪")
                with st.expander(f"{icon} [{q['id'][:8]}...] {q.get('client_id', 'N/A')} - {status}"):
                    st.markdown(f"**Created:** {q.get('created_at', 'N/A')}")
                    st.markdown(f"**Request:** {q.get('raw_text', 'N/A')}")
                    st.markdown(f"**Status:** `{status}`")

                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("View Details", key=f"view_{q['id']}"):
                            st.session_state["selected_quote"] = q["id"]
                            st.rerun()
    else:
        st.warning("Could not load quotes. Is the API running?")


# --- Page: Quote Details ---

elif page == "🔍 Quote Details":
    st.title("🔍 Quote Details")

    quote_id = st.text_input(
        "Quote ID",
        value=st.session_state.get("selected_quote", ""),
        placeholder="Enter quote ID...",
    )

    if quote_id:
        result = api_get(f"/quotes/{quote_id}")

        if result and result.get("success"):
            quote = result["data"]

            # Status header
            status = quote.get("status", "unknown")
            st.markdown(f"### Status: `{status}`")

            # Tabs for different views
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "📄 Request", "🔬 Extracted Data", "💰 Quotation", "✅ Approval", "📜 History"
            ])

            with tab1:
                st.markdown(f"**Client ID:** {quote.get('client_id')}")
                st.markdown(f"**Raw Request:**")
                st.info(quote.get("raw_text", "N/A"))
                st.markdown(f"**Created:** {quote.get('created_at')}")

            with tab2:
                extracted = quote.get("extracted_data")
                if extracted:
                    st.json(extracted)
                else:
                    st.info("No extracted data yet.")

            with tab3:
                quotation = quote.get("quotation")
                if quotation:
                    st.json(quotation)
                else:
                    st.info("No quotation calculated yet.")

                if quote.get("draft"):
                    st.markdown("---")
                    st.markdown("### 📝 Draft Response")
                    st.markdown(quote["draft"])

            with tab4:
                if status == "needs_approval":
                    st.warning("⏸️ This quote requires human approval.")

                    validation = quote.get("validation_result", {})
                    reasons = validation.get("approval_reasons", [])
                    if reasons:
                        st.markdown("**Reasons for approval:**")
                        for r in reasons:
                            st.markdown(f"- {r}")

                    st.markdown("---")

                    col1, col2 = st.columns(2)
                    notes = st.text_input("Notes (optional)")

                    with col1:
                        if st.button("✅ Approve", use_container_width=True, type="primary"):
                            with st.spinner("Processing approval..."):
                                res = api_post(f"/quotes/{quote_id}/approve", {
                                    "action": "approve",
                                    "notes": notes,
                                })
                            if res and res.get("success"):
                                st.success("Quote approved! Draft generated.")
                                st.rerun()
                            else:
                                st.error("Failed to approve.")

                    with col2:
                        if st.button("❌ Reject", use_container_width=True):
                            with st.spinner("Processing rejection..."):
                                res = api_post(f"/quotes/{quote_id}/approve", {
                                    "action": "reject",
                                    "notes": notes,
                                })
                            if res and res.get("success"):
                                st.info("Quote rejected.")
                                st.rerun()
                            else:
                                st.error("Failed to reject.")

                elif quote.get("approval"):
                    st.json(quote["approval"])
                else:
                    st.info("No approval action taken.")

            with tab5:
                history_result = api_get(f"/quotes/{quote_id}/history")
                if history_result and history_result.get("success"):
                    history = history_result["data"]
                    if history:
                        for event in history:
                            st.markdown(
                                f"**{event.get('timestamp', 'N/A')}** - "
                                f"`{event.get('event', 'N/A')}`"
                            )
                            if event.get("details"):
                                st.json(event["details"])
                    else:
                        st.info("No history yet.")
        elif result:
            st.error(result.get("error", {}).get("message", "Quote not found"))
        else:
            st.info("Enter a quote ID to view details.")
