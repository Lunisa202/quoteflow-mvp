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
        st.error("⚠️ No se puede conectar a la API. Asegúrese de que el backend esté corriendo.")
        return None
    except Exception as e:
        st.error(f"Error de API: {e}")
        return None


def api_post(endpoint: str, data: dict):
    """Make POST request to API."""
    try:
        response = requests.post(f"{API_URL}{endpoint}", json=data, timeout=60)
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error("⚠️ No se puede conectar a la API. Asegúrese de que el backend esté corriendo.")
        return None
    except Exception as e:
        st.error(f"Error de API: {e}")
        return None


# --- Sidebar Navigation ---

# Status translation map
STATUS_LABELS = {
    "completed": "Completada",
    "needs_approval": "Pendiente de Aprobación",
    "needs_clarification": "Requiere Aclaración",
    "blocked": "Bloqueada",
    "processing": "Procesando",
    "rejected": "Rechazada",
    "approved": "Aprobada",
    "error": "Error",
}


def translate_status(status: str) -> str:
    """Translate status code to Spanish label."""
    return STATUS_LABELS.get(status, status)


st.sidebar.title("📋 QuoteFlow")
st.sidebar.markdown("**AndesPro Industrial**")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navegación",
    ["📝 New Request", "📊 Dashboard", "🔍 Quote Details"],
    index=["📝 New Request", "📊 Dashboard", "🔍 Quote Details"].index(
        st.session_state.get("page", "📝 New Request")
    ),
    key="nav_radio",
)
# Sync page state
st.session_state["page"] = page


# --- Page: New Request ---

