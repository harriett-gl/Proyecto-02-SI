from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
import os


load_dotenv()

app = Flask(__name__)
CORS(app)


# =========================================================
# CONEXIÓN MYSQL
# =========================================================

def conectar_db():

    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )


# =========================================================
# INICIO API
# =========================================================

@app.route("/")
def inicio():

    return jsonify({
        "mensaje": "API TechMarket funcionando correctamente"
    }), 200

# ============================================================
# PRODUCTOS - OBTENER TODOS
# ============================================================

@app.route("/productos", methods=["GET"])
def obtener_productos():

    conexion = None
    cursor = None

    try:

        conexion = conectar_db()

        cursor = conexion.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                id,
                nombre,
                descripcion,
                precio,
                stock,
                detalle_producto
            FROM productos
            ORDER BY id ASC
        """)

        productos = cursor.fetchall()

        return jsonify(productos), 200

    except Exception as e:

        print("ERROR AL OBTENER PRODUCTOS:", e)

        return jsonify({
            "error": "No se pudieron obtener los productos",
            "detalle": str(e)
        }), 500

    finally:

        if cursor:
            cursor.close()

        if conexion:
            conexion.close()

# =========================================================
# PRODUCTOS - OBTENER UNO
# =========================================================

@app.route("/productos/<int:id>", methods=["GET"])
def obtener_producto(id):

    conexion = None
    cursor = None

    try:

        conexion = conectar_db()

        cursor = conexion.cursor(
            dictionary=True
        )

        cursor.execute("""
            SELECT
                id,
                nombre,
                descripcion,
                precio,
                stock,
                detalle_producto
            FROM productos
            WHERE id = %s
        """, (id,))

        producto = cursor.fetchone()

        if not producto:

            return jsonify({
                "error": "Producto no encontrado"
            }), 404

        return jsonify(producto), 200

    except Error as e:

        return jsonify({
            "error": str(e)
        }), 500

    finally:

        if cursor:
            cursor.close()

        if conexion and conexion.is_connected():
            conexion.close()

# =========================================================
# PRODUCTOS - CREAR
# =========================================================

@app.route("/productos", methods=["POST"])
def crear_producto():

    conexion = None
    cursor = None

    try:

        datos = request.get_json() or {}

        nombre = datos.get("nombre")
        descripcion = datos.get("descripcion")
        precio = datos.get("precio")
        stock = datos.get("stock")

        if not nombre or precio is None or stock is None:

            return jsonify({
                "error": "Faltan datos obligatorios"
            }), 400

        conexion = conectar_db()
        cursor = conexion.cursor()

        cursor.execute("""
            INSERT INTO productos (
                nombre,
                descripcion,
                precio,
                stock
            )
            VALUES (%s, %s, %s, %s)
        """, (
            nombre,
            descripcion,
            precio,
            stock
        ))

        conexion.commit()

        return jsonify({
            "mensaje": "Producto creado correctamente",
            "id": cursor.lastrowid
        }), 201

    except Error as e:

        if conexion:
            conexion.rollback()

        return jsonify({
            "error": str(e)
        }), 500

    finally:

        if cursor:
            cursor.close()

        if conexion and conexion.is_connected():
            conexion.close()


# =========================================================
# PRODUCTOS - ACTUALIZAR
# =========================================================

@app.route("/productos/<int:id>", methods=["PUT"])
def actualizar_producto(id):

    conexion = None
    cursor = None

    try:

        datos = request.get_json() or {}

        nombre = datos.get("nombre")
        descripcion = datos.get("descripcion")
        precio = datos.get("precio")
        stock = datos.get("stock")
        detalle_producto = datos.get("detalle_producto")

        if not nombre or precio is None or stock is None:

            return jsonify({
                "error": "Faltan datos obligatorios"
            }), 400

        conexion = conectar_db()
        cursor = conexion.cursor()

        cursor.execute("""
            UPDATE productos
            SET
                nombre = %s,
                descripcion = %s,
                precio = %s,
                stock = %s,
                detalle_producto = %s
            WHERE id = %s
        """, (
            nombre,
            descripcion,
            precio,
            stock,
            detalle_producto,
            id
        ))

        conexion.commit()

        if cursor.rowcount == 0:

            return jsonify({
                "error": "Producto no encontrado"
            }), 404

        return jsonify({
            "mensaje": "Producto actualizado correctamente"
        }), 200

    except Error as e:

        if conexion:
            conexion.rollback()

        return jsonify({
            "error": str(e)
        }), 500

    finally:

        if cursor:
            cursor.close()

        if conexion and conexion.is_connected():
            conexion.close()

# =========================================================
# PRODUCTOS - ELIMINAR
# =========================================================

@app.route("/productos/<int:id>", methods=["DELETE"])
def eliminar_producto(id):

    conexion = None
    cursor = None

    try:

        conexion = conectar_db()
        cursor = conexion.cursor()

        cursor.execute(
            "DELETE FROM productos WHERE id = %s",
            (id,)
        )

        conexion.commit()

        if cursor.rowcount == 0:

            return jsonify({
                "error": "Producto no encontrado"
            }), 404

        return jsonify({
            "mensaje": "Producto eliminado correctamente"
        }), 200

    except Error as e:

        if conexion:
            conexion.rollback()

        return jsonify({
            "error": str(e)
        }), 500

    finally:

        if cursor:
            cursor.close()

        if conexion and conexion.is_connected():
            conexion.close()


# =========================================================
# PEDIDOS - OBTENER TODOS
# =========================================================

@app.route("/pedidos", methods=["GET"])
def obtener_pedidos():

    conexion = None
    cursor = None

    try:

        conexion = conectar_db()
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                p.id,
                p.usuario_id,
                u.nombre AS cliente_nombre,
                u.correo AS cliente_correo,
                p.total,
                p.estado,
                COALESCE(SUM(dp.cantidad), 0) AS unidades
            FROM pedidos p
            INNER JOIN usuarios u
                ON u.id = p.usuario_id
            LEFT JOIN detalle_pedido dp
                ON dp.pedido_id = p.id
            GROUP BY
                p.id,
                p.usuario_id,
                u.nombre,
                u.correo,
                p.total,
                p.estado
            ORDER BY p.id DESC
        """)

        pedidos = cursor.fetchall()

        for pedido in pedidos:
            pedido["total"] = float(pedido["total"])
            pedido["unidades"] = int(pedido["unidades"])

        return jsonify(pedidos), 200

    except Error as e:

        return jsonify({
            "error": str(e)
        }), 500

    finally:

        if cursor:
            cursor.close()

        if conexion and conexion.is_connected():
            conexion.close()


