
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

@author: Denis
'''

from suit.core.objects import ObjectDepth
from suit.core.objects import ObjectLine

import chem_env

import ogre.renderer.OGRE as ogre
import suit.core.render.engine as render_engine

state_post = {ObjectDepth.OS_Normal: 'Normal',
              ObjectDepth.OS_Selected: 'Selected',
              ObjectDepth.OS_Highlighted: 'Highlighted'}

class ChemistryAtom(ObjectDepth):
    
    def __init__(self):
        ObjectDepth.__init__(self, None)
        
        self.entity = render_engine.SceneManager.createEntity("ChemistryAtom_" + str(self), chem_env.mesh_sphere)
        self.sceneNode.attachObject(self.entity)
        #self.setScale(ogre.Vector3(0.35, 0.35, 0.35))
        
        self._name = None
        
        self.needNameUpdate = True
        
    def __del__(self):
        ObjectDepth.__del__(self)
        render_engine.SceneManager.destroyEntity(self.entity)
        
    def _getMaterialName(self):
        """Return material name for point object based on current state
        
        @return: material name
        @rtype: str
        """
        if self.getState() == ObjectDepth.OS_Normal:
            return chem_env.material_state_pat % ("atom_%s" % self._name)
        
        return chem_env.material_state_pat % (state_post[self.getState()])
        
    def _updateView(self):
        """View update function
        
        Updates state for object
        """        
        if self.needNameUpdate:
            self.needNameUpdate = False
            self.entity.setMaterialName(self._getMaterialName())
            self.setText(self._name)
        
        if self.needStateUpdate:
            self.needStateUpdate = False
            self.entity.setMaterialName(self._getMaterialName())
        
        ObjectDepth._updateView(self)
        
        
    def setName(self, _name):
        """Set atom name from periodical table
        
        @param _name:    name of element from periodical table
        @type _name:    str
        """
        self._name = _name
        self.needNameUpdate = True
        
        
class ChemistryLink(ObjectLine):
    
    def __init__(self):
        ObjectLine.__init__(self, None)
        
        self.entity = render_engine.SceneManager.createEntity("ChemistryLink_" + str(self), chem_env.mesh_link)
        self.sceneNode.attachObject(self.entity)
        self.radius = 0.2
        
        self.needStateUpdate = True
        
    def __del__(self):
        ObjectLine.__del__(self)
        render_engine.SceneManager.destroyEntity(self.entity)
        
    def _update(self, _timeSinceLastFrame):
        """Updating of object
        """
        # updating geometry
        if self.needUpdate:
            op1 = self.beginObject.getPosition()
            op2 = self.endObject.getPosition()
        
            p1 = self.beginObject._getCross(op2)
            p2 = self.endObject._getCross(op1)
            
            self.begin_pos = p1
            self.end_pos = p2
            
            # rotating and scaling link
            orientV = p2 - p1
            self.sceneNode.setPosition(p1)
            l = orientV.length()
            if l < 0.1:
                self.sceneNode.setDirection(ogre.Vector3(1, 1, 0), ogre.SceneNode.TS_PARENT, [0, 1, 0])
            else:
                self.sceneNode.setDirection(orientV, ogre.SceneNode.TS_PARENT, [0, 1, 0])
            self.sceneNode.setScale(ogre.Vector3(self.radius * 2, l, self.radius * 2))    
        
        ObjectLine._update(self, _timeSinceLastFrame)
        
    def _updateView(self):
        """View update function
        
        Updates state for object
        """
        if self.needStateUpdate:
            self.needStateUpdate = False
            self.entity.setMaterialName(self._getMaterialName())
            
        ObjectLine._updateView(self)
        
    def _getMaterialName(self):
        """Return material name for point object based on current state
        
        @return: material name
        @rtype: str
        """       
        return chem_env.material_state_pat % ("link_%s" % state_post[self.getState()])
