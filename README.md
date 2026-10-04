# 🛒 TechMarket

Proyecto desarrollado para el curso de **Seguridad Informática**.

TechMarket simula una tienda de productos tecnológicos utilizando una arquitectura separada en tres servicios principales:

- 🌐 Aplicación WEB
- ⚙️ API REST
- 🗄️ Base de datos MySQL

La aplicación fue preparada con Docker para facilitar su despliegue e integración con la infraestructura de seguridad del proyecto.

> **Estado:** módulo de desarrollo finalizado y funcional. La aplicación WEB, la API REST y la base de datos se encuentran preparadas para su integración con el firewall perimetral, WAF, proxy y la segmentación de red del proyecto.

---

## 👩🏻‍💻 Desarrollo

**Desarrolladora:** Harriett Guzmán

Esta parte del proyecto incluye:

- Desarrollo del sitio WEB.
- Desarrollo de API REST.
- CRUD de productos.
- Registro de usuarios.
- Inicio y cierre de sesión.
- Roles de cliente y administrador.
- Carrito de compras.
- Creación de pedidos.
- Validación de stock.
- Actualización automática del inventario.
- Conexión WEB → API.
- Conexión API → MySQL.
- Contenedores Docker para WEB, API y DB.

---

# 📁 Estructura

```text
TechMarket/
│
├── web/
│   ├── app.py
│   ├── Dockerfile
│   ├── templates/
│   └── static/
│
├── api/
│   ├── app.py
│   └── Dockerfile
│
├── database/
│   └── init.sql
│
├── docker-compose.yml
├── .env
├── .env.example
├── .gitignore
└── README.md
```

---

# 🏗️ Arquitectura

El flujo de comunicación utilizado durante el desarrollo es:

```text
Usuario
   │
   ▼
WEB - Flask
   │
   │ HTTP / REST
   ▼
API - Flask
   │
   │ MySQL
   ▼
Base de Datos
```

La aplicación WEB no realiza consultas directamente a la base de datos.

Las consultas son realizadas mediante:

```text
WEB → API → DB
```

Esto permite separar las responsabilidades de cada servicio y facilita la integración posterior con los controles de seguridad del proyecto.

---

# 🐳 Docker

El proyecto utiliza Docker Compose para ejecutar:

```text
techmarket-web
techmarket-api
techmarket-db
```

Puertos utilizados durante el desarrollo:

| Servicio | Puerto |
|---|---:|
| WEB | 8000 |
| API | 5001 |
| MySQL | 3306 |

---

# ⚙️ Configuración

## 1. Clonar el repositorio

```bash
git clone URL_DEL_REPOSITORIO
```

Entrar a la carpeta:

```bash
cd TechMarket
```

---

## 2. Crear archivo `.env`

Copiar:

```text
.env.example
```

y crear:

```text
.env
```

Configurar las variables correspondientes.

Ejemplo:

```env
MYSQL_ROOT_PASSWORD=contraseña_segura
DB_HOST=db
DB_PORT=3306
DB_NAME=techmarket
DB_USER=techmarket_user
DB_PASSWORD=contraseña_segura
SECRET_KEY=clave_secreta
API_URL=http://api:5001
```

No se recomienda subir el archivo `.env` al repositorio.

---

# 🚀 Ejecutar TechMarket

Construir e iniciar todos los servicios:

```bash
docker compose up -d --build
```

Comprobar los contenedores:

```bash
docker compose ps
```

Los servicios deben aparecer activos.

---

# 🌐 Aplicación WEB

Abrir:

```text
http://localhost:8000
```

Desde la aplicación se puede:

- Consultar productos.
- Crear una cuenta.
- Iniciar sesión.
- Cerrar sesión.
- Consultar detalles de productos.
- Agregar productos al carrito.
- Modificar cantidades.
- Eliminar productos.
- Crear pedidos.
- Consultar el historial y seguimiento de pedidos.
- Cancelar pedidos pendientes.
- Consultar y editar la cuenta del cliente.

---

# ⚙️ API REST

Durante el entorno local de desarrollo la API está disponible en:

```text
http://localhost:5001
```

Ejemplo:

```bash
curl http://127.0.0.1:5001/productos
```

---

# 📦 Productos

La API implementa operaciones CRUD para productos.

## Obtener productos

```http
GET /productos
```

## Obtener producto

```http
GET /productos/{id}
```

## Crear producto

```http
POST /productos
```

## Actualizar producto

```http
PUT /productos/{id}
```

## Eliminar producto

```http
DELETE /productos/{id}
```

---

# 👤 Usuarios

La aplicación permite registrar usuarios e iniciar sesión.

```http
POST /registro
```

```http
POST /login
```

Los usuarios nuevos son registrados como clientes.

El acceso administrativo depende del rol almacenado para el usuario.

La aplicación diferencia dos perfiles principales:

- **Cliente:** consulta productos, administra su carrito, realiza pedidos, consulta su historial y gestiona su cuenta.
- **Administrador:** administra productos e inventario, consulta clientes y revisa y gestiona los pedidos registrados.

