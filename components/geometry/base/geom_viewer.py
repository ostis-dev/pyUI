
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

from suit.core.kernel import Kernel
import suit.core.objects as objects
from suit.cf.BaseModeLogic import BaseModeLogic
from suit.core.objects import BaseLogic
import suit.core.render.engine as render_engine
import ogre.io.OIS as ois
import ogre.renderer.OGRE as ogre
import geom_env as env

class GeometryViewer(BaseModeLogic):
    """Geometry viewer logic realization
    """
    def __init__(self):
        BaseModeLogic.__init__(self)
        
        # view modes
        self._modes = {}
        self.mode = None
        
        self.grid_material = ogre.MaterialManager.getSingleton().getByName(env.material_grid)
        
        self.needGridUpdate = True
        self.grid_size = 25.0
        self.is_root = False    # flag for root mode, need to store there for grow speed up
    
    def __del__(self):
        """Destruction
        """
        BaseModeLogic.__del__(self)
    
    def delete(self):
        """Deletion message
        """        
        BaseModeLogic.delete(self)
    
    def _setSheet(self, _sheet):
        BaseModeLogic._setSheet(self, _sheet)
        
        _sheet.eventRootChanged = self._onRootChanged
        _sheet.eventUpdate = self._onUpdate
        
        _sheet.eventChildAppend = self._onAppendChild
        _sheet.eventChildRemove = self._onRemoveChild
        _sheet.eventContentUpdate = self._onContentUpdate
        
        
    def _onRootChanged(self, _isRoot):
        """Notification message on sheet root changed
        """
        if _isRoot:
            sheet = self._getSheet()
            render_engine.SceneManager.setBackMaterial(env.material_grid)
        else:
            sheet = self._getSheet()
            render_engine.SceneManager.setDefaultBackMaterial()
            
        self.is_root = _isRoot
            
    def _onUpdate(self, _timeSinceLastFrame):
        """Notification on update
        """
        BaseLogic._update(self, _timeSinceLastFrame)
        
        if self.needGridUpdate:
            self.needGridUpdate = False
            self.updateGrid()
            
    def _onContentUpdate(self):
        
        import suit.core.keynodes as keynodes
        sheet = self._getSheet()
        
        sheet.content_type = objects.ObjectSheet.CT_String
        sheet.content_data = str("")
        sheet.content_format = keynodes.ui.format_geomx
        
    def _onAppendChild(self, _object):
        """Listener for sheet child objects appending
        """
#        geom_panel.append_object(_object)
        pass
        
    def _onRemoveChild(self, _object):
        """Listener for sheet child objects removing
        """
#        geom_panel.remove_object(_object)
        pass
            
    def setGridSize(self, _gridSize):
        """Sets new grid size
        
        @param _gridSize: new grid size
        @type _gridSize: int  
        """
        self.grid_size = _gridSize
        self.needGridUpdate = True
    
    def updateGrid(self):
        """Updates grid to new size.
        Recalculates multipliers for window coordinates -> space transform.
        It is need to calculate position on grid
        """
        # FIXME:    Add scrolling support
        self.grid_material.getTechnique(0).getPass(0).getFragmentProgramParameters().setNamedConstant("gridSize", self.grid_size)
        
    def positionMouseToGrid(self, _pos):
        """Translates mouse position to mouse position on grid
        @param _pos: mouse position
        @type _pos: tuple(int, int)
        
        @return: calculated mouse position on grid
        @rtype: tuple(int, int)  
        """
        # FIXME:    Add scrolling support
        return (int(_pos[0] / self.grid_size + 0.5) * self.grid_size, int(_pos[1] / self.grid_size + 0.5) * self.grid_size)
    