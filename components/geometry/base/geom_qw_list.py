import suit.core.render.engine as render_engine
import suit.core.render.mygui as mygui
import suit.core.kernel


class QuadrangleChanger:

    def __init__(self, _obj, _callback, _default_value = None):
        """Constructor

        @param _node:    SCg-node to change content
        @type _node:    SCgNode
        @param _callback_del:    functions that calls on dialog deletion
        @type _callback_del:    function
        """
        self.panel = None
        self.types_list = None
        self.object = _obj
        self._callback = _callback
        self.default_value = _default_value
        self._formats = {}  # map of formats, key: format name, value: (format sc_addr, edit support)
        self.button_ok = None
        self.button_cancel = None
        self.sel_fmt = None     # selected format title


        self.width = 250
        self.height = 250

        self.createPanel()

        self.build_list()

    def delete(self):
        self.destroyPanel()


    def createPanel(self):
        """Create controls panel
        """
        #assert self.panel is None

        self.panel = render_engine.Gui.createWidgetT("Window", "Panel", mygui.IntCoord(0, 0, self.width, self.height),
            mygui.Align(), "Info", "")
        self.types_list = self.panel.createWidgetT("List", "List", mygui.IntCoord(10, 10, self.width - 20, 165), mygui.Align())
        self.types_list.subscribeEventChangePosition(self, 'item_selected')

        self.button_ok = self.panel.createWidgetT("Button", "Button", mygui.IntCoord(10, self.height - 35, 50, 25), mygui.Align())
        self.button_cancel = self.panel.createWidgetT("Button", "Button", mygui.IntCoord(60, self.height - 35, 60, 25), mygui.Align())

        self.button_ok.setCaption("Ok")
        self.button_cancel.setCaption("Cancel")
        self.button_ok.setEnabled(False)
        self.button_ok.subscribeEventMouseButtonClick(self, '_onButtonOkClick')
        self.button_cancel.subscribeEventMouseButtonClick(self, '_onButtonCancelClick')

        self.panel.setVisible(True)

    def destroyPanel(self):
        """Destroys controls panel
        """
        assert self.panel is not None
        render_engine.Gui.destroyWidget(self.panel)

        self.panel = None

    def run(self):

        # build list of available components
        self.build_list()

        # calculate panel position
        pos = render_engine.pos3dTo2dWindow(self.object[0].getPosition() + self.object[0].getScale() / 2)
        # sure that dialog isn't placed out of screen
        x, y = pos
        x2 = x + self.width
        y2 = y + self.height

        if x2 >= render_engine.Window.width:
            x = render_engine.Window.width - self.width
        elif x < 0:
            x = 0

        if y2 >= render_engine.Window.height:
            y = render_engine.Window.height - self.height
        elif y < 0:
            y = 0

        self.panel.setPosition(x, y)

        # show panel
        self.panel.setVisible(True)

    def build_list(self):
        """Builds list of available viewers/editors components
        """
        kernel = suit.core.kernel.Kernel.getSingleton()
        session = kernel.session()

        # get available formats
        fmt_view = kernel.getRegisteredViewerFormats()
        fmt_edit = kernel.getRegisteredEditorFormats()

        # process formats to create map
        for fmt in fmt_view:
            title = session.get_idtf(fmt)
            if self._formats.has_key(title):
                continue
            self._formats[title] = (fmt, False)

        # check for edit
        for fmt in fmt_edit:
            title = session.get_idtf(fmt)
            self._formats[title] = (self._formats[title][0], True)

        # fill list with available information about formats
        self.types_list.removeAllItems()
        for title in ["Rectangle", "Square", "Rhombus", "Trapeze", "Parallelogram"]:
            self.types_list.addItem(title)

        self.types_list.clearIndexSelected()

    def item_selected(self, _widget, _idx):
        """Event handler for types list selection change
        """
        self.sel_fmt = (_idx, str(self.types_list.getItemNameAt(_idx)))


        # enable "ok" button if any item selected
        self.button_ok.setEnabled(True)


    def _onButtonOkClick(self, widget):
        """Event handler for "Ok" button
        """
        if self.sel_fmt is not None:
            self._callback(self.object, self.sel_fmt)
            print self.sel_fmt
        self.delete()

    def _onButtonCancelClick(self, widget):
        """Event handler for Cancel button
        """
        self.delete()

