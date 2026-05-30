import wx 

FRAMETB = True
TBFLAGS = ( wx.LI_VERTICAL
            | wx.NO_BORDER
            | wx.TB_FLAT
            )


class TestToolBar(wx.Frame):
    def __init__(self, parent, log):
        wx.Frame.__init__(self, parent, -1, 'Test ToolBar', size=(600, 400))
        self.log = log
        self.timer = None
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)

        client = wx.Panel(self)
        client.SetBackgroundColour(wx.WHITE)

        if FRAMETB:
            tb = self.CreateToolBar( TBFLAGS )
        else:
            tb = wx.ToolBar(client, style=TBFLAGS)
            sizer = wx.BoxSizer(wx.VERTICAL)
            sizer.Add(tb, 0, wx.EXPAND)
            client.SetSizer(sizer)

    def OnCloseWindow(self, event):
        if self.timer is not None:
            self.timer.Stop()
            self.timer = None
        self.Destroy()


class ConsoleLogger:
    def write(self, text):
        print(text, end="")
    def WriteText(self, text):
        print(text, end="")


if __name__ == '__main__':
    app = wx.App()
    logger = ConsoleLogger()
    panel = TestToolBar(None, logger)
    panel.Show()
    app.MainLoop()