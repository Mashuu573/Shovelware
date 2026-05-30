import wx 

FRAMETB = True
TBFLAGS = ( wx.TB_HORIZONTAL
            | wx.NO_BORDER
            | wx.TB_FLAT
            )

class TestSearchCtrl(wx.SearchCtrl):
    maxSearches = 5

    def __init__(self, parent, id=-1, value="",
                 pos=wx.DefaultPosition, size=wx.DefaultSize, style=0,
                 doSearch=None):
        style |= wx.TE_PROCESS_ENTER
        wx.SearchCtrl.__init__(self, parent, id, value, pos, size, style)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnTextEntered)
        self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.OnTextEntered)
        self.Bind(wx.EVT_MENU_RANGE, self.OnMenuItem, id=1, id2=self.maxSearches)
        self.doSearch = doSearch
        self.searches = []

    def OnTextEntered(self, evt):
        text = self.GetValue()
        if self.doSearch(text):
            self.searches.append(text)
            if len(self.searches) > self.maxSearches:
                del self.searches[0]
            self.SetMenu(self.MakeMenu())
        self.SetValue("")

    def OnMenuItem(self, evt):
        text = self.searches[evt.GetId()-1]
        self.doSearch(text)

    def MakeMenu(self):
        menu = wx.Menu()
        item = menu.Append(-1, "Recent Searches")
        item.Enable(False)
        for idx, txt in enumerate(self.searches):
            menu.Append(1+idx, txt)
        return menu

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

        log.write("Default toolbar tool size: %s\n" % str(tb.GetToolBitmapSize()))

        self.CreateStatusBar()

        tsize = (24,24)
        new_bmp =  wx.ArtProvider.GetBitmapBundle(wx.ART_NEW, wx.ART_TOOLBAR, tsize)
        open_bmp = wx.ArtProvider.GetBitmapBundle(wx.ART_FILE_OPEN, wx.ART_TOOLBAR, tsize)
        copy_bmp = wx.ArtProvider.GetBitmapBundle(wx.ART_COPY, wx.ART_TOOLBAR, tsize)
        paste_bmp= wx.ArtProvider.GetBitmapBundle(wx.ART_PASTE, wx.ART_TOOLBAR, tsize)
        
    
        toggle_bmp = wx.ArtProvider.GetBitmapBundle(wx.ART_TICK_MARK, wx.ART_TOOLBAR, tsize)
        null_bmp = wx.BitmapBundle(wx.NullBitmap)

        tb.SetToolBitmapSize(tsize)

        tb.AddTool(10, "New", new_bmp, null_bmp, wx.ITEM_NORMAL, "New", "Long help for 'New'", None)
        self.Bind(wx.EVT_TOOL, self.OnToolClick, id=10)
        self.Bind(wx.EVT_TOOL_RCLICKED, self.OnToolRClick, id=10)

        tb.AddTool(20, "Open", open_bmp, null_bmp, wx.ITEM_NORMAL, "Open", "Long help for 'Open'", None)
        self.Bind(wx.EVT_TOOL, self.OnToolClick, id=20)
        self.Bind(wx.EVT_TOOL_RCLICKED, self.OnToolRClick, id=20)

        tb.AddSeparator()
        tb.AddTool(30, "Copy", copy_bmp, null_bmp, wx.ITEM_NORMAL, "Copy", "Long help for 'Copy'", None)
        self.Bind(wx.EVT_TOOL, self.OnToolClick, id=30)
        self.Bind(wx.EVT_TOOL_RCLICKED, self.OnToolRClick, id=30)

        tb.AddTool(40, "Paste", paste_bmp, null_bmp, wx.ITEM_NORMAL, "Paste", "Long help for 'Paste'", None)
        self.Bind(wx.EVT_TOOL, self.OnToolClick, id=40)
        self.Bind(wx.EVT_TOOL_RCLICKED, self.OnToolRClick, id=40)

        tb.AddSeparator()

        
        tool = tb.AddTool(50, "Checkable", toggle_bmp, shortHelp="Toggle this",  kind=wx.ITEM_CHECK)
        self.Bind(wx.EVT_TOOL, self.OnToolClick, id=50)

        self.Bind(wx.EVT_TOOL_ENTER, self.OnToolEnter)
        self.Bind(wx.EVT_TOOL_RCLICKED, self.OnToolRClick) 
        self.Bind(wx.EVT_TIMER, self.OnClearSB)

        tb.AddSeparator()
        cbID = wx.NewIdRef()

        tb.AddControl(
            wx.ComboBox(
                tb, cbID, "", choices=["", "This", "is a", "wx.ComboBox"],
                size=(150,-1), style=wx.CB_DROPDOWN
                ))
        self.Bind(wx.EVT_COMBOBOX, self.OnCombo, id=cbID)

        tb.AddStretchableSpace()
        search = TestSearchCtrl(tb, size=(150,-1), doSearch=self.DoSearch)
        tb.AddControl(search)

        tb.Realize()

    def DoSearch(self,  text):
        self.log.WriteText("DoSearch: %s\n" % text)
        return True

    def OnToolClick(self, event):
        self.log.WriteText("tool %s clicked\n" % event.GetId())
        tb = event.GetEventObject()
        tb.EnableTool(10, not tb.GetToolEnabled(10))

    def OnToolRClick(self, event):
        self.log.WriteText("tool %s right-clicked\n" % event.GetId())

    def OnCombo(self, event):
        self.log.WriteText("combobox item selected: %s\n" % event.GetString())

    def OnToolEnter(self, event):
        self.log.WriteText('OnToolEnter: %s, %s\n' % (event.GetId(), event.GetInt()))

        if self.timer is None:
            self.timer = wx.Timer(self)

        if self.timer.IsRunning():
            self.timer.Stop()

        self.timer.Start(2000)
        event.Skip()

    def OnClearSB(self, event):  
        self.SetStatusText("")
        self.timer.Stop()
        self.timer = None

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