# Mapa de Impacto

## Módulos que Participan en el Flujo

```
Solicitud del usuario
        │
        ▼
┌─────────────────┐
│ API Endpoint    │  backend/api/endpoints/quotes.py
│ (create_quote)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Workflow Engine  │  backend/workflow/engine.py
│ (run_workflow)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Graph (Nodes)   │  backend/workflow/graph.py + nodes.py
│                 │
│ ┌─────────────┐ │
│ │ Extraction  │ │  → Usa LLM (langchain-openai)
│ │ Validation  │ │  → Usa domain/services.py
│ │ Calculation │ │  → Usa domain/services.py
│ │ Approval    │ │  → Interrupt (human-in-the-loop)
│ │ Draft       │ │  → Usa LLM (langchain-openai)
│ └─────────────┘ │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Domain Services │  backend/domain/services.py
│ (determinista)  │
│                 │
│ - get_client    │  → Lee de domain/data.py
│ - check_stock   │  → Lee de domain/data.py
│ - calc_total    │  → Función pura
│ - validate_disc │  → Lee de domain/data.py
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Domain Data     │  backend/domain/data.py
│ (fuente verdad) │
│                 │
│ - CLIENTS       │
│ - PRODUCTS      │
│ - INVENTORY     │
│ - POLICIES      │
└─────────────────┘
```

## ¿Qué Cambia al Modificar una Política?

### Ejemplo: Cambiar el umbral de aprobación de USD 10,000 a USD 15,000

| Archivo Afectado | Cambio | Impacto |
|------------------|--------|---------|
| `backend/domain/data.py` | Modificar `APPROVAL_THRESHOLD_USD` | Único punto de cambio |
| `backend/domain/services.py` | Ninguno | La función `requires_approval()` lee la constante |
| `backend/workflow/nodes.py` | Ninguno | Llama a `requires_approval()` |
| `tests/test_domain_services.py` | Actualizar valor esperado en tests | Verificar nuevo umbral |

**Conclusión:** Un cambio de política requiere modificar **un solo valor** en `data.py` y actualizar los tests correspondientes. El resto del sistema se adapta automáticamente.

### Ejemplo: Agregar un nuevo tier de cliente "diamond"

| Archivo Afectado | Cambio |
|------------------|--------|
| `backend/domain/data.py` | Agregar entrada en `DISCOUNT_POLICIES` |
| `backend/domain/data.py` | Agregar cliente(s) con tier "diamond" en `CLIENTS` |
| `tests/test_domain_services.py` | Agregar test para nuevo tier |

**Conclusión:** Diseño extensible — agregar un tier no requiere cambiar lógica, solo datos.

## Evidencia del Mapa que Influyó en el Plan

1. **Separación LLM/dominio** — Al mapear el flujo, se identificó que solo 2 de 7 nodos necesitan LLM. El resto es determinista.
2. **Punto único de datos** — `domain/data.py` es la fuente de verdad. Cambios de política son localizados.
3. **Interrupt localizado** — Solo el nodo `approval` requiere interacción humana. El resto fluye automáticamente.
4. **Testabilidad por diseño** — Al aislar domain/services de workflow/nodes, las pruebas no dependen del grafo ni del LLM.