# =========================================================
# PEDIDOS - CREAR
# =========================================================

@app.route("/pedidos", methods=["POST"])
def crear_pedido():

    conexion = None
    cursor = None

    try:

        datos = request.get_json()

        if not datos:

            return jsonify({
                "error": "No se enviaron datos"
            }), 400

        usuario_id = datos.get("usuario_id")
        productos = datos.get("productos")

        if not usuario_id or not productos:

            return jsonify({
                "error": "usuario_id y productos son obligatorios"
            }), 400

        conexion = conectar_db()
        cursor = conexion.cursor(dictionary=True)

        total = 0
        detalles = []

        for item in productos:

            producto_id = item.get("producto_id")
            cantidad = item.get("cantidad")

            if not producto_id or not cantidad or cantidad <= 0:

                conexion.rollback()

                return jsonify({
                    "error": "Producto o cantidad inválida"
                }), 400

            cursor.execute("""
                SELECT id, nombre, precio, stock
                FROM productos
                WHERE id = %s
            """, (producto_id,))

            producto = cursor.fetchone()

            if not producto:

                conexion.rollback()

                return jsonify({
                    "error":
                    f"Producto {producto_id} no encontrado"
                }), 404

            if producto["stock"] < cantidad:

                conexion.rollback()

                return jsonify({
                    "error":
                    f"Stock insuficiente para {producto['nombre']}"
                }), 400

            precio = producto["precio"]
            subtotal = precio * cantidad
            total += subtotal

            detalles.append({
                "producto_id": producto_id,
                "cantidad": cantidad,
                "precio": precio,
                "subtotal": subtotal
            })

        cursor.execute("""
            INSERT INTO pedidos (
                usuario_id,
                total,
                estado
            )
            VALUES (%s, %s, %s)
        """, (
            usuario_id,
            total,
            "pendiente"
        ))

        pedido_id = cursor.lastrowid

        for detalle in detalles:

            cursor.execute("""
                INSERT INTO detalle_pedido (
                    pedido_id,
                    producto_id,
                    cantidad,
                    precio_unitario,
                    subtotal
                )
                VALUES (%s, %s, %s, %s, %s)
            """, (
                pedido_id,
                detalle["producto_id"],
                detalle["cantidad"],
                detalle["precio"],
                detalle["subtotal"]
            ))

            cursor.execute("""
                UPDATE productos
                SET stock = stock - %s
                WHERE id = %s
            """, (
                detalle["cantidad"],
                detalle["producto_id"]
            ))

        conexion.commit()

        return jsonify({
            "mensaje": "Pedido creado correctamente",
            "pedido_id": pedido_id,
            "total": float(total)
        }), 201

    except Error as e:

        if conexion:
            conexion.rollback()

        return jsonify({
            "error": str(e)
        }), 500

    finally:

        if cursor:
            cursor.close()

        if conexion and conexion.is_connected():
            conexion.close()


