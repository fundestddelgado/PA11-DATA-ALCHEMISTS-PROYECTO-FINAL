# filter_three_classes.py
# Uso: python filter_three_classes.py
# Ajusta rutas y TARGET_PER_CLASS abajo según necesites.

import os
import pandas as pd
import re

# ---------- CONFIG ----------
CSV_PATH = "amazon_image_urls.csv"        # <- ruta a tu CSV original
OUT_CSV = "filtered_for_download.csv"    # <- CSV resultante listo para descarga
TARGET_CLASSES = {
    "electronics": ["electronics", "electronic", "electro", "electronics.jsonl", "electronics.json", "electronics.gz"],
    "video_games": ["video_games", "video-games", "video games", "video_game", "videogames", "video_games.json", "games"],
    "amazon_fashion": ["amazon_fashion", "amazon-fashion", "fashion", "clothing", "apparel", "Amazon_Fashion"]
}
TARGET_PER_CLASS = 5000   # <-- máximo por clase (ajusta a lo que quieras)
RANDOM_SEED = 42
# --------------------------------

def match_any(text, keywords):
    if not isinstance(text, str):
        return False
    t = text.lower()
    for k in keywords:
        if k.lower() in t:
            return True
    return False

def infer_class_from_row(row):
    # revisar source_file y category y asin fallback
    sf = row.get("source_file", "")
    cat = row.get("category", "")
    # priorizar source_file (suele indicar la categoría original)
    for cls, keys in TARGET_CLASSES.items():
        if match_any(sf, keys) or match_any(cat, keys):
            return cls
    return None

def main():
    if not os.path.exists(CSV_PATH):
        raise SystemExit(f"No encuentro {CSV_PATH} en este directorio. Ajusta CSV_PATH en el script.")

    print("Leyendo CSV (esto puede tardar según el tamaño)...")
    # leemos solo las columnas necesarias para ahorrar memoria
    df = pd.read_csv(CSV_PATH, usecols=["asin","category","image_url","source_file"], dtype=str, low_memory=True)
    print("Filas originales:", len(df))

    # limpiar nulos y espacios
    df = df.dropna(subset=["image_url"]).copy()
    df["image_url"] = df["image_url"].str.strip()
    df = df[df["image_url"] != ""].reset_index(drop=True)
    print("Filas tras quitar URLs vacías:", len(df))

    # inferir clase objetivo para cada fila
    df["target_class"] = df.apply(infer_class_from_row, axis=1)

    # quedarnos solo con las 3 clases deseadas
    df_k = df[df["target_class"].notna()].copy()
    print("Filas que coinciden con las 3 clases objetivo:", len(df_k))

    # quitar duplicados estrictos por URL (mantener primera aparición)
    before = len(df_k)
    df_k = df_k.drop_duplicates(subset=["image_url"]).reset_index(drop=True)
    print(f"Duplicados por URL eliminados: {before - len(df_k)} -> quedan {len(df_k)}")

    # agrupar por clase y samplear hasta TARGET_PER_CLASS
    selected_frames = []
    for cls in sorted(df_k["target_class"].unique()):
        group = df_k[df_k["target_class"] == cls].copy()
        count = len(group)
        take = min(count, TARGET_PER_CLASS)
        print(f"Clase {cls}: {count} URLs disponibles, se tomarán {take}")
        if count > take:
            # muestreo aleatorio para diversidad
            group = group.sample(n=take, random_state=RANDOM_SEED).reset_index(drop=True)
        selected_frames.append(group)

    if not selected_frames:
        raise SystemExit("No se encontraron filas para las clases objetivo. Revisa las palabras clave en TARGET_CLASSES.")

    df_out = pd.concat(selected_frames).reset_index(drop=True)
    # barajar para evitar orden por clase
    df_out = df_out.sample(frac=1.0, random_state=RANDOM_SEED).reset_index(drop=True)

    # Guardar CSV listo para usar con el downloader (tiene asin, category, image_url, source_file, target_class)
    df_out.to_csv(OUT_CSV, index=False)
    print(f"CSV filtrado guardado en: {OUT_CSV}")
    print("Resumen final por clase:")
    print(df_out["target_class"].value_counts())

    # Mostrar primeras filas como ejemplo
    print("\nEjemplos (primeras 10 filas):")
    print(df_out[["asin","target_class","image_url","source_file"]].head(10).to_string(index=False))

if __name__ == "__main__":
    main()
