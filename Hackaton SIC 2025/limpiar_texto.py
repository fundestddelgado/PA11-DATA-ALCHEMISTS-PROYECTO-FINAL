import os
import re

TXT_DIR = "Dataset/TXT"

for archivo in os.listdir(TXT_DIR):
    if not archivo.endswith(".txt"):
        continue

    ruta = os.path.join(TXT_DIR, archivo)
    with open(ruta, "r", encoding="utf-8") as f:
        texto = f.read()

    texto = re.sub(r"\n{2,}", "\n", texto)
    texto = re.sub(r"ART[IÍ]CULO", "Artículo", texto, flags=re.I)

    with open(ruta, "w", encoding="utf-8") as f:
        f.write(texto)

    print(f" Limpio: {archivo}")
