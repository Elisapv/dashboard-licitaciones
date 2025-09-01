import streamlit as st
import psycopg2
import pandas as pd
from dotenv import load_dotenv
import os
import datetime

# --- Configuración ---
load_dotenv()
conn = psycopg2.connect(
    user=os.getenv("user"),
    password=os.getenv("password"),
    host=os.getenv("host"),
    port=os.getenv("port"),
    dbname=os.getenv("dbname")
)

st.set_page_config(page_title="Mini Sistema de Licitaciones", layout="wide")
st.title("Mini Sistema de Gestión de Licitaciones Internas")
st.markdown("---")

# --- Resumen de licitaciones ---
st.subheader("Resumen de Licitaciones con Margen Total")
tender_df = pd.read_sql("""
    SELECT t.id AS tender_id, t.cliente, t.fecha_adjudicacion,
           COALESCE(SUM((o.precio - p.costo_unitario) * o.cantidad), 0) AS margen_total
    FROM tender t
    LEFT JOIN "order" o ON o.tender_id = t.id
    LEFT JOIN product p ON p.id = o.product_id
    GROUP BY t.id, t.cliente, t.fecha_adjudicacion
    ORDER BY t.fecha_adjudicacion DESC;
""", conn)

st.markdown(
    f"""
    <div style="display: flex; justify-content: center;">
        {tender_df.to_html(index=False)}
    </div>
    """, unsafe_allow_html=True
)

# --- Detalle de licitación ---
st.subheader("Detalle de Licitación")
tender_id = st.selectbox("Selecciona una Licitación", tender_df["tender_id"])
order_df = pd.read_sql(f"""
    SELECT o.id AS order_id, p.nombre AS producto, o.cantidad, 
           p.precio_venta, p.costo_unitario
    FROM "order" o
    JOIN product p ON p.id = o.product_id
    WHERE o.tender_id = '{tender_id}';
""", conn)

if not order_df.empty:
    order_df["margen"] = (order_df["precio_venta"] - order_df["costo_unitario"]) * order_df["cantidad"]
    st.dataframe(order_df)
    st.subheader("Margen por Producto")
    st.dataframe(order_df[["producto", "cantidad", "margen"]])
    st.subheader("Margen Total")
    st.write(order_df["margen"].sum())
else:
    st.info("Esta licitación aún no tiene productos adjudicados.")

st.markdown("---")

# --- Registrar nueva licitación ---
st.subheader("Registrar Nueva Licitación")
with st.form("new_tender_form", clear_on_submit=True):
    id_tender = st.text_input("ID Licitación", placeholder="Ej: 2306267LE24")
    cliente = st.text_input("Cliente", placeholder="Ej: Municipalidad de Santiago")
    fecha = st.date_input("Fecha de adjudicación", value=datetime.date.today())

    # Selección de productos
    prod_df = pd.read_sql("SELECT id, nombre, precio_venta, costo_unitario FROM product ORDER BY nombre;", conn)
    selected_products = st.multiselect(
        "Selecciona productos",
        options=prod_df["id"],
        format_func=lambda x: prod_df.loc[prod_df["id"] == x, "nombre"].values[0]
    )

    cantidades = {}
    for pid in selected_products:
        pname = prod_df.loc[prod_df["id"] == pid, "nombre"].values[0]
        cantidades[pid] = st.number_input(f"Cantidad para {pname}", min_value=1, value=1, key=f"qty_{pid}")

    submitted = st.form_submit_button("Guardar Licitación")

    if submitted:
        if not id_tender or not cliente or not selected_products:
            st.error("Debe ingresar un ID, cliente y al menos un producto.")
        else:
            try:
                cur = conn.cursor()
                # Insertar licitación usando ID del formulario
                cur.execute(
                    "INSERT INTO tender (id, cliente, fecha_adjudicacion) VALUES (%s, %s, %s);",
                    (id_tender, cliente, fecha)
                )

                # Insertar productos adjudicados
                total_margen = 0
                for pid, qty in cantidades.items():
                    row = prod_df.loc[prod_df["id"] == pid].iloc[0]
                    if row["precio_venta"] <= row["costo_unitario"]:
                        st.warning(f"El producto {row['nombre']} tiene precio de venta <= costo. No se insertó.")
                        continue
                    order_id = f"{id_tender}-{pid}"  # id único de la orden
                    cur.execute(
                        'INSERT INTO "order" (id, tender_id, product_id, cantidad, precio) VALUES (%s, %s, %s, %s, %s);',
                        (order_id, id_tender, pid, qty, row["precio_venta"])
                    )
                    total_margen += (row["precio_venta"] - row["costo_unitario"]) * qty

                conn.commit()
                cur.close()
                st.success(f"Licitación registrada con ID {id_tender} con margen total {total_margen}")

            except Exception as e:
                conn.rollback()
                st.error(f"Error al registrar licitación: {e}")
