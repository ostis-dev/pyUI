
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
from BaseMode import BaseMode
from TextInput import TextInput 
import ogre.io.OIS as ois

class BaseEditMode(BaseMode):
    """Base class for modes
    It has binds for keys:
    - A - selecting / unselecting objects. If there are no any objects selected, then
     selects all objects, else remove selection from selected objects.
     
    It have logic for mouse:
    - 
    """
    
    # editor states
    ES_None, ES_IdtfChange, ES_Count = range(3)
    
    def __init__(self, _logic, _name = "Unknown mode"):
        BaseMode.__init__(self, _logic, _name)
        # shift pressed flag
        self._shift = False
        self._ctrl = False
        # current state
        self.state = BaseEditMode.ES_None
        
        # initializing bindings
        #self.bindKeyPress(ois.KC_A, self._selectAll)
        self.bindKeyPress(ois.KC_I, self._setIdtf)
        self.bindKeyPress(ois.KC_DELETE, self._delete)
        self.bindKeyPress(ois.KC_R, self._setRoot)
        
    def __del__(self):
        BaseMode.__del__(self)
    
    def delete(self):
        """Deletion message
        """
        BaseMode.delete(self)
    
    def _activate(self):
        """Notification on mode activate.
        Only for internal usage
        """
        self.active = True
    
    def _onMouseMoved(self, _evt):
        if BaseMode._onMouseMoved(self, _evt):  return True
        
        return False
    
    def _onMousePressed(self, _evt, _id):
        if BaseMode._onMousePressed(self, _evt, _id):   return True
        
        return False
    
    def _onMouseReleased(self, _evt, _id):
        if BaseMode._onMouseReleased(self, _evt, _id):  return True
        
        return False
    
    def _onKeyPressed(self, _evt):
        
        if BaseMode._onKeyPressed(self, _evt):  return True
        
        key = _evt.key
        
        if key == ois.KC_LSHIFT:
            self._shift = True
        elif key == ois.KC_LCONTROL:
            self._ctrl = True
            
        if key == ois.KC_A and self._ctrl:
            self._selectAll()
            
        return False
    
    def _onKeyReleased(self, _evt):
        
        if BaseMode._onKeyReleased(self, _evt): return True
        
        key = _evt.key
        
        if key == ois.KC_LSHIFT:
            self._shift = False
        elif key == ois.KC_LCONTROL:
            self._ctrl = False
        
        return False
    
    def _objectDeleted(self, obj):
        """Calls after object deletion
        @param obj: Deleted object 
        """
        pass
    
    ########################
    #### Identificators ####
    ########################
    def _setIdtf(self):
        """Bind function for identificator changing
        """
        if self.state == BaseEditMode.ES_None:
            sheet = self._logic._getSheet()
            objs = sheet.getSelected()
            # get object for text changing 
            if len(objs) == 1 and objs[0]._getScAddr() is None:
                self.state = BaseEditMode.ES_IdtfChange
                self.idtf_changer = TextInput(objs[0], self._idtf_callback, objs[0].getText())
                 
    def _idtf_callback(self, _object, _value):
        """Callback for identificator changing finished
        """
        self.state = BaseEditMode.ES_None
        if _value is not None:
            _object.setText(_value)
            _object.setTextVisible(True)
        del self.idtf_changer
            
    
    ####################
    ##### Selection ####
    ####################
    def _selectAll(self):
        """Bind function on select all
        """      
        sheet = self._logic._getSheet()   
        if sheet.haveSelected():
            sheet.unselectAll()
        else:
            sheet.selectAll()
    
    def _selectObject(self, _object):
        """Selecting object on sheet
        """
        # selecting element
        sheet = self._logic._getSheet()
        if not _object._getSelected():
            if sheet.haveSelected() and not self._shift:
                sheet.unselectAll()
            sheet.select(_object)
            
    def _unselectObject(self, _object):
        """Unselecting object on sheet
        """
        sheet = self._logic._getSheet()
        sheet.unselect(_object)
    
    ##################
    #### Deleting ####
    ##################
    def _delete(self):
        """Bind function for deleting objects
        """
        # removing elements just if we doesn't moving or creating objects
        if self.state == BaseEditMode.ES_None:
            sheet = self._logic._getSheet()
            objs = [] + sheet.getSelected()
            for obj in objs:
                if obj.parent is not None:
                    sheet._deleteObject(obj)
                    self._objectDeleted(obj)
                    
                    
    ####################
    #### Graph Root ####
    ####################
    def _setRoot(self):
        """Bind function for graph root changing in radial graph layout
        """
        if self.state == BaseEditMode.ES_None:
            sheet = self._logic._getSheet()
            layout = sheet.getLayoutGroup()
            
            import suit.core.layout.LayoutGroupRadial as radialLayout
            if not isinstance(layout, radialLayout.LayoutGroupRadialSimple): 
                return
           
            objs = sheet.getSelected()
            # get object for root changing 
            if len(objs) == 1: 
                layout.setRoot(objs[0])
                
    
                     