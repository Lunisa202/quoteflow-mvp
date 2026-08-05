# Uso de IA en el Desarrollo

## Herramientas Utilizadas

| Herramienta | Rol Asignado | Uso |
|-------------|-------------|-----|
| Kiro (Claude) | Asistente de desarrollo | Scaffolding, código, documentación |
| GPT-4o-mini | Runtime del sistema | Extracción de datos y generación de borradores |

## Rol del Asistente IA en el Desarrollo

El asistente fue usado para:
- Generar la estructura inicial del proyecto
- Escribir el código base de cada módulo
- Redactar la documentación del reto
- Crear pruebas unitarias y de integración

## Outputs Aceptados

- Estructura de carpetas y archivos de configuración
- Implementación de funciones de dominio deterministas
- Definición del grafo LangGraph con estado tipado
- Endpoints FastAPI con manejo uniforme de errores
- Frontend Streamlit con las vistas requeridas
- Documentación BUSINESS_CASE, PROJECT, REQUIREMENTS

## Outputs Rechazados o Modificados

- Primeras versiones de documentación estaban en inglés — se pidió español
- Ninguna implementación fue aceptada sin revisión de coherencia

## Cómo Verifiqué el Resultado

1. **Revisión de coherencia:** Cada módulo fue revisado para verificar que los imports y dependencias son correctos
2. **Tests deterministas:** Las funciones de dominio tienen pruebas unitarias que validan cálculos exactos
3. **Tests de routing:** Las rutas condicionales del grafo se verifican con estados mock
4. **Tests de idempotencia:** Se confirma que las mismas entradas producen las mismas salidas
5. **Ejecución local:** La aplicación se ejecutó para verificar el flujo end-to-end
6. **Revisión manual de documentación:** Cada doc fue leído para confirmar que refleja el código

## Principio Aplicado

> El asistente genera; yo decido, verifico y soy responsable del resultado final.
