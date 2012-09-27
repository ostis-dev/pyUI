
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
Created on 11.12.2009

@author: Denis Koronchik
'''
from suit.cf import BaseViewMode
from suit.cf import BaseEditMode
from suit.cf import IdtfChanger
from suit.cf.flymode import FlyMode
from suit.cf.VisualMenu import VisualMenu
from suit.cf.VisualMenu import VisualMenuItem
import suit.cf.utils as comutils

import suit.core.render.engine as render_engine
import ogre.renderer.OGRE as ogre
import ogre.io.OIS as ois
import suit.core.objects as objects
import suit.core.render.mygui

import space_objects
import space_panel
import space_window


# mode show widget
_show_mode_window = None
_show_mode_text = None

def initialize():
    """Initialize mode show widget
    """
    global _show_mode_window
    global _show_mode_text
    _show_mode_window = render_engine.Gui.createWidgetT("Window", "Panel", 
                                                 mygui.IntCoord(0, 0, 0, 0), mygui.Align(),
                                                 "Popup", "")
    _show_mode_text = _show_mode_window.createWidgetT("StaticText", "StaticText",
                                               mygui.IntCoord(7, 7, 0, 0), mygui.Align())

def shutdown():
    """Shutting down mode show widget
    """
    global _show_mode_window
    global _show_mode_text
    render_engine.Gui.destroyWidget(_show_mode_window)
    _show_mode_window = None
    _show_mode_text = None

def _switchMode(_mode):
    """Shows mode description and change environment depend on mode
    """
    global _show_mode_text
    _show_mode_text.setCaption("#FF6633" + unicode(_mode.name))
    size = _show_mode_text.getTextSize()
    _show_mode_window.setSize(size.width + 14, size.height + 14)
    _show_mode_window.setPosition(render_engine.Window.width - size.width - 19,
                                  render_engine.Window.height - size.height - 19)
    _show_mode_text.setSize(size.width, size.height)
    
def hideMode():
    """Makes mode shower invisible
    """
    _show_mode_window.setVisible(False)
    
def showMode():
    """Makes mode shower visible
    """
    _show_mode_window.setVisible(True)

class SpaceViewMode(FlyMode, BaseEditMode):
    """Mode that allows user to view and navigate in scg window
    """
    def __init__(self, _logic):
        FlyMode.__init__(self, _logic)
        # highlighted object
        self._shift = False
        self._ctrl = False
        self.highlighted_obj = None
        
        # widgets
        self.type_combo = None
        self.content_combo = None
        
        # object we worked on in current state
        self.object_active = None
        
        # current mouse position
        self.mouse_pos = (0, 0)
        
#        # object we worked on in previous state
#        self.object_prev = none
        
        # visual menu
        self.vis_menu = None
        self._createVisualMenu()
        
    def __del__(self):
        FlyMode.__del__(self)
        
    def delete(self):
        """Deletion message
        """
        self.vis_menu.delete()
        self.object_active = None
        
        
    def activate(self):
        """Activation message
        """
        FlyMode.activate(self)
        self._updateVisualMenu()
        
    def deactivate(self):
        """Deactivation message
        """
        FlyMode.deactivate(self)
        self._updateVisualMenu()
        
    def _update(self, timeSinceLastFrame):
        """Updates mode
        """
        if FlyMode.isActive(self):
            FlyMode._update(self,timeSinceLastFrame);
#       if self.vis_menu.isShow():
        sel_objects = self._logic._getSheet().getSelected()
        n = len(sel_objects)
        if n == 1:
            obj = sel_objects[0]
            self.vis_menu.move(render_engine.pos3dTo2dWindow(sel_objects[0].getPosition()))
        self.vis_menu._update(timeSinceLastFrame)
        
    def _highlight(self):
        """Highlighting object under mouse
        """
        mobjects = []
        objects_tuple = self._logic._getSheet()._getObjectsUnderMouse(True, True, self.mouse_pos)
    
        if len(objects_tuple) is not 0:
            parent_tuple = objects_tuple[0]
            mobjects.append(parent_tuple)
            childs = parent_tuple[1]._getObjectsUnderMouse(True, True, self.mouse_pos);
            mobjects = mobjects + childs
            mobjects.sort()
            mobjects.reverse()
            
        if len(mobjects) > 0:
            obj = mobjects[0][1]
        else:
            return
        
        if (obj is None) and (self.highlighted_obj is None):    return
        if (obj is self.highlighted_obj):   return
        
        # change highlight
        if self.highlighted_obj:
            if self.highlighted_obj._getSelected():
                self.highlighted_obj.setState(objects.Object.OS_Selected)
            else:
                self.highlighted_obj.setState(objects.Object.OS_Normal)
        self.highlighted_obj = obj
        if self.highlighted_obj:    
            self.highlighted_obj.setState(objects.Object.OS_Highlighted)
            
        
    def _onMouseMoved(self, _evt):
        """Mouse moved event
        """
        mstate = _evt.get_state()
        prev_pos = self.mouse_pos
        self.mouse_pos = (mstate.X.abs, mstate.Y.abs)
        
        self._highlight()
        return False
    
    def _onMousePressed(self, _evt, _id):
        """Mouse button pressed event
        """
        if _id == ois.MB_Left:
            mstate = _evt.get_state()
            mpos = (mstate.X.abs, mstate.Y.abs)
            # getting objects under mouse
            mobjects = []
            objects_tuple = self._logic._getSheet()._getObjectsUnderMouse(True, True, mpos)
            
            if len(objects_tuple) is not 0:
                parent_tuple = objects_tuple[0]
                mobjects.append(parent_tuple)
                childs = parent_tuple[1]._getObjectsUnderMouse(True, True, mpos);
                mobjects = mobjects + childs
                mobjects.sort();
                mobjects.reverse();
                
            if len(mobjects) is not 0 and self.object_active != mobjects[0][1]:
                if self.object_active is not None:
                    self.object_active.sceneNode2.showBoundingBox(False)
                    space_window.deactivate()          
                self.object_active = mobjects[0][1]
                if self.object_active is not None:
                    self._selectObject(self.object_active)
                    self.object_active.sceneNode2.showBoundingBox(True)
                    space_window.activate(self.object_active)
                    return True
            if self._logic._getSheet().haveSelected():
                # removing selection from all nodes
                self._logic._getSheet().unselectAll()
                self.object_active.sceneNode2.showBoundingBox(False)
                self.object_active = None
                space_window.deactivate()
                return True   
        return False  
    
    def _createVisualMenu(self):
        """Creates visual menu
        """
        self.vis_menu = VisualMenu()
       

    def _updateVisualMenu(self):
        """Updates visual menu depending on selection
        """
        if self._logic is None or self._logic._getSheet() is None:
            return
        
        import types
        sel_objects = [] + self._logic._getSheet().getSelected()
        
        if self.vis_menu.isShow():
            self.vis_menu.hide()
        
        if not self.active: return
        
        n = len(sel_objects)
        if n > 0:   self.vis_menu.show(render_engine.pos3dTo2dWindow(sel_objects[0].getPosition()))

    def processInput(self):
        # processing mouse input
        ms = render_engine._oisMouse.getMouseState()
        if  ms.buttonDown(ois._ois_.MB_Right):
            self.rotX = ogre.Degree(-ms.X.rel * 0.13)
            self.rotY = ogre.Degree(-ms.Y.rel * 0.13)
        
        # processing keyboard input
        if  render_engine._oisKeyboard.isKeyDown(ois.KC_A):
            self.move.x = -self.moveScale    # Move camera left

        if  render_engine._oisKeyboard.isKeyDown(ois.KC_D):
            self.move.x = self.moveScale    # Move camera RIGHT

        if  render_engine._oisKeyboard.isKeyDown(ois.KC_W):
            self.move.z = -self.moveScale  # Move camera forward

        if  render_engine._oisKeyboard.isKeyDown(ois.KC_S):
            self.move.z = self.moveScale    # Move camera backward
            
        if  render_engine._oisKeyboard.isKeyDown(ois.KC_Q):
            self.move.y = self.moveScale  # Move camera up

        if  render_engine._oisKeyboard.isKeyDown(ois.KC_E):
            self.move.y = -self.moveScale    # Move camera down
    