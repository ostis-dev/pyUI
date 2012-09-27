
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
Created on 17.10.2009

@author: Maxim Kaskevich
'''
import ogre.renderer.OGRE as ogre
import suit.core.kernel as core
import suit.core.objects as objects
from space_modes import SpaceViewMode
from suit.cf import BaseModeLogic
from suit.core.objects import BaseLogic
import ogre.io.OIS as ois
import space_env as env
from space_objects import SpaceObject 
import suit.core.render.engine as render_engine
#import space_panel
import space_window


#def getResourceLocation():
#    """Return resource location folder
#    """
#    return core.Kernel.getResourceLocation() + getResourceGroup()
#
#def getResourceGroup():
#    """Return resource group name
#    """
#    return 'space'

prev_background  = ogre.ColourValue(0, 0, 0)

class SpaceViewer(BaseModeLogic):
    def __init__(self):
        """constructor
        """
        
        BaseModeLogic.__init__(self)
        # view modes
#        self.appendMode(ois.KC_X, FlyMode(self))
#        self._active_mode = self._modes[ois.KC_X]
        self.appendMode(ois.KC_S, SpaceViewMode(self))
        self.switchMode(ois.KC_S)
        self.is_root = False
        
    def __del__(self):
        BaseModeLogic.__del__(self)
        
    def _setSheet(self, _sheet):
        BaseModeLogic._setSheet(self, _sheet)
        
        _sheet.eventRootChanged = self._onRootChanged
        _sheet.eventUpdate = self._onUpdate
        _sheet.eventObjectUnderMouse = self._getObjectsUnderMouse
        _sheet.eventContentUpdate = self._onContentUpdate
        _sheet.eventHaveChild = self._haveChild
        
    def _onUpdate(self, _timeSinceLastFrame):
        """Notification on update
        """
        if self._getSheet().isRoot:
            if self._active_mode:
                self._active_mode._update(_timeSinceLastFrame)
                
        if self.is_root:    
#            space_panel.update(_timeSinceLastFrame)
            space_window.update(_timeSinceLastFrame)
        
    def _onContentUpdate(self):
        
        import suit.core.keynodes as keynodes
        sheet = self._getSheet()
        
        sheet.content_type = objects.ObjectSheet.CT_String
        sheet.content_data = str("")
        sheet.content_format = keynodes.ui.format_space
        
    def _onRootChanged(self, isRoot):
        """Root changed event
        """
        global prev_background
        global prev_back_visible
        BaseModeLogic._onRootChanged(self, isRoot)
        if isRoot:
            render_engine.setMode(render_engine.Mode_Perspective)            
            self.prev_cam_pos = render_engine._ogreCameraNode.getPosition()
            self.prev_cam_dir = render_engine._ogreCameraNode.getOrientation()
            prev_background = render_engine._ogreViewport.getBackgroundColour()
            render_engine._ogreViewport.setBackgroundColour(ogre.ColourValue(0, 0, 0)) 
#            space_panel.activate(self._getSheet().getChilds())
            prev_back_visible = render_engine.SceneManager.isBackVisible()
            if prev_back_visible:
                render_engine.SceneManager.hideBack()
        else:
            render_engine.setMode(render_engine.Mode_Isometric)
            render_engine._ogreCameraNode.setPosition(self.prev_cam_pos)
            render_engine._ogreCameraNode.setOrientation(self.prev_cam_dir)
            render_engine._ogreViewport.setBackgroundColour(prev_background)
#            space_panel.deactivate()
            space_window.deactivate()
            
            if prev_back_visible:
                render_engine.SceneManager.showBack()
        self.is_root = isRoot                
       
#    def _update(self, _timeSinceLastFrame):
#        """Updating scene
#        """
#        objects.ObjectSheet._update(self, _timeSinceLastFrame)

    def _getObjectsUnderMouse(self, sortDistance = True, forced = False, mpos = None):
        """@see: suit.core.objects.ObjectSheet._getObjectsUnderMouse
        """
        res = []
        for child in self._getSheet().getChilds():
            res.extend(child.getChildsRecursively())
            
        return res
    
    def _haveChild(self, child):
               
        res = []
        for _child in self._getSheet().getChilds():
            res.extend(_child.getChildsRecursively())
            res.append(_child)
            
        return res.count(child) > 0
        
    def play(self):
#        for obj in self._getSheet().getChilds():
#            obj.animate()
        pass
    
    def pause(self):
        pass
    
    def stop(self):
        pass
    
