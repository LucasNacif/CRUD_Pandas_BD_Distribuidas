from App.crud_mysql import (
    crear_venta_MySql,
    obtener_ventas_MySql,
    eliminar_venta_MySql,
    actualizar_venta_MySql,
    obtener_venta_por_id_MySql
)
from App.crud_mongo import (
    crear_producto_Mongo,
    obtener_productos_Mongo,
    eliminar_producto_Mongo,
    obtener_producto_por_id_Mongo,
    actualizar_producto_Mongo
)

salir = "1"

while salir == "1":
    print("Menu de opciones en MongoDB:")
    print("1 - Listar todos los productos")
    print("2 - Modificar un producto")
    print("3 - Eliminar un producto")
    print("4 - Crear un producto")
    print("5 - Listar un producto en especial")

    valor = input("Ingrese el numero de lo que desea hacer: ")

    if valor == "1":
        # Obtener y mostrar todos los productos
        productos = obtener_productos_Mongo()
        if productos:
            for producto in productos:
                print(producto)
        else:
            print("No hay productos disponibles")

    elif valor == "2":
        # Modificar un producto
        id_producto = input("Ingrese el ID del producto que quiere modificar: ")
        producto = obtener_producto_por_id_Mongo(id_producto)
        if producto:
            nombre = input("Ingrese el nuevo nombre: ")
            precio = float(input("Ingrese el nuevo precio: "))
            cantidad_stock = int(input("Ingrese la nueva cantidad de stock: "))
            exito = actualizar_producto_Mongo(id_producto, nombre, precio, cantidad_stock)
            if exito:
                print("Producto modificado con éxito")
            else:
                print("Error al modificar el producto")
        else:
            print("Producto inexistente")

    elif valor == "3":
        # Eliminar un producto
        id_producto = input("Ingrese el ID del producto que quiere eliminar: ")
        exito = eliminar_producto_Mongo(id_producto)
        if exito:
            print("Producto eliminado con éxito")
        else:
            print("Error al eliminar el producto")

    elif valor == "4":
        # Crear un nuevo producto
        nombre_producto = input("Ingrese el nombre del nuevo producto: ")
        precio_producto = float(input("Ingrese el precio del nuevo producto: "))
        cantidad_producto = int(input("Ingrese la cantidad del nuevo producto: "))
        
        id_nuevo_producto = crear_producto_Mongo(nombre_producto, precio_producto, cantidad_producto)
        print(f"Producto creado correctamente con ID: {id_nuevo_producto}")

    elif valor == "5":
        # Listar un solo producto
        id_producto = input("Ingrese el ID del producto que quiere listar: ")
        producto = obtener_producto_por_id_Mongo(id_producto)
        
        if producto:
            print(f"Producto encontrado:\nID: {producto['_id']}\nNombre: {producto['nombre']}\nPrecio: {producto['precio']}\nCantidad en stock: {producto['cantidad_stock']}")
        else:
            print("No se encontró el producto.")

    else:
        print("Opción no válida. Por favor, elija una opción del menú.")
    
    print("¿Desea continuar?")
    print("1 - Continuar")
    print("2 - Salir")
    salir = input() 
