# Hoja de Ruta

## Fase 01 — Vertical Principal (Actual)

**Meta:** Un flujo completo end-to-end demostrando todas las capacidades.

| Tarea | Módulo | DoD | Estado |
|-------|--------|-----|--------|
| Scaffolding del proyecto | Todos | Estructura creada, deps definidas | ✅ |
| Datos ficticios y funciones de dominio | `backend/domain/` | Tests pasan, sin LLM | ✅ |
| Workflow LangGraph (estado, nodos, routing) | `backend/workflow/` | Grafo compila, enruta correctamente | ✅ |
| Interrupt/resume para aprobación | `backend/workflow/` | Pausa y reanuda tras reinicio | ✅ |
| Endpoints FastAPI | `backend/api/` | Respuestas uniformes, manejo de errores | ✅ |
| Frontend Streamlit | `frontend/` | Las 5 vistas funcionales | ✅ |
| Tests unitarios (dominio) | `tests/` | Todos verdes, sin LLM | ✅ |
| Tests integración (routing) | `tests/` | Rutas verificadas con estado mock | ✅ |
| Documentación | `docs/` | Todos los docs requeridos presentes | ✅ |

## Fase 02 — Endurecimiento (Futuro)

- Lógica de reintentos para fallas del LLM
- Sanitización de entrada (defensa contra inyección de prompt)
- Rate limiting
- SQLAlchemy para datos de aplicación
- Containerización con Docker
- Pipeline CI/CD

## Fase 03 — Extensiones (Futuro)

- Cotizaciones multi-producto con items complejos
- Integración de email para recepción de solicitudes
- Generación de PDF de cotización
- Sincronización de stock en tiempo real vía webhook
- Dashboard administrativo con analytics
