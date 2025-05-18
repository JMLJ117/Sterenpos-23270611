from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput

def mostrar_popup(titulo, mensaje):
    box = BoxLayout(orientation='vertical', padding=10, spacing=10)
    box.add_widget(Label(text=mensaje))
    btn = Button(text='Cerrar', size_hint_y=None, height='40dp')
    box.add_widget(btn)
    popup = Popup(title=titulo, content=box,
                  size_hint=(None, None), size=('300dp','200dp'))
    btn.bind(on_release=popup.dismiss)
    popup.open()

def solicitar_datos(campos, callback):
    box = BoxLayout(orientation='vertical', padding=10, spacing=10)
    inputs = {}
    for c in campos:
        ti = TextInput(hint_text=c, multiline=False)
        inputs[c] = ti
        box.add_widget(ti)
    btn_ok = Button(text='OK', size_hint_y=None, height='40dp')
    box.add_widget(btn_ok)
    popup = Popup(title='Ingrese datos', content=box,
                  size_hint=(None, None),
                  size=('400dp', f'{60*len(campos)+60}dp'))
    def _on_ok(_):
        datos = {c: inputs[c].text for c in campos}
        callback(datos)
        popup.dismiss()
    btn_ok.bind(on_release=_on_ok)
    popup.open()

