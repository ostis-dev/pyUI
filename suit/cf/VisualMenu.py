
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
Created on 13.01.2010

@author: Denis Koronchik
'''
import suit.core.render.engine as render_engine
from suit.core.objects import ObjectOverlay
from suit.core.layout.LayoutGroup import LayoutGroupOverlay
import math
import suit.core.render.mygui as mygui

class VisualMenuItem(ObjectOverlay):
    """Class that realize visual menu item
    
    You can get callback to set attribute callback value with function you want to call.
    That function have one parameter: VisualMenuItem it called from
    """
    def __init__(self):
        ObjectOverlay.__init__(self)
        
        self.parent = None
        self.childs = []
        
        self.callback = None
        
        self._auto_move = True
        
        self._createWidget()
            
    def __del__(self):
        ObjectOverlay.__del__(self)
        
    def delete(self):
        """Deletion message
        """
        self._destroyWidget()
        #deleting childs
        for item in self.childs:
            item.delete()
            item.parent = None
            item.callback = None
        self.childs = None
    
    def _update(self, timeSinceLastFrame):
        """Translate update message to child items
        """
        ObjectOverlay._update(self, timeSinceLastFrame)
        
        for child in self.childs:
            child._update(timeSinceLastFrame)
   
    def _updateView(self):
        """Update view representation of menu item 
        """
        ObjectOverlay._updateView(self)
        
        # updating view in child items
        for item in self.childs:
            item._updateView()
 
    def isAtomic(self):
        """Check if item doesn't have subitems
        @return: if there are no subitems in menu, then return True, else - False
        @rtype: bool 
        """
        return len(self.childs) == 0
      
    def setVisible(self, _value):
        """@see: suit.objects.OverlayObject.setVisible
        """
        ObjectOverlay.setVisible(self, _value)
        self.needEnabledUpdate = True
    
    def appendItem(self, _item):
        """Appends item to menu
        @param _item:    item to append
        @type _item:    VisualMenuItem
        
        @raise RuntimeError:    raise error when item already exists
        """
        if _item in self.childs:    raise RuntimeError("Item '%s' already exists" % str(_item))
        if _item.parent is not None:    _item.parent.removeItem(_item)
        self.childs.append(_item)
        _item.parent = self
        #_item._move_speed = 0.05 * len(self.childs)
        
    def removeItem(self, _item):
        """Removes item from menu
        @param _item:    item to remove
        @type _item:    VisualMenuItem
        """
        self.childs.remove(_item)
        _item.parent = None
        
    def showItem(self):
        """Shows item
        """         
        self.setVisible(True)
        
    def hideItem(self):
        """Hides item
        """
        self.setVisible(False)
                
    def _createWidget(self):
        """Creates mygui widget to visualize item 
        """
        self._widget = render_engine.Gui.createWidgetT("Button",
                                                       "Button",
                                                       mygui.IntCoord(1, 1, 30, 30),
                                                       mygui.Align(), "Popup")
        
        self._widget.subscribeEventMouseButtonClick(self, "_widgetClick")
        self._widget.setVisible(False)
        self._widget.setAlpha(0.7)
                
        self._widget.subscribeEventMouseSetFocus(self, "_widgetMouseSetFocus")
        self._widget.subscribeEventMouseLostFocus(self, "_widgetMouseLostFocus")
        
        self.setScale((32, 32))
        
    def _destroyWidget(self):
        """Destroys mygui widget that visualizing item
        """
        if self._widget is None:    return
        
        render_engine.Gui.destroyWidget(self._widget)
        self._widget = None
        
    def _widgetMouseSetFocus(self, widget, v):
        """Mouse set focus message
        """
        self._widget.setAlpha(0.9)
        
    def _widgetMouseLostFocus(self, widget, v):
        """Mouse lost focus message
        """
        self._widget.setAlpha(0.5)
        
    def _widgetClick(self, widget):
        if self.callback is None:   raise RuntimeError("Menu item haven't any callback")
        self.callback(self)
        
class VisualMenu(VisualMenuItem):
    """Class that controls whole visual menu and layout process
    """
    def __init__(self):
        VisualMenuItem.__init__(self)
        
        self.expanded = None
        self.layout = VisualMenuLayoutGroup()
        
        self._destroyWidget()
        
    def __del__(self):
        VisualMenuItem.__del__(self)
        
    def showItem(self):
        """Shows menu
        """
        self.expanded = self
        self.showChilds(self.expanded)
    
    def hideItem(self):
        if self.expanded:
            self.hideChilds(self.expanded)
            self.expanded = None
    
    def show(self, _pos):
        """Shows visual menu
        @warning: is not thread safe
        """
        self.showItem()
        self.layout.setCenter(_pos)
        self._relayout()
        
    def hide(self):
        self.hideItem()
        
    def move(self, _pos):
        """Moves menu center to position
        """
        self.layout.setCenter(_pos)
        self.layout._layout()
    
    def isShow(self):
        """Check if menu is showing
        @return: if menu is showing, then return True, else - False
        """
        return self.expanded is not None
        
    def item_callback(self, _item):
        """Callback for items
        @param _item:    item send callback
        @type _item:    VisualMenuItem
        """
        self.hideChilds(self.expanded)
        self.expanded = _item
        self.showChilds(self.expanded)
        self._relayout()
        
            
    def showChilds(self, _item):
        """Shows child items for visual menu item
        @param _item:    visual menu item to show child items
        @type _item:    VisualMenuItem
        """
        # show child objects
        for item in _item.childs:
            item.showItem()
            if len(item.childs) > 0:
                item.callback = self.item_callback
                
    def hideChilds(self, _item):
        """Hides child items for visual menu item
        @param _item:    visual menu item to hide child items
        @type _item:    VisualMenuItem
        """
        # hide child items
        for item in _item.childs:
            item.hideItem()
           
        
    def _relayout(self):
        """Makes layout for menu items
        """
        #self.layout._appendListOfObjects(self.expanded.childs)
        self.layout.removeAllObjects()
        
        for item in self.expanded.childs:
            if item.isEnabled():
                self.layout.appendObject(item)
                
        self.layout._layout()
        
    def refresh(self):
        """Updates menu state
        """
        self.hideChilds(self.expanded)
        self.showChilds(self.expanded)
        self._relayout()
        

class VisualMenuLayoutGroup(LayoutGroupOverlay):
    
    def __init__(self):
        LayoutGroupOverlay.__init__(self)
        self.pos = None
        
    def __del__(self):
        LayoutGroupOverlay.__del__(self)
        
    def setCenter(self, _pos):
        """Sets center for menu
        @param _pos:    center position
        @type _pos:    tuple (x, y)        
        """
        self.pos = _pos
        
    def _apply(self):
        """Applies layout
        """
        # getting number of overlays and counting circle radius
        items_count = len(self.overlays)
        if items_count == 0 or not self.pos:    return 
        
        radius = max([40 / 2 / math.pi, 50])
        if render_engine.viewMode is render_engine.Mode_Isometric:
            radius = radius * render_engine.scale() / render_engine.scale_init() * 0.7
        else:
            radius = radius * render_engine.scale().x / render_engine.scale_init().x * 0.7
        
        # calculating positions
        x = self.pos[0] + radius
        y = self.pos[1] - radius / 2.0
        for obj in self.overlays:
            # set new position
            y += obj.getScale()[1] + 3
            obj.setPosition((int(x), int(y)))