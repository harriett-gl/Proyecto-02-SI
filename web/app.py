from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session
)

import requests
import os
from dotenv import load_dotenv
from functools import wraps


# =========================================================
# CONFIGURACIÓN
# =========================================================

load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv(
    "SECRET_KEY",
    "techmarket-clave-temporal"
)

API_URL = os.getenv(
    "API_URL",
    "http://api:5001"
)


# =========================================================
# FUNCIONES AUXILIARES
# =========================================================

def obtener_productos():

    respuesta = requests.get(
        f"{API_URL}/productos",
        timeout=5
    )

    respuesta.raise_for_status()

    return respuesta.json()


def obtener_producto(id):

    respuesta = requests.get(
        f"{API_URL}/productos/{id}",
        timeout=5
    )

    respuesta.raise_for_status()

    return respuesta.json()


def cantidad_carrito():

    carrito = session.get("carrito", {})

    return sum(
        int(cantidad)
        for cantidad in carrito.values()
    )


def usuario_actual():

    return session.get("usuario")


# =========================================================
# PROTECCIÓN DE RUTAS
# =========================================================

def login_requerido(func):

    @wraps(func)
    def verificar_login(*args, **kwargs):

        if not session.get("usuario"):
            return redirect(url_for("login"))

        return func(*args, **kwargs)

    return verificar_login


def admin_requerido(func):

    @wraps(func)
    def verificar_admin(*args, **kwargs):

        usuario = session.get("usuario")

        if not usuario:
            return redirect(url_for("login"))

        if usuario.get("rol") != "admin":
            return redirect(url_for("inicio"))

        return func(*args, **kwargs)

    return verificar_admin


# =========================================================
# INICIO
# =========================================================

@app.route("/")
def inicio():

    try:
        productos = obtener_productos()

    except requests.RequestException:
        productos = []

    return render_template(
        "index.html",
        productos=productos,
        cantidad_carrito=cantidad_carrito(),
        usuario=usuario_actual()
    )


# =========================================================
# PRODUCTOS
# =========================================================

@app.route("/productos")
def productos():

    try:
        lista_productos = obtener_productos()

    except requests.RequestException:
        lista_productos = []

    return render_template(
        "index.html",
        productos=lista_productos,
        cantidad_carrito=cantidad_carrito(),
        usuario=usuario_actual()
    )


@app.route("/producto/<int:id>")
def producto(id):

    try:

        producto_encontrado = obtener_producto(id)

    except requests.RequestException:

        return redirect(url_for("inicio"))

    return render_template(
        "producto.html",
        producto=producto_encontrado,
        cantidad_carrito=cantidad_carrito(),
        usuario=usuario_actual()
    )


# =========================================================
# REGISTRO
# =========================================================

@app.route("/registro", methods=["GET", "POST"])
def registro():

    error = None

    if request.method == "POST":

        nombre = request.form.get("nombre")
        correo = request.form.get("correo")
        password = request.form.get("password")
        confirmar_password = request.form.get(
            "confirmar_password"
        )

        if not nombre or not correo or not password:

            error = "Todos los campos son obligatorios."

        elif password != confirmar_password:

            error = "Las contraseñas no coinciden."

        else:

            try:

                respuesta = requests.post(
                    f"{API_URL}/registro",
                    json={
                        "nombre": nombre,
                        "correo": correo,
                        "password": password
                    },
                    timeout=5
                )

                datos = respuesta.json()

                if respuesta.status_code == 201:

                    return redirect(
                        url_for(
                            "login",
                            registrado="1"
                        )
                    )

                error = datos.get(
                    "error",
                    "No fue posible crear la cuenta."
                )

            except requests.RequestException:

                error = "No fue posible conectar con la API."

            except ValueError:

                error = "La API devolvió una respuesta inválida."

    return render_template(
        "registro.html",
        error=error,
        cantidad_carrito=cantidad_carrito(),
        usuario=usuario_actual()
    )


# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    error = None

    registrado = (
        request.args.get("registrado") == "1"
    )

    if request.method == "POST":

        correo = request.form.get("correo")
        password = request.form.get("password")

        if not correo or not password:

            error = "Correo y contraseña son obligatorios."

        else:

            try:

                respuesta = requests.post(
                    f"{API_URL}/login",
                    json={
                        "correo": correo,
                        "password": password
                    },
                    timeout=5
                )

                datos = respuesta.json()

                if respuesta.status_code == 200:

                    usuario = datos.get("usuario")

                    if not usuario:

                        error = (
                            "La API no devolvió "
                            "los datos del usuario."
                        )

                    else:

                        session["usuario"] = usuario
                        session["usuario_id"] = usuario["id"]
                        session["usuario_nombre"] = usuario["nombre"]
                        session["usuario_rol"] = usuario["rol"]

                        if usuario["rol"] == "admin":

                            session["admin"] = True

                            return redirect(
                                url_for("admin")
                            )

                        session.pop(
                            "admin",
                            None
                        )

                        return redirect(
                            url_for("inicio")
                        )

                else:

                    error = datos.get(
                        "error",
                        "Correo o contraseña incorrectos."
                    )

            except requests.RequestException:

                error = "No fue posible conectar con la API."

            except ValueError:

                error = "La API devolvió una respuesta inválida."

    return render_template(
        "login.html",
        error=error,
        registrado=registrado,
        cantidad_carrito=cantidad_carrito(),
        usuario=usuario_actual()
    )


# =========================================================
# CERRAR SESIÓN
# =========================================================

@app.route("/logout")
def logout():

    session.pop("usuario", None)
    session.pop("usuario_id", None)
    session.pop("usuario_nombre", None)
    session.pop("usuario_rol", None)
    session.pop("admin", None)

    return redirect(
        url_for("inicio")
    )


# =========================================================
# CARRITO
# =========================================================

@app.route("/carrito")
def carrito():

    carrito_guardado = session.get(
        "carrito",
        {}
    )

    productos_carrito = []

    total = 0

    for producto_id, cantidad in carrito_guardado.items():

        try:

            producto = obtener_producto(
                producto_id
            )

            cantidad = int(cantidad)

            producto["cantidad"] = cantidad

            subtotal = (
                float(producto["precio"])
                * cantidad
            )

            producto["subtotal"] = subtotal

            total += subtotal

            productos_carrito.append(
                producto
            )

        except requests.RequestException:

            continue

    return render_template(
        "carrito.html",
        productos=productos_carrito,
        total=total,
        cantidad_carrito=cantidad_carrito(),
        usuario=usuario_actual()
    )


# =========================================================
# AGREGAR AL CARRITO
# =========================================================

@app.route(
    "/carrito/agregar/<int:id>",
    methods=["POST"]
)
def agregar_carrito(id):

    carrito = session.get(
        "carrito",
        {}
    )

    producto_id = str(id)

    cantidad = request.form.get(
        "cantidad",
        1
    )

    try:

        cantidad = int(cantidad)

    except (ValueError, TypeError):

        cantidad = 1

    if cantidad < 1:

        cantidad = 1

    carrito[producto_id] = (
        carrito.get(producto_id, 0)
        + cantidad
    )

    session["carrito"] = carrito

    session.modified = True

    return redirect(
        url_for("carrito")
    )


# =========================================================
# ACTUALIZAR CARRITO
# =========================================================

@app.route(
    "/carrito/actualizar/<int:id>",
    methods=["POST"]
)
def actualizar_carrito(id):

    carrito = session.get(
        "carrito",
        {}
    )

    cantidad = request.form.get(
        "cantidad",
        1
    )

    try:

        cantidad = int(cantidad)

    except (ValueError, TypeError):

        cantidad = 1

    if cantidad <= 0:

        carrito.pop(
            str(id),
            None
        )

    else:

        carrito[str(id)] = cantidad

    session["carrito"] = carrito

    session.modified = True

    return redirect(
        url_for("carrito")
    )


# =========================================================
# ELIMINAR DEL CARRITO
# =========================================================

