# Casos de Prueba Funcionales

## Resumen

Estos son los casos de prueba end-to-end que demuestran el correcto funcionamiento de QuoteFlow. Se ejecutan desde la interfaz de Streamlit con el backend corriendo.

---

## Caso 1: Cotización Estándar (Flujo Completo)

**Objetivo:** Demostrar que una solicitud completa y dentro de política genera un borrador automáticamente.

| Campo | Valor |
|-------|-------|
| **Cliente** | CLI-001 (Minera del Sur - Gold) |
| **Solicitud** | "Necesito 20 cascos modelo HX-200 para la planta de Arequipa. Requiero entrega la próxima semana y un 8% de descuento." |

**Resultado Esperado:**
- Estado: `Completada`
- Datos extraídos: SKU HX-200, cantidad 20, descuento 8%, ubicación Arequipa
- Validación: cliente conocido ✅, producto conocido ✅, stock disponible ✅, descuento permitido ✅
- Cálculo: 20 × USD 45.00 = USD 900.00, descuento 8% = -USD 72.00, **Total: USD 828.00**
- Borrador de cotización generado en español
- No requiere aprobación (total < USD 10,000 y descuento dentro de auto-approve para Gold)

**Ruta del grafo:** `START → Extraction → Validation → Calculation → Draft → END`

---

## Caso 2: Solicitud Incompleta (Requiere Aclaración)

**Objetivo:** Demostrar que el sistema detecta información faltante y solicita aclaración.

| Campo | Valor |
|-------|-------|
| **Cliente** | CLI-002 (Constructora Andes - Silver) |
| **Solicitud** | "Necesito equipos de seguridad para nuestro nuevo proyecto." |

**Resultado Esperado:**
- Estado: `Requiere Aclaración`
- El LLM identifica que faltan: producto específico, cantidad, ubicación de entrega
- Se genera un mensaje indicando qué información se necesita
- No se genera cotización ni borrador

**Ruta del grafo:** `START → Extraction → Validation → Clarification → END`

---

## Caso 3: Cotización de Alto Valor (Requiere Aprobación)

**Objetivo:** Demostrar el flujo de human-in-the-loop con interrupt y reanudación.

| Campo | Valor |
|-------|-------|
| **Cliente** | CLI-003 (Petroleos del Norte - Platinum) |
| **Solicitud** | "Necesito 5 máquinas de soldar WL-100 y 3 compresores CP-750 para nuestra planta de Piura. Solicitamos 12% de descuento sobre el total." |

**Resultado Esperado (Paso 1 - Envío):**
- Estado: `Pendiente de Aprobación`
- Cálculo estimado: 5 × USD 2,500 + 3 × USD 1,800 = USD 17,900 (antes de descuento)
- Razones de aprobación: Total > USD 10,000
- El workflow se PAUSA aquí (interrupt)

**Resultado Esperado (Paso 2a - Si se Aprueba):**
- Estado cambia a: `Completada`
- Se genera borrador de cotización con el descuento aplicado
- Se registra en historial quién aprobó y cuándo

**Resultado Esperado (Paso 2b - Si se Rechaza):**
- Estado cambia a: `Rechazada`
- No se genera borrador
- Se registra el rechazo con las notas del revisor

**Ruta del grafo:** `START → Extraction → Validation → Calculation → Approval (INTERRUPT) → Post-Approval → Draft → END`

---

## Caso 4: Cliente Desconocido

**Objetivo:** Demostrar que un cliente no registrado se detecta y se solicita revisión.

| Campo | Valor |
|-------|-------|
| **Cliente** | CLI-999 (o cualquier ID no existente) |
| **Solicitud** | "Quiero cotizar 50 guantes GL-300 con entrega en Cusco." |

**Resultado Esperado:**
- Estado: `Requiere Aclaración`
- El sistema detecta que CLI-999 no existe
- Se indica que el cliente es desconocido y requiere revisión

**Ruta del grafo:** `START → Extraction → Validation → Clarification → END`

---

## Caso 5: Stock Insuficiente

**Objetivo:** Demostrar que el sistema bloquea solicitudes cuando no hay stock disponible.

| Campo | Valor |
|-------|-------|
| **Cliente** | CLI-001 (Minera del Sur - Gold) |
| **Solicitud** | "Necesito 200 máquinas de soldar WL-100 para entrega en Arequipa." |

**Resultado Esperado:**
- Estado: `Bloqueada`
- Stock de WL-100 en Arequipa: 5 unidades (necesita 200)
- Se indica el déficit de stock
- No se genera cotización

**Ruta del grafo:** `START → Extraction → Validation → Blocked → END`

---

## Caso 6: Descuento Excede Política

**Objetivo:** Demostrar que descuentos fuera de política se escalan para aprobación.

| Campo | Valor |
|-------|-------|
| **Cliente** | CLI-002 (Constructora Andes - Silver) |
| **Solicitud** | "Necesito 100 cascos HX-200 para Lima con 15% de descuento." |

**Resultado Esperado:**
- Estado: `Pendiente de Aprobación`
- Silver permite máximo 7% de descuento, se solicita 15%
- Se indica que el descuento excede la política
- Requiere aprobación humana para proceder

**Ruta del grafo:** `START → Extraction → Validation → Calculation → Approval (INTERRUPT)`

---

## Caso 7: Reanudación Durable (Reinicio de Aplicación)

**Objetivo:** Demostrar que una cotización pausada se puede reanudar después de reiniciar la app.

**Pasos:**
1. Enviar el Caso 3 (alto valor) → queda en "Pendiente de Aprobación"
2. Detener el backend (Ctrl+C)
3. Reiniciar el backend (`uvicorn backend.main:app --reload --port 8000`)
4. Ir a la página de detalles con el ID de la cotización
5. Aprobar la cotización

**Resultado Esperado:**
- La cotización sigue visible en el dashboard con estado "Pendiente de Aprobación"
- Al aprobar, se genera el borrador correctamente

**Nota:** Con MemorySaver el estado del grafo se pierde al reiniciar (es una limitación del MVP documentada). Los datos de la cotización sí persisten en `data/quotes.json`.

---

## Matriz de Cobertura

| Caso | Flujo Estándar | Info Faltante | Aprobación | Stock | Cliente Desconocido | Descuento | Reinicio |
|------|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| 1 | ✅ | | | | | | |
| 2 | | ✅ | | | | | |
| 3 | | | ✅ | | | | |
| 4 | | | | | ✅ | | |
| 5 | | | | ✅ | | | |
| 6 | | | | | | ✅ | |
| 7 | | | ✅ | | | | ✅ |
