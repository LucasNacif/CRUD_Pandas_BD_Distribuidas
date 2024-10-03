from App.crud import (
    crear_producto_MySql,
    obtener_productos_MySql,
    eliminar_productos_MySql,
    obtener_producto_PorID_MySql,
    actualizar_producto_MySql
)

print("Menu de opciones:")
print("1 - Listar todos los productos")
print("2 - Modificar un producto")
print("3 - Eliminar un producto")
print("4 - Crear un producto")
print("5 - Listar un producto en especial")

valor = input("Ingrese el numero de lo que desea hacer: ")

if valor == "1":
    # Obtener y mostrar todos los productos
    productos = obtener_productos_MySql()
    for producto in productos:
        print(producto)

elif valor == "2":
    # Modificar un producto
    id_producto = input("Ingrese el ID del producto que quiere modificar: ")
    nombre = input("Ingrese el nuevo nombre: ")
    precio = float(input("Ingrese el nuevo precio: "))
    cantidad_stock = int(input("Ingrese la nueva cantidad de stock: "))
    exito = actualizar_producto_MySql(id_producto, nombre, precio, cantidad_stock)
    if exito:
        print("Producto modificado con éxito")
    else:
        print("Error al modificar el producto")

elif valor == "3":
    # Eliminar un producto
    id_producto = input("Ingrese el ID del producto que quiere eliminar: ")
    exito = eliminar_productos_MySql(id_producto)
    if exito:
        print("Producto eliminado con éxito")
    else:
        print("Error al eliminar el producto")

elif valor == "4":
    # Crear un nuevo producto
    nombre_producto = input("Ingrese el nombre del nuevo producto: ")
    precio_producto = float(input("Ingrese el precio del nuevo producto: "))
    cantidad_producto = int(input("Ingrese la cantidad del nuevo producto: "))
    
    crear_producto_MySql(nombre_producto, precio_producto, cantidad_producto)
    print("Producto creado correctamente")

elif valor == "5":
    # Listar un solo producto
    id_producto = input("Ingrese el ID del producto que quiere listar: ")
    producto = obtener_producto_PorID_MySql(id_producto)
    
    if producto:
        print(f"Producto encontrado:\nID: {producto[0]}\nNombre: {producto[1]}\nPrecio: {producto[2]}\nCantidad en stock: {producto[3]}")
    else:
        print("No se encontró el producto.")


else:
    print("Opción no válida. Por favor, elija una opción del menú.")
