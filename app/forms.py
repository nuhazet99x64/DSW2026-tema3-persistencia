# Archivo: app/forms.py
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import BooleanField, FloatField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange


class ProductoForm(FlaskForm):
    nombre = StringField(
        "Nombre del Producto",
        validators=[
            DataRequired(message="El nombre es obligatorio."),
            Length(min=3, max=100, message="Debe tener entre 3 y 100 caracteres."),
        ],
    )
    precio = FloatField(
        "Precio (€)",
        validators=[
            DataRequired(
                message="El precio es obligatorio (usa punto para los decimales)."
            ),
            NumberRange(min=0.01, message="El precio debe ser mayor que 0."),
        ],
    )
    disponible = BooleanField("Disponible en stock", default=True)
    imagen = FileField(
        "Imagen del producto",
        validators=[
            FileAllowed(["jpg", "png", "jpeg"], "Solo se permite imagenes (JPG,PNG)")
        ],
    )
    submit = SubmitField("Guardar Producto")
