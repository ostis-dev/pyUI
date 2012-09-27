
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
Created on 28.10.2010

@author: Denis Koronchick
'''
import suit.core.render.engine as render_engine
import suit.core.render.mygui as mygui
import scg_objects
import scg_alphabet
import suit.core.kernel

class ChoiceControl:
    
    def __init__(self, _values, _default, _parent, _event_update):
        """Constructor
        @param _values:    list of values
        @type _values:    list of strings
        @param _default:    default values (sets at creation)
        @type _default:    str
        @param _parent:    parent widget
        @type _parent:    mygui.Widget
        @param _event_update:    function to call on update. Need to return bool value.
                                True - type successfully changed, else - False 
        @type _event_update:    function
        """
        self.values = _values
        self.default = _default
        self.panel = None
        self.parent = _parent
        self.widgets = []
        self.event_update = _event_update
        self.selection = None
        
        self.width = 105
        
        self._createWidget()
    
    def delete(self):
        self._destroyWidget()
    
    def _createWidget(self):
        """Creates panel widget
        """
        self.panel = self.parent.createWidgetT("Window", "StaticImage", mygui.IntCoord(5, 5, 10, 10),
                                                       mygui.Align())
        self._create_value_widgets()
        
    def _destroyWidget(self):
        """Destroys panel widget
        """
        redner_engine.Gui.destroyWidget(self.panel)
        self.panel = None
        
    def _create_value_widgets(self):
        """Creates widgets for values
        """
        
        # sort values
        self.values = sorted(self.values)
        self.selection = self.default
        
        for value in self.values:
            widget = self.panel.createWidgetT("Button", "Button", 
                                              mygui.IntCoord(15, (len(self.widgets)* 20 + 10), self.width - 20, 20),
                                              mygui.Align())
            widget.setUserString("value", value)
            widget.setCaption(value)
            self.widgets.append(widget)
            
            if value == self.default:
                widget.setStateCheck(True)
                
            widget.subscribeEventMouseButtonClick(self, '_onTypeClick')
            
        self.panel.setSize(self.width, len(self.widgets) * 20 + 20)
        
    def _destroy_value_widgets(self):
        """Destroys value widgets
        """
        for widget in self.widgets:
            render_engine.Gui.destroyWidget(widget)
            
    def _onTypeClick(self, widget):
        """Event listener for type button click
        """
        old_value = self.selection
        self.selection = widget.getUserString("value")
        
        if not self.event_update():
            self.selection = old_value
            return
                
        for _widg in self.widgets:
            _widg.setStateCheck(self.selection == _widg.getUserString("value"))
            
class TypeChanger:
    
    def __init__(self, _object, _callback_del):
        """Constructor
        @param _object:    object for type changing
        @type _object:    SCgObject
        @param _callback_del:    functions that calls on dialog deletion
        @type _callback_del:    function
        """
        self.panel = None
        self.button_ok = None
        self.button_cancel = None
        self.object = _object
        self.old_type = str(_object.getType())
        self.controls = []
        self.callback_del = _callback_del
    
        self.createPanel()
        
    def delete(self):
        self.destroyPanel()
        self.callback_del()
    
    def createPanel(self):
        """Creates main panel
        """
        assert self.panel is None
        self.panel = render_engine.Gui.createWidgetT("Window", "Panel", mygui.IntCoord(0, 0, 10, 10), 
                                                     mygui.Align(), "Info", "")
        self.button_ok = self.panel.createWidgetT("Button", "Button", mygui.IntCoord(10, 0, 50, 20), mygui.Align())
        self.button_cancel = self.panel.createWidgetT("Button", "Button", mygui.IntCoord(10, 0, 50, 20), mygui.Align())
        
        self.button_ok.setCaption("Ok")
        self.button_cancel.setCaption("Cancel")
        
        self.button_ok.subscribeEventMouseButtonClick(self, '_onButtonOkClick')
        self.button_cancel.subscribeEventMouseButtonClick(self, '_onButtonCancelClick')
        
        self.panel.setVisible(False)
        
        
    def destroyPanel(self):
        """Destroys main panel
        """
        render_engine.Gui.destroyWidget(self.panel)
        self.panel = None
        self.button_ok = None
        self.button_cancel = None
        
    def run(self):
        """Runs type changing dialog
        """
        split_old_type = self.old_type.split("/")
        types_list = None
        
        if isinstance(self.object, scg_objects.SCgNode):
            types_list = scg_alphabet.get_node_types()
        elif isinstance(self.object, scg_objects.SCgPair):
            types_list = scg_alphabet.get_pair_types()
        else:
            raise Exception("Unknown object type %s" % str(self.object))
        
        assert len(types_list) > 0
        
        split_types = []        
        for _type in types_list:
            split_types.append(_type.split("/"))
        
        # parse possible values and create controls for changing them
        for idx in xrange(0, len(split_types[0])):
            values = []
            for _type in split_types:
                if not _type[idx] in values:
                    values.append(_type[idx])
            
            ctrl = ChoiceControl(values, split_old_type[idx], self.panel, self.updateType)
            
            self.controls.append(ctrl)
            
        # layout created controls
        height = 5
        
        for ctrl in self.controls:
            ctrl.panel.setPosition(3, height)
            height += ctrl.panel.getHeight() + 5
            width = ctrl.panel.getWidth()
        
        self.button_ok.setPosition(10, height + 10)
        self.button_cancel.setPosition(65, height + 10)
        
        pos = render_engine.pos3dTo2dWindow(self.object.getPosition() + self.object.getScale() / 2)
        # make some offset
        width += 20
        height += 45   
        self.panel.setSize(width, height)
        
        # sure that dialog isn't placed out of screen  
        x, y = pos
        x2 = x + width
        y2 = y + height
        
        if x2 >= render_engine.Window.width:
            x = render_engine.Window.width - width
        elif x < 0:
            x = 0
            
        if y2 >= render_engine.Window.height:
            y = render_engine.Window.height - height
        elif y < 0:
            y = 0    
        
        self.panel.setPosition(x, y)
        
        # show panel
        self.panel.setVisible(True)
        
    def updateType(self):
        """Notification on type update
        """
        # building type
        _type = ""
        for ctrl in self.controls:
            _type = _type + ctrl.selection + "/"
        _type = _type[:-1]
        
        if scg_alphabet.elementsDescMap.has_key(_type):
            scg_alphabet.changeObjectType(self.object, _type)
            return True
        
        return False
        
    def _onButtonOkClick(self, widget):
        self.delete()
    
    def _onButtonCancelClick(self, widget):
        scg_alphabet.changeObjectType(self.object, self.old_type)
        self._onButtonOkClick(widget)

   
###########################################################
### Content changing
###########################################################

class ContentChanger:
    
    def __init__(self, _node, _callback_del):
        """Constructor
        
        @param _node:    SCg-node to change content
        @type _node:    SCgNode
        @param _callback_del:    functions that calls on dialog deletion
        @type _callback_del:    function
        """
        self.panel = None
        self.types_list = None
        self.object = _node
        self._formats = {}  # map of formats, key: format name, value: (format sc_addr, edit support)
        self.button_ok = None
        self.button_cancel = None
        self.checkbox_edit = None
        self.sel_fmt = None     # selected format title
        
        self.callback_del = _callback_del
        
        self.width = 250
        self.height = 250
        
        self.createPanel()
        
    def delete(self):
        self.destroyPanel()
        self.callback_del()
        
    def createPanel(self):
        """Create controls panel
        """
        assert self.panel is None
        
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
        
        self.checkbox_edit = self.panel.createWidgetT("Button", "CheckBox", mygui.IntCoord(10, 185, self.width - 20, 22), mygui.Align())
        self.checkbox_edit.setCaption("Create editor")
        self.checkbox_edit.setStateCheck(False)
        self.checkbox_edit.setEnabled(False)
        
        self.checkbox_edit.subscribeEventMouseButtonClick(self, "_onCheckBox")
        
        self.panel.setVisible(False)
    
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
        pos = render_engine.pos3dTo2dWindow(self.object.getPosition() + self.object.getScale() / 2)
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
        for title in self._formats.iterkeys():
            self.types_list.addItem(title)
            
        self.types_list.clearIndexSelected()
        
    def item_selected(self, _widget, _idx):
        """Event handler for types list selection change 
        """
        # get item title
        self.sel_fmt = str(self.types_list.getItemNameAt(_idx))
        
        # enable "ok" button if any item selected
        self.button_ok.setEnabled(True)
        # update editor checkbox
        self.checkbox_edit.setStateCheck(False)
        self.checkbox_edit.setEnabled(self._formats[self.sel_fmt][1])
        
    def _onCheckBox(self, widget):
        """Event handler for check box clicking
        """
        widget.setStateCheck(not widget.getStateCheck())
        
    def _onButtonOkClick(self, widget):
        """Event handler for "Ok" button
        """
        if self.sel_fmt is not None:
            import scg_utils
            scg_utils.createWindowFromNode(self.object,
                                           self._formats[self.sel_fmt][0],
                                           self.checkbox_edit.getStateCheck())
        
        self.delete()
    
    def _onButtonCancelClick(self, widget):
        """Event handler for Cancel button
        """
        self.delete()