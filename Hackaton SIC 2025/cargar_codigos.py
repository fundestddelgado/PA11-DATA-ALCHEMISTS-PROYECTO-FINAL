import os
from langchain_community.document_loaders import PyPDFLoader

RUTA = "Dataset/Codigos"

for archivo in os.listdir(RUTA):
    if archivo.endswith(".pdf"):
        ruta_pdf = os.path.join(RUTA, archivo)
        loader = PyPDFLoader(ruta_pdf)
        documentos = loader.load()

        print(f"{archivo} -> {len(documentos)} páginas cargadas")
