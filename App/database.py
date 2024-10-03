import os
from dotenv import load_dotenv
import mysql.connector
from pymongo import MongoClient

# Cargar las variables de entorno 
load_dotenv()

# Conexión a MySQL usando variables de entorno
def connect_mysql():
    connection = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DB")
    )
    return connection

# Conexión a MongoDB usando variables de entorno
def connect_mongo():
    client = MongoClient(os.getenv("MONGO_URI"))
    db = client["Productos_BD"]
    return db
