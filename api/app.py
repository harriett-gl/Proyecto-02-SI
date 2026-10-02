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
# CONEXIÓN A MYSQL
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


# =========================================================
# PRODUCTOS - OBTENER TODOS
# =========================================================

@app.route("/productos", methods=["GET"])
def obtener_productos():
    conexion = None
    cursor = None

    try:
        conexion = conectar_db()
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("""
            SELECT id, nombre, descripcion, precio, stock
            FROM productos
            ORDER BY id
        """)

        productos = cursor.fetchall()

        return jsonify(productos), 200

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
# PRODUCTOS - OBTENER UNO
# =========================================================

@app.route("/productos/<int:id>", methods=["GET"])
def obtener_producto(id):
    conexion = None
    cursor = None

    try:
        conexion = conectar_db()
        cursor = conexion.cursor(dictionary=True)

        sql = """
        SELECT id, nombre, descripcion, precio, stock
        FROM productos
        WHERE id = %s
        """

        cursor.execute(sql, (id,))
        producto = cursor.fetchone()

        return producto

    except Exception as error:
        print(f"Error al obtener producto: {error}")
        return None

    finally:
        if cursor is not None:
            cursor.close()

        if conexion is not None and conexion.is_connected():
            conexion.close()

# =========================================================
# PRODUCTOS - CREAR
# =========================================================

@app.route("/productos", methods=["POST"])
def crear_producto():
    conexion = None
    cursor = None

    try:
        datos = request.get_json()

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

        sql = """
        INSERT INTO productos (nombre, descripcion, precio, stock)
        VALUES (%s, %s, %s, %s)
        """

        cursor.execute(
            sql,
            (nombre, descripcion, precio, stock)
        )

        conexion.commit()

        return jsonify({
            "mensaje": "Producto creado correctamente",
            "id": cursor.lastrowid
        }), 201

    except Error as e:
        return jsonify({
            "error": str(e)
        }), 500

    finally:
        if cursor is not None:
            cursor.close()

        if conexion is not None and conexion.is_connected():
            conexion.close()

# =========================================================
# PRODUCTOS - ACTUALIZAR
# =========================================================

@app.route("/productos/<int:id>", methods=["PUT"])
def actualizar_producto(id):
    conexion = None
    cursor = None

    try:
        datos = request.get_json()

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

        sql = """
        UPDATE productos
        SET nombre = %s,
            descripcion = %s,
            precio = %s,
            stock = %s
        WHERE id = %s
        """

        cursor.execute(
            sql,
            (nombre, descripcion, precio, stock, id)
        )

        conexion.commit()

        if cursor.rowcount == 0:
            return jsonify({
                "error": "Producto no encontrado"
            }), 404

        return jsonify({
            "mensaje": "Producto actualizado correctamente"
        }), 200

    except Error as e:
        return jsonify({
            "error": str(e)
        }), 500

    finally:
        if cursor is not None:
            cursor.close()

        if conexion is not None and conexion.is_connected():
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
                    return jsonify({
                        "error": str(e)
                    }), 500

                finally:
                    if cursor is not None:
                        cursor.close()

                    if conexion is not None and conexion.is_connected():
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
        return jsonify({
            "error": str(e)
        }), 500

    finally:
        if cursor is not None:
            cursor.close()

        if conexion is not None and conexion.is_connected():
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
            SELECT id, usuario_id, total, estado
            FROM pedidos
            ORDER BY id
        """)

        pedidos = cursor.fetchall()

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
# PEDIDOS - CREAR PEDIDO
# =========================================================

@app.route("/pedidos", methods=["POST"])
def crear_pedido():
    conexion = None
    cursor = None

    try:
        datos = request.get_json()

        if not datos:
            return jsonify({"error": "No se enviaron datos"}), 400

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

        # Validar productos y calcular total
        for item in productos:
            producto_id = item.get("producto_id")
            cantidad = item.get("cantidad")

            if not producto_id or not cantidad or cantidad <= 0:
                conexion.rollback()
                return jsonify({
                    "error": "Producto o cantidad inválida"
                }), 400

            cursor.execute(
                """
                SELECT id, nombre, precio, stock
                FROM productos
                WHERE id = %s
                """,
                (producto_id,)
            )

            producto = cursor.fetchone()

            if not producto:
                conexion.rollback()
                return jsonify({
                    "error": f"Producto {producto_id} no encontrado"
                }), 404

            if producto["stock"] < cantidad:
                conexion.rollback()
                return jsonify({
                    "error": f"Stock insuficiente para {producto['nombre']}"
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

        # Crear pedido
        cursor.execute(
            """
            INSERT INTO pedidos (usuario_id, total, estado)
            VALUES (%s, %s, %s)
            """,
            (usuario_id, total, "pendiente")
        )

        pedido_id = cursor.lastrowid

        # Crear detalle y descontar stock
        for detalle in detalles:

            cursor.execute(
                """
                INSERT INTO detalle_pedido
                (pedido_id, producto_id, cantidad, precio_unitario, subtotal)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    pedido_id,
                    detalle["producto_id"],
                    detalle["cantidad"],
                    detalle["precio"],
                    detalle["subtotal"]
                )
            )

            cursor.execute(
                """
                UPDATE productos
                SET stock = stock - %s
                WHERE id = %s
                """,
                (
                    detalle["cantidad"],
                    detalle["producto_id"]
                )
            )

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
                "error": "Nombre, correo y password son obligatorios"
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
            INSERT INTO usuarios (nombre, correo, password, rol)
            VALUES (%s, %s, %s, %s)
        """, (nombre, correo, password_hash, "cliente"))

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
                "error": "Correo y password son obligatorios"
            }), 400

        conexion = conectar_db()
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("""
            SELECT id, nombre, correo, password, rol
            FROM usuarios
            WHERE correo = %s
        """, (correo,))

        usuario = cursor.fetchone()

        if usuario is None:
            return jsonify({
                "error": "Correo o contraseña incorrectos"
            }), 401

        if not check_password_hash(usuario["password"], password):
            return jsonify({
                "error": "Correo o contraseña incorrectos"
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


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5001,
        debug=True
    )