---

# 🛒 Pedidos

Los pedidos son creados mediante:

```http
POST /pedidos
```

El sistema:

1. Identifica al usuario.
2. Recibe los productos solicitados.
3. Verifica la existencia del producto.
4. Verifica el stock disponible.
5. Calcula el total.
6. Registra el pedido.
7. Registra el detalle del pedido.
8. Actualiza el inventario.

---

# 📉 Validación de stock

TechMarket evita que un usuario compre una cantidad superior al inventario disponible.

Por ejemplo, si existen:

```text
9 unidades
```

y se solicitan:

```text
20 unidades
```

la API rechaza la operación con un error de stock insuficiente.

El pedido inválido no debe registrarse ni reducir el inventario.

---

# 🗄️ Base de datos

La base de datos utiliza **MySQL 8.4**.

La inicialización se realiza mediante:

```text
database/init.sql
```

Las tablas utilizadas incluyen las necesarias para:

- Productos.
- Usuarios.
- Pedidos.
- Detalle de pedidos.

La API es responsable de comunicarse con MySQL.

---

# 🔐 Separación de servicios

La arquitectura está diseñada para integrarse posteriormente en la infraestructura de Seguridad Informática.

La arquitectura final del equipo contempla:

### Arquitectura principal

```text
                    ┌──────────────┐
                    │   Internet   │
                    └──────┬───────┘
                           │
                           ▼
                ┌─────────────────────┐
                │ Firewall Perimetral │
                └──────────┬──────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │     WEB     │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │     WAF     │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │     API     │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │     DB      │
                    └─────────────┘
```

### Red interna

Los equipos de los empleados se conectarán a la red interna y utilizarán **Proxy Squid** para aplicar políticas de navegación y restricciones de acceso.

```text
               ┌───────────────────┐
               │     Empleados     │
               └─────────┬─────────┘
                         │
                         ▼
               ┌───────────────────┐
               │    Proxy Squid    │
               └─────────┬─────────┘
                         │
                         ▼
               ┌───────────────────┐
               │ Internet / WEB    │
               └───────────────────┘
```

### Función de cada componente

| Componente | Función |
|---|---|
| **Firewall Perimetral** | Controla el tráfico entre Internet, DMZ y red interna. |
| **WEB** | Publica la aplicación web de TechMarket. |
| **WAF** | Protege la aplicación frente a solicitudes web maliciosas. |
| **API** | Gestiona productos, usuarios, autenticación y pedidos. |
| **DB** | Almacena la información del sistema TechMarket. |
| **Proxy Squid** | Aplica restricciones de navegación a los equipos de empleados. |

# 🧪 Pruebas realizadas

Durante el desarrollo se comprobaron:

- WEB → API.
- API → MySQL.
- Consulta de productos.
- CRUD de productos.
- Registro de usuarios.
- Inicio de sesión.
- Manejo de roles.
- Carrito de compras.
- Creación de pedidos.
- Registro de detalle de pedidos.
- Reducción automática del stock.
- Rechazo de pedidos con stock insuficiente.
- Ejecución de WEB, API y DB mediante Docker.
- Flujo completo de compra desde el cliente.
- Consulta del historial y seguimiento de pedidos.
- Acceso y funciones diferenciadas para cliente y administrador.
- Consulta administrativa de clientes, productos y pedidos.

---

# 🔗 Integración con la infraestructura de seguridad

El módulo desarrollado está preparado para integrarse con:

- Firewall perimetral.
- WAF.
- Proxy Squid.
- Máquinas virtuales de empleados.
- Segmentación WAN / DMZ / LAN.

La integración final se realizará en el entorno preparado por el equipo para la demostración del proyecto, manteniendo separados los servicios WEB, API y base de datos para aplicar los controles de seguridad correspondientes.

---

# 👥 Equipo y responsabilidades

| Integrante | Responsabilidad |
|---|---|
| **Harriett Guzmán** | Desarrollo de la aplicación WEB, API REST, base de datos, lógica de clientes y administradores, carrito, pedidos e integración mediante Docker. |
| **Esly** | Infraestructura virtual, segmentación de red y firewall perimetral. |
| **José** | WAF, Proxy Squid y controles de seguridad internos. |

---

# ✅ Estado actual

El módulo desarrollado por Harriett cumple el flujo principal:

```text
Cliente / Administrador
        │
        ▼
       WEB
        │
        ▼
    API REST
        │
        ▼
      MySQL
```

Se verificó el funcionamiento de la interfaz para clientes y administradores, las operaciones CRUD, autenticación, carrito, pedidos, actualización de inventario y comunicación entre los tres servicios.

**Estado actual: desarrollo finalizado, funcional y preparado para la integración con la infraestructura de seguridad del Proyecto 02.**

---

## 📌 Evidencia de desarrollo

El historial del repositorio conserva los commits realizados en la rama de desarrollo, permitiendo identificar los cambios implementados y la documentación final del módulo.