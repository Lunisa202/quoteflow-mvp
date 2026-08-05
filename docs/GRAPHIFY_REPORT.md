# Reporte Graphify — Mapa de Código

## Visión General del Proyecto

```mermaid
graph TD
    subgraph Frontend
        APP[frontend/app.py<br>Streamlit UI]
    end

    subgraph API["Backend - API Layer"]
        MAIN[backend/main.py<br>FastAPI App]
        ROUTES[backend/api/routes.py]
        ENDPOINTS[backend/api/endpoints/quotes.py]
        ERRORS[backend/api/errors.py]
    end

    subgraph Workflow["Backend - Workflow Layer"]
        ENGINE[backend/workflow/engine.py<br>Orquestador]
        GRAPH[backend/workflow/graph.py<br>Definición del Grafo]
        NODES[backend/workflow/nodes.py<br>Nodos]
        STATE[backend/workflow/state.py<br>Estado Tipado]
    end

    subgraph Domain["Backend - Domain Layer"]
        SERVICES[backend/domain/services.py<br>Lógica Determinista]
        DATA[backend/domain/data.py<br>Datos de Referencia]
    end

    subgraph Storage["Persistencia"]
        QUOTES_SVC[backend/services/quote_service.py]
        JSON_FILE[(data/quotes.json)]
        SQLITE[(data/checkpoints.db)]
    end

    APP -->|HTTP| MAIN
    MAIN --> ROUTES
    ROUTES --> ENDPOINTS
    ENDPOINTS --> ERRORS
    ENDPOINTS --> ENGINE
    ENDPOINTS --> QUOTES_SVC
    ENGINE --> GRAPH
    GRAPH --> NODES
    GRAPH --> STATE
    NODES --> SERVICES
    NODES --> QUOTES_SVC
    SERVICES --> DATA
    QUOTES_SVC --> JSON_FILE
    ENGINE --> SQLITE
```

## Dependencias entre Módulos

| Módulo | Depende de | Es usado por |
|--------|-----------|--------------|
| `domain/data.py` | (ninguno) | `domain/services.py` |
| `domain/services.py` | `domain/data.py` | `workflow/nodes.py` |
| `workflow/state.py` | (ninguno) | `workflow/graph.py`, `workflow/engine.py` |
| `workflow/nodes.py` | `domain/services.py`, `services/quote_service.py` | `workflow/graph.py` |
| `workflow/graph.py` | `workflow/nodes.py`, `workflow/state.py` | `workflow/engine.py` |
| `workflow/engine.py` | `workflow/graph.py`, `services/quote_service.py` | `api/endpoints/quotes.py` |
| `services/quote_service.py` | `config.py` | `workflow/nodes.py`, `api/endpoints/quotes.py` |
| `api/endpoints/quotes.py` | `workflow/engine.py`, `services/quote_service.py`, `api/errors.py` | `api/routes.py` |
| `api/errors.py` | (ninguno) | `api/endpoints/quotes.py`, `main.py` |
| `main.py` | `api/routes.py`, `api/errors.py` | (entry point) |
| `frontend/app.py` | (solo HTTP a API) | (entry point) |

## Capas de Abstracción

```
┌─────────────────────────────────────────────┐
│            Frontend (Streamlit)              │  ← Solo UI, sin lógica
├─────────────────────────────────────────────┤
│            API (FastAPI)                     │  ← HTTP, validación de input
├─────────────────────────────────────────────┤
│            Workflow (LangGraph)              │  ← Orquestación, estado, routing
├─────────────────────────────────────────────┤
│            Domain (Servicios puros)          │  ← Reglas de negocio, cálculos
├─────────────────────────────────────────────┤
│            Data (Referencia estática)        │  ← Fuente de verdad
└─────────────────────────────────────────────┘
```

## Flujo de Datos por Caso de Uso

### Caso 1: Solicitud Estándar

```mermaid
sequenceDiagram
    participant U as Usuario
    participant F as Frontend
    participant A as API
    participant W as Workflow
    participant D as Domain
    participant S as Storage

    U->>F: Envía solicitud
    F->>A: POST /api/v1/quotes
    A->>S: Crea registro
    A->>W: run_quote_workflow()
    W->>W: Extraction (LLM)
    W->>D: Validation (check client, stock, policy)
    D-->>W: Resultado validación
    W->>D: Calculation (precios, descuentos)
    D-->>W: Totales calculados
    W->>W: Draft (LLM)
    W->>S: Guarda resultado
    W-->>A: Estado final
    A-->>F: Response JSON
    F-->>U: Muestra borrador
```

### Caso 2: Requiere Aprobación

```mermaid
sequenceDiagram
    participant U as Usuario
    participant A as API
    participant W as Workflow
    participant CP as Checkpointer

    U->>A: POST /api/v1/quotes
    A->>W: run_quote_workflow()
    W->>W: Extraction → Validation → Calculation
    W->>CP: Guarda estado (INTERRUPT)
    W-->>A: status: "needs_approval"
    A-->>U: Esperando aprobación

    Note over U,CP: Tiempo pasa... incluso puede reiniciar la app

    U->>A: POST /quotes/{id}/approve {action: "approve"}
    A->>W: resume_quote_workflow()
    W->>CP: Carga estado guardado
    W->>W: Post-Approval → Draft (LLM)
    W-->>A: status: "completed"
    A-->>U: Borrador generado
```

## Puntos de Extensión

| Si necesitas... | Modifica... | Sin tocar... |
|-----------------|-------------|--------------|
| Agregar un producto | `domain/data.py` (PRODUCTS, INVENTORY) | Todo lo demás |
| Cambiar política de descuento | `domain/data.py` (DISCOUNT_POLICIES) | Todo lo demás |
| Cambiar umbral de aprobación | `domain/data.py` (APPROVAL_THRESHOLD_USD) | Todo lo demás |
| Agregar un nodo al grafo | `workflow/nodes.py` + `workflow/graph.py` | Domain, API, Frontend |
| Cambiar proveedor LLM | `workflow/engine.py` (1 import + 1 línea) | Todo lo demás |
| Migrar a PostgreSQL | `services/quote_service.py` + `workflow/engine.py` | Domain, Nodes, Frontend |
