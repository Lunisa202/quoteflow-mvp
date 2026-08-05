# Evidencia

## Comandos Ejecutados y Resultados

### Setup del Proyecto
```bash
pip install -e ".[dev]"
# Resultado: Instalación exitosa de todas las dependencias
```

### Ejecución de Tests
```bash
pytest tests/ -v
# Resultado: Tests del dominio, routing e idempotencia pasan
```

### Inicio del Backend
```bash
uvicorn backend.main:app --reload --port 8000
# Resultado: API corriendo en http://localhost:8000
# Docs disponibles en http://localhost:8000/docs
```

### Inicio del Frontend
```bash
streamlit run frontend/app.py --server.port 8501
# Resultado: UI disponible en http://localhost:8501
```

## Casos de Prueba Ejecutados

### Caso 1: Solicitud Estándar (Cliente Gold)
- **Input:** CLI-001, "Necesito 20 cascos modelo HX-200 para Arequipa, 8% descuento"
- **Ruta esperada:** extraction → validation → calculation → draft
- **Resultado:** Borrador generado correctamente

### Caso 2: Solicitud de Alto Valor (Requiere Aprobación)
- **Input:** CLI-003, "5 WL-100 y 3 CP-750 para Piura, 12% descuento"
- **Ruta esperada:** extraction → validation → calculation → approval (interrupt)
- **Resultado:** Workflow pausado en aprobación

### Caso 3: Solicitud Incompleta
- **Input:** CLI-002, "Necesito equipos de seguridad"
- **Ruta esperada:** extraction → validation → clarification
- **Resultado:** Solicitud de aclaración generada

## Limitaciones Observadas

- El tiempo de respuesta depende de la latencia del API de OpenAI (~2-5 segundos)
- Solicitudes muy ambiguas pueden generar extracciones parciales
- El checkpointer SQLite no es ideal para concurrencia alta (aceptable para MVP)
