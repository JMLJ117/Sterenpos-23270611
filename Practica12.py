import mysql.connector
import os

# Establecer la conexión
conexion = mysql.connector.connect(
    host="localhost",
    user="root",
    password="alfa0117",
    database="sterenpos",
    #port=3307
)

if conexion.is_connected():
    print("Conexión exitosa")
    # Crear un cursor
    cursor = conexion.cursor()
else:
    print("No se pudo conectar a la base de datos")

# CRUD para Productos
def ver_productos():
    cursor.execute("SELECT p.ProductoID, p.Nombre, p.Categoria, p.Precio, p.Stock, pr.Nombre as Proveedor FROM productos p LEFT JOIN proveedores pr ON p.ProveedorID = pr.ProveedorID")
    resultados = cursor.fetchall()
    print("\n--- LISTA DE PRODUCTOS ---")
    print("ID | Nombre | Categoría | Precio | Stock | Proveedor")
    for fila in resultados:
        print(f"{fila[0]} | {fila[1]} | {fila[2]} | ${fila[3]} | {fila[4]} | {fila[5]}")

def pedir_datos_producto():
    nombre = input("Nombre del producto: ")
    categoria = input("Categoría: ")
    precio = float(input("Precio: "))
    stock = int(input("Stock: "))
    proveedor_id = input("ID del proveedor (dejar vacío si no aplica): ")
    if proveedor_id == "":
        proveedor_id = None
    else:
        proveedor_id = int(proveedor_id)
    return nombre, categoria, precio, stock, proveedor_id

def insertar_producto(nombre, categoria, precio, stock, proveedor_id):
    query = "INSERT INTO productos(Nombre, Categoria, Precio, Stock, ProveedorID) VALUES (%s, %s, %s, %s, %s)"
    valores = (nombre, categoria, precio, stock, proveedor_id)
    cursor.execute(query, valores)
    conexion.commit()
    print(f"Producto '{nombre}' agregado correctamente")

def actualizar_producto(producto_id):
    nombre, categoria, precio, stock, proveedor_id = pedir_datos_producto()
    query = "UPDATE productos SET Nombre=%s, Categoria=%s, Precio=%s, Stock=%s, ProveedorID=%s WHERE ProductoID=%s"
    valores = (nombre, categoria, precio, stock, proveedor_id, producto_id)
    cursor.execute(query, valores)
    conexion.commit()
    print(f"Producto ID: {producto_id} actualizado correctamente")

def eliminar_producto(producto_id):
    query = "DELETE FROM productos WHERE ProductoID=%s"
    valores = (producto_id,)
    cursor.execute(query, valores)
    conexion.commit()
    print(f"Producto ID: {producto_id} eliminado correctamente")

# CRUD para Proveedores
def ver_proveedores():
    cursor.execute("SELECT * FROM proveedores")
    resultados = cursor.fetchall()
    print("\n--- LISTA DE PROVEEDORES ---")
    print("ID | Nombre | Contacto | Teléfono")
    for fila in resultados:
        print(f"{fila[0]} | {fila[1]} | {fila[2]} | {fila[3]}")

def pedir_datos_proveedor():
    nombre = input("Nombre del proveedor: ")
    contacto = input("Nombre de contacto: ")
    telefono = input("Teléfono: ")
    return nombre, contacto, telefono

def insertar_proveedor(nombre, contacto, telefono):
    query = "INSERT INTO proveedores(Nombre, Contacto, Telefono) VALUES (%s, %s, %s)"
    valores = (nombre, contacto, telefono)
    cursor.execute(query, valores)
    conexion.commit()
    print(f"Proveedor '{nombre}' agregado correctamente")

def actualizar_proveedor(proveedor_id):
    nombre, contacto, telefono = pedir_datos_proveedor()
    query = "UPDATE proveedores SET Nombre=%s, Contacto=%s, Telefono=%s WHERE ProveedorID=%s"
    valores = (nombre, contacto, telefono, proveedor_id)
    cursor.execute(query, valores)
    conexion.commit()
    print(f"Proveedor ID: {proveedor_id} actualizado correctamente")

def eliminar_proveedor(proveedor_id):
    query = "DELETE FROM proveedores WHERE ProveedorID=%s"
    valores = (proveedor_id,)
    cursor.execute(query, valores)
    conexion.commit()
    print(f"Proveedor ID: {proveedor_id} eliminado correctamente")