# =========================================================
# USUARIOS - REGISTRO
# =========================================================

@app.route("/registro", methods=["POST"])
def registro():

    conexion = None
    cursor = None

    try:

        datos = request.get_json()

        nombre = datos.get("nombre")
        correo = datos.get("correo") or datos.get("email")
        password = datos.get("password")

        if not nombre or not correo or not password:

            return jsonify({
                "error":
                "Nombre, correo y password son obligatorios"
            }), 400

        conexion = conectar_db()
        cursor = conexion.cursor(dictionary=True)

        cursor.execute(
            "SELECT id FROM usuarios WHERE correo = %s",
            (correo,)
        )

        if cursor.fetchone():

            return jsonify({
                "error": "El correo ya está registrado"
            }), 409

        password_hash = generate_password_hash(password)

        cursor.execute("""
            INSERT INTO usuarios (
                nombre,
                correo,
                password,
                rol
            )
            VALUES (%s, %s, %s, %s)
        """, (
            nombre,
            correo,
            password_hash,
            "cliente"
        ))

        conexion.commit()

        return jsonify({
            "mensaje": "Usuario registrado correctamente",
            "usuario_id": cursor.lastrowid
        }), 201

    except Error as e:

        if conexion:
            conexion.rollback()

        return jsonify({
            "error": str(e)
        }), 500

    finally:

        if cursor:
            cursor.close()

        if conexion and conexion.is_connected():
            conexion.close()


# =========================================================
# USUARIOS - LOGIN
# =========================================================

@app.route("/login", methods=["POST"])
def login():

    conexion = None
    cursor = None

    try:

        datos = request.get_json()

        correo = datos.get("correo") or datos.get("email")
        password = datos.get("password")

        if not correo or not password:

            return jsonify({
                "error":
                "Correo y password son obligatorios"
            }), 400

        conexion = conectar_db()
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                id,
                nombre,
                correo,
                password,
                rol
            FROM usuarios
            WHERE correo = %s
        """, (correo,))

        usuario = cursor.fetchone()

        if usuario is None:

            return jsonify({
                "error":
                "Correo o contraseña incorrectos"
            }), 401

        if not check_password_hash(
            usuario["password"],
            password
        ):

            return jsonify({
                "error":
                "Correo o contraseña incorrectos"
            }), 401

        return jsonify({
            "mensaje": "Inicio de sesión correcto",

            "usuario": {
                "id": usuario["id"],
                "nombre": usuario["nombre"],
                "correo": usuario["correo"],
                "rol": usuario["rol"]
            }

        }), 200

    except Error as e:

        return jsonify({
            "error": str(e)
        }), 500

    finally:

        if cursor:
            cursor.close()

        if conexion and conexion.is_connected():
            conexion.close()


# =========================================================
# CLIENTES - OBTENER TODOS CON RESUMEN DE COMPRAS
# =========================================================

@app.route("/clientes", methods=["GET"])
def obtener_clientes():

    conexion = None
    cursor = None

    try:

        conexion = conectar_db()
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                u.id,
                u.nombre,
                u.correo,
                COUNT(DISTINCT p.id) AS total_pedidos,
                COALESCE(SUM(dp.cantidad), 0) AS total_productos,
                COALESCE(SUM(dp.subtotal), 0) AS total_gastado
            FROM usuarios u
            LEFT JOIN pedidos p
                ON p.usuario_id = u.id
            LEFT JOIN detalle_pedido dp
                ON dp.pedido_id = p.id
            WHERE u.rol = 'cliente'
            GROUP BY
                u.id,
                u.nombre,
                u.correo
            ORDER BY u.nombre ASC
        """)

        clientes = cursor.fetchall()

        for cliente in clientes:
            cliente["total_pedidos"] = int(cliente["total_pedidos"])
            cliente["total_productos"] = int(cliente["total_productos"])
            cliente["total_gastado"] = float(cliente["total_gastado"])

        return jsonify(clientes), 200

    except Error as e:

        return jsonify({
            "error": str(e)
        }), 500

    finally:

        if cursor:
            cursor.close()

        if conexion and conexion.is_connected():
            conexion.close()


