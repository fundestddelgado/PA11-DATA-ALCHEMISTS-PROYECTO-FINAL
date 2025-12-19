from langchain_community.document_loaders import PyPDFLoader
import os

PDF_DIR = "Dataset/PDF"
TXT_DIR = "Dataset/TXT"
os.makedirs(TXT_DIR, exist_ok=True)

for archivo in os.listdir(PDF_DIR):
    if not archivo.endswith(".pdf"):
        continue

    ruta_pdf = os.path.join(PDF_DIR, archivo)
    loader = PyPDFLoader(ruta_pdf)
    docs = loader.load()

    texto = "\n".join(d.page_content for d in docs)

    nombre = archivo.replace(".pdf", ".txt")
    with open(os.path.join(TXT_DIR, nombre), "w", encoding="utf-8") as f:
        f.write(texto)

    print(f" Texto extraído: {archivo}")
