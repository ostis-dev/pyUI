
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
Created on 20.01.2010

@author: Maxim Kaskevich
'''

import suit.core.kernel as core
import os
import space_viewer
import space_editor
import sc2space
import space2sc
import space_panel
import space_window
import space_env

def initialize():
    
    kernel = core.Kernel.getSingleton()
    
    from suit.core.objects import Factory
    import suit.core.keynodes as keynodes
    
    global view_factory
    global edit_factory
    global transc2space_factory
    global transpace2sc_factory
    
    view_factory = Factory(viewer_creator)
    edit_factory = Factory(viewer_creator)
    transc2space_factory = Factory(sc2space_creator)
    transpace2sc_factory = Factory(space2sc_creator)
    
    kernel.registerViewerFactory(view_factory, [keynodes.ui.format_space])
    kernel.registerEditorFactory(edit_factory, [keynodes.ui.format_space])
    kernel.registerTranslatorFactory(transc2space_factory, [keynodes.ui.format_sc], [keynodes.ui.format_space])
    kernel.registerTranslatorFactory(transpace2sc_factory, [keynodes.ui.format_space], [keynodes.ui.format_sc])
    
#    space_panel.initialize()
    space_window.initialize()

def shutdown():
    global view_factory
    global edit_factory
    global transc2space_factory
    global transpace2sc_factory
    
    kernel = core.Kernel.getSingleton()
    kernel.unregisterViewerFactory(view_factory)
    kernel.unregisterEditorFactory(edit_factory)
    kernel.unregisterTranslatorFactory(transc2space_factory)
    kernel.unregisterTranslatorFactory(transpace2sc_factory)
    
#    space_panel.shutdown()
    space_window.shutdown()    

def _resourceLocations():
    """Specified resources for a geometry module
    """
    res = []
    for path in space_env.resource_dirs:
        res.append((path, "FileSystem", getResourceGroup()))
        
    import suit.core.environment
    res.append((space_env.res_gui_dir, "FileSystem", suit.core.environment.GUI_resource_group))
    
    return res

def getResourceLocation():
    """Return resource location folder
    """
    return os.path.join(core.Kernel.getResourceLocation(), space_env.resource_dir) 

def getResourceGroup():
    """Return resource group name
    """
    return space_env.resource_group

def viewer_creator():
    return space_viewer.SpaceViewer()

def editor_creator():
    return space_editor.SpaceEditor() 

def sc2space_creator():
    return sc2space.TranslatorSc2Space()

def space2sc_creator():
    return space2sc.TranslatorSpace2Sc();