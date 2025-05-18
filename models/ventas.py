from db import conectar
from utils import mostrar_popup
from kivy.uix.recycleview import RecycleView
import datetime

def ver_ventas_gui(rv: RecycleView):
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
            FROM ventas v
            JOIN usuarios u ON v.UsuarioID = u.UsuarioID
            JOIN clientes c ON v.ClienteID = c.ClienteID
            ORDER BY v.Fecha DESC
        """)
        rv.data = [{
            'text': (
                f"ID Venta: {row['VentaID']}  |  "
                f"Fecha: {row['Fecha']}  |  "
                f"Vendedor: {row['Vendedor']}  |  "
                f"Cliente: {row['Cliente']}  |  "
                f"Total: ${row['Total']:.2f}"
            )
        } for row in cur.fetchall()]
    except Exception as e:
        mostrar_popup('Error al listar ventas', str(e))
    finally:
        cur.close()
        conn.close()

def nueva_venta(datos):
    conn = conectar()
    cur = conn.cursor()
    try:
        fecha = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cur.execute(
            "INSERT INTO ventas (Fecha,UsuarioID,ClienteID,Total) VALUES (%s,%s,%s,%s)",
            (fecha, int(datos['UsuarioID']), int(datos['ClienteID']), float(datos['Total']))
        )
        conn.commit()
        mostrar_popup('Éxito', 'Venta registrada correctamente')
    except Exception as e:
        mostrar_popup('Error al registrar venta', str(e))
    finally:
        cur.close()
        conn.close()

def historial_ventas(rv: RecycleView):
    ver_ventas_gui(rv)

