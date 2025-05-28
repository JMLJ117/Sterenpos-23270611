from controllers.detalles_ventas_controllers import DetallesVentasController
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QSpinBox, QLineEdit, QLabel
)
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon
import cv2
from pyzbar.pyzbar import decode

class VentanaDetallesVentas(QWidget):
    detalle_modificado = pyqtSignal() 
    
    def __init__(self, id_venta=None):
        super().__init__()
        self.controller = DetallesVentasController()
        self.id_venta = id_venta
        self.setWindowTitle(f"Detalles de Venta #{self.id_venta if id_venta else 'Nueva'}")
        self.resize(800, 500)
        self.setWindowIcon(QIcon("icons/details.png"))
        
        if self.id_venta is None:
            self.id_venta = self.controller.obtener_ultima_venta()
            self.setWindowTitle(f"Detalles de Venta #{self.id_venta}")
        
        self.init_ui()
        self.cargar_datos()
    
    def init_ui(self):
        layout = QVBoxLayout()

        # Tabla de detalles
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels([
            "ID Venta", "Artículo", "Precio Unitario", "Cantidad", "Subtotal"
        ])
        self.tabla.setColumnWidth(1, 250)
        layout.addWidget(self.tabla)

        # Formulario para agregar artículos
        form_layout = QHBoxLayout()

        self.input_codigo = QLineEdit()
        self.input_codigo.setPlaceholderText("Código o nombre del artículo")
        self.input_codigo.returnPressed.connect(self.buscar_articulo_por_codigo)
        form_layout.addWidget(self.input_codigo)

        self.spin_cantidad = QSpinBox()
        self.spin_cantidad.setRange(1, 999)
        self.spin_cantidad.setValue(1)
        form_layout.addWidget(QLabel("Cantidad:"))
        form_layout.addWidget(self.spin_cantidad)

        btn_estilo = """
        QPushButton {
            background-color: #27ae60;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 5px 10px;
            min-width: 80px;
        }
        QPushButton:hover {
            background-color: #2ecc71;
        }
        QPushButton:pressed {
            background-color: #219653;
        }
        """

        btn_escanear = QPushButton("Escanear")
        btn_escanear.setStyleSheet(btn_estilo)
        btn_escanear.clicked.connect(self.escanear_y_agregar)
        form_layout.addWidget(btn_escanear)

        btn_eliminar = QPushButton("Eliminar")
        btn_eliminar.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 5px 10px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        btn_eliminar.clicked.connect(self.eliminar_detalle)
        form_layout.addWidget(btn_eliminar)

        layout.addLayout(form_layout)
        self.setLayout(layout)
    
    def cargar_datos(self):
        if not self.id_venta:
            return

        try:
            detalles = self.controller.obtener_detalles_venta(self.id_venta)
            self.tabla.setRowCount(0)
            
            for fila, detalle in enumerate(detalles):
                self.tabla.insertRow(fila)
                self.tabla.setItem(fila, 0, QTableWidgetItem(str(detalle["id_ventas"])))
                self.tabla.setItem(fila, 1, QTableWidgetItem(detalle["nombre_articulo"]))
                self.tabla.setItem(fila, 2, QTableWidgetItem(f"${detalle['precio_articulo']:.2f}"))
                self.tabla.setItem(fila, 3, QTableWidgetItem(str(detalle["cantidad"])))
                self.tabla.setItem(fila, 4, QTableWidgetItem(f"${detalle['subtotal']:.2f}"))

            # Calcular y mostrar total
            total = self.controller.obtener_total_venta(self.id_venta)
            
            self.tabla.insertRow(self.tabla.rowCount())
            fila_total = self.tabla.rowCount() - 1
            self.tabla.setItem(fila_total, 3, QTableWidgetItem("TOTAL:"))
            self.tabla.setItem(fila_total, 4, QTableWidgetItem(f"${total:.2f}"))
            self.tabla.item(fila_total, 4).setBackground(Qt.GlobalColor.lightGray)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar los detalles: {e}")
    
    def buscar_articulo_por_codigo(self):
        entrada = self.input_codigo.text().strip()
        cantidad = self.spin_cantidad.value()

        if not entrada:
            QMessageBox.warning(self, "Advertencia", "Ingrese un código o nombre de artículo")
            return

        try:
            articulo = self.controller.buscar_articulo(entrada)
            
            if not articulo:
                QMessageBox.warning(self, "No encontrado", "Artículo no encontrado o no activo")
                return

            if not self.id_venta:
                QMessageBox.critical(self, "Error", "No hay una venta asociada")
                return

            # Agregar artículo a la venta
            subtotal = cantidad * articulo["precio_articulo"]
            self.controller.agregar_articulo(self.id_venta, articulo["codigo_articulo"], cantidad, subtotal)
            
            self.cargar_datos()
            QTimer.singleShot(100, self.controller.detalle_modificado.emit)
            
            QMessageBox.information(self, "Éxito", "Artículo agregado a la venta")
            self.input_codigo.clear()
            self.spin_cantidad.setValue(1)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al procesar artículo: {e}")
    
    def escanear_y_agregar(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            QMessageBox.critical(self, "Error", "No se pudo acceder a la cámara")
            return

        QMessageBox.information(self, "Escaneo", "Apunte el código de barras a la cámara.\nPresione 'Q' para salir.")
        
        codigo_encontrado = None

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                codigos = decode(frame)
                for codigo in codigos:
                    data = codigo.data.decode('utf-8')
                    codigo_encontrado = data
                    break

                cv2.imshow("Escaneo de código", frame)
                
                if codigo_encontrado or cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        finally:
            cap.release()
            cv2.destroyAllWindows()

        if codigo_encontrado:
            self.input_codigo.setText(codigo_encontrado)
            self.buscar_articulo_por_codigo()
    
    def eliminar_detalle(self):
        fila = self.tabla.currentRow()
        if fila < 0 or fila >= self.tabla.rowCount() - 1:
            QMessageBox.warning(self, "Advertencia", "Seleccione un artículo para eliminar")
            return

        nombre_articulo = self.tabla.item(fila, 1).text()

        try:
            articulo = self.controller.buscar_articulo(nombre_articulo)
            
            if not articulo:
                QMessageBox.warning(self, "Error", "No se pudo identificar el artículo")
                return

            respuesta = QMessageBox.question(
                self, "Confirmar",
                f"¿Eliminar '{nombre_articulo}' de la venta?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if respuesta == QMessageBox.StandardButton.Yes:
                self.controller.eliminar_articulo(self.id_venta, articulo["codigo_articulo"])
                self.cargar_datos()
                QTimer.singleShot(100, self.controller.detalle_modificado.emit)
                QMessageBox.information(self, "Éxito", "Artículo eliminado")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo eliminar: {e}")
    
    def closeEvent(self, event):
        self.controller.detalle_modificado.emit()
        event.accept()