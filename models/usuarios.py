from db import conectar
from utils import mostrar_popup
from kivy.uix.recycleview import RecycleView

def ver_usuarios_gui(rv: RecycleView):
    conn = conectar(); cur = conn.cursor(dictionary=True)
    try:
        cur.execute("""
            SELECT u.UsuarioID, u.Nombre, u.Correo, r.Nombre AS Rol
            FROM usuarios u
            JOIN roles r ON u.RolID = r.RolID
        """)
        rv.data = [{
            'text': f"{r['UsuarioID']} | {r['Nombre']} | {r['Correo']} | {r['Rol']}"
        } for r in cur.fetchall()]
    except Exception as e:
        mostrar_popup('Error al listar usuarios', str(e))
    finally:
        cur.close(); conn.close()

def agregar_usuario(datos):
    conn = conectar(); cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO usuarios (Nombre, Correo, RolID) VALUES (%s, %s, %s)",
            (datos['Nombre'], datos['Correo'], int(datos['RolID']))
        )
        conn.commit()
        mostrar_popup('Éxito', 'Usuario agregado')
    except Exception as e:
        mostrar_popup('Error al agregar usuario', str(e))
    finally:
        cur.close(); conn.close()

def actualizar_usuario(datos):
    conn = conectar(); cur = conn.cursor()
    try:
        cur.execute(
            "UPDATE usuarios SET Nombre=%s, Correo=%s, RolID=%s WHERE UsuarioID=%s",
            (datos['Nombre'], datos['Correo'], int(datos['RolID']), int(datos['UsuarioID']))
        )
        conn.commit()
        mostrar_popup('Éxito', 'Usuario actualizado')
    except Exception as e:
        mostrar_popup('Error al actualizar usuario', str(e))
    finally:
        cur.close(); conn.close()

def eliminar_usuario(usuario_id):
    conn = conectar(); cur = conn.cursor()
    try:
        cur.execute("DELETE FROM usuarios WHERE UsuarioID=%s", (int(usuario_id),))
        conn.commit()
        mostrar_popup('Éxito', 'Usuario eliminado')
    except Exception as e:
        mostrar_popup('Error al eliminar usuario', str(e))
    finally:
        cur.close(); conn.close()
