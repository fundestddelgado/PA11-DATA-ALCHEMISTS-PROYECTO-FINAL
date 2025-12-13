from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import numpy as np
import io
import tensorflow as tf

app = FastAPI(title="Image Classifier API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ======================================================
# CONFIGURACIÓN
# ======================================================
CLASSES = ["electronics", "videogames"]
IMG_SIZE = (224, 224)

# AHORA USAMOS EL ARCHIVO .keras
MODEL_PATH = "models/classifier.keras"

# ======================================================
# CARGAR MODELO
# ======================================================
print(f"🔍 Cargando modelo desde: {MODEL_PATH}")

try:
    # En Keras 3, .keras es el formato recomendado
    model = tf.keras.models.load_model(MODEL_PATH, compile=False)
    print("✅ Modelo cargado correctamente")
    print(f"   Input shape: {model.input_shape}")
    print(f"   Output shape: {model.output_shape}")
    load_error = None
except Exception as e:
    print(f"❌ Error al cargar el modelo: {e}")
    model = None
    load_error = str(e)

# ======================================================
# ENDPOINTS
# ======================================================
@app.get("/")
def root():
    return {
        "message": "API de clasificación de imágenes",
        "status": "online",
        "classes": CLASSES
    }

@app.get("/health")
def health():
    return {
        "status": "ok",
        "model_loaded": model is not None,
        "img_size": IMG_SIZE,
        "classes": CLASSES,
        "error": load_error,
    }

def preprocess_image(img: Image.Image) -> np.ndarray:
    """
    Preprocesa la imagen exactamente como en el entrenamiento.
    """
    img = img.convert("RGB")
    img = img.resize(IMG_SIZE)
    arr = np.array(img, dtype=np.float32)
    arr = np.expand_dims(arr, axis=0)
    # Mismo preprocesado que MobileNetV2
    arr = tf.keras.applications.mobilenet_v2.preprocess_input(arr)
    return arr

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    if model is None:
        return {
            "success": False,
            "error": "model not loaded",
            "detail": load_error,
        }

    try:
        content = await file.read()
        img = Image.open(io.BytesIO(content))

        x = preprocess_image(img)
        preds = model.predict(x, verbose=0)

        preds = np.array(preds).flatten()
        probs = tf.nn.softmax(preds).numpy()

        results = {}
        for i, class_name in enumerate(CLASSES):
            results[class_name] = round(float(probs[i]) * 100, 2)

        top_idx = int(np.argmax(probs))
        top_class = CLASSES[top_idx]
        top_conf = float(probs[top_idx]) * 100

        return {
            "success": True,
            "top_class": top_class,
            "confidence": round(top_conf, 2),
            "results": results,
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": "prediction failed",
            "detail": str(e),
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)