import os
from pathlib import Path

# ======================================================
# CONFIGURACIÓN
# ======================================================
DATA_SPLITS_ROOT = "data_splits" # Carpeta raíz con train, val, test

# ======================================================
# FUNCIÓN PARA LIMPIAR Y RENOMBRAR
# ======================================================
def clean_and_rename_files(root_dir):
    print(f"Procesando directorio: {root_dir}")
    for split_folder in ["train", "val", "test"]:
        split_path = os.path.join(root_dir, split_folder)
        if not os.path.isdir(split_path):
            print(f"  Saltando {split_path}: no existe.")
            continue

        print(f"  Procesando split: {split_folder}")
        for class_folder in os.listdir(split_path):
            class_path = os.path.join(split_path, class_folder)
            if not os.path.isdir(class_path):
                continue

            print(f"    Procesando clase: {class_folder}")
            for filename in os.listdir(class_path):
                old_filepath = os.path.join(class_path, filename)
                if not os.path.isfile(old_filepath):
                    continue

                # Extraer el nombre base sin la parte final "_XXXX" y asegurar .jpg
                # Ejemplo: "A1xubX4gxnL._AC_UL1500_.jpg_10508" -> "A1xubX4gxnL._AC_UL1500_"
                # Ejemplo: "imagen.png" -> "imagen"
                name_parts = filename.split('.')
                base_name = name_parts[0] # Tomamos la primera parte antes del primer punto

                # Si el nombre original ya tenía un .jpg o similar, lo quitamos y lo ponemos al final
                if len(name_parts) > 1 and name_parts[-1].lower().startswith('jpg'):
                    base_name = ".".join(name_parts[:-1]) # Quitamos la última extensión si es jpg_XXXX

                # Limpiar cualquier sufijo numérico o de extensión no estándar
                # Esto es para casos como "nombre.jpg_123" o "nombre.png_456"
                # Buscamos el último '_' seguido de números al final
                if '_' in base_name:
                    parts_with_underscore = base_name.rsplit('_', 1)
                    if len(parts_with_underscore) > 1 and parts_with_underscore[1].isdigit():
                        base_name = parts_with_underscore[0]

                new_filename = f"{base_name}.jpg"
                new_filepath = os.path.join(class_path, new_filename)

                # Evitar renombrar si el nombre ya es el deseado o si el nuevo nombre ya existe
                if old_filepath == new_filepath:
                    continue
                if os.path.exists(new_filepath):
                    # Si el nuevo nombre ya existe (ej. por duplicados), añadir un sufijo único
                    counter = 1
                    temp_new_filename = f"{base_name}_{counter}.jpg"
                    temp_new_filepath = os.path.join(class_path, temp_new_filename)
                    while os.path.exists(temp_new_filepath):
                        counter += 1
                        temp_new_filename = f"{base_name}_{counter}.jpg"
                        temp_new_filepath = os.path.join(class_path, temp_new_filename)
                    new_filepath = temp_new_filepath
                    new_filename = temp_new_filename

                try:
                    os.rename(old_filepath, new_filepath)
                    # print(f"      Renombrado: {filename} -> {new_filename}")
                except Exception as e:
                    print(f"      ERROR al renombrar {filename}: {e}")

    print(f"\n Proceso de limpieza y renombrado completado en {root_dir}.")

# ======================================================
# EJECUTAR EL SCRIPT
# ======================================================
if __name__ == "__main__":
    clean_and_rename_files(DATA_SPLITS_ROOT)