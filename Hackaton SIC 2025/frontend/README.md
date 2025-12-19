# LegalBot Panamá – Frontend

Interfaz oscura y responsiva para la demo del chatbot legal (RAG + Gemini).

## Ejecutar

Opción rápida (sin dependencias):
```bash
cd "PA11-DATA-ALCHEMISTS-PROYECTO-FINAL/Hackaton SIC 2025"
bash run_local.sh
```
- Frontend: http://localhost:8001
- Backend: http://localhost:8000

## Conectar al backend

El frontend usa un mock local si no hay API configurada. Para llamar a tu endpoint (FastAPI/Streamlit):
1. Levanta el backend (`uvicorn main:app --port 8000` o con `run_local.sh`).
2. La UI intenta `http://localhost:8000/api/chat` por defecto; si tu endpoint es otro, define en consola:
```js
window.LEGALBOT_API_URL = "http://mi-endpoint/api/chat";
```
Si la llamada falla, el mock seguirá activo.

## Estructura de archivos
- `index.html` – Layout principal (hero, tarjetas, panel de chat, checklist).
- `styles.css` – Tema oscuro sobrio con acentos verde/azul y animación de carga.
- `app.js` – Lógica de UI: envío de preguntas, loading, respuesta (backend o mock), quick prompts y reset.
