from db import conectar
from utils import mostrar_popup
from kivy.uix.recycleview import RecycleView

def ver_productos_gui(rv: RecycleView):
    conn = conectar(); cur = conn.cursor(dictionary=True)
    try:
        cur.execute("""
            SELECT p.ProductoID, p.Nombre, p.Precio, pr.Nombre AS Proveedor
            FROM productos p
            LEFT JOIN proveedores pr ON p.ProveedorID = pr.ProveedorID
        """)
        rv.data = [{
            'text': f"{r['ProductoID']} | {r['Nombre']} | ${r['Precio']:.2f} | {r['Proveedor']}"
        } for r in cur.fetchall()]
    except Exception as e:
        mostrar_popup('Error al listar productos', str(e))
    finally:
        cur.close(); conn.close()

def agregar_producto(datos):
    conn = conectar(); cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO productos (Nombre, Precio, ProveedorID) VALUES (%s, %s, %s)",
            (datos['Nombre'], float(datos['Precio']), int(datos['ProveedorID']))
        )
        conn.commit()
        mostrar_popup('Éxito', 'Producto agregado')
    except Exception as e:
        mostrar_popup('Error al agregar producto', str(e))
    finally:
        cur.close(); conn.close()

def actualizar_producto(datos):
    conn = conectar(); cur = conn.cursor()
    try:
        cur.execute(
            "UPDATE productos SET Nombre=%s, Precio=%s, ProveedorID=%s WHERE ProductoID=%s",
            (datos['Nombre'], float(datos['Precio']),
             int(datos['ProveedorID']), int(datos['ProductoID']))
        )
        conn.commit()
        mostrar_popup('Éxito', 'Producto actualizado')
    except Exception as e:
        mostrar_popup('Error al actualizar producto', str(e))
    finally:
        cur.close(); conn.close()

def eliminar_producto(prod_id):
    conn = conectar(); cur = conn.cursor()
    try:
        cur.execute("DELETE FROM productos WHERE ProductoID=%s", (int(prod_id),))
        conn.commit()
        mostrar_popup('Éxito', 'Producto eliminado')
    except Exception as e:
        mostrar_popup('Error al eliminar producto', str(e))
    finally:
        cur.close(); conn.close()
