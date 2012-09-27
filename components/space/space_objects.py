
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
Created on 11.02.2010

@author: Jake, Grechishkin Pavel
'''
import ogre.renderer.OGRE as ogre
import suit.core.objects as objects
import ogre.io.OIS as ois
import suit.core.kernel as core
import suit.core.render.engine as render_engine
import math

# material postfix
state_post = {objects.Object.OS_Normal: '_Normal',
              objects.Object.OS_Selected: '_Selected',
              objects.Object.OS_Highlighted: '_Highlighted',
              objects.Object.OS_WasInMemory: '_Normal',
              objects.Object.OS_NewInMemory: '_Normal',
              objects.Object.OS_Merged: '_Normal'}

title2material = {'Земля'.encode('cp1251'): 'Earth'.encode('cp1251'),
                  'Венера'.encode('cp1251'): 'Venus'.encode('cp1251'),
                  'Меркурий'.encode('cp1251'): 'Mercury'.encode('cp1251')}

pi2 = math.pi * 2

class SpaceObject(objects.ObjectDepth):
    def __init__(self, sceneNode, parent = None, A = 0, B = 0, orbRelCenterPos = (0,0,0), year = 0, day = 0, title = None,
                 scale = 1.0, properties = None):
        """constructor
        """
        objects.ObjectDepth.__init__(self)
        self.sceneNode.addChild(sceneNode)
        self.sceneNode2 = sceneNode
        self.orbA = A
        self.orbB = B
        self.orbRelCenterPos = (0,0,0)
        self.orbParent = parent
        self.year = float(year)
        self.day = float(day)

        self.__childObjects = []
        self.__relSceneNodes = dict()
        self.scale = scale
        self.sceneNode2.setScale(scale, scale, scale)

        self.setText(title)
        self.title = title
        self.ray = None
        self.properties = properties
        self.time_year = 0
        self.time_day = 0
                       

    def __del__(self):
        sceneManager = core.Kernel.getSingleton().ogreSceneManager
        
#        if self.orbAnimState.hasEnabled():  core.Kernel.getSingleton().removeAnimation(self.orbAnimState)
#        if self.spinAnimState.hasEnabled():  core.Kernel.getSingleton().removeAnimation(self.spinAnimState)
#        
#        if self.animation_orb:  sceneManager.destroyAnimation(self.animation_orb)
#        if self.animation_spin: sceneManager.destroyAnimation(self.animation_spin)
#        if self.orbAnimState:   sceneManager.destroyAnimationState(self.orbAnimState)
#        if self.spinAnimState:  sceneManager.destroyAnimationState(self.spinAnimState)
           
        
        objects.ObjectDepth.__del__(self)
        
    def _update(self, _timeSinceLastFrame):
        objects.ObjectDepth._update(self, _timeSinceLastFrame)
        
        if not self.year == 0:
            self.time_year += _timeSinceLastFrame
            if self.time_year > self.year:
                self.time_year -= self.year
            # calculate object
            an = pi2 * float(self.time_year) / self.year
            self.setPosition(ogre.Vector3(self.orbA * math.cos(an), 0, self.orbB * math.sin(an)))

        if not self.day == 0:
            self.time_day += _timeSinceLastFrame
            if self.time_day > self.day:
                self.time_day -= self.day
            self.sceneNode.setOrientation(ogre.Quaternion(ogre.Radian(pi2 * self.time_day / self.day), ogre.Vector3(0, 1, 0)))
            
        # update child objects
        childs = self.getChilds()
        for child in childs:
            child._update(_timeSinceLastFrame)
                
    def _updateView(self):
        """Update object view
        """        
        updateList = []
        childs = self.getChilds()
        for child in childs:
            if child.needStateUpdate:
                updateList.append(child)
        
        if updateList:
            for space_object in updateList:
                
                space_object.needStateUpdate = False
                n = space_object.sceneNode2.numAttachedObjects()
                mat_name = space_object._getMaterialName()
                for idx in xrange(n):
                    object = space_object.sceneNode2.getAttachedObject(idx)
                    object.setMaterialName(mat_name)
                 
        objects.ObjectDepth._updateView(self)
    
    def _getMaterialName(self):
        """Returns material name for node object based on state
        """
        title = self.getText() 
        if title is not None:
            return "space/" + title2material[title] + state_post[self.getState()]
        else:
            return "space/None"
        

    def addChildList(self, childs):
        """Adds list of child objects
        @see: FlyObject.addChild
        """
        for child in childs:
            self.addChild(child)
    
    def addChild(self, child):
        """Adds child object
        """
        if (child in self.__childObjects):
            raise AssertionError('Child object already exists. Please use \'haveChild\' method')
        # register object in childs        
        self.__childObjects.append(child)
        # remove old parent
        if child.parent is not None:
            childparent.removeChild(child)
        child.parent = self 
        
        kernel = core.Kernel.getSingleton()
        sceneManager = render_engine._ogreSceneManager    
        sn = sceneManager.createSceneNode()
        sn.addChild(child.sceneNode)
        self.__relSceneNodes[child] = sn
        self.sceneNode.addChild(sn)
    
    def removeChildList(self, childs):
        """Removes list of child objects
        @see: FlyObject.removeChild
        """
        for child in childs:
            self.removeChild(child)
    
    def removeChild(self, child):
        """Removes child object from sheet
        """
        child.parent = None
        self.__childObjects.remove(child)
        self.sceneNode.removeChild(self.__relSceneNodes[child])
        self.__relSceneNodes[child] = None 
        
    def haveChild(self, child):
        """Check if child object already exists
        """
        return self.__childObjects.count(child) > 0
    
    def getChilds(self):
        """Returns list of existing childs 
        """        
        return self.__childObjects
    
    def getChildsRecursively(self):
        res = []
        res.extend(self.__childObjects)
        for child in self.__childObjects:
            res.extend(child.getChildsRecursively())
        return res
    
    def rotateOrb(self, child, angle, vec):
        if child in self.__childObjects:
            sn = self.__relSceneNodes[child]
            sn.rotate(vec,angle)
    
    def _getObjectsUnderMouse(self, sortDistance = True, forced = False, mpos = None):
        """Returns objects under mouse. By default it's caching results for frame, but
        if you need to find objects anyway, then set forced parameter to True.
        @warning: You must be accurate with using this function. It's not thread safe, because
        it gets mouse state
        @param forced: flag to force finding
        @type forced: bool  
        @param sortDistance: flag to sort founded object by distance from near to far
        @type sortDistance: bool 
        @param mpos: mouse position. If you set it to None, then mouse position will be given for
        current mouse state. If you set parameters to None, then it will be work in forced mode
        automatically.
        @type mpos: tuple (x, y)  
        @return: list of tuples (distance, object)
        @rtype: tuple
        """
        founded = []
        if  forced or mpos is not None:
            # building intersection ray 
            if mpos is None:
                mstate = render_engine._getMouseState()
                self.ray = render_engine.pos2dToViewPortRay((mstate.X.abs, mstate.Y.abs))
            else:
                self.ray = render_engine.pos2dToViewPortRay(mpos)
            #x = mstate.X.abs / float(mstate.width)
            #y = mstate.Y.abs / float(mstate.height)
            # iterating through objects and finding intersections
            
            for child in self.__childObjects:
                founded = founded + child._getObjectsUnderMouse(True, True)
                res, dist = child._checkRayIntersect(self.ray)
                if res:
                    founded.append((dist, child))
            
            if sortDistance: 
                founded.sort()
            
        return founded
    
    def _checkRayIntersect(self, ray):
        """Check if ray intersects object
        @param ray: ray to check intersection with
        @type ray: ogre.Ray  
        @returns tuple (intersection result, intersection point)
        """
        res = ogre.Math.intersects(ray, self.sceneNode2._getWorldAABB())
       
#        if res.first is True:
#            ogre.SceneNode.showBoundingBox(self.sceneNode2, True)
        return res.first, ray.getPoint(res.second)   
