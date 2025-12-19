import os

# ==================================================
# CONFIGURACIÓN DE DIRECTORIOS
# ==================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_DIR = os.path.join(BASE_DIR, "Dataset/Codigos")
JSON_DIR = os.path.join(BASE_DIR, "Dataset/JSON")
FAISS_DIR = os.path.join(BASE_DIR, "Dataset/FAISS")

# ==================================================
# CONFIGURACIÓN DE MODELOS
# ==================================================
GEMINI_MODEL = "gemini-1.5-flash"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# ==================================================
# CONFIGURACIÓN DE CÓDIGOS LEGALES
# ==================================================

# Define los códigos que se procesarán en la base de conocimiento
CODIGOS_A_PROCESAR = [
    {
        "id": "codigo_familia",
        "pdf_filename": "codigo_familia.pdf",
        "nombre_completo": "Código de la Familia",
        "rama": "Derecho de Familia",
        "keywords": ["familia", "matrimonio", "alimentos", "adopción", "patria potestad"]
    },
    {
        "id": "codigo_penal",
        "pdf_filename": "codigo_penal.pdf",
        "nombre_completo": "Código Penal",
        "rama": "Derecho Penal",
        "keywords": ["penal", "delito", "pena", "homicidio", "robo", "hurto", "estafa"]
    },
    {
        "id": "codigo_trabajo",
        "pdf_filename": "codigo_trabajo.pdf",
        "nombre_completo": "Código de Trabajo",
        "rama": "Derecho Laboral",
        "keywords": ["trabajo", "laboral", "trabajador", "contrato", "despido", "salario"]
    },
    {
        "id": "codigo_civil",
        "pdf_filename": "codigo_civil.pdf",
        "nombre_completo": "Código Civil",
        "rama": "Derecho Civil",
        "keywords": ["civil", "contrato", "obligación", "propiedad", "herencia"]
    }
]

# Mapeo para la detección de códigos en el chatbot
CODIGOS_CHATBOT = {
    codigo["id"]: codigo["keywords"] for codigo in CODIGOS_A_PROCESAR
}
