import mysql.connector
from mysql.connector import Error
from utils import mostrar_popup

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'alfa0117',
    'database': 'sterenpos',
    'raise_on_warnings': True
}

def conectar():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        if conn.is_connected():
            return conn
    except Error as e:
        mostrar_popup('Error de conexión', str(e))
    return None

def validar_usuario(correo, contrasena):
    conn = conectar()
    if not conn: return None
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT u.UsuarioID, r.Nombre AS Rol "
            "FROM usuarios u JOIN roles r ON u.RolID=r.RolID "
            "WHERE u.Correo=%s AND u.Contrasena=MD5(%s)",
            (correo, contrasena)
        )
        return cur.fetchone()
    except Error as e:
        mostrar_popup('Error en validación', str(e))
        return None
    finally:
        cur.close(); conn.close()
