import wx 

TBFLAGS = ( wx.TB_HORIZONTAL
            | wx.NO_BORDER
            | wx.TB_FLAT
            )


class TestToolBar(wx.Frame):
    def __init__(self, parent):
        super().__init__(parent, title="tittle", size=(600, 400))
        
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)

        client = wx.Panel(self)
        client.SetBackgroundColour(wx.WHITE)

        

        tb = wx.ToolBar(client, style=TBFLAGS)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(tb, 0, wx.EXPAND)

        t1 = wx.TextCtrl(client, -1, "Mensaje", size=(125, -1))
        sizer.Add(t1, 0, wx.EXPAND)
        
        client.SetSizer(sizer)

        
        

        
    def OnCloseWindow(self, event):
        self.Destroy()       



if __name__ == '__main__':
    app = wx.App()
    panel = TestToolBar(None)
    panel.Center()
    panel.Show()
    app.MainLoop()