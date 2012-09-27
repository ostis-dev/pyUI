
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
Created on 02.01.2010

@author: Denis Koronchik
'''
import suit.core.objects as objects
import ogre.io.OIS as ois

class BaseModeLogic(objects.BaseLogic):
    """Class that realize base logic for mode oriented viewers and editors 
    """
    def __init__(self):
        """Construction
        """
        objects.BaseLogic.__init__(self)
        # dictionary of available modes
        self._modes = {}
        # active mode
        self._active_mode = None
        self._active_mode_key = None
        self._alt = False

    
    def __del__(self):
        objects.BaseLogic.__del__(self) 
        
    def delete(self):
        """Deletion message
        """
        self._active_mode = None
        for mode in self._modes.itervalues():
            mode.delete()
        self._modes = None
        
        print "__del__ in %s" % str(self)
    
    def mergeModes(self, _mode_logic):
        """Merges current logic with another.
        In result it will be add modes from _mode_logic to self.
        
        @param _mode_logic: another mode based logic to merge
        @type _mode_logic: BaseModeLogic
        """
        for key, value in _mode_logic._modes.items():
            self._modes[key] = value
            
    def _setSheet(self, _sheet):
        """Notification on sheet setup for current logic
        
        @param _sheet: new sheet
        @type _sheet: srs_engine.objects.ObjectSheet  
        """
        objects.BaseLogic._setSheet(self, _sheet)
        
        _sheet.eventMouseMoved = self._onMouseMoved
        _sheet.eventMousePressed = self._onMousePressed
        _sheet.eventMouseReleased = self._onMouseReleased
        
        _sheet.eventKeyPressed = self._onKeyPressed
        _sheet.eventKeyReleased = self._onKeyReleased
        
        _sheet.eventDelete = self._onSheetDelete
        
#        _sheet.eventUpdate = self._onUpdate

    def _onSheetDelete(self, _object):
        """Sheet deletion event handler
        """
#        for mode in self._modes.itervalues():
#            mode._delete()
        # FIXME:    mode deletion
        pass
       
    def appendMode(self, _key, _mode):
        """Append new mode by key
        @param _key: key to store mode in dictionary
        @type _key: int (ois.KeyCode)
        
        @param _mode: instance of objects, that realize mode
        @type _mode: BaseMode 
        """
        if self._modes.has_key(_key):  raise KeyError("Another mode already binded to '%s'" % str(_key))
        self._modes[_key] = _mode
        
    def removeMode(self, _key):
        """Removes mode by key
        @param _key: mode key to remove
        @type _key: int (ois.KeyCode) 
        """
        if self._modes[_key] is self._active_mode:
            self._switchMode(None)
        self._modes.pop(_key)
        
    def updateActiveMode(self, _timeSinceLastFrame):
        if self._active_mode:   self._active_mode._update(_timeSinceLastFrame)

    def switchMode(self, _key):
        """Switches active mode to another.
        You could disable all modes by setting _key parameter to None value
        
        @param _key: key of mode that would be activated
        @type _key: int
        """
        if self._active_mode is not None:
            self._active_mode.deactivate()
            self._active_mode = None
            
        if _key is not None:
            self._active_mode = self._modes[_key]
            self._active_mode.activate()
            self._active_mode_key = _key
        
    def _onRootChanged(self, _isRoot):
        if _isRoot:
            self._active_mode.activate()
        else:
            self._active_mode.deactivate()
            
        self._active_mode._onRootChanged(_isRoot)
        
        
    def _onMouseMoved(self, _evt):
        """Mouse moved event
        @param _evt: mouse event object
        @type _evt: ois.MouseEvent  
        """
        if self._active_mode is not None:
            return self._active_mode._onMouseMoved(_evt)
        else:
            return False
    
    def _onMousePressed(self, _evt, _id):
        """Mouse pressed event
        @param _evt: mouse event object
        @type _evt: ois.MouseEvent  
        @param _id: pressed button id
        @type _id: ois.MouseButtonID
        """
        if self._active_mode is not None:
            return self._active_mode._onMousePressed(_evt, _id)
        else:
            return False
    
    def _onMouseReleased(self, _evt, _id):
        """Mouse released event
        @param _evt: mouse event object
        @type _evt: ois.MouseEvent
        @param _id: released button id
        @type _id: ois.MouseButtonID    
        """
        if self._active_mode is not None:
            return self._active_mode._onMouseReleased(_evt, _id)
        else:
            return False
    
    def _onKeyPressed(self, _evt):
        """Key pressed event
        """
        
        if _evt.key == ois.KC_LSHIFT:
            self._alt = True
        
        if self._active_mode is not None:
            return self._active_mode._onKeyPressed(_evt)
        else:
            return False
    
    def _onKeyReleased(self, _evt):
        """Key released event
        """
        # switching mode
        if _evt.key == ois.KC_LSHIFT:
            self._alt = False
        
        if self._active_mode is not None:
            return self._active_mode._onKeyReleased(_evt)
        else:
            return False