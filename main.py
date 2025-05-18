import os
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from utils import mostrar_popup, solicitar_datos
from db import validar_usuario
from models.productos import ver_productos_gui, agregar_producto, actualizar_producto, eliminar_producto
from models.usuarios import ver_usuarios_gui, agregar_usuario, actualizar_usuario, eliminar_usuario
from models.clientes import ver_clientes_gui, agregar_cliente, actualizar_cliente, eliminar_cliente
from models.proveedores import ver_proveedores_gui, agregar_proveedor, actualizar_proveedor, eliminar_proveedor
from models.ventas import ver_ventas_gui, nueva_venta, historial_ventas

KV_DIR = os.path.join(os.path.dirname(__file__), 'screens')

class LoginScreen(Screen):
    def login(self):
        correo = self.ids.correo.text.strip()
        clave  = self.ids.contrasena.text.strip()
        if not correo or not clave:
            mostrar_popup('Error', 'Debe llenar todos los campos')
            return
        res = validar_usuario(correo, clave)
        if res:
            App.get_running_app().usuario = res
            self.manager.current = 'productos'
        else:
            mostrar_popup('Login fallido', 'Credenciales incorrectas')

class ProductosScreen(Screen):
    def on_enter(self): ver_productos_gui(self.ids.rv)
    def agregar_producto(self):
        solicitar_datos(
            ['Nombre','Precio','ProveedorID'],
            lambda d: (agregar_producto(d), ver_productos_gui(self.ids.rv))
        )
    def actualizar_producto(self):
        solicitar_datos(
            ['ProductoID','Nombre','Precio','ProveedorID'],
            lambda d: (actualizar_producto(d), ver_productos_gui(self.ids.rv))
        )
    def eliminar_producto(self):
        solicitar_datos(
            ['ProductoID'],
            lambda d: (eliminar_producto(d['ProductoID']), ver_productos_gui(self.ids.rv))
        )

class UsuariosScreen(Screen):
    def on_enter(self): ver_usuarios_gui(self.ids.rv)
    def agregar_usuario(self):
        solicitar_datos(
            ['Nombre','Correo','RolID'],
            lambda d:(agregar_usuario(d), ver_usuarios_gui(self.ids.rv))
        )
    def actualizar_usuario(self):
        solicitar_datos(
            ['UsuarioID','Nombre','Correo','RolID'],
            lambda d:(actualizar_usuario(d), ver_usuarios_gui(self.ids.rv))
        )
    def eliminar_usuario(self):
        solicitar_datos(
            ['UsuarioID'],
            lambda d:(eliminar_usuario(d['UsuarioID']), ver_usuarios_gui(self.ids.rv))
        )

class ClientesScreen(Screen):
    def on_enter(self): ver_clientes_gui(self.ids.rv)
    def agregar_cliente(self):
        solicitar_datos(
            ['Nombre','Telefono','Direccion'],
            lambda d:(agregar_cliente(d), ver_clientes_gui(self.ids.rv))
        )
    def actualizar_cliente(self):
        solicitar_datos(
            ['ClienteID','Nombre','Telefono','Direccion'],
            lambda d:(actualizar_cliente(d), ver_clientes_gui(self.ids.rv))
        )
    def eliminar_cliente(self):
        solicitar_datos(
            ['ClienteID'],
            lambda d:(eliminar_cliente(d['ClienteID']), ver_clientes_gui(self.ids.rv))
        )

class ProveedoresScreen(Screen):
    def on_enter(self): ver_proveedores_gui(self.ids.rv)
    def agregar_proveedor(self):
        solicitar_datos(
            ['Nombre','Telefono','Direccion'],
            lambda d:(agregar_proveedor(d), ver_proveedores_gui(self.ids.rv))
        )
    def actualizar_proveedor(self):
        solicitar_datos(
            ['ProveedorID','Nombre','Telefono','Direccion'],
            lambda d:(actualizar_proveedor(d), ver_proveedores_gui(self.ids.rv))
        )
    def eliminar_proveedor(self):
        solicitar_datos(
            ['ProveedorID'],
            lambda d:(eliminar_proveedor(d['ProveedorID']), ver_proveedores_gui(self.ids.rv))
        )

class VentasScreen(Screen):
    def on_enter(self): ver_ventas_gui(self.ids.rv)
    def nueva_venta(self):
        solicitar_datos(
            ['UsuarioID','ClienteID','Total'],
            lambda d:(nueva_venta(d), ver_ventas_gui(self.ids.rv))
        )
    def historial(self):
        historial_ventas(self.ids.rv)

class Manager(ScreenManager): pass

class SterenApp(App):
    def build(self):
        Builder.load_file(os.path.join(KV_DIR, 'manager.kv'))
        for f in os.listdir(KV_DIR):
            if f.endswith('.kv') and f != 'manager.kv':
                Builder.load_file(os.path.join(KV_DIR, f))
        sm = Manager()
        sm.current = 'login'
        return sm

if __name__ == '__main__':
    SterenApp().run()
