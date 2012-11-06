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
Created on 09.02.2010

@author: Pavel Karpan
'''

import suit.core.kernel as core
import suit.core.render.engine as render_engine
import suit.core.render.mygui as mygui
import suit.core.objects as objects
from suit.core.kernel import Kernel
from suit.core.objects import BaseLogic
import ogre.renderer.OGRE as ogre
import ogre.io.OIS as ois


def initialize():
    pass


def shutdown():
    pass
    
def _createViever():
    return TextViewer()

class TextViewer(BaseLogic):
    
    def __init__(self):
        """Constructor
        """
        BaseLogic.__init__(self)
        self.widget = None

        self.isRoot = False
         
        # attach flags
        self.rectAttached = False
        
        self._createArea = self._createStaticText
        
        # creating rectangle (surface)
#        self.rect = ogre.Rectangle2D(True)
#        self.rect.setCorners(-1.0, 1.0, 1.0, -1.0)
#        self.rect.setRenderQueueGroup(ogre.RENDER_QUEUE_8)
#        self.rect.setBoundingBox(ogre.AxisAlignedBox(ogre.Vector3(-100000.0, -100000.0, -100000.0), ogre.Vector3(100000.0, 100000.0, 100000.0)))
    
    def __del__(self):
        """Destructor
        """        
        BaseLogic.__del__(self)        
        
    def delete(self):
        """Deletion message
        """
        BaseLogic.delete(self)
        # detaching objects
        if self.rectAttached:
            self._getSheet().sceneNodeChilds.detachObject(self.rect)
        self.destroyPanel()
    
    def _onUpdate(self, _timeSinceLastFrame):
        """Logic update
        """
        BaseLogic._update(self, _timeSinceLastFrame)
        self._updateState() 
                    
    def _setSheet(self, _sheet):
        """Sets sheet for a logic
        """
        BaseLogic._setSheet(self, _sheet)
        _sheet.eventRootChanged = self._onRootChanged
        _sheet.eventUpdate = self._onUpdate
        _sheet.eventContentUpdate = self._onContentUpdate
        
        self._createArea()
        self.widget.setCaption(unicode(self.getContent()))
        
    def _onContentUpdate(self):
        
        import suit.core.keynodes as keynodes
        sheet = self._getSheet()
        
        sheet.content_type = objects.ObjectSheet.CT_String
        sheet.content_data = unicode(self.widget.getCaption()).encode('cp1251')
        sheet.content_format = keynodes.ui.format_string
 
    def _onRootChanged(self, isRoot):
        """Root mode switching.
        Creating interface and surface for playing in root mode.
        """        
        if isRoot:
#            self._getSheet().sceneNodeChilds.attachObject(self.rect)
#            self.rectAttached = True            
            self.isRoot = True
            
            # calculating position

            size = self.getSize()
            pos = self.getPosition()
            self.widget.setPosition(pos[0], pos[1])
            self.widget.setSize(size[0], size[1])
            render_engine.SceneManager.setBackMaterial("Back/SimpleLights")                                 
        else:
#            if self.rectAttached:
#                self._getSheet().sceneNodeChilds.detachObject(self.rect)
#                self.rectAttached = False
            self.isRoot = False
            self._updateState()
            size = self.getSize()
            self.widget.setSize(size[0], size[1])
            render_engine.SceneManager.setDefaultBackMaterial() 
            
    def getSize(self):
        """Calculate widget size
        @return: tuple that contains calculated size (width, height)
        """
        if self.isRoot:
            tsize = self.widget.getTextSize()
            size = (max([min([tsize.width, int(render_engine.Window.width * 0.75)]), render_engine.Window.width / 2]), 
                    max([min([tsize.height, int(render_engine.Window.height * 0.75)]), render_engine.Window.height / 2]))
            return size
        
        return (91, 91)
    
    def getPosition(self):
        """Calculate widget position
        @return: tuple that contains new widget position 
        """
        if self.isRoot:
            size = self.getSize()
            return ((render_engine.Window.width - size[0]) / 2, (render_engine.Window.height - size[1]) / 2)
            
        pos3d = self._getSheet().getPosition()
        pos2d = render_engine.pos3dTo2dWindow(pos3d)
        return (pos2d[0] - 45, pos2d[1] - 45)
    
    def getContent(self):        
        import suit.core.sc_utils as sc_utils
        import suit.core.keynodes as keynodes
        session = core.Kernel.session()
        _addr = self._getSheet()._getScAddr()
        if _addr is not None:
            fmt = sc_utils.getContentFormat(session, _addr)
            
            if fmt.this == keynodes.ui.format_string.this or fmt.this == keynodes.ui.format_term.this:
                value = session.get_content_str(_addr)
            elif fmt.this == keynodes.ui.format_int.this or fmt.this == keynodes.ui.format_real.this:
                value = str(session.get_content_real(_addr))
            
            if value is None:
                return ""
            
            return value            
			
        return ""
    
    def _createStaticText(self):
        self.widget = render_engine.Gui.createWidgetT("StaticText", "StaticTextBack",
                                                          mygui.IntCoord(0, 0, 91, 91),
                                                          mygui.Align(mygui.ALIGN_VSTRETCH),
                                                          "Main")
        self.widget.setVisible(False)
        self.widget.setTextColour(mygui.Colour(0.0, 0.0, 0.0, 1.0))
        #self.widget.setCaption(self.getContent())
        self.widget.setNeedMouseFocus(False)        
        
    def destroyPanel(self):        
        if self.widget:
            render_engine.Gui.destroyWidget(self.widget)
    
    def _updateState(self):
        
        _sheet = self._getSheet()
        if self.isRoot:
            self.widget.setVisible(True)
        elif not self.isRoot and _sheet.isContentShow and _sheet.isSceneAttached:
            self.widget.setVisible(True) 
            pos = self.getPosition()
            self.widget.setPosition(pos[0], pos[1])  
        elif not _sheet.isContentShow or not _sheet.isSceneAttached and not self.isRoot:
            self.widget.setVisible(False)
                    
        return True
