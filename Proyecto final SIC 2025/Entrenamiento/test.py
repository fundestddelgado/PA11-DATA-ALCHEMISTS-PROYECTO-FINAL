import os

TRAIN_DIR = "data_splits/train"

for cls in os.listdir(TRAIN_DIR):
    cls_path = os.path.join(TRAIN_DIR, cls)
    if not os.path.isdir(cls_path):
        continue

    files = [f for f in os.listdir(cls_path) if os.path.isfile(os.path.join(cls_path, f))]
    print(f"\nClase: {cls}  -  {len(files)} archivos encontrados")

    # Muestra solo los primeros 10 para inspeccionar nombres
    for f in files[:10]:
        print("   ", f)

        import os

        print("Working directory:", os.getcwd())
        print("TRAIN_DIR absoluto:", os.path.abspath(TRAIN_DIR))