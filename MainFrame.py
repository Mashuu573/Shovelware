import wx
from Toolbar import TestToolBar
class MyFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title="tittle", size=(600, 400))
        
        TestToolBar()



if __name__ == '__main__':
    App = wx.App()
    MyFrame().Show()
    App.MainLoop()
