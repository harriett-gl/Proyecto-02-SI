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

            pedido_id = datos.get("pedido_id")

            return redirect(
                url_for(
                    "pedido_exitoso",
                    id=pedido_id
                )
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
# CLIENTE - PEDIDO REALIZADO
# =========================================================

@app.route("/pedido/exitoso/<int:id>")
@login_requerido
def pedido_exitoso(id):

    try:
        respuesta = requests.get(
            f"{API_URL}/pedidos/{id}",
            timeout=5
        )
        respuesta.raise_for_status()
        pedido = respuesta.json()

        if int(pedido.get("usuario_id", 0)) != int(session["usuario_id"]):
            return redirect(url_for("mis_pedidos"))

    except (requests.RequestException, ValueError, TypeError):
        return redirect(url_for("mis_pedidos"))

    return render_template(
        "pedido_exitoso.html",
        pedido=pedido,
        usuario=usuario_actual()
    )


# =========================================================
# CLIENTE - MIS PEDIDOS
# =========================================================

@app.route("/mis-pedidos")
def mis_pedidos():

    usuario = session.get("usuario")

    if not usuario:
        return redirect(url_for("login"))

    try:
        pagina = request.args.get("pagina", 1, type=int)

        if pagina < 1:
            pagina = 1

        por_pagina = 10

        respuesta = requests.get(
            f"{API_URL}/clientes/{usuario['id']}/pedidos",
            timeout=5
        )

        if respuesta.status_code != 200:

            return render_template(
                "mis_pedidos.html",
                pedidos=[],
                usuario=usuario,
                pagina=1,
                total_paginas=1,
                error="No fue posible cargar tus pedidos."
            )

        pedidos = respuesta.json()

        # Ordenar del pedido más reciente al más antiguo
        pedidos = sorted(
            pedidos,
            key=lambda pedido: pedido.get("id", 0),
            reverse=True
        )

        total_pedidos = len(pedidos)

        total_paginas = max(
            1,
            (total_pedidos + por_pagina - 1) // por_pagina
        )

        # Evitar páginas que no existen
        if pagina > total_paginas:
            pagina = total_paginas

        inicio = (pagina - 1) * por_pagina
        fin = inicio + por_pagina

        pedidos_pagina = pedidos[inicio:fin]

        return render_template(
            "mis_pedidos.html",
            pedidos=pedidos_pagina,
            usuario=usuario,
            pagina=pagina,
            total_paginas=total_paginas,
            total_pedidos=total_pedidos,
            error=None
        )

    except requests.RequestException:

        return render_template(
            "mis_pedidos.html",
            pedidos=[],
            usuario=usuario,
            pagina=1,
            total_paginas=1,
            total_pedidos=0,
            error="No fue posible conectar con la API."
        )


# =========================================================
# CLIENTE - DETALLE DE MI PEDIDO
# =========================================================

@app.route("/mis-pedidos/<int:id>")
@login_requerido
def mi_pedido(id):

    try:
        respuesta = requests.get(
            f"{API_URL}/pedidos/{id}",
            timeout=5
        )
        respuesta.raise_for_status()
        pedido = respuesta.json()

        if int(pedido.get("usuario_id", 0)) != int(session["usuario_id"]):
            return redirect(url_for("mis_pedidos"))

    except (requests.RequestException, ValueError, TypeError):
        return redirect(url_for("mis_pedidos"))

    return render_template(
        "mi_pedido.html",
        pedido=pedido,
        usuario=usuario_actual()
    )

# =========================================================
# CLIENTE - CANCELAR MI PEDIDO
# =========================================================

@app.route(
    "/mis-pedidos/<int:id>/cancelar",
    methods=["POST"]
)
@login_requerido
def cancelar_mi_pedido(id):

    try:

        # Primero comprobamos que realmente sea
        # un pedido del usuario conectado.
        respuesta_pedido = requests.get(
            f"{API_URL}/pedidos/{id}",
            timeout=5
        )

        respuesta_pedido.raise_for_status()

        pedido = respuesta_pedido.json()

        if int(pedido.get("usuario_id", 0)) != int(
            session["usuario_id"]
        ):

            return redirect(
                url_for("mis_pedidos")
            )

        respuesta = requests.put(
            f"{API_URL}/pedidos/{id}/cancelar",
            json={
                "usuario_id": session["usuario_id"]
            },
            timeout=5
        )

        if respuesta.status_code != 200:

            try:
                datos = respuesta.json()
                print(
                    "No se pudo cancelar pedido:",
                    datos.get("error")
                )

            except ValueError:
                print(
                    "No se pudo cancelar el pedido."
                )

    except requests.RequestException as exc:

        print(
            "Error cancelando pedido:",
            exc
        )

    return redirect(
        url_for(
            "mi_pedido",
            id=id
        )
    )


# =========================================================
# CLIENTE - MI CUENTA
# =========================================================

@app.route("/mi-cuenta")
@login_requerido
def mi_cuenta():

    try:

        respuesta = requests.get(
            f"{API_URL}/clientes/{session['usuario_id']}",
            timeout=5
        )

        respuesta.raise_for_status()

        cliente = respuesta.json()

    except (
        requests.RequestException,
        ValueError
    ):

        cliente = {
            "id": session.get("usuario_id"),
            "nombre": session.get(
                "usuario_nombre",
                ""
            ),
            "correo": session.get(
                "usuario",
                {}
            ).get(
                "correo",
                ""
            ),
            "total_pedidos": 0,
            "total_productos": 0,
            "total_gastado": 0
        }

    return render_template(
        "mi_cuenta.html",
        cliente=cliente,
        cantidad_carrito=cantidad_carrito(),
        usuario=usuario_actual()
    )


# =========================================================
# CLIENTE - EDITAR MI CUENTA
# =========================================================

@app.route(
    "/mi-cuenta/editar",
    methods=["GET", "POST"]
)
@login_requerido
def editar_mi_cuenta():

    error = None
    exito = None

    try:

        respuesta_cliente = requests.get(
            f"{API_URL}/clientes/{session['usuario_id']}",
            timeout=5
        )

        respuesta_cliente.raise_for_status()

        cliente = respuesta_cliente.json()

    except (
        requests.RequestException,
        ValueError
    ):

        return redirect(
            url_for("mi_cuenta")
        )

    if request.method == "POST":

        nombre = (
            request.form.get("nombre") or ""
        ).strip()

        correo = (
            request.form.get("correo") or ""
        ).strip().lower()

        if not nombre or not correo:

            error = (
                "Nombre y correo son obligatorios."
            )

        else:

            try:

                respuesta = requests.put(
                    f"{API_URL}/usuarios/{session['usuario_id']}",
                    json={
                        "nombre": nombre,
                        "correo": correo
                    },
                    timeout=5
                )

                datos = respuesta.json()

                if respuesta.status_code == 200:

                    usuario_nuevo = datos[
                        "usuario"
                    ]

                    session["usuario"] = (
                        usuario_nuevo
                    )

                    session[
                        "usuario_nombre"
                    ] = usuario_nuevo[
                        "nombre"
                    ]

                    session.modified = True

                    return redirect(
                        url_for("mi_cuenta")
                    )

                error = datos.get(
                    "error",
                    "No fue posible actualizar tus datos."
                )

            except requests.RequestException:

                error = (
                    "No fue posible conectar con la API."
                )

            except ValueError:

                error = (
                    "La API devolvió una respuesta inválida."
                )

    return render_template(
        "editar_cuenta.html",
        cliente=cliente,
        error=error,
        exito=exito,
        cantidad_carrito=cantidad_carrito(),
        usuario=usuario_actual()
    )


# =========================================================
# CLIENTE - ELIMINAR MI CUENTA
# =========================================================

@app.route(
    "/mi-cuenta/eliminar",
    methods=["POST"]
)
@login_requerido
def eliminar_mi_cuenta():

    try:

        respuesta = requests.delete(
            f"{API_URL}/usuarios/{session['usuario_id']}",
            timeout=5
        )

        datos = respuesta.json()

        if respuesta.status_code == 200:

            session.clear()

            return redirect(
                url_for("inicio")
            )

        mensaje = datos.get(
            "error",
            "No fue posible eliminar la cuenta."
        )

        return redirect(
            url_for(
                "mi_cuenta",
                error=mensaje
            )
        )

    except requests.RequestException:

        return redirect(
            url_for("mi_cuenta")
        )

    except ValueError:

        return redirect(
            url_for("mi_cuenta")
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
# ADMIN - LISTA DE PRODUCTOS
# =========================================================

@app.route("/admin/productos")
@admin_requerido
def admin_productos():

    try:

        productos = obtener_productos()

    except requests.RequestException:

        productos = []

    return render_template(
        "admin_productos.html",
        productos=productos,
        usuario=usuario_actual()
    )


# =========================================================
# ADMIN - PÁGINA EDITAR PRODUCTO
# =========================================================

@app.route("/admin/productos/<int:id>/editar")
@admin_requerido
def admin_editar_producto(id):

    try:

        producto = obtener_producto(id)

    except requests.RequestException:

        return redirect(
            url_for("admin_productos")
        )

    return render_template(
        "admin_editar_producto.html",
        producto=producto,
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

        respuesta = requests.post(
            f"{API_URL}/productos",
            json=datos,
            timeout=5
        )

        respuesta.raise_for_status()

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

        "nombre":
            request.form.get("nombre"),

        "descripcion":
            request.form.get("descripcion"),

        "precio":
            request.form.get("precio"),

        "stock":
            request.form.get("stock"),

        "detalle_producto":
            request.form.get("detalle_producto")
    }

    accion = request.form.get(
        "accion",
        "guardar"
    )

    try:

        respuesta = requests.put(
            f"{API_URL}/productos/{id}",
            json=datos,
            timeout=5
        )

        respuesta.raise_for_status()

    except requests.RequestException as error:

        print(
            "Error editando producto:",
            error
        )

        return redirect(
            url_for(
                "admin_editar_producto",
                id=id
            )
        )

    # -----------------------------------------------------
    # GUARDAR Y VOLVER AL LISTADO
    # -----------------------------------------------------

    if accion == "guardar_volver":

        return redirect(
            url_for("admin_productos")
        )

    # -----------------------------------------------------
    # GUARDAR Y PERMANECER EN EDICIÓN
    # -----------------------------------------------------

    return redirect(
        url_for(
            "admin_editar_producto",
            id=id
        )
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

        respuesta = requests.delete(
            f"{API_URL}/productos/{id}",
            timeout=5
        )

        respuesta.raise_for_status()

    except requests.RequestException as error:

        print(
            "Error eliminando producto:",
            error
        )

    return redirect(
        url_for("admin_productos")
    )


# =========================================================
# ADMIN - CLIENTES
# =========================================================

@app.route("/admin/clientes")
@admin_requerido
def admin_clientes():

    clientes = []
    error = None

    try:

        respuesta = requests.get(
            f"{API_URL}/clientes",
            timeout=5
        )

        respuesta.raise_for_status()
        clientes = respuesta.json()

    except requests.RequestException as exc:

        print("Error obteniendo clientes:", exc)
        error = "No fue posible cargar los clientes."

    except ValueError:

        error = "La API devolvió una respuesta inválida."

    return render_template(
        "admin_clientes.html",
        clientes=clientes,
        error=error,
        usuario=usuario_actual()
    )


# =========================================================
# ADMIN - DETALLE DE CLIENTE
# =========================================================

@app.route("/admin/clientes/<int:id>")
@admin_requerido
def admin_cliente(id):

    try:
        # Página actual
        pagina = request.args.get("pagina", 1, type=int)

        if pagina < 1:
            pagina = 1

        por_pagina = 10

        # Obtener datos del cliente
        respuesta_cliente = requests.get(
            f"{API_URL}/clientes/{id}",
            timeout=5
        )

        respuesta_cliente.raise_for_status()
        cliente = respuesta_cliente.json()

        # Obtener pedidos del cliente
        respuesta_pedidos = requests.get(
            f"{API_URL}/clientes/{id}/pedidos",
            timeout=5
        )

        respuesta_pedidos.raise_for_status()
        pedidos = respuesta_pedidos.json()

        # Ordenar del pedido más reciente al más antiguo
        pedidos = sorted(
            pedidos,
            key=lambda pedido: pedido.get("id", 0),
            reverse=True
        )

        # Total de pedidos
        total_pedidos = len(pedidos)

        # Calcular páginas
        total_paginas = max(
            1,
            (total_pedidos + por_pagina - 1) // por_pagina
        )

        # Evitar páginas inexistentes
        if pagina > total_paginas:
            pagina = total_paginas

        # Obtener solamente los pedidos de esta página
        inicio = (pagina - 1) * por_pagina
        fin = inicio + por_pagina

        pedidos_pagina = pedidos[inicio:fin]

    except requests.RequestException as exc:

        print("Error obteniendo detalle del cliente:", exc)

        return redirect(
            url_for("admin_clientes")
        )

    except ValueError:

        return redirect(
            url_for("admin_clientes")
        )

    return render_template(
        "admin_cliente.html",
        cliente=cliente,
        pedidos=pedidos_pagina,
        usuario=usuario_actual(),
        pagina=pagina,
        total_paginas=total_paginas,
        total_pedidos=total_pedidos
    )


# =========================================================
# ADMIN - PEDIDOS
# =========================================================

@app.route("/admin/pedidos")
@admin_requerido
def admin_pedidos():

    pedidos = []
    error = None

    # Página solicitada
    pagina = request.args.get("pagina", 1, type=int)

    if pagina < 1:
        pagina = 1

    # Máximo 10 pedidos por página
    por_pagina = 10

    try:

        respuesta = requests.get(
            f"{API_URL}/pedidos",
            timeout=5
        )

        respuesta.raise_for_status()

        pedidos = respuesta.json()

        # Ordenar del pedido más reciente al más antiguo
        pedidos = sorted(
            pedidos,
            key=lambda pedido: pedido.get("id", 0),
            reverse=True
        )

    except requests.RequestException as exc:

        print("Error obteniendo pedidos:", exc)
        error = "No fue posible cargar los pedidos."
        pedidos = []

    except ValueError:

        error = "La API devolvió una respuesta inválida."
        pedidos = []


    # =====================================================
    # PAGINACIÓN
    # =====================================================

    total_pedidos = len(pedidos)

    total_paginas = max(
        1,
        (total_pedidos + por_pagina - 1) // por_pagina
    )

    # Evitar acceder a una página inexistente
    if pagina > total_paginas:
        pagina = total_paginas

    inicio = (pagina - 1) * por_pagina
    fin = inicio + por_pagina

    pedidos_pagina = pedidos[inicio:fin]


    # =====================================================
    # RENDER
    # =====================================================

    return render_template(
        "admin_pedidos.html",
        pedidos=pedidos_pagina,
        error=error,
        usuario=usuario_actual(),
        pagina=pagina,
        total_paginas=total_paginas,
        total_pedidos=total_pedidos
    )


# =========================================================
# ADMIN - DETALLE DE PEDIDO
# =========================================================

@app.route("/admin/pedidos/<int:id>")
@admin_requerido
def admin_pedido(id):

    try:

        respuesta = requests.get(
            f"{API_URL}/pedidos/{id}",
            timeout=5
        )

        respuesta.raise_for_status()
        pedido = respuesta.json()

    except requests.RequestException as exc:

        print("Error obteniendo detalle del pedido:", exc)

        return redirect(
            url_for("admin_pedidos")
        )

    except ValueError:

        return redirect(
            url_for("admin_pedidos")
        )

    return render_template(
        "admin_pedido.html",
        pedido=pedido,
        usuario=usuario_actual()
    )


# =========================================================
# ADMIN - ACTUALIZAR ESTADO DEL PEDIDO
# =========================================================

@app.route(
    "/admin/pedidos/<int:id>/estado",
    methods=["POST"]
)
@admin_requerido
def admin_actualizar_estado_pedido(id):

    estado = request.form.get("estado", "").strip().lower()
    estados_validos = {
        "pendiente",
        "procesando",
        "completado",
        "cancelado"
    }

    if estado not in estados_validos:
        return redirect(url_for("admin_pedido", id=id))

    try:
        respuesta = requests.put(
            f"{API_URL}/pedidos/{id}/estado",
            json={"estado": estado},
            timeout=5
        )
        respuesta.raise_for_status()

    except requests.RequestException as exc:
        print("Error actualizando estado del pedido:", exc)

    return redirect(url_for("admin_pedido", id=id))


# =========================================================
# EJECUTAR WEB
# =========================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=8000,
        debug=True
    )