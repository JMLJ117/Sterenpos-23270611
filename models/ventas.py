# ventas.py
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.recycleview import RecycleView
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty, StringProperty, ListProperty
from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.factory import Factory
from kivy.app import App

from db import conectar
from utils import mostrar_popup
import datetime

class ProductoCarrito(RecycleDataViewBehavior, BoxLayout):
    index = NumericProperty(0)
    producto_id = NumericProperty(0)
    nombre = StringProperty('')
    precio = NumericProperty(0)
    cantidad = NumericProperty(1)
    subtotal = NumericProperty(0)
    
    def actualizar_cantidad(self, nueva_cantidad):
        try:
            nueva_cantidad = int(nueva_cantidad)
            if nueva_cantidad <= 0:
                raise ValueError("La cantidad debe ser mayor a 0")
            self.cantidad = nueva_cantidad
            self.subtotal = self.precio * self.cantidad
            App.get_running_app().root.get_screen('ventas').actualizar_total()
        except ValueError as e:
            mostrar_popup("Error", str(e))

def buscar_productos(query, callback):
    conn = conectar()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("""
            SELECT ProductoID, Nombre, Precio 
            FROM Productos 
            WHERE Activo = 1 AND 
            (Nombre LIKE %s OR Codigo LIKE %s)
            LIMIT 10
        """, (f"%{query}%", f"%{query}%"))
        resultados = cur.fetchall()
        callback(resultados)
    except Exception as e:
        mostrar_popup('Error en búsqueda', str(e))
    finally:
        cur.close()
        conn.close()