# CRUD para Usuarios
def ver_usuarios():
    cursor.execute("SELECT u.UsuarioID, u.Nombre, u.Correo, r.Nombre as Rol FROM usuarios u JOIN roles r ON u.RolID = r.RolID")
    resultados = cursor.fetchall()
    print("\n--- LISTA DE USUARIOS ---")
    print("ID | Nombre | Correo | Rol")
    for fila in resultados:
        print(f"{fila[0]} | {fila[1]} | {fila[2]} | {fila[3]}")

def pedir_datos_usuario():
    nombre = input("Nombre del usuario: ")
    correo = input("Correo electrónico: ")
    contrasena = input("Contraseña: ")
    rol_id = int(input("ID del rol: "))
    return nombre, correo, contrasena, rol_id

def insertar_usuario(nombre, correo, contrasena, rol_id):
    query = "INSERT INTO usuarios(Nombre, Correo, Contrasena, RolID) VALUES (%s, %s, MD5(%s), %s)"
    valores = (nombre, correo, contrasena, rol_id)
    cursor.execute(query, valores)
    conexion.commit()
    print(f"Usuario '{nombre}' agregado correctamente")

def actualizar_usuario(usuario_id):
    nombre, correo, contrasena, rol_id = pedir_datos_usuario()
    query = "UPDATE usuarios SET Nombre=%s, Correo=%s, Contrasena=MD5(%s), RolID=%s WHERE UsuarioID=%s"
    valores = (nombre, correo, contrasena, rol_id, usuario_id)
    cursor.execute(query, valores)
    conexion.commit()
    print(f"Usuario ID: {usuario_id} actualizado correctamente")

def eliminar_usuario(usuario_id):
    query = "DELETE FROM usuarios WHERE UsuarioID=%s"
    valores = (usuario_id,)
    cursor.execute(query, valores)
    conexion.commit()
    print(f"Usuario ID: {usuario_id} eliminado correctamente")

# CRUD para Clientes
def ver_clientes():
    cursor.execute("SELECT * FROM clientes")
    resultados = cursor.fetchall()
    print("\n--- LISTA DE CLIENTES ---")
    print("ID | Nombre | RFC | Teléfono")
    for fila in resultados:
        print(f"{fila[0]} | {fila[1]} | {fila[2]} | {fila[3]}")

def pedir_datos_cliente():
    nombre = input("Nombre del cliente: ")
    rfc = input("RFC: ")
    telefono = input("Teléfono: ")
    return nombre, rfc, telefono

def insertar_cliente(nombre, rfc, telefono):
    query = "INSERT INTO clientes(Nombre, RFC, Telefono) VALUES (%s, %s, %s)"
    valores = (nombre, rfc, telefono)
    cursor.execute(query, valores)
    conexion.commit()
    print(f"Cliente '{nombre}' agregado correctamente")

def actualizar_cliente(cliente_id):
    nombre, rfc, telefono = pedir_datos_cliente()
    query = "UPDATE clientes SET Nombre=%s, RFC=%s, Telefono=%s WHERE ClienteID=%s"
    valores = (nombre, rfc, telefono, cliente_id)
    cursor.execute(query, valores)
    conexion.commit()
    print(f"Cliente ID: {cliente_id} actualizado correctamente")

def eliminar_cliente(cliente_id):
    query = "DELETE FROM clientes WHERE ClienteID=%s"
    valores = (cliente_id,)
    cursor.execute(query, valores)
    conexion.commit()
    print(f"Cliente ID: {cliente_id} eliminado correctamente")

def cerrar():
    cursor.close()
    conexion.close()
    print("Conexión cerrada correctamente")

def limpiar_pantalla():
    os.system('cls' if os.name == 'nt' else 'clear')

def menu_principal():
    while True:
        limpiar_pantalla()
        print("\n=== SISTEMA DE GESTIÓN STERENPOS ===")
        print("1. Gestionar Productos")
        print("2. Gestionar Proveedores")
        print("3. Gestionar Usuarios")
        print("4. Gestionar Clientes")
        print("0. Salir")
        
        opcion = input("\nSeleccione una opción: ")
        
        if opcion == "1":
            menu_productos()
        elif opcion == "2":
            menu_proveedores()
        elif opcion == "3":
            menu_usuarios()
        elif opcion == "4":
            menu_clientes()
        elif opcion == "0":
            break
        else:
            input("Opción inválida. Presione Enter para continuar...")