# =========================================================
# CLIENTES - OBTENER UNO CON RESUMEN
# =========================================================

@app.route("/clientes/<int:id>", methods=["GET"])
def obtener_cliente(id):

    conexion = None
    cursor = None

    try:

        conexion = conectar_db()
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                u.id,
                u.nombre,
                u.correo,
                COUNT(DISTINCT p.id) AS total_pedidos,
                COALESCE(SUM(dp.cantidad), 0) AS total_productos,
                COALESCE(SUM(dp.subtotal), 0) AS total_gastado
            FROM usuarios u
            LEFT JOIN pedidos p
                ON p.usuario_id = u.id
            LEFT JOIN detalle_pedido dp
                ON dp.pedido_id = p.id
            WHERE u.id = %s
              AND u.rol = 'cliente'
            GROUP BY
                u.id,
                u.nombre,
                u.correo
        """, (id,))

        cliente = cursor.fetchone()

        if not cliente:

            return jsonify({
                "error": "Cliente no encontrado"
            }), 404

        cliente["total_pedidos"] = int(cliente["total_pedidos"])
        cliente["total_productos"] = int(cliente["total_productos"])
        cliente["total_gastado"] = float(cliente["total_gastado"])

        return jsonify(cliente), 200

    except Error as e:

        return jsonify({
            "error": str(e)
        }), 500

    finally:

        if cursor:
            cursor.close()

        if conexion and conexion.is_connected():
            conexion.close()


# =========================================================
# CLIENTES - HISTORIAL DE PEDIDOS
# =========================================================

@app.route("/clientes/<int:id>/pedidos", methods=["GET"])
def obtener_pedidos_cliente(id):

    conexion = None
    cursor = None

    try:

        conexion = conectar_db()
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                p.id,
                p.usuario_id,
                p.total,
                p.estado,
                COALESCE(SUM(dp.cantidad), 0) AS unidades
            FROM pedidos p
            LEFT JOIN detalle_pedido dp
                ON dp.pedido_id = p.id
            WHERE p.usuario_id = %s
            GROUP BY
                p.id,
                p.usuario_id,
                p.total,
                p.estado
            ORDER BY p.id DESC
        """, (id,))

        pedidos = cursor.fetchall()

        for pedido in pedidos:
            pedido["total"] = float(pedido["total"])
            pedido["unidades"] = int(pedido["unidades"])

        return jsonify(pedidos), 200

    except Error as e:

        return jsonify({
            "error": str(e)
        }), 500

    finally:

        if cursor:
            cursor.close()

        if conexion and conexion.is_connected():
            conexion.close()


# =========================================================
# PEDIDOS - OBTENER DETALLE DE UNO
# =========================================================

