from flask import Flask, render_template, request, redirect, send_file, url_for
import pandas as pd 
from io import BytesIO

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
        return send_file(output, download_name="ventas.xlsx", as_attachment=True, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    redirect('/dashboard')

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