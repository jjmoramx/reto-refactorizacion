"""Punto de entrada del gestor de tienda (menu interactivo en consola)."""

import almacen
import gestor
import reportes

ARCHIVO = "datos_ejemplo.json"
OPCION_SALIR = "8"


def pedir_numero(mensaje):
    # pide un numero al usuario hasta que escriba algo valido
    while True:
        texto = input(mensaje)
        try:
            return float(texto)
        except ValueError:
            print("Eso no es un numero, intenta de nuevo.")


def _cargar_datos_iniciales():
    if almacen.hay_archivo(ARCHIVO):
        almacen.cargar_datos(ARCHIVO)
        print("Datos cargados de", ARCHIVO)


def _mostrar_opciones():
    print("")
    print("1) Agregar producto")
    print("2) Registrar venta")
    print("3) Cotizar")
    print("4) Reporte de inventario")
    print("5) Resumen de ventas")
    print("6) Mas vendidos")
    print("7) Alertas de stock bajo")
    print("8) Guardar y salir")


def _agregar_producto():
    codigo = input("Codigo: ")
    nombre = input("Nombre: ")
    precio = pedir_numero("Precio: ")
    stock = int(pedir_numero("Stock inicial: "))
    if gestor.agregarProducto(codigo, nombre, precio, stock):
        print("Producto agregado.")
    else:
        print("Error:", gestor.ultimo_error)


def _registrar_venta():
    codigo = input("Codigo del producto: ")
    cantidad = int(pedir_numero("Cantidad: "))
    cliente = input("Codigo de cliente (enter si no tiene): ")
    venta = gestor.registrar_venta(codigo, cantidad, cliente)
    if venta is not None:
        print(venta["ticket"])
    else:
        print("Error:", gestor.ultimo_error)


def _cotizar():
    codigo = input("Codigo del producto: ")
    cantidad = int(pedir_numero("Cantidad: "))
    total = gestor.cotizar(codigo, cantidad)
    if total is not None:
        print("Total estimado (con IVA): $" + str(total))
    else:
        print("Error:", gestor.ultimo_error)


def _reporte_inventario():
    reportes.reporte_inventario()


def _resumen_ventas():
    reportes.resumen_ventas()


def _mas_vendidos():
    for codigo, unidades in reportes.mas_vendidos():
        print(codigo, "->", unidades, "unidades")


def _alertas_stock_bajo():
    bajos = reportes.productos_stock_bajo()
    if len(bajos) == 0:
        print("No hay productos con stock bajo.")
        return
    for producto in bajos:
        print("OJO:", producto["nombre"], "solo tiene", producto["stock"], "unidades")


def _guardar_y_salir():
    almacen.guardar_datos(ARCHIVO)
    print("Datos guardados. Hasta luego.")


ACCIONES_MENU = {
    "1": _agregar_producto,
    "2": _registrar_venta,
    "3": _cotizar,
    "4": _reporte_inventario,
    "5": _resumen_ventas,
    "6": _mas_vendidos,
    "7": _alertas_stock_bajo,
}


def menu():
    print("Bienvenido al gestor de la tienda La Esquina")
    _cargar_datos_iniciales()
    while True:
        _mostrar_opciones()
        opcion = input("Opcion: ")
        if opcion == OPCION_SALIR:
            _guardar_y_salir()
            break
        accion = ACCIONES_MENU.get(opcion)
        if accion is None:
            print("Opcion no valida.")
        else:
            accion()


if __name__ == "__main__":
    menu()
