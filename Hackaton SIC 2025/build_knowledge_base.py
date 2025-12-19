import os
import re
import json
import faiss
import numpy as np
from langchain_community.document_loaders import PyPDFLoader
from sentence_transformers import SentenceTransformer
from config import (
    PDF_DIR,
    JSON_DIR,
    FAISS_DIR,
    CODIGOS_A_PROCESAR,
    EMBEDDING_MODEL,
)

# ==================================================
# ASEGURAR DIRECTORIOS
# ==================================================
os.makedirs(JSON_DIR, exist_ok=True)
os.makedirs(FAISS_DIR, exist_ok=True)

# ==================================================
# FUNCIÓN DE PARSEO DE PDF
# ==================================================

def parsear_pdf_a_json(codigo_info):
    """
    Parsea un archivo PDF de un código legal, extrae los artículos y los guarda en un archivo JSON.
    """
    pdf_path = os.path.join(PDF_DIR, codigo_info["pdf_filename"])
    codigo_nombre = codigo_info["nombre_completo"]
    rama = codigo_info["rama"]
    codigo_id = codigo_info["id"]
    json_path = os.path.join(JSON_DIR, f"{codigo_id}.json")

    print(f"📄 Procesando PDF: {pdf_path}")

    if not os.path.exists(pdf_path):
        print(f"⚠️  Archivo no encontrado: {pdf_path}")
        return False

    try:
        loader = PyPDFLoader(pdf_path)
        docs = loader.load()
        texto = "\n".join(d.page_content for d in docs)
        texto = re.sub(r'\s+', ' ', texto)

        # Regex para encontrar artículos. Puede necesitar ajustes.
        patron = r'(Artículo\s+\d+[A-Z]?\s*\.?-?)'
        partes = re.split(patron, texto)

        articulos = []
        for i in range(1, len(partes), 2):
            numero_raw = partes[i]
            numero_match = re.search(r'(\d+[A-Z]?)', numero_raw)
            if not numero_match:
                continue
            numero = numero_match.group(1)

            contenido = partes[i+1].strip()

            articulos.append({
                "codigo": codigo_nombre,
                "articulo": numero,
                "rama": rama,
                "texto": f"Artículo {numero}. {contenido}"
            })

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(articulos, f, ensure_ascii=False, indent=2)

        print(f"✔ {len(articulos)} artículos de {codigo_nombre} guardados en {json_path}")
        return True

    except Exception as e:
        print(f"❌ Error procesando {pdf_path}: {e}")
        return False

# ==================================================
# FUNCIÓN DE CREACIÓN DE ÍNDICE FAISS
# ==================================================

def crear_indice_faiss(codigo_id):
    """
    Crea un índice FAISS y un archivo docs.json a partir de un archivo JSON de artículos.
    """
    json_path = os.path.join(JSON_DIR, f"{codigo_id}.json")
    faiss_code_dir = os.path.join(FAISS_DIR, codigo_id)
    os.makedirs(faiss_code_dir, exist_ok=True)

    print(f"\n🔧 Creando índice FAISS para: {codigo_id}")

    if not os.path.exists(json_path):
        print(f"⚠️ Archivo JSON no encontrado: {json_path}")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not data:
        print(f"⚠️ El archivo {json_path} está vacío. Se omite.")
        return

    textos = [a["texto"] for a in data]
    modelo = SentenceTransformer(EMBEDDING_MODEL)
    embeddings = modelo.encode(textos, show_progress_bar=True)
    embeddings = np.array(embeddings).astype("float32")

    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)

    faiss.write_index(index, os.path.join(faiss_code_dir, "index.faiss"))

    # Guardar los documentos originales para referencia
    with open(os.path.join(faiss_code_dir, "docs.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✔ Índice FAISS para {codigo_id} creado con {len(data)} artículos.")

# ==================================================
# EJECUCIÓN PRINCIPAL
# ==================================================

if __name__ == "__main__":
    print("🚀 Iniciando la construcción de la base de conocimiento...")

    for codigo_info in CODIGOS_A_PROCESAR:
        if parsear_pdf_a_json(codigo_info):
            crear_indice_faiss(codigo_info["id"])

    print("\n✅ Proceso completado.")
