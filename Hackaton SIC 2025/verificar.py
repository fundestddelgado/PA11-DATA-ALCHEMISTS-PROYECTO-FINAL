import json

with open("Dataset/JSON/codigo_trabajo.json", "r", encoding="utf-8") as f:
    data = json.load(f)

arts = [a for a in data if a["articulo"] == 45]

if arts:
    print(" Artículo 45 OK\n")
    print(arts[0]["texto"][:300])
else:
    print(" Artículo 45 NO encontrado")
