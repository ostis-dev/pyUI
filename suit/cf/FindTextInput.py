"""
-----------------------------------------------------------------------------
This source file is part of OSTIS (Open Semantic Technology for Intelligent Systems)
For the latest info, see http://www.ostis.net

Copyright (c) 2010 OSTIS

OSTIS is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

OSTIS is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with OSTIS.  If not, see <http://www.gnu.org/licenses/>.
-----------------------------------------------------------------------------
"""


'''
Created on 12.12.2012

@author: Vasiliy Posudevskiy
'''
import suit.core.render.engine as render_engine
import suit.core.render.mygui as mygui

class FindTextInput:
    """Class that realize idtf value input for a find
    """
    def __init__(self, _callback, _listOfFoundObjs, _manual = False):

        """Constructor
        @param _callback: function that will be called when value
        input finished. This function takes two parameters - object, text value.
        @type _callback: function
        @param _manual: flag to start changing manually. If it is True, then
        user will be need to call start function manually, else it will be called
        automatically on IdtfChanger object creation.
        """
        self._callback = _callback
        self._listOfFoundObjs = _listOfFoundObjs
        self.started = False
        self.panel = None
        self.button_find = None
        self.button_next = None
        self.button_cancel = None
        self.idtf_edit = None
        if not _manual: self.start()

    def __del__(self):
        if self.started:    self._destroy_idtf_edit()

    def createWidgets(self):
        """Creates edit control for identifiers for a find
        """
        self.panel = render_engine.Gui.createWidgetT("Window", "Panel",
            mygui.IntCoord(0, 0, 190, 80), mygui.Align(),
            "Info", "")
        assert self.idtf_edit is None
        self.idtf_edit = self.panel.createWidgetT("Edit", "Edit",
            mygui.IntCoord(10, 10, 170, 30), mygui.Align())

        self.button_find = self.panel.createWidgetT("Button", "Button", mygui.IntCoord(15, 50, 45, 20), mygui.Align())
        self.button_find.setCaption("Find")

        self.button_next = self.panel.createWidgetT("Button", "Button", mygui.IntCoord(65, 50, 45, 20), mygui.Align())
        self.button_next.setCaption("Next")

        self.button_cancel = self.panel.createWidgetT("Button", "Button", mygui.IntCoord(115, 50, 60, 20), mygui.Align())
        self.button_cancel.setCaption("Cancel")

        # subscribing events
        self.idtf_edit.subscribeEventSelectAccept(self, '_findNext')
        self.button_find.subscribeEventMouseButtonClick(self, '_findNext')
        self.button_next.subscribeEventMouseButtonClick(self, '_findNext')
        self.button_cancel.subscribeEventMouseButtonClick(self, '_textNoAccept')

        self.idtf_edit.setVisible(True)
        self.button_find.setVisible(True)
        self.button_next.setVisible(True)
        self.button_cancel.setVisible(True)

    def destroyWidgets(self):
        """Destroys edit control for identificators for a find
        """
        render_engine.Gui.destroyWidget(self.panel)
        self.panel = None
        self.idtf_edit = None

    def start(self):
        """Creates controls to change object identifier for a find
        """
        self.createWidgets()
        _height = render_engine.Window.height
        self.panel.setPosition(0, _height - 100)
        mygui.InputManager.getInstance().setKeyFocusWidget(self.idtf_edit)

    def _findNext(self, _widget):
        """Callback for identifier value accepted event and find a next object
        """
        self.nextNotFinish(unicode(self.idtf_edit.getCaption()), self._listOfFoundObjs)

    def _textNoAccept(self, _widget):
        """Callback for identifier editing cancel
        """
        self.finish(None)

    def finish(self, _value):
        """Finish identifier changing
        """
        self.destroyWidgets()
        #        self.object = None
        # callback
        self._callback(None, None)

    def nextNotFinish(self, _value, _listOfFoundObjs):
        """not Finish find by identifier
        """
        #        self.object = None
        # callback
        self._callback(_value, _listOfFoundObjs)
