
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
Created on 24.11.2009

@author: Denis Koronchick

Modified on 8.04.2010
by Maxim Kaskevich
'''

import suit.core.objects
import suit.core.exceptions
import suit.core.render.engine as render_engine
import ogre.renderer.OGRE as ogre
import graph_env

state_post = {suit.core.objects.Object.OS_Normal: 'Normal',
              suit.core.objects.Object.OS_Selected: 'Selected',
              suit.core.objects.Object.OS_Highlighted: 'Highlighted'}

class GraphVertex(suit.core.objects.ObjectDepth):
    """Object that represents graph point
    
    @warning: creation of this object need be synchronized
    """
    def __init__(self):
        suit.core.objects.ObjectDepth.__init__(self, None)
        
        # creating entity
        self.entity = render_engine.SceneManager.createEntity("GraphVertex_" + str(self), graph_env.mesh_point)
        self.sceneNode.attachObject(self.entity)
     
    
    def __del__(self):
        suit.core.objects.ObjectDepth.__del__(self)
        render_engine.SceneManager.destroyEntity(self.entity)
        
    def _getMaterialName(self):
        """Return material name for point object based on current state
        
        @return: material name
        @rtype: str
        """
        return graph_env.material_state_pat % ("object_%s" % (state_post[self.getState()]))
        
        
    def _updateView(self):
        """View update function
        
        Updates state for object
        """
        if self.needStateUpdate:
            self.needStateUpdate = False
            self.entity.setMaterialName(self._getMaterialName())
#            if state_post[self.getState()] == "Selected":
#                self.sceneNode.showBoundingBox(True)
#            else:
#                self.sceneNode.showBoundingBox(False)

        suit.core.objects.ObjectDepth._updateView(self)
        
    def get_idtf(self):
        """Returns object identificator.
        It parse structures like: Point(A), Point A, pA and return A
        """
        #FIXME:    add parsing for Point(A), Point A and etc. structures
        idtf = self.getText()
        if idtf is None or len(idtf) == 0:
            idtf = str(self)[-9:-2] # FIXME:    make identification more useful
            
        return idtf
        

class GraphLink(suit.core.objects.ObjectLine):
    """Object that represents graph line section
    """
    def __init__(self, haveArrow = True):
        suit.core.objects.ObjectLine.__init__(self, None)
        
        # creating entity
        self.entity = render_engine.SceneManager.createEntity("graph_lsection_%s" % str(self), graph_env.mesh_lsect)
        sceneMngr = render_engine._ogreSceneManager
        self.sceneNodeLine = sceneMngr.createSceneNode()
        self.sceneNode.addChild(self.sceneNodeLine)

        self.sceneNodeLine.attachObject(self.entity)
        self.__sceneNodeEnd = None
        
    def __del__(self):
        suit.core.objects.ObjectLine.__del__(self)
        render_engine.SceneManager.destroyEntity(self.entity)
        
        
    def setArrowEnabled(self, en):
        self.__haveArrow = en
        
    def _getMaterialName(self):
        """Returns material name based on object state
        """
        return graph_env.material_state_pat % ("object_%s" % (state_post[self.getState()]))
        
    def _update(self, _timeSinceLastFrame):
        
        # updating graph
        if self.needUpdate:
            op1 = self.beginObject.getPosition()
            op2 = self.endObject.getPosition()
        
            p1 = self.beginObject._getCross(op2)
            p2 = self.endObject._getCross(op1)
            
            self.begin_pos = p1
            self.end_pos = p2


            
            # rotating and scaling line
            orientV = p2 - p1
            self.sceneNode.setPosition(p1)
            l = orientV.length()
            if l < 0.1:
                self.sceneNode.setDirection(ogre.Vector3(1, 1, 0), ogre.SceneNode.TS_PARENT, [0, 1, 0])
            else:
                self.sceneNode.setDirection(orientV, ogre.SceneNode.TS_PARENT, [0, 1, 0])
            self.sceneNode.setScale(ogre.Vector3(self.radius * 2, l, self.radius * 2))
            
                
            # update identificator position
            if self.begin_pos and self.end_pos and self.text_obj:
                self.text_obj.setPosition((self.begin_pos + self.end_pos) / 2.0 + self.radius * 1.2 * ogre.Vector3(1.0, 1.0, 0.0))
                self.needUpdate = False
            else:
                self.needUpdate = True
            
        suit.core.objects.ObjectLine._update(self, _timeSinceLastFrame)
                       
    def _updateView(self):
        """View update function
        
        Updates state for object
        """
        if self.needStateUpdate:
            self.needStateUpdate = False
            self.entity.setMaterialName(self._getMaterialName())
            
        suit.core.objects.ObjectDepth._updateView(self)
     
    def get_idtf(self):
        """Returns object identificator.
        It parse structures like: Point(A), Point A, pA and return A
        """
        #FIXME:    add parsing for Point(A), Point A and etc. structures
        idtf = self.getText()
        if idtf is None or len(idtf) == 0:
            return None
            
        return idtf
     
