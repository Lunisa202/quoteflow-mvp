# ADR-001: LangGraph como Motor de Workflow

## Estado
Aceptado

## Contexto

El sistema necesita orquestar un flujo de cotización con múltiples pasos, decisiones condicionales, pausa/reanudación para aprobación humana, y persistencia durable del estado.

Alternativas consideradas:
1. **LangGraph** — Grafo de estados con checkpointer, interrupt nativo, tipado
2. **Celery + state machine** — Cola de tareas con máquina de estados manual
3. **Temporal.io** — Workflow engine empresarial
4. **Custom async pipeline** — Implementación propia

## Decisión

Usamos **LangGraph** como motor de workflow por las siguientes razones:

1. **Requisito del reto** — Es obligatorio.
2. **Estado tipado** — TypedDict proporciona validación en tiempo de desarrollo.
3. **Interrupt nativo** — `interrupt_before` permite human-in-the-loop sin lógica custom.
4. **Checkpointer SQLite** — Persistencia durable con una línea de configuración.
5. **Routing condicional** — `add_conditional_edges` permite decisiones declarativas.
6. **Integración LangChain** — Los nodos que usan LLM se integran naturalmente.

## Consecuencias

### Positivas
- El flujo es declarativo y visualizable
- La reanudación tras reinicio funciona out-of-the-box
- Los nodos son funciones puras testeables individualmente
- El estado del workflow es inspeccionable en cualquier punto

### Negativas
- Dependencia fuerte en el ecosistema LangChain/LangGraph
- La API de LangGraph aún evoluciona (posibles breaking changes)
- El debug puede ser más complejo que un pipeline lineal
- El checkpointer SQLite no escala a alta concurrencia

### Nivel de Autonomía

**El LLM tiene autonomía limitada:**
- Puede interpretar texto natural → datos estructurados
- Puede redactar borradores de cotización
- **NO puede** calcular precios, validar stock, aplicar descuentos ni aprobar cotizaciones
- Todas las decisiones de negocio son deterministas y están en funciones del dominio
