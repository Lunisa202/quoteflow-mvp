# Fase 01 — Vertical Principal

## Objetivo

Entregar una vertical funcional: una solicitud de cotización fluye desde texto natural a través de extracción, validación, cálculo, y opcionalmente aprobación, hasta un borrador generado. Toda la lógica de negocio es determinista y testeable.

## Tareas

### 1. Estructura del Proyecto
- **Archivos:** `pyproject.toml`, `.env.example`, `.gitignore`, estructura de carpetas
- **DoD:** `pip install -e .` funciona, todos los imports resuelven

### 2. Datos de Dominio y Servicios
- **Archivos:** `backend/domain/data.py`, `backend/domain/services.py`
- **DoD:** `pytest tests/test_domain_services.py` todo en verde

### 3. Estado del Workflow
- **Archivos:** `backend/workflow/state.py`
- **DoD:** TypedDict compila, todos los campos documentados

### 4. Nodos del Workflow
- **Archivos:** `backend/workflow/nodes.py`
- **DoD:** Cada nodo maneja una sola responsabilidad, extracción/borrador usan LLM, el resto es determinista

### 5. Definición del Grafo
- **Archivos:** `backend/workflow/graph.py`
- **DoD:** El grafo compila, tests de routing pasan, interrupt configurado

### 6. Motor del Workflow
- **Archivos:** `backend/workflow/engine.py`
- **DoD:** `run_quote_workflow` y `resume_quote_workflow` ejecutan correctamente

### 7. Endpoints de la API
- **Archivos:** `backend/api/endpoints/quotes.py`, `backend/api/errors.py`
- **DoD:** Todos los endpoints retornan formato uniforme, errores capturados

### 8. Frontend Streamlit
- **Archivos:** `frontend/app.py`
- **DoD:** Crear, listar, inspeccionar, aprobar, ver borrador — todo funcional

### 9. Pruebas
- **Archivos:** `tests/test_domain_services.py`, `tests/test_workflow_routing.py`, `tests/test_idempotency.py`
- **DoD:** Todo en verde con `pytest tests/ -v`

### 10. Documentación
- **Archivos:** `docs/BUSINESS_CASE.md`, `docs/PROJECT.md`, `docs/REQUIREMENTS.md`, etc.
- **DoD:** Todos los docs requeridos presentes y reflejan el código actual
