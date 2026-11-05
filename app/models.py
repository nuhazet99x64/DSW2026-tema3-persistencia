from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped, mapped_column
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()


class Producto(db.Model):
    __tablename__ = "productos"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(db.String(100), nullable=False)
    precio: Mapped[float] = mapped_column(db.Float, nullable=False)
    disponible: Mapped[bool] = mapped_column(default=True)
    imagen: Mapped[str | None] = mapped_column(db.String(200), nullable=True)

    def __repr__(self):
        return f"Producto id={self.id}: {self.nombre} ({self.precio}€)"


class Usuario(db.Model, UserMixin):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(db.String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(db.String(120), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(db.String(256), nullable=False)
    rol: Mapped[str] = mapped_column(db.String(20), default="cliente", nullable=False)

    def set_password(self, password: str) -> None:
        """Recibe la contraseña en texto plano y almacena su hash seguro."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verifica si la contraseña en texto plano coincide con el hash guardado."""
        return check_password_hash(self.password_hash, password)

    @property
    def es_admin(self) -> bool:
        """Propiedad auxiliar para comprobar rápidamente si el usuario es administrador."""
        return self.rol == "admin"

    def __repr__(self) -> str:
        return f"Usuario id={self.id}: {self.username} ({self.rol})"
