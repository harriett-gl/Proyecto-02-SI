from pathlib import Path
import re


ARCHIVOS = [
    "web/templates/index.html",
    "web/templates/carrito.html",
    "web/templates/producto.html",
    "web/templates/mis_pedidos.html",
    "web/templates/mi_pedido.html",
    "web/templates/mi_cuenta.html",
    "web/templates/editar_cuenta.html",
    "web/templates/pedido_exitoso.html",
]


NUEVO_HEADER = """{% include 'navbar_cliente.html' %}"""


for ruta in ARCHIVOS:

    archivo = Path(ruta)

    if not archivo.exists():

        print(
            f"⚠ No existe: {ruta}"
        )

        continue

    contenido = archivo.read_text(
        encoding="utf-8"
    )

    nuevo_contenido, cambios = re.subn(
        r"<header\\b[^>]*>.*?</header>",
        NUEVO_HEADER,
        contenido,
        count=1,
        flags=re.DOTALL | re.IGNORECASE
    )

    if cambios == 0:

        print(
            f"⚠ No encontré header en: {ruta}"
        )

        continue

    archivo.write_text(
        nuevo_contenido,
        encoding="utf-8"
    )

    print(
        f"✓ Navbar actualizado: {ruta}"
    )


print()
print("Proceso terminado.")