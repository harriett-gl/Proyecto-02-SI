USE techmarket;

CREATE TABLE IF NOT EXISTS productos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion VARCHAR(255),
    precio DECIMAL(10,2) NOT NULL,
    stock INT NOT NULL DEFAULT 0
);

INSERT INTO productos (nombre, descripcion, precio, stock)
SELECT 'Monitor Gamer', 'Monitor 24 pulgadas 144Hz', 1850.00, 10
WHERE NOT EXISTS (
    SELECT 1 FROM productos WHERE nombre = 'Monitor Gamer'
);

INSERT INTO productos (nombre, descripcion, precio, stock)
SELECT 'Teclado Mecanico', 'Teclado RGB con switches red', 650.00, 15
WHERE NOT EXISTS (
    SELECT 1 FROM productos WHERE nombre = 'Teclado Mecanico'
);

INSERT INTO productos (nombre, descripcion, precio, stock)
SELECT 'Audifonos Gamer', 'Audifonos con microfono', 475.00, 20
WHERE NOT EXISTS (
    SELECT 1 FROM productos WHERE nombre = 'Audifonos Gamer'
);

INSERT INTO productos (nombre, descripcion, precio, stock)
SELECT 'Fuente 750W', 'Fuente certificada 80 Plus Gold', 950.00, 8
WHERE NOT EXISTS (
    SELECT 1 FROM productos WHERE nombre = 'Fuente 750W'
);

# TABLA DE USUARIOS

CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(150) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    rol VARCHAR(20) NOT NULL DEFAULT 'cliente',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

/* =========================================================
   TABLA DE PEDIDOS
   ========================================================= */

CREATE TABLE IF NOT EXISTS pedidos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    total DECIMAL(10,2) NOT NULL,
    estado VARCHAR(30) NOT NULL DEFAULT 'pendiente',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (usuario_id)
        REFERENCES usuarios(id)
);


/* =========================================================
   DETALLE DE CADA PEDIDO
   ========================================================= */

CREATE TABLE IF NOT EXISTS detalle_pedido (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pedido_id INT NOT NULL,
    producto_id INT NOT NULL,
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,

    FOREIGN KEY (pedido_id)
        REFERENCES pedidos(id),

    FOREIGN KEY (producto_id)
        REFERENCES productos(id)
);

SHOW TABLES;

DESCRIBE pedidos;
DESCRIBE detalle_pedido;