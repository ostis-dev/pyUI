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
import os, math
import suit.core.kernel as core
import suit.core.keynodes as keynodes

_window_panel = None

_version_   =   "0.2.0"
_name_      =   "WindowPanel"

def initialize():
    global _window_panel
    
    _window_panel = WindowPanel()
    core.windows_panel = _window_panel 

def shutdown():
    
    global _window_panel
    _window_panel.delete()
    _window_panel = None
    

class WindowPanel:
    """Class that realize window panel
    """
    def __init__(self):
        
        self.height = 38    # constant depend on skin
        self.buttonSize = (56, 56)  # constant depend on skin size
        self.scrollOffset = 0     # scroll offset
        self.scrollSpeed = 300   # scroll speed (pixels/seconds)
        self.scrollStep = 150    # scrolling step (one click on scroll button)
        
        self.needScrollOffset = 0     # need offset of buttons
        
        self.back = None
        self.buttonLeft = None
        self.buttonRight = None
        self.buttonContainer = None # container that contain buttons
        
        self.buttons = []
        
        self.createControls()
        self.windows_list = WindowListPanel()    # control to work with list of windows
        self.addr2widget = {}       # map to translate sc_addr to button widget
        self.widget2addr = {}       # map to translate button widget to sc_addr
        
        core.Kernel.getSingleton().addUpdateListener(self)
          
    def __del__(self):
        pass
    
    
    def createControls(self):
        """Create controls that will used by panel
        """
        
        self.back = render_engine.Gui.createWidgetT("Window", "WindowPanel_Back",
                                                    mygui.IntCoord(0, render_engine.Window.height - self.height,
                                                                   render_engine.Window.width, self.height),
                                                    mygui.Align(),
                                                    "Popup")
        
        
        self.buttonRight = render_engine.Gui.createWidgetT("Button", "ScrollButton_Right",
                                                           mygui.IntCoord(render_engine.Window.width - 49, render_engine.Window.height - 49,
                                                                          44, 44),
                                                           mygui.Align(),
                                                           "Popup")
        self.buttonLeft = render_engine.Gui.createWidgetT("Button", "ScrollButton_Left",
                                                           mygui.IntCoord(5, render_engine.Window.height - 49,
                                                                          44, 44),
                                                           mygui.Align(),
                                                           "Popup")
        self.buttonRight.setEnabled(False)
        self.buttonLeft.setEnabled(False)
        
        self.buttonLeft.subscribeEventMouseButtonClick(self, "_onScrollLeft")
        self.buttonRight.subscribeEventMouseButtonClick(self, "_onScrollRight")
        
        self.buttonContainer = render_engine.Gui.createWidgetT("Window", "WindowPanel_Container",
                                                               mygui.IntCoord(55, render_engine.Window.height - self.buttonSize[1],
                                                                              render_engine.Window.width - 110, self.buttonSize[1]),
                                                               mygui.Align(),
                                                               "Popup")
   
    def delete(self):
        """Deletes window panel
        """
        core.Kernel.getSingleton().removeUpdateListener(self)
        if self.windows_list:
            self.windows_list.delete()
    
    def getFormatIcon(self, _format):
        """Return icon associated with specified format
        @param _format: sc-node that designate format
        @type _format: sc_addr
        
        @return: Name of texture that contains icon associated to _format, if there are no any
                icons, then return None
        """
        import suit.core.sc_utils as sc_utils
        import sc_core.constants as sc_constants
        import sc_core.pm as sc
        import ogre.renderer.OGRE as ogre
        
        session = core.Kernel.session()
        
        icon = None
        idtf_set = sc_utils.searchOneShotBinPairAttrToNode(session, _format, keynodes.common.nrel_identification, sc.SC_CONST)
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
            
            icon_name = "icon_%s" % str(_format)
            ogre.TextureManager.getSingleton().loadImage(icon_name, "General", img)
            return icon_name
            
        
        return None
    
    def addButton(self, _format):
        """Adds button to panel
        @param _format:    sc-node that designate format associated with button
        @type _format:    sc_addr
        """
        button = self.buttonContainer.createWidgetT("Button", "WindowPanel_Button",
                                                    mygui.IntCoord(self.scrollOffset + self.buttonSize[0] * len(self.buttons), 2,
                                                                   self.buttonSize[0], self.buttonSize[1]),
                                                    mygui.Align())
        icon = button.createWidgetT("StaticImage", "StaticImage",
                                         mygui.IntCoord(10, 8, button.getWidth() - 20, button.getHeight() - 20),
                                         mygui.Align())
        icon.setNeedKeyFocus(False)
        icon.setNeedMouseFocus(False)
        icon_name = self.getFormatIcon(_format)
        if icon_name is not None:
            icon.setImageTexture(icon_name)
            
        self.buttons.append(button)
        button.setUserString("id", str(button))
        # subscribing click event
        button.subscribeEventMouseButtonClick(self, '_onButtonClick')        
        self.addr2widget[str(_format)] = button
        self.widget2addr[str(button)] = _format
        
        self.updateButtonsPosition()
        self.updateScrollButtons()
        
    def removeButton(self, _format):
        """Remove button from panel
        @param _format:  sc-node that designate format associated with button
        @type _format: sc_addr
        """
        pass
        
    def updateScrollButtons(self):
        """Updates scroll buttons state
        """
        self.buttonLeft.setEnabled(self.isScrollableLeft())
        self.buttonRight.setEnabled(self.isScrollableRight())
        
    def updateButtonsPosition(self):
        """Updates buttons position
        """ 
        idx = 0
        for button in self.buttons:
            button.setPosition(int(self.scrollOffset + idx * self.buttonSize[0]), button.getTop())
            idx += 1
            
    def _update(self, timeSinceLastFrame):
        """Update notification
        @param timeSinceLastFrame:    time since last update in ms
        @type timeSinceLastFrame:    float
        """
        dOffset = self.needScrollOffset - self.scrollOffset
        if math.fabs(dOffset) > 1:
            if dOffset > 0:
                self.scrollOffset += self.scrollSpeed * timeSinceLastFrame
            elif dOffset < 0:
                self.scrollOffset -= self.scrollSpeed * timeSinceLastFrame
            self.updateButtonsPosition()
            self.updateScrollButtons() 
            
    def normalizeNeedScrollOffset(self):
        """Makes needScrollOffset value in range between left and right borders of panel
        """
        if self.needScrollOffset > 0:
            self.needScrollOffset = 0
        
        offset = (self.needScrollOffset + len(self.buttons) * self.buttonSize[0])
        if offset < self.buttonContainer.getWidth():
            self.needScrollOffset += self.buttonContainer.getWidth() - offset
        
    
    def isScrollableLeft(self):
        """Check if buttons can be scrolled to left
        
        @return: if buttons can be scrolled to left, then return True, else - False
        """
        return self.scrollOffset < 0
    
    def isScrollableRight(self):
        """Check if buttons can be scrolled to right
        
        @return: if buttons can be scrolled to right, then return True, else - False
        """
        return (self.scrollOffset + len(self.buttons) * self.buttonSize[0]) > self.buttonContainer.getWidth()
    
    def _onScrollLeft(self, widget):
        """Scrolls buttons to left
        """
        if not self.isScrollableLeft():
            return
        
        self.needScrollOffset += self.scrollStep
        self.normalizeNeedScrollOffset()
        
    def _onScrollRight(self, widget):
        """Scrolls buttons to right
        """
        if not self.isScrollableRight():
            return
        
        self.needScrollOffset -= self.scrollStep
        self.normalizeNeedScrollOffset()
        
    def _onButtonClick(self, widget):
        """Show/hide list of windows
        """
        _format = self.widget2addr[widget.getUserString("id")]
        show = False
        if self.windows_list is not None and self.windows_list.format is not None and self.windows_list.format.this == _format.this:
            show = not self.windows_list.isVisible()
        else:
            show = True
            
        # update buttons alpha
        alpha = 1.0
        if show:
            alpha = 0.5
        for button in self.buttons:
            button.setAlpha(alpha)
                    
        if show:
            pos = widget.getAbsolutePosition()
            self.windows_list.show(_format, pos.left, pos.top)
            widget.setAlpha(1.0)
        else:
            self.windows_list.hide()
            
            
        
