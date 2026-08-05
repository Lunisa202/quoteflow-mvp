# Ciclo de Mejora (Loop)

## Loop Actual: Implementación del MVP

| Campo | Valor |
|-------|-------|
| **Objetivo** | Entregar vertical funcional de QuoteFlow |
| **Worker** | Desarrolladora (Carolina) + Asistente IA (Kiro) |
| **Verifier** | Tests automatizados + revisión manual |
| **Estado** | En progreso |
| **Presupuesto** | 6 horas netas |
| **Condición de salida** | Los 3 casos de demo funcionan, tests pasan, docs completos |
| **Condición de bloqueo** | Fallo de API OpenAI, error irrecuperable en LangGraph |
| **Handoff** | README + STATE.md permiten que otro continúe |

## Ciclo de Trabajo

```
┌─────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│ Discutir │────▶│ Planificar│────▶│ Ejecutar │────▶│ Verificar│
└─────────┘     └──────────┘     └──────────┘     └────┬─────┘
      ▲                                                  │
      │              ┌──────────┐                        │
      └──────────────│  Handoff │◀───────────────────────┘
                     └──────────┘
```

### Iteración 1: Scaffolding
- **Discutir:** Definir arquitectura (FastAPI + LangGraph + Streamlit)
- **Planificar:** Crear tareas atómicas en PHASE_01.md
- **Ejecutar:** Generar estructura completa del proyecto
- **Verificar:** Revisar imports, dependencias, coherencia
- **Handoff:** Código base listo para ejecución

### Iteración 2: Validación
- **Discutir:** Confirmar que tests pasan
- **Planificar:** Identificar ajustes necesarios
- **Ejecutar:** Correr pytest, corregir errores
- **Verificar:** Tests en verde
- **Handoff:** Módulo validado

### Iteración 3: Integración End-to-End
- **Discutir:** Probar flujo completo con API key
- **Planificar:** Ejecutar los 3 casos de demo
- **Ejecutar:** Enviar solicitudes vía Streamlit
- **Verificar:** Resultados coinciden con lo esperado
- **Handoff:** Demo lista para presentación

## Reglas del Loop

1. Cada iteración tiene un entregable concreto
2. Si algo falla 2 veces, cambiar de enfoque
3. El verificador (tests) es independiente del worker
4. El handoff incluye: qué se hizo, qué falta, qué puede fallar
5. No se continúa sin que la verificación pase
