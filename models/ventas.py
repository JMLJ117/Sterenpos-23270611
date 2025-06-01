# ventas.py
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.recycleview import RecycleView
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty, StringProperty, ListProperty, BooleanProperty
from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox  # ✅ Importado para generar factura
from kivy.factory import Factory
from kivy.app import App

# ✅ Importa funciones desde modelos
from models.usuarios import obtener_usuarios  # Función para popup de usuarios
from models.clientes import obtener_clientes  # Función para popup de clientes
from models.ventas_helper import ver_ventas_gui, obtener_detalle_venta  # Evita ciclos de importación

from db import conectar
from utils import mostrar_popup
import datetime
from reportlab.pdfgen import canvas  # Para generar PDF
import os

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
    """Busca productos por nombre o código"""
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
        
        # ✅ Solo se inserta Subtotal, los demás son generados por la BD
        cur.execute("""
            INSERT INTO Ventas 
            (Fecha, UsuarioID, ClienteID, ModoPagoID, Subtotal) 
            VALUES (%s, %s, %s, %s, %s)
        """, (
            fecha,
            datos_venta['usuario_id'],
            datos_venta['cliente_id'] or None,
            datos_venta['modo_pago_id'],
            datos_venta['total']  # ✅ Se inserta el total calculado en Python
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

class VentasScreen(Screen):
    carrito = ListProperty([])
    usuario_seleccionado = NumericProperty(0)
    cliente_seleccionado = NumericProperty(0)
    modo_pago_seleccionado = NumericProperty(0)
    cambio = NumericProperty(0)
    factura_generada = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super(VentasScreen, self).__init__(**kwargs)
        self._buscar_popup = None
        self._popup_efectivo = None

    def dismiss_popup(self):
        """Cierra cualquier popup abierto"""
        if self._buscar_popup:
            self._buscar_popup.dismiss()
            self._buscar_popup = None

    def mostrar_popup_usuarios(self):
        """Muestra un popup para seleccionar un usuario"""
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
        """Selecciona un usuario del popup"""
        self.usuario_seleccionado = usuario['UsuarioID']
        self.ids.usuario_btn.text = usuario['Nombre']
        self.dismiss_popup()

    def mostrar_popup_clientes(self):
        """Muestra un popup para seleccionar un cliente"""
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
        """Selecciona un cliente del popup"""
        self.cliente_seleccionado = cliente['ClienteID']
        self.ids.cliente_btn.text = cliente['Nombre']
        self.dismiss_popup()

    def seleccionar_modo_pago(self, modo_pago_id):
        """Selecciona el método de pago"""
        if modo_pago_id not in [1, 2, 3]:
            mostrar_popup("Error", "Método de pago inválido")
            return
        self.modo_pago_seleccionado = modo_pago_id
        modos_pago = {1: "Efectivo", 2: "Tarjeta", 3: "Transferencia"}
        self.ids.modo_pago_btn.text = modos_pago.get(modo_pago_id, "Seleccionar Pago")
        
        if modo_pago_id == 1:  # Efectivo
            self._mostrar_popup_efectivo()

    def _mostrar_popup_efectivo(self):
        """Popup para ingresar el monto en efectivo"""
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        label = Label(text="Monto entregado por el cliente:")
        input_monto = TextInput(hint_text="Ingrese el monto", multiline=False)
        btn_aceptar = Button(text="Aceptar", size_hint=(1, 0.3))
        
        layout.add_widget(label)
        layout.add_widget(input_monto)
        layout.add_widget(btn_aceptar)
        
        self._popup_efectivo = Popup(title="Pago en Efectivo", content=layout, size_hint=(0.6, 0.4))
        btn_aceptar.bind(on_release=lambda btn: self._calcular_cambio(input_monto.text))
        self._popup_efectivo.open()

    def _calcular_cambio(self, monto_texto):
        """Calcula el cambio si el pago es en efectivo"""
        try:
            monto = float(monto_texto)
            total_venta = float(self.ids.total_label.text.split(':')[1].strip().replace('$', '').replace(',', ''))
            
            if monto < total_venta:
                raise ValueError(f"El monto es menor al total (${total_venta:.2f})")
            
            self.cambio = monto - total_venta
            self._popup_efectivo.dismiss()
            mostrar_popup("Cambio", f"El cambio es: ${self.cambio:.2f}")
        except ValueError as e:
            mostrar_popup("Error", str(e))

    def agregar_producto_por_codigo(self, codigo):
        """Agrega un producto al carrito por código o nombre"""
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
        """Busca productos por nombre o código"""
        if not texto:
            self.ids.resultados_busqueda.height = 0
            self.ids.resultados_busqueda.opacity = 0
            return
        def callback(resultados):
            if resultados:
                self.ids.resultados_rv.data = [{'text': f"{p['Nombre']} - ${p['Precio']:.2f}"} for p in resultados]
                self.ids.resultados_busqueda.height = 100
                self.ids.resultados_busqueda.opacity = 1
            else:
                self.ids.resultados_busqueda.height = 0
                self.ids.resultados_busqueda.opacity = 0
        buscar_productos(texto, callback)

    def agregar_al_carrito(self, producto):
        """Agrega un producto al carrito o incrementa su cantidad si ya está"""
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
        """Actualiza la vista del carrito y recalcula totales"""
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
        """Valida los datos y muestra un popup para generar factura"""
        if not self.usuario_seleccionado:
            mostrar_popup("Error", "Debe seleccionar un usuario")
            return
        if not self.carrito:
            mostrar_popup("Error", "El carrito está vacío")
            return
        if self.modo_pago_seleccionado == 0:
            mostrar_popup("Error", "Debe seleccionar un método de pago")
            return
    
        # ✅ CORREGIDO: Calculamos el subtotal (sin IVA) correctamente
        subtotal_venta = sum(float(p['subtotal']) for p in self.carrito)
    
        datos_venta = {
            'usuario_id': self.usuario_seleccionado,
            'cliente_id': self.cliente_seleccionado or None,
            'modo_pago_id': self.modo_pago_seleccionado,
            'subtotal': subtotal_venta  # ✅ Enviamos el subtotal, no el total
        }
    
        layout = BoxLayout(orientation='vertical', padding=10)
        chk_factura = CheckBox()
        lbl_factura = Label(text="¿Generar factura?")
        btn_aceptar = Button(text="Aceptar", size_hint_y=None, height=40)
    
        layout.add_widget(lbl_factura)
        layout.add_widget(chk_factura)
        layout.add_widget(btn_aceptar)
    
        popup = Popup(title="Finalizar Venta", content=layout, size_hint=(0.6, 0.4))
        btn_aceptar.bind(
            on_release=lambda btn: self._registrar_venta_con_factura(popup, chk_factura.active, datos_venta)
        )
        popup.open()

    def _registrar_venta_con_factura(self, popup, generar_factura, datos_venta):
        """Registra la venta y genera factura si se solicita"""
        conn = conectar()
        cur = conn.cursor()
        try:
            conn.start_transaction()
            fecha = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
            # ✅ CORREGIDO: Insertamos el subtotal correcto
            cur.execute("""
                INSERT INTO Ventas 
                (Fecha, UsuarioID, ClienteID, ModoPagoID, Subtotal) 
                VALUES (%s, %s, %s, %s, %s)
            """, (
                fecha,
                datos_venta['usuario_id'],
                datos_venta['cliente_id'] or None,
                datos_venta['modo_pago_id'],
                datos_venta['subtotal']  # ✅ Insertamos subtotal, no total
            ))
            venta_id = cur.lastrowid
        
            for producto in self.carrito:
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
        
            # Actualiza stock
            for producto in self.carrito:
                cur.execute("""
                    UPDATE Productos 
                    SET Stock = Stock - %s 
                    WHERE ProductoID = %s
                """, (producto['cantidad'], producto['producto_id']))
        
            conn.commit()
            if generar_factura:
                self._generar_factura(venta_id, datos_venta)
            self.limpiar_carrito()
            popup.dismiss()
            mostrar_popup('Éxito', 'Venta registrada correctamente')
        except Exception as e:
            conn.rollback()
            mostrar_popup('Error al registrar venta', str(e))
        finally:
            cur.close()
            conn.close()
            popup.dismiss()

    def _calcular_cambio(self, monto_texto):
        """Calcula el cambio si el pago es en efectivo"""
        try:
            monto = float(monto_texto)
            # ✅ CORREGIDO: Calculamos el total correctamente desde el subtotal
            subtotal_venta = sum(float(p['subtotal']) for p in self.carrito)
            total_venta = subtotal_venta * 1.16  # Aplicamos IVA del 16%
        
            if monto < total_venta:
                raise ValueError(f"El monto es menor al total (${total_venta:.2f})")
        
            self.cambio = monto - total_venta
            self._popup_efectivo.dismiss()
            mostrar_popup("Cambio", f"El cambio es: ${self.cambio:.2f}")
        except ValueError as e:
            mostrar_popup("Error", str(e))

    def _generar_factura(self, venta_id, datos_venta):
        """Genera una factura en PDF"""
        ruta_facturas = "facturas"
        if not os.path.exists(ruta_facturas):
            os.makedirs(ruta_facturas)
        
        ruta_pdf = os.path.join(ruta_facturas, f"venta_{venta_id}.pdf")
        c = canvas.Canvas(ruta_pdf)
        
        # Encabezado
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, 800, "SterenPOS - Factura de Venta")
        c.setFont("Helvetica", 12)
        c.drawString(50, 780, f"Venta ID: {venta_id}")
        c.drawString(50, 760, f"Fecha: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
        c.drawString(50, 740, f"Vendedor: {self.ids.usuario_btn.text}")
        c.drawString(50, 720, f"Cliente: {self.ids.cliente_btn.text}")
        c.drawString(50, 700, "Productos:")
        
        y = 680
        for p in self.carrito:
            c.drawString(70, y, f"{p['cantidad']} x {p['nombre']} - ${p['precio']:.2f} = ${p['subtotal']:.2f}")
            y -= 20
        
        # Totales
        c.setFont("Helvetica-Bold", 12)
        subtotal = float(self.ids.subtotal_label.text.split(':')[1].strip().replace('$', '').replace(',', ''))
        c.drawString(50, y-20, f"Subtotal: ${subtotal:.2f}")
        c.drawString(50, y-40, f"IVA (16%): ${subtotal * 0.16:.2f}")
        c.drawString(50, y-60, f"Total: ${subtotal * 1.16:.2f}")
        
        c.save()
        mostrar_popup("Factura Generada", f"Guardada en: {ruta_pdf}")

    def limpiar_carrito(self):
        """Vacía el carrito y reinicia totales"""
        self.carrito = []
        self.ids.carrito_rv.data = []
        self.actualizar_total()

class HistorialVentasScreen(Screen):
    def on_enter(self):
        self.cargar_historial()
    
    def cargar_historial(self):
        """Carga el historial de ventas desde la base de datos"""
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
            self.ids.rv_ventas.data = [{
                'text': (
                    f"ID: {v['VentaID']}  |  "
                    f"Fecha: {v['Fecha']}  |  "
                    f"Vendedor: {v['Vendedor']}  |  "
                    f"Cliente: {v['Cliente']}  |  "
                    f"Total: ${v['Total']:.2f}"
                ),
                'venta_id': v['VentaID']
            } for v in ventas]
        except Exception as e:
            mostrar_popup('Error al listar ventas', str(e))
        finally:
            cur.close()
            conn.close()

    def mostrar_detalle_venta(self, venta_id):
        """Muestra el detalle de una venta seleccionada"""
        def callback(detalles, info_venta):
            layout = BoxLayout(orientation='vertical', padding=10)
            scroll = ScrollView()
            contenido = BoxLayout(orientation='vertical', size_hint_y=None)
            contenido.bind(minimum_height=contenido.setter('height'))
            
            contenido.add_widget(Label(text=f"Venta ID: {venta_id}", bold=True))
            contenido.add_widget(Label(text=f"Fecha: {info_venta['Fecha']}"))
            contenido.add_widget(Label(text=f"Vendedor: {info_venta['Vendedor']}"))
            contenido.add_widget(Label(text=f"Cliente: {info_venta['Cliente']}"))
            contenido.add_widget(Label(text=f"Método de pago: {info_venta['MetodoPago']}"))
            contenido.add_widget(Label(text=f"Total: ${info_venta['Total']:.2f}"))
            contenido.add_widget(Label(text=f"Factura: {'Sí' if info_venta['FacturaGenerada'] else 'No'}"))
            
            contenido.add_widget(Label(text="Detalles:", font_size='16sp', bold=True))
            for detalle in detalles:
                contenido.add_widget(Label(
                    text=f"{detalle['Cantidad']} x {detalle['Producto']} - ${detalle['PrecioUnitario']:.2f} = ${detalle['Subtotal']:.2f}"
                ))
            
            scroll.add_widget(contenido)
            layout.add_widget(scroll)
            btn_regresar = Button(text="Regresar", size_hint_y=None, height=40)
            layout.add_widget(btn_regresar)
            popup = Popup(title=f"Detalle de Venta #{venta_id}", content=layout, size_hint=(0.9, 0.9))
            btn_regresar.bind(on_release=popup.dismiss)
            popup.open()
        
        obtener_detalle_venta(venta_id, callback)

Factory.register('VentasScreen', module='ventas')

class VentaHistorialItem(RecycleDataViewBehavior, Button):
    """Item clickeable para el historial de ventas"""
    index = NumericProperty(0)
    venta_id = NumericProperty(0)
    
    def refresh_view_attrs(self, rv, index, data):
        """Actualiza los atributos del item"""
        self.index = index
        self.venta_id = data.get('venta_id', 0)
        return super(VentaHistorialItem, self).refresh_view_attrs(rv, index, data)
    
    def on_release(self):
        """Se ejecuta cuando se hace clic en el item"""
        if self.venta_id > 0:
            # Obtener la pantalla del historial y llamar al método de detalle
            historial_screen = App.get_running_app().root.get_screen('historial_ventas')
            historial_screen.mostrar_detalle_venta(self.venta_id)

# Método actualizado para cargar historial con más información
def cargar_historial(self):
    """Carga el historial de ventas desde la base de datos"""
    conn = conectar()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("""
            SELECT 
                v.VentaID,
                DATE_FORMAT(v.Fecha, '%Y-%m-%d %H:%i') AS Fecha,
                u.Nombre AS Vendedor,
                COALESCE(c.Nombre, 'Sin cliente') AS Cliente,
                mp.Tipo AS MetodoPago,
                v.Subtotal,
                v.IVA,
                v.Total
            FROM Ventas v
            JOIN Usuarios u ON v.UsuarioID = u.UsuarioID
            LEFT JOIN Clientes c ON v.ClienteID = c.ClienteID
            JOIN ModoPago mp ON v.ModoPagoID = mp.ModoPagoID
            ORDER BY v.Fecha DESC
            LIMIT 100
        """)
        ventas = cur.fetchall()
        
        # Formatear datos para el RecycleView
        self.ids.rv_ventas.data = [{
            'text': (
                f"#{v['VentaID']} | {v['Fecha']} | {v['Vendedor']} | "
                f"{v['Cliente']} | {v['MetodoPago']} | ${v['Total']:.2f}"
            ),
            'venta_id': v['VentaID']
        } for v in ventas]
        
    except Exception as e:
        mostrar_popup('Error al cargar historial', str(e))
    finally:
        cur.close()
        conn.close()

# Método mejorado para mostrar detalle de venta
def mostrar_detalle_venta(self, venta_id):
    """Muestra el detalle completo de una venta seleccionada"""
    conn = conectar()
    cur = conn.cursor(dictionary=True)
    try:
        # Obtener información general de la venta
        cur.execute("""
            SELECT 
                v.VentaID,
                DATE_FORMAT(v.Fecha, '%Y-%m-%d %H:%i:%s') AS Fecha,
                u.Nombre AS Vendedor,
                COALESCE(c.Nombre, 'Cliente general') AS Cliente,
                COALESCE(c.RFC, 'N/A') AS ClienteRFC,
                COALESCE(c.Telefono, 'N/A') AS ClienteTelefono,
                mp.Tipo AS MetodoPago,
                v.Subtotal,
                v.IVA,
                v.Total,
                v.Devolucion
            FROM Ventas v
            JOIN Usuarios u ON v.UsuarioID = u.UsuarioID
            LEFT JOIN Clientes c ON v.ClienteID = c.ClienteID
            JOIN ModoPago mp ON v.ModoPagoID = mp.ModoPagoID
            WHERE v.VentaID = %s
        """, (venta_id,))
        
        info_venta = cur.fetchone()
        if not info_venta:
            mostrar_popup("Error", "No se encontró la venta")
            return
        
        # Obtener detalles de productos
        cur.execute("""
            SELECT 
                p.Nombre AS Producto,
                p.Codigo,
                dv.Cantidad,
                dv.PrecioUnitario,
                dv.Subtotal,
                cat.Nombre AS Categoria,
                m.Nombre AS Marca
            FROM DetalleVenta dv
            JOIN Productos p ON dv.ProductoID = p.ProductoID
            JOIN Categorias cat ON p.CategoriaID = cat.CategoriaID
            JOIN Marcas m ON p.MarcaID = m.MarcaID
            WHERE dv.VentaID = %s
            ORDER BY p.Nombre
        """, (venta_id,))
        
        detalles = cur.fetchall()
        
        # Verificar si hubo cambio (solo para efectivo)
        cambio_info = ""
        if info_venta['MetodoPago'] == 'Efectivo':
            # Aquí podrías agregar lógica para obtener el cambio si lo guardas en BD
            cambio_info = "Cambio: Consultar con vendedor"
        
        # Crear el popup con toda la información
        self._crear_popup_detalle(info_venta, detalles, cambio_info)
        
    except Exception as e:
        mostrar_popup('Error al obtener detalle', str(e))
    finally:
        cur.close()
        conn.close()

def _crear_popup_detalle(self, info_venta, detalles, cambio_info):
    """Crea el popup con el detalle completo de la venta"""
    # Layout principal
    main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
    
    # ScrollView para el contenido
    scroll = ScrollView()
    content_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=5)
    content_layout.bind(minimum_height=content_layout.setter('height'))
    
    # Información general de la venta
    content_layout.add_widget(Label(
        text=f"DETALLE DE VENTA #{info_venta['VentaID']}", 
        font_size='18sp', 
        bold=True,
        size_hint_y=None, 
        height=40
    ))
    
    content_layout.add_widget(Label(
        text=f"Fecha: {info_venta['Fecha']}", 
        size_hint_y=None, 
        height=30
    ))
    
    content_layout.add_widget(Label(
        text=f"Vendedor: {info_venta['Vendedor']}", 
        size_hint_y=None, 
        height=30
    ))
    
    content_layout.add_widget(Label(
        text=f"Cliente: {info_venta['Cliente']}", 
        size_hint_y=None, 
        height=30
    ))
    
    if info_venta['ClienteRFC'] != 'N/A':
        content_layout.add_widget(Label(
            text=f"RFC: {info_venta['ClienteRFC']}", 
            size_hint_y=None, 
            height=30
        ))
    
    if info_venta['ClienteTelefono'] != 'N/A':
        content_layout.add_widget(Label(
            text=f"Teléfono: {info_venta['ClienteTelefono']}", 
            size_hint_y=None, 
            height=30
        ))
    
    content_layout.add_widget(Label(
        text=f"Método de pago: {info_venta['MetodoPago']}", 
        size_hint_y=None, 
        height=30
    ))
    
    if cambio_info:
        content_layout.add_widget(Label(
            text=cambio_info, 
            size_hint_y=None, 
            height=30
        ))
    
    # Separador
    content_layout.add_widget(Label(
        text="─" * 50, 
        size_hint_y=None, 
        height=20
    ))
    
    # Título de productos
    content_layout.add_widget(Label(
        text="PRODUCTOS VENDIDOS:", 
        font_size='16sp', 
        bold=True,
        size_hint_y=None, 
        height=35
    ))
    
    # Lista de productos
    for detalle in detalles:
        # Información del producto
        content_layout.add_widget(Label(
            text=f"• {detalle['Producto']} ({detalle['Codigo']})", 
            size_hint_y=None, 
            height=25,
            text_size=(None, None),
            halign='left'
        ))
        
        content_layout.add_widget(Label(
            text=f"  Marca: {detalle['Marca']} | Categoría: {detalle['Categoria']}", 
            size_hint_y=None, 
            height=20,
            color=(0.7, 0.7, 0.7, 1)
        ))
        
        content_layout.add_widget(Label(
            text=f"  Cantidad: {detalle['Cantidad']} | Precio: ${detalle['PrecioUnitario']:.2f} | Subtotal: ${detalle['Subtotal']:.2f}", 
            size_hint_y=None, 
            height=25
        ))
        
        # Separador pequeño
        content_layout.add_widget(Label(
            text="", 
            size_hint_y=None, 
            height=10
        ))
    
    # Separador
    content_layout.add_widget(Label(
        text="─" * 50, 
        size_hint_y=None, 
        height=20
    ))
    
    # Totales
    content_layout.add_widget(Label(
        text="RESUMEN DE TOTALES:", 
        font_size='16sp', 
        bold=True,
        size_hint_y=None, 
        height=35
    ))
    
    content_layout.add_widget(Label(
        text=f"Subtotal: ${info_venta['Subtotal']:.2f}", 
        size_hint_y=None, 
        height=30
    ))
    
    content_layout.add_widget(Label(
        text=f"IVA (16%): ${info_venta['IVA']:.2f}", 
        size_hint_y=None, 
        height=30
    ))
    
    content_layout.add_widget(Label(
        text=f"TOTAL: ${info_venta['Total']:.2f}", 
        font_size='16sp',
        bold=True,
        size_hint_y=None, 
        height=35
    ))
    
    if info_venta['Devolucion']:
        content_layout.add_widget(Label(
            text="⚠️ VENTA CON DEVOLUCIÓN", 
            color=(1, 0.5, 0, 1),
            size_hint_y=None, 
            height=30
        ))
    
    # Agregar contenido al scroll
    scroll.add_widget(content_layout)
    main_layout.add_widget(scroll)
    
    # Botones
    btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
    
    btn_cerrar = Button(text="Cerrar")
    btn_reimprimir = Button(text="Reimprimir Factura")
    
    btn_layout.add_widget(btn_reimprimir)
    btn_layout.add_widget(btn_cerrar)
    main_layout.add_widget(btn_layout)
    
    # Crear popup
    popup = Popup(
        title=f"Detalle Venta #{info_venta['VentaID']}", 
        content=main_layout, 
        size_hint=(0.95, 0.9)
    )
    
    # Conectar eventos
    btn_cerrar.bind(on_release=popup.dismiss)
    btn_reimprimir.bind(on_release=lambda x: self._reimprimir_factura(info_venta['VentaID']))
    
    popup.open()

def _reimprimir_factura(self, venta_id):
    """Reimprime la factura de una venta"""
    try:
        # Aquí puedes agregar la lógica para reimprimir
        ruta_factura = f"facturas/venta_{venta_id}.pdf"
        if os.path.exists(ruta_factura):
            mostrar_popup("Factura", f"Factura encontrada en: {ruta_factura}")
            # Aquí podrías abrir el archivo PDF o enviarlo a imprimir
        else:
            mostrar_popup("Aviso", "No se encontró la factura original. ¿Desea generar una nueva?")
    except Exception as e:
        mostrar_popup("Error", f"Error al buscar factura: {str(e)}")

# Agregar al final del archivo, justo antes de Factory.register
Factory.register('VentaHistorialItem', VentaHistorialItem)

class HistorialVentasScreen(Screen):
    def on_enter(self):
        """Se ejecuta cada vez que se entra a la pantalla"""
        self.cargar_historial()
    
    def cargar_historial(self):
        """Carga el historial de ventas desde la base de datos"""
        conn = conectar()
        cur = conn.cursor(dictionary=True)
        try:
            cur.execute("""
                SELECT 
                    v.VentaID,
                    DATE_FORMAT(v.Fecha, '%Y-%m-%d %H:%i') AS Fecha,
                    u.Nombre AS Vendedor,
                    COALESCE(c.Nombre, 'Sin cliente') AS Cliente,
                    mp.Tipo AS MetodoPago,
                    v.Subtotal,
                    v.IVA,
                    v.Total
                FROM Ventas v
                JOIN Usuarios u ON v.UsuarioID = u.UsuarioID
                LEFT JOIN Clientes c ON v.ClienteID = c.ClienteID
                JOIN ModoPago mp ON v.ModoPagoID = mp.ModoPagoID
                ORDER BY v.Fecha DESC
                LIMIT 100
            """)
            ventas = cur.fetchall()
            
            # Formatear datos para el RecycleView
            self.ids.rv_ventas.data = [{
                'text': (
                    f"#{v['VentaID']} | {v['Fecha']} | {v['Vendedor']} | "
                    f"{v['Cliente']} | {v['MetodoPago']} | ${v['Total']:.2f}"
                ),
                'venta_id': v['VentaID']
            } for v in ventas]
            
        except Exception as e:
            mostrar_popup('Error al cargar historial', str(e))
        finally:
            cur.close()
            conn.close()

    def mostrar_detalle_venta(self, venta_id):
        """Muestra el detalle completo de una venta seleccionada"""
        conn = conectar()
        cur = conn.cursor(dictionary=True)
        try:
            # Obtener información general de la venta
            cur.execute("""
                SELECT 
                    v.VentaID,
                    DATE_FORMAT(v.Fecha, '%Y-%m-%d %H:%i:%s') AS Fecha,
                    u.Nombre AS Vendedor,
                    COALESCE(c.Nombre, 'Cliente general') AS Cliente,
                    COALESCE(c.RFC, 'N/A') AS ClienteRFC,
                    COALESCE(c.Telefono, 'N/A') AS ClienteTelefono,
                    mp.Tipo AS MetodoPago,
                    v.Subtotal,
                    v.IVA,
                    v.Total,
                    v.Devolucion
                FROM Ventas v
                JOIN Usuarios u ON v.UsuarioID = u.UsuarioID
                LEFT JOIN Clientes c ON v.ClienteID = c.ClienteID
                JOIN ModoPago mp ON v.ModoPagoID = mp.ModoPagoID
                WHERE v.VentaID = %s
            """, (venta_id,))
            
            info_venta = cur.fetchone()
            if not info_venta:
                mostrar_popup("Error", "No se encontró la venta")
                return
            
            # Obtener detalles de productos
            cur.execute("""
                SELECT 
                    p.Nombre AS Producto,
                    p.Codigo,
                    dv.Cantidad,
                    dv.PrecioUnitario,
                    dv.Subtotal,
                    cat.Nombre AS Categoria,
                    m.Nombre AS Marca
                FROM DetalleVenta dv
                JOIN Productos p ON dv.ProductoID = p.ProductoID
                JOIN Categorias cat ON p.CategoriaID = cat.CategoriaID
                JOIN Marcas m ON p.MarcaID = m.MarcaID
                WHERE dv.VentaID = %s
                ORDER BY p.Nombre
            """, (venta_id,))
            
            detalles = cur.fetchall()
            
            # Verificar si hubo cambio (solo para efectivo)
            cambio_info = ""
            if info_venta['MetodoPago'] == 'Efectivo':
                cambio_info = "Cambio: Consultar con vendedor"
            
            # Crear el popup con toda la información
            self._crear_popup_detalle(info_venta, detalles, cambio_info)
            
        except Exception as e:
            mostrar_popup('Error al obtener detalle', str(e))
        finally:
            cur.close()
            conn.close()

    def _crear_popup_detalle(self, info_venta, detalles, cambio_info):
        """Crea el popup con el detalle completo de la venta"""
        # Layout principal
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # ScrollView para el contenido
        scroll = ScrollView()
        content_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=5)
        content_layout.bind(minimum_height=content_layout.setter('height'))
        
        # Información general de la venta
        content_layout.add_widget(Label(
            text=f"DETALLE DE VENTA #{info_venta['VentaID']}", 
            font_size='18sp', 
            bold=True,
            size_hint_y=None, 
            height=40
        ))
        
        content_layout.add_widget(Label(
            text=f"Fecha: {info_venta['Fecha']}", 
            size_hint_y=None, 
            height=30
        ))
        
        content_layout.add_widget(Label(
            text=f"Vendedor: {info_venta['Vendedor']}", 
            size_hint_y=None, 
            height=30
        ))
        
        content_layout.add_widget(Label(
            text=f"Cliente: {info_venta['Cliente']}", 
            size_hint_y=None, 
            height=30
        ))
        
        if info_venta['ClienteRFC'] != 'N/A':
            content_layout.add_widget(Label(
                text=f"RFC: {info_venta['ClienteRFC']}", 
                size_hint_y=None, 
                height=30
            ))
        
        if info_venta['ClienteTelefono'] != 'N/A':
            content_layout.add_widget(Label(
                text=f"Teléfono: {info_venta['ClienteTelefono']}", 
                size_hint_y=None, 
                height=30
            ))
        
        content_layout.add_widget(Label(
            text=f"Método de pago: {info_venta['MetodoPago']}", 
            size_hint_y=None, 
            height=30
        ))
        
        if cambio_info:
            content_layout.add_widget(Label(
                text=cambio_info, 
                size_hint_y=None, 
                height=30
            ))
        
        # Separador
        content_layout.add_widget(Label(
            text="─" * 50, 
            size_hint_y=None, 
            height=20
        ))
        
        # Título de productos
        content_layout.add_widget(Label(
            text="PRODUCTOS VENDIDOS:", 
            font_size='16sp', 
            bold=True,
            size_hint_y=None, 
            height=35
        ))
        
        # Lista de productos
        for detalle in detalles:
            # Información del producto
            content_layout.add_widget(Label(
                text=f"• {detalle['Producto']} ({detalle['Codigo']})", 
                size_hint_y=None, 
                height=25,
                text_size=(None, None),
                halign='left'
            ))
            
            content_layout.add_widget(Label(
                text=f"  Marca: {detalle['Marca']} | Categoría: {detalle['Categoria']}", 
                size_hint_y=None, 
                height=20,
                color=(0.7, 0.7, 0.7, 1)
            ))
            
            content_layout.add_widget(Label(
                text=f"  Cantidad: {detalle['Cantidad']} | Precio: ${detalle['PrecioUnitario']:.2f} | Subtotal: ${detalle['Subtotal']:.2f}", 
                size_hint_y=None, 
                height=25
            ))
            
            # Separador pequeño
            content_layout.add_widget(Label(
                text="", 
                size_hint_y=None, 
                height=10
            ))
        
        # Separador
        content_layout.add_widget(Label(
            text="─" * 50, 
            size_hint_y=None, 
            height=20
        ))
        
        # Totales
        content_layout.add_widget(Label(
            text="RESUMEN DE TOTALES:", 
            font_size='16sp', 
            bold=True,
            size_hint_y=None, 
            height=35
        ))
        
        content_layout.add_widget(Label(
            text=f"Subtotal: ${info_venta['Subtotal']:.2f}", 
            size_hint_y=None, 
            height=30
        ))
        
        content_layout.add_widget(Label(
            text=f"IVA (16%): ${info_venta['IVA']:.2f}", 
            size_hint_y=None, 
            height=30
        ))
        
        content_layout.add_widget(Label(
            text=f"TOTAL: ${info_venta['Total']:.2f}", 
            font_size='16sp',
            bold=True,
            size_hint_y=None, 
            height=35
        ))
        
        if info_venta['Devolucion']:
            content_layout.add_widget(Label(
                text="⚠️ VENTA CON DEVOLUCIÓN", 
                color=(1, 0.5, 0, 1),
                size_hint_y=None, 
                height=30
            ))
        
        # Agregar contenido al scroll
        scroll.add_widget(content_layout)
        main_layout.add_widget(scroll)
        
        # Botones
        btn_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        
        btn_cerrar = Button(text="Cerrar")
        btn_reimprimir = Button(text="Reimprimir Factura")
        
        btn_layout.add_widget(btn_reimprimir)
        btn_layout.add_widget(btn_cerrar)
        main_layout.add_widget(btn_layout)
        
        # Crear popup
        popup = Popup(
            title=f"Detalle Venta #{info_venta['VentaID']}", 
            content=main_layout, 
            size_hint=(0.95, 0.9)
        )
        
        # Conectar eventos
        btn_cerrar.bind(on_release=popup.dismiss)
        btn_reimprimir.bind(on_release=lambda x: self._reimprimir_factura(info_venta['VentaID']))
        
        popup.open()

    def _reimprimir_factura(self, venta_id):
        """Reimprime la factura de una venta"""
        try:
            ruta_factura = f"facturas/venta_{venta_id}.pdf"
            if os.path.exists(ruta_factura):
                mostrar_popup("Factura", f"Factura encontrada en: {ruta_factura}")
                # Aquí podrías abrir el archivo PDF o enviarlo a imprimir
            else:
                mostrar_popup("Aviso", "No se encontró la factura original. ¿Desea generar una nueva?")
        except Exception as e:
            mostrar_popup("Error", f"Error al buscar factura: {str(e)}")