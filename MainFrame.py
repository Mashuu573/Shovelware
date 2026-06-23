import wx 
import red
import emoji
import wx.lib.colourchooser as cc
import wx.adv
from wx.lib.wordwrap import wordwrap

# Estilo de la barra de herramientas
ESTILO_TOOLBAR = wx.TB_VERTICAL | wx.NO_BORDER | wx.TB_FLAT

# Clase principal
class MainFrame(wx.Frame):
    
    def __init__(self):
        super().__init__(parent=None, title="Shovelware", size=(600, 400))
        
        # Variables que guardan información importante

        self.mi_nombre = ""
        self.sala_actual = "General"
        self.red_actual = None 
        
        # Aquí guardaremos todas las conversaciones
        self.conversaciones = {
            "General": ""
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
        self.splashArt()
        panel_izquierdo, panel_derecho = self.crear_paneles_divididos()
        self.crear_lista_contactos(panel_izquierdo)
        self.crear_area_chat(panel_derecho)
        self.crear_menu()
        self.crear_barra_estado()
        self.iniciar_reloj()
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
        self.lista_contactos.Append("General")
        self.lista_contactos.SetSelection(0)
        self.lista_contactos.Bind(wx.EVT_LISTBOX, self.cuando_cambiar_sala)
        organizador.Add(self.lista_contactos, 1, wx.EXPAND | wx.ALL, 5)
        
        panel.SetSizer(organizador)
    







    def crear_area_chat(self, panel):
       #Crea el área de mensajes a la derecha
        organizador = wx.BoxSizer(wx.VERTICAL)
        
        # Etiqueta con el nombre del contacto
        self.etiqueta_sala = wx.StaticText(panel, label="Chat: General")
        organizador.Add(self.etiqueta_sala, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        
        # Área donde se ven los mensajes (solo lectura)
        self.area_mensajes = wx.TextCtrl(
            panel, 
            value=self.conversaciones["General"],
            style=wx.TE_READONLY | wx.TE_MULTILINE
        )
        organizador.Add(self.area_mensajes, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
        
        # Caja para escribir mensajes
        self.caja_escritura = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER)
        self.caja_escritura.SetHint("Escribi aca y pulsa Enter...")
        self.caja_escritura.Bind(wx.EVT_TEXT_ENTER, self.cuando_enviar_mensaje)
        organizador.Add(self.caja_escritura, 0, wx.EXPAND | wx.ALL, 5)
        
        panel.SetSizer(organizador)
    
    #Creo el status bar
    def crear_barra_estado(self):
        self.statusBar = self.CreateStatusBar(1)
        self.statusBar.SetStatusText("Iniciando reloj...")
    
    def iniciar_reloj(self):
        self.timer_reloj = wx.Timer(self) #Fijo un temporizador que se va a ir actualizando cada 1000 ms (1 segundo)
        self.Bind(wx.EVT_TIMER, self.actualizar_hora, self.timer_reloj)
        self.timer_reloj.Start(1000)
        self.actualizar_hora(None)

    def actualizar_hora(self, event):
        ahora = wx.DateTime.Now()
        hora_formateada = ahora.Format("%H:%M:%S")
        self.statusBar.SetStatusText(f"Hora actual: {hora_formateada}")

    def crear_menu(self):
        menuBar = wx.MenuBar()
        menu1 = wx.Menu()
        menu2 = wx.Menu()
        menu3 = wx.Menu()
        menu1.Append(101, "Agregar contacto")
        menu1.Append(102, "Eliminar contacto")
        menu2.Append(202, "Mostrar lista emojis")
        menu2.Append(203, "Acerca De")
        menuBar.Append(menu1, "&Contactos")
        menuBar.Append(menu2, "&Informacion")
        self.SetMenuBar(menuBar)


        self.Bind(wx.EVT_MENU, self.agregar_contacto, id=101)
        self.Bind(wx.EVT_MENU, self.eliminar_contacto, id=102)
        self.Bind(wx.EVT_MENU, self.mostrarEmojiLista, id=202)
        self.Bind(wx.EVT_MENU, self.acercaDe, id=203)
        
    
    
    def crear_toolbar(self):
        #Crea la barra de herramientas superior
        toolbar = self.CreateToolBar(ESTILO_TOOLBAR)
        
        # Boton Agregar
        icono_agregar = wx.ArtProvider.GetBitmap(wx.ART_PLUS, wx.ART_TOOLBAR)
        btn_agregar = toolbar.AddTool(wx.NewIdRef(), "Agregar", icono_agregar, "Agregar contacto")
        
        # Boton Eliminar
        icono_eliminar = wx.ArtProvider.GetBitmap(wx.ART_DELETE, wx.ART_TOOLBAR)
        btn_eliminar = toolbar.AddTool(-1, "Eliminar", icono_eliminar, "Eliminar contacto")
        
        # Boton informacion 
        icono_informacion = wx.ArtProvider.GetBitmap(wx.ART_INFORMATION, wx.ART_TOOLBAR)
        btn_informacion = toolbar.AddTool(-1, "Informacion", icono_informacion, "mostrar informacion")

        
        
        toolbar.Realize()
        
        # Conectar los botones con sus funciones
        self.Bind(wx.EVT_TOOL, self.agregar_contacto, btn_agregar)
        self.Bind(wx.EVT_TOOL, self.eliminar_contacto, btn_eliminar)
        self.Bind(wx.EVT_TOOL, self.acercaDe, btn_informacion)
 
        
    #Acciones del usuario
    def pedir_nombre_usuario(self):
        #Pide el nombre al iniciar el programa
        dialogo = wx.TextEntryDialog(self, "¿Cuál es tu nombre?", "Bienvenido")
        
        if dialogo.ShowModal() == wx.ID_OK:
            self.mi_nombre = dialogo.GetValue().strip()
        dialogo.Destroy()
        
        if not self.mi_nombre:
            self.mi_nombre = "Invitado"
        
        self.red_actual = red.Acciones_Red()
        self.red_actual.registrar_ventana(self)
        self.red_actual.iniciar_conexion_servidor()
    






    def cuando_cambiar_sala(self, event):
        #Se ejecuta al hacer clic en un contacto
        indice = event.GetSelection()
        self.sala_actual = self.lista_contactos.GetString(indice)
        
        # Actualizar la interfaz
        self.etiqueta_sala.SetLabel(f"Sala: {self.sala_actual}")
        texto_conversacion = self.conversaciones.get(self.sala_actual, "")
        self.area_mensajes.SetValue(texto_conversacion)
    





    def agregar_contacto(self, event):
        #Se ejecuta al pulsar el botón Agregar
        dialogo = wx.TextEntryDialog(self, "Nombre del contacto:", "Agregar contacto")
        
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
            self.red_actual.enviar_al_servidor({
                "accion": "verificar_usuario",
                "nombre": nombre
            })
        
        dialogo.Destroy()
    



    def eliminar_contacto(self, event):
        #Se ejecuta al pulsar el botón Eliminar
        if self.sala_actual == "General":
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
            
            # Volver al chat general
            self.sala_actual = "General"
            self.lista_contactos.SetSelection(0)
            self.etiqueta_sala.SetLabel("Sala: General")
            self.area_mensajes.SetValue(self.conversaciones["General"])
    

    def acercaDe(self, event):
        
        info = wx.adv.AboutDialogInfo()
        info.Name = "Shovelware"
        info.Version = "4.3.6"
        info.Copyright = "(c) 2026-2044 Programmer forever"
        
        info.Description = wordwrap(
        "Universidad Nacional de Pilar - 2026 - Programacion Orientada a Objetos \
        \nSe utilizo codigo de internet para poder crear la estructura de servidor y un poco de red, se utilizo: \
        \nstackoverflow y Reddit, ademas de algunas consultas a la IA para ver enfoques de estructuras",350, wx.ClientDC(self))
        info.WebSite = (
            "https://github.com/Mashuu573/Shovelware", 
            "Código Fuente | Licencia: https://www.gnu.org/licenses/gpl-3.0.html"
        )
        info.Developers = ["Torres Mauricio Ezequiel"]
        info.License = wordwrap("https://www.gnu.org/licenses/gpl-3.0.html#license-text", 500, wx.ClientDC(self))
        wx.adv.AboutBox(info)
    def mostrarEmojiLista(self, event):
        mensaje_lista = (
            "EXPRESIONES Y CARAS:\n"
            ":cara_sonriente_con_ojos_sonrientes: -> 😊\n"
            ":cara_llorando_de_risa: -> 😂\n"
            ":cara_guiñando_el_ojo: -> 😉\n"
            ":cara_pensativa: -> 🤔\n"
            ":cara_con_ojos_de_corazón: -> 😍\n"
            ":cara_haciendo_un_guiño_y_mandando_un_beso: -> 😘\n"
            ":cara_neutral: -> 😐\n"
            ":cara_gritando_de_miedo: -> 😱\n"
            ":cara_llorando_fuertemente: -> 😭\n"
            ":cara_enojada: -> 😡\n"
            ":cara_con_gafas_de_sol: -> 😎\n"
            ":cara_durmiendo: -> 😴\n"
            ":cara_alreves: -> 🙃\n\n"
            
            "GESTOS Y MANOS:\n"
            ":pulgar_hacia_arriba: -> 👍\n"
            ":pulgar_hacia_abajo: -> 👎\n"
            ":manos_aplaudiendo: -> 👏\n"
            ":mano_saludando: -> 👋\n"
            ":manos_en_oración: -> 🙏\n"
            ":mano_haciendo_el_signo_de_la_victoria: -> ✌️\n"
            ":mano_con_gesto_de_bien: -> 👌\n\n"
            
            "CORAZONES Y SÍMBOLOS:\n"
            ":corazón_rojo: -> ❤️\n"
            ":corazón_roto: -> 💔\n"
            ":corazón_azul: -> 💙\n"
            ":corazón_verde: -> 💚\n"
            ":corazón_brillante: -> 💖\n"
            ":cien_puntos: -> 💯\n"
            ":marca_de_verificación: -> ✅\n"
            ":atención: -> ⚠️\n"
            ":prohibido: -> 🚫\n\n"
            
            "EFECTOS Y ELEMENTOS:\n"
            ":fuego: -> 🔥\n"
            ":destellos: -> ✨\n"
            ":colisión: -> 💥\n"
            ":gotas_de_sudor: -> 💦\n"
            ":viento: -> 💨\n\n"
            
            "OBJETOS Y TECNOLOGÍA:\n"
            ":bocadillo_de_diálogo: -> 💬\n"
            ":computadora_portátil: -> 💻\n"
            ":teléfono_móvil: -> 📱\n"
            ":cohete: -> 🚀\n"
            ":corona: -> 👑\n"
            ":regalo_empaquetado: -> 🎁\n"
            ":bombilla: -> 💡\n"
            ":candado_cerrado: -> 🔒\n"
            ":llave: -> 🔑\n"
            ":chincheta: -> 📌"
        )
        wx.MessageBox(mensaje_lista, "Lista de emojis")

    def cuando_enviar_mensaje(self, event):
        #Se ejecuta al pulsar Enter en la caja de texto
        texto = self.caja_escritura.GetValue().strip()
        
        if texto and self.red_actual and self.red_actual.conexion_websocket:
            self.caja_escritura.Clear()
            
            # Enviar mensaje al servidor
            self.red_actual.enviar_al_servidor({
                "accion": "enviar_mensaje",
                "destino": self.sala_actual,
                "texto": emoji.emojize(texto, language='es')
            })
        else: 
            wx.MessageBox("No hay conexion con el servidor, no se puede enviar el mensaje", "error")
    
    def splashArt(self):
        splash_image = wx.Bitmap(r"C:\Users\maure\OneDrive\Desktop\Nueva carpeta (2)\Gemini_Generated_Image_5ngipu5ngipu5ngi.png", wx.BITMAP_TYPE_PNG) 
        splash = wx.adv.SplashScreen(splash_image, wx.adv.SPLASH_CENTER_ON_SCREEN | wx.adv.SPLASH_TIMEOUT, 3000, None, -1)
        wx.Yield()
        


# Inicia el programa
if __name__ == '__main__':
    app = wx.App()
    ventana = MainFrame()
    ventana.Center()
    ventana.Show()
    app.MainLoop()