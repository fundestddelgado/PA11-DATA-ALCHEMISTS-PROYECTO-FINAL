import os
import csv
import requests
from urllib.parse import urlparse
from time import sleep

CSV_PATH = "filtered_for_download.csv"
OUTPUT_ROOT = "data_raw"  # carpeta raíz donde se guardarán las imágenes
MAX_RETRIES = 3
TIMEOUT = 10

os.makedirs(OUTPUT_ROOT, exist_ok=True)

def safe_filename(url, asin=None, idx=None):
    """
    Genera un nombre de archivo seguro a partir de la URL/asin/idx.
    """
    # Intentar usar asin si está
    if asin:
        base = asin
    else:
        # Extraer nombre del path de la URL
        parsed = urlparse(url)
        base = os.path.basename(parsed.path) or "img"
    if idx is not None:
        base = f"{base}_{idx}"
    # Asegurar extensión
    if not os.path.splitext(base)[1]:
        base = base + ".jpg"
    # Limpiar caracteres raros
    base = "".join(c for c in base if c.isalnum() or c in ("_", "-", ".",))
    return base

def download_image(url, out_path):
    for attempt in range(MAX_RETRIES):
        try:
            r = requests.get(url, timeout=TIMEOUT)
            if r.status_code == 200 and r.content:
                with open(out_path, "wb") as f:
                    f.write(r.content)
                return True
        except Exception:
            pass
        sleep(0.5)  # pequeño backoff
    return False

with open(CSV_PATH, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for idx, row in enumerate(reader, start=1):
        url = row.get("image_url")
        cls = row.get("target_class")
        asin = row.get("asin")

        if not url or not cls:
            continue

        class_dir = os.path.join(OUTPUT_ROOT, cls)
        os.makedirs(class_dir, exist_ok=True)

        fname = safe_filename(url, asin=asin, idx=idx)
        out_path = os.path.join(class_dir, fname)

        # Saltar si ya existe (re-ejecución segura)
        if os.path.exists(out_path):
            continue

        ok = download_image(url, out_path)
        if not ok:
            # Podrías loguear en un archivo CSV de errores si quieres
            print(f"Fallo al descargar: {url}")