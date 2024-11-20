from App.database import connect_mysql

def crear_venta_MySql(id_producto, cantidad, nombre_cliente):
    connection = connect_mysql()
    with connection.cursor() as cursor:
        sql = "INSERT INTO Ventas (id_producto, cantidad, nombreCliente) VALUES (%s, %s, %s)"
        cursor.execute(sql, (id_producto, cantidad, nombre_cliente))
    connection.commit()
    connection.close()

def obtener_ventas_MySql():
    connection = connect_mysql()
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Ventas")
        ventas = cursor.fetchall()
    connection.close()
    return ventas

def eliminar_venta_MySql(id_venta):
    venta = obtener_venta_por_id_MySql(id_venta)
    if venta:
        connection = connect_mysql()
        with connection.cursor() as cursor:
            sql = "DELETE FROM Ventas WHERE id_venta = %s"
            cursor.execute(sql, (id_venta,))
            connection.commit()
        connection.close()
        return True
    else:
        return False

def actualizar_venta_MySql(id_venta, nombre_cliente):
    venta = obtener_venta_por_id_MySql(id_venta)
    if venta:
        connection = connect_mysql()
        with connection.cursor() as cursor:
            sql = "UPDATE Ventas SET nombreCliente = %s WHERE id_venta = %s"
            cursor.execute(sql, (nombre_cliente, id_venta))
            connection.commit()
        connection.close()
        return True
    else:
        return False

def obtener_venta_por_id_MySql(id_venta):
    connection = connect_mysql()
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Ventas WHERE id_venta = %s", (id_venta,))
        venta = cursor.fetchone()
    connection.close()
    return venta
