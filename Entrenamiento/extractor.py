
import os, io, json, gzip, glob
from urllib.parse import urlparse
from tqdm import tqdm
import pandas as pd

# --- CONFIG --- ajusta estas rutas
META_DIR = "amazon_meta"  # carpeta donde descargaste los meta/*.gz
OUT_CSV = "amazon_image_urls.csv"  # destino CSV temporal en Colab
FILE_PATTERNS = ["*.json.gz", "*.json", "*.jsonl", "*.gz", "*.txt"]  # patrones a buscar
MAX_ITEMS = None  # <--- VUELVE A NONE para procesar TODO


# ---------------

def is_valid_image_url(u: str):
    if not u or not isinstance(u, str):
        return False
    u = u.strip()
    if u == "" or u.lower().startswith("http") is False:
        return False
    # ext check (jpg, jpeg, png, webp, gif) - no obligatorio, pero ayuda a filtrar urls no imagen
    parsed = urlparse(u)
    path = parsed.path.lower()
    if any(path.endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".webp", ".gif"]):
        return True
    # permitimos URLs sin extensión (servicios que generan imagenes)
    if "images" in path or "img" in path or "media" in path:
        return True
    return False


def extract_urls_from_obj(obj):
    """Recorre recursivamente el objeto JSON buscando valores tipo str que parezcan URLs de imagen,
       y devuelve una lista de ellas (sin duplicados)."""
    found = set()
    if obj is None:
        return []
    if isinstance(obj, str):
        if is_valid_image_url(obj):
            found.add(obj.strip())
        return list(found)
    if isinstance(obj, dict):
        for k, v in obj.items():
            # nombres comunes que suelen contener imágenes
            if isinstance(v, str) and is_valid_image_url(v):
                found.add(v.strip())
            elif isinstance(v, (list, dict)):
                for u in extract_urls_from_obj(v):
                    found.add(u)
            else:
                # si es otro tipo, recursar para seguridad
                for u in extract_urls_from_obj(v):
                    found.add(u)
    elif isinstance(obj, list):
        for item in obj:
            for u in extract_urls_from_obj(item):
                found.add(u)
    return list(found)


def parse_line_json(line):
    try:
        return json.loads(line)
    except Exception:
        return None


def handle_obj(obj, source_file, results):
    """Extrae asin, category y urls; agrega filas a results; devuelve número de filas agregadas"""
    if not isinstance(obj, dict):
        return 0
    asin = obj.get("asin") or obj.get("product_id") or obj.get("ASIN") or None
    # intentar obtener alguna representación de categoría
    category = None
    # campos posibles
    for key in ["category", "categories", "category_tree", "product_category", "group", "node"]:
        if key in obj and obj[key]:
            category = obj[key]
            break
    # si categories es list/arr, intentar aplanar a string
    if isinstance(category, list):
        try:
            # algunas estructuras son listas anidadas: [['Electronics', ...]]
            if len(category) > 0:
                if isinstance(category[0], list):
                    category = " / ".join(map(str, category[0]))
                else:
                    category = " / ".join(map(str, category))
        except Exception:
            category = str(category)
    # extraer urls
    urls = extract_urls_from_obj(obj)
    rows_added = 0
    for u in urls:
        if not is_valid_image_url(u):
            continue
        # normalizar
        u = u.strip()
        results.append({
            "asin": asin,
            "category": category,
            "image_url": u,
            "source_file": source_file
        })
        rows_added += 1
    return rows_added


def process_file(path, results, max_items=None):
    """
    MODIFICADA: Procesa un archivo, extrae datos, y ahora maneja errores de parseo
    por línea para evitar que el archivo problemático detenga todo el proceso.
    """
    processed = 0
    basename = os.path.basename(path)
    open_fn = gzip.open if path.endswith(".gz") else open
    mode = "rt"

    try:
        with open_fn(path, mode, encoding="utf-8", errors="ignore") as f:
            lines = list(f)

            # Intentar primero cargar como JSON Array completo si el archivo es pequeño o comienza con '['
            if len(lines) < 1000 and lines[0].strip().startswith("["):
                try:
                    whole = "".join(lines)
                    arr = json.loads(whole)
                    if isinstance(arr, list):
                        print(f"[INFO] Procesando {basename} como JSON Array completo.")
                        for obj in arr:
                            proc = handle_obj(obj, basename, results)
                            if proc:
                                processed += proc
                                if max_items and processed >= max_items:
                                    return processed
                        return processed
                except Exception as e:
                    print(
                        f"[WARN] Falló la carga del archivo {basename} como JSON Array: {e}. Intentando línea por línea.")

            # Si no fue JSON Array, o si falló, intentar línea por línea (LDJSON)
            for line in lines:
                if not line or line.strip() == "":
                    continue

                data = None
                try:
                    data = parse_line_json(line)
                except Exception as e:
                    # Esto ocurre si la línea no es un JSON válido
                    print(f"[WARN] Falló el parseo de una línea en {basename}: {e}")
                    continue

                if data is not None:
                    proc = handle_obj(data, basename, results)
                    if proc:
                        processed += proc
                        if max_items and processed >= max_items:
                            return processed
                else:
                    # Esta línea es un caso extremo que debería ser cubierto por la excepción anterior
                    # Pero se mantiene si parse_line_json devuelve None silenciosamente
                    continue

    except Exception as e:
        # Aquí se captura si falla al abrir el archivo (ej. permisos o archivo corrupto)
        print(f"[ERROR CRÍTICO] Falló procesando archivo {path}: {e}. SALTANDO ARCHIVO.")

    return processed


# --- Recolectar archivos a procesar ---
files = []
for pat in FILE_PATTERNS:
    files.extend(glob.glob(os.path.join(META_DIR, pat)))
files = sorted(list(set(files)))
print(f"Archivos encontrados: {len(files)}")
if len(files) == 0:
    raise SystemExit(f"No se encontraron archivos en {META_DIR}. Revisa la ruta o patrones.")

results = []
total_processed = 0
for p in tqdm(files, desc="Archivos"):
    added = process_file(p, results, max_items=MAX_ITEMS)
    total_processed += added
    # si se usa limite global
    if MAX_ITEMS and total_processed >= MAX_ITEMS:
        break

print(f"URLs extraídas (raw): {len(results)}")

# --- Limpiar y deduplicar ---
df = pd.DataFrame(results)
if df.empty:
    print("No se extrajeron URLs válidas.")
else:
    # quitar filas sin URL válida
    df = df[df["image_url"].notna()].copy()
    # quitar urls que no parezcan imagen
    df = df[df["image_url"].apply(is_valid_image_url)].copy()
    # normalizar asin y category a string
    df["asin"] = df["asin"].astype(str).replace("None", "")
    df["category"] = df["category"].astype(str).replace("None", "")
    # deduplicar por image_url (mantener primera aparición)
    df = df.drop_duplicates(subset=["image_url"])
    df = df.reset_index(drop=True)
    print("Filas finales únicas:", len(df))
    # Guardar CSV
    df.to_csv(OUT_CSV, index=False)
    print("CSV guardado en:", OUT_CSV)
    print(df.head(20))