if page == "📝 New Request":
    st.title("📝 Nueva Solicitud de Cotización")
    st.markdown("Envíe una solicitud de cotización en lenguaje natural.")

    with st.form("quote_form"):
        col1, col2 = st.columns([1, 2])

        with col1:
            client_id = st.selectbox(
                "Cliente",
                ["CLI-001 (Minera del Sur - Gold)",
                 "CLI-002 (Constructora Andes - Silver)",
                 "CLI-003 (Petroleos del Norte - Platinum)",
                 "CLI-004 (Transportes Huancayo - Standard)",
                 "Otro (cliente nuevo o desconocido)"],
                help="Seleccione el cliente o ingrese uno nuevo",
            )
            # Extract just the ID
            if "Otro" in client_id:
                client_id = st.text_input(
                    "Ingrese identificador del cliente",
                    placeholder="Ej: CLI-005, nombre de empresa, etc.",
                )
            else:
                client_id = client_id.split(" ")[0]

        with col2:
            raw_text = st.text_area(
                "Solicitud (lenguaje natural)",
                height=150,
                placeholder="Ej: Necesito 20 cascos modelo HX-200 para la planta de Arequipa. Somos clientes Gold. Requiero entrega la próxima semana y un 8% de descuento.",
            )

        submitted = st.form_submit_button("🚀 Enviar Solicitud", use_container_width=True)

        if submitted:
            if not client_id or not raw_text:
                st.warning("Por favor complete el cliente y el texto de la solicitud.")
            else:
                with st.spinner("Procesando solicitud de cotización..."):
                    result = api_post("/quotes", {
                        "client_id": client_id,
                        "raw_text": raw_text,
                    })

                if result and result.get("success"):
                    data = result["data"]
                    status = data.get("status", "unknown")

                    if status == "completed":
                        st.success("✅ Cotización completada!")
                    elif status == "needs_approval":
                        st.warning("⏸️ La cotización requiere aprobación humana.")
                    elif status == "needs_clarification":
                        st.info("❓ Se necesita información adicional.")
                    elif status == "blocked":
                        st.error("🚫 Cotización bloqueada.")
                    elif status == "error":
                        st.error(f"💥 Error: {data.get('error', 'Error desconocido')}")
                    else:
                        st.info(f"Estado: {status}")

                    # Show formatted results
                    st.markdown(f"**ID de cotización:** `{data.get('quote_id', 'N/A')}`")

                    # Extracted data
                    extracted = data.get("extracted_data")
                    if extracted:
                        st.markdown("#### 📋 Datos Extraídos")
                        items = extracted.get("items", [])
                        if items:
                            for item in items:
                                st.markdown(
                                    f"- **{item.get('product_name', 'N/A')}** "
                                    f"(SKU: {item.get('sku', 'N/A')}) — "
                                    f"Cantidad: {item.get('quantity', 0)}, "
                                    f"Descuento solicitado: {item.get('requested_discount_pct', 0)}%"
                                )
                        if extracted.get("delivery_location"):
                            st.markdown(f"- **Ubicación de entrega:** {extracted['delivery_location']}")
                        if extracted.get("delivery_date"):
                            st.markdown(f"- **Fecha de entrega:** {extracted['delivery_date']}")

                    # Quotation
                    quotation = data.get("quotation")
                    if quotation and "lines" in quotation:
                        st.markdown("#### 💰 Cotización Calculada")
                        for line in quotation["lines"]:
                            st.markdown(
                                f"- {line.get('product_name', 'N/A')}: "
                                f"{line.get('quantity', 0)} × USD {line.get('unit_price', 0):.2f} "
                                f"= USD {line.get('subtotal', 0):.2f} "
                                f"(descuento {line.get('discount_pct', 0)}%: -USD {line.get('discount_amount', 0):.2f}) "
                                f"→ **USD {line.get('line_total', 0):.2f}**"
                            )
                        st.markdown(f"**Total: USD {quotation.get('grand_total', 0):,.2f}**")

                    # Clarification message
                    if data.get("clarification_message"):
                        st.markdown("#### ❓ Información Requerida")
                        st.warning(data["clarification_message"])

                    # Draft
                    if data.get("draft"):
                        st.markdown("#### 📝 Borrador de Cotización")
                        st.markdown(data["draft"])

                    # Show raw JSON in expander for technical review
                    with st.expander("🔧 Ver respuesta completa (JSON)"):
                        st.json(data)

                elif result:
                    st.error(f"Error: {result.get('error', {}).get('message', 'Error desconocido')}")

    # Example requests
    st.markdown("---")
    st.markdown("### 💡 Solicitudes de Ejemplo")

    examples = [
        {
            "title": "Cotización Estándar (Cliente Gold)",
            "client": "CLI-001",
            "text": "Necesito 20 cascos modelo HX-200 para la planta de Arequipa. Somos clientes Gold. Requiero entrega la próxima semana y un 8% de descuento.",
        },
        {
            "title": "Cotización de Alto Valor (Requiere Aprobación)",
            "client": "CLI-003",
            "text": "Necesito 5 máquinas de soldar WL-100 y 3 compresores CP-750 para nuestra planta de Piura. Solicitamos 12% de descuento sobre el total.",
        },
        {
            "title": "Solicitud Incompleta (Requiere Aclaración)",
            "client": "CLI-002",
            "text": "Necesito equipos de seguridad para nuestro nuevo proyecto.",
        },
    ]

    for ex in examples:
        with st.expander(ex["title"]):
            st.code(f"Cliente: {ex['client']}\n{ex['text']}")


# --- Page: Dashboard ---

elif page == "📊 Dashboard":
    st.title("📊 Panel de Cotizaciones")

    if st.button("🔄 Actualizar"):
        st.rerun()

    result = api_get("/quotes")

    if result and result.get("success"):
        quotes = result["data"]

        if not quotes:
            st.info("No hay solicitudes de cotización aún. Cree una desde la barra lateral.")
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
                    st.metric(f"{icon} {translate_status(status)}", count)

            st.markdown("---")

            # Quotes table
            for q in quotes:
                status = q.get("status", "unknown")
                icon = status_colors.get(status, "⚪")
                with st.expander(f"{icon} [{q['id'][:8]}...] {q.get('client_id', 'N/A')} - {translate_status(status)}"):
                    st.markdown(f"**Creado:** {q.get('created_at', 'N/A')}")
                    st.markdown(f"**Solicitud:** {q.get('raw_text', 'N/A')}")
                    st.markdown(f"**Estado:** `{translate_status(status)}`")

                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Ver Detalles", key=f"view_{q['id']}"):
                            st.session_state["selected_quote"] = q["id"]
                            st.session_state["page"] = "🔍 Quote Details"
                            st.rerun()
    else:
        st.warning("No se pudo cargar las cotizaciones. ¿Está corriendo la API?")


