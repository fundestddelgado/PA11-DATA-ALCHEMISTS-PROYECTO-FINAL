# Web Clasificador de Imágenes

Este módulo proporciona una interfaz web para interactuar con el modelo de clasificación de imágenes, permitiendo a los usuarios cargar una imagen y recibir una predicción instantánea.

## Descripción General

La aplicación consta de dos partes principales: un backend desarrollado con FastAPI que aloja el modelo de IA y expone una API de predicción, y un frontend simple basado en HTML/JavaScript que permite la interacción del usuario.

## Tecnologías Utilizadas

### Backend
*   **Python**: Lenguaje de programación principal.
*   **FastAPI**: Framework web moderno y rápido para construir APIs.
*   **Uvicorn**: Servidor ASGI para ejecutar la aplicación FastAPI.
*   **TensorFlow/Keras**: Para cargar y ejecutar el modelo de clasificación de imágenes.
*   **Pillow (PIL)**: Para el procesamiento de imágenes.
*   **Numpy**: Para operaciones numéricas.

### Frontend
*   **HTML5**: Estructura de la interfaz de usuario.
*   **JavaScript**: Lógica interactiva para la carga de imágenes, comunicación con el backend y visualización de resultados.
*   **TailwindCSS**: Framework CSS para un diseño rápido y responsivo (cargado vía CDN).

## Estructura del Proyecto

```
Web-Clasificador/
├── Backend/
│   ├── app.py                  # Aplicación FastAPI y lógica de predicción.
│   └── Models/                 # Directorio donde se espera el modelo de Keras (classifier.keras).
├── Frontend/
│   └── index.html              # Interfaz de usuario web.
└── Requirements.txt          # Dependencias de Python para el backend.
```

## Configuración del Entorno y Ejecución

Sigue estos pasos para poner en marcha la aplicación web.

### 1. Preparar el Modelo
El backend espera encontrar el modelo entrenado (`classifier.keras`) en la ruta `Web-Clasificador/Backend/Models/classifier.keras`.

**Acción Requerida:**
Asegúrate de que el modelo `classifier.keras` (generado por el script `Entrenamiento.py` en el directorio principal del proyecto) esté copiado dentro de la carpeta `Web-Clasificador/Backend/Models/`. Si la carpeta `Models` no existe dentro de `Backend`, deberás crearla.

### 2. Instalación de Dependencias (Backend)

Navega al directorio `Web-Clasificador/` y instala las dependencias de Python:

```bash
cd Web-Clasificador
pip install -r Requirements.txt
```

### 3. Iniciar el Backend

Desde el directorio `Web-Clasificador/Backend/`, ejecuta la aplicación FastAPI usando Uvicorn:

```bash
cd Web-Clasificador/Backend
python app.py
# O alternativamente:
# uvicorn app:app --host 0.0.0.0 --port 8000
```
El backend estará disponible en `http://localhost:8000`.

### 4. Acceder al Frontend

Simplemente abre el archivo `index.html` en tu navegador web preferido:

```
file:///C:/Users/WarMachine/PycharmProjects/Proyecto/Web-Clasificador/Frontend/index.html en caso del nuestras pruebas
```

## Uso de la Aplicación Web

1.  **Cargar Imagen**: En la interfaz, haz clic en el área "Selecciona una imagen" o arrastra una imagen (JPG, PNG, WebP) para subirla.
2.  **Vista Previa**: Verás una vista previa de la imagen seleccionada.
3.  **Predecir**: Haz clic en el botón "PREDICIR".
4.  **Resultados**: La aplicación enviará la imagen al backend, el modelo realizará la predicción y los resultados (clase principal, confianza y barras de confianza por categoría) se mostrarán en la sección "Resultados".

## Endpoints de la API (Backend)

La API de FastAPI expone los siguientes endpoints:

*   **`GET /`**: Devuelve un mensaje de bienvenida, el estado de la API y las clases de clasificación configuradas.
*   **`GET /health`**: Proporciona información sobre el estado del servidor, si el modelo se ha cargado correctamente y cualquier error.
*   **`POST /predict`**:
    *   **Método:** `POST`
    *   **Cuerpo:** Archivo de imagen (`UploadFile`)
    *   **Descripción:** Recibe una imagen, la preprocesa, utiliza el modelo cargado para realizar una predicción y devuelve el resultado en formato JSON (clase predicha, confianza y probabilidades por clase).