def registrar_venta(datos_venta, productos):
    conn = conectar()
    cur = conn.cursor()
    try:
        conn.start_transaction()
        fecha = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cur.execute("""
            INSERT INTO Ventas 
            (Fecha, UsuarioID, ClienteID, ModoPagoID, Subtotal) 
            VALUES (%s, %s, %s, %s, %s)
        """, (
            fecha,
            datos_venta['usuario_id'],
            datos_venta['cliente_id'] or None,
            datos_venta['modo_pago_id'],
            float(datos_venta['subtotal'])
        ))
        venta_id = cur.lastrowid
        
        for producto in productos:
            cur.execute("""
                INSERT INTO DetalleVenta 
                (VentaID, ProductoID, Cantidad, PrecioUnitario) 
                VALUES (%s, %s, %s, %s)
            """, (
                venta_id,
                producto['producto_id'],
                producto['cantidad'],
                float(producto['precio'])
            ))
        
        conn.commit()
        mostrar_popup('Éxito', 'Venta registrada correctamente')
        return True
    except Exception as e:
        conn.rollback()
        mostrar_popup('Error al registrar venta', str(e))
        return False
    finally:
        cur.close()
        conn.close()

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
            FROM Ventas v
            JOIN Usuarios u ON v.UsuarioID = u.UsuarioID
            JOIN Clientes c ON v.ClienteID = c.ClienteID
            ORDER BY v.Fecha DESC
        """)
        rv.data = [{
            'text': (
                f"ID: {row['VentaID']}  |  "
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

def obtener_usuarios(callback):
    conn = conectar()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("SELECT UsuarioID, Nombre FROM Usuarios")
        callback(cur.fetchall())
    finally:
        cur.close()
        conn.close()

def obtener_clientes(callback):
    conn = conectar()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("SELECT ClienteID, Nombre FROM Clientes")
        callback(cur.fetchall())
    finally:
        cur.close()
        conn.close()

class VentasScreen(Screen):
    carrito = ListProperty([])
    usuario_seleccionado = NumericProperty(0)
    cliente_seleccionado = NumericProperty(0)
    modo_pago_seleccionado = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super(VentasScreen, self).__init__(**kwargs)
        self._buscar_popup = None

    def dismiss_popup(self):
        if self._buscar_popup:
            self._buscar_popup.dismiss()
            self._buscar_popup = None

    def mostrar_popup_usuarios(self):
        def callback_usuarios(usuarios):
            if not usuarios:
                mostrar_popup("Error", "No hay usuarios disponibles")
                return
            popup = Popup(title="Seleccionar Usuario", size_hint=(0.8, 0.6))
            scroll = ScrollView()
            layout = BoxLayout(orientation='vertical', spacing=5, padding=10)
            for usuario in usuarios:
                btn = Button(text=usuario['Nombre'], 
                            on_release=lambda b, u=usuario: self.seleccionar_usuario(u))
                layout.add_widget(btn)
            scroll.add_widget(layout)
            popup.content = scroll
            popup.open()
        obtener_usuarios(callback_usuarios)

    def seleccionar_usuario(self, usuario):
        self.usuario_seleccionado = usuario['UsuarioID']
        self.ids.usuario_btn.text = usuario['Nombre']
        self.dismiss_popup()

    def mostrar_popup_clientes(self):
        def callback_clientes(clientes):
            if not clientes:
                mostrar_popup("Error", "No hay clientes registrados")
                return
            popup = Popup(title="Seleccionar Cliente", size_hint=(0.8, 0.6))
            scroll = ScrollView()
            layout = BoxLayout(orientation='vertical', spacing=5, padding=10)
            for cliente in clientes:
                btn = Button(text=cliente['Nombre'], 
                            on_release=lambda b, c=cliente: self.seleccionar_cliente(c))
                layout.add_widget(btn)
            scroll.add_widget(layout)
            popup.content = scroll
            popup.open()
        obtener_clientes(callback_clientes)

    def seleccionar_cliente(self, cliente):
        self.cliente_seleccionado = cliente['ClienteID']
        self.ids.cliente_btn.text = cliente['Nombre']
        self.dismiss_popup()

    def seleccionar_modo_pago(self, modo_pago_id):
        if modo_pago_id not in [1, 2, 3]:
            mostrar_popup("Error", "Método de pago inválido")
            return
        self.modo_pago_seleccionado = modo_pago_id
        modos_pago = {1: "Efectivo", 2: "Tarjeta", 3: "Transferencia"}
        self.ids.modo_pago_btn.text = modos_pago.get(modo_pago_id, "Seleccionar Pago")

    def agregar_producto_por_codigo(self, codigo):
        conn = conectar()
        cur = conn.cursor(dictionary=True)
        try:
            cur.execute("""
                SELECT ProductoID, Nombre, Precio 
                FROM Productos 
                WHERE Activo = 1 AND (Codigo = %s OR Nombre LIKE %s)
                LIMIT 1
            """, (codigo, f"%{codigo}%"))
            producto = cur.fetchone()
            if producto:
                self.agregar_al_carrito(producto)
                self.ids.codigo_input.text = ""
            else:
                mostrar_popup("Producto no encontrado", "No se encontró ningún producto")
        finally:
            cur.close()
            conn.close()

    def buscar_productos(self, texto):
        if not texto:
            self.ids.resultados_busqueda.height = 0
            self.ids.resultados_busqueda.opacity = 0
            return
        def callback(resultados):
            if resultados:
                self.ids.resultados_rv.data = [{'text': f"{p['Nombre']} - ${p['Precio']:.2f}"} 
                                              for p in resultados]
                self.ids.resultados_busqueda.height = 100
                self.ids.resultados_busqueda.opacity = 1
            else:
                self.ids.resultados_busqueda.height = 0
                self.ids.resultados_busqueda.opacity = 0
        buscar_productos(texto, callback)

    def agregar_al_carrito(self, producto):
        for item in self.carrito:
            if item['producto_id'] == producto['ProductoID']:
                item['cantidad'] += 1
                item['subtotal'] = item['precio'] * item['cantidad']
                break
        else:
            self.carrito.append({
                'producto_id': producto['ProductoID'],
                'nombre': producto['Nombre'],
                'precio': float(producto['Precio']),
                'cantidad': 1,
                'subtotal': float(producto['Precio'])
            })
        self.actualizar_carrito()

    def actualizar_carrito(self):
        self.ids.carrito_rv.data = [{
            'text': f"{p['nombre']} - ${p['precio']:.2f} x {p['cantidad']} = ${p['subtotal']:.2f}"
        } for p in self.carrito]
        self.actualizar_total()

    def actualizar_total(self):
        subtotal = sum(float(p['subtotal']) for p in self.carrito)
        iva = subtotal * 0.16
        total = subtotal + iva
        self.ids.subtotal_label.text = f"Subtotal: ${subtotal:.2f}"
        self.ids.iva_label.text = f"IVA (16%): ${iva:.2f}"
        self.ids.total_label.text = f"Total: ${total:.2f}"

    def finalizar_venta(self):
        if not self.usuario_seleccionado:
            mostrar_popup("Error", "Debe seleccionar un usuario")
            return
        if not self.carrito:
            mostrar_popup("Error", "El carrito está vacío")
            return
        if self.modo_pago_seleccionado == 0:
            mostrar_popup("Error", "Debe seleccionar un método de pago")
            return
            
        datos_venta = {
            'usuario_id': self.usuario_seleccionado,
            'cliente_id': self.cliente_seleccionado or None,
            'modo_pago_id': self.modo_pago_seleccionado,
            'subtotal': float(self.ids.subtotal_label.text.split('$')[1]),
        }
        if registrar_venta(datos_venta, self.carrito):
            self.limpiar_carrito()

    def limpiar_carrito(self):
        self.carrito = []
        self.ids.carrito_rv.data = []
        self.actualizar_total()

class HistorialVentasScreen(Screen):
    def on_enter(self):
        ver_ventas_gui(self.ids.rv_ventas)

Factory.register('VentasScreen', module='ventas')
Factory.register('HistorialVentasScreen', module='ventas')