@app.route(
    "/carrito/eliminar/<int:id>",
    methods=["POST"]
)
def eliminar_carrito(id):

    carrito = session.get(
        "carrito",
        {}
    )

    producto_id = str(id)

    if producto_id in carrito:

        carrito.pop(
            producto_id
        )

    session["carrito"] = carrito

    session.modified = True

    return redirect(
        url_for("carrito")
    )


# =========================================================
# VACIAR CARRITO
# =========================================================

@app.route(
    "/carrito/vaciar",
    methods=["POST"]
)
def vaciar_carrito():

    session["carrito"] = {}

    session.modified = True

    return redirect(
        url_for("carrito")
    )


# =========================================================
# REALIZAR PEDIDO
# =========================================================

@app.route(
    "/pedido/realizar",
    methods=["POST"]
)
@login_requerido
def realizar_pedido():

    carrito_guardado = session.get(
        "carrito",
        {}
    )

    if not carrito_guardado:

        return redirect(
            url_for("carrito")
        )

    productos = []

    for producto_id, cantidad in carrito_guardado.items():

        productos.append({
            "producto_id": int(producto_id),
            "cantidad": int(cantidad)
        })

    try:

        respuesta = requests.post(
            f"{API_URL}/pedidos",
            json={
                "usuario_id": session["usuario_id"],
                "productos": productos
            },
            timeout=5
        )

        datos = respuesta.json()

        if respuesta.status_code == 201:

            session["carrito"] = {}

            session.modified = True

            return redirect(
                url_for("inicio")
            )

        print(
            "Error al crear pedido:",
            datos
        )

        return redirect(
            url_for("carrito")
        )

    except requests.RequestException as error:

        print(
            "Error de conexión:",
            error
        )

        return redirect(
            url_for("carrito")
        )


# =========================================================
# PANEL ADMINISTRADOR
# =========================================================

@app.route("/admin")
@admin_requerido
def admin():

    try:

        productos = obtener_productos()

    except requests.RequestException:

        productos = []

    return render_template(
        "admin.html",
        productos=productos,
        usuario=usuario_actual()
    )


# =========================================================
# ADMIN - AGREGAR PRODUCTO
# =========================================================

@app.route(
    "/admin/agregar",
    methods=["POST"]
)
@admin_requerido
def admin_agregar():

    datos = {
        "nombre": request.form.get("nombre"),
        "descripcion": request.form.get("descripcion"),
        "precio": request.form.get("precio"),
        "stock": request.form.get("stock")
    }

    try:

        requests.post(
            f"{API_URL}/productos",
            json=datos,
            timeout=5
        )

    except requests.RequestException as error:

        print(
            "Error agregando producto:",
            error
        )

    return redirect(
        url_for("admin")
    )


# =========================================================
# ADMIN - EDITAR PRODUCTO
# =========================================================

@app.route(
    "/admin/editar/<int:id>",
    methods=["POST"]
)
@admin_requerido
def admin_editar(id):

    datos = {
        "nombre": request.form.get("nombre"),
        "descripcion": request.form.get("descripcion"),
        "precio": request.form.get("precio"),
        "stock": request.form.get("stock")
    }

    try:

        requests.put(
            f"{API_URL}/productos/{id}",
            json=datos,
            timeout=5
        )

    except requests.RequestException as error:

        print(
            "Error editando producto:",
            error
        )

    return redirect(
        url_for("admin")
    )


# =========================================================
# ADMIN - ELIMINAR PRODUCTO
# =========================================================

@app.route(
    "/admin/eliminar/<int:id>",
    methods=["POST"]
)
@admin_requerido
def admin_eliminar(id):

    try:

        requests.delete(
            f"{API_URL}/productos/{id}",
            timeout=5
        )

    except requests.RequestException as error:

        print(
            "Error eliminando producto:",
            error
        )

    return redirect(
        url_for("admin")
    )


# =========================================================
# EJECUTAR WEB
# =========================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=8000,
        debug=True
    )