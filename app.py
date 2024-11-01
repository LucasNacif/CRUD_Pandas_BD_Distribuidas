from flask import Flask, render_template, request, redirect, send_file, url_for, flash, jsonify
import pandas as pd 
from io import BytesIO
from bson import ObjectId, errors as bson_errors
from datetime import datetime

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
app.secret_key = 'tu_clave_secreta_aqui'

@app.route('/')
def index():
    return redirect(url_for('listar_ventas'))

@app.route('/ventas')
def listar_ventas():
    ventas = obtener_ventas_MySql()
    productos = {str(p['_id']): p for p in obtener_productos_Mongo()}
    return render_template('listar_ventas.html', ventas=ventas, productos=productos)

@app.route('/crear_venta', methods=['GET', 'POST'])
def crear_venta():
    productos = obtener_productos_Mongo()
    
    if not productos:
        flash('No hay productos disponibles para vender. Por favor, agregue productos primero.', 'error')
        return redirect(url_for('listar_productos'))

    if request.method == 'POST':
        try:
            id_producto = request.form['id_producto']
            cantidad = int(request.form['cantidad'])
            nombre_cliente = request.form['nombre_cliente']
            
            producto = obtener_producto_por_id_Mongo(id_producto)
            
            if not producto:
                flash('Producto no encontrado', 'error')
                return redirect(url_for('crear_venta'))
            
            if producto['cantidad_stock'] < cantidad:
                flash(f'No hay suficiente stock disponible. Stock actual: {producto["cantidad_stock"]}', 'error')
                return redirect(url_for('crear_venta'))
            
            crear_venta_MySql(id_producto, cantidad, nombre_cliente)
            
            nuevo_stock = producto['cantidad_stock'] - cantidad
            actualizar_producto_Mongo(
                id_producto,
                producto['nombre'],
                producto['precio'],
                nuevo_stock
            )
            
            flash('Venta creada exitosamente', 'success')
            return redirect(url_for('listar_ventas'))
            
        except ValueError:
            flash('Cantidad inválida', 'error')
        except Exception as e:
            flash(f'Error al crear la venta: {str(e)}', 'error')

    return render_template('crear_venta.html', productos=productos)

@app.route('/ventas/modificar/<int:id_venta>', methods=['GET', 'POST'])
def modificar_venta(id_venta):
    venta = obtener_venta_por_id_MySql(id_venta)
    if request.method == 'POST':
        id_producto = request.form['id_producto']
        cantidad = request.form['cantidad']
        nombre_cliente = request.form['nombre_cliente']
        actualizar_venta_MySql(id_venta, id_producto, cantidad, nombre_cliente)
        flash('Venta modificada exitosamente', 'success')
        return redirect(url_for('listar_ventas'))
    productos = obtener_productos_Mongo()
    return render_template('modificar_venta.html', venta=venta, productos=productos)

@app.route('/ventas/eliminar/<int:id_venta>', methods=['POST'])
def eliminar_venta(id_venta):
    eliminar_venta_MySql(id_venta)
    flash('Venta eliminada exitosamente', 'success')
    return redirect(url_for('listar_ventas'))

# Rutas para Productos
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

# Rutas para Dashboard
@app.route('/dashboard')
def dashboard():
    ventas = obtener_ventas_MySql()
    
    df = pd.DataFrame(ventas, columns=['id_venta', 'id_producto', 'cantidad', 'nombreCliente', 'fecha'])
    
    df['fecha'] = pd.to_datetime(df['fecha'])
    
    def get_producto_nombre(id_producto):
        producto = get_producto(id_producto)
        return producto.get('nombre', 'Desconocido')
    
    df['nombre_producto'] = df['id_producto'].apply(get_producto_nombre)
    
    df['fecha_formato'] = df['fecha'].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    return render_template('pandas.html', 
                         df=df,
                         total_ventas=len(df),
                         total_productos=df['cantidad'].sum(),
                         clientes_unicos=df['nombreCliente'].nunique(),
                         venta_promedio=df['cantidad'].mean())

@app.route('/export')
def exportarExcel():
    ventas = obtener_ventas_MySql()
    df = pd.DataFrame(ventas, columns=['id_venta', 'id_producto', 'cantidad', 'nombreCliente', 'fecha'])
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Ventas')
        writer.close()
        output.seek(0)
        return send_file(output, 
                        download_name="ventas.xlsx", 
                        as_attachment=True, 
                        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    return redirect('/dashboard')

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