@app.route("/pedidos/<int:id>", methods=["GET"])
def obtener_detalle_pedido(id):

    conexion = None
    cursor = None

    try:

        conexion = conectar_db()
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                p.id,
                p.usuario_id,
                p.total,
                p.estado,
                u.nombre AS cliente_nombre,
                u.correo AS cliente_correo
            FROM pedidos p
            INNER JOIN usuarios u
                ON u.id = p.usuario_id
            WHERE p.id = %s
        """, (id,))

        pedido = cursor.fetchone()

        if not pedido:

            return jsonify({
                "error": "Pedido no encontrado"
            }), 404

        cursor.execute("""
            SELECT
                dp.producto_id,
                pr.nombre AS producto_nombre,
                dp.cantidad,
                dp.precio_unitario,
                dp.subtotal
            FROM detalle_pedido dp
            INNER JOIN productos pr
                ON pr.id = dp.producto_id
            WHERE dp.pedido_id = %s
            ORDER BY dp.producto_id ASC
        """, (id,))

        detalles = cursor.fetchall()

        pedido["total"] = float(pedido["total"])

        for detalle in detalles:
            detalle["precio_unitario"] = float(detalle["precio_unitario"])
            detalle["subtotal"] = float(detalle["subtotal"])
            detalle["cantidad"] = int(detalle["cantidad"])

        pedido["productos"] = detalles

        return jsonify(pedido), 200

    except Error as e:

        return jsonify({
            "error": str(e)
        }), 500

    finally:

        if cursor:
            cursor.close()

        if conexion and conexion.is_connected():
            conexion.close()

# =========================================================
# USUARIO - ACTUALIZAR DATOS PERSONALES
# =========================================================

@app.route("/usuarios/<int:id>", methods=["PUT"])
def actualizar_usuario(id):

    conexion = None
    cursor = None

    try:

        datos = request.get_json() or {}

        nombre = (datos.get("nombre") or "").strip()
        correo = (datos.get("correo") or "").strip().lower()

        if not nombre or not correo:
            return jsonify({
                "error": "Nombre y correo son obligatorios"
            }), 400

        conexion = conectar_db()
        cursor = conexion.cursor(dictionary=True)

        # Verificar que el usuario exista
        cursor.execute("""
            SELECT id, rol
            FROM usuarios
            WHERE id = %s
        """, (id,))

        usuario = cursor.fetchone()

        if not usuario:
            return jsonify({
                "error": "Usuario no encontrado"
            }), 404

        # Evitar correos duplicados
        cursor.execute("""
            SELECT id
            FROM usuarios
            WHERE correo = %s
              AND id <> %s
        """, (correo, id))

        correo_existente = cursor.fetchone()

        if correo_existente:
            return jsonify({
                "error": "Ese correo ya está registrado"
            }), 409

        cursor.execute("""
            UPDATE usuarios
            SET nombre = %s,
                correo = %s
            WHERE id = %s
        """, (
            nombre,
            correo,
            id
        ))

        conexion.commit()

        return jsonify({
            "mensaje": "Datos actualizados correctamente",
            "usuario": {
                "id": id,
                "nombre": nombre,
                "correo": correo,
                "rol": usuario["rol"]
            }
        }), 200

    except Error as e:

        if conexion:
            conexion.rollback()

        return jsonify({
            "error": str(e)
        }), 500

    finally:

        if cursor:
            cursor.close()

        if conexion and conexion.is_connected():
            conexion.close()

# =========================================================
# USUARIO - ELIMINAR CUENTA
# =========================================================

@app.route("/usuarios/<int:id>", methods=["DELETE"])
def eliminar_usuario(id):

    conexion = None
    cursor = None

    try:

        conexion = conectar_db()
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                id,
                rol
            FROM usuarios
            WHERE id = %s
        """, (id,))

        usuario = cursor.fetchone()

        if not usuario:

            return jsonify({
                "error": "Usuario no encontrado"
            }), 404

        if usuario["rol"] != "cliente":

            return jsonify({
                "error": "No se puede eliminar una cuenta administrativa."
            }), 403

        # -------------------------------------------------
        # No permitimos eliminar la cuenta si tiene
        # pedidos que todavía están activos.
        # -------------------------------------------------

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM pedidos
            WHERE usuario_id = %s
              AND estado IN ('pendiente', 'procesando')
        """, (id,))

        activos = cursor.fetchone()["total"]

        if activos > 0:

            return jsonify({
                "error":
                "No puedes eliminar tu cuenta mientras tengas "
                "pedidos pendientes o en procesamiento."
            }), 409

        # -------------------------------------------------
        # Si no tiene pedidos, se puede eliminar físicamente.
        # Si tiene historial, se conserva para no destruir
        # registros de ventas.
        # -------------------------------------------------

        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM pedidos
            WHERE usuario_id = %s
        """, (id,))

        historial = cursor.fetchone()["total"]

        if historial > 0:

            return jsonify({
                "error":
                "Tu cuenta tiene historial de compras y no puede "
                "eliminarse físicamente sin borrar registros de ventas."
            }), 409

        cursor.execute("""
            DELETE FROM usuarios
            WHERE id = %s
              AND rol = 'cliente'
        """, (id,))

        conexion.commit()

        return jsonify({
            "mensaje": "Cuenta eliminada correctamente"
        }), 200

    except Error as e:

        if conexion:
            conexion.rollback()

        return jsonify({
            "error": str(e)
        }), 500

    finally:

        if cursor:
            cursor.close()

        if conexion and conexion.is_connected():
            conexion.close()


# =========================================================
# PEDIDO - CANCELAR POR EL CLIENTE
# =========================================================

