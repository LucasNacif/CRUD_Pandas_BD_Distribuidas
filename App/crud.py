from App.database import connect_mysql

# Crear un producto en MySQL
def crear_producto_MySql(nombre, precio, cantidad_stock):
    connection = connect_mysql()
    with connection.cursor() as cursor:
        sql = "INSERT INTO Producto (nombre, precio, cantidad_stock) VALUES (%s, %s, %s)"
        cursor.execute(sql, (nombre, precio, cantidad_stock))
    connection.commit()
    connection.close()

def obtener_productos_MySql():
    connection = connect_mysql()
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Producto")
        productos = cursor.fetchall()
    connection.close()
    return productos

def eliminar_productos_MySql(id):
    connection = connect_mysql()
    with connection.cursor() as cursor:
        sql = "DELETE FROM Producto WHERE id_producto = %s"
        cursor.execute(sql, (id,))
        connection.commit()
    connection.close()
    return True

def actualizar_producto_MySql(id, nombre, precio, cantidad_stock):
    connection = connect_mysql()
    with connection.cursor() as cursor:
        sql = "UPDATE Producto SET nombre = %s, precio = %s, cantidad_stock = %s WHERE id_producto = %s"
        cursor.execute(sql, (nombre, precio, cantidad_stock, id))
        connection.commit()
    connection.close()
    return True

def obtener_producto_PorID_MySql(id):
    connection = connect_mysql()
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Producto WHERE id_producto = %s", (id,))  
        producto = cursor.fetchone()
    connection.close()
    return producto
