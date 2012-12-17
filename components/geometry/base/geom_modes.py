
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
Created on 18.12.2009

@author: Denis Koronchik
'''
import ogre.renderer.OGRE as ogre
import ogre.io.OIS as ois

from suit.cf import BaseEditMode
from suit.cf import BaseViewMode
from suit.cf.TextInput import TextInput
from suit.core.objects import Object
from geom_objects import GeometryPoint
from geom_objects import GeometryLineSection
from geom_objects import GeometryTriangle
from geom_objects import GeometryQuadrangle
from geom_objects import GeometryCircle
from geom_objects import GeometryAbstractObject

import suit.cf.utils as comutils
import suit.core.render.engine as render_engine
import geom_controls

class GeometryEditMode(BaseEditMode):
    
    # states
    ES_Move, \
    ES_LineCreate, \
    ES_CircleCreate, \
    ES_LengthChange, \
    ES_SquareChange, \
    ES_PerimeterChange, \
    ES_Count = range(BaseEditMode.ES_Count + 1, BaseEditMode.ES_Count + 8)
    
    def __init__(self, _logic):
        BaseEditMode.__init__(self, _logic, "Geometry edit")
        
        # last scroll position
        self.last_scroll_pos = None
        
        # grid align mode
        self.grid_align = True
        self.mouse_pos = (0, 0)
        self.objectInfoPanel = geom_controls.ObjectInfoPanel()
        
        # objects we works with
        self.highlighted_obj = None
        # current edit state
        self.state = GeometryEditMode.ES_None
        # current object we worked with
        self.active_object = None
        # candidate object to be processed with mouse
        self.candidate_object = None
        # line creation mode
        self.__pointSpirit = GeometryPoint()
        self.__pointSpirit.setState(Object.OS_Normal)
        self.__pointSpirit.setScale(ogre.Vector3(0.5, 0.5, 0.5))
        self.__lineSpirit = GeometryLineSection()
        self.__lineSpirit.setState(Object.OS_Normal)        
        self.__lineSpirit.setEnd(self.__pointSpirit) 
        self.__lineBegin = None
                
    def __del__(self):
        BaseEditMode.__del__(self)
        
    def delete(self):
        self.objectInfoPanel.delete()
        BaseEditMode.delete(self)
        
    def activate(self):
        BaseEditMode.activate(self)
        
    def deactivate(self):
        BaseEditMode.deactivate(self)
    
    def _onRootChanged(self, _isRoot):
        BaseEditMode._onRootChanged(self, _isRoot)
        self.objectInfoPanel.setVisible(_isRoot)
        
    def _selectObject(self, _object):
        BaseEditMode._selectObject(self, _object)
        
        self.objectInfoPanel.setObject(_object)
        
    def _unselectObject(self, _object):
        BaseEditMode._unselectObject(self, _object)
        
        selected = self._logic._getSheet().getSelected()
        if len(selected) > 0:
            self.objectInfoPanel.setObject(selected[-1])
        else:
            self.objectInfoPanel.setObject(None)
    
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
            self.highlighted_obj.resetState()
#            if self.highlighted_obj._getSelected():
#                self.highlighted_obj.setState(Object.OS_Selected)
#            else:
#                self.highlighted_obj.setState(Object.OS_Normal)
        self.highlighted_obj = obj
        if self.highlighted_obj:    self.highlighted_obj.setState(Object.OS_Highlighted)
    
    def _getMousePos(self, _state):
        """Returns mouse position based on state and align mode
        @return: mouse position
        @rtype: tuple(int, int)
        """
        if self.grid_align:
            return self._logic.positionMouseToGrid((_state.X.abs, _state.Y.abs))
        else:
            return (_state.X.abs, _state.Y.abs)
        
    def _onMouseMoved(self, _evt):
        """Mouse moved notification event
        """
        if BaseEditMode._onMouseMoved(self, _evt):  return True
      
        mstate = _evt.get_state()
        mpos = self._getMousePos(mstate)
        self.mouse_pos = (mstate.X.abs, mstate.Y.abs)
        
        if self.state is GeometryEditMode.ES_Move:
            self.active_object.setPosition(render_engine.pos2dTo3dIsoPos(mpos))
            return True
        
        elif self.state is GeometryEditMode.ES_LineCreate:
            self.__pointSpirit.setPosition(render_engine.pos2dTo3dIsoPos(mpos))
            self._updateLineSpirits()
            self._highlight()
            return True
        elif self.state is GeometryEditMode.ES_CircleCreate:
            radius = self.active_object.getPosition().distance(render_engine.pos2dTo3dIsoPos(mpos))
            self.active_object.setRadius(radius)
        
        self._highlight()
        
        return False
        
    def _onMousePressed(self, _evt, _id):
        """Event on mouse button pressed
        """
        if BaseEditMode._onMousePressed(self, _evt, _id):   return True
        
        mstate = _evt.get_state()
        original_mpos = (mstate.X.abs, mstate.Y.abs)
        mpos = self._getMousePos(mstate)

        # getting objects under mouse
        mobjects = self._logic._getSheet()._getObjectsUnderMouse(True, True, self.mouse_pos)

        if _id == ois.MB_Right:
            # none any mode
            if self.state is GeometryEditMode.ES_None:
                # creating point if there is no any objects under mouse
                if len(mobjects) is 0:
                    obj = self._logic.createPoint(mpos)
                    sheet = self._logic._getSheet()
                    sheet.addChild(obj)
                    return True
                else:
                    # get line sections
                    line = comutils._getFirstObjectTypeFromList(mobjects, [GeometryLineSection, GeometryCircle])
                    if line is not None:
                        # create point
                        point = self._logic.createPoint(original_mpos)
                        sheet = self._logic._getSheet()
                        sheet.addChild(point)
                        
                        # append it into line section
                        line.addPoint(point, line._calculatePointRelPosition(render_engine.pos2dTo3dIsoPos(original_mpos)))
                        
                        self.objectInfoPanel.update()
                        return True
                    
                    obj = comutils._getFirstObjectTypeFromList(mobjects, [GeometryPoint])
                    if obj is not None:
                        self.state = GeometryEditMode.ES_LineCreate
                        self.__lineSpirit.setBegin(obj)
                        sheet = self._logic._getSheet()
                        sheet.sceneNodeChilds.addChild(self.__lineSpirit.sceneNode)
                        sheet.sceneNodeChilds.addChild(self.__pointSpirit.sceneNode)
                        self.__lineBegin = obj
                        self.__pointSpirit.setPosition(render_engine.pos2dTo3dIsoPos(mpos))
                        self._updateLineSpirits()
                        
                        self.objectInfoPanel.update()
                        return True
            # on line creation mode finishing line
            elif self.state is GeometryEditMode.ES_LineCreate:
                obj = comutils._getFirstObjectTypeFromList(mobjects, [GeometryPoint])
                sheet = self._logic._getSheet()
                if obj is not None:
                    # creating line
                    line = self._logic.createLineSection(self.__lineBegin, obj)
                    sheet.addChild(line)
                    
                # removing state
                self.state = GeometryEditMode.ES_None
                sheet.sceneNodeChilds.removeChild(self.__lineSpirit.sceneNode)
                sheet.sceneNodeChilds.removeChild(self.__pointSpirit.sceneNode)
                self.__lineBegin = None
                    
            
        elif _id == ois.MB_Left:
            # if there is an any object under mouse, then starts moving
            if len(mobjects) > 0 and self.state is GeometryEditMode.ES_None:
                if self.candidate_object is not None and self.candidate_object._getSelected() and not self._shift:
                    self._unselectObject(self.candidate_object)
                self._next_candidate()
                self.active_object = self.candidate_object#comutils._getFirstObjectTypeFromList(mobjects, [GeometryPoint])
                if self.active_object is not None:
                    self.state = GeometryEditMode.ES_Move
                    self._selectObject(self.active_object)
                else:
                    # selecting first object under mouse
                    self._selectObject(mobjects[0][1])
                
                return True
            elif self.state is GeometryEditMode.ES_CircleCreate:
                
                _point = comutils._getFirstObjectTypeFromList(mobjects, [GeometryPoint])
                if _point is not None:
                    self.active_object.setRadiusPoint(_point)
                
                self.active_object = None
                self.state = GeometryEditMode.ES_None
            
        return False
                 
            
    def _onMouseReleased(self, _evt, _id):
        """Event on mouse button released
        """
        if BaseEditMode._onMouseReleased(self, _evt, _id):  return True
        
        mstate = _evt.get_state()
        mpos = self._getMousePos(mstate)
        
        if _id == ois.MB_Left:
            
            # moving state finishing
            if self.state is GeometryEditMode.ES_Move:
                self.state = GeometryEditMode.ES_None
#                self._selectObject(self.active_object)
                self.active_object = None                
        
        return False
    
    def _onKeyPressed(self, _evt):
        """Event on key pressed
        """
        
        if BaseEditMode._onKeyPressed(self, _evt):  return True
        
        key = _evt.key
        
        if key == ois.KC_C:
            _selected = self._logic._getSheet().getSelected()
            self.active_object = self._logic.createCircle()
            if self.active_object.makeBasedOnObjects(_selected):
                self._logic._getSheet().addChild(self.active_object)
            else:
                self.active_object.delete()
            self.active_object = None
            
        if key == ois.KC_A:
            _selected = self._logic._getSheet().getSelected()
            self.active_object = self._logic.createAngle()
            if self.active_object.makeBasedOnObjects(_selected):
                self._logic._getSheet().addChild(self.active_object)
            else:
                self.active_object.delete()
            self.active_object = None
            
        if key == ois.KC_T:
            _selected = self._logic._getSheet().getSelected()
            self.active_object = self._logic.createTriangle()
            if self.active_object.makeBasedOnObjects(_selected):
                self._logic._getSheet().addChild(self.active_object)
            else:
                self.active_object.delete()
            self.active_object = None
            
        if key == ois.KC_Q:
            _selected = self._logic._getSheet().getSelected()
            self.active_object = self._logic.createQuadrangle()
            if self.active_object.makeBasedOnObjects(_selected):
                self._logic._getSheet().addChild(self.active_object)
            else:
                self.active_object.delete()
            self.active_object = None
                    
        if key == ois.KC_L:
            selected = self._logic._getSheet().getSelected()
            if len(selected) == 1:
                obj = selected[0]
                if isinstance(selected[0], (GeometryLineSection, GeometryCircle)):
                    self.state = GeometryEditMode.ES_LengthChange
                    self.length_changer = TextInput(obj, self._length_change_callback, obj.getPropertyValue(GeometryAbstractObject.PropLength))
                
        if key == ois.KC_E:
            selected = self._logic._getSheet().getSelected()
            if len(selected) == 2:
                if isinstance(selected[0], selected[1].__class__):
                    selected[0].setEqualTo(selected[1])
                    if self.objectInfoPanel.getObject() is selected[0] or self.objectInfoPanel.getObject() is selected[1]:
                        self.objectInfoPanel.update()              
        
        if key == ois.KC_S:
            selected = self._logic._getSheet().getSelected()
            if len(selected) == 1:
                obj = selected[0]
                if isinstance(obj, (GeometryCircle, GeometryTriangle, GeometryQuadrangle)):
                    self.state = GeometryEditMode.ES_SquareChange
                    self.square_changer = TextInput(obj, self._square_change_callback, obj.getPropertyValue(GeometryAbstractObject.PropSquare))
                    
        if key == ois.KC_P:
            selected = self._logic._getSheet().getSelected()
            if len(selected) == 1:
                obj = selected[0]
                if isinstance(obj, (GeometryTriangle, GeometryQuadrangle)):
                    self.state = GeometryEditMode.ES_PerimeterChange
                    self.perimetr_changer = TextInput(obj, self._perimeter_change_callback, obj.getPropertyValue(GeometryAbstractObject.PropPerimeter))

        if key == ois.KC_V:
            selected = self._logic._getSheet().getSelected()
            for obj in selected:
                if isinstance(obj, GeometryQuadrangle):
                    if obj.canHaveInCircle():

                        points = obj.getInCirclePoints()
                        sheet = self._logic._getSheet()

                        c = self._logic.createPoint(render_engine.pos3dTo2dWindow(points[0]))
                        sheet.addChild(c)
                        c._updateView()

                        p = self._logic.createPoint(render_engine.pos3dTo2dWindow(points[1]))
                        sheet.addChild(p)
                        p._updateView()

                        self.active_object = self._logic.createCircle()
                        if self.active_object.makeBasedOnObjects([c, p]):
                            sheet.addChild(self.active_object)
                        else:
                            self.active_object.delete()
                        self.active_object = None

        return False
    
    def _onKeyReleased(self, _evt):
        """Event key released
        """
        if BaseEditMode._onKeyReleased(self, _evt): return True
        return False
    
    def _next_candidate(self):
        """Find next candidate object for mouse processing 
        """
        mobjects = self._logic._getSheet()._getObjectsUnderMouse(True, True, self.mouse_pos)      
        self.candidate_object = self._get_next_from_mouse_object_list(self.candidate_object, mobjects)
               
    def _prev_candidate(self):
        """Find previous candidate object for mouse processing
        """
        mobjects = self._logic._getSheet()._getObjectsUnderMouse(True, True, self.mouse_pos)
        self.candidate_object = self._get_prev_from_mouse_object_list(self.candidate_object, mobjects)
        
    
    def _length_change_callback(self, _object, _value):
        """Callback on line length changing
        """
        self.state = GeometryEditMode.ES_None
        if _value is not None:
            v = None
            try:
                v = float(str(_value))
                
            except ValueError:
                print "Non-numeric value found %s" % str(_value)
                
            if v is not None:
                _object.setPropertyValue(GeometryAbstractObject.PropLength, v)
        
        del self.length_changer
        
        if self.objectInfoPanel.getObject() is _object:
            self.objectInfoPanel.update()
        
    def _square_change_callback(self, _object, _value):
        """Callback on square change
        """
        self.state = GeometryEditMode.ES_None
        if _value is not None:
            v = None
            try:
                v = float(str(_value))
            except:
                print "Non-numeric value found %s" % str(_value)
            
            if v is not None:
                _object.setPropertyValue(GeometryAbstractObject.PropSquare, v)
                
        del self.square_changer
        
        if self.objectInfoPanel.getObject() is _object:
            self.objectInfoPanel.update()
        
    def _perimeter_change_callback(self, _object, _value):
        """Callback on perimeter change
        """
        self.state = GeometryEditMode.ES_None
        if _value is not None:
            v = None
            try:
                v = float(str(_value))
            except:
                print "Non-numeric value found %s" % str(_value)
            
            if v is not None:
                _object.setPropertyValue(GeometryAbstractObject.PropPerimeter, v)
                
        del self.perimetr_changer
        
        if self.objectInfoPanel.getObject() is _object:
            self.objectInfoPanel.update()
    
    def _updateLineSpirits(self):
        """Updates spirit objects used in line creation mode
        """
        self.__pointSpirit.needUpdate = True
        self.__pointSpirit._update(0)
        self.__lineSpirit.needUpdate = True
        self.__lineSpirit._update(0)
        
    def _objectDeleted(self, obj):
        """Notification about object deletion
        """
        if self.candidate_object is obj:
            self.candidate_object = None
        
        if self.objectInfoPanel.getObject() is obj:
            self.objectInfoPanel.setObject(None)

    def _check_in_mouse_object_list(self, _obj, _list):
        """Check if specified object is in mouse object list
        @param _obj: object for check 
        @param _list: List of tuples for objects, that are under mouse 
        """
        for v, obj in _list:
            if obj is _obj:
                return True
            
        return False
    
    def _get_next_from_mouse_object_list(self, _obj, _list):
        """Return object that placed after \p _obj in mouse object list.
        If it's a last object, then first object will be returned
        @param _obj: object to get next 
        @param _list: List of tuples for objects, that are under mouse 
        """
        ret = False
        for v, obj in _list:
            if ret is True:
                return obj
            if _obj is obj:
                ret = True
        if len(_list) == 0:
            return None
        
        return _list[0][1]
    
    def _get_prev_from_mouse_object_list(self, _obj, _list):
        """Return object that placed before \p _obj in mouse object list.
        If it's a first object, then last object will be returned
        @param _obj: object to get previous 
        @param _list: List of tuples for objects, that are under mouse 
        """
        prev = None
        for v, obj in _list:
            if _obj is obj:
                return prev
            prev = obj
            
        if len(_list) > 0:
            prev = _list[len(_list) - 1][1]
            
        return prev
        
        