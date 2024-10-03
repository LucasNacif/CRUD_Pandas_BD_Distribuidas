from App.database import connect_mysql

# Crear un producto en MySQL
def crear_producto_MySql(nombre, precio, cantidad_stock):
    connection = connect_mysql()
    with connection.cursor() as cursor:
        sql = "INSERT INTO Producto (nombre, precio, cantidad_stock) VALUES (%s, %s, %s)"
        cursor.execute(sql, (nombre, precio, cantidad_stock))
    connection.commit()
    connection.close()

# Leer todos los productos
def obtener_productos_MySql():
    connection = connect_mysql()
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Producto")
        productos = cursor.fetchall()
    connection.close()
    return productos