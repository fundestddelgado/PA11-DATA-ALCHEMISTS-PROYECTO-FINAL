import os
import tensorflow as tf

# ============================================
# CONFIGURACIÓN
# ============================================
DATA_ROOT = "data_splits"  # carpeta donde están train/val/test
IMG_SIZE = (224, 224)      # tamaño de entrada para el modelo
BATCH_SIZE = 32

# ============================================
# CREAR DATASETS
# ============================================
train_dir = os.path.join(DATA_ROOT, "train")
val_dir = os.path.join(DATA_ROOT, "val")
test_dir = os.path.join(DATA_ROOT, "test")

print("Cargando dataset de entrenamiento...")
train_ds = tf.keras.utils.image_dataset_from_directory(
    train_dir,
    labels="inferred",
    label_mode="int",
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    shuffle=True,
    seed=42
)

print("Cargando dataset de validación...")
val_ds = tf.keras.utils.image_dataset_from_directory(
    val_dir,
    labels="inferred",
    label_mode="int",
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    shuffle=False
)

print("Cargando dataset de test...")
test_ds = tf.keras.utils.image_dataset_from_directory(
    test_dir,
    labels="inferred",
    label_mode="int",
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    shuffle=False
)

# Obtener nombres de clases
class_names = train_ds.class_names
print(f"\nClases detectadas: {class_names}")
print(f"Número de clases: {len(class_names)}")

# ============================================
# OPTIMIZACIÓN DE RENDIMIENTO
# ============================================
AUTOTUNE = tf.data.AUTOTUNE

train_ds = train_ds.cache().shuffle(1000).prefetch(AUTOTUNE)
val_ds = val_ds.cache().prefetch(AUTOTUNE)
test_ds = test_ds.cache().prefetch(AUTOTUNE)

print("\n Datasets creados exitosamente")
print(f"   - Train batches: {tf.data.experimental.cardinality(train_ds).numpy()}")
print(f"   - Val batches: {tf.data.experimental.cardinality(val_ds).numpy()}")
print(f"   - Test batches: {tf.data.experimental.cardinality(test_ds).numpy()}")