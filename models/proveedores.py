from db import conectar
from utils import mostrar_popup
from kivy.uix.recycleview import RecycleView

def ver_proveedores_gui(rv: RecycleView):
    conn = conectar(); cur = conn.cursor(dictionary=True)
    try:
        cur.execute("SELECT ProveedorID, Nombre, Telefono, Direccion FROM proveedores")
        rv.data = [{
            'text': f"{r['ProveedorID']} | {r['Nombre']} | {r['Telefono']} | {r['Direccion']}"
        } for r in cur.fetchall()]
    except Exception as e:
        mostrar_popup('Error al listar proveedores', str(e))
    finally:
        cur.close(); conn.close()

def agregar_proveedor(datos):
    conn = conectar(); cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO proveedores (Nombre, Telefono, Direccion) VALUES (%s, %s, %s)",
            (datos['Nombre'], datos['Telefono'], datos['Direccion'])
        )
        conn.commit()
        mostrar_popup('Éxito', 'Proveedor agregado')
    except Exception as e:
        mostrar_popup('Error al agregar proveedor', str(e))
    finally:
        cur.close(); conn.close()

def actualizar_proveedor(datos):
    conn = conectar(); cur = conn.cursor()
    try:
        cur.execute(
            "UPDATE proveedores SET Nombre=%s, Telefono=%s, Direccion=%s WHERE ProveedorID=%s",
            (datos['Nombre'], datos['Telefono'], datos['Direccion'], int(datos['ProveedorID']))
        )
        conn.commit()
        mostrar_popup('Éxito', 'Proveedor actualizado')
    except Exception as e:
        mostrar_popup('Error al actualizar proveedor', str(e))
    finally:
        cur.close(); conn.close()

def eliminar_proveedor(proveedor_id):
    conn = conectar(); cur = conn.cursor()
    try:
        cur.execute("DELETE FROM proveedores WHERE ProveedorID=%s", (int(proveedor_id),))
        conn.commit()
        mostrar_popup('Éxito', 'Proveedor eliminado')
    except Exception as e:
        mostrar_popup('Error al eliminar proveedor', str(e))
    finally:
        cur.close(); conn.close()

