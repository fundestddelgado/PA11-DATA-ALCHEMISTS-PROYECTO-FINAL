## LegalBot Panamá – Backend (FastAPI)

API FastAPI que usa los índices FAISS existentes en `Dataset/FAISS` y los `docs.json` asociados para devolver artículos relevantes. Endpoints:
- `GET /api/health` – estado + índices cargados.
- `POST /api/chat` – recibe `{ question, strict, citations, top_k?, codigo? }` y devuelve `{ answer, sources }`.

### Requisitos
```bash
pip install -r requirements.txt
```

### Ejecutar en desarrollo
```bash
cd "PA11-DATA-ALCHEMISTS-PROYECTO-FINAL/Hackaton SIC 2025/backend"
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
Docs interactivas: http://localhost:8000/docs

### Conectar desde el frontend
En la consola del navegador (ya con el backend levantado):
```js
window.LEGALBOT_API_URL = "http://localhost:8000/api/chat";
```
Envía una consulta desde la UI y verás la respuesta del backend. Si el backend no responde, el frontend vuelve al mock local.

### Notas de implementación
- El backend carga todos los índices presentes en `Dataset/FAISS/*` (usa `index.faiss` y `docs.json`).
- La detección de código usa palabras clave ampliadas; si no detecta, busca globalmente y devuelve los `top_k` más cercanos (distancia L2).
- `build_answer` devuelve fragmentos textuales; puedes reemplazar la construcción de respuesta para llamar a Gemini usando las evidencias como contexto.
