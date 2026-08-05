# AGENTS.md — Instrucciones de Gobierno del Agente

## Contexto del Proyecto

QuoteFlow es un sistema de cotización B2B impulsado por IA para AndesPro Industrial.
El workflow usa LangGraph con estado tipado, enrutamiento condicional e interrupt para human-in-the-loop.

## Estructura del Repositorio

```
backend/           → FastAPI + LangGraph workflow
backend/domain/    → Lógica de negocio determinista (NUNCA usa LLM)
backend/workflow/  → Grafo, nodos, estado, motor
backend/api/       → Endpoints REST
frontend/          → Streamlit
tests/             → Pytest (sin dependencia de LLM)
docs/              → Documentación del reto
data/              → Datos ficticios y persistencia
```

## Reglas para el Agente

### Código
- Todo el código fuente en **inglés** (variables, funciones, comentarios)
- Documentación del proyecto en **español**
- Seguir el formato de respuesta API: `{success, data, error, meta}`
- Las funciones de dominio son **puras y deterministas** — sin side effects
- El LLM solo se usa en nodos de extracción y borrador
- Nunca hardcodear la API key — siempre usar .env

### Workflow
- Cada nodo del grafo tiene **una sola responsabilidad**
- Los nodos deterministas (validation, calculation) **no** llaman al LLM
- El interrupt se usa **solo** para aprobación humana
- El estado es TypedDict — mantener tipado estricto

### Tests
- Los tests deben correr **sin API key de OpenAI**
- Usar datos de `backend/domain/data.py` directamente
- Verificar idempotencia en todas las funciones de dominio
- Tests de routing usan estados mock (no ejecutan el grafo completo)

### Documentación
- Mantener STATE.md actualizado al completar tareas
- Registrar decisiones importantes en ADR
- EVIDENCE.md debe reflejar comandos realmente ejecutados

## Comandos Útiles

```bash
# Instalar dependencias
pip install -e ".[dev]"

# Ejecutar tests
pytest tests/ -v

# Iniciar backend
uvicorn backend.main:app --reload --port 8000

# Iniciar frontend
streamlit run frontend/app.py --server.port 8501
```

## Definición de Hecho (DoD)

Una tarea está completa cuando:
1. El código implementa el requisito
2. Los tests relevantes pasan
3. La documentación se actualizó si aplica
4. No hay errores de import ni sintaxis
