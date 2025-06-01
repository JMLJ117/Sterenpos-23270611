# models/ventas_helper.py
from kivy.uix.recycleview import RecycleView  # ✅ Importa RecycleView
from db import conectar
from utils import mostrar_popup

def ver_ventas_gui(rv: RecycleView):  # Ahora RecycleView está definido
    conn = conectar()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("""
            SELECT 
                v.VentaID,
                v.Fecha,
                u.Nombre AS Vendedor,
                c.Nombre AS Cliente,
                v.Total
            FROM Ventas v
            JOIN Usuarios u ON v.UsuarioID = u.UsuarioID
            JOIN Clientes c ON v.ClienteID = c.ClienteID
            ORDER BY v.Fecha DESC
        """)
        ventas = cur.fetchall()
        rv.data = [{
            'text': (
                f"ID: {row['VentaID']}  |  "
                f"Fecha: {row['Fecha']}  |  "
                f"Vendedor: {row['Vendedor']}  |  "
                f"Cliente: {row['Cliente']}  |  "
                f"Total: ${row['Total']:.2f}"
            ),
            'venta_id': row['VentaID']
        } for row in ventas]
    except Exception as e:
        mostrar_popup('Error al listar ventas', str(e))
    finally:
        cur.close()
        conn.close()

def obtener_detalle_venta(venta_id, callback):
    conn = conectar()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("""
            SELECT 
                p.Nombre AS Producto,
                dv.Cantidad,
                dv.PrecioUnitario,
                dv.Subtotal
            FROM DetalleVenta dv
            JOIN Productos p ON dv.ProductoID = p.ProductoID
            WHERE dv.VentaID = %s
        """, (venta_id,))
        detalles = cur.fetchall()
        cur.execute("""
            SELECT 
                mp.Tipo AS MetodoPago,
                v.Total,
                v.FacturaGenerada
            FROM Ventas v
            JOIN ModoPago mp ON v.ModoPagoID = mp.ModoPagoID
            WHERE v.VentaID = %s
        """, (venta_id,))
        info_venta = cur.fetchone()
        callback(detalles, info_venta)
    finally:
        cur.close()
        conn.close()