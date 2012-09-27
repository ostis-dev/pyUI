
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
Created on 19.11.2009

@author: Denis Koronchik
'''

import suit.core.kernel as core
import suit.core.objects as objects
import suit.core.render.engine as render_engine
import ogre.renderer.OGRE as ogre


# material postfixes
state_post = {objects.Object.OS_Normal: 'Normal',
              objects.Object.OS_Selected: 'Selected',
              objects.Object.OS_Highlighted: 'Highlighted',
              objects.Object.OS_WasInMemory: 'WasInMemory',
              objects.Object.OS_NewInMemory: 'NewInMemory',
              objects.Object.OS_Merged: 'Merged'}

class SCgNode(objects.ObjectDepth):
    """Class that represents realization of scg-node object.
    
    SCg-node has next scene node structure:
        Node:
        +---Entity 1
        ...
        +---Entity N
    To attach another objects you need to use child scene nodes. When object 
    state changed, then materials will be changed for all child objects (Entities), that why
    you can't attach another objects primary to scene node.
    """
    def __init__(self, sceneNode, type):
        """Constructor
        """
        objects.ObjectDepth.__init__(self, sceneNode)
        self.type = type
        
        self.needScaleUpdate = True
        
    def __del__(self):
        """Destructor
        """
        objects.ObjectDepth.__del__(self)
               
    def _onScAddrChanged(self, _addr_new, _addr_old):
        """Check if node have sc_addr in memory and change status
        """        
        pass
    
    def _getMaterialName(self):
        """Returns material name for node object based on state
        """         
        return "scg_Node_" + state_post[self.getState()]
    
    def _updateView(self):
        """Update object view
        """
        if self.needStateUpdate:
            self.needStateUpdate = False
            n = self.sceneNode.numAttachedObjects()
            mat_name = self._getMaterialName()
            for idx in xrange(n):
                object = self.sceneNode.getAttachedObject(idx)
                object.setMaterialName(mat_name)
            
        if self.needScaleUpdate:
            self.sceneNode.setScale(self.scale)
            self.needScaleUpdate = False
            
        if self.needModeUpdate:
            if render_engine.viewMode is render_engine.Mode_Perspective:
                self.sceneNode.setAutoTracking(True, render_engine._ogreCameraNode, ogre.Vector3(0, 0, 1))
            else:
                self.sceneNode.setAutoTracking(False)
                self.sceneNode.resetOrientation()
            self.needModeUpdate = False
            
        if self.needTextPositionUpdate:
            if self.text_obj:   self.text_obj.setPosition(self.position + self.scale * ogre.Vector3(0.125, -0.125, 0.125)) 
            self.needTextPositionUpdate = False
            
        objects.ObjectDepth._updateView(self)
                
    def _notifyModeChanged(self, _newMode, _oldMode):
        """Notification on mode changing
        """
        self.needModeUpdate = True
        self.needViewUpdate = True
    
    def getRadius(self):
        sz = self.getSize() / 2.0
        return max([sz.x, sz.y, sz.z])
    
    def _getCross(self, pos):
        """Count cross position
        @param pos:    Position for another end of line object
        """
        c = self.position#self.sceneNode.getPosition()
        v = pos - c
        sz = self.scale / 2.0
        radius = max([sz.x, sz.y, sz.z])
        v.normalise()
        return c + (v * radius * 1.1)
    
    def distance(self, ray):
        m = ogre.Matrix4() 
        self.getSceneNode().getWorldTransforms(m)
        p = ogre.Matrix4.getTrans(m)
        
        pl = ogre.Plane(ray.getDirection(),p)
        pr = ray.intersects(pl)
        if pr.first:
            d = ray.getPoint(pr.second)            
            return (d-p).length()
        
        return None
    
    def getType(self):
        return self.type
    
    def setType(self, type):
        self.type = type

        
        
# sc.g-pair
class SCgPair(objects.ObjectLine):
    """@change: 20.09.09 Class renamed from SCgLine to SCgPair
    
    Object that represents scg-pairs.
    
    It has specified structure of scene node.
        Node:
        +---Line
        +---Node begin arrow
            +---[Arrow begin]
        +---Node end arrow
            +---[Arrow end]
    You can attach just another scene objects to that. When state updates, then it 
    use current structure to change objects materials.    
    """
    
    vert3x = [-1, -1, -1, -1,
             -1, -1, 1, 1,
             1, 1, 1, 1,
             1, 1, -1, -1]
    vert3y = [0, 1, 1, 0,
              0, 1, 1, 0,
              0, 1, 1, 0,
              0, 1, 1, 0]
    vert3z = [1, 1, -1, -1,
             -1, -1, -1, -1,
             -1, -1, 1, 1,
             1, 1, 1, 1]
    
    norm3 = [(-1, 0, 0), (-1, 0, 0), (-1, 0, 0), (-1, 0, 0),
             (0, 0, 1), (0, 0, 1), (0, 0, 1), (0, 0, 1),
             (1, 0, 0), (1, 0, 0), (1, 0, 0), (1, 0, 0),
             (0, 0, -1), (0, 0, -1), (0, 0, -1), (0, 0, -1)]
    
    def __init__(self, sceneNode, materialName, lineEndsType, type):
        """Constructor
        @param sceneNode:    Ogre Scene node for line object
        """
        objects.ObjectLine.__init__(self, sceneNode)
        self.__manualObject = None
        self.__isDinamyc  = False
#        self.__sideCount = 2
        self.__materialName = 'scg_empty'
        self.__materialNameArr = 'scg_empty'
        self._lineEndsType = lineEndsType
        self.radius = 0.20
        self.length = 1.0
        self.__arrowLength = 2.5 * self.radius
        self.__arrowWidth = 2.0 * self.radius 
        
        # manual objects for arrows
        self.__manualObjectB = None
        self.__manualObjectE = None
        
        # scene nodes for arrows
        self.__sceneNodeBegin = None
        self.__sceneNodeEnd = None
        self.__sceneNode2d = render_engine.SceneManager.createSceneNode()
        self.__sceneNode3d = render_engine.SceneManager.createSceneNode()
        
        self.__entity3d = render_engine.SceneManager.createEntity("3d_" + str(self), "scg_line_seg.mesh")
        self.__sceneNode3d.attachObject(self.__entity3d)
        # array for arrow verts
        self.__arrowVerts = None
        # materials map
        self.materials = {}
        
        self.type = type
        # create arrows
        self._recreateArrows2d(True)
        # clone materials
        self.createMaterials()
        # orientation vector
        self.__orientV = None
        
        self.needUpdate = True
        self.needViewUpdate = True
        self.needStateUpdate = True
        
    def __del__(self):
        """Destructor
        """
        objects.ObjectDepth.__del__(self)
    
    def delete(self):
        # @todo: make thread safe
        #sceneMngr = render_engine._ogreSceneManager#core.Kernel.getSingleton().ogreSceneManager
        # destroying ogre objects
        if self.__manualObject:
            render_engine.SceneManager.destroyManualObject(self.__manualObject)
        if self.__manualObjectB:
            render_engine.SceneManager.destroyManualObject(self.__manualObjectB)
        if self.__manualObjectE:
            render_engine.SceneManager.destroyManualObject(self.__manualObjectE)
        if self.__sceneNodeBegin:
            render_engine.SceneManager.destroySceneNode(self.__sceneNodeBegin)
        if self.__sceneNodeEnd:
            render_engine.SceneManager.destroySceneNode(self.__sceneNodeEnd)
        
        render_engine.SceneManager.destroySceneNode(self.__sceneNode2d)
        render_engine.SceneManager.destroySceneNode(self.__sceneNode3d)
        render_engine.SceneManager.destroyEntity(self.__entity3d)
        
        self.destroyMaterials()
            
        objects.ObjectLine.__del__(self)    

            
    def getType(self):
        return self.type
    
    def setType(self, _type):        
        """Sets line type
        
        @warning: function is not thread safe, so you need to be care to use it
        """
        # destroying ogre objects
        if self.__manualObjectB:
            self.__sceneNodeBegin.detachObject(self.__manualObjectB)
            render_engine.SceneManager.destroyManualObject(self.__manualObjectB)
            self.__manualObjectB = None
            
        if self.__manualObjectE:
            self.__sceneNodeEnd.detachObject(self.__manualObjectE)
            render_engine.SceneManager.destroyManualObject(self.__manualObjectE)
            self.__manualObjectE = None

        self.type = _type
        self.needViewUpdate = True
        self.needStateUpdate = True
        self.needUpdate = True
    
    def _getCross(self, pos):
        v = pos - self.position
        v.normalise()
        return self.position + v * self.radius
    
    def createMaterials(self):
        """Create clone of materials for scaling them
        """
        for key, value in state_post.iteritems():
            matr = ogre.MaterialManager.getSingleton().getByName("scg_%s_%s" % (self.type, value))
            
            c_matr = matr.clone("scg_%s_%s_%s" % (self.type, value, str(self)))
            self.materials[key] = c_matr
    
    def destroyMaterials(self):
        """Destroys material clones
        """
        for matr in self.materials.itervalues():
            ogre.MaterialManager.getSingleton().remove(matr)
        self.materials = {}
    
    def _getMaterialName2d(self):
        """Returns material name for pair object based on state
        """
        return "scg_%s_%s_%s" % (self.type, state_post[self.getState()], str(self))
    
    def _getMaterialName3d(self):
        """Returns material name for a pair in 3d mode based on state
        """
        return "scg_%s" % state_post[self.getState()]
    
    def _getMaterialNameArr(self):
        """Returns material name for arrow object based on state
        """
        return "scg_arrow_" + state_post[self.getState()]   

    def _update(self, timeSinceLastFrame):
        """Update line. Creates new geometry.
        Don't need to synchronize that function, because it calls from main thread,
        so we can use ogre directly
        """
        
        if self.needViewUpdate: self._updateView()
        
        if (not self.needUpdate):
#            self._rotateToCamera()
            return
        
        if self.beginObject is None or self.endObject is None:
            return
        
        if self.beginObject is not None and self.beginObject.needUpdate:
            self.beginObject._update(timeSinceLastFrame)
        if self.endObject is not None and self.endObject.needUpdate:
            self.endObject._update(timeSinceLastFrame)
        
        
        if render_engine.viewMode is render_engine.Mode_Isometric:
            sceneMngr = render_engine._ogreSceneManager
            # recreate geometry
            if (self.__manualObject is None):
                #sceneMngr.destroyManualObject(self.__manualObject)
                self.__manualObject = sceneMngr.createManualObject(str(self))
                self.__manualObject.setDynamic(self.__isDinamyc)
                # attach to scene node
                self.__sceneNode2d.attachObject(self.__manualObject)
            self._updateGeometry(False)
        else:
            sceneMngr = render_engine._ogreSceneManager
            # recreate geometry
            if (self.__manualObject is None):
                #sceneMngr.destroyManualObject(self.__manualObject)
                self.__manualObject = sceneMngr.createManualObject(str(self))
                self.__manualObject.setDynamic(self.__isDinamyc)
                # attach to scene node
                self.__sceneNode2d.attachObject(self.__manualObject)
            self._updateGeometry3d()
#        self._rotateToCamera()
        #self.__manualObject.setMaterialName(0, 'empty')
        
        self.needUpdate = False
           
    def _updateView(self):
        """Update object view
        
        Updating object materials based on state.
        """
        objects.ObjectDepth._updateView(self)
        
        if self.needStateUpdate:
            # need to recreate materials
            self.destroyMaterials()
            self.createMaterials()
            
            #if render_engine.viewMode is render_engine.Mode_Isometric:
            if self.__manualObject is not None:
                self.needStateUpdate = False
                self.__materialName = self._getMaterialName2d()
                self.__materialNameArr = self._getMaterialNameArr()
                if self.__manualObject.getNumSections() > 0:
                    self.__manualObject.setMaterialName(0, self.__materialName)
                if self.__manualObjectB is not None: 
                    self.__manualObjectB.setMaterialName(0, self.__materialNameArr)
                if self.__manualObjectE is not None:
                    self.__manualObjectE.setMaterialName(0, self.__materialNameArr)
            else:
                self.needUpdate = True
                self.needViewUpdate = True
            #else:
            #    self.needStateUpdate = False
#                self.__entity3d.setMaterialName(self._getMaterialName3d())
                
            self._recalculateMaterial()
        
        # mode updating
        if self.needModeUpdate:
            
            if render_engine.viewMode is render_engine.Mode_Perspective:
                self.sceneNode.removeChild(self.__sceneNode2d)
#                self.sceneNode.addChild(self.__sceneNode3d)
                self.sceneNode.addChild(self.__sceneNode2d)
            else:
#                self.sceneNode.removeChild(self.__sceneNode3d)
                self.sceneNode.removeChild(self.__sceneNode2d)
                self.sceneNode.addChild(self.__sceneNode2d)
            
            self.needModeUpdate = False
            
        if render_engine.viewMode is render_engine.Mode_Perspective and self.__orientV is not None:
            p1 = self.sceneNode.getPosition()# + self.__orientV / 2.0
            lookVec = p1 - render_engine._ogreCameraNode.getPosition()
            #upVec = render_engine._ogreCamera.getUp()
            
            orient = self.__orientV
            orient.normalise()
            
            rightVec = orient.crossProduct(lookVec)
            rightVec.normalise()
            lookVec = rightVec.crossProduct(orient)
            lookVec.normalise()
            
            matr = ogre.Matrix3()
            matr.FromAxes(rightVec, orient, lookVec)
            orientation = ogre.Quaternion()
            orientation.FromRotationMatrix(matr)
            orientation.normalise()
            #print orientation
            
            #self.sceneNode.setDirection(orient, ogre.SceneNode.TS_PARENT, [0, 1, 0])
            self.sceneNode.setOrientation(orientation)
            
           
        # do not update position
        self.needPositionUpdate = False
        
    def _updateGeometry3d(self):
        """Updates geometry for a 3d mode
        """
        if (not self.__manualObject):
            raise AssertionError('Invalid manual object')
        
        if ((self.__manualObject.getDynamic()) and (self.__manualObject.getNumSections() > 0)):
            self.__manualObject.beginUpdate(0)
        else:
            self.__manualObject.clear()
            self.__manualObject.begin(self.__materialName)
          
        op1 = self.beginObject.getPosition()
        op2 = self.endObject.getPosition()
        
        p1 = self.beginObject._getCross(op2)
        p2 = self.endObject._getCross(op1)
        
        self.begin_pos = p1
        self.end_pos = p2

        self.position = (p1 + p2) / 2.0

        length = p1.distance(p2)
        if length < 0.001:
            length = 0.001
        # begin arrow offset
        offsetY = 0
        # we doesn't need to update begin arrow coordinates
        # just update end arrow
        if (self._lineEndsType == objects.ObjectLine.LET_BOTH):
            length = length - self.__arrowLength * 2
            offsetY = self.__arrowLength
            self.__sceneNodeEnd.setPosition(ogre.Vector3(0, length + self.__arrowLength, 0))
        else:
            if (self._lineEndsType == objects.ObjectLine.LET_BEGIN):
                length = length - self.__arrowLength
                offsetY = self.__arrowLength
            if (self._lineEndsType == objects.ObjectLine.LET_END):
                length = length - self.__arrowLength
                self.__sceneNodeEnd.setPosition(ogre.Vector3(0, length, 0))
                
        # check mode and generate geometry depending on it
        if render_engine.viewMode == render_engine.Mode_Perspective:
            
            self.__manualObject.position(-self.radius, 0.0, 0.0)
            self.__manualObject.textureCoord(0.0, 0.0)
            self.__manualObject.normal(0, 0, 1)
            
            self.__manualObject.position(-self.radius, length, 0.0)
            self.__manualObject.textureCoord(1.0, 0.0)
            self.__manualObject.normal(0, 0, 1)
            
            self.__manualObject.position(self.radius, length, 0.0)
            self.__manualObject.textureCoord(1.0, 1.0)
            self.__manualObject.normal(0, 0, 1)
            
            self.__manualObject.position(self.radius, 0.0, 0.0)
            self.__manualObject.textureCoord(0.0, 1.0)
            self.__manualObject.normal(0, 0, 1)
            
            self.__manualObject.quad(0, 1, 2, 3)
            
        # ends building of manual object
        self.__manualObject.end()

        self.__orientV = p2 - p1
        self.sceneNode.setPosition(p1)
        #self.sceneNode.setDirection(self.__orientV, ogre.SceneNode.TS_PARENT, [0, 1, 0])      
       
#        self.__manualObject.setRenderQueueGroup(ogre.RENDER_QUEUE_OVERLAY - 1)
        self.length = length
        self._recalculateMaterial()
#        op1 = self.beginObject.getPosition()
#        op2 = self.endObject.getPosition()
#    
#        p1 = self.beginObject._getCross(op2)
#        p2 = self.endObject._getCross(op1)
#        
#        self.begin_pos = p1
#        self.end_pos = p2
#        
#        self.position = (p1 + p2) / 2.0
#        
#        # rotating and scaling line
#        orientV = p2 - p1
#        self.sceneNode.setPosition(p1)
#        l = orientV.length()
#        if l < 0.1:
#            self.sceneNode.setDirection(ogre.Vector3(1, 1, 0), ogre.SceneNode.TS_PARENT, [0, 1, 0])
#        else:
#            self.sceneNode.setDirection(orientV, ogre.SceneNode.TS_PARENT, [0, 1, 0])
#        self.__sceneNode3d.setScale(ogre.Vector3(self.radius * 0.5, l, self.radius * 0.5))
#        
#        self.length = l
        
        
    def _updateGeometry(self, countNormals = False):
        """Updates geometry.
        Don't need to synchronize that function, because it calls from main thread,
        so we can use ogre directly
        @todo: move vCoreVerts array to attributes to
            making minimum updates, just when we need
        @todo: make calculation for length < 1 
        """ 
        if (not self.__manualObject):
            raise AssertionError('Invalid manual object')
        
        if ((self.__manualObject.getDynamic()) and (self.__manualObject.getNumSections() > 0)):
            self.__manualObject.beginUpdate(0)
        else:
            self.__manualObject.clear()
            self.__manualObject.begin(self.__materialName)
          
        op1 = self.beginObject.getPosition()
        op2 = self.endObject.getPosition()
        
        p1 = self.beginObject._getCross(op2)
        p2 = self.endObject._getCross(op1)
        
        self.begin_pos = p1
        self.end_pos = p2

        self.position = (p1 + p2) / 2.0

        length = p1.distance(p2)
        if length < 0.001:
            length = 0.001
        # begin arrow offset
        offsetY = 0
        # we doesn't need to update begin arrow coordinates
        # just update end arrow
        if (self._lineEndsType == objects.ObjectLine.LET_BOTH):
            length = length - self.__arrowLength * 2
            offsetY = self.__arrowLength
            self.__sceneNodeEnd.setPosition(ogre.Vector3(0, length + self.__arrowLength, 0))
        else:
            if (self._lineEndsType == objects.ObjectLine.LET_BEGIN):
                length = length - self.__arrowLength
                offsetY = self.__arrowLength
            if (self._lineEndsType == objects.ObjectLine.LET_END):
                length = length - self.__arrowLength
                self.__sceneNodeEnd.setPosition(ogre.Vector3(0, length, 0))
                
        # check mode and generate geometry depending on it
        if render_engine.viewMode == render_engine.Mode_Isometric:
            
            self.__manualObject.position(-self.radius, 0.0, 0.0)
            self.__manualObject.textureCoord(0.0, 0.0)
            self.__manualObject.normal(0, 0, 1)
            
            self.__manualObject.position(-self.radius, length, 0.0)
            self.__manualObject.textureCoord(1.0, 0.0)
            self.__manualObject.normal(0, 0, 1)
            
            self.__manualObject.position(self.radius, length, 0.0)
            self.__manualObject.textureCoord(1.0, 1.0)
            self.__manualObject.normal(0, 0, 1)
            
            self.__manualObject.position(self.radius, 0.0, 0.0)
            self.__manualObject.textureCoord(0.0, 1.0)
            self.__manualObject.normal(0, 0, 1)
            
            self.__manualObject.quad(0, 1, 2, 3)
            
        # ends building of manual object
        self.__manualObject.end()

        self.__orientV = p2 - p1
        self.sceneNode.setPosition(p1)
        self.sceneNode.setDirection(self.__orientV, ogre.SceneNode.TS_PARENT, [0, 1, 0])
       
#        self.__manualObject.setRenderQueueGroup(ogre.RENDER_QUEUE_OVERLAY - 1)
        self.length = length
        self._recalculateMaterial()
    
    def _recalculateMaterial(self):
        """Recalculates material depending on line length
        """
        # calculate new scale for material
        matr = self.materials[self.getState()]
        sc = 1.0
        if self.length > 0:
            sc = 1.0 / self.length
        matr.getTechnique(0).getPass(0).getTextureUnitState(0).setTextureUScale(sc)

        
    def _recreateArrows2d(self, countNormals = False):
        """Recreate arrows geometry.
        Don't need to synchronize that function, because it calls from main thread,
        so we can use ogre directly.
        """ 
        sceneMngr = render_engine._ogreSceneManager
        # clear old geometry
        if (self.__manualObjectB):
            self.__manualObjectB.clear()
        if (self.__manualObjectE):
            self.__manualObjectE.clear()
        
        vertx = [-1, 0, 1]
        verty = [0, 1, 0]
            
        # BEGIN ARROW
        if (self._lineEndsType == objects.ObjectLine.LET_BEGIN or
            self._lineEndsType == objects.ObjectLine.LET_BOTH):
            # create new begin arrow geometry
            if not self.__manualObjectB:
                self.__manualObjectB = sceneMngr.createManualObject(str(self) + 'b')
                self.__manualObjectB.setDynamic(self.__isDinamyc)
            
            # filling arrow geometry
            if ((not self.__manualObjectB.getDynamic()) and (self.__manualObjectB.getNumSections() > 0)):
                self.__manualObjectB.beginUpdate(0)
            else:
                self.__manualObjectB.begin(self.__materialNameArr)

            for v in xrange(3):
                self.__manualObjectB.position(vertx[v] * self.__arrowWidth / 2.0, -verty[v] * self.__arrowLength, 0)
                if countNormals:    self.__manualObjectB.normal(0, 0, 1)
            self.__manualObjectB.triangle(2, 1, 0)
            
               
            self.__manualObjectB.end()
            # create scene node
            self.__sceneNodeBegin = sceneMngr.createSceneNode()
            self.__sceneNodeBegin.attachObject(self.__manualObjectB)
            self.__sceneNode2d.addChild(self.__sceneNodeBegin)
               
        # END ARROW       
        if (self._lineEndsType == objects.ObjectLine.LET_END or
            self._lineEndsType == objects.ObjectLine.LET_BOTH):
            # create new end arrow geometry
            if not self.__manualObjectE:
                self.__manualObjectE = sceneMngr.createManualObject(str(self) + 'e')
                self.__manualObjectE.setDynamic(self.__isDinamyc)
            
            # filling arrow geometry
            if ((not self.__manualObjectE.getDynamic()) and (self.__manualObjectE.getNumSections() > 0)):
                self.__manualObjectE.beginUpdate(0)
            else:
                self.__manualObjectE.begin(self.__materialNameArr)


            for v in xrange(3):
                self.__manualObjectE.position(vertx[v] * self.__arrowWidth / 2.0, verty[v] * self.__arrowLength, 0)
                if countNormals:    self.__manualObjectE.normal(0, 0, 1)
            self.__manualObjectE.triangle(2, 1, 0)
               
            self.__manualObjectE.end()
            # create scene node
            self.__sceneNodeEnd = sceneMngr.createSceneNode()
            self.__sceneNodeEnd.attachObject(self.__manualObjectE)
            self.__sceneNode2d.addChild(self.__sceneNodeEnd)


class SCgBus(objects.ObjectDepth):
    
    def __init__(self, sceneNode):
        objects.ObjectDepth(self, sceneNode)
        
    def __del__(self):
        pass
    
    def delete(self):
        pass
    
    
class SCgContour(objects.ObjectDepth):
    
    def __init__(self, sceneNode):
        objects.ObjectDepth.__init__(self, sceneNode)
        
        self.needGeometryUpdate = False
        self.points = []
        
        self.width = 0.15   # contour line width
        self.__manualObject = None  # manual object to store and render geometry
        
    def __del__(self):
        objects.ObjectDepth.__del__(self)
    
    def delete(self):
        
        if self.__manualObject:
            render_engine.SceneManager.destroyManualObject(self.__manualObject)
        
        objects.ObjectDepth.delete(self)
        
    def appendPoint(self, point):
        """Appends point to the end of points list
        @param point:    point for appending
        @type point:    ogre.Vector3
        """
        self.points.append(point)
        self.needGeometryUpdate = True
        
    def setPoints(self, points):
        """Sets contour points
        @param points:    list of points (ogre.Vector3)
        @type points:    list
        """
        self.points = []
        self.points.extend(points)
        
        self.needGeometryUpdate = True
        
    def _getMaterialName(self):
        """Returns material name for node object based on state
        """
        return "scg_Node_" + state_post[self.getState()]
    
    def _getCross(self, pos):
        return self.position
    
            
    def _checkRayIntersect(self, ray):
        """Check if ray intersects object
        @see: objects.ObjectDepth._checkRayIntersect
        """
        res = ogre.Math.intersects(ray, self.sceneNode._getWorldAABB())
        rvalue, pos = objects.ObjectDepth._checkRayIntersect(self, ray) 
        
        if not rvalue:
            return False, -1
        
        # works just for a isometric mode
        m = ogre.Matrix4() 
        self.getSceneNode().getWorldTransforms(m)
        p = ogre.Matrix4.getTrans(m)
        
        pl = ogre.Plane(ray.getDirection(), p)
        pr = ray.intersects(pl)
        if not pr.first:
            return False, -1
        
        d = ray.getPoint(pr.second)
        
        rvalue = False
        for idx in range(len(self.points)):
            p2 = self.points[idx] + p
            p1 = self.points[idx - 1] + p
            if (((p2.y <= d.y and d.y < p1.y) or (p1.y <= d.y and d.y < p2.y)) and \
                (d.x > (p1.x - p2.x) * (d.y - p2.y) / (p1.y - p2.y) + p2.x)):
                rvalue = not rvalue
                    
        return rvalue, 0

    
    def _update(self, timeSinceLastFrame):
        """Update contour. Creates new geometry.
        Don't need to synchronize that function, because it calls from main thread,
        so we can use ogre directly
        """
        
        objects.ObjectDepth._update(self, timeSinceLastFrame)
        
        if self.needGeometryUpdate:
            self.needGeometryUpdate = False
            self._updateGeometry()
        
    def _updateView(self):
        """Update object view
        
        Updating object materials based on state.
        """
        if self.needStateUpdate and self.__manualObject is not None:
            self.needStateUpdate = False
            self.__manualObject.setMaterialName(0, self._getMaterialName())
            self.needGeometryUpdate = True
        
        objects.ObjectDepth._updateView(self)
    
    def _updateGeometry(self):
        """Updates contour geometry
        """
        
        if not len(self.points) > 0:
            return
        
        if self.__manualObject is None:
            self.__manualObject = render_engine._ogreSceneManager.createManualObject(str(self))
            self.__manualObject.setDynamic(True)
            self.sceneNode.attachObject(self.__manualObject)
            self.__manualObject.begin(self._getMaterialName())
        else:
            self.__manualObject.beginUpdate(0)
            
        
        length = 0
        n = len(self.points) - 1
        # calculate contour length
        for idx in range(n):
            length += self.points[idx].distance(self.points[idx + 1])
        
        # create geometry
        w2 = self.width * 0.5
        l = 0
        for idx in range(-1, n):
            p0 = self.points[idx - 1]
            p1 = self.points[idx]
            p2 = self.points[idx + 1]
            
            v1 = p0 - p1
            v2 = p2 - p1
            
            # get joint points direction
            v1.normalise()
            v2.normalise()
            v = v1 + v2
            #v.normalise()
            v =  v * w2
            
            tcx = l / length 
            
            self.__manualObject.position(p1 + v)
            self.__manualObject.textureCoord(tcx, 0)
            self.__manualObject.normal(0, 0, 1)
            #self.__manualObject.colour(1, 1, 1, 1)
           
            self.__manualObject.position(p1 - v)
            self.__manualObject.textureCoord(tcx, 1)
            self.__manualObject.normal(0, 0, 1)
            #self.__manualObject.colour(1, 1, 1, 1)
                                  
            l += p1.distance(p2)
            
        # create quads
        for idx in range(n):
            idx1 = idx * 2
            self.__manualObject.quad(idx1, idx1 + 1, idx1 + 3, idx1 + 2)
        self.__manualObject.quad(n*2, n*2 + 1, 1, 0)
        self.__manualObject.end()
         