
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
-----------------------------------------------------------------------------
"""


'''
Created on 18.12.2009

@author: Denis Koronchik

Modified on 8.04.2010
by Maxim Kaskevich
'''
import ogre.renderer.OGRE as ogre
import ogre.io.OIS as ois
#import mygui
import suit.core.render.mygui

from suit.cf import BaseEditMode
from suit.cf import BaseViewMode
from suit.cf import TextInput
from suit.core.objects import Object
from graph_objects import GraphVertex
from graph_objects import GraphLink

import suit.cf.utils as comutils
import suit.core.render.engine as render_engine


class GraphEditMode(BaseEditMode):
    
    # states
    ES_Move         =   BaseEditMode.ES_Count + 1
    ES_LineCreate   =   ES_Move + 1
    ES_Count        =   ES_LineCreate + 1
    
    
    
    def __init__(self, _logic):
        BaseEditMode.__init__(self, _logic, "Graph edit")
        
        # last scroll position
        self.last_scroll_pos = None
        
        # grid align mode
        self.mouse_pos = (0, 0)
        
        # objects we works with
        self.highlighted_obj = None
        # current edit state
        self.state = GraphEditMode.ES_None
        # current object we worked with
        self.active_object = None
        # line creation mode
        self.__pointSpirit = GraphVertex()
        self.__pointSpirit.setState(Object.OS_Normal)
        self.__pointSpirit.setScale(ogre.Vector3(0.5, 0.5, 0.5))
        self.__lineSpirit = GraphLink()
        self.__lineSpirit.setState(Object.OS_Normal)        
        self.__lineSpirit.setEnd(self.__pointSpirit) 
        self.__lineBegin = None
        
    def __del__(self):
        BaseEditMode.__del__(self) 
        
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
        if self.highlighted_obj is not None:
            self.highlighted_obj.resetState()

        self.highlighted_obj = obj
        if self.highlighted_obj:    self.highlighted_obj.setState(Object.OS_Highlighted)
    
    def _getMousePos(self, _state):
        """Returns mouse position based on mouse state
        @return: mouse position
        @rtype: tuple(int, int)
        """
        return (_state.X.abs, _state.Y.abs)
        
    def _onMouseMoved(self, _evt):
        """Mouse moved notification event
        """
        if BaseEditMode._onMouseMoved(self, _evt):  return True
        
        mstate = _evt.get_state()
        mpos = self._getMousePos(mstate)
        self.mouse_pos = (mstate.X.abs, mstate.Y.abs)
        
        if self.state is GraphEditMode.ES_Move:
            self.active_object.setPosition(render_engine.pos2dTo3dIsoPos(mpos))
            return True
        
        elif self.state is GraphEditMode.ES_LineCreate:
            self.__pointSpirit.setPosition(render_engine.pos2dTo3dIsoPos(mpos))
            self._updateLineSpirits()
            self._highlight()
            return True
        
        self._highlight()
        
        return False
        
    def _onMousePressed(self, _evt, _id):
        """Event on mouse button pressed
        """
        if BaseEditMode._onMousePressed(self, _evt, _id):   return True
        
        mstate = _evt.get_state()
        mpos = self._getMousePos(mstate)

        # getting objects under mouse
        mobjects = self._logic._getSheet()._getObjectsUnderMouse(True, True, self.mouse_pos)

        if _id == ois.MB_Right:
            # none any mode
            if self.state is GraphEditMode.ES_None:
                # creating point if there is no any objects under mouse
                if len(mobjects) is 0:
                    obj = self._logic.createVertex(mpos)
                    sheet = self._logic._getSheet()
                    sheet.addChild(obj)
                    return True
                else:
                    obj = comutils._getFirstObjectTypeFromList(mobjects, [GraphVertex])
                    if obj is not None:
                        self.state = GraphEditMode.ES_LineCreate
                        self.__lineSpirit.setBegin(obj)
                        sheet = self._logic._getSheet()
                        sheet.sceneNodeChilds.addChild(self.__lineSpirit.sceneNode)
                        sheet.sceneNodeChilds.addChild(self.__pointSpirit.sceneNode)
                        self.__lineBegin = obj
                        self.__pointSpirit.setPosition(render_engine.pos2dTo3dIsoPos(mpos))
                        self._updateLineSpirits()
                        return True
            # on line creation mode finishing line
            elif self.state is GraphEditMode.ES_LineCreate:
                obj = comutils._getFirstObjectTypeFromList(mobjects, [GraphVertex])
                sheet = self._logic._getSheet()
                if obj is not None:
                    # creating line
                    line = self._logic.createLink(self.__lineBegin, obj)
                    sheet.addChild(line)
                    
                # removing state
                self.state = GraphEditMode.ES_None
                sheet.sceneNodeChilds.removeChild(self.__lineSpirit.sceneNode)
                sheet.sceneNodeChilds.removeChild(self.__pointSpirit.sceneNode)
                self.__lineBegin = None
                    
            
        elif _id == ois.MB_Left:
            # if there is an any object under mouse, then starts moving
            if len(mobjects) > 0 and self.state is GraphEditMode.ES_None:
                self.active_object = comutils._getFirstObjectTypeFromList(mobjects, [GraphVertex])
                if self.active_object is not None:
                    self.state = GraphEditMode.ES_Move
                    self._selectObject(self.active_object)
                else:
                    # selecting first object under mouse
                    self.active_object = comutils._getFirstObjectTypeFromList(mobjects, [GraphLink])
                    self._selectObject(mobjects[0][1])
                
                
                return True
            
        return False
                 
            
    def _onMouseReleased(self, _evt, _id):
        """Event on mouse button released
        """
        if BaseEditMode._onMouseReleased(self, _evt, _id):  return True
        
        mstate = _evt.get_state()
        mpos = self._getMousePos(mstate)
        
        if _id == ois.MB_Left:
            
            # moving state finishing
            if self.state is GraphEditMode.ES_Move:
                self.state = GraphEditMode.ES_None
#                self._selectObject(self.active_object)
                #self.active_object = None                
        
        return False
    
    def _onKeyPressed(self, _evt):
        """Event on key pressed
        """
        if BaseEditMode._onKeyPressed(self, _evt):  return True
                
        return False
    
    def _onKeyReleased(self, _evt):
        """Event key released
        """
        if BaseEditMode._onKeyReleased(self, _evt): return True
        
        return False
    
        
    def _updateLineSpirits(self):
        """Updates spirit objects used in line creation mode
        """
        self.__pointSpirit.needUpdate = True
        self.__pointSpirit._update(0)
        self.__lineSpirit.needUpdate = True
        self.__lineSpirit._update(0)
        
    def _idtf_callback(self):
        """Callback for identificator changer
        """
        self.state = GraphEditMode.ES_None
        del self.idtf_changer
        
