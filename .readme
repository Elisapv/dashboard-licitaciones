# Mini Sistema de Gestión de Licitaciones

Este proyecto es un **dashboard interactivo** desarrollado con **Streamlit** y **PostgreSQL**.

## Características

- Registro de nuevas licitaciones con **ID manual** y fecha de adjudicación.  
- Selección de productos y cantidades para cada licitación.  
- Cálculo automático de márgenes por producto y por licitación.  
- Visualización de resumen de licitaciones y detalle de productos.  
- Integración con **PostgreSQL** para almacenamiento persistente.  

## Tecnologías utilizadas

- **Python 3.11+**  
- **Streamlit** para la interfaz web interactiva  
- **Pandas** para manipulación de datos  
- **psycopg2** para conexión con PostgreSQL  
- **dotenv** para manejar variables de entorno  
- **PostgreSQL / Supabase** como base de datos  

## Estructura de tablas

### Tabla `tender` (licitaciones)

```sql

-- Tabla tender (licitaciones)
CREATE TABLE IF NOT EXISTS tender (
    id TEXT PRIMARY KEY,                 -- ID tal cual viene del endpoint o formulario
    cliente TEXT NOT NULL,               -- client
    fecha_adjudicacion DATE NOT NULL     -- creation_date del endpoint
);

-- Tabla product
CREATE TABLE IF NOT EXISTS product (
    id BIGINT PRIMARY KEY,               -- SKU del producto como ID
    nombre TEXT NOT NULL,                -- title
    sku TEXT NOT NULL,                   -- sku
    precio_venta NUMERIC NOT NULL CHECK (precio_venta > 0),  -- price
    costo_unitario NUMERIC NOT NULL CHECK (costo_unitario > 0) -- cost
);

-- Tabla order (detalle de licitación)
CREATE TABLE IF NOT EXISTS "order" (
    id TEXT PRIMARY KEY,                 -- id del order del endpoint
    tender_id TEXT NOT NULL REFERENCES tender(id) ON DELETE CASCADE,
    product_id BIGINT NOT NULL REFERENCES product(id) ON DELETE RESTRICT,
    cantidad INT NOT NULL CHECK (cantidad > 0),  -- quantity
    precio NUMERIC NOT NULL                       -- price
);

-- Vista tender_margin
CREATE OR REPLACE VIEW tender_margin AS
SELECT 
    t.id AS tender_id,
    t.cliente,
    t.fecha_adjudicacion,
    COALESCE(SUM((o.precio - p.costo_unitario) * o.cantidad), 0) AS margen_total
FROM tender t
LEFT JOIN "order" o ON o.tender_id = t.id
LEFT JOIN product p ON p.id = o.product_id
GROUP BY t.id, t.cliente, t.fecha_adjudicacion;
