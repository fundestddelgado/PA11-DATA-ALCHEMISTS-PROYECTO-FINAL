import os
import random
import shutil
from pathlib import Path

# ======================================================
# CONFIGURACIÓN
# ======================================================
TRAIN_DIR = "data_splits/train"
BACKUP_DIR = "data_splits/train_backup_removed"  # aquí se guardan las que quitamos
SEED = 42

random.seed(SEED)

# ======================================================
# CONTAR IMÁGENES POR CLASE
# ======================================================
classes = [d for d in os.listdir(TRAIN_DIR) if os.path.isdir(os.path.join(TRAIN_DIR, d))]
class_counts = {}

print("Distribución ANTES del balanceo:")
for cls in classes:
    cls_path = os.path.join(TRAIN_DIR, cls)
    images = [f for f in os.listdir(cls_path) if os.path.isfile(os.path.join(cls_path, f))]
    class_counts[cls] = len(images)
    print(f"  {cls}: {len(images)} imágenes")

# ======================================================
# IDENTIFICAR CLASE MINORITARIA
# ======================================================
min_count = min(class_counts.values())
print(f"\nClase minoritaria tiene: {min_count} imágenes")
print(f"Reduciendo todas las clases a {min_count} imágenes...\n")

# ======================================================
# UNDERSAMPLING
# ======================================================
os.makedirs(BACKUP_DIR, exist_ok=True)

for cls in classes:
    cls_path = os.path.join(TRAIN_DIR, cls)
    backup_cls_path = os.path.join(BACKUP_DIR, cls)
    os.makedirs(backup_cls_path, exist_ok=True)

    images = [f for f in os.listdir(cls_path) if os.path.isfile(os.path.join(cls_path, f))]
    current_count = len(images)

    if current_count <= min_count:
        print(f"✓ {cls}: ya tiene {current_count} imágenes (≤ {min_count}), no se toca")
        continue

    # Cuántas hay que quitar
    to_remove = current_count - min_count

    # Seleccionar aleatoriamente las que se van al backup
    random.shuffle(images)
    images_to_remove = images[:to_remove]

    print(f"→ {cls}: moviendo {to_remove} imágenes al backup...")

    for img in images_to_remove:
        src = os.path.join(cls_path, img)
        dst = os.path.join(backup_cls_path, img)
        shutil.move(src, dst)

    print(f"  {cls}: ahora tiene {min_count} imágenes")

# ======================================================
# VERIFICAR RESULTADO
# ======================================================
print("\n" + "=" * 50)
print("Distribución DESPUÉS del balanceo:")
for cls in classes:
    cls_path = os.path.join(TRAIN_DIR, cls)
    images = [f for f in os.listdir(cls_path) if os.path.isfile(os.path.join(cls_path, f))]
    print(f"  {cls}: {len(images)} imágenes")

print("\n Balanceo completado.")
print(f"   Las imágenes removidas están en: {BACKUP_DIR}")
print("   Puedes reentrenar el modelo ahora con el dataset balanceado.")