from App.database import connect_mongo
from bson.objectid import ObjectId

def crear_producto_Mongo(nombre, precio, cantidad_stock):
    db = connect_mongo()
    producto = {
        "nombre": nombre,
        "precio": precio,
        "cantidad_stock": cantidad_stock
    }
    result = db.productos.insert_one(producto)
    return str(result.inserted_id) 

def obtener_productos_Mongo():
    db = connect_mongo()
    productos = db.productos.find()
    return list(productos)  

def obtener_producto_por_id_Mongo(id):
    db = connect_mongo()
    producto = db.productos.find_one({"_id": ObjectId(id)})
    return producto  

def eliminar_producto_Mongo(id):
    db = connect_mongo()
    result = db.productos.delete_one({"_id": ObjectId(id)})
    return result.deleted_count > 0  

def actualizar_producto_Mongo(id, nombre, precio, cantidad_stock):
    db = connect_mongo()
    result = db.productos.update_one(
        {"_id": ObjectId(id)},
        {"$set": {"nombre": nombre, "precio": precio, "cantidad_stock": cantidad_stock}}
    )
    return result.modified_count > 0 
