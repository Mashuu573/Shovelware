import wx 
import websockets as ws
import asyncio
import threading

TBFLAGS = ( wx.TB_HORIZONTAL
            | wx.NO_BORDER
            | wx.TB_FLAT
            )

class MySplitter(wx.SplitterWindow):
    def __init__(self, parent):
        
        super().__init__(parent, style=wx.SP_LIVE_UPDATE | wx.SP_3D)



class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title="Shovelware", size=(600, 400))
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        
        self.ws_conexion = None 
        self.loop_asyncio = None 


        #Agrego mi ventana dividido al mainframe, designo el estilo y una variable a cada mitad de la ventana, tambien agrego
        #un punto default de tamaño para que se abra en una vista comoda y un tamaño minimo de panel
        splitter = MySplitter(self)
        sty = wx.BORDER_SUNKEN
        p1 = wx.Panel(splitter, style=sty)
        p2 = wx.Panel(splitter, style=sty)
        splitter.SetMinimumPaneSize(50)  
        splitter.SplitVertically(p1, p2, 180)
        
        

        

        
        #Texto estatico para señalar puntos
        contacto_lista = wx.StaticText(p1, -1, "Lista de Contactos")
        


        #Creo la toolbar para elementos esenciales
        toolbar = self.CreateToolBar(TBFLAGS)
        imagen_contacto_original = wx.Image(r"D:\Proyectos\Python\iconos\images-removebg-preview.png", wx.BITMAP_TYPE_ANY)
        imagen_contacto_Redimensionada = imagen_contacto_original.Scale(24, 24, wx.IMAGE_QUALITY_HIGH)
        toolbar.AddTool(-1, "Agregar", wx.Bitmap(imagen_contacto_Redimensionada), shortHelp="Agregar contacto")
        
        imagen_basura_original = wx.Image(r"D:\Proyectos\Python\iconos\png-transparent-rubbish-bins-waste-paper-baskets-recycling-bin-computer-icons-others-miscellaneous-text-rectangle.png")
        imagen_basura_Redimensionada = imagen_basura_original.Scale(24, 24, wx.IMAGE_QUALITY_HIGH)
        toolbar.AddTool(-1, "Eliminar", wx.Bitmap(imagen_basura_Redimensionada), shortHelp="eliminar contacto actual")
        toolbar.Realize()

        #Creo contenedores para poder ordenar de mejor manera los elementos que voy a ingresar
        sizer = wx.BoxSizer(wx.VERTICAL)
        contacto_actual = wx.StaticText(p2, -1, "Contacto actual")
        self.mensajes_recibidos = wx.TextCtrl(p2, -1, value="", style=wx.TE_READONLY | wx.TE_MULTILINE)
        self.mensaje_enviar =  wx.TextCtrl(p2, -1, style=wx.TE_PROCESS_ENTER)
        self.mensaje_enviar.Bind(wx.EVT_TEXT_ENTER, self.OnEnviar)
        self.mensaje_enviar.SetHint("Escriba su mensaje...")
        sizer.Add(contacto_actual, 0, wx.ALIGN_CENTER)
        sizer.Add(self.mensajes_recibidos, 1, wx.EXPAND)
        sizer.Add(self.mensaje_enviar, 0, wx.EXPAND)
        
        


        sizer2 = wx.BoxSizer(wx.VERTICAL)
        sizer2.Add(contacto_lista, 0, wx.ALIGN_CENTER)

        p1.SetSizer(sizer2)
        p2.SetSizer(sizer)

        #Lo uso para refrescar las ventanas y que muestren informacion correctamente
        p1.Layout()
        p2.Layout()
        splitter.Layout()
        self.Layout()

        self.hilo_red = threading.Thread(target=self.ArrancarBucleAsyncio, daemon=True)
        self.hilo_red.start()

    def ArrancarBucleAsyncio(self):
        self.loop_asyncio = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop_asyncio)
        self.loop_asyncio.run_until_complete(self.ConectarServidorWS())        

    async def ConectarServidorWS(self):
        url = "ws://192.168.1.40:6789"
        try:
                async with ws.connect(url) as websocket:
                    self.ws_conexion = websocket
                    wx.CallAfter(self.ActualizarHistorial, "[Conectado al servidor de chat]\n")
                    
                    
                    async for msg in websocket:
                        # Enviamos el mensaje recibido de forma segura a la interfaz 
                        wx.CallAfter(self.ActualizarHistorial, f"Otro: {msg}\n")
                        
        except Exception as e:
                wx.CallAfter(self.ActualizarHistorial, f"[Error de conexión: {e}]\n")

    def ActualizarHistorial(self, texto):
        #Método seguro ejecutado en el hilo principal para pintar el texto
        self.mensajes_recibidos.AppendText(texto)   
    def OnEnviar(self, event):
        texto = self.mensaje_enviar.GetValue()
        if texto:
            self.mensajes_recibidos.AppendText(f"Tu: {texto}\n")
            self.mensaje_enviar.Clear()
            asyncio.run_coroutine_threadsafe(self.ws_conexion.send(texto), self.loop_asyncio)
        
    #Creo un evento para que deje de ejecutarse luego de darle click al boton de cerrar, caso contrario seguira en segundo plano
    def OnCloseWindow(self, event):
        self.Destroy()       




if __name__ == '__main__':
    app = wx.App()
    panel = MainFrame()
    panel.Center()
    panel.Show()
    app.MainLoop()