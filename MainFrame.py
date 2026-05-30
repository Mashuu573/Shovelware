import wx

class MyFrame(wx.Frame):
    def __init__(self):

        wx.Frame.__init__(self, parent=None, title="Hola")
        panel = wx.Panel(self, -1)

        button = wx.Button(panel, 1003, "Close Me")
        button.SetPosition((15, 15))
        self.Bind(wx.EVT_BUTTON, self.OnCloseMe, button)
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)


    def OnCloseMe(self, event):
        self.Close(True)

    def OnCloseWindow(self, event):
        self.Destroy()


if __name__ == '__main__':
    App = wx.App()
    MyFrame().Show()
    App.MainLoop()
