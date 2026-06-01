import wx 

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
        splitter = MySplitter(self)

        sty = wx.BORDER_SUNKEN

        
        p1 = wx.Window(splitter, style=sty)
        
        contacto_lista = wx.StaticText(p1, -1, "Lista de Contactos", (10, 10))

        
        p2 = wx.Window(splitter, style=sty)
        
        contacto_actual = wx.StaticText(p2, -1, "Contacto actual", (10, 10))

        splitter.SetMinimumPaneSize(50)  
        
        
        splitter.SplitVertically(p1, p2, 180)

        self.CreateToolBar(TBFLAGS)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer2 = wx.BoxSizer(wx.VERTICAL)

        p1.SetSizer(sizer2)
        sizer2.Add(contacto_lista, 0, wx.ALIGN_CENTER)

        p2.SetSizer(sizer)

        sizer.Add(contacto_actual, 0, wx.ALIGN_CENTER)

        mensajes_recibidos = wx.TextCtrl(p2, 1, "Mensaje recibido", size=(125, -1))
        mensaje_enviar =  wx.TextCtrl(p2, 0, "Mensaje", size=(125, -1))
        sizer.Add(mensajes_recibidos, 1, wx.EXPAND)
        sizer.Add(mensaje_enviar, 0, wx.EXPAND)
        
    
    def OnCloseWindow(self, event):
        self.Destroy()       




if __name__ == '__main__':
    app = wx.App()
    panel = MainFrame()
    panel.Center()
    panel.Show()
    app.MainLoop()