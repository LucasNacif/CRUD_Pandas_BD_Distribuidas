import base64
import io
from flask import Flask, render_template, request, redirect, send_file, url_for, flash, jsonify
import pandas as pd 
from io import BytesIO
from bson import ObjectId, errors as bson_errors
import seaborn as sns
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from werkzeug.utils import secure_filename
import os


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
app.secret_key = 'claveUltraSuperSecretaQueNadieConoceyNadieVe'

ALLOWED_EXTENSIONS = {'xlsx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return redirect(url_for('listar_ventas_productos'))

# Rutas para Ventas
@app.route('/ventas_productos')
def listar_ventas_productos():
    ventas = obtener_ventas_MySql()
    productos = obtener_productos_Mongo()
    
    if not productos:
        flash('No hay productos disponibles. Por favor, agregue productos primero.', 'warning')
        return render_template('listar_ventas_productos.html', ventas=ventas, productos=productos)

    if not ventas:
        flash('No hay ventas registradas aún.', 'warning')
        return render_template('listar_ventas_productos.html', ventas=ventas, productos=productos)
    
    productosVentas = {str(p['_id']): p for p in productos}
    return render_template('listar_ventas_productos.html', ventas=ventas, productos=productos, productosVentas=productosVentas)

@app.route('/crear_venta', methods=['GET', 'POST'])
def crear_venta():
    productos = obtener_productos_Mongo()

    if not productos:
        flash('No hay productos disponibles para vender. Por favor, agregue productos primero.', 'error')
        return redirect(url_for('listar_ventas_productos'))

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
            return redirect(url_for('listar_ventas_productos'))
            
        except ValueError:
            flash('Cantidad inválida', 'error')
        except Exception as e:
            flash(f'Error al crear la venta: {str(e)}', 'error')
    return render_template('crear_venta.html', productos=productos)

@app.route('/ventas/modificar/<int:id_venta>', methods=['GET', 'POST'])
def modificar_venta(id_venta):
  
    if request.method == 'POST':
        nombre_cliente = request.form['nombre_cliente']
        actualizar_venta_MySql(id_venta, nombre_cliente)
        flash('Venta modificada exitosamente', 'success')
        return redirect(url_for('listar_ventas_productos'))

    venta = obtener_venta_por_id_MySql(id_venta)
    producto = obtener_producto_por_id_Mongo(venta[1]) 
    return render_template('modificar_venta.html', venta=venta, producto=producto)

@app.route('/ventas/eliminar/<int:id_venta>', methods=['POST'])
def eliminar_venta(id_venta):
    exito = eliminar_venta_MySql(id_venta)
    if exito:
        flash('Venta eliminada exitosamente', 'success')
    else:
        flash('Error al eliminar la venta', 'error')
    return redirect(url_for('listar_ventas_productos'))


# Rutas para Productos
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
        return redirect(url_for('listar_ventas_productos'))
    
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
        return redirect(url_for('listar_ventas_productos'))
    
    producto = obtener_producto_por_id_Mongo(id_producto)
    if producto:
        return render_template('modificar_producto.html', producto=producto)
    flash('Producto no encontrado', 'error')
    return redirect(url_for('listar_ventas_productos'))

@app.route('/productos/eliminar/<id_producto>')
def eliminar_producto(id_producto):
    exito = eliminar_producto_Mongo(id_producto)
    if exito:
        flash('Producto eliminado exitosamente', 'success')
    else:
        flash('Error al eliminar el producto', 'error')
    return redirect(url_for('listar_ventas_productos'))

@app.route('/productos/<id_producto>')
def ver_producto(id_producto):
    producto = obtener_producto_por_id_Mongo(id_producto)
    if producto:
        return render_template('ver_producto.html', producto=producto)
    flash('Producto no encontrado', 'error')
    return redirect(url_for('listar_ventas_productos'))


# Rutas para Dashboard
def generar_grafico():
    productos = obtener_productos_Mongo()

    if not productos:
       return []
    
    # Si hay productos, proceder a crear el gráfico
    df = pd.DataFrame(productos)

    plt.figure(figsize=(10, 7))
    plt.pie(df['cantidad_stock'], labels=df['nombre'], autopct='%1.1f%%', startangle=90)
    plt.title('Distribución de Stock de Productos')
    plt.axis('equal')

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    buffer.seek(0)
    imagen = base64.b64encode(buffer.getvalue()).decode()
    plt.close()

    return imagen

@app.route('/dashboard')
def dashboard():
    ventas = obtener_ventas_MySql()
    grafico_productos = generar_grafico()
    
    if not ventas:
        flash('No hay ventas registradas. Realice una venta para ver estadísticas.', 'warning')
        df = pd.DataFrame(ventas, columns=[])
        return render_template('pandas.html', ventas=[], total_ventas=0, total_productos=0, clientes_unicos=0, venta_promedio=0,  grafico_productos=grafico_productos, df=df)

    df = pd.DataFrame(ventas, columns=['id_venta', 'id_producto', 'cantidad', 'nombreCliente', 'fecha'])
    df['fecha'] = pd.to_datetime(df['fecha'])
    

    def get_producto_nombre(id_producto):
        producto = obtener_producto_por_id_Mongo(id_producto)
        if producto:
            return producto['nombre']
        else:
            return('Desconocido')

    
    df['nombre_producto'] = df['id_producto'].apply(get_producto_nombre)
    
    df['fecha_formato'] = df['fecha'].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    return render_template('pandas.html', 
                         df=df,
                         total_ventas=len(df),
                         total_productos=df['cantidad'].sum(),
                         clientes_unicos=df['nombreCliente'].nunique(),
                         venta_promedio=df['cantidad'].mean(),
                         grafico_productos=grafico_productos)

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


# Rutas para importar datos con excel
@app.route('/importar_ventas', methods=['POST'])
def importar_ventas():
    # Verificar si el archivo fue enviado
    if 'file' not in request.files:
        flash('No se ha seleccionado ningún archivo.', 'error')
        return redirect(request.url)

    file = request.files['file']
    
    if file.filename == '':
        flash('No se ha seleccionado un archivo.', 'error')
        return redirect(request.url)

    # Crear el directorio 'uploads' si no existe
    upload_folder = os.path.join(os.getcwd(), 'uploads')
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    # Guardar el archivo
    filepath = os.path.join(upload_folder, 'ventas.xlsx')
    file.save(filepath)
    
    exito = procesarExcel()

    if exito:
        flash('Se han importado los datos correctamente.', 'success')
    else:
        flash('Ha ocurrido un error al importar los datos.', 'error')
        
    return redirect(url_for('dashboard'))

def procesarExcel():
    try:
        # Leer el archivo Excel con pandas
        df = pd.read_excel('uploads/ventas.xlsx')

        for _, row in df.iterrows():
            crear_venta_MySql(row['id_producto'], row['cantidad'], row['nombreCliente'])
            return True

    except Exception as e:
        flash(f'Error al importar las ventas: {str(e)}', 'error')
        return True
            
@app.route('/importar_productos', methods=['POST'])
def importar_productos():
    if 'file' not in request.files:
        flash('No se seleccionó ningún archivo', 'error')
        return redirect(request.url)
    
    file = request.files['file']
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join('uploads', filename)
        file.save(filepath)

        try:
            # Leer el archivo Excel con pandas
            df = pd.read_excel(filepath)
            for _, row in df.iterrows():
                crear_producto_Mongo(row['nombre_producto'], row['precio_producto'], row['cantidad_producto'])

            flash('Productos importados exitosamente', 'success')
            return redirect(url_for('listar_ventas_productos'))
        except Exception as e:
            flash(f'Error al importar los productos: {str(e)}', 'error')
            return redirect(request.url)

    flash('Formato de archivo no permitido', 'error')
    return redirect(request.url)



if __name__ == '__main__':
    app.run(debug=True)