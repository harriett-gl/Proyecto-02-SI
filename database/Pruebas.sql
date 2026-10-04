/* =========================================================
   1. TABLA USUARIOS
   ========================================================= */

CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    rol ENUM('cliente', 'admin') NOT NULL DEFAULT 'cliente',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


/* Ver estructura de la tabla */

DESCRIBE usuarios;


/* Consultar usuarios registrados */

SELECT
    id,
    nombre,
    correo,
    rol,
    fecha_creacion
FROM usuarios;


/* =========================================================
   2. ASIGNAR ROL DE ADMINISTRADOR
   ========================================================= */

UPDATE usuarios
SET rol = 'admin'
WHERE correo = 'harriett@techmarket.com';

COMMIT;


/* Verificar cambio de rol */

SELECT
    id,
    nombre,
    correo,
    rol
FROM usuarios
WHERE correo = 'harriett@techmarket.com';


/* =========================================================
   3. CONSULTAR PRODUCTOS
   ========================================================= */

SELECT
    id,
    nombre,
    precio,
    stock
FROM productos;


/* =========================================================
   4. CONSULTAR PEDIDOS
   ========================================================= */

SELECT *
FROM pedidos;


/* =========================================================
   5. CONSULTAR DETALLE DE PEDIDOS
   ========================================================= */

SELECT *
FROM detalle_pedido;