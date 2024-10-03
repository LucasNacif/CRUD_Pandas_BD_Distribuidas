from App.crud import crear_producto_MySql, obtener_productos_MySql

# Crear un nuevo producto
producto_id = crear_producto_MySql("Laptop", 1200.00, 10)
print(f"Producto creado correctamente")

# Obtener y mostrar todos los productos
productos = obtener_productos_MySql()
for producto in productos:
    print(producto)
