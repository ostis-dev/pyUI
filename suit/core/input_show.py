
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
Created on 24.01.2012

@author: Denis Koronchik
'''
import render.mygui as mygui
import render.engine as render_engine
import ogre.io.OIS as ois
import objects
import math

# This file contain functions to show user input
guid = mygui.ResourceManager.getInstance().getResource("pic_EmulationSet").getResourceID()

class Icon(objects.ObjectOverlay):
    def __init__(self):
        objects.ObjectOverlay.__init__(self)
        self.autoSize = False
        
        self._anim_speed = 24.0
        self._linear_animations = {} # map of widgets and target alpha values
        self._pulse_animations = {}

    def __del__(self):
        objects.ObjectOverlay.__del__(self)
    
    def delete(self):
        objects.ObjectOverlay.delete(self)
        
        self._animations.clear()
    
    def _update(self, _timeSinceLastFrame):
        objects.ObjectOverlay._update(self, _timeSinceLastFrame)
        
        if len(self._linear_animations.keys()) > 0:        
            # update linear animations
            anims = []
            anims.extend(self._linear_animations.items())
            for _widget, _target in anims:
                alpha = _widget.getAlpha()
                da = math.copysign(self._anim_speed * _timeSinceLastFrame, _target - alpha)
                if da < 0:
                    da = da / 10.0
                new_alpha = alpha + da
                if da < 0:
                    alpha = max([_target, new_alpha])
                elif da > 0:
                    alpha = min([_target, new_alpha])
                    
                _widget.setAlpha(alpha)
                
                if alpha == _target:
                    self._linear_animations.pop(_widget)
                    
        if len(self._pulse_animations.keys()) > 0:        
            # update pulse animations
            anims = []
            anims.extend(self._pulse_animations.items())
            for _widget, _target in anims:
                alpha = _widget.getAlpha()
                da = math.copysign(self._anim_speed * _timeSinceLastFrame, _target - alpha)
                if da < 0:
                    da = da / 10.0
                new_alpha = alpha + da
                if da < 0:
                    alpha = max([_target, new_alpha])
                elif da > 0:
                    alpha = min([_target, new_alpha])
                    
                _widget.setAlpha(alpha)
                
                if alpha == _target and _target > 0.0:
                    self._pulse_animations[_widget] = 0.0
                
                if alpha == 0.0 and _target == 0.0:
                    self._pulse_animations.pop(_widget)
                
    def _addLinearAnimation(self, _widget, _target):
        """Append new animation. If \p _widget exists in animations, then
        it target will be changed
        """
        self._linear_animations[_widget] = _target
    
    def _addPulseAnimation(self, _widget, _target):
        """Append new animation. If \p _widget exists in animations, then
        it target will be changed
        """
        self._pulse_animations[_widget] = _target

class MouseIcon(Icon):
    """Class realize mouse animated icon
    """
    def __init__(self):
        Icon.__init__(self)
        
        self.wscale = 0.5
        
        self._widget = render_engine.Gui.createWidgetT("StaticImage", "StaticImage",
                                                       mygui.IntCoord(0, 0, 128, 128),
                                                       mygui.Align(),
                                                       "FadeBusy")
        self._widget.setVisible(False)
        self._widget.setNeedKeyFocus(False)
        self._widget.setNeedMouseFocus(False)
        
        self._widget.setItemResource(guid)
        self._widget.setItemGroup("Mouse")
        self._widget.setItemName("EmulationMouse")
        
        self._mouseMiddle = self._widget.createWidgetT("StaticImage", "StaticImage",
                                                      mygui.IntCoord(int(46 * self.wscale),
                                                                     int(20 * self.wscale),
                                                                     int(17 * self.wscale),
                                                                     int(30 * self.wscale)),
                                                      mygui.Align())
        self._mouseMiddle.setItemResource(guid)
        self._mouseMiddle.setItemGroup("MouseButton")
        self._mouseMiddle.setItemName("EmulationMouseButton")
        
        # left highlight
        self._mouseLeft = self._widget.createWidgetT("StaticImage", "StaticImage",
                                                     mygui.IntCoord(int(17 * self.wscale), 
                                                                    int(15 * self.wscale), 
                                                                    int(34 * self.wscale),
                                                                    int(61 * self.wscale)),
                                                     mygui.Align())
        self._mouseLeft.setItemResource(guid)
        self._mouseLeft.setItemGroup("MouseButton")
        self._mouseLeft.setItemName("EmulationMouseButton")
        
        # tight highlight
        self._mouseRight = self._widget.createWidgetT("StaticImage", "StaticImage",
                                                      mygui.IntCoord(int(55 * self.wscale),
                                                                     int(15 * self.wscale),
                                                                     int(34 * self.wscale),
                                                                     int(61 * self.wscale)),
                                                      mygui.Align())
        self._mouseRight.setItemResource(guid)
        self._mouseRight.setItemGroup("MouseButton")
        self._mouseRight.setItemName("EmulationMouseButton")
        

        self._mouseMiddleUp = self._widget.createWidgetT("StaticImage", "StaticImage",
                                                      mygui.IntCoord(int(39 * self.wscale),
                                                                     int(0 * self.wscale),
                                                                     int(30 * self.wscale),
                                                                     int(37 * self.wscale)),
                                                      mygui.Align())
        self._mouseMiddleUp.setItemResource(guid)
        self._mouseMiddleUp.setItemGroup("MouseMiddleUp")
        self._mouseMiddleUp.setItemName("EmulationMouseMiddleUp")
        
        self._mouseMiddleDown = self._widget.createWidgetT("StaticImage", "StaticImage",
                                                      mygui.IntCoord(int(39 * self.wscale),
                                                                     int(30 * self.wscale),
                                                                     int(30 * self.wscale),
                                                                     int(37 * self.wscale)),
                                                      mygui.Align())
        self._mouseMiddleDown.setItemResource(guid)
        self._mouseMiddleDown.setItemGroup("MouseMiddleDown")
        self._mouseMiddleDown.setItemName("EmulationMouseMiddleDown")
        
        self._mouseLeft.setAlpha(0.0)
        self._mouseMiddle.setAlpha(0.0)
        self._mouseMiddleDown.setAlpha(0.0)
        self._mouseMiddleUp.setAlpha(0.0)
        self._mouseRight.setAlpha(0.0)
        
        
        self.setScale((int(128 * self.wscale), int(128 * self.wscale)))
    
    def __del__(self):
        Icon.__del__(self)
    
    def delete(self):
        Icon.delete(self)
    
    def _update(self, _timeSinceLastFrame):
        Icon._update(self, _timeSinceLastFrame)
        
    def mouseMoved(self, _evt):
        """Mouse moved notification
        """
        state = _evt.get_state()
              
        if state.Z.rel > 0:
            self._addPulseAnimation(self._mouseMiddleUp, 1.0)
            
        if state.Z.rel < 0:
            self._addPulseAnimation(self._mouseMiddleDown, 1.0)
        
        return False 
        
    def mousePressed(self, _evt, _id):
        """Mouse button pressed notification
        """
        _widget = None
        
        if _id == ois.MB_Left:
            _widget = self._mouseLeft
        elif _id == ois.MB_Right:
            _widget = self._mouseRight
        elif _id == ois.MB_Middle:
            _widget = self._mouseMiddle
        
        if _widget is not None:
            self._addLinearAnimation(_widget, 1.0)
        
        return False
    
    def mouseReleased(self, _evt, _id):
        """Mouse button released notification
        """
        _widget = None
        
        if _id == ois.MB_Left:
            _widget = self._mouseLeft
        elif _id == ois.MB_Right:
            _widget = self._mouseRight
        elif _id == ois.MB_Middle:
            _widget = self._mouseMiddle
        
        if _widget is not None:
            self._addLinearAnimation(_widget, 0.0)
        
        return False

class KeyIcon(Icon):
    
    sz = 64
    
    def __init__(self):
        Icon.__init__(self)
                
        self._widget = render_engine.Gui.createWidgetT("StaticImage", "KeyIcon",
                                                       mygui.IntCoord(0, 0, self.sz, self.sz),
                                                       mygui.Align(),
                                                       "FadeBusy")
        self._widget.setVisible(False)
        self._widget.setNeedKeyFocus(False)
        self._widget.setNeedMouseFocus(False)
        self._widget.setAlpha(0.0)
        
        self._widget.setItemResource(guid)
        self._widget.setItemGroup("Key")
        self._widget.setItemName("EmulationKey")
                
        self.setScale((self.sz, self.sz))
        self.autoSize = False
        
    def __del__(self):
        Icon.__del__(self)
        
    def reset(self):
        self._widget.setAlpha(0.0)
        
    def _updateTextValue(self):
        """Recalculate widget size
        """
        Icon._updateTextValue(self)
    
        width = self.sz
        if len(self.textValue) > 5:
            width = 110
        elif len(self.textValue) > 3:
            width = 96
    
        self.setScale((width, self.sz))
        
    def keyPressed(self, _evt):
        """Key pressed event
        """
        self._addLinearAnimation(self._widget, 1.0)
        self.setText(unicode(render_engine._oisKeyboard.getAsString(_evt.key)))        
        return False
    
    def keyReleased(self, _evt):
        """Key released event
        """
        self._addLinearAnimation(self._widget, 0.0)
        return False

class InputShow:
    """Class that realize input show logic.
    It controls all icons
    """
    def __init__(self):
        self.is_enabled = False
        self.mouse_icon = MouseIcon()
        self.mouse_offset = 32
        
        self.key_icons = []
        self.key_stack_max_size = 5
        self.key_pressed = {}
        
        for x in xrange(self.key_stack_max_size):
            icon = KeyIcon()
            icon.setEnabled(True)
            icon.setVisible(True)
            self.key_icons.append(icon)
        
        self.mouse_icon.setEnabled(True)
        
        self._updateOnMouseState(render_engine._oisMouse.getMouseState())

    def enable(self):
        """Enable input showing
        """
        self.mouse_icon.setVisible(True)
        for key in self.key_icons:
            key.setVisible(True)
        
        self.is_enabled = True
    
    def disable(self):
        """Disable input showing
        """
        self.mouse_icon.setVisible(False)
        for key in self.key_icons:
            key.setVisible(False)
        
        self.is_enabled = False
        
    def toggle(self):
        """Switch between enabled and disabled states
        """
        if self.is_enabled:
            self.disable()
        else:
            self.enable()
            
    def _updateOnMouseState(self, state):
        """Updates input icons relative to mouse state
        """
        x = state.X.abs
        y = state.Y.abs
        
        mscale = self.mouse_icon.getScale()    
        
        if (x + mscale[0] + self.mouse_offset) > render_engine.Window.width:
            x = x - mscale[0] - 10
        else:
            x += self.mouse_offset
            
        if (y + mscale[1] + self.mouse_offset) > render_engine.Window.height:
            y = y - mscale[1] - 10
        else:
            y += self.mouse_offset
            
        self.mouse_icon.setPosition((x, y))
        
    def _updateKeyboardStack(self):
        
        # calculate stack icons position
        if len(self.key_pressed.keys()) > 0:
            y = render_engine.Window.height
            for idx in xrange(len(self.key_pressed)):
                y -= self.key_icons[idx].getScale()[1] - 5
                self.key_icons[idx].setPosition((5, y))
                    
    def mouseMoved(self, _evt):
        """Mouse moved notification
        """
        if not self.is_enabled: return False

        self._updateOnMouseState(_evt.get_state())
        self.mouse_icon.mouseMoved(_evt)
        return False 
    
    def mousePressed(self, _evt, _id):
        """Mouse button pressed notification
        """
        if not self.is_enabled: return False
        
        self.mouse_icon.mousePressed(_evt, _id)
        return False
    
    def mouseReleased(self, _evt, _id):
        """Mouse button released notification
        """
        if not self.is_enabled: return False
        
        self.mouse_icon.mouseReleased(_evt, _id)
        return False
    
    def keyPressed(self, _evt):
        """Key pressed event
        """
        if not self.is_enabled: return False
        
        idx = len(self.key_pressed)
        assert idx <= self.key_stack_max_size
        
        if idx < self.key_stack_max_size:
            icon = self.key_icons[idx]
            
            icon.reset()
            icon.keyPressed(_evt)
            
            if not _evt.key in self.key_pressed:
                self.key_pressed[_evt.key] = icon
        else:
            pass
                
        self._updateKeyboardStack()
                
        return False
    
    def keyReleased(self, _evt):
        """Key released event
        """
        if not self.is_enabled: return False
        
        if self.key_pressed.has_key(_evt.key):
            icon = self.key_pressed[_evt.key]
            self.key_pressed.pop(_evt.key)
            icon.keyReleased(_evt)

        self._updateKeyboardStack()
        return False