# ADR-002: Groq como Proveedor de LLM

## Estado
Aceptado

## Contexto

El sistema necesita un LLM para dos tareas:
1. Extraer datos estructurados de texto libre (solicitudes de cotización)
2. Generar borradores de cotización en lenguaje natural

Se evaluaron las siguientes opciones:

| Proveedor | Modelo | Costo | Latencia |
|-----------|--------|-------|----------|
| OpenAI | gpt-4o-mini | ~$0.15/1M tokens | ~2-3s |
| Groq | llama-3.1-8b-instant | Gratis (tier free) | ~0.5-1s |
| Google | gemini-1.5-flash | Gratis (15 RPM) | ~2s |

## Decisión

Usamos **Groq con llama-3.1-8b-instant** porque:

1. **Costo cero** — El tier gratuito es suficiente para desarrollo y demo
2. **Baja latencia** — Groq ejecuta en hardware especializado (LPU), respuestas en <1s
3. **Compatibilidad LangChain** — `langchain-groq` se integra igual que `langchain-openai`
4. **Modelo capaz** — Llama 3.1 8B maneja bien extracción JSON y generación de texto profesional

## Consecuencias

### Positivas
- Sin costo de desarrollo ni demo
- Latencia excelente para UX interactiva
- Fácil migración a OpenAI si se requiere (cambiar 1 import + 1 variable de entorno)

### Negativas
- Rate limits del tier free (30 RPM) — suficiente para MVP, no para producción
- Modelo más pequeño que GPT-4o — puede fallar en solicitudes muy ambiguas
- Dependencia de disponibilidad del servicio gratuito

### Migración a Producción

Para migrar a OpenAI basta cambiar:
```python
# De:
from langchain_groq import ChatGroq
llm = ChatGroq(model="llama-3.1-8b-instant", api_key=GROQ_API_KEY)

# A:
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4o-mini", api_key=OPENAI_API_KEY)
```

El resto del sistema no cambia — la abstracción de LangChain lo permite.
