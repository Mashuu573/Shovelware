import json
import threading
import websocket  
import wx

# Dirección del servidor
DIRECCION_SERVIDOR = "ws://192.168.1.40:6789"


class Acciones_Red:
    conexion_websocket = None
    ventana = None

    def registrar_ventana(self, ventana_instancia):
        # Guarda la referencia a la ventana activa de la GUI
        self.ventana = ventana_instancia

    def iniciar_conexion_servidor(self):
        # Iniciamos el hilo solo para que no se congele la pantalla
        hilo = threading.Thread(target=self.conectar_servidor, daemon=True) #Utilizo el deamon como forma de que sea un hilo temporal que al cerrar la ventana principal este hilo se destruya
        hilo.start()

    def conectar_servidor(self):
        # Conexión principal
        try:
            # Creamos la conexión directa
            self.conexion_websocket = websocket.create_connection(
                DIRECCION_SERVIDOR
            )

            # Registrarse en el servidor 
            paquete_registro = {
                "accion": "registrar",
                "nombre": self.ventana.mi_nombre,
            }
            self.conexion_websocket.send(json.dumps(paquete_registro))

            # Escuchar mensajes del servidor en un bucle "while"
            while True:
                mensaje = self.conexion_websocket.recv()
                datos = json.loads(mensaje)
                self.procesar_mensaje_servidor(datos)

        except Exception as error:
            wx.CallAfter(
                self.ventana.area_mensajes.AppendText, f"Error: {error}\n"
            )

    def enviar_al_servidor(self, datos):
        # Envía datos de forma directa 
        if self.conexion_websocket:
            try:
                paquete = json.dumps(datos)
                self.conexion_websocket.send(paquete)
            except Exception as error:
                print(f"Error al enviar datos: {error}")

    def procesar_mensaje_servidor(self, datos):
        # Procesa los mensajes que llegan del servidor
        accion = datos.get("accion")

        if accion == "mensaje_entrante":
            wx.CallAfter(self.recibir_mensaje, datos)
        elif accion == "error":
            wx.CallAfter(wx.MessageBox, datos.get("texto"), "Error")
        elif accion == "resultado_verificacion":
            wx.CallAfter(self.procesar_verificacion, datos)

    def recibir_mensaje(self, datos):
        # Muestra un mensaje nuevo en la conversación correcta
        remitente = datos.get("remitente")
        destino = datos.get("destino")
        texto = datos.get("texto")

        if destino == "General":
            sala = "General"
            linea = f"{remitente}: {texto}\n"
        else:
            sala = (
                remitente if remitente != self.ventana.mi_nombre else destino
            )
            nombre_mostrar = (
                "Tú" if remitente == self.ventana.mi_nombre else remitente
            )
            linea = f"{nombre_mostrar}: {texto}\n"

        if sala not in self.ventana.conversaciones:
            self.ventana.conversaciones[sala] = f"Chat Privado con {sala}\n"
            self.ventana.lista_contactos.Append(sala)

        self.ventana.conversaciones[sala] += linea

        if self.ventana.sala_actual == sala:
            self.ventana.area_mensajes.AppendText(linea)

    def procesar_verificacion(self, datos):
        # Procesa si un usuario existe o no
        existe = datos.get("existe")
        nombre = datos.get("nombre")

        if existe:
            self.ventana.conversaciones[nombre] = f"Chat Privado con {nombre}\n"
            self.ventana.lista_contactos.Append(nombre)

            posicion = self.ventana.lista_contactos.FindString(nombre)
            self.ventana.lista_contactos.SetSelection(posicion)
            self.ventana.sala_actual = nombre
            self.ventana.etiqueta_sala.SetLabel(f"Sala: {nombre}")
            self.ventana.area_mensajes.SetValue(
                self.ventana.conversaciones[nombre]
            )
        else:
            wx.MessageBox(f"El usuario '{nombre}' no existe", "error")