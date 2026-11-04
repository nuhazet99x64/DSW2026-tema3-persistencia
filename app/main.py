import os

from flask import Flask, redirect, render_template, url_for
from werkzeug.utils import secure_filename

from app.forms import ProductoForm
from app.models import Producto, db

app = Flask(__name__)
app.config["SECRET_KEY"] = "una_contraseña_segura_al_azar"

# Configuración de la base de datos (En local = SQLite)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tienda.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config["UPLOAD_FOLDER"] = os.path.join("app", "static", "img", "uploads")
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024

# Vinculamos SQLAlchemy con nuestra aplicación de Flask
db.init_app(app)

with app.app_context():
    db.create_all()  # Crea las tablas en la base de datos (si no existieran)

    if not Producto.query.first():
        nuevo_producto = Producto(nombre="Teclado Mecánico RGB", precio=49.99)
        db.session.add(nuevo_producto)
        db.session.commit()
        print(">>>> Producto de prueba insertado en la BD. <<<<<<<<<<<<<<<<<<<")


@app.route("/")
def home():
    return redirect(url_for("mostrar_catalogo"))


@app.route("/catalogo")
def mostrar_catalogo():
    productos = Producto.query.all()
    return render_template("catalogo.html", lista_productos=productos)


@app.route("/producto/nuevo", methods=["GET", "POST"])
def crear_producto():
    form = ProductoForm()
    if form.validate_on_submit():
        nombre_imagen = None
        # Llega con POST

        # procesar el upload de la imagen
        if form.imagen.data:  # checkea si se ha subido una imagen
            archivo = form.imagen.data
            nombre_imagen = secure_filename(archivo.filename)

            # Asegurar que la ruta existe
            os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

            # Guardar el fichero
            archivo.save(os.path.join(app.config["UPLOAD_FOLDER"], nombre_imagen))

        nuevo_producto = Producto(
            nombre=form.nombre.data,
            precio=form.precio.data,
            disponible=form.disponible.data,
            imagen=nombre_imagen if form.imagen.data else None,
        )

        db.session.add(nuevo_producto)
        db.session.commit()
        # Patrón PRG: redirigir después de procesar.
        return redirect(url_for("mostrar_catalogo"))

    # Llega con GET
    return render_template("producto_form.html", form=form, titulo="Nuevo Producto")


@app.route("/producto/<int:prod_id>/editar", methods=["GET", "POST"])
def editar_producto(prod_id):
    producto = db.get_or_404(Producto, prod_id)

    form = ProductoForm(obj=producto)
    # procesar el upload de la imagen
    if form.imagen.data:  # checkea si se ha subido una imagen
        archivo = form.imagen.data
        nombre_imagen = secure_filename(archivo.filename)

        # Asegurar que la ruta existe
        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

        # Guardar el fichero
        archivo.save(os.path.join(app.config["UPLOAD_FOLDER"], nombre_imagen))

    if form.validate_on_submit():
        producto.nombre = form.nombre.data
        producto.precio = form.precio.data
        producto.disponible = form.disponible.data
        producto.imagen = nombre_imagen if form.imagen.data else None

        db.session.commit()
        return redirect(url_for("mostrar_catalogo"))

    return render_template("producto_form.html", form=form, titulo="Editar producto")


@app.route("/producto/<int:prod_id>/eliminar", methods=["POST"])
def eliminar_producto(prod_id):
    producto = db.get_or_404(Producto, prod_id)
    db.session.delete(producto)
    db.session.commit()
    return redirect(url_for("mostrar_catalogo"))


if __name__ == "__main__":
    app.run(debug=True)
