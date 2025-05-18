from db import conectar
from utils import mostrar_popup
from kivy.uix.recycleview import RecycleView

def ver_clientes_gui(rv: RecycleView):
    conn = conectar(); cur = conn.cursor(dictionary=True)
    try:
        cur.execute("SELECT ClienteID, Nombre, Telefono, Direccion FROM clientes")
        rv.data = [{
            'text': f"{r['ClienteID']} | {r['Nombre']} | {r['Telefono']} | {r['Direccion']}"
        } for r in cur.fetchall()]
    except Exception as e:
        mostrar_popup('Error al listar clientes', str(e))
    finally:
        cur.close(); conn.close()

def agregar_cliente(datos):
    conn = conectar(); cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO clientes (Nombre, Telefono, Direccion) VALUES (%s, %s, %s)",
            (datos['Nombre'], datos['Telefono'], datos['Direccion'])
        )
        conn.commit()
        mostrar_popup('Éxito', 'Cliente agregado')
    except Exception as e:
        mostrar_popup('Error al agregar cliente', str(e))
    finally:
        cur.close(); conn.close()

def actualizar_cliente(datos):
    conn = conectar(); cur = conn.cursor()
    try:
        cur.execute(
            "UPDATE clientes SET Nombre=%s, Telefono=%s, Direccion=%s WHERE ClienteID=%s",
            (datos['Nombre'], datos['Telefono'], datos['Direccion'], int(datos['ClienteID']))
        )
        conn.commit()
        mostrar_popup('Éxito', 'Cliente actualizado')
    except Exception as e:
        mostrar_popup('Error al actualizar cliente', str(e))
    finally:
        cur.close(); conn.close()

def eliminar_cliente(cliente_id):
    conn = conectar(); cur = conn.cursor()
    try:
        cur.execute("DELETE FROM clientes WHERE ClienteID=%s", (int(cliente_id),))
        conn.commit()
        mostrar_popup('Éxito', 'Cliente eliminado')
    except Exception as e:
        mostrar_popup('Error al eliminar cliente', str(e))
    finally:
        cur.close(); conn.close()

