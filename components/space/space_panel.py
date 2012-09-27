
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
Created on 08.03.2010

@author: DerDevil
@summary: Realization of tools panel for space editor
'''

import suit.core.render.mygui as mygui
import suit.core.exceptions
import suit.core.render.engine

panel_window = None     # main window of panel
panel_locked = False    # lock on screen flag
panel_width = 200       # panel width
panel_height = 500      # panel height
panel_side_width    =   45  # right side width

lock_button =   None    # lock button
lock_button_offset  =   (-32, -2)

scroll_view = None      # widget for scroll view (it contains items)
need_scroll_view_canvas_sz_update   =   False   # flag to update scroll view canvas size
scroll_bar_width    =   16  # scroll bar width on scroll view

move_time   =   0.25     # time to move panel on hide/show
move_dir    =   1       # direction for moving
need_pos_update = False # flag to position update
followModeOn = False

items   =   []      # items that exists on panel
obj2item = {}       # map for object to item conversion

def initialize():
    """Initialize panel.
    Calls on geometry module startup.
    """
    import space_env
    #if not mygui.SkinManager.getInstance().load(space_env.gui_skin_panel):  # skin loading
    #    raise suit.core.exceptions.ResourceLoadError("Can't load skin '%s'" % space_env.gui_skin_panel)
    
    create_panel()  # creating panel
    
def shutdown():
    """Destroys panel.
    Calls on geometry module shutting down
    """
    # we can't unload mygui resources (not supported by mygui)
    destroy_panel()

def create_panel():
    """Creates panel and preparing it for using
    """
    global panel_window
    global lock_button
    assert not panel_window
    
    panel_window = suit.core.render.engine.Gui.createWidgetT("Window", "Panel",
                                                              mygui.IntCoord(panel_side_width - panel_width,
                                                                             suit.core.render.engine.Window.height - 530,
                                                                             panel_width, panel_height),
                                                              mygui.Align())
    panel_window.setVisible(False)     # don't show panel at startup
    panel_window.setAlpha(0.9)          # make it with small alpha
    panel_window.subscribeEventRootMouseChangeFocus(eventRootMouseChangeFocus, '')
    panel_window.subscribeEventMouseMove(eventPanelMouseMoved, '')
    
    
    global scroll_view
    scroll_view = panel_window.createWidgetT("ScrollView", "ScrollView",
                                             mygui.IntCoord(0, 25, panel_width - panel_side_width - 3, panel_height - 35),
                                             mygui.Align())
    scroll_view.setVisible(True)
    
    
    lock_button = panel_window.createWidgetT("Button", "Button",
                                             mygui.IntCoord(panel_width + lock_button_offset[0], lock_button_offset[1],
                                                            35, 35),
                                                            mygui.Align())
    lock_button.setVisible(True)
    lock_button.setStateCheck(panel_locked)
    lock_button.subscribeEventMouseButtonClick(eventLockButtonMouseClick, '')
    
    
    

def destroy_panel():
    """Destroys panel
    """
    global panel_window
    global lock_button
    global scroll_view
    assert panel_window
    suit.core.render.engine.Gui.destroyWidget(panel_window)
    panel_window = None
    lock_button = None
    scroll_view = None
    
def activate(childs):
    """Activates panel. Makes it visible.
    This function must call when geometry window is going into root mode. 
    """
    global panel_window
    assert panel_window
    createMiniMap(childs)
    panel_window.setVisible(True)

def deactivate():
    """Deactivates panel. Makes it invisible.
    This function must call when geometry window is going out from root mode.
    """
    global panel_window
    assert panel_window
    deleteMiniMap()
    panel_window.setVisible(False)
    
    
def update(dt):
    """Update function.
    Must call from geometry window that in root mode
    """
    global need_pos_update
    
    if need_pos_update:
        pos = panel_window.getPosition()    # get current window position
        dw = panel_width - panel_side_width
        offset = move_dir * dt * (dw) / move_time  # calculating position offset
        
        newX = pos.left + offset
        if move_dir < 0:
            newX = max([newX, -dw])
        else:
            newX = min([newX, 0])
        
        panel_window.setPosition(int(newX), pos.top)    # set new position for a panel
        if newX <= -dw or newX >= 0:
            need_pos_update = False
            
    if need_scroll_view_canvas_sz_update:   # updating scroll view canvas size
        assert scroll_view
        canvas_height = 0
        for item in items:
            canvas_height += item.widget.getHeight() + 1
        scroll_view.setCanvasSize(scroll_view.getSize().width - scroll_bar_width, canvas_height)
        global need_scroll_view_canvas_sz_update
        need_scroll_view_canvas_sz_update = False
        
    if followModeOn:
        return
    
def eventLockButtonMouseClick(_widget):
    """Listener for lock button mouse click
    """
    global panel_locked
    
    panel_locked = not panel_locked
    lock_button.setStateCheck(panel_locked)
    
    if panel_locked:
        global move_dir
        global need_pos_update
        move_dir = 1.0
        need_pos_update = True
    
def eventRootMouseChangeFocus(_widget, _focused):
    """Listener for mouse root focus changed
    """
    if panel_locked:    return  # skip this event if panel is locked
    
    global move_dir
    global need_pos_update
    if _focused:
        move_dir = 1.0
    else:
        move_dir = -1.0
        need_pos_update = True
        
def eventPanelMouseMoved(_widget, _x, _y):
    """Listener for mouse moving on panel
    """
    if _x < 3 and move_dir > 0:
        global need_pos_update
        need_pos_update = True
    

def append_object(_object):
    """Appends object to panel.
    This function must call every time, when object added to window.
    @param _object:    object to append
    @type _object:    srs_engine.objects.ObjectDepth
    """
    assert _object
    
    try:
        prev = items[-1]    # trying to get previous panel item
    except:
        prev = None
    
    item = PanelItem(prev = prev, object = _object)
    item.createWidget()
    items.append(item)
    
    obj2item[_object] = item    # store in conversion map
    global need_scroll_view_canvas_sz_update
    need_scroll_view_canvas_sz_update = True
    
    update_object(_object)
    
def createMiniMap(childs):
    for child in childs:
        append_object(child)
        subchild = child.getChilds()
        createMiniMap(subchild)
        
def deleteMiniMap():
    while len(items):
        remove_object(items[0])
    
def remove_object(item):
    """Removes object from panel.
    This function must call every time, when object removes from window.
    @param _object:    object to remove
    @type _object:    srs_engine.objects.ObjectDepth
    """
    items.remove(item)
    item.delete()
    
    global need_scroll_view_canvas_sz_update
    need_scroll_view_canvas_sz_update = True
    
def update_object(_object):
    """Object information update.
    Must call after geometry object changed. For example changed identificator.
    """
    item = obj2item[_object]
    item.notifyObjectUpdated()    # updating item
    
    
class PanelItem:
    
    def __init__(self, prev = None, object = None):
        self.widget = None
    
        self.prev_item = prev
        self._object = object 
    
    def __del__(self):
        """Object destruction
        """
        assert not self.widget
        print "__del__ in %s" % str(self)
    
    def delete(self):
        """Deletion message
        """
        if self.widget: self.destroyWidget()
    
    def createWidget(self):
        """Creates widget that allows to control item
        """
        assert scroll_view
        posY = 1    # initial y position
        if self.prev_item:  posY = self.prev_item.widget.getPosition().top + self.prev_item.widget.getSize().height + 1
        self.widget = scroll_view.createWidgetT("Button", "Button",
                                                mygui.IntCoord(0, posY, scroll_view.getSize().width - scroll_bar_width, 20),
                                                mygui.Align())
        self.widget.setVisible(True)
        self.widget.subscribeEventMouseButtonClick(self, "_eventPlanetButtonClick")
    
    def destroyWidget(self):
        """Destroys widget
        """
        suit.core.render.engine.Gui.destroyWidget(self.widget)
        self.widget = None
        
    def notifyObjectUpdated(self):
        """Sets new caption for an item
        """
        text = self._object.getText()
        if text is None:
            text = 'None'
        self.widget.setCaption(text)
        
    def _eventPlanetButtonClick(self, widget):
        global followModeOn
        vector = self._object.sceneNode._getDerivedPosition()
        suit.core.render.engine._ogreCameraNode.setPosition((vector.x - 10), vector.y, (vector.z - 10))
        suit.core.render.engine._ogreCamera.lookAt(vector)
        followModeOn = True
        
            