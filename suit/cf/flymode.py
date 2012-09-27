
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
Created on 26.09.2009

@author: Max Kaskevich modified by Denis Koronchik
'''

import ogre.renderer.OGRE as ogre
import ogre.io.OIS as ois
import suit.core.kernel as core
import suit.core.render.engine as render_engine
import math
from suit.cf.BaseViewMode import BaseViewMode

class FlyMode(BaseViewMode, ogre.FrameListener):
    
    def __init__(self, _logic):
        BaseViewMode.__init__(self, _logic)
        self.cameraNode = render_engine._ogreCameraNode
        self.camera = render_engine._ogreCamera
        
        self.rotX = 0.0 
        self.rotY = 0.0
        self.move = ogre.Vector3(0.0, 0.0, 0.0)
        
        self.moveScale = 0.0
        self.rotScale = 0.0
        
        self.moveSpeed = 15.0
        self.rotateSpeed = 60
        
    def __del__(self):
        pass
    
    def activate(self):
        BaseViewMode.activate(self)
        
    
    def deactivate(self):
        BaseViewMode.deactivate(self)
        
    def enable(self):
        render_engine._gui.hidePointer()
        
    def disable(self):
        render_engine._gui.showPointer()
        
    def _update(self, timeSinceLastFrame):
        if timeSinceLastFrame == 0:
            self.moveScale = 0.01
            self.rotScale = 0.1
            # Otherwise scale movement units by time passed since last frame
        else:
            # Move about 10 units per second,
            self.moveScale = self.moveSpeed * timeSinceLastFrame
            # Take about 10 seconds for full rotation
            self.rotScale = ogre.Degree(self.rotateSpeed * timeSinceLastFrame)
            
        # processing input
        self.processInput()
        
        # applying modifications
        self.cameraNode.translate(self.camera.getOrientation() * self.move)
        self.camera.yaw(self.rotX)
        self.camera.pitch(self.rotY)
        
        self.rotX = 0.0
        self.rotY = 0.0
        self.move = ogre.Vector3(0.0, 0.0, 0.0)
        return True
    
    def processInput(self):
        # processing mouse input
        ms = render_engine._oisMouse.getMouseState()
        self.rotX = ogre.Degree(-ms.X.rel * 0.13)
        self.rotY = ogre.Degree(-ms.Y.rel * 0.13)
        
        # processing keyboard input
        if  render_engine._oisKeyboard.isKeyDown(ois.KC_A):
            self.move.x = -self.moveScale    # Move camera left

        if  render_engine._oisKeyboard.isKeyDown(ois.KC_D):
            self.move.x = self.moveScale    # Move camera RIGHT

        if  render_engine._oisKeyboard.isKeyDown(ois.KC_W):
            self.move.z = -self.moveScale  # Move camera forward

        if  render_engine._oisKeyboard.isKeyDown(ois.KC_S):
            self.move.z = self.moveScale    # Move camera backward
            
        if  render_engine._oisKeyboard.isKeyDown(ois.KC_Q):
            self.move.y = self.moveScale  # Move camera up

        if  render_engine._oisKeyboard.isKeyDown(ois.KC_E):
            self.move.y = -self.moveScale    # Move camera down
        
