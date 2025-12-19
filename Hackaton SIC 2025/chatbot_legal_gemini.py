import time
import sys
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted, InvalidArgument

# ========================================================
# 1. CONFIGURACIÓN
# ========================================================
API_KEY = "AIzaSyBhxeidAt3t_yDeLlBuSZw9LI4KguqU3vk"  # <--- PEGA TU KEY AQUÍ
MODEL_NAME = "gemini-2.5-flash"

# Diccionario para guardar respuestas y no repetir llamadas a la API
cache_legal = {
    "hola": "Hola, soy tu asistente legal experto en el Código de la Familia. ¿En qué artículo o trámite puedo ayudarte?",
    "articulo 25 codigo de la familia": "El Artículo 25 del Código de la Familia generalmente se refiere a los requisitos para el matrimonio o deberes conyugales (esto varía según el país, pero la IA lo detallará si hay conexión)."
}

# ========================================================
# 2. INICIALIZACIÓN
# ========================================================
try:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel(MODEL_NAME)
except Exception as e:
    print(f" Error de configuración: {e}")


# ========================================================
# 3. LÓGICA DE INTELIGENCIA ARTIFICIAL
# ========================================================
def llamar_gemini(prompt):
    """Llama a Gemini con manejo de cuotas y reintentos."""
    intentos = 0
    max_intentos = 3
    espera = 15  # Segundos entre reintentos para limpiar la cuota

    while intentos < max_intentos:
        try:
            # Configuración de seguridad para evitar bloqueos por contenido sensible
            safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            ]

            response = model.generate_content(prompt, safety_settings=safety_settings)
            return response.text

        except ResourceExhausted:
            intentos += 1
            print(
                f"⚠ [CUOTA EXCEDIDA] El servidor de Google está saturado. Reintento {intentos}/{max_intentos} en {espera}s...")
            time.sleep(espera)
            espera += 5  # Incrementamos el tiempo si sigue fallando

        except InvalidArgument as e:
            return f" Error: La API Key no es válida o está mal configurada. {e}"

        except Exception as e:
            return f" Error inesperado: {str(e)}"

    return " No se pudo obtener respuesta tras varios intentos por límites de Google (Plan Gratuito)."


# ========================================================
# 4. PROCESAMIENTO LEGAL
# ========================================================
def consultar_asistente(pregunta):
    pregunta_limpia = pregunta.lower().strip()

    # Paso A: Revisar si la respuesta ya está en Caché
    if pregunta_limpia in cache_legal:
        print("[INFO] Respuesta recuperada de memoria local (Sin gasto de API).")
        return cache_legal[pregunta_limpia]

    # Paso B: Preparar el Prompt para la IA
    prompt_legal = f"""
    Eres un Abogado Virtual experto. Tu tarea es responder consultas sobre leyes.

    INSTRUCCIONES:
    1. Si el usuario pregunta por un artículo específico (ej. Art. 25 del Código de la Familia), cítalo textualmente si es posible.
    2. Si no estás seguro, indica que el usuario debe consultar el Registro Oficial.
    3. Responde de forma profesional.

    CONSULTA: {pregunta}
    """

    # Paso C: Llamar a la IA
    print(f"[INFO] Consultando a {MODEL_NAME}...")
    respuesta = llamar_gemini(prompt_legal)

    # Guardar en caché si la respuesta es exitosa
    if "" not in respuesta:
        cache_legal[pregunta_limpia] = respuesta

    return respuesta


# ========================================================
# 5. INTERFAZ DE CONSOLA
# ========================================================
def main():
    print("\n" + "=" * 40)
    print("⚖️  ASISTENTE LEGAL VIRTUAL (GEMINI)")
    print("=" * 40)
    print("Escribe tu duda legal o 'salir' para finalizar.\n")

    while True:
        usuario = input("Consulta legal > ")

        if usuario.lower() in ["salir", "exit", "quit"]:
            print("Cerrando sistema legal. ¡Buena suerte en la hackatón!")
            break

        if not usuario.strip():
            continue

        respuesta = consultar_asistente(usuario)

        print("\n" + "-" * 20 + " RESPUESTA " + "-" * 20)
        print(respuesta)
        print("-" * 51 + "\n")


if __name__ == "__main__":
    main()