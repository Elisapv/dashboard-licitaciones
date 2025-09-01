import psycopg2
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

DB_USER = os.getenv("user")
DB_PASSWORD = os.getenv("password")
DB_HOST = os.getenv("host")
DB_PORT = os.getenv("port")
DB_NAME = os.getenv("dbname")

try:
    # Conexión a la base
    conn = psycopg2.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME
    )
    cursor = conn.cursor()
    print("Conexión exitosa")

    # --- Eliminar datos ---
    cursor.execute('DELETE FROM "order";')
    print("Tabla 'order' limpiada")

    cursor.execute('DELETE FROM tender;')
    print("Tabla 'tender' limpiada")

    cursor.execute('DELETE FROM product;')
    print("Tabla 'product' limpiada")

    conn.commit()
    print("Todas las tablas han sido limpiadas correctamente.")

    cursor.close()
    conn.close()
    print("Conexión cerrada")

except Exception as e:
    print(f"Error al limpiar las tablas: {e}")
