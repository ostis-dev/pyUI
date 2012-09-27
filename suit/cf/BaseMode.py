
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
Created on 25.12.2009

@author: Denis Koronchik
'''

import ogre.io.OIS as ois


class BaseMode:
    """Base class for modes
    This class has dictionary of key bindings (key code, function). Key binding functions
    hasn't any parameters.
    By default it has bindings for keys:
    - A - selecting / unselecting objects. If there are no any objects selected, then
     selects all objects, else remove selection from selected objects.
     
    It have logic for mouse:
    - 
    """
    def __init__(self, _logic, _name = "Unknown mode"):
        
        assert _logic is not None and _name is not None
        
        self._logic = _logic
        self.name = _name
        self.cursor = None
        self.active = False
        # key bindings
        self.key_press_bindings = {}
        self.key_release_bindings = {}
        
    def __del__(self):
        print "__del__ in %s" % str(self)
    
    def delete(self):
        """Deletion message
        """
        self.key_press_bindings = None
        self.key_release_bindings = None
        self._logic = None
        
    
    def activate(self):
        """Notification on mode activate.
        Only for internal usage
        """
        self.active = True
    
    def deactivate(self):
        """Notification on mode deactivate.
        Only for internal usage
        """
        self.active = False
        
    def isActive(self):
        """Check if mode is active
        """
        return self.active
    
    def _onRootChanged(self, _isRoot):
        """Notification on sheet root change
        """
        pass
    
    def _update(self, timeSinceLastFrame):
        """Update message
        """
        pass
    
    def _onMouseMoved(self, _evt):
        return False
    
    def _onMousePressed(self, _evt, _id):
        return False
    
    def _onMouseReleased(self, _evt, _id):
        return False
    
    def _onKeyPressed(self, _evt):
        
        if self.key_press_bindings.has_key(_evt.key):
            self.key_press_bindings[_evt.key]()
            return True
        
        return False
     
    def _onKeyReleased(self, _evt):
        
        if self.key_release_bindings.has_key(_evt.key):
            self.key_release_bindings[_evt.key]()
            return True
        
        return False

    # work with bindings
    def bindKeyPress(self, _key, _bind_func):
        """Adds binding for a key press event
        @param _key: key code
        @type _key: ois.KeyCode
        @param _bind_func: function binded for a key
        @type _bind_func: function    
        """
        if self.key_press_bindings.has_key(_key):
            raise RuntimeWarning("Binding for key %s press already exists" % _key)
        self.key_press_bindings[_key] = _bind_func
        
    def unbindKeyPress(self, _key):
        """Removes binding for a key release event
        @param _key: key code
        @type _key: ois.KeyCode  
        """
        self.key_press_bindings.pop(_key)
        
    def bindKeyRelease(self, _key, _bind_func):
        """Adds binding for a key release event
        @param _key: key code
        @type _key: ois.KeyCode
        @param _bind_func: function binded for a key
        @type _bind_func: function    
        """
        if self.key_release_bindings.has_key(_key):
            raise RuntimeWarning("Binding for key %s release already exists" % _key)
        self.key_release_bindings[_key] = _bind_func
        
    def unbindKeyRelease(self, _key):
        """Removes binding for a key release event
        @param _key: key code
        @type _key: ois.KeyCode  
        """
        self.key_release_bindings.pop(_key)