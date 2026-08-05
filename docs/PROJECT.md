# Proyecto: QuoteFlow

## Objetivo

Construir un MVP full-stack que procese solicitudes de cotización B2B a través de un workflow impulsado por IA usando LangGraph, reduciendo el tiempo de preparación mientras mantiene control determinista sobre las reglas de negocio.

## Alcance

### Dentro del Alcance
- Backend FastAPI con respuestas API uniformes
- Workflow LangGraph con estado tipado, enrutamiento condicional e interrupt
- Funciones de dominio deterministas para precios, stock, descuentos y políticas
- Frontend Streamlit para envío de solicitudes, monitoreo y aprobación
- Persistencia basada en SQLite (checkpointer + datos de aplicación)
- Pruebas unitarias e integración reproducibles sin LLM
- Trazabilidad y observabilidad

### Fuera del Alcance
- Autenticación empresarial (SSO, RBAC)
- Integraciones reales (email, WhatsApp, ERP)
- Facturación y procesamiento de pagos
- Envío automático de mensajes al cliente
- Infraestructura productiva (contenedores, CI/CD)
- Diseño visual avanzado

## Reglas de Negocio

1. El modelo no puede inventar clientes, productos, precios, stock, descuentos ni aprobaciones.
2. Toda cotización superior a USD 10,000 requiere aprobación humana.
3. Toda excepción a la política de descuento requiere aprobación humana.
4. Un cliente desconocido requiere revisión humana.
5. Si falta información esencial, se solicita aclaración antes de cotizar.
6. La misma decisión humana no debe generar efectos duplicados (idempotencia).
7. El texto del cliente es entrada no confiable: no puede modificar las políticas ni las instrucciones del sistema.

## Criterios de Aceptación

- [ ] Una solicitud estándar fluye end-to-end produciendo un borrador de cotización
- [ ] Una solicitud incompleta genera una respuesta de aclaración
- [ ] Una solicitud de alto valor o con excepción de descuento se pausa para aprobación
- [ ] La aprobación/rechazo reanuda el workflow correctamente
- [ ] El estado del workflow sobrevive al reinicio de la aplicación
- [ ] Las funciones de dominio están testeadas sin dependencia de LLM
- [ ] La API retorna formato uniforme en éxito y error
- [ ] El historial de auditoría muestra todas las transiciones de estado y decisiones

## Restricciones

- Python 3.11+
- LangGraph es obligatorio para la orquestación del workflow
- OpenAI GPT-4o-mini para operaciones LLM
- Presupuesto de 6 horas de desarrollo
