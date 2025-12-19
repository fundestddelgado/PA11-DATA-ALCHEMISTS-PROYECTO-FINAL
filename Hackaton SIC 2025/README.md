## 📄 `PROJECT_OVERVIEW.md`

*(Idea central + arquitectura + alcance del proyecto)*

````markdown
# LegalBot Panamá 🇵🇦  
Chatbot Informativo de Consulta Legal con IA (Gemini + RAG)

## Descripción general
LegalBot Panamá es un chatbot informativo que permite consultar **códigos y leyes panameñas** utilizando Inteligencia Artificial.

El sistema combina un **LLM (Gemini API)** con una arquitectura de **búsqueda semántica (RAG)** para responder preguntas legales **solo con información oficial**, citando siempre los artículos correspondientes.

⚠️ Este sistema **NO brinda asesoría legal**. Su propósito es exclusivamente informativo.

---

## Objetivo del proyecto
Desarrollar un chatbot que:
- Facilite el acceso a información legal
- Explique artículos legales en lenguaje natural
- Cite leyes y artículos automáticamente
- Evite respuestas inventadas o no verificables

---

## Alcance
El proyecto trabaja con un **conjunto limitado de normativas**, por ejemplo:
- Código de Trabajo de Panamá
- Código de Tránsito
- Reglamentos específicos (según disponibilidad)

Este alcance acotado garantiza precisión y control del modelo.

---

## Enfoque técnico: LLM + RAG

El sistema utiliza un enfoque **Retrieval-Augmented Generation**:

1. Buscar información relevante en documentos legales
2. Recuperar fragmentos específicos (artículos)
3. Generar respuestas con Gemini usando solo esos fragmentos

El LLM no responde sin evidencia documental.

---

## Arquitectura del sistema

### 1. Ingesta de documentos
- PDFs oficiales (Gaceta Oficial, códigos)
- Conversión a texto
- Segmentación por artículos o secciones

### 2. Vectorización
- Conversión de fragmentos a embeddings
- Almacenamiento en base vectorial

### 3. Consulta
- El usuario formula una pregunta
- Se recuperan los fragmentos más relevantes (Top-K)

### 4. Generación con LLM
- Gemini genera la respuesta usando solo los fragmentos recuperados
- Se aplican reglas estrictas de citación

### 5. Respuesta final
- Explicación clara
- Artículos citados
- Referencia legal visible

---

## Control de alucinaciones
- El modelo no puede inventar información
- Si no hay datos suficientes, responde con “No encontrado”
- Todas las respuestas incluyen fuente legal

---

## Tecnologías utilizadas
- Python
- FastAPI
- Gemini API (LLM)
- FAISS o ChromaDB
- Streamlit (frontend)
- PyPDF2 / pdfplumber

---

## Estructura del proyecto

```bash
legalbot-panama/
├── data/
│   ├── raw_pdfs/
│   └── processed_chunks/
├── embeddings/
│   └── vector_store/
├── backend/
│   ├── main.py
│   ├── rag_pipeline.py
│   └── gemini_client.py
├── frontend/
│   └── app.py
├── prompts/
│   └── system_prompt.txt
├── README.md
└── requirements.txt
````

---

## Impacto del proyecto

* Democratiza el acceso a información legal
* Reduce la complejidad del lenguaje jurídico
* Promueve el uso responsable de IA
* Aplica LLMs a un contexto local y real

```

---

### 🧠 Cierre honesto
Con estos dos archivos:
- Tus compañeros **entienden la idea sin saber IA**
- El LLM **no se descontrola**
- El proyecto queda **defendible ante SIC**
- Codex puede implementar sin ambigüedad

Si quieres, el siguiente paso lógico es:
- el **`system_prompt.txt` final para Gemini**, o  
- un **diagrama de arquitectura** listo para diapositivas SIC.
```


## 📄 `LLM_INSTRUCTIONS.md`

*(Instrucciones operativas para el LLM – Gemini API / CLI)*

```markdown
# Instrucciones del LLM – LegalBot Panamá

## Rol del modelo
Eres un asistente legal **informativo**, no un abogado.
Tu función es **explicar y resumir información legal** basada únicamente en los documentos proporcionados por el sistema.

NO debes ofrecer asesoría legal ni emitir opiniones jurídicas.

---

## Contexto de conocimiento
- Tu conocimiento legal está **limitado exclusivamente** a los fragmentos de leyes y códigos panameños proporcionados en cada consulta.
- No debes usar conocimiento previo ni externo.
- Si la información no se encuentra en los documentos, debes indicarlo explícitamente.

---

## Reglas estrictas (guardrails)

1. **No inventes artículos, leyes ni numerales**
2. **No completes información faltante con suposiciones**
3. **Cita siempre las fuentes legales**
4. **Si no hay información suficiente, dilo claramente**

Ejemplo de respuesta válida cuando no hay evidencia:
> “No se encontró información relevante en los documentos legales disponibles para responder esta consulta.”

---

## Estilo de respuesta
- Lenguaje claro y sencillo
- Evitar jerga jurídica innecesaria
- Respuestas estructuradas cuando sea posible
- No redactar como sentencia ni como asesor legal

---

## Formato de salida obligatorio

Toda respuesta debe seguir esta estructura:

### Respuesta
[Explicación clara basada únicamente en los fragmentos proporcionados]

### Fuente legal
- Ley / Código: [Nombre]
- Artículo(s): [Número]
- Documento: [Referencia si está disponible]

---

## Ejemplo

Pregunta:
> ¿Cuáles son las obligaciones del empleador según el Código de Trabajo?

Respuesta esperada:

### Respuesta
El empleador tiene la obligación de garantizar condiciones adecuadas de trabajo, cumplir con el pago del salario acordado y respetar los derechos laborales establecidos por la ley.

### Fuente legal
- Código de Trabajo de Panamá
- Artículo 12, Artículo 15
```

---

## 🚀 Ejecución rápida (demo local)

1. Instala dependencias del backend:
   ```bash
   cd "PA11-DATA-ALCHEMISTS-PROYECTO-FINAL/Hackaton SIC 2025/backend"
   pip install -r requirements.txt
   ```
2. Arranca frontend + backend desde la raíz del proyecto:
   ```bash
   cd "PA11-DATA-ALCHEMISTS-PROYECTO-FINAL/Hackaton SIC 2025"
   bash run_local.sh
   ```
   - Backend (FastAPI + FAISS): http://localhost:8000  
   - Frontend (UI oscura): http://localhost:8001  
3. La UI consulta `http://localhost:8000/api/chat` por defecto. Si usas otro endpoint, en la consola del navegador define:
   ```js
   window.LEGALBOT_API_URL = "http://mi-endpoint/api/chat";
   ```
