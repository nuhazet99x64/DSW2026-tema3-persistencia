import os
from datetime import timedelta
from functools import wraps

from flask import (
    Flask,
    abort,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_debugtoolbar import DebugToolbarExtension
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from werkzeug.utils import secure_filename

from app.forms import LoginForm, ProductoForm, RegistroForm
from app.models import Producto, Usuario, db

app = Flask(__name__)

# the toolbar is only enabled en debug mode
app.debug = False

app.config["SECRET_KEY"] = "una_contraseña_segura_al_azar"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=2)
toolbar = DebugToolbarExtension(app)

# Configuración de la base de datos (En local = SQLite)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tienda.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config["UPLOAD_FOLDER"] = os.path.join("app", "static", "img", "uploads")
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024

# Vinculamos SQLAlchemy con nuestra aplicación de Flask
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

# indicamos el nombre de la función de vista a la que redirigir si un anónimo intenta entrar a una ruta protegida
login_manager.login_view = "login"
login_manager.login_message = "Pr favor, inicia sesión para acceder a esta sección"
login_manager.login_message_category = "info"


@login_manager.user_loader
def cargar_usuario(user_id):
    """Recupera el objeto Usuario desde tienda.db a partir del ID guardado en la cookie session."""
    return db.session.get(Usuario, int(user_id))


def admin_required(f):
    """Decorador que restringe el acceso exclusivamente a usuarios con rol 'admin'."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 1. Si es un visitante anónimo, lo enviamos al formulario de login
        if not current_user.is_authenticated:
            return login_manager.unauthorized()
        # 2. Si está logueado pero NO es administrador, lanzamos error HTTP 403 (Prohibido)
        if not current_user.es_admin:
            abort(403)
        # 3. Si es admin, ejecutamos la función de vista original con normalidad
        return f(*args, **kwargs)

    return decorated_function


with app.app_context():
    db.create_all()  # Crea las tablas en la base de datos (si no existieran)

    if not Producto.query.first():
        nuevo_producto = Producto(nombre="Teclado Mecánico RGB", precio=49.99)
        db.session.add(nuevo_producto)
        db.session.commit()
        print(">>>> Producto de prueba insertado en la BD. <<<<<<<<<<<<<<<<<<<")

    if not Usuario.query.first():
        admin = Usuario(username="admin", email="admin@tienda.com", rol="admin")
        admin.set_password("admin123")

        cliente = Usuario(username="cliente", email="cliente@tienda.com", rol="cliente")
        cliente.set_password("cliente123")

        db.session.add_all([admin, cliente])
        db.session.commit()
        print(">>> Usuarios de prueba (admin y cliente) creados correctamente.")


@app.route("/")
def home():
    return redirect(url_for("mostrar_catalogo"))


@app.route("/catalogo")
def mostrar_catalogo():
    productos = Producto.query.all()
    return render_template("catalogo.html", lista_productos=productos)


@app.route("/producto/nuevo", methods=["GET", "POST"])
@admin_required
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


@app.route("/producto/<int:prod_id>")
def ver_producto(prod_id):
    # producto = db.get_or_404(Producto, prod_id)

    # respuesta = make_response(
    #     render_template("producto_detalle.html", producto=producto)
    # )

    # respuesta.set_cookie(
    #     "ultimo_visto",
    #     value=producto.nombre,
    #     max_age=60 * 60 * 24 * 7,
    #     httponly=True,
    #     samesite="Lax",
    # )
    return "respuesta"


@app.route("/producto/<int:prod_id>/editar", methods=["GET", "POST"])
@admin_required
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
@admin_required
def eliminar_producto(prod_id):
    producto = db.get_or_404(Producto, prod_id)
    db.session.delete(producto)
    db.session.commit()
    return redirect(url_for("mostrar_catalogo"))


@app.route("/carrito/anadir/<int:prod_id>", methods=["POST"])
@login_required
def anadir_al_carrito(prod_id):
    producto = db.get_or_404(Producto, prod_id)

    session.permanent = True

    if "carrito" not in session:
        session["carrito"] = []

    session["carrito"].append(producto.id)

    session.modified = True

    flash(f"¡'{producto.nombre}' añadido al carrito!", "exito")

    return redirect(url_for("mostrar_catalogo"))


@app.route("/carrito")
@login_required
def ver_carrito():

    ids_carrito = session.get("carrito", [])

    if ids_carrito:
        productos_carrito = Producto.query.filter(Producto.id.in_(ids_carrito)).all()
    else:
        productos_carrito = []

    return render_template("carrito.html", productos=productos_carrito)


@app.route("/carrito/vaciar", methods=["POST"])
@login_required
def vaciar_carrito():
    session.pop("carrito", None)
    flash("Has vaciado tu carrito de la compra.", "info")
    return redirect(url_for("mostrar_catalogo"))


# Ejercicio 1:Eliminar un producto individual del Carrito (session)
@app.route("/carrito/eliminar/<int:prod_id>", methods=["POST"])
def eliminar_producto_carrito(prod_id):

    if prod_id in session["carrito"]:
        session["carrito"].remove(prod_id)
        flash("producto eliminado del carrito", "info")
    else:
        flash("El producto no estaba en el carrito", "warning")
    return redirect(url_for("ver_carrito"))


# 1. REGISTRO DE NUEVOS CLIENTES
@app.route("/registro", methods=["GET", "POST"])
def registro():
    # Si el usuario ya tiene sesión iniciada, lo enviamos al catálogo
    if current_user.is_authenticated:
        return redirect(url_for("mostrar_catalogo"))

    form = RegistroForm()
    if form.validate_on_submit():
        nuevo_usuario = Usuario(
            username=form.username.data,
            email=form.email.data,
            rol="cliente",  # Todo registro público nace con rol 'cliente'
        )
        nuevo_usuario.set_password(form.password.data)

        db.session.add(nuevo_usuario)
        db.session.commit()

        flash("¡Cuenta creada con éxito! Ya puedes iniciar sesión.", "exito")
        return redirect(url_for("login"))

    return render_template("registro.html", form=form)


# 2. INICIO DE SESIÓN (LOGIN)
@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("mostrar_catalogo"))

    form = LoginForm()
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form.email.data).first()

        # Comprobamos que el correo exista y que el hash coincida con la contraseña
        if usuario and usuario.check_password(form.password.data):
            # Registra al usuario en la sesión (y crea cookie persistente si marcó 'remember')
            login_user(usuario, remember=form.remember.data)
            flash(f"¡Bienvenido de nuevo, {usuario.username}!", "exito")

            # Si venía redirigido desde una ruta protegida (parámetro ?next=...), lo devolvemos allí
            siguiente_pagina = request.args.get("next")
            if siguiente_pagina and siguiente_pagina.startswith("/"):
                return redirect(siguiente_pagina)
            return redirect(url_for("mostrar_catalogo"))
        else:
            flash("Correo electrónico o contraseña incorrectos.", "error")

    return render_template("login.html", form=form)


# 3. CIERRE DE SESIÓN (LOGOUT)
@app.route("/logout")
@login_required
def logout():
    logout_user()  # Elimina el ID del usuario de la cookie session
    flash("Has cerrado sesión correctamente.", "info")
    return redirect(url_for("mostrar_catalogo"))


# 4. PERFIL DEL USUARIO
@app.route("/perfil")
@login_required
def perfil():
    return render_template("perfil.html")


if __name__ == "__main__":
    app.run(debug=True)
