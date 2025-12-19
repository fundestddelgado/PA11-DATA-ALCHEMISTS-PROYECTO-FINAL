import os
import sys
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from PIL import Image

# =====================================================
# CONFIGURACIÓN
# =====================================================
MODEL_PATH = "models/V1/mobilenetv2_amazon.keras"  # o .h5 si lo prefieres
IMG_SIZE = (224, 224)

# IMPORTANTE: pon aquí el mismo orden que viste en train_ds.class_names
CLASS_NAMES = ["amazon_fashion", "electronics", "video_games"]  # <-- AJUSTA ESTO

# =====================================================
# CARGAR MODELO
# =====================================================
if not os.path.exists(MODEL_PATH):
    print(f"ERROR: No se encontró el modelo en: {MODEL_PATH}")
    sys.exit(1)

print(f"Cargando modelo desde {MODEL_PATH} ...")
model = keras.models.load_model(MODEL_PATH)
print("Modelo cargado correctamente.\n")


# =====================================================
# FUNCIÓN PARA PREPROCESAR UNA IMAGEN
# =====================================================
def load_and_preprocess_image(img_path):
    """
    Carga una imagen desde disco y la prepara para MobileNetV2.
    """
    if not os.path.exists(img_path):
        raise FileNotFoundError(f"No se encontró la imagen: {img_path}")

    # Cargar con PIL
    img = Image.open(img_path).convert("RGB")
    img = img.resize(IMG_SIZE)

    img_array = np.array(img, dtype=np.float32)

    # Añadimos batch dimension
    img_array = np.expand_dims(img_array, axis=0)

    # Preprocesado de MobileNetV2
    img_array = keras.applications.mobilenet_v2.preprocess_input(img_array)
    return img_array


# =====================================================
# FUNCIÓN DE PREDICCIÓN
# =====================================================
def predict_image(img_path):
    img_array = load_and_preprocess_image(img_path)

    # Predicción
    preds = model.predict(img_array)
    probs = tf.nn.softmax(preds[0]).numpy()

    top_idx = int(np.argmax(probs))
    top_class = CLASS_NAMES[top_idx]
    top_prob = probs[top_idx]

    # Mostrar resultados
    print(f"Imagen: {img_path}")
    print("Probabilidades por clase:")
    for i, (cls, p) in enumerate(zip(CLASS_NAMES, probs)):
        print(f"  {i}: {cls:15s} -> {p*100:6.2f}%")

    print(f"\nPredicción final: {top_class} ({top_prob*100:.2f}% de confianza)")
    return top_class, top_prob



if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python predecir_imagen.py ruta/a/imagen.jpg")
        sys.exit(1)

    image_path = sys.argv[1]
    predict_image(image_path)