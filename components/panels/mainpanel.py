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
Created on 15.08.2010

@author: Denis Koronchik
@version: 0.1
'''

import suit.core.render.engine as render_engine
import suit.core.render.mygui as mygui
import suit.core.kernel as core
import suit.core.keynodes as keynodes
import suit.core.objects as objects
import sc_core.pm, sc_core.constants
import suit.core.sc_utils as sc_utils
from suit.core.event_handler import ScEventHandlerSetMember
from suit.core.event_handler import ScEventHandlerDie
import thread
import os, math

_main_panel = None
_output_window_set = None

_version_   =   "0.1.0"
_name_      =   "MainPanel"

def initialize():
    global _main_panel
    
    _main_panel = MainPanel()
    _main_panel.setVisible(True)
    _main_panel.setEnabled(True)
    
    kernel = core.Kernel.getSingleton()
    # register operation
    kernel.registerOperation(ScEventHandlerSetMember(u"операция отображения новых окон для вывода", 
                                                     keynodes.ui.set_output_windows,
                                                     _main_panel.addOutputWindow, []))
def shutdown():
    
    global _main_panel
    _main_panel.delete()
    _main_panel = None
    

class IconButton(objects.ObjectOverlay):
    
    def __init__(self):
        objects.ObjectOverlay.__init__(self)
        
        self.needIconUpdate = False
        self.iconWidget = None
        
    def __del__(self):
        objects.ObjectOverlay.__del__(self)
        
    def delete(self):
        objects.ObjectOverlay.delete(self)
        
#        if self.iconWidget is not None:
#            render_engine.Gui.destroyWidget(self.iconWidget)
#            self.iconWidget = None
            
#        if self._widget is not None:
#            render_engine.Gui.destroyWidget(self._widget)
#            self._widget = None
        
    def _updateView(self):
        objects.ObjectOverlay._updateView(self)
        
        if self.needIconUpdate:
            self._updateIcon()
            self.needIconUpdate = False
            
    def _updateIcon(self):
        """Updates button icon based in image identifier
        """
        if self._getScAddr() is None: # do nothing
            return
        
        icon_name = self.getIcon()
        
        if icon_name is None:
            return
        
        self.iconWidget.setImageTexture(icon_name)
        
    def _setScAddr(self, _addr):
        objects.ObjectOverlay._setScAddr(self, _addr)
        
        self.needIconUpdate = True
        self.needViewUpdate = True
    
    def getIconAddr(self):
        """Return sc-addr of element that will be used to get image identifier
        """
        return None
        
    def getIcon(self):
        """Return icon associated with specified icon addr
        
        @return: Name of texture that contains icon associated to _format, if there are no any
                icons, then return None
        """
        import suit.core.sc_utils as sc_utils
        import sc_core.constants as sc_constants
        import sc_core.pm as sc
        import ogre.renderer.OGRE as ogre
        
        session = core.Kernel.session()
        
        addr = self.getIconAddr()
        assert addr is not None
        icon_name = "icon_%s" % str(addr.this)
        
        # check if icon already loaded
        if ogre.TextureManager.getSingleton().getByName(icon_name) is not None:
            return icon_name
        
        icon = None
        idtf_set = sc_utils.searchOneShotBinPairAttrToNode(session, addr, keynodes.common.nrel_identification, sc.SC_CONST)
        if idtf_set is not None:
            
            it1 = session.create_iterator(session.sc_constraint_new(sc_constants.CONSTR_3_f_a_a,
                                                                   idtf_set,
                                                                   sc.SC_A_CONST,
                                                                   sc.SC_N_CONST), True)
            while not it1.is_over():
                if sc_utils.checkIncToSets(session, it1.value(2), [keynodes.common.group_image], sc.SC_CONST):
                    icon = it1.value(2)
                    break                 
                it1.next()
            
            if icon is None:
                return None
            
            _fmt = sc_utils.getContentFormat(session, icon)
            assert _fmt is not None
    
            _cont = session.get_content_const(icon)
            assert _cont is not None
    
            _cont_data = _cont.convertToCont()
    
            data = _cont.get_data(_cont_data.d.size)
            stream = ogre.MemoryDataStream("%s" % str(self), _cont_data.d.size, False)
            stream.setData(data)
    
            try:
                img = ogre.Image()
                img.load(stream, ogre.Image.getFileExtFromMagic(stream))
            except:
                import sys, traceback
                print "Error:", sys.exc_info()[0]
                traceback.print_exc(file=sys.stdout)
            
            ogre.TextureManager.getSingleton().loadImage(icon_name, "General", img)
            return icon_name
        
        return None
    
    

class MainPanelButton(IconButton):
    
    def __init__(self):
        IconButton.__init__(self)
        
        self._widget = render_engine.Gui.createWidgetT("Button", "MainPanel_Button",
                                                       mygui.IntCoord(0, 0, 0, 0),
                                                       mygui.Align(),
                                                       "Popup")
        self.autoSize = False
        
        self.iconWidget = self._widget.createWidgetT("StaticImage", "StaticImage",
                                                     mygui.IntCoord(0, 0, 10, 10),
                                                     mygui.Align())
        self.iconWidget.setNeedKeyFocus(False)
        self.iconWidget.setNeedMouseFocus(False)
               
    def __del__(self):
        IconButton.__del__(self)
        
    def delete(self):
        IconButton.delete(self)
            
    def _updateScale(self):
        IconButton._updateScale(self)
        
        # calculate icon size as 2/3 * button_size
        scale = self.getScale()
        icon_scale = (scale[0] * 2 / 3.0, scale[1] * 2 / 3.0)
        
        self.iconWidget.setPosition(int((scale[0] - icon_scale[0]) / 2.0),
                                    int((scale[1] - icon_scale[1]) / 2.0))
        self.iconWidget.setSize(int(icon_scale[0]), int(icon_scale[1]))
    
    def getIconAddr(self):
        return self._getScAddr()
    
        
class OutputWindowButton(IconButton):
    
    def __init__(self):
        IconButton.__init__(self)
        
        self._widget = render_engine.Gui.createWidgetT("Button", "MainPanel_OutputWindowButton",
                                                       mygui.IntCoord(0, 0, 0, 0),
                                                       mygui.Align(),
                                                       "Popup")
        self.autoSize = False
        
        self.iconWidget = self._widget.createWidgetT("StaticImage", "StaticImage",
                                                     mygui.IntCoord(0, 0, 10, 10),
                                                     mygui.Align())
        self.iconWidget.setNeedKeyFocus(False)
        self.iconWidget.setNeedMouseFocus(False)
        
        self.deleteControl = render_engine.Gui.createWidgetT("Button", "MainPanel_OutputWindowDelButton",
                                                             mygui.IntCoord(0, 0, 20, 20),
                                                             mygui.Align(),
                                                             "Popup")
        self.deleteControl.setVisible(False)
        self.deleteControl.subscribeEventMouseButtonClick(self, '_onDeleteButtonClicked')
        
        # handler for window deletion from output set
        self.deleteHandler = None
        
        self.setScale((70, 80))
        
    def __del__(self):
        IconButton.__del__(self)
        
    def delete(self):
        IconButton.delete(self)
        
        if self.deleteControl is not None:
            render_engine.Gui.destroyWidget(self.deleteControl)
            self.deleteControl = None
        
        #if self.deleteHandler is not None:
            #kernel = core.Kernel.getSingleton()
            #kernel.unregisterOperation(self.deleteHandler)
            # FIXME: this line crashes code
            #self.deleteHandler = None
        
    def getIconAddr(self):
        return sc_utils.getContentFormat(core.Kernel.session(), self._getScAddr())
    
    def _setScAddr(self, _addr):        
        IconButton._setScAddr(self, _addr)
        
        kernel = core.Kernel.getSingleton()
        # FIXME
#        if self.deleteHandler is not None:
#            kernel.unregisterOperation(self.deleteHandler)
#            self.deleteHandler = None
            
        if _addr is None: # do nothing
            return
            
        session = kernel.session()
        pair = session.search_one_shot(session.sc_constraint_new(sc_core.constants.CONSTR_3_f_a_f,
                                                                 keynodes.ui.set_output_windows,
                                                                 sc_core.pm.SC_A_CONST,
                                                                 _addr), True, 3)
        assert pair is not None
            
#        self.deleteHandler = ScEventHandlerDie(u"операция удаления окна для вывода %s" % str(_addr), 
#                                               pair[1],
#                                               self._processDeletion, [])# register operation
#        kernel.registerOperation(self.deleteHandler)
        
    
    def _updateShow(self):
        IconButton._updateShow(self)
        
        self.deleteControl.setVisible(self.isVisible())
    
    def _updatePosition(self):
        IconButton._updatePosition(self)
        
        pos = self.getPosition()
        scale = self.getScale()
        
        x = pos[0] + scale[0] - self.deleteControl.getWidth() / 2.0 - 4
        y = pos[1] - self.deleteControl.getHeight() / 2.0 + 4
        self.deleteControl.setPosition(int(x), int(y))
    
    def _updateScale(self):
        IconButton._updateScale(self)
        
        # calculate icon size as 4/5 * button_size
        scale = self.getScale()
        icon_scale = (scale[0] * 4 / 5.0, scale[1] * 4 / 5.0)
        
        self.iconWidget.setPosition(int((scale[0] - icon_scale[0]) / 2.0),
                                    int((scale[1] - icon_scale[1]) / 2.0))
        self.iconWidget.setSize(int(icon_scale[0]), int(icon_scale[1] - 10))
        
    def _onDeleteButtonClicked(self, widget):
        """Processing window deletion from output set 
        """
        assert self._getScAddr() is not None
        
        core.Kernel.getSingleton().removeOutputWindow(self._getScAddr())
        _main_panel.removeOutpuWindow(self._getScAddr())
        
    def _processDeletion(self, _params, _segement):
        _main_panel.removeOutpuWindow(self._getScAddr())
        
class MainPanel(objects.ObjectOverlay):
    """Class that realize window panel
    """
    def __init__(self):
        objects.ObjectOverlay.__init__(self)
        
        self.corner_size = (103, 103)
        self.buttonsStack = []
        self.buttonsOffsets = [(-160, -55), (-127, -104), (-83, -133), (-38, -145)]
        self.buttonsSizes = [(64, 64), (56, 56), (48, 48), (40, 40)]
        
        self.toolsLine = None
        self.toolsLineLength = 10
        self.needToolsLineUpdate = True
        self.needButtonsUpdate = True
        self.needOutputButtonsUpdate = True
        
        self._addOutputWindowQueue = []
        self._removeOutputWindowQueue = []
        self._queueLock = thread.allocate_lock()
        
        self.outputWindowWidgets = []
        
        self.createControls()
          
         
    def __del__(self):
        objects.ObjectOverlay.__del__(self)
        
    def delete(self):
        objects.ObjectOverlay.__del__(self)
        self.destroyControls()
        
        windows = [] + self.outputWindowWidgets
        for window in windows:
            window.delete()
    
    def createControls(self):
        """Create widgets that need to control ui
        """
        pos = (render_engine.Window.width - self.corner_size[0],
               render_engine.Window.height - self.corner_size[1])
        self._widget = render_engine.Gui.createWidgetT("Window", "MainPanel_Corner",
                                                       mygui.IntCoord(pos[0], pos[1], self.corner_size[0], self.corner_size[1]),
                                                        mygui.Align(),
                                                        "Popup")
        self.setPosition(pos)
        self.setScale(self.corner_size)
        self.setVisible(False)
        self.setEnabled(True)
        
        self.toolsLine = render_engine.Gui.createWidgetT("Window", "MainPanel_ToolsLine",
                                                         mygui.IntCoord(0, 0, 0, 0),
                                                         mygui.Align(),
                                                         "Popup")
        self.setVisible(False)
        self.setEnabled(False)
        
        # create buttons
        buttonWindows = MainPanelButton()
        buttonWindows._setScAddr(keynodes.ui.set_output_windows)
        buttonWindows.setVisible(True)
        buttonWindows.setEnabled(True)
        self.appendButton(buttonWindows)
        
    def destroyControls(self):
        """Destroy all created controls
        """
        if self._widget is not None:
            render_engine.Gui.destroyWidget(self._widget)
            self._widget = None
            
        if self.toolsLine is not None:
            render_engine.Gui.destroyWidget(self.toolsLine)
            self.toolsLine = None
            
    def appendButton(self, button):
        """Appends new button into stack
        @param button: New button object
        @type button:  MainPanelButton
        """
        if button in self.buttonsStack:
            raise Exception("Button already exist")
        
        self.buttonsStack.append(button)
        self.needButtonsUpdate = True
        self.needToolsLineUpdate = True
        self.needViewUpdate = True
    
    def _update(self, timeSinceLastFrame):
        
        # process queue for output windows adding
        if len(self._addOutputWindowQueue) > 0:
            self._queueLock.acquire()
            
            for window in self._addOutputWindowQueue:
                self._appendOutputButton(window)
                
            self._addOutputWindowQueue = []
            self._queueLock.release()
            
        if len(self._removeOutputWindowQueue) > 0:
            self._queueLock.acquire()
            
            for window in self._removeOutputWindowQueue:
                self._removeOutputButton(window)
                
            self._removeOutputWindowQueue = []
            self._queueLock.release()
        
        objects.ObjectOverlay._update(self, timeSinceLastFrame)
            
    def _updateView(self):
        if self.needShowUpdate:
            self.needToolsLineUpdate = True
            
        if self.needToolsLineUpdate:
            self._updateToolsLine()
            self.needToolsLineUpdate = False
            
        if self.needButtonsUpdate:
            self._updateButtons()
            self.needButtonsUpdate = False
            
        if self.needOutputButtonsUpdate:
            self._updateOutputButtons()
            self.needOutputButtonsUpdate = False
            
        objects.ObjectOverlay._updateView(self)
            
    def _updateToolsLine(self):
        """Update position and size of tools line
        """                
        if len(self.buttonsStack) > 0 and self.isVisible():
            self.toolsLine.setVisible(True)
        else:
            self.toolsLine.setVisible(False)
        
        realWidth = 44 + self.toolsLineLength
        self.toolsLine.setSize(realWidth, 64)
        
        self.toolsLine.setPosition(render_engine.Window.width + self.buttonsOffsets[0][0] - realWidth + 27,
                                   render_engine.Window.height + self.buttonsOffsets[0][1] - 7)
    
    def _updateButtons(self):
        """Update buttons size and position. It based on buttons stack
        """
        idx = 0
        for button in self.buttonsStack:
            
            if idx == 4:
                break
            
            button.setScale(self.buttonsSizes[idx])
            button.setPosition((render_engine.Window.width + self.buttonsOffsets[idx][0],
                               render_engine.Window.height + self.buttonsOffsets[idx][1]))
            
            idx += 1
            
    def _updateOutputButtons(self):
        """Update output buttons positions, sizes and etc.
        """
        # calculate and update tools line length
        offset = 0
        if len(self.outputWindowWidgets) > 0:
            offset = -30
        self.toolsLineLength = 75 * len(self.outputWindowWidgets) + offset
        self._updateToolsLine()
               
        idx = 0
        for button in self.outputWindowWidgets:
            pos = (self.toolsLineLength + self.toolsLine.getPosition().left - 75 * (idx + 1),
                   render_engine.Window.height - 77)
            button.setPosition(pos)
            idx += 1
        
    def _appendOutputButton(self, addr):
        """Append button for specified \p addr, that designate window
        """
        assert addr is not None
        
        widget = OutputWindowButton()
        widget._setScAddr(addr)
        widget.setEnabled(True)
        widget.setVisible(True)
        self.outputWindowWidgets.append(widget)
        
        self.needOutputButtonsUpdate = True
        self.needViewUpdate = True
        
    def _removeOutputButton(self, addr):
        """Remove control that designate output window with specified \p addr
        """
        assert addr is not None
        
        control = None
        for widget in self.outputWindowWidgets:
            if widget._getScAddr().this == addr.this:
                control = widget
                break
        
        assert control is not None
        
        self.outputWindowWidgets.remove(control)
        control.delete()
        
        self.needOutputButtonsUpdate = True
        self.needViewUpdate = True
            
    def addOutputWindow(self, _params, _segment):
        """Process output window add event
        """
        session = core.Kernel.session()

        window = session.search_one_shot(session.sc_constraint_new(sc_core.constants.CONSTR_5_f_a_a_a_f,
                                                                   keynodes.ui.set_output_windows,
                                                                   sc_core.pm.SC_A_CONST,
                                                                   sc_core.pm.SC_N_CONST,
                                                                   sc_core.pm.SC_A_CONST,
                                                                   _params), True, 5)
        assert window is not None
        window = window[2]
            
        self._queueLock.acquire()            
        self._addOutputWindowQueue.append(window)
        self._queueLock.release()
        
    def removeOutpuWindow(self, addr):
        """Appends into queue deletion of control, that designates output window with specified \p addr
        """
        
        self._queueLock.acquire()
        self._removeOutputWindowQueue.append(addr)
        self._queueLock.release()
        