
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
Created on 17.12.2009

@author: Denis Koronchick
'''
import os
import geom_env
import geom_viewer
import geom_editor
import geom2sc


_version_   =   "0.2.0"
_name_      =   "Geometry-interface"

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
    edit_factory = Factory(editor_creator)
    trans_geom2sc_factory = Factory(transGeom2Sc_creator)
    kernel.registerViewerFactory(view_factory, [keyn.ui.format_geomx])
    kernel.registerEditorFactory(edit_factory, [keyn.ui.format_geomx])
    kernel.registerTranslatorFactory(trans_geom2sc_factory, [keyn.ui.format_geomx], [keyn.ui.format_sc])


def shutdown():
    import suit.core.kernel as core    
    kernel = core.Kernel.getSingleton()
    
    global view_factory
    global edit_factory
    global trans_geom2sc_factory
    
    #TODO:    make language unloading
    
    # unregister components
    kernel.unregisterViewerFactory(view_factory)
    kernel.unregisterEditorFactory(edit_factory)
    kernel.unregisterTranslatorFactory(trans_geom2sc_factory)
    

def _resourceLocations():
    """Specified resources for a geometry module
    """
    res = []
    for path in geom_env.resource_dirs:
        res.append((path, "FileSystem", getResourceGroup()))
        
    import srs_engine.environment
    res.append((geom_env.res_gui_dir, "FileSystem", srs_engine.environment.GUI_resource_group))
        
    return res

def getResourceLocation():
    """Return resource location folder
    """
    return os.path.join(core.Kernel.getResourceLocation(), geom_env.resource_dir) 

def getResourceGroup():
    """Return resource group name
    """
    return geom_env.resource_group

def viewer_creator():
    return geom_viewer.GeometryViewer()

def editor_creator():
    return geom_editor.GeometryEditor()

def transGeom2Sc_creator():
    return geom2sc.TranslatorGeom2Sc()