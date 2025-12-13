# Módulo de Entrenamiento y Pruebas del Modelo

Este directorio contiene los scripts y recursos necesarios para entrenar, evaluar y utilizar el modelo de clasificación de imágenes.

## Descripción General

El objetivo es entrenar un modelo capaz de clasificar imágenes en categorías predefinidas (ej. `electronics`, `video_games`). El flujo de trabajo se basa en los siguientes pasos:
1.  **Entrenamiento**: Utilizar un conjunto de datos pre-procesado para entrenar un modelo de Deep Learning.
2.  **Evaluación**: Medir el rendimiento del modelo en un conjunto de datos de prueba que no ha visto antes.
3.  **Predicción**: Usar el modelo entrenado para clasificar nuevas imágenes.

## Estructura de Archivos

-   `Entrenamiento.py`: Script principal que carga los datos, construye el modelo usando Transfer Learning (MobileNetV2), lo entrena y lo guarda.
-   `predecir.py`: Script para cargar un modelo ya entrenado y realizar una predicción sobre una imagen nueva.
-   `test.py`: Script de utilidad para verificar la estructura y contenido del directorio de entrenamiento.
-   `data_splits/`: Directorio que debe contener los datos separados en `train/`, `val/` y `test/`.
-   `models/`: Directorio donde se guardan los modelos entrenados.
-   `Pruebas/`: Directorio con imágenes de ejemplo para realizar predicciones.

---

## Flujo de Trabajo

### 1. Prerrequisitos

-   Asegúrate de tener Python y las dependencias del proyecto instaladas. Se recomienda utilizar un entorno virtual.
-   El conjunto de datos debe estar previamente organizado y dividido en las carpetas `data_splits/train`, `data_splits/val` y `data_splits/test`. Cada una de estas carpetas debe contener subdirectorios con el nombre de cada clase.

### 2. Entrenamiento del Modelo

El script `Entrenamiento.py` se encarga de todo el proceso de forma automática. Al ejecutarlo, realizará los siguientes pasos:
-   Carga los datos desde `data_splits`.
-   Construye un modelo basado en MobileNetV2 pre-entrenado en ImageNet.
-   Realiza un entrenamiento en dos fases: primero con el `backbone` congelado y luego un `fine-tuning` de las capas superiores.
-   Evalúa el modelo final con el conjunto de `test` y muestra la precisión, una matriz de confusión y un reporte de clasificación.
-   Guarda el modelo entrenado en `models/classifier.keras` y también en el formato `models/classifier_savedmodel`.

**Para iniciar el entrenamiento, ejecuta:**
```bash
python Entrenamiento.py
```

### 3. Realizar Predicciones

Una vez que el modelo ha sido entrenado, puedes usar `predecir.py` para clasificar una imagen individual.

**Nota**: El script `predecir.py` puede tener una ruta de modelo (`MODEL_PATH`) y nombres de clases (`CLASS_NAMES`) pre-configurados. Asegúrate de que coincidan con el modelo que deseas usar y las clases de tu dataset. Por ejemplo, para usar el modelo recién entrenado, actualiza la ruta en el script a `models/classifier.keras`.

**Para hacer una predicción, pasa la ruta de la imagen como argumento:**
```bash
python predecir.py ruta/a/tu/imagen.jpg
```

**Ejemplo usando una imagen del directorio `Pruebas`:**
```bash
python predecir.py Pruebas/images.jpg
```

El script imprimirá la clase predicha y el porcentaje de confianza para cada categoría.
