import os
import re
import json

TXT_DIR = "Dataset/TXT"
JSON_DIR = "Dataset/JSON"
os.makedirs(JSON_DIR, exist_ok=True)

patron = re.compile(
    r"(Artículo\s+\d+\.)(.*?)(?=Artículo\s+\d+\.|$)",
    re.S
)

for archivo in os.listdir(TXT_DIR):
    if not archivo.endswith(".txt"):
        continue

    codigo = archivo.replace(".txt", "")
    with open(os.path.join(TXT_DIR, archivo), "r", encoding="utf-8") as f:
        texto = f.read()

    articulos = []

    for m in patron.finditer(texto):
        encabezado = m.group(1)
        cuerpo = m.group(2).strip()
        numero = int(re.search(r"\d+", encabezado).group())

        articulos.append({
            "codigo": codigo,
            "rama": codigo.replace("codigo_", ""),
            "articulo": numero,
            "texto": encabezado + " " + cuerpo
        })

    with open(os.path.join(JSON_DIR, f"{codigo}.json"), "w", encoding="utf-8") as f:
        json.dump(articulos, f, ensure_ascii=False, indent=2)

    print(f" {codigo}: {len(articulos)} artículos")
