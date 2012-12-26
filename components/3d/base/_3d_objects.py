
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
import os

import suit.core.objects as objects
import suit.core.render.engine as render_engine
import _3d_dotscene as scene
import _3d_env as env

# material postfix
state_post = {objects.Object.OS_Normal: '_Normal',
              objects.Object.OS_Selected: '_Selected',
              objects.Object.OS_Highlighted: '_Highlighted',
              objects.Object.OS_WasInMemory: '_Normal',
              objects.Object.OS_NewInMemory: '_Normal',
              objects.Object.OS_Merged: '_Normal'}

class _3DObject(objects.ObjectDepth):
    def __init__(self, name = "roadster"):
        """constructor
        """
        objects.ObjectDepth.__init__(self)
        # creating entity
        path = os.path.abspath(os.path.join(env.res_scene_location, name, name + '.scene'))
        self.__scene = scene.DotScene(path, render_engine.SceneManager, self.sceneNode)


    def __del__(self):
        objects.ObjectDepth.__del__(self)
        self.__scene.__del__()

    def get_idtf(self):
        """Returns object identificator.
        It parse structures like: Point(A), Point A, pA and return A
        """
        #FIXME:    add parsing for Point(A), Point A and etc. structures
        idtf = self.getText()
        if idtf is None or len(idtf) == 0:
            idtf = str(self)[-9:-2] # FIXME:    make identification more useful

        return idtf
