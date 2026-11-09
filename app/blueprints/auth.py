# Archivo: app/blueprints/auth.py
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.forms import LoginForm, RegistroForm
from app.models import Usuario, db

# Todas las rutas de este Blueprint comenzarán automáticamente por /auth/...
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/registro", methods=["GET", "POST"])
def registro():
    if current_user.is_authenticated:
        return redirect(url_for("public.mostrar_catalogo"))

    form = RegistroForm()
    if form.validate_on_submit():
        nuevo_usuario = Usuario(
            username=form.username.data,
            email=form.email.data,
            rol="cliente",
        )
        nuevo_usuario.set_password(form.password.data)
        db.session.add(nuevo_usuario)
        db.session.commit()
        flash("¡Cuenta creada con éxito! Ya puedes iniciar sesión.", "exito")
        return redirect(url_for("auth.login"))

    return render_template("registro.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("public.mostrar_catalogo"))

    form = LoginForm()
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form.email.data).first()
        if usuario and usuario.check_password(form.password.data):
            login_user(usuario, remember=form.remember.data)
            flash(f"¡Bienvenido de nuevo, {usuario.username}!", "exito")

            siguiente_pagina = request.args.get("next")
            if siguiente_pagina and siguiente_pagina.startswith("/"):
                return redirect(siguiente_pagina)
            return redirect(url_for("public.mostrar_catalogo"))
        else:
            flash("Correo electrónico o contraseña incorrectos.", "error")

    return render_template("login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Has cerrado sesión correctamente.", "info")
    return redirect(url_for("public.mostrar_catalogo"))


@auth_bp.route("/perfil")
@login_required
def perfil():
    return render_template("perfil.html")
