from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped, mapped_column

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
