# Archivo: app/config.py
import os
from datetime import timedelta

from dotenv import load_dotenv

# Carga las variables definidas en el archivo .env dentro del entorno del sistema
load_dotenv()


class Config:
    """Configuración centralizada de la aplicación Flask."""

    # 1. Clave secreta leída desde .env (con valor de respaldo solo para desarrollo)
    SECRET_KEY = os.environ.get("SECRET_KEY", "clave-de-desarrollo-insegura")

    # 2. Configuración de Base de Datos SQLAlchemy (Apartado 1)
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///tienda.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 3. Configuración de Subida de Imágenes (Apartado 3)
    UPLOAD_FOLDER = os.path.join("app", "static", "img", "uploads")
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # Límite estricto de 2 MB

    # 4. Duración de la Sesión Permanente del Carrito (Apartado 4.4)
    PERMANENT_SESSION_LIFETIME = timedelta(days=2)
