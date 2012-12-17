
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
'''

import suit.core.objects
import suit.core.exceptions
import suit.core.render.engine as render_engine
import geom_env
import math
import ogre.renderer.OGRE as ogre

state_post = {suit.core.objects.Object.OS_Normal: 'Normal',
              suit.core.objects.Object.OS_Selected: 'Selected',
              suit.core.objects.Object.OS_Highlighted: 'Highlighted',
              suit.core.objects.Object.OS_WasInMemory: 'WasInMemory',
              suit.core.objects.Object.OS_NewInMemory: 'NewInMemory',
              suit.core.objects.Object.OS_Merged: 'Merged'}    

class GeometryAbstractObject:
    
    groups = {}
    
    PropSquare = u"Площадь"
    PropPerimeter = u"Периметр"
    PropLength = u"Длина"
        
    def __init__(self):
        # list of child points (begin and end points are excluded)
        # that list contains tuples. Each tuple contains point and it position.
        # Position calculates like (distance(pBegin - p) / length(pEnd - p Begin)),
        # where p - point coordinates, pBegin, pEnd - begin/end point coordinates.
        # This mechanism used for circles and other objects. It works like dot point in scg.
        self.points = []
        
        self.equalGroup = None
        
        if not GeometryAbstractObject.groups.has_key(self.__class__):
            GeometryAbstractObject.groups[self.__class__] = {}
            
        self.properties = {}    # object properties
    
    def __del__(self):
        pass
    
    def delete(self):
        self.setEqualGroup(None)
    
    def setEqualGroup(self, newGroup):
        """Set new equivalence group
        """
        if self.equalGroup is not None:
            GeometryAbstractObject.groups[self.__class__][self.equalGroup].remove(self)
            if len(GeometryAbstractObject.groups[self.__class__][self.equalGroup]) == 0:
                GeometryAbstractObject.groups[self.__class__].pop(self.equalGroup)
        
        self.equalGroup = newGroup
        
        if self.equalGroup is not None:
            if not GeometryAbstractObject.groups[self.__class__].has_key(self.equalGroup):
                GeometryAbstractObject.groups[self.__class__][self.equalGroup] = [self]
            else:
                GeometryAbstractObject.groups[self.__class__][self.equalGroup].append(self)
    
    def getEqualGroup(self):
        """Return object equal group
        """
        return self.equalGroup
    
    def setEqualTo(self, _object):
        """Set current object equivalence to specified \p _object
        """
        selGroup = _object.getEqualGroup()
        if self.equalGroup is None and selGroup is None:
            _equalGroup = self.getAvailableEqualGroup()
            self.setEqualGroup(_equalGroup)
            _object.setEqualGroup(_equalGroup)
        elif self.equalGroup is not None and selGroup is None:
            _object.setEqualGroup(self.equalGroup)
        elif self.equalGroup is None and selGroup is not None:
            self.setEqualGroup(_object.getEqualGroup())
        else:
            return # do nothing
        
    def getPropertiesAsString(self):
        """Return all properties of object in a one string
        """
        res = u"Идентификатор:" + "\n  %s\n" % self.getIdtf()
        
        if self.points is not None and len(self.points) > 0:
            res += u"Точки:\n"
            for idx in xrange(len(self.points)):
                if idx != 0:
                    res += ",\n"
                res += "  " + self.points[idx][0].getIdtf()
            res += "\n"
        
        if self.equalGroup is not None:
            res += u"Конгруэнтность:\n"
            
            objs = GeometryAbstractObject.groups[self.__class__][self.equalGroup]
            
            added = 0
            for idx in xrange(len(objs)):
                
                if objs[idx] is self: continue
                
                if added != 0:
                    res += ",\n"
                res += "  " + objs[idx].getIdtf()
                added += 1
        
        for prop, value in self.properties.items():
            res += "%s = %s\n" % (str(prop), str(value))
        
        return res
        
    def getAvailableEqualGroup(objectClass):
        
        idx = 1
        while (GeometryAbstractObject.groups[objectClass].has_key(idx)):
            idx += 1
        
        return idx
        
    getAvailableEqualGroup = classmethod(getAvailableEqualGroup)
        
    def addPoint(self, _point, _pos):
        """Add new point into points list
        @param _point: point that need to be added
        @type _point: GeometryPoint
        @param _pos: Point position (relative in [0..1] range)
        @type _pos: float    
        """
        
        assert(not self.hasPoint(_point))
        
        if len(self.points) == 0:
            self.points.append((_point, _pos))
        else:
            appended = False
            idx = 0
            for pt, dot in self.points:
                if dot > _pos:
                    self.points.insert(idx, (_point, _pos))
                    appended = True
                    break
                idx += 1
            if not appended:
                self.points.append((_point, _pos))
        
        _point.baseLine = self        
        _point.setPosition(self._calculatePointPosition(_pos))
        self.addLinkedObject(suit.core.objects.Object.LS_BASEONTHIS, _point)
    
    def removePoint(self, _point):
        """Remove specified point from points list
        """
        assert(self.hasPoint(_point))

        for pt, dot in self.points:
            if pt is _point:
                _point.baseLine = None
                self.points.remove((pt, dot))
                self.removeLinkedObject(suit.core.objects.Object.LS_BASEONTHIS, pt)                
    
    def hasPoint(self, _point):
        """Check if specified point exist
        @param _point: Point for check
        @type _point: GeometryPoint  
        """
        for pt, dot in self.points:
            if pt is _point:
                return True
            
        return False
    
    def getPoints(self):
        """Return list of points
        """
        res = []
        res.extend(self.points)
        return res
    
    def _updateAllPoints(self):
        """Recalculate all point positions
        """
        for point, pos in self.points:
            point.setPosition(self._calculatePointPosition(pos))
    
    def _calculatePointPosition(self, _pos):
        """Function, that calculates point position, depend on
        relative position. This function need to be overloaded. 
        
        @param _pos: Relative position
        
        @return: ogre.Vector3, that contains result coordinates 
        """
        return ogre.Vector3(0, 0, 0)
    
    def _calculatePointRelPosition(self, _coords):
        """Calculate relative position for point by it
        coordinates \p _coords
        
        @param _coords: Point coordinates
        @type _coords: ogre.Vector3  
        
        @return: Return relative position of point in range [0..1]
        """
        return 0.5
    
    def setPropertyValue(self, _name, _value):
        """Setup new property value
        @param _name: property name
        @param _value: property value  
        """
        self.properties[_name] = _value
        
    def getPropertyValue(self, _name):
        """Return value of property with specified \p _name.
        If property doesn't exist, then return None
        """
        if self.properties.has_key(_name):
            return self.properties[_name]
        return None
    
    def build_text_idtf(self):
        """Builds text identifier for an object
        """
        return None

    def getIdtf(self):
        """Return identifier of this object
        """
        if self._getScAddr() is not None:
            return str(self.getText())
        else:
            return self.build_text_idtf()

class GeometryPoint(suit.core.objects.ObjectDepth, GeometryAbstractObject):
    """Object that represents geometry point
    
    @warning: creation of this object need be synchronized
    """
    
    names = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    name_available = [True] * len(names)
    
    def __init__(self):
        suit.core.objects.ObjectDepth.__init__(self, None)
        GeometryAbstractObject.__init__(self)
        
        self.baseLine = None
        
        # creating entity
        self.entity = render_engine.SceneManager.createEntity("GeometryPoint_" + str(self), geom_env.mesh_point)
        self.sceneNode.attachObject(self.entity)
        self.setScale(ogre.Vector3(0.5, 0.5, 0.5))
                
    def __del__(self):
        suit.core.objects.ObjectDepth.__del__(self)
        GeometryAbstractObject.__del__(self)
        
    def delete(self):
        render_engine.SceneManager.destroyEntity(self.entity)
        suit.core.objects.ObjectDepth.delete(self)
        GeometryAbstractObject.delete(self)
        
        self.setText(None)
        
        if self.baseLine is not None:
            self.baseLine.removePoint(self)
            
    @staticmethod
    def getAvailableName():
        """Return first available name. If there are no available names, then return None 
        """
        for idx in xrange(len(GeometryPoint.names)):
            if GeometryPoint.name_available[idx]:
                return str(GeometryPoint.names[idx])
        
    def _getMaterialName(self):
        """Return material name for point object based on current state
        
        @return: material name
        @rtype: str
        """
        return geom_env.material_state_pat % ("point_%s" % (state_post[self.getState()]))
        
    def _updateView(self):
        """View update function
        
        Updates state for object
        """
        if self.needStateUpdate:
            self.needStateUpdate = False
            self.entity.setMaterialName(self._getMaterialName())
            
        suit.core.objects.ObjectDepth._updateView(self)
        
    def get_idtf(self):
        """Returns object identifier.
        It parse structures like: Point(A), Point A, pA and return A
        """
        return self.getText()
        
    def build_text_idtf(self):
        """Builds text identifier for an object
        """        
        idtf = self.get_idtf()
        if idtf is None:
            return None
        return "%s%s" % (u'Тчк', idtf)
    
    def setText(self, _text):
        txt = str(self.getText())
        if txt is not None:
            if len(txt) == 1:
                for idx in xrange(len(self.names)):
                    if self.names[idx] == txt[0]:
                        self.name_available[idx] = True
        
        suit.core.objects.ObjectDepth.setText(self, _text)
        
        txt = str(_text)
        if _text is not None:
            if len(txt) == 1:
                for idx in xrange(len(self.names)):
                    if self.names[idx] == txt[0]:
                        self.name_available[idx] = False
    
class GeometryLineSection(suit.core.objects.ObjectLine, GeometryAbstractObject):
    """Object that represents geometry line section
    """
    def __init__(self):
        suit.core.objects.ObjectLine.__init__(self, None)
        GeometryAbstractObject.__init__(self)
        
        # creating entity
        self.entity = render_engine.SceneManager.createEntity("geom_lsection_%s" % str(self), geom_env.mesh_lsect)
        self.sceneNode.attachObject(self.entity)
        self.radius = 0.08
        
        self._equalObject = None
        self._equalNode = render_engine.SceneManager.createSceneNode()
        self._equalNode.setInheritScale(False)
        render_engine.SceneNode.addChild(self.sceneNode, self._equalNode) 
        
        # need to be moved into base class GeometryProperty in future
        self.length = None
        self.length_text_obj = None
        
        self.needLengthUpdate = False
        self.needLengthPositionUpdate = False
        
        # list of line sections, that created with child points
        self.sections = []        
                
    def __del__(self):
        suit.core.objects.ObjectLine.__del__(self)
        GeometryAbstractObject.__del__(self)
    
    def delete(self):
        """Object deletion
        """
        if self.entity:
            render_engine.SceneManager.destroyEntity(self.entity)
        
        if self.length_text_obj is not None:
            self.length_text_obj.delete() 
            self.length_text_obj = None
        
        if self._equalObject is not None:
            render_engine.SceneManager.destroyManualObject(self._equalObject)
        if self._equalNode is not None:
            render_engine.SceneManager.destroySceneNode(self._equalNode)
        
        suit.core.objects.ObjectDepth.delete(self)
        GeometryAbstractObject.delete(self)
        
    def _calculatePointPosition(self, _pos):
        
        assert (_pos <= 1.0) and (_pos >= 0.0)    
        return self.begin_pos + (self.end_pos - self.begin_pos) * _pos
    
    def _calculatePointRelPosition(self, _coords):
        """@see:  GeometryAbstractObject._calculatePointRelPosition
        """
        v = self.end_pos - self.begin_pos
        if v.length() == 0:
            return 0.5
        
        vn = v.normalisedCopy()
        vp = _coords - self.begin_pos
        p = self.begin_pos + vn * vn.dotProduct(vp)
        r = p - self.begin_pos
        dotPos = r.length() / v.length()
        
        dotPos = max([0, dotPos])
        dotPos = min([1.0, dotPos])
        
        return dotPos

    def _getMaterialName(self):
        """Returns material name based on object state
        """
        return geom_env.material_state_pat % ("lsec_%s" % (state_post[self.getState()]))
    
    def setLength(self, _length):
        self.length = _length
        self.needLengthUpdate = True
        self.needViewUpdate = True
        
    def setPropertyValue(self, _name, _value):
        
        if _name == self.PropLength:
            self.setLength(_value)
        GeometryAbstractObject.setPropertyValue(self, _name, _value)
        
    def getLength(self):
        return self.length
        
    def _update(self, _timeSinceLastFrame):
        """Updates line state
        """        
        if not self.needUpdate: # do nothing
            return       
            
        # notify, that need to update length position
        self.needLengthPositionUpdate = True
        
        suit.core.objects.ObjectLine._update(self, _timeSinceLastFrame)
        
        # calculate rotation
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
        
        # update identifier position
        if self.begin_pos and self.end_pos and self.text_obj:
            self.text_obj.setPosition((self.begin_pos + self.end_pos) / 2.0 + self.radius * 1.2 * ogre.Vector3(1.0, 1.0, 0.0))
            self.needUpdate = False
        else:
            self.needUpdate = True
            
        self.position = (self.begin_pos + self.end_pos) / 2.0
        
        # update all points
        self._updateAllPoints()
        
        # update equivalence
        if self.equalGroup is not None:
            self._updateEqual()
            
        if self.length_text_obj is not None: self.length_text_obj._update(_timeSinceLastFrame)
    
    def _updateView(self):
        """View update function
        
        Updates state for object
        """
        if self.needStateUpdate:
            self.needStateUpdate = False
            self.entity.setMaterialName(self._getMaterialName())
            if self._equalObject is not None:
                self._equalObject.setMaterialName(0, self._getMaterialName())
            
        if self.needLengthUpdate or self.needSceneAttachUpdate:
            self.needLengthUpdate = False
#            self.needSceneAttachUpdate = False
            self._updateLength()
            
        if self.needLengthPositionUpdate:
            self.needLengthPositionUpdate = False
            self._updateLengthPosition()
            
        suit.core.objects.ObjectLine._updateView(self)
        
    def _updateEqual(self):
        """Updates geometry, that show equivalence group
        """
        assert self.equalGroup is not None
        
        # recreate geometry
        if self._equalObject is None:
            #sceneMngr.destroyManualObject(self.__manualObject)
            self._equalObject = render_engine._ogreSceneManager.createManualObject(str(self) + "_eq")
            self._equalObject.setDynamic(True)
            # attach to scene node
            self._equalNode.attachObject(self._equalObject)
            self._equalObject.begin(self._getMaterialName())
        else:
            self._equalObject.beginUpdate(0)
            
        # recalculate mesh
        width = self.radius * 2
        height2 = width * 2
        orientV = self.end_pos - self.begin_pos
        l = orientV.length()
        offset_y = l * 0.5 - (self.equalGroup * 2 - 1) * width
        
        for group in xrange(self.equalGroup):    
            
            vy = offset_y + group * 2 * width
        
            self._equalObject.position(-height2, vy + width, 0.0)
            self._equalObject.normal(0, 0, 1)
            self._equalObject.position(height2, vy + width, 0.0)
            self._equalObject.normal(0, 0, 1)
                
            self._equalObject.position(height2, vy, 0.0)
            self._equalObject.normal(0, 0, 1)
            self._equalObject.position(-height2, vy, 0.0)
            self._equalObject.normal(0, 0, 1)
        
            
            idx = group * 4
            self._equalObject.quad(idx, idx + 1, idx + 2, idx + 3)

        self._equalObject.end()
        
    def _updateLength(self):
        """Updates length object
        """
        if self.length is not None and self.isSceneAttached:                
            if not self.length_text_obj:
                self.length_text_obj = suit.core.objects.ObjectText(self.getPosition(), self)
                self.length_text_obj.show()
                
            self.length_text_obj.setText("#000000%s" % str(self.length))
        else:
            self.length_text_obj = None
            
        self.needLengthPositionUpdate = True
        self.needViewUpdate = True
            
    def _updateLengthPosition(self):
        """Recalculate length text position 
        """
        if self.length_text_obj:
            
            # get center
            p1 = self.getBegin().getPosition()
            p2 = self.getEnd().getPosition()
            
            pm = p1.midPoint(p2)
            pm = p1.midPoint(pm)
            
            angle = math.atan2(p2.y - p1.y, p2.x - p1.x)
            angle = ogre.Radian(angle) + ogre.Degree(90.0).valueRadians()
            angle = angle.valueRadians()
           
            r = 0.2
            self.length_text_obj.setPosition(ogre.Vector3(r * math.cos(angle), r * math.sin(angle), 0.0) + pm)
                 
    def setEqualGroup(self, newGroup):
        
        GeometryAbstractObject.setEqualGroup(self, newGroup)
        
        self.needUpdate = True
        self.needMeshUpdate = True
                 
    def get_idtf(self):
        """Returns object identifier.
        It parse structures like: Point(A), Point A, pA and return A
        """
        #FIXME:    add parsing for Point(A), Point A and etc. structures
        idtf = self.getText()
        if idtf is None or len(idtf) == 0:
            return None
            
        return idtf
     
    def build_text_idtf(self):
        """Builds text identifier for an object
        """
        idtf = self.get_idtf()
        if not idtf:
            begIdtf = self.beginObject.build_text_idtf()
            endIdtf = self.endObject.build_text_idtf()
            
            if begIdtf is None or endIdtf is None:
                return None
            
            return "%s(%s;%s)" % (u'Отр', begIdtf, endIdtf)
        else:
            return None
     
class GeometryCircle(suit.core.objects.ObjectDepth, GeometryAbstractObject):
    
    def __init__(self):
        suit.core.objects.ObjectDepth.__init__(self)
        GeometryAbstractObject.__init__(self)
        
        self.width = 0.2
        self.radius = 1.0
        self.sectors = 90
        
        self.manualObject = None
        self.center_point = None
        self.radius_point = None
        
        self.needMeshUpdate = False
        self.needCenterPointUpdate = False
        self.needRadiusPointUpdate = False
        
    def __del__(self):
        suit.core.objects.ObjectDepth.__del__(self)
        GeometryAbstractObject.__del__(self)
        
    def delete(self):
            
        if self.center_point is not None:
            self.center_point.removeLinkedObject(suit.core.objects.Object.LS_BASEONTHIS, self)
            self.center_point = None
        
        if self.manualObject is not None:
            render_engine.SceneManager.destroyManualObject(self.manualObject)
        suit.core.objects.ObjectDepth.delete(self)
        GeometryAbstractObject.delete(self)
        
    def _getMaterialName(self):
        """Returns material name based on object state
        """
        return geom_env.material_state_pat % ("lsec_%s" % (state_post[self.getState()]))
        
    def _update(self, _timeSinceLastFrame):
        
        if not self.needUpdate:
            return
               
        self.needTextPositionUpdate = True
        
        # update circle position based on center point
        self.position = self.center_point.getPosition()
        self._updatePosition()
        
        # calculate radius
        if self.radius_point is not None:
            c = self.center_point.getPosition()
            r = self.radius_point.getPosition()
            
            # calculate radius length
            self.setRadius(math.sqrt((c[0] - r[0]) ** 2 + (c[1] - r[1]) ** 2))
        
        self._updateAllPoints()
        
        if self.needMeshUpdate:
            self._updateMesh()
            self.needMeshUpdate = False
            
        suit.core.objects.ObjectDepth._update(self, _timeSinceLastFrame)
        
    def _updateView(self):
        """Update object view
        """
        # do not moves and scale for circle
        self.needPositionUpdate = False
        self.needScaleUpdate = False
        
        if self.needCenterPointUpdate:
            self.needCenterPointUpdate = False
            
        if self.needRadiusPointUpdate:
            self.needRadiusPointUpdate = False
            
        if self.needStateUpdate:
            self.needStateUpdate = False
            self.manualObject.setMaterialName(0, self._getMaterialName())
            
        suit.core.objects.ObjectDepth._updateView(self)
        
        
    def _updateMesh(self):
        """Updates circle mesh
        """
        # recreate geometry
        if self.manualObject is None:
            #sceneMngr.destroyManualObject(self.__manualObject)
            self.manualObject = render_engine._ogreSceneManager.createManualObject(str(self))
            self.manualObject.setDynamic(True)
            # attach to scene node
            self.sceneNode.attachObject(self.manualObject)
            self.manualObject.begin(self._getMaterialName())
        else:
            self.manualObject.beginUpdate(0)
            
        # recalculate mesh
        a_step = ogre.Degree(360 / self.sectors).valueRadians()
        angle = 0.0
        r_in = self.radius - self.width / 2.0
        r_out = r_in + self.width
        for sector in xrange(self.sectors):
            vx = math.cos(angle)
            vy = math.sin(angle)
            
            self.manualObject.position(vx * r_in, vy * r_in, 0.0)
            self.manualObject.normal(0, 0, 1)
            self.manualObject.position(vx * r_out, vy * r_out, 0.0)
            self.manualObject.normal(0, 0, 1)
            
            angle += a_step
            
        for idx in xrange(self.sectors):
            idx1 = idx * 2
            self.manualObject.quad(idx1, idx1 + 1, idx1 + 3, idx1 + 2)
        self.manualObject.quad(self.sectors*2 - 2, self.sectors*2 - 1, 1, 0)
        self.manualObject.end()
        
    def setRadius(self, _radius):
        """Set circle radius
        @param _radius: radius length
        @type _radius: float
        """
        self.radius = _radius
        self.needMeshUpdate = True
        
    def setCenterPoint(self, _point):
        """Sets center point object
        @param _point: center point object
        @type _point: GeometryPoint
        """
        if self.center_point is not None:
            self.center_point.removeLinkedObject(suit.core.objects.Object.LS_BASEONTHIS, self)
        
        self.center_point = _point
        self.needCenterPointUpdate = True
        self.needViewUpdate = True
        
        if self.center_point is not None:
            self.center_point.addLinkedObject(suit.core.objects.Object.LS_BASEONTHIS, self)
            
    def setRadiusPoint(self, _point):
        """Sets radius point. Radius points - is a point, that lies on circle.
        @param _point: Radius point
        @type _point: GeometryPoint  
        """
        if self.radius_point is not None:
            self.radius_point.removeLinkedObject(suit.core.objects.Object.LS_BASEONTHIS, self)
            
        self.radius_point = _point
        self.needRadiusPointUpdate = True
        self.needViewUpdate = True
        
        if self.radius_point is not None:
            self.radius_point.addLinkedObject(suit.core.objects.Object.LS_BASEONTHIS, self)
            
    def _checkRayIntersect(self, ray):
        """Check if ray intersects circle object.
       
        @param ray:    ray for intersection checking
        @type ray:    ogre.Ray
        """
        res, pos = suit.core.objects.ObjectDepth._checkRayIntersect(self, ray)
        if not res:
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
        
        dist = self.center_point.getPosition().distance(d)
        if math.fabs(dist - self.radius) <= self.width / 2.0:
            return True, 0
        
        return False, -1
    
    def get_idtf(self):
        """Returns object identifier.
        It parse structures like: Point(A), Point A, pA and return A
        """
        #FIXME:    add parsing for Point(A), Point A and etc. structures
        idtf = self.getText()
        if idtf is None or len(idtf) == 0:
            return None
            
        return idtf
    
    def build_text_idtf(self):
        """Builds text identifier for an object
        """
        idtf = self.get_idtf()
        if not idtf:
            cIdtf = self.center_point.build_text_idtf()
            rIdtf = self.radius_point.build_text_idtf()
            if cIdtf is None or rIdtf is None:
                return None
            
            return "%s(%s;%s)" % (u'Окр', cIdtf, rIdtf)
        else:
            return None
    
    def _calculatePointPosition(self, _pos):
        
        assert (_pos <= 1.0) and (_pos >= 0.0)    
        a = 2 * math.pi * _pos
        return self.center_point.getPosition() + ogre.Vector3(math.cos(a), math.sin(a), 0.0) * self.radius
    
    def _calculatePointRelPosition(self, _coords):
        """@see:  GeomatryAbstractObject._calculatePointRelPosition
        """
        v = _coords - self.center_point.getPosition()
        a = math.atan2(v.y, v.x)
        if a < 0:
            a += math.pi * 2.0
        return a / math.pi * 0.5
    
    def makeBasedOnObjects(self, _objects):
        """Create circle based on specified objects
        @param _objects: List of objects
        @type _objects: list
        
        @return: Return true, if circle was created; otherwise return false  
        """
        
        # create based on two points
        if len(_objects) == 2:
            # create by two points
            # first point is a center, second point is an any point on circle
            if isinstance(_objects[0], GeometryPoint) and isinstance(_objects[1], GeometryPoint):
                self.setCenterPoint(_objects[0])
                self.setRadiusPoint(_objects[1])
                
                return True
            
            # create by center point and radius
            elif (isinstance(_objects[0], GeometryPoint) and isinstance(_objects[1], GeometryLineSection)):
                if _objects[1].getBegin() is _objects[0] or _objects[1].getEnd() is _objects[0]:
                    self.setCenterPoint(_objects[0])
                    if _objects[1].getBegin() is _objects[0]:
                        self.setRadiusPoint(_objects[1].getEnd())
                    else:
                        self.setRadiusPoint(_objects[1].getBegin())
                        
                    return True
            
            elif (isinstance(_objects[0], GeometryLineSection) and isinstance(_objects[1], GeometryPoint)):
                if _objects[0].getBeing() is _objects[1] or _objects[0].getEnd() is _objects[1]:
                    self.setCenterPoint(_objects[1])
                    if _objects[0].getBegin() is _objects[1]:
                        self.setRadiusPoint(_objects[0].getEnd())
                    else:
                        self.setRadiusPoint(_objects[0].getBegin())
                        
                    return True
                
        return False
    
    def getRadiusObject(self):
        """Return radius line object
        """
        out_lines = self.center_point.getLinkedObjects(suit.core.objects.Object.LS_OUT)
        for line in out_lines:
            if line.getEnd() is self.radius_point:
                return line
            
        in_lines = self.center_point.getLinkedObjects(suit.core.objects.Object.LS_IN)
        for line in in_lines:
            if line.getBegin() is self.radius_point:
                return line
            
        return None
    
class GeometryTriangle(suit.core.objects.ObjectDepth, GeometryAbstractObject):
    
    def __init__(self):
        """Constructor
        """
        suit.core.objects.ObjectDepth.__init__(self)
        GeometryAbstractObject.__init__(self)
        
        self.__manualObject = None  # manual object to store and render geometry
        self.pts = []        # triangle vertex points
        self.sides = []         # triangle sides
            
    def __del__(self):
        suit.core.objects.ObjectDepth.__del__(self)
        GeometryAbstractObject.__del__(self)
    
    def delete(self):
        """Object deletion
        """
        for _line in self.sides:
            _line.removeLinkedObject(suit.core.objects.Object.LS_BASEONTHIS, self)
        
        if self.__manualObject:
            render_engine.SceneManager.destroyManualObject(self.__manualObject)
            
        suit.core.objects.ObjectDepth.delete(self)
        GeometryAbstractObject.delete(self)
        
    def _getMaterialName(self):
        """Returns material name based on object state
        """        
        return geom_env.material_state_pat % ("triangle_%s" % (state_post[self.getState()]))
    
    def _update(self, _timeSinceLastFrame):
        """Object update
        """
        if not self.needUpdate: # do nothing
            return 
        
        # notify, that text position need to be updated
        self.needTextPositionUpdate = True
        
        # calculate center position
        p1 = self.pts[0].getPosition()
        p2 = self.pts[1].getPosition()
        p3 = self.pts[2].getPosition()
        
        s1 = p1.distance(p2)
        s2 = p2.distance(p3)
        s3 = p3.distance(p1)
        
        perim = 1 / (s1 + s2 + s3)
        
        # using Geron S=UR
        x = (s2 * p1.x + s3 * p2.x + s1 * p3.x) * perim
        y = (s2 * p1.y + s3 * p2.y + s1 * p3.y) * perim
        
        self.position = ogre.Vector3(x, y, 0)
        self.sceneNode.setPosition(self.position)
        
        # update/create mesh
        if self.__manualObject is None:
            self.__manualObject = render_engine._ogreSceneManager.createManualObject(str(self))
            self.__manualObject.setDynamic(True)
            self.sceneNode.attachObject(self.__manualObject)
            self.__manualObject.begin(self._getMaterialName())
        else:
            self.__manualObject.beginUpdate(0)
            
        for point in self.pts:
            self.__manualObject.position(point.getPosition() - self.position)
            self.__manualObject.normal(0, 0, 1)
        
        self.__manualObject.triangle(2, 1, 0)
        
        self.__manualObject.end()
        
        suit.core.objects.ObjectDepth._update(self, _timeSinceLastFrame)
        
    def _updateView(self):
        """View update function
        Updates state for object
        """
        suit.core.objects.ObjectDepth._updateView(self)
        
        if self.needStateUpdate:
            self.needStateUpdate = False
            self.__manualObject.setMaterialName(0, self._getMaterialName())
             
    
    def _checkRayIntersect(self, ray):
        """Check if ray intersects triangle.
        
        @param ray:    ray for intersection checking
        @type ray:    ogre.Ray
        """
        res = suit.core.objects.ObjectDepth._checkRayIntersect(self, ray)
        if not res[0]:
            return res
        
        res = ogre.Math.intersects(ray,
                                    self.pts[0].getPosition(),
                                    self.pts[1].getPosition(),
                                    self.pts[2].getPosition())
        
        return res.first, res.second
    
    def _getLinePoints(self, _lines):
        """Get points from triangle side lines.
        @return: List of triangle vertex points. If it impossible to 
        build triangle on specified \p _lines, then return None
        """
        # get points
        _points = {}
        for _line in _lines:
            _points[_line.getBegin()] = 0
            _points[_line.getEnd()] = 0
            
        for _line in _lines:
            _points[_line.getBegin()] += 1
            _points[_line.getEnd()] += 1
            
        for key, value in _points.items():
            if value != 2:
                return None
        
        return _points.keys()
    
    def setSides(self, _lines):
        """Set triangle sides
        @param _line: GeometryLineSection objects, that are a sides of triangle
        @type _line: list of GeometryLineSection objects
        """
        assert len(_lines) == 3
        
        if self.sides is not None:
            for _line in self.sides:
                _line.removeLinkedObject(suit.core.objects.Object.LS_BASEONTHIS, self)
                
        self.sides = []
        self.sides.extend(_lines)
        
        self.pts = self._getLinePoints(self.sides)
        assert self.pts is not None   
        
        self.needUpdate = True
            
        if self.sides is not None:
            for _line in self.sides:
                _line.addLinkedObject(suit.core.objects.Object.LS_BASEONTHIS, self)
                
    def getSides(self):
        """Retur list of sides
        """
        res = []
        if self.sides is not None:
            res.extend(self.sides)
        return res
    
    def makeBasedOnObjects(self, _objects):
        """Create triagnel based on specified objects
        @param _objects: List of objects
        @type _objects: list
        
        @return: Return true, if circle was created; otherwise return false  
        """
        if len(_objects) == 3:
            # fist way to build triangle based on lines
            lines3 = True
            for obj in _objects:
                if not isinstance(obj, GeometryLineSection):
                    lines3 = False
                    
            if not lines3:
                return False
            
            self.pts = self._getLinePoints(_objects)
            if not self.pts:
                return False
            
            self.setSides(_objects)
            return True
        
    def get_idtf(self):
        """Returns object identifier.
        It parse structures like: Point(A), Point A, pA and return A
        """
        #FIXME:    add parsing for Point(A), Point A and etc. structures
        idtf = self.getText()
        if idtf is None or len(idtf) == 0:
            return None
            
        return idtf
    
    def build_text_idtf(self):
        """Builds text identifier for an object
        """
        idtf = self.get_idtf()
        if not idtf:
            
            idtf1 = self.pts[0].build_text_idtf()
            idtf2 = self.pts[1].build_text_idtf()
            idtf3 = self.pts[2].build_text_idtf()
            
            if idtf1 is None or idtf2 is None or idtf3 is None:
                return None
            
            return u"%s(%s;%s;%s)" % (u'Треугк', idtf1, idtf2, idtf3)
        else:
            return None 
        
  
class GeometryQuadrangle(suit.core.objects.ObjectDepth, GeometryAbstractObject):
    
    def __init__(self):
        """Constructor
        """
        suit.core.objects.ObjectDepth.__init__(self)
        GeometryAbstractObject.__init__(self)
        
        self.__manualObject = None  # manual object to store and render geometry
        self.pts = []        # quadrangle vertex points
        self.sides = []         # quadrangle sides
            
    def __del__(self):
        suit.core.objects.ObjectDepth.__del__(self)
        GeometryAbstractObject.__del__(self)
    
    def delete(self):
        """Object deletion
        """
        for _line in self.sides:
            _line.removeLinkedObject(suit.core.objects.Object.LS_BASEONTHIS, self)
        
        if self.__manualObject:
            render_engine.SceneManager.destroyManualObject(self.__manualObject)
            
        suit.core.objects.ObjectDepth.delete(self)
        GeometryAbstractObject.delete(self)
        
    def _getMaterialName(self):
        """Returns material name based on object state
        """        
        return geom_env.material_state_pat % ("triangle_%s" % (state_post[self.getState()]))
    
    def _update(self, _timeSinceLastFrame):
        """Object update
        """
        if not self.needUpdate: # do nothing
            return 
        
        # notify, that text position need to be updated
        self.needTextPositionUpdate = True
        
        # calculate center position
        minX = self.pts[0].getPosition().x
        minY = self.pts[0].getPosition().y
        maxX = minX
        maxY = minY
        
        for pt in self.pts:
            pos = pt.getPosition()
            minX = min([minX, pos.x])
            minY = min([minY, pos.y])
            maxX = max([maxX, pos.x])
            maxY = max([maxY, pos.y])
        
        x = (minX + maxX) / 2.0
        y = (minY + maxY) / 2.0
        
        self.position = ogre.Vector3(x, y, 0)
        self.sceneNode.setPosition(self.position)
        
        # update/create mesh
        if self.__manualObject is None:
            self.__manualObject = render_engine._ogreSceneManager.createManualObject(str(self))
            self.__manualObject.setDynamic(True)
            self.sceneNode.attachObject(self.__manualObject)
            self.__manualObject.begin(self._getMaterialName())
        else:
            self.__manualObject.beginUpdate(0)
            
        for point in self.pts:
            self.__manualObject.position(point.getPosition() - self.position)
            self.__manualObject.normal(0, 0, 1)
        
        self.__manualObject.quad(0, 1, 2, 3)
        
        self.__manualObject.end()
        
        suit.core.objects.ObjectDepth._update(self, _timeSinceLastFrame)
        
    def _updateView(self):
        """View update function
        Updates state for object
        """
        suit.core.objects.ObjectDepth._updateView(self)
        
        if self.needStateUpdate:
            self.needStateUpdate = False
            self.__manualObject.setMaterialName(0, self._getMaterialName())
             
    
    def _checkRayIntersect(self, ray):
        """Check if ray intersects quadrangle.
        
        @param ray:    ray for intersection checking
        @type ray:    ogre.Ray
        """
        res = suit.core.objects.ObjectDepth._checkRayIntersect(self, ray)
        if not res[0]:
            return res
        
        res = ogre.Math.intersects(ray,
                                    self.pts[0].getPosition(),
                                    self.pts[1].getPosition(),
                                    self.pts[2].getPosition())
        
        if res.first:
            return res.first, res.second
        
        res = ogre.Math.intersects(ray,
                                    self.pts[0].getPosition(),
                                    self.pts[2].getPosition(),
                                    self.pts[3].getPosition())
        
        return res.first, res.second
    
    def _getLinePoints(self, _lines):
        """Get points from quadrangle side lines.
        @return: List of quadrangle vertex points. If it impossible to 
        build quadrangle on specified \p _lines, then return None
        """
        # get points
        _points = {}
        for _line in _lines:
            _points[_line.getBegin()] = 0
            _points[_line.getEnd()] = 0
            
        for _line in _lines:
            _points[_line.getBegin()] += 1
            _points[_line.getEnd()] += 1
            
        for key, value in _points.items():
            if value != 2:
                return None
            
        # sort points by link order
        _line_flag = [False] * len(_lines)
        _line_flag[0] = True
        
        ordered_points = [_lines[0].getBegin(), _lines[0].getEnd()]
        for idx in xrange(1, len(_lines)):
            _line = _lines[idx]
            
            if _line_flag[idx]: continue    # skip processed line
            if len(ordered_points) == 4: continue # do nothing
            
            if _line.getBegin() is ordered_points[-1]:
                ordered_points.append(_line.getEnd())
                _line_flag[idx] = True
            elif _line.getEnd() is ordered_points[-1]:
                ordered_points.append(_line.getBegin())
                _line_flag[idx] = True
            elif _line.getBegin() is ordered_points[0]:
                ordered_points.insert(0, _line.getEnd())
                _line_flag[idx] = True
            elif _line.getEnd() is ordered_points[0]:
                ordered_points.insert(0, _line.getBegin())
                _line_flag[idx] = True
                
        
        return ordered_points
    
    def setSides(self, _lines):
        """Set quadrangle sides
        @param _lines: GeometryLineSection objects, that are a sides of triangle
        @type _lines: list of GeometryLineSection objects
        """
        assert len(_lines) == 4
        
        if self.sides is not None:
            for _line in self.sides:
                _line.removeLinkedObject(suit.core.objects.Object.LS_BASEONTHIS, self)
                
        self.sides = []
        self.sides.extend(_lines)
        
        self.pts = self._getLinePoints(self.sides)
        assert self.pts is not None   
        
        self.needUpdate = True
            
        if self.sides is not None:
            for _line in self.sides:
                _line.addLinkedObject(suit.core.objects.Object.LS_BASEONTHIS, self)

    def getSideLength(self, index):
        return self.sides[index].getLineLength()

    def getPerimeter(self):
        return self.getSideLength(0) \
            + self.getSideLength(1) \
            + self.getSideLength(2) \
            + self.getSideLength(3)

    def getSides(self):
        assert len(self.sides) == 4
        unused = self.sides
        ab = unused.pop()
        cd = self.getOppositeSide(ab)
        unused.remove(cd)
        bc = unused.pop()
        ad = unused.pop()
        return [ab, bc, cd, ad]

    def getDiagonals(self):
        assert len(self.sides) == 4
        sides = self.getSides()
        points = [self._getDifferentPoints(sides[0], sides[1]), \
                  self._getDifferentPoints(sides[2], sides[3])]
        d1 = suit.core.objects.ObjectDepth.getDistance(points[0][0].getPosition(), points[0][1].getPosition())
        d2 = suit.core.objects.ObjectDepth.getDistance(points[1][0].getPosition(), points[1][1].getPosition())
        return [d1, d2]

    def _getDifferentPoints(self, sideA, sideB):
        if sideA.getBegin() is sideB.getBegin():
            return [sideA.getEnd(), sideB.getEnd()]
        if sideA.getBegin() is sideB.getEnd():
            return [sideA.getEnd(), sideB.getBegin()]
        if sideA.getEnd() is sideB.getBegin():
            return [sideA.getBegin(), sideB.getEnd()]
        if sideA.getEnd() is sideB.getEnd():
            return [sideA.getBegin(), sideB.getBegin()]

    def getSquare(self):
        assert len(self.sides) == 4
        sides = self.getSides()
        a = sides[0].getLineLength()
        b = sides[1].getLineLength()
        c = sides[2].getLineLength()
        d = sides[3].getLineLength()
        diagonals = self.getDiagonals()
        d1 = diagonals[0]
        d2 = diagonals[1]
        square = math.sqrt((4 * d1*d1 * d2*d2 - (b*b + d*d - a*a - c*c)) / 16)
        return square

    def canHaveInCircle(self):
        assert len(self.sides) == 4
        sides = self.getSides()
        a = sides[0].getLineLength() + sides[2].getLineLength()
        b = sides[1].getLineLength() + sides[3].getLineLength()
        return (a - b) <= 0.1

    def getOppositeSide(self, side):
        for _side in self.sides:
            if _side.getBegin() == side.getBegin():
                continue
            if _side.getBegin() == side.getEnd():
                continue
            if _side.getEnd() == side.getBegin():
                continue
            if _side.getEnd() == side.getEnd():
                continue
            return _side

    def getInCircleRadius(self):
        return 2 * self.getSquare() / self.getPerimeter()

    def getInCirclePoints(self):
        r = self.getInCircleRadius()
        sides = self.getSides()
        p1, p3 = self._getDifferentPoints(sides[0], sides[1])
        if p1 is sides[0].getBegin():
            p2 = sides[0].getEnd()
        else:
            p2 = sides[0].getBegin()
        p1 = p1.getPosition()
        p2 = p2.getPosition()
        p3 = p3.getPosition()
        a = sides[0].getLineLength()
        b = sides[1].getLineLength()
        c = suit.core.objects.ObjectDepth.getDistance(p1, p3)
        cosY = (a*a + b*b - c*c) / (2*a*b)
        y = math.acos(cosY)
        x = 2*r*r - 2*r*r*math.cos(math.pi / 2 - y)
        p2_a_dist = math.sqrt((x*x / (1 - cosY)) / 2)
        k = a / p2_a_dist
        np = p2 + (p1 - p2) * k
        sinA = p2_a_dist / math.fabs(p2[0] - np[0])
        cosA = math.sqrt(1 - sinA * sinA)
        center = ogre.Vector3(np[0] + r*sinA, np[1] - r*cosA, 0)
        return [center, np]

    def getSides(self):
        """Returns list of sides
        """
        res = []
        if self.sides is not None:
            res.extend(self.sides)
        return res
    
    def makeBasedOnObjects(self, _objects):
        """Create quadrangle based on specified objects
        @param _objects: List of objects
        @type _objects: list
        
        @return: Return true, if quadrangle was created; otherwise return false  
        """
        if len(_objects) == 4:
            lines4 = True
            for obj in _objects:
                if not isinstance(obj, GeometryLineSection):
                    lines4 = False
                    
            if not lines4:
                return False
            
            self.pts = self._getLinePoints(_objects)
            if not self.pts:
                return False
            
            self.setSides(_objects)
            return True
        
    def get_idtf(self):
        """Returns object identifier.
        It parse structures like: Point(A), Point A, pA and return A
        """
        #FIXME:    add parsing for Point(A), Point A and etc. structures
        idtf = self.getText()
        if idtf is None or len(idtf) == 0:
            return None
            
        return idtf
    
    def build_text_idtf(self):
        """Builds text identifier for an object
        """
        idtf = self.get_idtf()
        if not idtf:
            
            idtf1 = self.pts[0].build_text_idtf()
            idtf2 = self.pts[1].build_text_idtf()
            idtf3 = self.pts[2].build_text_idtf()
            idtf4 = self.pts[3].build_text_idtf()
            
            if idtf1 is None or idtf2 is None or idtf3 is None:
                return None
            
            return u"%s(%s;%s;%s;%s)" % (u'Четырехугольник', idtf1, idtf2, idtf3, idtf4)
        else:
            return None  
    
class GeometryAngle(suit.core.objects.ObjectDepth, GeometryAbstractObject):
    """Class that realize geometry angle
    """
    def __init__(self):
        suit.core.objects.ObjectDepth.__init__(self)
        GeometryAbstractObject.__init__(self)
        
        # angle always based on three points
        self.point1 = None
        self.pointC = None
        self.point2 = None
        
        self.width = 0.12
        self.radius = 1.2
        self.sectors = 20
        
        self._equalObject = None
        
        # mesh
        self.manualObject = None
        self.needMeshUpdate = False
    
    def __del__(self):
        suit.core.objects.ObjectDepth.__del__(self)
        GeometryAbstractObject.__del__(self)
    
    def delete(self):
        suit.core.objects.ObjectDepth.delete(self)
        GeometryAbstractObject.delete(self)
        
        if self.point1 is not None:
            self.point1.removeLinkedObject(suit.core.objects.Object.LS_BASEONTHIS, self)
            self.point1 = None
            
        if self.point2 is not None:
            self.point2.removeLinkedObject(suit.core.objects.Object.LS_BASEONTHIS, self)
            self.point2 = None
            
        if self.pointC is not None:
            self.pointC.removeLinkedObject(suit.core.objects.Object.LS_BASEONTHIS, self)
            self.pointC = None
        
        if self.manualObject is not None:
            render_engine.SceneManager.destroyManualObject(self.manualObject)
            
        if self._equalObject is not None:
            render_engine.SceneManager.destroyManualObject(self._equalObject)
        
    def _getMaterialName(self):
        """Returns material name based on object state
        """
        return geom_env.material_state_pat % ("triangle_%s" % (state_post[self.getState()]))
    
    def _getEqualMaterialName(self):
        """Returns material name based on object state
        """
        return geom_env.material_state_pat % ("lsec_%s" % (state_post[self.getState()]))
        
    def _update(self, _timeSinceLastFrame):
        """Update object state
        """
        if not self.needUpdate or self.pointC is None or self.point1 is None or self.point2 is None:
            return
                           
        # update based on center point
        self.setPosition(self.pointC.getPosition())
        
        self._updateMesh()
                
        suit.core.objects.ObjectDepth._update(self, _timeSinceLastFrame)
    
    def _updateView(self):
        """Updates graphical object representation
        """       
        if self.needStateUpdate:
            self.needStateUpdate = False
            self.manualObject.setMaterialName(0, self._getMaterialName())
            if self._equalObject is not None:
                self._equalObject.setMaterialName(0, self._getEqualMaterialName())
            
        suit.core.objects.ObjectDepth._updateView(self)
    
    def _updateMesh(self):
        """Updates circle mesh
        """
        # recreate geometry
        if self.manualObject is None:
            #sceneMngr.destroyManualObject(self.__manualObject)
            self.manualObject = render_engine._ogreSceneManager.createManualObject(str(self))
            self.manualObject.setDynamic(True)
            # attach to scene node
            self.sceneNode.attachObject(self.manualObject)
            self.manualObject.begin(self._getMaterialName())
        else:
            self.manualObject.beginUpdate(0)
            
        # calculate angle value
        p1 = self.point1.getPosition()
        p2 = self.point2.getPosition()
        pC = self.pointC.getPosition()
        
        a1 = math.atan2(p1[1] - pC[1], p1[0] - pC[0])
        a2 = math.atan2(p2[1] - pC[1], p2[0] - pC[0])     
        
        a1 = math.degrees(a1)
        a2 = math.degrees(a2)
                        
        if a1 < 0:
            a1 += 360
        if a2 < 0:
            a2 += 360
            
        if a1 < a2:
            a1 += 360
                    
        # recalculate mesh
        a_step = ogre.Degree((a2 - a1) / self.sectors).valueRadians()
        angle = ogre.Degree(a1).valueRadians()
        r_in = self.radius - self.width / 2.0
        groups = 0
        if self.equalGroup is not None:
            groups = self.equalGroup
        r_out = self.width * groups * 2 + self.radius
        
        self.manualObject.position(0.0, 0.0, 0.0)
        self.manualObject.normal(0, 0, 1)
        for sector in xrange(self.sectors + 1):
            vx = math.cos(angle)
            vy = math.sin(angle)
            
            self.manualObject.position(vx * r_out, vy * r_out, 0.0)
            self.manualObject.normal(0, 0, 1)
            self.manualObject.position(vx * r_out, vy * r_out, 0.0)
            self.manualObject.normal(0, 0, 1)
            
            angle += a_step
            
        for idx in xrange(self.sectors):
            idx1 = idx * 2
            self.manualObject.triangle(0, idx1, idx1 + 1)
            
        self.manualObject.end()
            
        # update equivalence
        if self.equalGroup is not None:
            
            # recreate geometry
            if self._equalObject is None:
                #sceneMngr.destroyManualObject(self.__manualObject)
                self._equalObject = render_engine._ogreSceneManager.createManualObject(str(self) + "_eq")
                self._equalObject.setDynamic(True)
                # attach to scene node
                self.sceneNode.attachObject(self._equalObject)
                self._equalObject.begin(self._getEqualMaterialName())
            else:
                self._equalObject.beginUpdate(0)
            
            idx_offset = 0
            for group in xrange(self.equalGroup):
                
                a_step = ogre.Degree((a2 - a1) / self.sectors).valueRadians()
                angle = ogre.Degree(a1).valueRadians()
                r_in = self.radius + self.width * group * 2 - self.width
                r_out = r_in + self.width
                for sector in xrange(self.sectors):
                    vx = math.cos(angle)
                    vy = math.sin(angle)
                    self._equalObject.position(vx * r_in, vy * r_in, 0.0)
                    self._equalObject.normal(0, 0, 1)
                    self._equalObject.position(vx * r_out, vy * r_out, 0.0)
                    self._equalObject.normal(0, 0, 1)
                    angle += a_step
                    vx = math.cos(angle)
                    vy = math.sin(angle)
                    self._equalObject.position(vx * r_in, vy * r_in, 0.0)
                    self._equalObject.normal(0, 0, 1)
                    self._equalObject.position(vx * r_out, vy * r_out, 0.0)
                    self._equalObject.normal(0, 0, 1)
                    self._equalObject.quad(idx_offset, idx_offset + 1, idx_offset + 3, idx_offset + 2)
                    idx_offset += 4
                                
            self._equalObject.end()

    def makeBasedOnObjects(self, _objects):
        """Create circle based on specified objects
        @param _objects: List of objects
        @type _objects: list
        
        @return: Return true, if circle was created; otherwise return false  
        """
        if len(_objects) == 2:
            
            if isinstance(_objects[0], GeometryLineSection) and isinstance(_objects[1], GeometryLineSection):
                
                if _objects[0].getBegin() is _objects[1].getBegin():
                    self.setPointC(_objects[0].getBegin())
                    self.setPoint1(_objects[0].getEnd())
                    self.setPoint2(_objects[1].getEnd())
                elif _objects[0].getBegin() is _objects[1].getEnd():
                    self.setPointC(_objects[0].getBegin())
                    self.setPoint1(_objects[0].getEnd())
                    self.setPoint2(_objects[1].getBegin())
                elif _objects[0].getEnd() is _objects[1].getBegin():
                    self.setPointC(_objects[0].getEnd())
                    self.setPoint1(_objects[0].getBegin())
                    self.setPoint2(_objects[1].getEnd())
                elif _objects[0].getEnd() is _objects[1].getEnd():
                    self.setPointC(_objects[0].getEnd())
                    self.setPoint1(_objects[0].getBegin())
                    self.setPoint2(_objects[1].getBegin())
                else:
                    return False
                
                return True
        
        return False
    
    def setPoint1(self, _point1):
        """Set first base point
        """
        
        if self.point1 is not None:
            self.point1.removeLinkedObject(suit.core.objects.Object.LS_BASEONTHIS, self)
        
        self.point1 = _point1
        self.needMeshUpdate = True
        self.needUpdate = True
        
        if self.point1 is not None:
            self.point1.addLinkedObject(suit.core.objects.Object.LS_BASEONTHIS, self)
        
    def setPoint2(self, _point2):
        """Set second base point
        """
        if self.point2 is not None:
            self.point2.removeLinkedObject(suit.core.objects.Object.LS_BASEONTHIS, self)
            
        self.point2 = _point2
        self.needMeshUpdate = True
        self.needUpdate = True

        if self.point2 is not None:
            self.point2.addLinkedObject(suit.core.objects.Object.LS_BASEONTHIS, self)
        
    def setPointC(self, _pointC):
        """Set center base point
        """
        if self.pointC is not None:
            self.pointC.removeLinkedObject(suit.core.objects.Object.LS_BASEONTHIS, self)
            
        self.pointC = _pointC
        self.needMeshUpdate = True
        self.needUpdate = True
        
        if self.pointC is not None:
            self.pointC.addLinkedObject(suit.core.objects.Object.LS_BASEONTHIS, self)
    
    def setEqualGroup(self, newGroup):
        
        GeometryAbstractObject.setEqualGroup(self, newGroup)
        
        self.needUpdate = True
        self.needMeshUpdate = True
    
    def _checkRayIntersect(self, ray):
        """Check if ray intersects angle object.
                
        @param ray:    ray for intersection checking
        @type ray:    ogre.Ray
        """
        res, pos = suit.core.objects.ObjectDepth._checkRayIntersect(self, ray)
        if not res:
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
        
        # calculate angle value
        p1 = self.point1.getPosition()
        p2 = self.point2.getPosition()
        pC = self.pointC.getPosition()
        
        a1 = math.atan2(p1[1] - pC[1], p1[0] - pC[0])
        a2 = math.atan2(p2[1] - pC[1], p2[0] - pC[0])
        aD = math.atan2(d[1] - pC[1], d[0] - pC[0])
        
        a1 = math.degrees(a1)
        a2 = math.degrees(a2)
        aD = math.degrees(aD)
                        
        if a1 < 0:
            a1 += 360
        if a2 < 0:
            a2 += 360
            
#        if a1 < a2:
#            a1 += 360
            
        if aD < 0:
            aD += 360

        if (aD < min([a1, a2])) or (aD > max([a1, a2])):
            return False, -1
        
        dist = pC.distance(d)
        
        #if math.fabs(dist - self.radius) <= self.width / 2.0:
        groups = 0
        if self.equalGroup is not None:
            groups = self.equalGroup
        r_out = self.width * groups * 2 + self.radius
        if dist < r_out:
            return True, 0
        
        return False, -1
    

    def get_idtf(self):
        """Returns object identifier.
        It parse structures like: Point(A), Point A, pA and return A
        """
        return self.getText()
        
    def build_text_idtf(self):
        """Builds text identifier for an object
        """        
        idtf = self.get_idtf()
        if idtf is None:
            return None
        
        idtf1 = self.point1.build_text_idtf()
        idtfC = self.pointC.build_text_idtf()
        idtf2 = self.point2.build_text_idtf()
        
        if idtf1 is None or idtfC is None or idtf2 is None:
            return None
        
        return "%s(%s;%s;%s)" % (u'Угол', idtf1, idtfC, idtf2)
     
class GeometryUnion(suit.core.objects.ObjectDepth):
    """Object that represents objects union.
    
    It can consist of any count of objects.
    """
    
    def __init__(self):
        suit.core.objects.ObjectDepth.__init__(self)
        
        self.objects = []
        
    def __del__(self):
        suit.core.objects.ObjectDepth.__del__(self)
        
    def _checkRayIntersect(self, ray):
        """Check if ray intersects union object.
        Just check if it intersects any of object included to union.
        
        @param ray:    ray for intersection checking
        @type ray:    ogre.Ray
        """
        for obj in self.objects:
            res = obj._checkRayIntersect(ray)
            if res[0]: 
                return res
        
        return False, -1
    
    
    def appendObject(self, _obj):
        """Appends object to union
        @param _obj:    object to append
        @type _obj:    suit.core.objects.ObjectDepth
        """
        if not isinstance(_obj, suit.core.objects.ObjectDepth):
            raise TypeError("Unsupported type of object '%s' in union '%s'" % (str(_obj), str(self)))
        
        if _obj in self.objects:
            raise suit.core.exceptions.ItemAlreadyExistsError("Object '%s' already exists in union '%s'" % (str(_obj), str(self)))
        
        self.objects.append(_obj)
        
    def removeObject(self, _obj):
        """Removes object from union
        @param _obj:    object for removing
        @type _obj:    suit.core.objects.ObjectDepth
        """
        pass