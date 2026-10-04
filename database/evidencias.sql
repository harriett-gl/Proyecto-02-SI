-- EVIDENCIA 1 - TABLAS DE LA BASE DE DATOS

SHOW TABLES;


-- EVIDENCIA 2 - USUARIOS REGISTRADOS

SELECT
    id,
    nombre,
    correo,
    rol,
    fecha_creacion
FROM usuarios
ORDER BY id;

-- EVIDENCIA 3 - PRODUCTOS REGISTRADOS

SELECT
    id,
    nombre,
    precio,
    stock
FROM productos
ORDER BY id;


-- EVIDENCIA 4 - PEDIDOS REGISTRADOS

SELECT
    id,
    usuario_id,
    total,
    estado
FROM pedidos
ORDER BY id DESC;


-- EVIDENCIA 5 - DETALLE DE LOS PEDIDOS

SELECT
    pedido_id,
    producto_id,
    cantidad,
    precio_unitario
FROM detalle_pedido
ORDER BY pedido_id DESC;


-- EVIDENCIA 6 - PEDIDOS CON INFORMACIÓN DEL CLIENTE

SELECT
    p.id AS pedido,
    u.nombre AS cliente,
    u.correo,
    p.total,
    p.estado
FROM pedidos p
INNER JOIN usuarios u
    ON p.usuario_id = u.id
ORDER BY p.id DESC;


--   EVIDENCIA 7 - PRODUCTOS DE CADA PEDIDO

SELECT
    dp.pedido_id AS pedido,
    pr.nombre AS producto,
    dp.cantidad,
    dp.precio_unitario,
    (dp.cantidad * dp.precio_unitario) AS subtotal
FROM detalle_pedido dp
INNER JOIN productos pr
    ON dp.producto_id = pr.id
ORDER BY dp.pedido_id DESC;


-- EVIDENCIA 8 - RESUMEN DE PEDIDOS POR ESTADO

SELECT
    estado,
    COUNT(*) AS cantidad_pedidos
FROM pedidos
GROUP BY estado
ORDER BY cantidad_pedidos DESC;


-- EVIDENCIA 9 - TOTAL DE PEDIDOS POR CLIENTE

SELECT
    u.nombre AS cliente,
    u.correo,
    COUNT(p.id) AS total_pedidos,
    COALESCE(SUM(p.total), 0) AS total_compras
FROM usuarios u
LEFT JOIN pedidos p
    ON p.usuario_id = u.id
WHERE u.rol = 'cliente'
GROUP BY
    u.id,
    u.nombre,
    u.correo
ORDER BY total_pedidos DESC;

-- EVIDENCIA 10 - INVENTARIO ACTUAL

SELECT
    id,
    nombre,
    precio,
    stock
FROM productos
ORDER BY stock ASC;