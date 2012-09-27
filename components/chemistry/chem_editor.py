
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

from suit.cf import BaseModeLogic
from chem_viewer import ChemistryViewer
import chem_modes

class ChemistryEditor(BaseModeLogic):
    
    def __init__(self, _viewer = None):
        BaseModeLogic.__init__(self)
        
        if not _viewer:
            self._viewer = ChemistryViewer()
        else:
            raise RuntimeError("Chemistry editor doesn't support existing viewers for now")
        
        self.mergeModes(self._viewer)

        import ogre.io.OIS as ois
        self.appendMode(ois.KC_E, chem_modes.ChemistryEditMode(self))
        self.switchMode(ois.KC_E)
        
    def __del__(self):
        BaseModeLogic.__del__(self)
        
    def __getattr__(self, _name):
        """Returning attributes that exists in viewer to unify
        calling from modes
        """
        return getattr(self._viewer, _name)
        
    def delete(self):
        """Deletion message
        """
        BaseModeLogic.delete(self)
        
    def _setSheet(self, _sheet):
        # process event to viewer
        self._viewer._setSheet(_sheet)
        
        BaseModeLogic._setSheet(self, _sheet)
        
        #subscribe events
        _sheet.eventRootChanged = self._onRootChanged
        _sheet.eventUpdate = self._onUpdate
        
    def _onUpdate(self, _timeSinceLastFrame):
        """Viewer update message
        """
        if self._active_mode is not None:
            self._active_mode._update(_timeSinceLastFrame)
        else:
            self._viewer._onUpdate(_timeSinceLastFrame)
        
        
    def _onRootChanged(self, _isRoot):
        """Root changing
        """
        self._viewer._onRootChanged(_isRoot)
        
        BaseModeLogic._onRootChanged(self, _isRoot)