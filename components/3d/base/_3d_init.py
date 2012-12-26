
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
from suit import core

import os
import _3d_env
import _3d_viewer
import _3d2sc


_version_   =   "0.2.0"
_name_      =   "3D-Viewver-interface"

def initialize():

    import suit.core.kernel as core
    import suit.core.keynodes as keyn
    from suit.core.objects import Factory

    global view_factory
    global edit_factory
    global trans_geom2sc_factory
    
    # register viewers and editors
    kernel = core.Kernel.getSingleton()
    # registering components
    view_factory = Factory(viewer_creator)
    trans_geom2sc_factory = Factory(transGeom2Sc_creator)
    kernel.registerViewerFactory(view_factory, [keyn.ui.format_3d])
    kernel.registerTranslatorFactory(trans_geom2sc_factory, [keyn.ui.format_3d], [keyn.ui.format_sc])


def shutdown():
    import suit.core.kernel as core    
    kernel = core.Kernel.getSingleton()
    
    global view_factory
    global edit_factory
    global trans_geom2sc_factory
    
    #TODO:    make language unloading
    
    # unregister components
    kernel.unregisterViewerFactory(view_factory)
    kernel.unregisterTranslatorFactory(trans_geom2sc_factory)
    

def _resourceLocations():
    """Specified resources for a geometry module
    """
    import suit.core.kernel as core

    res = []
    for directory in os.listdir ( _3d_env.res_scene_location ):
        fullPath = os.path.join (  _3d_env.res_scene_location, directory )
        if os.path.isdir( fullPath ):
            res.append((fullPath, "FileSystem", getResourceGroup()))

    return res

def getResourceGroup():
    """Return resource group name
    """
    return _3d_env.resource_group

def viewer_creator():
    return _3d_viewer._3DViewer()


def transGeom2Sc_creator():
    return _3d2sc.Translator3D2Sc()