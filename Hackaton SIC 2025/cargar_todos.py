import json, glob

articulos = []

for archivo in glob.glob("data/articulos/*.json"):
    with open(archivo, encoding="utf-8") as f:
        articulos.extend(json.load(f))

print(f"✔ Total de artículos cargados: {len(articulos)}")
print(articulos[0]["codigo"], articulos[0]["articulo"])
