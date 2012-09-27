
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
Created on 31.01.2010

@author: Maxim Kaskevich
'''


import ogre.renderer.OGRE as ogre
import ogre.io.OIS as ois
from suit.cf import BaseEditMode
from suit.cf import BaseViewMode
#from suit.cf import IdtfChanger
from suit.core.objects import Object
import flash_env as env

import suit.cf.utils as comutils
import suit.core.render.engine as render_engine


class FlashDefaultViewMode(BaseViewMode, ogre.FrameListener):
    
    def __init__(self, _logic):
        BaseViewMode.__init__(self, _logic, "Object view")
        ogre.FrameListener.__init__(self)
        render_engine._ogreRoot.addFrameListener(self)
        
        self.scale = False
        self.move = False
        
    def __del__(self):
        BaseViewMode.__del__(self) 
        
    def updateView(self, timeSinceLastFrame):
        
        time = timeSinceLastFrame    
        state = render_engine._oisMouse.getMouseState()
        x = state.X.abs
        y = state.Y.abs
#        if self.panel and self.isRoot:
#            if self.y - y < 50:
#                self.showPanel()
#            else: self.hidePanel()


      
    def _onMouseMoved(self, _evt):
        state = _evt.get_state()
        if self._logic.material:
            return self._logic.material.injectMouseMove(int((state.X.abs + self._logic.coord_offset[0]) * self._logic.coord_mult[0]),
                                                  int((state.Y.abs + self._logic.coord_offset[1]) * self._logic.coord_mult[1]))
                    
        return False
    
    def _onMousePressed(self, _evt, _id):
        state = _evt.get_state()
        if self._logic.material:
            return self._logic.material.injectMouseDown(int((state.X.abs + self._logic.coord_offset[0]) * self._logic.coord_mult[0]),
                                                  int((state.Y.abs + self._logic.coord_offset[1]) * self._logic.coord_mult[1]))
        return False
    
    def _onMouseReleased(self, _evt, _id):
        state = _evt.get_state()
        if self._logic.material:
            return self._logic.material.injectMouseUp(int((state.X.abs + self._logic.coord_offset[0]) * self._logic.coord_mult[0]),
                                                  int((state.Y.abs + self._logic.coord_offset[1]) * self._logic.coord_mult[1]))
        return False
    
    def _onKeyPressed(self, _evt):
        if env.hikariMgr.isAnyFocused():
            return True
        
        return False

     
   