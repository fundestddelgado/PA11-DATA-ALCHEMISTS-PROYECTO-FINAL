
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

codigo = "codigo_trabajo"

index = faiss.read_index(f"Dataset/FAISS/{codigo}/index.faiss")

with open(f"Dataset/FAISS/{codigo}/docs.json", "r", encoding="utf-8") as f:
    docs = json.load(f)

modelo = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

query = "derechos del trabajador"
vector = modelo.encode([query]).astype("float32")

_, idx = index.search(vector, 3)

for i in idx[0]:
    print(f"\n Artículo {docs[i]['articulo']}")
    print(docs[i]["texto"][:300])
