# Estado del Proyecto

## Estado Actual: Fase 01 — En desarrollo

**Última actualización:** 2025-08-05

## Resumen

El scaffolding completo está implementado. La estructura de carpetas, datos ficticios, funciones de dominio, workflow LangGraph, API FastAPI, frontend Streamlit y pruebas están creados.

## Módulos Completados

| Módulo | Estado | Notas |
|--------|--------|-------|
| Estructura del proyecto | ✅ Completo | pyproject.toml, .env.example, .gitignore |
| Datos ficticios (domain/data.py) | ✅ Completo | 4 clientes, 6 productos, inventario, políticas |
| Servicios de dominio (domain/services.py) | ✅ Completo | Funciones puras, deterministas |
| Estado del workflow (workflow/state.py) | ✅ Completo | TypedDict con todos los campos |
| Nodos del workflow (workflow/nodes.py) | ✅ Completo | 7 nodos con responsabilidades definidas |
| Grafo (workflow/graph.py) | ✅ Completo | Routing condicional + interrupt |
| Motor (workflow/engine.py) | ✅ Completo | Run + resume con checkpointer |
| API endpoints | ✅ Completo | CRUD + approve + history |
| Frontend Streamlit | ✅ Completo | 3 páginas: crear, dashboard, detalles |
| Tests unitarios | ✅ Completo | Domain services + idempotencia |
| Tests de routing | ✅ Completo | Todas las rutas verificadas |

## Limitaciones Conocidas

- Los datos de aplicación se persisten en JSON (no SQLAlchemy).
- No hay defensa activa contra prompt injection más allá del diseño de prompts.
- La UI de Streamlit es funcional pero no tiene diseño visual elaborado.
- No hay retry logic para fallos del LLM.

## Deuda Técnica Aceptada

1. JSON como store en lugar de DB relacional — aceptable para MVP
2. Sin containerización — el README provee instrucciones manuales
3. Sin CI/CD — las pruebas se ejecutan localmente

## Siguiente Paso

- Ejecutar pruebas para verificar que todo funciona
- Probar el flujo end-to-end con una API key real
- Preparar demo para presentación
