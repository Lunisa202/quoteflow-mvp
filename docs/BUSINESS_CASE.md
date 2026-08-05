# Caso de Negocio: QuoteFlow MVP

## Usuario y Proceso Actual

**Usuario:** Ejecutivos de ventas de AndesPro Industrial (distribuidor B2B de equipamiento industrial).

**Proceso actual:** Las solicitudes llegan por correo, formularios y mensajería en texto libre. Un ejecutivo debe manualmente:
1. Identificar al cliente
2. Interpretar productos y cantidades
3. Consultar catálogo y stock
4. Aplicar políticas comerciales
5. Gestionar excepciones de descuento
6. Redactar una respuesta

**Tiempo promedio por cotización:** 25-40 minutos en casos estándar, hasta 2 horas en complejos.

## Problema

- La alta carga cognitiva genera errores de precios y violaciones de política.
- El tiempo de respuesta lento (horas a días) pierde oportunidades competitivas.
- No existe trazabilidad de decisiones de precios.
- Aplicación inconsistente de descuentos entre ejecutivos.

## Hipótesis de Valor

> Al automatizar la extracción, validación y generación de borradores manteniendo supervisión humana para excepciones, QuoteFlow puede reducir el tiempo de preparación de cotizaciones en un 60-70% sin comprometer márgenes, exactitud de stock ni cumplimiento de políticas.

## MVP y No Alcance

**Alcance del MVP:**
- Interpretación de solicitudes en lenguaje natural (asistida por LLM)
- Validación determinista contra datos de clientes, productos, stock y políticas
- Cálculo automático de precios
- Aprobación humana para excepciones (human-in-the-loop)
- Generación de borrador de cotización
- Trazabilidad de decisiones (audit trail)

**Fuera de alcance:**
- Integraciones con email/WhatsApp/ERP
- Autenticación y multi-tenant
- Envío automático al cliente
- Infraestructura productiva
- Diseño visual avanzado

## Métricas de Éxito y Guardia

| Métrica | Actual | Objetivo | Guardia |
|---------|--------|----------|---------|
| Tiempo promedio de preparación | 35 min | 12 min | Cero aprobaciones falsas |
| Tasa de cumplimiento de política | ~85% | 100% | Cero erosión de margen |
| Tasa de revisión humana | 100% | <30% (solo excepciones) | Todas las excepciones revisadas |
| Exactitud de datos (precios, stock) | Variable | 100% determinista | Cero datos inventados por LLM |

## Principales Riesgos

| Riesgo | Impacto | Mitigación |
|--------|---------|------------|
| LLM alucinando precios/stock | Crítico | Todos los datos de negocio provienen únicamente de funciones deterministas |
| Inyección de prompt vía texto del cliente | Alto | Prompts del sistema aislados; texto del cliente tratado como entrada no confiable |
| Aprobación automática falsa | Alto | Reglas de umbral son deterministas; el LLM no puede eludirlas |
| Datos de inventario desactualizados | Medio | MVP usa datos estáticos; producción requiere sincronización en tiempo real |
| Dependencia de un solo proveedor de LLM | Medio | Abstraído via LangChain; intercambiable |

## Nivel de Autonomía Recomendado

**Nivel 2 — Borrador y Confirmar:** El sistema prepara borradores completos pero nunca envía al cliente automáticamente. El humano revisa cada output antes de comunicación externa.

- Cotizaciones estándar (< USD 10,000, dentro de política de descuento): Borrador auto-generado, el ejecutivo revisa y envía.
- Cotizaciones con excepción: El workflow se pausa para aprobación explícita antes de generar borrador.

## Propuesta de Piloto

- **Duración:** 4 semanas
- **Alcance:** 2-3 ejecutivos de ventas, categorías de productos estándar únicamente
- **Criterios de éxito:** Reducción de 50%+ en tiempo sin violaciones de política
- **Plan de rollback:** Los ejecutivos revierten al proceso manual; todos los borradores son solo consultivos
