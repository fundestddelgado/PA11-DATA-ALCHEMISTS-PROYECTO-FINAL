import os
import collections
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from sklearn.metrics import confusion_matrix, classification_report

# -----------------------------------------------------
# CONFIGURACIÓN BÁSICA
# -----------------------------------------------------
DATA_ROOT = "data_splits"   # carpeta con train/val/test
IMG_SIZE = (224, 224)
BATCH_SIZE = 32
SEED = 42
NUM_CLASSES = 2  # electronics, videogames

# -----------------------------------------------------
# CREAR DATASETS A PARTIR DE DIRECTORIOS
# -----------------------------------------------------
train_dir = os.path.join(DATA_ROOT, "train")
val_dir = os.path.join(DATA_ROOT, "val")
test_dir = os.path.join(DATA_ROOT, "test")

print("Cargando dataset de entrenamiento...")
train_ds = keras.utils.image_dataset_from_directory(
    train_dir,
    labels="inferred",
    label_mode="int",
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    shuffle=True,
    seed=SEED
)

print("Cargando dataset de validación...")
val_ds = keras.utils.image_dataset_from_directory(
    val_dir,
    labels="inferred",
    label_mode="int",
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    shuffle=False
)

print("Cargando dataset de test...")
test_ds = keras.utils.image_dataset_from_directory(
    test_dir,
    labels="inferred",
    label_mode="int",
    image_size=IMG_SIZE,
    batch_size=BATCH_SIZE,
    shuffle=False
)

class_names = train_ds.class_names
print(f"\nClases detectadas: {class_names}")

# ======================================================
# DISTRIBUCIÓN DE CLASES
# ======================================================
counter = collections.Counter()
for _, labels in train_ds.unbatch():
    counter[int(labels.numpy())] += 1

print("\nDistribución de clases en TRAIN (label_id: count):")
print(counter)

# ======================================================
# OPTIMIZACIÓN DE INPUT PIPELINE
# ======================================================
AUTOTUNE = tf.data.AUTOTUNE
train_ds = train_ds.cache().shuffle(1000).prefetch(AUTOTUNE)
val_ds = val_ds.cache().prefetch(AUTOTUNE)
test_ds = test_ds.cache().prefetch(AUTOTUNE)

# ======================================================
# DATA AUGMENTATION
# ======================================================
data_augmentation = keras.Sequential(
    [
        layers.RandomFlip("horizontal"),
        layers.RandomRotation(0.1),
        layers.RandomZoom(0.15),
        layers.RandomContrast(0.1),
        layers.RandomTranslation(0.1, 0.1),
    ],
    name="data_augmentation",
)

# ======================================================
# MODELO CON TRANSFER LEARNING: MobileNetV2
# ======================================================
base_model = keras.applications.MobileNetV2(
    input_shape=IMG_SIZE + (3,),
    include_top=False,
    weights="imagenet"
)
base_model.trainable = False

inputs = keras.Input(shape=IMG_SIZE + (3,))
x = data_augmentation(inputs)
x = keras.applications.mobilenet_v2.preprocess_input(x)
x = base_model(x, training=False)
x = layers.GlobalAveragePooling2D()(x)
x = layers.Dropout(0.5)(x)
outputs = layers.Dense(NUM_CLASSES, activation="softmax")(x)

model = keras.Model(inputs, outputs, name="mobilenetv2_classifier")

model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=1e-3),
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)

model.summary()

# ======================================================
# ENTRENAMIENTO FASE 1: BACKBONE CONGELADO
# ======================================================
EPOCHS_FROZEN = 5

print("\n===== ENTRENANDO (backbone congelado) =====")
history1 = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=EPOCHS_FROZEN,
)

# ======================================================
# FINE-TUNING: DESCONGELAR PARTE SUPERIOR DEL BACKBONE
# ======================================================
base_model.trainable = True

fine_tune_at = int(len(base_model.layers) * 0.85)
for layer in base_model.layers[:fine_tune_at]:
    layer.trainable = False

model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=5e-5),
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)

early_stop = keras.callbacks.EarlyStopping(
    monitor="val_loss",
    patience=3,
    restore_best_weights=True
)

EPOCHS_FT = 20

print("\n===== FINE-TUNING (últimas capas del backbone) =====")
history2 = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=EPOCHS_FT,
    callbacks=[early_stop],
)

# ======================================================
# EVALUACIÓN EN TEST
# ======================================================
print("\n===== EVALUANDO EN TEST =====")
test_loss, test_acc = model.evaluate(test_ds)
print(f"Test accuracy: {test_acc:.4f}  -  Test loss: {test_loss:.4f}")

# ======================================================
# MATRIZ DE CONFUSIÓN Y REPORTE
# ======================================================
y_true = []
y_pred = []

for images, labels in test_ds:
    preds = model.predict(images)
    y_true.extend(labels.numpy())
    y_pred.extend(np.argmax(preds, axis=1))

y_true = np.array(y_true)
y_pred = np.array(y_pred)

print("\nMatriz de confusión:")
print(confusion_matrix(y_true, y_pred))

print("\nReporte de clasificación:")
print(classification_report(y_true, y_pred, target_names=class_names))

# ======================================================
# GUARDAR MODELO - SOLO SAVEDMODEL (evita problemas con .h5)
# ======================================================
os.makedirs("models", exist_ok=True)

# Guardar en formato SavedModel (recomendado)
model.export("models/classifier_savedmodel")
print("\n Modelo guardado en: models/classifier_savedmodel")

# También guardar en formato .keras (nuevo formato nativo de Keras 3)
model.save("models/classifier.keras")
print(" Modelo guardado en: models/classifier.keras")

print("\n Entrenamiento completado")