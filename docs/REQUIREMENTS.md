# Requisitos

## Requisitos Funcionales

### RF-01: Registrar Solicitud de Cotización
- El ejecutivo proporciona un ID de cliente y una solicitud en lenguaje natural
- El sistema asigna un ID único de cotización
- El workflow inicia el procesamiento

### RF-02: Extraer Datos Estructurados
- El LLM extrae: productos, cantidades, ubicación, fecha, descuento
- La salida es JSON estructurado con campos faltantes explícitos
- Productos desconocidos marcados como "UNKNOWN"

### RF-03: Validar Reglas de Negocio
- Verificar que el cliente existe en el sistema
- Verificar que todos los productos están en el catálogo
- Comprobar disponibilidad de stock en la ubicación de entrega
- Validar descuento contra la política del tier del cliente
- Identificar si se requiere aprobación

### RF-04: Calcular Precios
- Cálculo determinista usando funciones del dominio
- Aplicar descuento permitido (limitado si excede la política)
- Computar totales por línea y total general
- Sin intervención del LLM en los cálculos

### RF-05: Flujo de Aprobación Humana
- El workflow se pausa cuando se requiere aprobación
- El ejecutivo puede aprobar o rechazar con notas
- La decisión se registra en la trazabilidad
- El workflow se reanuda desde el punto de interrupción

### RF-06: Generar Borrador de Cotización
- El LLM genera texto de cotización profesional
- Basado en los datos calculados (no recalcula)
- Incluye todos los términos y condiciones relevantes

### RF-07: Trazabilidad (Audit Trail)
- Cada transición de estado se registra
- Timestamps, decisiones y errores se documentan
- El historial es consultable por cotización

### RF-08: Persistencia Durable
- El estado del workflow persiste al reiniciar la aplicación
- Checkpointer SQLite para el estado de LangGraph
- Almacén JSON para datos de la aplicación

## Requisitos No Funcionales

### RNF-01: Lógica de Negocio Determinista
- Precios, stock y políticas nunca provienen del LLM
- Las mismas entradas siempre producen las mismas salidas

### RNF-02: Respuestas API Uniformes
- Formato: `{success: bool, data?: any, error?: {code, message, details}, meta?: any}`

### RNF-03: Manejo de Errores
- Fallo controlado con mensajes de error significativos
- Ninguna excepción sin manejar llega al cliente

### RNF-04: Testeabilidad
- Funciones del dominio testeables sin LLM
- Lógica de enrutamiento testeable con estado mock
- Modo de prueba disponible sin llamadas a API externa

### RNF-05: Seguridad
- Texto del cliente tratado como entrada no confiable
- Sin secretos en el repositorio
- `.env.example` proporcionado sin credenciales reales
