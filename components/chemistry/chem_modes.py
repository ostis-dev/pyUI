
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
Created on 29.06.2010

@author: Denis Koronchik
'''
from suit.cf import BaseEditMode
from suit.cf import BaseViewMode
from suit.core.objects import Object
import suit.cf.utils as utils
import chem_objects

import suit.core.render.engine as render_engine
import ogre.renderer.OGRE as ogre
import ogre.io.OIS as ois

class ChemistryEditMode(BaseEditMode):
    
    type_bindings = {ois.KC_1: "H",
                     ois.KC_2: "O",
                     ois.KC_3: "C",
                     ois.KC_4: "N"}
    
    def __init__(self, _logic):
        BaseEditMode.__init__(self, _logic)
        
        self.mouse_pos = (0, 0)
        # objects we works with
        self.highlighted_obj = None
        
        # 3d navigation mode
        self.rotX = 0.0 
        self.rotY = 0.0
        self.move = ogre.Vector3(0.0, 0.0, 0.0)
        self.moveSpeed = 15.0
        self.moveScale = 1.0
        self.navigation = False
        
    def __del__(self):
        BaseEditMode.__del__(self)
    
    def _highlight(self):
        """Highlighting object under mouse
        """
        mobjects = self._logic._getSheet()._getObjectsUnderMouse(self.mouse_pos)
        obj = None
        if len(mobjects) > 0:
            obj = mobjects[0][1]
        
        if (obj is None) and (self.highlighted_obj is None):    return 
        if (obj is self.highlighted_obj):   return
        
        # change highlight
        if self.highlighted_obj:
            if self.highlighted_obj._getSelected():
                self.highlighted_obj.setState(Object.OS_Selected)
            else:
                self.highlighted_obj.setState(Object.OS_Normal)
        self.highlighted_obj = obj
        if self.highlighted_obj:    self.highlighted_obj.setState(Object.OS_Highlighted)    
    
    def _onMouseMoved(self, _evt):
        """Mouse moved event
        """
        
        if BaseEditMode._onMouseMoved(self, _evt):  return True
        mstate = _evt.get_state()
        self.mouse_pos = (mstate.X.abs, mstate.Y.abs)
        
        self._highlight()
        
        if self.navigation:
            self.rotX = ogre.Degree(-mstate.X.rel * 0.13)
            self.rotY = ogre.Degree(-mstate.Y.rel * 0.13)
        
        return False
    
    def _onMousePressed(self, _evt, _id):
        """Mouse button pressed event
        """
        if BaseEditMode._onMousePressed(self, _evt, _id):   return True
        
        # getting objects under mouse
        mobjects = self._logic._getSheet()._getObjectsUnderMouse(True, True, self.mouse_pos)
        
        if _id == ois.MB_Right:
            if len(mobjects) == 0:
                if render_engine.viewMode is render_engine.Mode_Perspective:
                    self._logic.addAtom(render_engine.pos2dToViewPortRay(self.mouse_pos).getPoint(10.0), "H")
                else:
                    self._logic.addAtom(render_engine.pos2dTo3dIsoPos(self.mouse_pos), "H")
                 
         
        elif _id == ois.MB_Left:
            if len(mobjects) > 0:
                self._selectObject(mobjects[0][1])
            else:
                if render_engine.viewMode is render_engine.Mode_Perspective:
                    self.navigation = True
        
        return False
    
    def _onMouseReleased(self, _evt, _id):
        """Mouse button released event
        """
        if BaseEditMode._onMouseReleased(self, _evt, _id):  return True
        
        if _id == ois.MB_Left and self.navigation:
            self.navigation = False
        
        return False
    
    def _onKeyPressed(self, _evt):
        """Keyboard button pressed event
        """
        if BaseEditMode._onKeyPressed(self, _evt):  return True
        
        if _evt.key == ois.KC_F9:
            
            if render_engine.viewMode is render_engine.Mode_Isometric:
                self._logic._getSheet().changeMode(render_engine.Mode_Perspective)
            else:
                self._logic._getSheet().changeMode(render_engine.Mode_Isometric)
            self.navigation = False
            
        # create link between objects    
        if _evt.key == ois.KC_SPACE:
            _args = self._logic._getSheet().getSelected()
            if len(_args) == 2 and isinstance(_args[0], chem_objects.ChemistryAtom) and isinstance(_args[1], chem_objects.ChemistryAtom):
                self._logic.addLink(_args[0], _args[1])
                
        # create random element
        if _evt.key == ois.KC_F1:
            import random
            atoms_num = random.randint(50, 100)
            links_num = random.randint(0, atoms_num)
            names = self.type_bindings.values()
            atoms = []
            for a in xrange(atoms_num):
                _atom = self._logic.addAtom(ogre.Vector3(float(random.randint(-10, 10)), float(random.randint(-10, 10)), 0.0), 'C')
                if len(atoms) > 0:
                    a1 = random.randint(0, len(atoms) - 1)
                    self._logic.addLink(atoms[a1], _atom)
                    
                atoms.append(_atom)
                
#            for l in xrange(links_num):
#                a1 = random.randint(0, atoms_num - 1)
#                a2 = random.randint(0, atoms_num - 1)
#                while a1 == a2:
#                    a2 = random.randint(0, atoms_num - 1)
#                self._logic.addLink(atoms[a1], atoms[a2])
        
        # test type changing
        if self.type_bindings.has_key(_evt.key):
            self.setSelectionName(self.type_bindings[_evt.key])
        
        
        return False
    
    def _onKeyReleased(self, _evt):
        """Keyboard button released event
        """
        if BaseEditMode._onKeyReleased(self, _evt): return True
        
        return False
    
    def _update(self, _timeSinceLastFrame):
        """Update mode
        """
        if self.navigation:
            if self._logic._getSheet().isRoot and render_engine.viewMode is render_engine.Mode_Perspective:
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
            
                # updating camera position
                camera = render_engine._ogreCamera
                cameraNode = render_engine._ogreCameraNode
                cameraNode.translate(camera.getOrientation() * self.move)
                camera.yaw(self.rotX)
                camera.pitch(self.rotY)
                self.move = ogre.Vector3(0, 0, 0)
                self.rotX = 0
                self.rotY = 0
        
    
    def setSelectionName(self, _name):
        """Set specified atom name to selected atoms
        """
        objects = self._logic._getSheet().getSelected()
        for obj in objects:
            if isinstance(obj, chem_objects.ChemistryAtom):
                obj.setName(_name)
    
class ChemistryViewMode(BaseViewMode):
    
    def __init__(self, _logic):
        BaseViewMode.__init__(self, _logic)
        
    def __del__(self):
        BaseViewMode.__del__(self)
        
    def _onMouseMoved(self, _evt):
        """Mouse moved event
        """
        if BaseViewMode._onMouseMoved(self, _evt):  return True
        mstate = _evt.get_state()
        self.mouse_pos = (mstate.X.abs, mstate.Y.abs)
        
        return False
    
    def _onMousePressed(self, _evt, _id):
        """Mouse button pressed event
        """
        if BaseViewMode._onMousePressed(self, _evt, _id):   return True
        
        return False
    
    def _onMouseReleased(self, _evt, _id):
        """Mouse button released event
        """
        if BaseViewMode._onMouseReleased(self, _evt, _id):  return True
        
        return False
    
    def _onKeyPressed(self, _evt):
        """Keyboard button pressed event
        """
        if BaseViewMode._onKeyPressed(self, _evt):  return True
            
        return False
    
    def _onKeyReleased(self, _evt):
        """Keyboard button released event
        """
        if BaseViewMode._onKeyReleased(self, _evt): return True
        
        return False