class WindowListPanel:
    
    def __init__(self, pos = (0, 0)):
        """Constructor
        """
        self.format = None
        self.back = None
        self.buttonContainer = None
        self.head_text = None
        self.pos = None     # (x,y)
        self.size = None    # (width, heoght)
        self.buttons = []
        self.button_height = 25 # height of list button
        self.button_offset = 3  # distance between buttons
        self.head_text_height = 20 # height of header
        
        self.widget2addr = {}   # map for converting widgets to sc_addrs
    
    def delete(self):
        """Delete windows panel and free memory
        """
        if self.back is not None:
            self.destroyControls()
    
    def createControls(self):
        """Create controls
        """
        self.back = render_engine.Gui.createWidgetT("Window", "Panel",
                                                    mygui.IntCoord(0, 0, 10, 10),
                                                    mygui.Align(),
                                                    "Popup")
        self.buttonContainer = self.back.createWidgetT("ScrollView", "ScrollView",
                                                       mygui.IntCoord(0, 0, 0, 0),
                                                       mygui.Align())
        self.head_text = self.back.createWidgetT("StaticText", "StaticTextHead", mygui.IntCoord(0, 0, 0, 0), mygui.Align())
        
        self.back.setVisible(False)
        #self.back.setAlpha(0.8)
        
    def destroyControls(self):
        """Destroys controls
        """
        render_engine.Gui.destroyWidget(self.back)
        self.back = None
    
    def show(self, _format, x, y):
        """Shows list of windows
        @param _format: sc-node that designate specified format
        @type _format: sc_addr  
        @param x: coordinates of window
        @type x: int 
        @param y: coordinates of window
        @type y: int 
        @note: Coordinates will be moved to best position, depending on screen size  
        """
        self.format = _format
        if self.back is None:
            self.createControls()
        
        self.head_text.setCaption(unicode(core.Kernel.session().get_idtf(self.format)))   
        
        self.updateList()
        self.back.setPosition(x, y)
        self.pos = (x, y)
        self.updateBounds()
        self.updateButtons()       
        
        self.back.setVisible(True)
        
    def updateList(self):
        """Updates list of windows
        """
        # remove old buttons
        self.clearList()
        
        # get output arcs from format
        import sc_core.constants, sc_core.pm
        import suit.core.sc_utils as sc_utils
        session = core.Kernel.session()
        
        it = session.create_iterator(session.sc_constraint_new(sc_core.constants.CONSTR_3_f_a_a,
                                                               self.format,
                                                               sc_core.pm.SC_A_CONST,
                                                               sc_core.pm.SC_N_CONST), True)
        while not it.is_over():
            # check if founded node designate sc-window
            if sc_utils.checkIncToSets(session, it.value(2), [keynodes.ui.sc_window], sc_core.pm.SC_A_CONST):
                button = self.buttonContainer.createWidgetT("Button", "Button", mygui.IntCoord(0, 0, 0, 0), mygui.Align())
                button.setCaption(unicode(session.get_idtf(it.value(2))))
                button.subscribeEventMouseButtonClick(self, '_onButtonClick')
                
                id = str(button)
                button.setUserString("id", id)
                self.widget2addr[id] = it.value(2)
                
                button.setStateCheck(core.Kernel.getSingleton().haveOutputWindow(it.value(2)))
                
                self.buttons.append(button)       
            it.next()
            
    def clearList(self):
        """Clears buttons list
        """
        for button in self.buttons:
            render_engine.Gui.destroyWidget(button)
        self.buttons = []
            
    def updateButtons(self):
        """Update buttons positions and size
        """
        idx = 0
        for button in self.buttons:
            button.setPosition(2, idx * (self.button_height + self.button_offset) + 3)
            button.setSize(self.size[0] - 48, self.button_height)
            idx += 1
        
        
    def updateBounds(self):
        """Update bounds of panel.
        Calculates size and position for a panel. 
        """
        self.size = (250, 200)
        self.back.setSize(self.size[0], self.size[1])
        self.back.setPosition(self.pos[0], self.pos[1] - self.size[1])
        self.head_text.setPosition(5, 5)
        self.head_text.setSize(self.size[0] - 10, self.head_text_height)
        self.buttonContainer.setPosition(5, 5 + self.head_text_height)
        self.buttonContainer.setSize(self.size[0] - 10, self.size[1] - 10 - self.head_text_height)
        self.buttonContainer.setCanvasSize(210, (self.button_height + 3) * len(self.buttons) + 10)
        
    def hide(self):
        """Hide list of windows
        """
        self.back.setVisible(False)
        
    def isVisible(self):
        """Check if list is visible
        """
        if self.back is None:
            return False
        return self.back.isVisible()
    
    def _onButtonClick(self, widget):
        """Event handler for list item click
        """
        widget.setStateCheck(not widget.getStateCheck())
        id = widget.getUserString("id")
        _window = self.widget2addr[id]
        
        if widget.getStateCheck():
            core.Kernel.getSingleton().addOutputWindow(_window)
        else:
            core.Kernel.getSingleton().removeOutputWindow(_window)