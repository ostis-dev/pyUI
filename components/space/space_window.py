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
Created on 29.04.2010

@author: DerDevil
'''

import suit.core.render.mygui as mygui
import suit.core.exceptions
import suit.core.render.engine
import space_env

panel_window = None         # main window
scroll_view = None          # widget for scroll view (it contains property panels)
main_proppanel = None       # widget for main SpaceObject properties. They are common for all space objects
second_proppanel = None     # widget for other SpaceObject properties

panel_width = 300           # panel width
panel_height = 430          # panel height
panel_caption_height = 38
panel_side_width    =   45  # right side width
textOffset1 = 3
textOffset2 = 6
scroll_bar_width    =   15  # scroll bar width on scroll view
move_time   =   2     # time to move panel on hide/show

need_scroll_view_canvas_sz_update   =   False   # flag to update scroll view canvas size
need_panel_position_update          =   False

prop_panels = []            # list of all properties panels

def initialize():
    """Initialize panel.
    Calls on space module startup.
    """
    #if not mygui.SkinManager.getInstance().load(space_env.gui_skin_panel):  # skin loading
    #    raise suit.core.exceptions.ResourceLoadError("Can't load skin '%s'" % space_env.gui_skin_panel)
    
    create_window()  # creating panel
    
def shutdown():
    """Destroys panel.
    Calls on space module shutting down
    """
    # we can't unload mygui resources (not supported by mygui)
    destroy_window()

def create_window():
    """Creates window and preparing it for using
    """
    global panel_window
    assert not panel_window
    
    panel_window = suit.core.render.engine.Gui.createWidgetT("Window", "Window",
                                                              mygui.IntCoord(suit.core.render.engine.Window.width - panel_width - 5,
                                                                             35,
                                                                             panel_width, panel_height),
                                                              mygui.Align())
    panel_window.setVisible(False)     # don't show panel at startup
    panel_window.setAlpha(0.9)          # make it with small alpha
    panel_window.setCaption("Object Properties")    
    
    global scroll_view
    scroll_view = panel_window.createWidgetT("ScrollView", "ScrollView",
                                             mygui.IntCoord(0, 0, panel_width - 10, panel_height - panel_caption_height),
                                             mygui.Align())
    scroll_view.setCanvasSize(scroll_view.getSize().width - scroll_bar_width, scroll_view.getSize().height)
    
    global main_proppanel
    main_proppanel = PropertyPanel()
    main_proppanel.createPanel("Main Properties")
    main_proppanel.addPropertyWidget("Edit", "Edit", "Object Name")
    main_proppanel.addPropertyWidget("Edit", "Edit", "Year")
    main_proppanel.addPropertyWidget("Edit", "Edit", "Day")
    main_proppanel.addPropertyWidget("Edit", "Edit", "Radius")
    main_proppanel.addPropertyWidget("Edit", "Edit", "Orbital radius")
    prop_panels.append(main_proppanel)
    
    global second_proppanel
    second_proppanel = PropertyPanel(main_proppanel)
    second_proppanel.createPanel("Other Properties") 
    prop_panels.append(second_proppanel)
    
def destroy_window():
    """Destroys window
    """
    global panel_window
    global scroll_view
    assert panel_window
    suit.core.render.engine.Gui.destroyWidget(panel_window)
    panel_window = None
    scroll_view = None
    
def update(dt):
    global need_scroll_view_canvas_sz_update
    global scroll_view
    global need_panel_position_update
    for panel in prop_panels:
        if panel.needSizeUpdate:
            maxSize_y = (textOffset1 + panel.pWidget_height)*len(panel.widgets) + panel.caption_height + textOffset1
            minSize_y = panel.caption_height
            offset_y = panel.moveSpeed * move_time
            if panel.moveSpeed > 0:
                newSize_y = min([maxSize_y, panel.widget.getSize().height + offset_y])
                panel.widget.setSize(panel.widget.getSize().width,
                                     newSize_y)
                if newSize_y == maxSize_y:
                    panel.needSizeUpdate = False
            elif panel.moveSpeed < 0:
                newSize_y = max([minSize_y, panel.widget.getSize().height + offset_y])
                panel.widget.setSize(panel.widget.getSize().width,
                                     newSize_y)
                if newSize_y == minSize_y:
                    panel.needSizeUpdate = False
            need_scroll_view_canvas_sz_update = True
            need_panel_position_update = True
    if need_panel_position_update:
        for panel in prop_panels:
            if panel.prev_panel:
                panel.widget.setPosition(panel.widget.getPosition().left,
                                         panel.prev_panel.widget.getSize().height + textOffset1)
        need_panel_position_update = False
                
    if need_scroll_view_canvas_sz_update:
        canvasSize = 0
        for panel in prop_panels:
            canvasSize += panel.widget.getSize().height
        scroll_view.setCanvasSize(scroll_view.getCanvasSize().width,
                                  canvasSize)
        scroll_view.setCanvasAlign(mygui.Align(mygui.Align.Enum.Top))
        need_scroll_view_canvas_sz_update = False

def activate(space_obj):
    """Activates window. Makes it visible. 
    """
    assert panel_window
    setObjectDescr(space_obj)
    panel_window.setVisible(True)

def deactivate():
    """Deactivates window. Makes it invisible.
    """
    assert panel_window
    deleteObjectDescr()
    panel_window.setVisible(False)
        
def setObjectDescr(space_obj):    
    params = []
    params.append(space_obj.getText())
    params.append(str(space_obj.year)) 
    params.append(str(space_obj.day))
    params.append(str(space_obj.scale))
    params.append(str(space_obj.orbA))
    
    createMainProp(params)
    if(space_obj.properties):
        createOtherProp(space_obj.properties)
        
def deleteObjectDescr():
    while len(second_proppanel.widgets):
        second_proppanel.deletePropertyWidget(0)
    
def createMainProp(params):
    for i, p in enumerate(params):
        prop_value = 'None'
        if p is not None:
            prop_value = p
        main_proppanel.widgets[i].setCaption(prop_value)
        
def createOtherProp(params):
    for i, p in enumerate(params):
        if p:
            second_proppanel.addPropertyWidget("Edit", "Edit", str(p[0]))
            second_proppanel.widgets[i].setCaption(str(p[1]))
        
class PropertyPanel:
    pWidget_width = 100
    pWidget_height = 20
    caption_height = 0
    
    def __init__(self, prev = None):
        self.widget = None
        self.prev_panel = prev
        self.roll_button = None
        self.caption = None
        self.widgets = []
        self.texts = []
        self.pWidget_Y = 0
        self.needSizeUpdate = False
        self.moveSpeed = 0
        
    def __del__(self):
        """Deletion message
        """
        assert not self.widget
        print "__del__ in %s" % str(self)
        
    def delete(self):
        """Object destruction
        """
        if self.widget: 
            self.destroyPanel()
        
    def createPanel(self, string = "Panel"):
        assert scroll_view
        posY = 0
        offsetY = 0
        if self.prev_panel:
            offsetY = self.prev_panel.widget.getSize().height + 1
            posY = self.prev_panel.widget.getPosition().top
        else:
            offsetY = 0
            
        self.widget = scroll_view.createWidgetT("Window", "Panel",
                                                mygui.IntCoord(0, posY + offsetY, 
                                                          scroll_view.getCanvasSize().width,
                                                          200),
                                                mygui.Align())
        self.widget.setVisible(True)
        self.caption = self.widget.createWidgetT("StaticText", "StaticText",
                                            mygui.IntCoord(0, 0, 0, 0),
                                            mygui.Align())
        self.caption.setCaption(string)
        self.caption.setCoord((self.widget.getSize().width - self.caption.getTextSize().width)/2,
                         textOffset1,
                         self.caption.getTextSize().width,
                         self.caption.getTextSize().height)
        self.caption.setVisible(True)
        
        self.roll_button = self.widget.createWidgetT("Button", "ButtonMinusPlus",
                                                mygui.IntCoord(0,0,20,20), 
                                                mygui.Align())
        self.roll_button.setPosition(self.widget.getSize().width - self.roll_button.getSize().width - textOffset2,
                             textOffset1)
        self.roll_button.setVisible(True)
        self.roll_button.subscribeEventMouseButtonClick(self, "_eventRollButtonClick")

        self.pWidget_Y = self.caption.getSize().height + textOffset2 + textOffset1
        self.caption_height = self.pWidget_Y
    
    def destroyPanel(self):
        suit.core.render.engine.Gui.destroyWidget(self.widget)
        self.widget = None
        self.roll_button = None
        self.caption = None
    
    def addPropertyWidget(self, type, skin, name):
        p_text = self.widget.createWidgetT("StaticText", "StaticText",
                                           mygui.IntCoord(0,0,0,0),
                                           mygui.Align())
        p_text.setCaption(name)
        p_text.setCoord(self.widget.getSize().width - self.pWidget_width - textOffset2 - textOffset1 - p_text.getTextSize().width,
                        self.pWidget_Y,
                        p_text.getTextSize().width,
                        p_text.getTextSize().height)
        p_text.setVisible(True)
        self.texts.append(p_text)
        p_widget = self.widget.createWidgetT(type, skin,
                                  mygui.IntCoord(self.widget.getSize().width - self.pWidget_width - textOffset2,
                                                 self.pWidget_Y,
                                                 self.pWidget_width,
                                                 self.pWidget_height),
                                  mygui.Align())
        p_widget.setVisible(True)
        self.widgets.append(p_widget)
        self.pWidget_Y += self.pWidget_height + textOffset1
        
        global need_scroll_view_canvas_sz_update
        need_scroll_view_canvas_sz_update = True
        self.needSizeUpdate = True
        self.updateSize()
        
    def deletePropertyWidget(self, i):
        suit.core.render.engine.Gui.destroyWidget(self.widgets[i])
        del self.widgets[i]
        
        suit.core.render.engine.Gui.destroyWidget(self.texts[i])
        del self.texts[i]
        
        self.pWidget_Y -= (self.pWidget_height + textOffset1)       
                
    def updateSize(self):
        self.widget.setSize(self.widget.getSize().width,
                            (textOffset1 + self.pWidget_height)*len(self.widgets) + self.caption_height + textOffset1)
        self.needSizeUpdate = False       
                        
    def _eventRollButtonClick(self, widget):
        if self.roll_button.getButtonPressed():
            self.moveSpeed = 1
        else:
            self.moveSpeed = -1
        self.roll_button.setButtonPressed(not self.roll_button.getButtonPressed())
        self.needSizeUpdate = True
        
        
        
