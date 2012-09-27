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
Created on 19.04.2010

@author: Grechishkin Pavel
'''

"""SCg-editor component realization
"""
import ogre.io.OIS as ois
import ogre.renderer.OGRE as ogre
import suit.core.objects as objects
import suit.core.render.engine as render_engine
from space_viewer import SpaceViewer
from suit.cf import BaseModeLogic
#import scg_alphabet
#import scg_objects
#import scg_help
#import scg_modes



class SpaceEditor(BaseModeLogic):
    """Logic realization of Space-editor.
    
    To synchronize this object we use transaction model.
    Each transaction applies in update method. That guarantee
    ogre calls in one graphical thread.  
    """ 
    
    def __init__(self, viewer = None):
        """Constructor
        """
        BaseModeLogic.__init__(self)
        
        # setting new logic for a sheet if viewer already exists
        if viewer is not None:
            self.__viewer = viewer
            sheet = self.__viewer._getSheet()
            if sheet is None:   raise RuntimeError("There is no sheet")
        else:
            self.__viewer = SpaceViewer()
                     
        self.mergeModes(self.__viewer)
        self.appendMode(ois.KC_E, scg_modes.SCgEditMode(self))
        self.switchMode(ois.KC_E)
        
                   
    def __del__(self):
        """Destructor
        """
        BaseModeLogic.__del__(self)
        
    def delete(self):
        """Deletion message
        """
        BaseModeLogic.delete(self)
        if self.__viewer:   self.__viewer.delete()
        
    def __getattr__(self, _name):
        """Returning attributes that exists in viewer to unify
        calling from modes
        """
        return getattr(self.__viewer, _name)
        
    def _setSheet(self, _sheet):
        """Notification about sheet changed for logic
        
        @param _sheet: sheet object logic sets to
        @type _sheet: ObjectSheet  
         
        @attention: this method only for internal usage and calls by 
        ObhectSheet automatically when you set logic for it 
        """
        self.__viewer._setSheet(_sheet)
        BaseModeLogic._setSheet(self, _sheet)

        _sheet.eventUpdateView = self._onUpdateView
        _sheet.eventUpdate = self._onUpdate        
        
        _sheet.eventRootChanged = self._onRootChanged
                
        _sheet.eventSelectionChanged = self._modes[ois.KC_E]._handlerSelChanged
    
    def _onUpdate(self, _dt):
        """Update sheet event
        @param _dt: time since last frame
        @type _dt: float  
        """
        if self._active_mode is not None:
            self._active_mode._update(_dt)
    
    def _onUpdateView(self):
        """Update sheet view event
        """
        pass
    
    def _onRootChanged(self, _isRoot):
        """Root state changed event
        @param _isRoot: new root state
        @type _isRoot: bool  
        """
        BaseModeLogic._onRootChanged(self, _isRoot)        
            

        
