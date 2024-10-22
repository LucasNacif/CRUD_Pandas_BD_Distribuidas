from flask import Flask, render_template, request, redirect, url_for
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

app = Flask(__name__, template_folder='App/templates')

@app.route('/')
def index():
    return redirect(url_for('listar_ventas'))

@app.route('/ventas', methods=['GET'])
def listar_ventas():
    ventas = obtener_ventas_MySql()
    productos = obtener_productos_Mongo() 
    return render_template('listar_ventas.html', ventas=ventas, productos=productos)

@app.route('/ventas/crear', methods=['GET', 'POST'])
def crear_venta():
    if request.method == 'POST':
        id_producto = request.form['id_producto']
        cantidad = request.form['cantidad']
        nombre_cliente = request.form['nombre_cliente']
        crear_venta_MySql(id_producto, cantidad, nombre_cliente)
        return redirect(url_for('listar_ventas'))
    productos = obtener_productos_Mongo()
    return render_template('crear_venta.html', productos=productos)

@app.route('/ventas/modificar/<int:id_venta>', methods=['GET', 'POST'])
def modificar_venta(id_venta):
    venta = obtener_venta_por_id_MySql(id_venta)
    if request.method == 'POST':
        id_producto = request.form['id_producto']
        cantidad = request.form['cantidad']
        nombre_cliente = request.form['nombre_cliente']
        actualizar_venta_MySql(id_venta, id_producto, cantidad, nombre_cliente)
        return redirect(url_for('listar_ventas'))
    productos = obtener_productos_Mongo()
    return render_template('modificar_venta.html', venta=venta, productos=productos)

@app.route('/ventas/eliminar/<int:id_venta>', methods=['POST'])
def eliminar_venta(id_venta):
    eliminar_venta_MySql(id_venta)
    return redirect(url_for('listar_ventas'))

@app.template_global()
def get_producto(id_producto):
    try:
        id_producto_str = str(id_producto)
        productos = obtener_productos_Mongo()
        
        for producto in productos:
            if str(producto.get('id', '')) == id_producto_str:
                return producto
                
        return {"nombre": "Producto no encontrado"}
        
    except Exception as e:
        print(f"Error al obtener producto: {e}")
        return {"nombre": "Error al obtener producto"}

if __name__ == '__main__':
    app.run(debug=True)