def menu_productos():
    while True:
        limpiar_pantalla()
        print("\n=== GESTIÓN DE PRODUCTOS ===")
        print("1. Ver todos los productos")
        print("2. Agregar nuevo producto")
        print("3. Actualizar producto")
        print("4. Eliminar producto")
        print("0. Volver al menú principal")
        
        opcion = input("\nSeleccione una opción: ")
        
        if opcion == "1":
            ver_productos()
        elif opcion == "2":
            nombre, categoria, precio, stock, proveedor_id = pedir_datos_producto()
            insertar_producto(nombre, categoria, precio, stock, proveedor_id)
        elif opcion == "3":
            ver_productos()
            producto_id = int(input("\nIngrese el ID del producto a actualizar: "))
            actualizar_producto(producto_id)
        elif opcion == "4":
            ver_productos()
            producto_id = int(input("\nIngrese el ID del producto a eliminar: "))
            eliminar_producto(producto_id)
        elif opcion == "0":
            break
        else:
            print("Opción inválida")
        
        input("\nPresione Enter para continuar...")

def menu_proveedores():
    while True:
        limpiar_pantalla()
        print("\n=== GESTIÓN DE PROVEEDORES ===")
        print("1. Ver todos los proveedores")
        print("2. Agregar nuevo proveedor")
        print("3. Actualizar proveedor")
        print("4. Eliminar proveedor")
        print("0. Volver al menú principal")
        
        opcion = input("\nSeleccione una opción: ")
        
        if opcion == "1":
            ver_proveedores()
        elif opcion == "2":
            nombre, contacto, telefono = pedir_datos_proveedor()
            insertar_proveedor(nombre, contacto, telefono)
        elif opcion == "3":
            ver_proveedores()
            proveedor_id = int(input("\nIngrese el ID del proveedor a actualizar: "))
            actualizar_proveedor(proveedor_id)
        elif opcion == "4":
            ver_proveedores()
            proveedor_id = int(input("\nIngrese el ID del proveedor a eliminar: "))
            eliminar_proveedor(proveedor_id)
        elif opcion == "0":
            break
        else:
            print("Opción inválida")
        
        input("\nPresione Enter para continuar...")

def menu_usuarios():
    while True:
        limpiar_pantalla()
        print("\n=== GESTIÓN DE USUARIOS ===")
        print("1. Ver todos los usuarios")
        print("2. Agregar nuevo usuario")
        print("3. Actualizar usuario")
        print("4. Eliminar usuario")
        print("0. Volver al menú principal")
        
        opcion = input("\nSeleccione una opción: ")
        
        if opcion == "1":
            ver_usuarios()
        elif opcion == "2":
            nombre, correo, contrasena, rol_id = pedir_datos_usuario()
            insertar_usuario(nombre, correo, contrasena, rol_id)
        elif opcion == "3":
            ver_usuarios()
            usuario_id = int(input("\nIngrese el ID del usuario a actualizar: "))
            actualizar_usuario(usuario_id)
        elif opcion == "4":
            ver_usuarios()
            usuario_id = int(input("\nIngrese el ID del usuario a eliminar: "))
            eliminar_usuario(usuario_id)
        elif opcion == "0":
            break
        else:
            print("Opción inválida")
        
        input("\nPresione Enter para continuar...")

def menu_clientes():
    while True:
        limpiar_pantalla()
        print("\n=== GESTIÓN DE CLIENTES ===")
        print("1. Ver todos los clientes")
        print("2. Agregar nuevo cliente")
        print("3. Actualizar cliente")
        print("4. Eliminar cliente")
        print("0. Volver al menú principal")
        
        opcion = input("\nSeleccione una opción: ")
        
        if opcion == "1":
            ver_clientes()
        elif opcion == "2":
            nombre, rfc, telefono = pedir_datos_cliente()
            insertar_cliente(nombre, rfc, telefono)
        elif opcion == "3":
            ver_clientes()
            cliente_id = int(input("\nIngrese el ID del cliente a actualizar: "))
            actualizar_cliente(cliente_id)
        elif opcion == "4":
            ver_clientes()
            cliente_id = int(input("\nIngrese el ID del cliente a eliminar: "))
            eliminar_cliente(cliente_id)
        elif opcion == "0":
            break
        else:
            print("Opción inválida")
        
        input("\nPresione Enter para continuar...")

if __name__ == "__main__":
    try:
        menu_principal()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cerrar()