@app.route("/pedidos/<int:id>/cancelar", methods=["PUT"])
def cancelar_pedido_cliente(id):

    conexion = None
    cursor = None

    try:

        datos = request.get_json() or {}

        usuario_id = datos.get("usuario_id")

        if not usuario_id:

            return jsonify({
                "error": "usuario_id es obligatorio"
            }), 400

        conexion = conectar_db()
        cursor = conexion.cursor(dictionary=True)

        # Bloqueamos el pedido mientras se cancela.
        cursor.execute("""
            SELECT
                id,
                usuario_id,
                estado
            FROM pedidos
            WHERE id = %s
            FOR UPDATE
        """, (id,))

        pedido = cursor.fetchone()

        if not pedido:

            conexion.rollback()

            return jsonify({
                "error": "Pedido no encontrado"
            }), 404

        # Seguridad: un cliente solamente puede cancelar
        # sus propios pedidos.
        if int(pedido["usuario_id"]) != int(usuario_id):

            conexion.rollback()

            return jsonify({
                "error": "No tienes permiso para cancelar este pedido."
            }), 403

        if pedido["estado"] == "cancelado":

            conexion.rollback()

            return jsonify({
                "error": "Este pedido ya está cancelado."
            }), 409

        if pedido["estado"] != "pendiente":

            conexion.rollback()

            return jsonify({
                "error":
                "Solo puedes cancelar pedidos que todavía "
                "estén pendientes."
            }), 409

        # Recuperamos las cantidades compradas.
        cursor.execute("""
            SELECT
                producto_id,
                cantidad
            FROM detalle_pedido
            WHERE pedido_id = %s
        """, (id,))

        productos = cursor.fetchall()

        # Devolvemos las unidades al inventario.
        for producto in productos:

            cursor.execute("""
                UPDATE productos
                SET stock = stock + %s
                WHERE id = %s
            """, (
                producto["cantidad"],
                producto["producto_id"]
            ))

        cursor.execute("""
            UPDATE pedidos
            SET estado = 'cancelado'
            WHERE id = %s
        """, (id,))

        conexion.commit()

        return jsonify({
            "mensaje": "Pedido cancelado correctamente",
            "estado": "cancelado"
        }), 200

    except Error as e:

        if conexion:
            conexion.rollback()

        return jsonify({
            "error": str(e)
        }), 500

    finally:

        if cursor:
            cursor.close()

        if conexion and conexion.is_connected():
            conexion.close()


# =========================================================
# PEDIDO - ACTUALIZAR ESTADO POR ADMINISTRADOR
# =========================================================

@app.route("/pedidos/<int:id>/estado", methods=["PUT"])
def actualizar_estado_pedido(id):

    conexion = None
    cursor = None

    try:

        datos = request.get_json() or {}

        estado = (
            datos.get("estado") or ""
        ).strip().lower()

        estados_validos = {
            "pendiente",
            "procesando",
            "completado",
            "cancelado"
        }

        if estado not in estados_validos:

            return jsonify({
                "error": "Estado no válido"
            }), 400

        conexion = conectar_db()
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                id,
                estado
            FROM pedidos
            WHERE id = %s
            FOR UPDATE
        """, (id,))

        pedido = cursor.fetchone()

        if not pedido:

            conexion.rollback()

            return jsonify({
                "error": "Pedido no encontrado"
            }), 404

        estado_anterior = pedido["estado"]

        if estado_anterior == estado:

            conexion.rollback()

            return jsonify({
                "mensaje": "El pedido ya tiene ese estado.",
                "estado": estado
            }), 200

        # Si se cancela por primera vez, devolvemos inventario.
        if estado == "cancelado" and estado_anterior != "cancelado":

            cursor.execute("""
                SELECT
                    producto_id,
                    cantidad
                FROM detalle_pedido
                WHERE pedido_id = %s
            """, (id,))

            productos = cursor.fetchall()

            for producto in productos:

                cursor.execute("""
                    UPDATE productos
                    SET stock = stock + %s
                    WHERE id = %s
                """, (
                    producto["cantidad"],
                    producto["producto_id"]
                ))

        # Evitamos reactivar un pedido cancelado porque
        # su inventario ya fue devuelto.
        if estado_anterior == "cancelado" and estado != "cancelado":

            conexion.rollback()

            return jsonify({
                "error":
                "Un pedido cancelado no puede reactivarse."
            }), 409

        cursor.execute("""
            UPDATE pedidos
            SET estado = %s
            WHERE id = %s
        """, (
            estado,
            id
        ))

        conexion.commit()

        return jsonify({
            "mensaje": "Estado actualizado correctamente",
            "estado": estado
        }), 200

    except Error as e:

        if conexion:
            conexion.rollback()

        return jsonify({
            "error": str(e)
        }), 500

    finally:

        if cursor:
            cursor.close()

        if conexion and conexion.is_connected():
            conexion.close()

# =========================================================
# EJECUTAR API
# =========================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5001,
        debug=True
    )
