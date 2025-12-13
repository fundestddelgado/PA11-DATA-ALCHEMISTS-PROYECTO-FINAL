import os
import shutil

# ======================================================
# CONFIGURACIÓN
# ======================================================
DATA_SPLITS_ROOT = "data_splits"
CLASS_TO_REMOVE = "amazon_fashion"
BACKUP_DIR = "data_splits_backup_fashion_removed"  # Carpeta para guardar lo eliminado


# ======================================================
# FUNCIÓN PARA ELIMINAR CLASE
# ======================================================
def remove_class_from_splits(root_dir, class_name):
    print(f"Eliminando la clase '{class_name}' de los splits en {root_dir}...")

    backup_root = os.path.join(root_dir, BACKUP_DIR)
    os.makedirs(backup_root, exist_ok=True)

    for split_folder in ["train", "val", "test"]:
        class_path = os.path.join(root_dir, split_folder, class_name)

        if os.path.exists(class_path) and os.path.isdir(class_path):
            print(f"  Moviendo '{class_path}' a backup...")
            # Mover la carpeta completa a un backup
            shutil.move(class_path, os.path.join(backup_root, split_folder + "_" + class_name))
            print(f"  Carpeta '{class_path}' eliminada.")
        else:
            print(f"  Carpeta '{class_path}' no encontrada, saltando.")

    print(f"\n Clase '{class_name}' eliminada de todos los splits.")
    print(f"   Copia de seguridad guardada en: {backup_root}")


# ======================================================
# EJECUTAR EL SCRIPT
# ======================================================
if __name__ == "__main__":
    remove_class_from_splits(DATA_SPLITS_ROOT, CLASS_TO_REMOVE)