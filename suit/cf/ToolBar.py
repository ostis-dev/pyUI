
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
Created on 07.01.2011

@author: Denis Koronchik
'''
from suit.core.objects import ObjectOverlay
import suit.core.render.engine as render_engine
import suit.core.render.mygui as mygui

class ToolBarButton(ObjectOverlay):
    """Events:
    - eventPush - function that calls on mouse click.
    function(ToolBarButton)
    """
    
    def __init__(self, parent, texture_name, index, tile_size, image_coord):
        """Constructor
        @param parent:    parent object
        @type parent:    ObjectOverlay
        
        @param texture_name:    name of texture to get image
        @type taxture_name:    str
        
        @param index:    tile index
        @type index:    int
        
        @param tile_size:    size of image tile
        @type tile_size:    (int, int)
        
        @param image_coord:    coordinates on image to get tiles
        @type image_coord:    (int, int, int, int) -> (let, top, width, height)
        """
        ObjectOverlay.__init__(self, parent)
        self.autoSize = False
        
        self.static_image = None 
        self.needImageUpdate = True
        self.texture = texture_name
        self.index = index
        self.tile_size = tile_size
        self.image_coord = image_coord
        
        self.checkable = False  # flag to use button as check button
        self.checked = False    # check state
        
        self.user_data = None   # user data to associate with button 
        
        self.eventPush = None
        
        self.needCheckUpdate = False    # flag to update check state
        
        self.createWidget()
    
    def __del__(self):
        ObjectOverlay.__del__(self)
    
    def delete(self):
        
        self.destroyWidget()
        
    def _update(self, timeSinceLastFrame):
        """Update object
        """
        ObjectOverlay._update(self, timeSinceLastFrame)
        
    def _updateView(self):
        """Update view message
        """
        ObjectOverlay._updateView(self)
        
        if self.needImageUpdate:
            self.needImageUpdate = False
            self._updateImage()
        
        if self.needCheckUpdate:
            self.needCheckUpdate = False
            self._updateCheck()
        
    def _updateImage(self):
        self.static_image.setImageTile(mygui.IntSize(self.tile_size[0], self.tile_size[1]))
        self.static_image.setImageTexture(self.texture)
        self.static_image.setImageIndex(self.index)
        self.static_image.setImageCoord(mygui.IntCoord(self.image_coord[0],
                                                       self.image_coord[1],
                                                       self.image_coord[2],
                                                       self.image_coord[3]))
        
    def _updateCheck(self):
        self._widget.setStateCheck(self.checked)
        
    def createWidget(self):
        """Create static image widget
        """
        assert self._widget is None
        self._widget = self.parent._widget.createWidgetT("Button",
                                                         "Button",
                                                         mygui.IntCoord(0, 0, 10, 10),
                                                         mygui.Align(), "ToolBarButton_%s" % str(self))
        
        self.static_image = self._widget.createWidgetT("StaticImage",
                                                       "StaticImage",
                                                       mygui.IntCoord(3, 3, 4, 4),
                                                       mygui.Align(mygui.ALIGN_STRETCH))
        self.static_image.setNeedMouseFocus(False)
        
        self._widget.subscribeEventMouseButtonClick(self, "_onMouseClick")
    
    def destroyWidget(self):
        """Destroy static image
        """ 
        render_engine.Gui.destroyWidget(self._widget)
        self._widget = None
        
    def setTextureName(self, texture_name):
        self.texture = texture_name
        self.needImageUpdate = True
        
    def setCheckable(self, value):
        """Sets checkable flag
        """
        self.checkable = value
        self.needCheckUpdate = True
        self.needViewUpdate = True
        
    def isChekable(self):
        return self.checkable
    
    def setChecked(self, value):
        self.checked = value
        self.needCheckUpdate = True
        self.needViewUpdate= True
        
    def isChecked(self):
        return self.checked    
    
    def setUserData(self, data):
        self.user_data = data
    
    def getUserData(self):
        return self.user_data    
    
    def _onMouseClick(self, widget):
        if self.checkable:
            self.setChecked(not self.isChecked())
        if self.eventPush:
            self.eventPush(self)
        

class ToolBar(ObjectOverlay):
    
    Top, Left, Right, Bottom, AlignCount = range(5)
    
    def __init__(self):
        ObjectOverlay.__init__(self)
        
        self.buttons_size = 32  # buttons size (buttons are squares)
        
        self.needLayoutUpdate = True     # flag to update size
        self.needButtonsUpdate = False  # flag to update buttons
        
        self.align = ToolBar.Left       # alignment
        self.min_length = 100           # minimal length
        self.max_length = 550            # maximum length

        self.createWidget()
       
    def __del__(self):
        ObjectOverlay.__del__(self)
    
    def delete(self):
        ObjectOverlay.__del__(self)
        self.destroyWidget()
    
    def _update(self, timeSinceLastFrame):
        """Update toolbar
        """
        ObjectOverlay._update(self, timeSinceLastFrame)
   
    def _updateView(self):
        """Update toolbar view
        """
        ObjectOverlay._updateView(self)
        
        if self.needLayoutUpdate:
            self.needLayoutUpdate = False
            self.updateLayout()
            
        if self.needButtonsUpdate:
            self.needButtonsUpdate = False
            self.updateButtons()
        
    def __getitem__(self, idx):
        return self._childs[idx]
        
    def createWidget(self):
        """Create toolbar panel
        """
        assert self._widget is None
        self._widget = render_engine.Gui.createWidgetT("Window",
                                                       "Panel",
                                                       mygui.IntCoord(0, 0, 0, 0),
                                                       mygui.Align(), "Main")
        self._widget.setVisible(False)
        
    def destroyWidget(self):
        """Destroy toolbar panel
        """
        render_engine.Gui.destroyWidget(self._widget)
        self._widget = None
        
    def setButtonSize(self, size):
        """Sets buttons size
        
        @param size:    new buttons size value
        @type size:    int
        """
        self.buttons_size = size
        self.needLayoutUpdate = True
        self.needButtonsUpdate = True
        self.needViewUpdate = True
        
    def appendButton(self, caption, image, index, tile_size, image_coord):
        """Append button into toolbar
        @param caption:    Button caption
        @type caption:    string
        
        @param image:    name of image that contains icons
        @type image:    str
        
        @param index:    index of tile on image
        @type index:     int
        
        @param tile_size:    image tile size
        @type tile_size:    (int, int)
        
        @param image_coord:    coordinates on image to get tiles
        @type image_coord:    (int, int, int, int) -> (let, top, width, height)
        
        @return: toolbar button object
        @rtype: ToolBarButton
        """
        button = ToolBarButton(self, image, index, tile_size, image_coord)
        button.setText(caption)
        button.setVisible(True)
        button.setEnabled(True)
       
        self.needViewUpdate = True
        self.needButtonsUpdate = True
        
        return button
    
    def removeButton(self):
        """Removes button from tool bar
        """
        pass
    
    def lengthHint(self):
        """Calculates best length 
        """
        return max([min([len(self._childs) * (self.buttons_size + 5), self.max_length]), self.min_length])
    
    def updateLayout(self):
        """Calculates new size and position on screen
        """
        width = height = 0
        left = top = 0
        
        if self.align is ToolBar.Top or self.align is ToolBar.Bottom:
            width = self.lengthHint()
            height = self.buttons_size
        else:
            height = self.lengthHint()
            width = self.buttons_size
            
        if self.align is ToolBar.Left:
            left = 0
            top = (render_engine.Window.height - height) / 2
        elif self.align is ToolBar.Right:
            left = render_engine.Window.width - width
            top = (render_engine.Window.height - height) / 2
        elif self.align is Toolbar.Top:
            left = (render_engine.Window.width - width) / 2
            top = 0
        else:
            left = (render_engine.Window.width - width) / 2
            top = render_engine.Window.height - height
            
            
        width += 10
        height += 10
        self.setPosition((int(left), int(top)))
        self.setScale((int(width), int(height)))
        #self._widget.setCoord(int(left), int(top), int(width), int(height))

    def updateButtons(self):
        """Updates button positions and size
        """
        idx = 0
        for button in self._childs:
            button.setScale((int(self.buttons_size), int(self.buttons_size)))
            offset = 5 + idx * (self.buttons_size + 5)
            if self.align is ToolBar.Top or self.align is ToolBar.Bottom:
                button.setPosition((int(offset), int(5)))
            else:
                button.setPosition((int(5), int(offset)))
            idx += 1