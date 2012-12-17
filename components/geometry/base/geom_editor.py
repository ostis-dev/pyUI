
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
import suit.core.render.engine as render_engine
import ogre.io.OIS as ois
import geom_viewer
import geom_objects as gobjects
import geom_modes
import ogre.renderer.OGRE as ogre

from suit.cf import BaseModeLogic
from suit.core.objects import Object


class GeometryEditor(BaseModeLogic):
    
    def __init__(self, _viewer = None):
        BaseModeLogic.__init__(self)
        
        # creating geometry viewer if need
        if _viewer is not None:
            self._viewer = _viewer
            sheet = self._viewer._getSheet()
            if sheet is None:   raise RuntimeError("There is no sheet")
        else:
            self._viewer = geom_viewer.GeometryViewer()
        
        # merging viewer modes
        self.mergeModes(self._viewer)
        self.appendMode(ois.KC_E, geom_modes.GeometryEditMode(self))
        self.switchMode(ois.KC_E)
        
    def __del__(self):
        BaseModeLogic.__del__(self)
        
    def delete(self):
        """Deletion message
        """
        BaseModeLogic.delete(self)
        
        self._viewer.delete()
        
    def __getattr__(self, _name):
        """Returning attributes that exists in viewer to unify
        calling from modes
        """
        return getattr(self._viewer, _name)
        
    def _setSheet(self, _sheet):
        """Notification on sheet changed
        
        @param _sheet: new sheet controlled by logic
        @type _sheet: objects.ObjectSheet 
        """
        self._viewer._setSheet(_sheet)
        BaseModeLogic._setSheet(self, _sheet)
        
        _sheet.eventRootChanged = self._onRootChanged
        
    def _onRootChanged(self, _isRoot):
        """Notification message on sheet root changed
        """
        self._viewer._onRootChanged(_isRoot)
        BaseModeLogic._onRootChanged(self, _isRoot)
        
        
    def createPoint(self, _pos):
        """Creates point based on mouse position
        @param _pos: mouse coordinates
        @type _pos: tuple 
        
        @return: created geometry point object
        @rtype: GeometryPoint
        """
        point_obj = gobjects.GeometryPoint()
        point_obj.setPosition(render_engine.pos2dTo3dIsoPos(_pos))
        point_obj.setState(Object.OS_Normal)
        
        point_obj.setText(point_obj.getAvailableName())
        
        return point_obj
    
    def createLineSection(self, _beg, _end):
        """Creates line section
        @param _beg: begin point object
        @type _beg: GeometryPoint
        @param _end: end point object
        @type _end: GeometryPoint
        @return: created line section object
        @rtype: GeometryLineSection 
        """
        endPosition = _end.getPosition()
        line_obj = gobjects.GeometryLineSection()
        line_obj.setBegin(_beg)
        line_obj.setEnd(_end)
        line_obj.setState(Object.OS_Normal)
        _end.setPosition(_beg.getPosition())
        line_obj._update(0)
        _end.setPosition(endPosition)
        return line_obj

    def createCircle(self):
        """Create circle object
        @return: Return created circle object 
        """
        return gobjects.GeometryCircle()
    
    def createAngle(self):
        """Create new angle object
        """
        return gobjects.GeometryAngle()
    
    def createTriangle(self):
        return gobjects.GeometryTriangle()
    
    def createQuadrangle(self):
        return gobjects.GeometryQuadrangle()