# --- Page: Quote Details ---

elif page == "🔍 Quote Details":
    st.title("🔍 Detalle de Cotización")

    quote_id = st.text_input(
        "ID de Cotización",
        value=st.session_state.get("selected_quote", ""),
        placeholder="Ingrese el ID de la cotización...",
    )

    if quote_id:
        result = api_get(f"/quotes/{quote_id}")

        if result and result.get("success"):
            quote = result["data"]

            # Status header
            status = quote.get("status", "unknown")
            st.markdown(f"### Estado: `{translate_status(status)}`")

            # Tabs for different views
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "📄 Solicitud", "🔬 Datos Extraídos", "💰 Cotización", "✅ Aprobación", "📜 Historial"
            ])

            with tab1:
                st.markdown(f"**Cliente:** {quote.get('client_id')}")
                st.markdown(f"**Solicitud original:**")
                st.info(quote.get("raw_text", "N/A"))
                st.markdown(f"**Creado:** {quote.get('created_at')}")

            with tab2:
                extracted = quote.get("extracted_data")
                if extracted:
                    st.json(extracted)
                else:
                    st.info("Sin datos extraídos aún.")

            with tab3:
                quotation = quote.get("quotation")
                if quotation:
                    if "lines" in quotation:
                        for line in quotation["lines"]:
                            st.markdown(
                                f"- **{line.get('product_name', 'N/A')}**: "
                                f"{line.get('quantity', 0)} × USD {line.get('unit_price', 0):.2f} "
                                f"= USD {line.get('line_total', 0):.2f} "
                                f"(descuento: {line.get('discount_pct', 0)}%)"
                            )
                        st.markdown(f"### Total: USD {quotation.get('grand_total', 0):,.2f}")
                    else:
                        st.json(quotation)
                else:
                    st.info("Cotización aún no calculada.")

                if quote.get("draft"):
                    st.markdown("---")
                    st.markdown("### 📝 Borrador de Respuesta")
                    st.markdown(quote["draft"])

            with tab4:
                if status == "needs_approval":
                    st.warning("⏸️ Esta cotización requiere aprobación humana.")

                    validation = quote.get("validation_result", {})
                    reasons = validation.get("approval_reasons", [])
                    if reasons:
                        st.markdown("**Razones de aprobación:**")
                        for r in reasons:
                            st.markdown(f"- {r}")

                    st.markdown("---")

                    col1, col2 = st.columns(2)
                    notes = st.text_input("Notas (opcional)")

                    with col1:
                        if st.button("✅ Aprobar", use_container_width=True, type="primary"):
                            with st.spinner("Procesando aprobación..."):
                                res = api_post(f"/quotes/{quote_id}/approve", {
                                    "action": "approve",
                                    "notes": notes,
                                })
                            if res and res.get("success"):
                                st.success("¡Cotización aprobada! Borrador generado.")
                                st.rerun()
                            else:
                                st.error("Error al aprobar.")

                    with col2:
                        if st.button("❌ Rechazar", use_container_width=True):
                            with st.spinner("Procesando rechazo..."):
                                res = api_post(f"/quotes/{quote_id}/approve", {
                                    "action": "reject",
                                    "notes": notes,
                                })
                            if res and res.get("success"):
                                st.info("Cotización rechazada.")
                                st.rerun()
                            else:
                                st.error("Error al rechazar.")

                elif quote.get("approval"):
                    st.json(quote["approval"])
                else:
                    st.info("Sin acciones de aprobación.")

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
                        st.info("Sin historial aún.")
        elif result:
            st.error(result.get("error", {}).get("message", "Cotización no encontrada"))
        else:
            st.info("Ingrese un ID de cotización para ver detalles.")
