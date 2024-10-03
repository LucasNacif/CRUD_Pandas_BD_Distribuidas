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
    productos = {producto['_id']: producto for producto in obtener_productos_Mongo()}  
    return render_template('listar_ventas.html', ventas=ventas, productos=productos)


@app.route('/ventas/crear', methods=['GET', 'POST'])
def crear_venta():
    if request.method == 'POST':
        id_producto = request.form['id_producto']
        cantidad = request.form['cantidad']
        nombre_cliente = request.form['nombre_cliente']
        crear_venta_MySql(id_producto, cantidad, nombre_cliente)
        return redirect(url_for('listar_ventas'))
    return render_template('crear_venta.html')

@app.route('/ventas/modificar/<int:id_venta>', methods=['GET', 'POST'])
def modificar_venta(id_venta):
    venta = obtener_venta_por_id_MySql(id_venta)
    if request.method == 'POST':
        id_producto = request.form['id_producto']
        cantidad = request.form['cantidad']
        nombre_cliente = request.form['nombre_cliente']
        actualizar_venta_MySql(id_venta, id_producto, cantidad, nombre_cliente)
        return redirect(url_for('listar_ventas'))
    return render_template('modificar_venta.html', venta=venta)

@app.route('/ventas/eliminar/<int:id_venta>', methods=['POST'])
def eliminar_venta(id_venta):
    eliminar_venta_MySql(id_venta)
    return redirect(url_for('listar_ventas'))

@app.template_global()
def get_producto(id_producto):
    producto = obtener_producto_por_id_Mongo(id_producto)
    return producto  

if __name__ == '__main__':
    app.run(debug=True)
