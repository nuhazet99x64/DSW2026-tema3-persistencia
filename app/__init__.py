# Archivo: app/__init__.py
from flask import Flask, render_template

from app.config import Config
from app.models import Producto, Usuario, db, login_manager


def create_app(config_class=Config):
    """Factoría de aplicaciones: ensambla y devuelve la instancia de Flask."""
    app = Flask(__name__)

    # 1. Cargamos toda la configuración desde la clase Config (app/config.py)
    app.config.from_object(config_class)

    # 2. Vinculamos las extensiones con la instancia actual de la aplicación
    db.init_app(app)
    login_manager.init_app(app)

    # 3. Importamos y registramos los Blueprints
    from app.blueprints.admin import admin_bp
    from app.blueprints.auth import auth_bp
    from app.blueprints.public import public_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)

    # 4. Registro global de errores personalizados (403 y 404)
    @app.errorhandler(403)
    def acceso_prohibido(e):
        return render_template("403.html"), 403

    @app.errorhandler(404)
    def pagina_no_encontrada(e):
        return render_template("404.html"), 404

    # 5. Creación de tablas y semilla inicial controlada
    with app.app_context():
        db.create_all()

        if not Producto.query.first():
            prod_inicial = Producto(
                nombre="Teclado Mecánico RGB", precio=49.99, disponible=True
            )
            db.session.add(prod_inicial)
            db.session.commit()

        if not Usuario.query.first():
            admin = Usuario(username="admin", email="admin@tienda.com", rol="admin")
            admin.set_password("admin123")
            cliente = Usuario(
                username="cliente", email="cliente@tienda.com", rol="cliente"
            )
            cliente.set_password("cliente123")
            db.session.add_all([admin, cliente])
            db.session.commit()

    return app
