import wx 
import websockets as ws
import asyncio
import threading
import json


# Estilo de la barra de herramientas
ESTILO_TOOLBAR = wx.TB_HORIZONTAL | wx.NO_BORDER | wx.TB_FLAT

# Dirección del servidor (Ip de mi maquina, cambiar si se prueba en otra)
DIRECCION_SERVIDOR = "ws://192.168.1.40:6789"



# Clase principal
class VentanaChat(wx.Frame):
    
    def __init__(self):
        super().__init__(parent=None, title="Mi Chat", size=(600, 400))
        
        # Variables que guardan información importante
        self.conexion_websocket = None
        self.bucle_asyncio = None
        self.mi_nombre = ""
        self.sala_actual = "Global"
        
        # Aquí guardaremos todas las conversaciones
        self.conversaciones = {
            "Global": "Sala General\n"
        }
        
        # Construir la ventana paso a paso
        self.crear_interfaz()
        self.pedir_nombre_usuario()
        
        # Cerrar la ventana correctamente
        self.Bind(wx.EVT_CLOSE, self.cerrar_ventana)
    
    

    
    def cerrar_ventana(self, event):
        self.Destroy()
    
    # Crear interfaz
    def crear_interfaz(self):
        #Construye toda la ventana por partes
        panel_izquierdo, panel_derecho = self.crear_paneles_divididos()
        self.crear_lista_contactos(panel_izquierdo)
        self.crear_area_chat(panel_derecho)
        self.crear_toolbar()
    
    def crear_paneles_divididos(self):
        #Crea la ventana dividida en dos partes
        splitter = wx.SplitterWindow(self, style=wx.SP_LIVE_UPDATE | wx.SP_3D)
        splitter.SetMinimumPaneSize(50)
        
        panel_izq = wx.Panel(splitter, style=wx.BORDER_SUNKEN)
        panel_der = wx.Panel(splitter, style=wx.BORDER_SUNKEN)
        
        splitter.SplitVertically(panel_izq, panel_der, 180)
        return panel_izq, panel_der
    
    def crear_lista_contactos(self, panel):
        #Crea la lista de contactos a la izquierda
        organizador = wx.BoxSizer(wx.VERTICAL)
        
        # Título
        titulo = wx.StaticText(panel, label="Contactos")
        organizador.Add(titulo, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        
        # Lista de contactos
        self.lista_contactos = wx.ListBox(panel, style=wx.LB_SINGLE)
        self.lista_contactos.Append("Global")
        self.lista_contactos.SetSelection(0)
        self.lista_contactos.Bind(wx.EVT_LISTBOX, self.cuando_cambiar_sala)
        organizador.Add(self.lista_contactos, 1, wx.EXPAND | wx.ALL, 5)
        
        panel.SetSizer(organizador)
    
    def crear_area_chat(self, panel):
       #Crea el área de mensajes a la derecha
        organizador = wx.BoxSizer(wx.VERTICAL)
        
        # Etiqueta con el nombre del contacto
        self.etiqueta_sala = wx.StaticText(panel, label="Sala: Global")
        organizador.Add(self.etiqueta_sala, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        
        # Área donde se ven los mensajes (solo lectura)
        self.area_mensajes = wx.TextCtrl(
            panel, 
            value=self.conversaciones["Global"],
            style=wx.TE_READONLY | wx.TE_MULTILINE
        )
        organizador.Add(self.area_mensajes, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
        
        # Caja para escribir mensajes
        self.caja_escritura = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER)
        self.caja_escritura.SetHint("Escribe aquí y pulsa Enter...")
        self.caja_escritura.Bind(wx.EVT_TEXT_ENTER, self.cuando_enviar_mensaje)
        organizador.Add(self.caja_escritura, 0, wx.EXPAND | wx.ALL, 5)
        
        panel.SetSizer(organizador)
    
    def crear_toolbar(self):
        #Crea la barra de herramientas superior
        toolbar = self.CreateToolBar(ESTILO_TOOLBAR)
        
        # Botón Agregar
        icono_agregar = wx.ArtProvider.GetBitmap(wx.ART_PLUS, wx.ART_TOOLBAR)
        toolbar.AddTool(wx.NewIdRef(), "Agregar", icono_agregar, "Agregar contacto")
        
        # Botón Eliminar
        icono_eliminar = wx.ArtProvider.GetBitmap(wx.ART_DELETE, wx.ART_TOOLBAR)
        toolbar.AddTool(wx.NewIdRef(), "Eliminar", icono_eliminar, "Eliminar contacto")
        
        toolbar.Realize()
        
        # Conectar los botones con sus funciones
        self.Bind(wx.EVT_TOOL, self.cuando_agregar_contacto, id=toolbar.GetToolByPos(0).GetId())
        self.Bind(wx.EVT_TOOL, self.cuando_eliminar_contacto, id=toolbar.GetToolByPos(1).GetId())
    
    
    #Acciones del usuario
    def pedir_nombre_usuario(self):
        #Pide el nombre al iniciar el programa
        dialogo = wx.TextEntryDialog(self, "¿Cuál es tu nombre?", "Bienvenido")
        
        if dialogo.ShowModal() == wx.ID_OK:
            self.mi_nombre = dialogo.GetValue().strip()
        dialogo.Destroy()
        
        if not self.mi_nombre:
            self.mi_nombre = "Invitado"
        
        # Iniciar conexión con el servidor en segundo plano
        self.iniciar_conexion_servidor()
    
    def cuando_cambiar_sala(self, event):
        #Se ejecuta al hacer clic en un contacto
        indice = event.GetSelection()
        self.sala_actual = self.lista_contactos.GetString(indice)
        
        # Actualizar la interfaz
        self.etiqueta_sala.SetLabel(f"Sala: {self.sala_actual}")
        texto_conversacion = self.conversaciones.get(self.sala_actual, "")
        self.area_mensajes.SetValue(texto_conversacion)
    
    def cuando_agregar_contacto(self, event):
        #Se ejecuta al pulsar el botón Agregar
        dialogo = wx.TextEntryDialog(self, "Nombre del usuario:", "Agregar contacto")
        
        if dialogo.ShowModal() == wx.ID_OK:
            nombre = dialogo.GetValue().strip()
            
            # Validaciones básicas
            if not nombre:
                dialogo.Destroy()
                return
            if nombre == self.mi_nombre:
                wx.MessageBox("No puedes agregarte a ti mismo", "Error")
                dialogo.Destroy()
                return
            if nombre in self.conversaciones:
                wx.MessageBox("Ya tienes este chat abierto", "Aviso")
                dialogo.Destroy()
                return
            
            # Preguntar al servidor si el usuario existe
            self.enviar_al_servidor({
                "accion": "verificar_usuario",
                "nombre": nombre
            })
        
        dialogo.Destroy()
    
    def cuando_eliminar_contacto(self, event):
        #Se ejecuta al pulsar el botón Eliminar
        if self.sala_actual == "Global":
            wx.MessageBox("No puedes eliminar la sala general", "Error")
            return
        
        # Pedir confirmación
        mensaje = f"¿Borrar conversación con {self.sala_actual}?"
        if wx.MessageBox(mensaje, "Confirmar", wx.YES_NO) == wx.YES:
            # Borrar conversación
            if self.sala_actual in self.conversaciones:
                del self.conversaciones[self.sala_actual]
            
            # Quitar de la lista
            posicion = self.lista_contactos.FindString(self.sala_actual)
            self.lista_contactos.Delete(posicion)
            
            # Volver a Global
            self.sala_actual = "Global"
            self.lista_contactos.SetSelection(0)
            self.etiqueta_sala.SetLabel("Sala: Global")
            self.area_mensajes.SetValue(self.conversaciones["Global"])
    
    def cuando_enviar_mensaje(self, event):
        #Se ejecuta al pulsar Enter en la caja de texto
        texto = self.caja_escritura.GetValue().strip()
        
        if texto and self.conexion_websocket:
            self.caja_escritura.Clear()
            
            # Enviar mensaje al servidor
            self.enviar_al_servidor({
                "accion": "enviar_mensaje",
                "destino": self.sala_actual,
                "texto": texto
            })
    
    
    # Conexion con el servidor
    def iniciar_conexion_servidor(self):
        #Inicia la conexión en un hilo aparte 
        def tarea_en_segundo_plano():
            self.bucle_asyncio = asyncio.new_event_loop()
            asyncio.set_event_loop(self.bucle_asyncio)
            self.bucle_asyncio.run_until_complete(self.conectar_servidor())
        
        hilo = threading.Thread(target=tarea_en_segundo_plano, daemon=True)
        hilo.start()
    
    async def conectar_servidor(self):
        #Conexión principal con el servidor WebSocket
        try:
            async with ws.connect(DIRECCION_SERVIDOR) as websocket:
                self.conexion_websocket = websocket
                
                # Registrarse en el servidor
                await websocket.send(json.dumps({
                    "accion": "registrar",
                    "nombre": self.mi_nombre
                }))
                
                # Escuchar mensajes del servidor
                async for mensaje in websocket:
                    datos = json.loads(mensaje)
                    self.procesar_mensaje_servidor(datos)
                    
        except Exception as error:
            wx.CallAfter(self.area_mensajes.AppendText, f"Error: {error}\n")
    
    def procesar_mensaje_servidor(self, datos):
        #Procesa los mensajes que llegan del servidor
        accion = datos.get("accion")
        
        if accion == "mensaje_entrante":
            wx.CallAfter(self.recibir_mensaje, datos)
        elif accion == "error":
            wx.CallAfter(wx.MessageBox, datos.get("texto"), "Error")
        elif accion == "resultado_verificacion":
            wx.CallAfter(self.procesar_verificacion, datos)
    
    def recibir_mensaje(self, datos):
        #Muestra un mensaje nuevo en la conversación correcta
        remitente = datos.get("remitente")
        destino = datos.get("destino")
        texto = datos.get("texto")
        
        # Decidir a qué conversación pertenece
        if destino == "Global":
            sala = "Global"
            linea = f"{remitente}: {texto}\n"
        else:
            # Chat privado
            sala = remitente if remitente != self.mi_nombre else destino
            nombre_mostrar = "Tú" if remitente == self.mi_nombre else remitente
            linea = f"{nombre_mostrar}: {texto}\n"
        
        # Crear la conversación si no existe
        if sala not in self.conversaciones:
            self.conversaciones[sala] = f"Chat Privado con {sala}\n"
            self.lista_contactos.Append(sala)
        
        # Guardar el mensaje
        self.conversaciones[sala] += linea
        
        # Mostrarlo si estamos en esa sala
        if self.sala_actual == sala:
            self.area_mensajes.AppendText(linea)
    
    def procesar_verificacion(self, datos):
        #Procesa si un usuario existe o no
        existe = datos.get("existe")
        nombre = datos.get("nombre")
        
        if existe:
            # Crear nueva conversación
            self.conversaciones[nombre] = f"Chat Privado con {nombre}\n"
            self.lista_contactos.Append(nombre)
            
            # Seleccionar automáticamente
            posicion = self.lista_contactos.FindString(nombre)
            self.lista_contactos.SetSelection(posicion)
            self.sala_actual = nombre
            self.etiqueta_sala.SetLabel(f"Sala: {nombre}")
            self.area_mensajes.SetValue(self.conversaciones[nombre])
        else:
            wx.MessageBox(f"El usuario '{nombre}' no existe", "No encontrado")
    
    def enviar_al_servidor(self, datos):
        #Envía datos al servidor de forma segura
        if self.conexion_websocket:
            paquete = json.dumps(datos)
            asyncio.run_coroutine_threadsafe(
                self.conexion_websocket.send(paquete),
                self.bucle_asyncio
            )



# Inicia el programa
if __name__ == '__main__':
    app = wx.App()
    ventana = VentanaChat()
    ventana.Center()
    ventana.Show()
    app.MainLoop()