
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

from suit.cf import BaseEditMode
from suit.cf.flymode import FlyMode
from suit.cf.VisualMenu import VisualMenu


import suit.core.render.engine as render_engine
import ogre.renderer.OGRE as ogre
import ogre.io.OIS as ois


class _3DViewMode(FlyMode, BaseEditMode):
    """Mode that allows user to view and navigate in scg window
    """
    def __init__(self, _logic):
        FlyMode.__init__(self, _logic)
        # highlighted object
        self.main3dObject = None
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
        self.moveSpeed = 60

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
            FlyMode._update(self,timeSinceLastFrame)

    def _onMouseMoved(self, _evt):
        """Mouse moved event
        """
        if FlyMode.isActive(self):
            FlyMode._onMouseMoved(self, _evt)
        return False

    def _onMousePressed(self, _evt, _id):
        """Mouse button pressed event
        """
        if FlyMode.isActive(self):
            FlyMode._onMousePressed(self, _evt, _id)
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
    