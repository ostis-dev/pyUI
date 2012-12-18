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
Created on 15.01.2011

@author: Denis Koronchik
'''
from suit.core.kernel import Kernel
import ogre.io.OIS as ois
import suit.core.render.engine as render_engine
import suit.core.objects as objects
import math

class BaseCommand:
    
    def __init__(self):
        self.speed = 1.0    # command apply speed
        
        self.eventFinished = None
    
    def delete(self):
        Kernel.getSingleton().removeUpdateListener(self)
    
    def _update(self, timeSinceLastFrame):
        pass
    
    def start(self):
        Kernel.getSingleton().addUpdateListener(self)
        
    def finish(self):
        self.eventFinished(self)
    
class MouseMove(BaseCommand):
    
    def __init__(self, init_pos, target_object):
        """Constructor
        
        @param init_pos:    initial mouse position
        @type init_pos:    (int, int)
        
        @param target_object:    target mouse object
        @type target_object:    suit.core.objects.Object
        """
        BaseCommand.__init__(self)
        
        state = render_engine._oisMouse.getMouseState()
        
        self.init_pos = init_pos
        self.current_pos =  (state.X.abs, state.Y.abs)
        self.speed = 200
        self.object = target_object
        self.init_pause = 0.5
        self.pause = self.init_pause
        self.paused = False
        
       
    def _update(self, timeSinceLastFrame):
        BaseCommand._update(self, timeSinceLastFrame)
        
        if self.object is None:
            self.finish()
            return
        
        if self.paused and self.pause <= 0:
            self.finish()
            return
        else:
            self.pause -= timeSinceLastFrame
        
        target_pos = None
        if isinstance(self.object, objects.ObjectDepth):
            target_pos = render_engine.pos3dTo2dWindow(self.object.getPosition())
        else:
            target_pos = self.object.getCenter()
        
        dist = self.speed * timeSinceLastFrame
        rem_dist = self.distance(self.current_pos, target_pos)
               
        if dist >= rem_dist:    # end moving
            self.setMousePosition(target_pos)
            self.paused = True
            return
        else:
            self.pause = self.init_pause
        
        dx = target_pos[0] - self.current_pos[0]
        dy = target_pos[1] - self.current_pos[1]
        d = self.distance((0, 0), (dx, dy))
        new_pos = (self.current_pos[0] + dx / d * dist,
                   self.current_pos[1] + dy / d * dist)
                
        self.setMousePosition(new_pos)
        self.current_pos = new_pos
        
        
    def distance(self, p1, p2):
        """Calculate distance between points
        @param p1:    fisrt point
        @type p1: (int, int)
        
        @param p2: second point 
        @type p2: (int, int)  
        """
        return math.sqrt(math.pow(p1[0] - p2[0], 2) + math.pow(p1[1] - p2[1], 2))
    
    def getMousePosition(self):
        return (0, 0)
    
    def setMousePosition(self, pos):
        """Sets new mouse position
        
        @param pos:    new mouse position
        @type pos:    (int, int)
        """
        
        state = render_engine._oisMouse.getMouseState()
        
        # create Axes
        state.X.abs = int(pos[0])
        state.X.rel = int(pos[0] - self.current_pos[0])
        
        state.Y.abs = int(pos[1])
        state.Y.rel = int(pos[1] - self.current_pos[1])
        
        render_engine._inputListener.mouseMoved(ois.MouseEvent(render_engine._oisMouse, state))

class MouseMoveTo(BaseCommand) :

    def __init__(self, init_pos):
        """Constructor

        @param init_pos:    initial mouse position
        @type init_pos:    (int, int)
        """
        BaseCommand.__init__(self)

        state = render_engine._oisMouse.getMouseState()

        self.init_pos = init_pos
        self.current_pos =  (state.X.abs, state.Y.abs)
        self.speed = 200
        self.init_pause = 0.5
        self.pause = self.init_pause
        self.paused = False

    def _update(self, timeSinceLastFrame):
        BaseCommand._update(self, timeSinceLastFrame)

        if self.paused and self.pause <= 0:
            self.finish()
            return
        else:
            self.pause -= timeSinceLastFrame

        dist = self.speed * timeSinceLastFrame

        rem_dist = self.distance(self.current_pos, self.init_pos)

        if dist >= rem_dist:    # end moving
            self.setMousePosition(self.init_pos)
            self.paused = True
            return
        else:
            self.pause = self.init_pause

        dx = self.init_pos[0] - self.current_pos[0]
        dy = self.init_pos[1] - self.current_pos[1]
        d = self.distance((0, 0), (dx, dy))
        new_pos = (self.current_pos[0] + dx / d * dist,
                   self.current_pos[1] + dy / d * dist)

        self.setMousePosition(new_pos)

        self.current_pos = new_pos


    def distance(self, p1, p2):
        """Calculate distance between points
        @param p1:    fisrt point
        @type p1: (int, int)

        @param p2: second point
        @type p2: (int, int)
        """
        return math.sqrt(math.pow(p1[0] - p2[0], 2) + math.pow(p1[1] - p2[1], 2))

    def setMousePosition(self, pos):
        """Sets new mouse position

        @param pos:    new mouse position
        @type pos:    (int, int)
        """

        state = render_engine._oisMouse.getMouseState()

        # create Axes
        state.X.abs = int(pos[0])
        state.X.rel = int(pos[0] - self.current_pos[0])

        state.Y.abs = int(pos[1])
        state.Y.rel = int(pos[1] - self.current_pos[1])

        render_engine._inputListener.mouseMoved(ois.MouseEvent(render_engine._oisMouse, state))
        
class MouseButton(BaseCommand):
    
    def __init__(self, _button_id, _time, _pressed):
        """Constructor
        
        @param _button_id:    pressed button id
        @type _button_id:    ois.KeyCode
        
        @param _time: press button time
        @type _time: int
        
        @param _pressed: button pressed flag. If it's True, then need to emulate button press, else - button release.
        @type _pressed: bool
        """
        BaseCommand.__init__(self)
        
        self.button_id = _button_id
        self.press_time = _time
        self.pressed = _pressed
        self.is_pressed = render_engine._oisMouse.getMouseState().buttonDown(self.button_id)
        self.paused = False
        self.pause = 0.5
           
    def _update(self, timeSinceLastFrame):
        BaseCommand._update(self, timeSinceLastFrame)
        
        if self.paused:
            if self.pause <= 0:
                self.finish()
                return
            else:
                self.pause -= timeSinceLastFrame
        
        if self.is_pressed or self.press_time <= 0:  
            state = render_engine._oisMouse.getMouseState()
            if self.pressed and not state.buttonDown(self.button_id):
                state.buttons += (1 << self.button_id)
                render_engine._inputListener.mousePressed(ois.MouseEvent(render_engine._oisMouse, state),
                                                  self.button_id)
            elif not self.pressed and state.buttonDown(self.button_id):
                state.buttons = state.buttons & (~(1 << self.button_id))
                render_engine._inputListener.mouseReleased(ois.MouseEvent(render_engine._oisMouse, state),
                                                  self.button_id)
                  
            self.paused = True
            
        self.press_time -= timeSinceLastFrame

class KeyboardButton(BaseCommand):

    def __init__(self, _button_id, _time, _pressed):
        """Constructor

        @param _button_id:    pressed button id
        @type _button_id:    ois.KeyCode

        @param _time: press button time
        @type _time: int

        @param _pressed: button pressed flag. If it's True, then need to emulate button press, else - button release.
        @type _pressed: bool
        """
        BaseCommand.__init__(self)

        self.button_id = _button_id
        self.press_time = _time
        self.pressed = _pressed
        self.paused = False
        self.pause = 0.5

    def _update(self, timeSinceLastFrame):
        BaseCommand._update(self, timeSinceLastFrame)

        if self.paused:
            if self.pause <= 0:
                self.finish()
            else:
                self.pause -= timeSinceLastFrame


        if self.press_time <= 0 and not self.paused:
            if self.pressed :
                render_engine._inputListener.keyPressed(ois.KeyEvent(render_engine._oisKeyboard, self.button_id, True))
            elif not self.pressed :
                render_engine._inputListener.keyReleased(ois.KeyEvent(render_engine._oisKeyboard, self.button_id, True))

            self.paused = True

        self.press_time -= timeSinceLastFrame
