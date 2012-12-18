
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
Created on 02.01.2010

@author: Denis Koronchik
'''
import suit.core.render.engine as render_engine
import suit.core.render.mygui as mygui


class TextInput:
    """Class that realize text value input
    """    
    def __init__(self, _obj, _callback, _default_value = None, _manual = False):
        """Constructor
        @param _obj: object to change text property for
        @type _obj: objects.ObjectDepth
        @param _callback: function that will be called when value
        input finished. This function takes two parameters - object, text value.
        @type _callback: function
        @param _manual: flag to start changing manually. If it is True, then 
        user will be need to call start function manually, else it will be called
        automatically on IdtfChanger object creation.     
        """ 
        self.object = _obj
        self._callback = _callback
        self.started = False
        self.panel = None
        self.button_ok = None
        self.button_cancel = None
        self.idtf_edit = None
        self.default_value = _default_value
        if not _manual: self.start()
        
    def __del__(self):
        if self.started:    self._destroy_idtf_edit()
        
    def createWidgets(self):
        """Creates edit control for identifiers
        """        
        self.panel = render_engine.Gui.createWidgetT("Window", "Panel",
                                                     mygui.IntCoord(0, 0, 140, 80), mygui.Align(),
                                                     "Info", "")
        assert self.idtf_edit is None
        self.idtf_edit = self.panel.createWidgetT("Edit", "Edit", 
                                                  mygui.IntCoord(10, 10, 120, 30), mygui.Align())
        
        self.button_ok = self.panel.createWidgetT("Button", "Button", mygui.IntCoord(15, 50, 45, 20), mygui.Align())
        self.button_ok.setCaption("Ok")
        
        self.button_cancel = self.panel.createWidgetT("Button", "Button", mygui.IntCoord(65, 50, 60, 20), mygui.Align())
        self.button_cancel.setCaption("Cancel")
        
        # subscribing events
        self.idtf_edit.subscribeEventSelectAccept(self, '_textAccept')
        self.button_ok.subscribeEventMouseButtonClick(self, '_textAccept')
        self.button_cancel.subscribeEventMouseButtonClick(self, '_textNoAccept') 
        
        self.idtf_edit.setVisible(True)
        self.button_ok.setVisible(True)
        self.button_cancel.setVisible(True)
        
    def destroyWidgets(self):
        """Destroys edit control for identificators
        """
        render_engine.Gui.destroyWidget(self.panel)
        self.panel = None
        self.idtf_edit = None        
        
    def start(self):
        """Creates controls to change object identifier
        """
        self.createWidgets()
        pos = render_engine.pos3dTo2dWindow(self.object.getPosition() + self.object.getScale() / 2)
        if pos is not None:
            self.panel.setPosition(pos[0], pos[1])
            # set old text to edit
#            text_value = self.object.getText()
            if self.default_value is not None: self.idtf_edit.setCaption(str(self.default_value))
            mygui.InputManager.getInstance().setKeyFocusWidget(self.idtf_edit)
        else:
            self.destroyWidgets()
            
    def _textAccept(self, _widget):
        """Callback for identifier value accepted event
        """
        self.finish(unicode(self.idtf_edit.getCaption()))
        
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
        self._callback(self.object, _value)
