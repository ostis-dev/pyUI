
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
Created on 8.04.2010

@author: Denis Koronchick

Modified on 8.04.2010
by Maxim Kaskevich
'''
import suit.core.render.engine as render_engine
import ogre.renderer.OGRE as ogre
import ogre.io.OIS as ois
import graph_viewer
import graph_objects as gobjects
import graph_modes

from suit.cf import BaseModeLogic
from suit.core.objects import Object


class GraphEditor(BaseModeLogic):
    
    def __init__(self, _viewer = None):
        BaseModeLogic.__init__(self)
        
        # creating graph viewer if need
        if _viewer is not None:
            self._viewer = _viewer
            sheet = self._viewer._getSheet()
            if sheet is None:   raise RuntimeError("There is no sheet")
        else:
            self._viewer = graph_viewer.GraphViewer()
        
        # merging viewer modes
        self.mergeModes(self._viewer)
        self.appendMode(ois.KC_E, graph_modes.GraphEditMode(self))
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
        
        
