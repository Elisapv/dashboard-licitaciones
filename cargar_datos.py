
import psycopg2
from dotenv import load_dotenv
import os
import requests

# Cargar variables de entorno
load_dotenv()

DB_USER = os.getenv("user")
DB_PASSWORD = os.getenv("password")
DB_HOST = os.getenv("host")
DB_PORT = os.getenv("port")
DB_NAME = os.getenv("dbname")

def normalize_tender_id(tid):
    """Quita los guines del Id de tender para que coincida con el order"""
    return tid.replace("-", "")

try:
    # Conexión a la base
    connection = psycopg2.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME
    )
    print("Conexión exitosa")
    cursor = connection.cursor()

    # --- Tender ---
    tender_data = requests.get("https://kaiken.up.railway.app/webhook/tender-sample").json()
    for row in tender_data:
        tid = normalize_tender_id(row["id"])
        cursor.execute(
            "INSERT INTO tender (id, cliente, fecha_adjudicacion) VALUES (%s, %s, %s) ON CONFLICT (id) DO NOTHING",
            (tid, row["client"], row["creation_date"])
        )
    print(f"{len(tender_data)} filas de tender insertadas")

    # --- Product ---
    product_data = requests.get("https://kaiken.up.railway.app/webhook/product-sample").json()
    for row in product_data:
        precio_venta = row["cost"] * 1.4  # ejemplo: 40% margen
        cursor.execute(
            "INSERT INTO product (id, nombre, sku, precio_venta, costo_unitario) VALUES (%s, %s, %s, %s, %s) ON CONFLICT (id) DO NOTHING;",
            (int(row["sku"]), row["title"], row["sku"], precio_venta, row["cost"])
        )
    print(f"{len(product_data)} filas de product insertadas")

    # --- Order ---
    order_data = requests.get("https://kaiken.up.railway.app/webhook/order-sample").json()
    for row in order_data:
        order_id = row["id"]
        tender_id = row["tender_id"]  # Debe coincidir con tender.id en la tabla
        product_id = int(row["product_id"])
        cantidad = int(row["quantity"])
        precio = row["price"]
        cursor.execute("""INSERT INTO "order" (id, tender_id, product_id, cantidad, precio) VALUES (%s, %s, %s, %s, %s) ON CONFLICT (id) DO NOTHING""",
            (order_id, tender_id, product_id, cantidad, precio)
        )
    print(f"{len(order_data)} filas de order insertadas")


    connection.commit()
    print("Todos los datos fueron cargados correctamente.")

    cursor.close()
    connection.close()
    print("Conexión cerrada")

except Exception as e:
    print(f"Error de conexión o inserción: {e}")
