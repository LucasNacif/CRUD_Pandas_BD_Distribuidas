from flask import Flask, render_template, request, redirect, url_for, flash
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
app.secret_key = 'tu_clave_secreta'  # Necesario para flash messages

@app.route('/')
def index():
    return redirect(url_for('listar_productos'))

@app.route('/productos', methods=['GET'])
def listar_productos():
    productos = obtener_productos_Mongo()
    return render_template('listar_productos.html', productos=productos)

@app.route('/productos/crear', methods=['GET', 'POST'])
def crear_producto():
    if request.method == 'POST':
        nombre_producto = request.form['nombre_producto']
        precio_producto = float(request.form['precio_producto'])
        cantidad_producto = int(request.form['cantidad_producto'])
        
        id_nuevo_producto = crear_producto_Mongo(nombre_producto, precio_producto, cantidad_producto)
        if id_nuevo_producto:
            flash('Producto creado exitosamente', 'success')
        else:
            flash('Error al crear el producto', 'error')
        return redirect(url_for('listar_productos'))
    return render_template('crear_producto.html')

@app.route('/productos/editar/<id_producto>', methods=['GET', 'POST'])
def editar_producto(id_producto):
    if request.method == 'POST':
        nombre = request.form['nombre_producto']
        precio = float(request.form['precio_producto'])
        cantidad_stock = int(request.form['cantidad_producto'])
        
        exito = actualizar_producto_Mongo(id_producto, nombre, precio, cantidad_stock)
        if exito:
            flash('Producto actualizado exitosamente', 'success')
        else:
            flash('Error al actualizar el producto', 'error')
        return redirect(url_for('listar_productos'))
    
    producto = obtener_producto_por_id_Mongo(id_producto)
    if producto:
        return render_template('editar_producto.html', producto=producto)
    flash('Producto no encontrado', 'error')
    return redirect(url_for('listar_productos'))

@app.route('/productos/eliminar/<id_producto>')
def eliminar_producto(id_producto):
    exito = eliminar_producto_Mongo(id_producto)
    if exito:
        flash('Producto eliminado exitosamente', 'success')
    else:
        flash('Error al eliminar el producto', 'error')
    return redirect(url_for('listar_productos'))

@app.route('/productos/<id_producto>')
def ver_producto(id_producto):
    producto = obtener_producto_por_id_Mongo(id_producto)
    if producto:
        return render_template('ver_producto.html', producto=producto)
    flash('Producto no encontrado', 'error')
    return redirect(url_for('listar_productos'))

if __name__ == '__main__':
    app.run(debug=True)