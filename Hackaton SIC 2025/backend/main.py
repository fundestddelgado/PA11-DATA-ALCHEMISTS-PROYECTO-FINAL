import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import faiss
import numpy as np
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

# Directorios base (backend está en /Hackaton SIC 2025/backend)
BACKEND_DIR = Path(__file__).resolve().parent
ROOT_DIR = BACKEND_DIR.parent
FAISS_ROOT = ROOT_DIR / "Dataset" / "FAISS"


# ------------------------------------------------------------
# Modelos de request/response
# ------------------------------------------------------------
class ChatRequest(BaseModel):
    question: str
    strict: bool = True
    citations: bool = True
    top_k: int = 3
    codigo: Optional[str] = None  # Permite forzar un código específico opcionalmente.


class Source(BaseModel):
    code: str
    article: str
    document: str


class ChatResponse(BaseModel):
    answer: str
    sources: List[Source]


# ------------------------------------------------------------
# Carga de índices FAISS + docs
# ------------------------------------------------------------
@dataclass
class LoadedIndex:
    code_id: str
    code_name: str
    index: faiss.Index
    docs: List[dict]


# Palabras clave para detección rápida (ampliadas con todos los códigos disponibles).
CODE_KEYWORDS: Dict[str, List[str]] = {
    "codigo_trabajo": ["trabajo", "laboral", "empleador", "empleado", "licencia", "fuero", "despido"],
    "codigo_penal": ["penal", "delito", "pena", "hurto", "robo", "homicidio", "estafa"],
    "codigo_civil": ["civil", "contrato", "obligacion", "obligación", "responsabilidad", "daños", "perjuicios"],
    "codigo_familia": ["familia", "matrimonio", "divorcio", "adopcion", "adopción", "guarda", "menor", "patria potestad"],
    "codigo_electoral": ["electoral", "eleccion", "elección", "partido", "voto", "campaña"],
    "codigo_comercio": ["comercio", "mercantil", "sociedad", "empresa", "firma", "accionista", "accionistas"],
    "codigo_fiscal": ["fiscal", "impuesto", "tributo", "declaracion", "declaración", "renta", "iva"],
    "codigo_judicial": ["judicial", "proceso", "demanda", "recurso", "apelacion", "apelación", "tribunal"],
    "codigo_sanitario": ["sanitario", "salud", "hospital", "medico", "médico", "farmacia"],
    "codigo_agrario": ["agrario", "agricola", "agrícola", "tierra", "finca", "agro"],
    "codigo_recursos_minerales": ["mineria", "minería", "mineral", "concesion", "concesión", "yacimientos"],
}


def detect_code(question: str) -> Optional[str]:
    q = question.lower()
    for code_id, keywords in CODE_KEYWORDS.items():
        if any(k in q for k in keywords):
            return code_id
    return None


def load_indexes() -> Dict[str, LoadedIndex]:
    indexes: Dict[str, LoadedIndex] = {}
    if not FAISS_ROOT.exists():
        raise FileNotFoundError(f"No se encontró la ruta de índices FAISS: {FAISS_ROOT}")

    for dir_path in FAISS_ROOT.iterdir():
        if not dir_path.is_dir():
            continue
        index_path = dir_path / "index.faiss"
        docs_path = dir_path / "docs.json"
        if not index_path.exists() or not docs_path.exists():
            continue

        try:
            index = faiss.read_index(str(index_path))
            docs = json.loads(docs_path.read_text(encoding="utf-8"))
            if not docs:
                continue
            code_name = docs[0].get("codigo", dir_path.name)
            indexes[dir_path.name] = LoadedIndex(
                code_id=dir_path.name,
                code_name=code_name,
                index=index,
                docs=docs,
            )
            print(f"[LOAD] {dir_path.name}: {len(docs)} artículos")
        except Exception as exc:  # pragma: no cover - solo log
            print(f"[WARN] No se pudo cargar {dir_path.name}: {exc}")

    if not indexes:
        raise RuntimeError("No se cargó ningún índice FAISS. Revisa la carpeta Dataset/FAISS.")
    return indexes


@lru_cache(maxsize=1)
def get_model() -> SentenceTransformer:
    print("[INIT] Cargando modelo de embeddings (sentence-transformers/all-MiniLM-L6-v2)...")
    return SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


@lru_cache(maxsize=1)
def get_indexes() -> Dict[str, LoadedIndex]:
    return load_indexes()


# ------------------------------------------------------------
# Búsqueda
# ------------------------------------------------------------
def search_indexes(
    question: str, code_hint: Optional[str], top_k: int
) -> Tuple[List[Tuple[float, dict, LoadedIndex]], np.ndarray]:
    model = get_model()
    vector = model.encode([question]).astype("float32")
    results: List[Tuple[float, dict, LoadedIndex]] = []
    used_indexes: List[LoadedIndex] = []

    available = get_indexes()
    targets = (
        [available[code_hint]]
        if code_hint and code_hint in available
        else list(available.values())
    )

    for item in targets:
        distances, idxs = item.index.search(vector, top_k)
        for dist, idx in zip(distances[0], idxs[0]):
            if idx < 0 or idx >= len(item.docs):
                continue
            results.append((float(dist), item.docs[idx], item))
        used_indexes.append(item)

    # Menor distancia = más similar en L2
    results.sort(key=lambda r: r[0])
    return results[:top_k], vector


def truncate_text(text: str, limit: int = 420) -> str:
    return text if len(text) <= limit else text[:limit].rstrip() + "..."


def build_answer(question: str, strict: bool, include_citations: bool, code_hint: Optional[str], top_k: int) -> ChatResponse:
    detected = detect_code(question)
    code_to_use = code_hint or detected

    hits, _ = search_indexes(question, code_to_use, top_k)
    if not hits:
        msg = (
            "No encontré evidencia suficiente en los códigos cargados. "
            "Prueba especificar el código o artículo, o revisa que la base esté construida."
        )
        return ChatResponse(answer=msg, sources=[])

    bullets = []
    sources: List[Source] = []

    for dist, doc, idx_info in hits:
        article = doc.get("articulo", "s/n")
        code_name = idx_info.code_name
        snippet = truncate_text(doc.get("texto", ""))
        bullets.append(f"- {code_name}, Art. {article}: {snippet}")
        if include_citations:
            sources.append(
                Source(
                    code=code_name,
                    article=f"Artículo {article}",
                    document=f"Dataset/FAISS/{idx_info.code_id}/docs.json",
                )
            )

    hint_txt = f"Código detectado: {detected}" if detected else "Sin código detectado, búsqueda global."
    mode_txt = "Modo estricto: se devuelven solo fragmentos recuperados." if strict else "Modo flexible: puedes extender la explicación sobre estos fragmentos."
    answer = f"{hint_txt}\n{mode_txt}\n\nEvidencias:\n" + "\n".join(bullets)

    return ChatResponse(answer=answer, sources=sources)


# ------------------------------------------------------------
# FastAPI
# ------------------------------------------------------------
app = FastAPI(title="LegalBot Panamá Backend", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok", "indexes": list(get_indexes().keys())}


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """
    Usa la base existente (Dataset/FAISS + Dataset/JSON) para devolver los artículos más cercanos.
    Sustituye build_answer por tu pipeline Gemini si quieres generación neural encima de las evidencias.
    """
    return build_answer(
        question=request.question,
        strict=request.strict,
        include_citations=request.citations,
        code_hint=request.codigo,
        top_k=max(1, min(request.top_k, 5)),
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
