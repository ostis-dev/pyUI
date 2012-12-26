
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


import suit.core.objects as objects
from suit.cf.BaseModeLogic import BaseModeLogic
from _3d_modes import _3DViewMode
import suit.core.render.engine as render_engine
import ogre.io.OIS as ois
import ogre.renderer.OGRE as ogre
import _3d_objects

class _3DViewer(BaseModeLogic):
    """Geometry viewer logic realization
    """
    def __init__(self):
        """constructor
        """

        BaseModeLogic.__init__(self)
        # view modes
        #        self.appendMode(ois.KC_X, FlyMode(self))
        #        self._active_mode = self._modes[ois.KC_X]
        self.appendMode(ois.KC_S, _3DViewMode(self))
        self.switchMode(ois.KC_S)
        self.is_root = False
    
    def __del__(self):
        """Destruction
        """
        BaseModeLogic.__del__(self)
    
    def delete(self):
        """Deletion message
        """        
        BaseModeLogic.delete(self)
    
    def _setSheet(self, _sheet):
        BaseModeLogic._setSheet(self, _sheet)

        _sheet.eventRootChanged = self._onRootChanged
        _sheet.eventUpdate = self._onUpdate

        _sheet.eventChildAppend = self._onAppendChild
        _sheet.eventChildRemove = self._onRemoveChild
        _sheet.eventContentUpdate = self._onContentUpdate
        
        
    def _onRootChanged(self, _isRoot):
        """Root changed event
        """
        global prev_background
        global prev_back_visible
        BaseModeLogic._onRootChanged(self, _isRoot)
        if _isRoot:
            render_engine.setMode(render_engine.Mode_Perspective)
            self.prev_cam_pos = render_engine._ogreCamera.getPosition()
            self.prev_cam_dir = render_engine._ogreCamera.getOrientation()
            self.prev_cam_node_pos = render_engine._ogreCameraNode.getPosition()
            self.prev_cam_node_dir = render_engine._ogreCameraNode.getOrientation()
            prev_background = render_engine._ogreViewport.getBackgroundColour()
            render_engine._ogreViewport.setBackgroundColour(ogre.ColourValue(0, 0, 0))

            prev_back_visible = render_engine.SceneManager.isBackVisible()
            if prev_back_visible:
                render_engine.SceneManager.hideBack()

            self.main3dObject = _3d_objects._3DObject()
            self._getSheet().addChild(self.main3dObject)
            render_engine._ogreCamera.setPosition(80,40,100)
            render_engine._ogreCamera.lookAt(0,0,0)
        else:
            render_engine._ogreCameraNode.setPosition(self.prev_cam_node_pos)
            render_engine._ogreCameraNode.setOrientation(self.prev_cam_node_dir)
            render_engine._ogreCamera.setPosition(self.prev_cam_pos)
            render_engine._ogreCamera.setOrientation(self.prev_cam_dir)
            render_engine.setMode(render_engine.Mode_Isometric)
            render_engine._ogreViewport.setBackgroundColour(prev_background)
            self.main3dObject.__del__()
            self._getSheet().removeChild(self.main3dObject)
            self.main3dObject = None

            if prev_back_visible:
                render_engine.SceneManager.showBack()
        self.is_root = _isRoot

    def _onUpdate(self, _timeSinceLastFrame):
        """Notification on update
        """
        if self._getSheet().isRoot:
            if self._active_mode:
                self._active_mode._update(_timeSinceLastFrame)

    def _onContentUpdate(self):

        import suit.core.keynodes as keynodes
        sheet = self._getSheet()

        sheet.content_type = objects.ObjectSheet.CT_String
        sheet.content_data = str("")
        sheet.content_format = keynodes.ui.format_3d
        
    def _onAppendChild(self, _object):
        """Listener for sheet child objects appending
        """
        pass
        
    def _onRemoveChild(self, _object):
        """Listener for sheet child objects removing
        """
        pass

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
