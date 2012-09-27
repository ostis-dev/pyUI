
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
Created on 03.12.2009

@author: Denis Koronchik
'''
import suit.core.kernel as core
import scg_alphabet
import scg_help
import scg_modes
import scg_viewer, scg_editor
import scg2sc, sc2scg
import os
import scg_environment as env

resourceGroupManager = None

_version_   =   "0.2.0"
_name_      =   "SCg-interface"

def initialize():
    
    # initialize resources
    scg_alphabet.initialize_code()
    scg_help.initialize()
    scg_modes.initialize()
    
    # register viewers
    kernel = core.Kernel.getSingleton()
    
    import suit.core.keynodes as keyn
    from suit.core.objects import Factory
    
    global view_factory
    global edit_factory
    global transcg2sc_factory
    global transc2scg_factory
    
    # registering components
    view_factory = Factory(viewer_creator)
    edit_factory = Factory(editor_creator)
    transcg2sc_factory = Factory(scg2sc_creator)
    transc2scg_factory = Factory(sc2scg_creator)
    
    kernel.registerViewerFactory(view_factory, [keyn.ui.format_scgx])
    kernel.registerEditorFactory(edit_factory, [keyn.ui.format_scgx])
    kernel.registerTranslatorFactory(transcg2sc_factory, [keyn.ui.format_scgx], [keyn.ui.format_sc])
    kernel.registerTranslatorFactory(transc2scg_factory, [keyn.ui.format_sc], [keyn.ui.format_scgx])
    
#    MyGUI::ResourceManager::getInstance().load("Resources.xml");

    # loading resources for visual menu
    import suit.core.render.mygui as mygui
    mygui.ResourceManager.getInstance().load(env.vis_menu_resources)
    
    
def shutdown():
    scg_modes.shutdown()
    scg_help.shutdown()
    
    global view_factory
    global edit_factory
    global transcg2sc_factory
    global transc2scg_factory
    # unregister components
    kernel = core.Kernel.getSingleton()
    
    kernel.unregisterViewerFactory(view_factory)
    kernel.unregisterEditorFactory(edit_factory)
    kernel.unregisterTranslatorFactory(transcg2sc_factory)
    kernel.unregisterTranslatorFactory(transc2scg_factory)
    
def _resourceLocations():
    """Returns list of resource locations
    
    @return: list of tuples that represents resource storage type, location and group (storage_type, location, group)
    @rtype: list 
    """
    res = []
    for _path in env.resource_dirs:
        res.append( (_path, "FileSystem", env.resource_group) )
        
    res.append( (env.res_vismenu_dir, "FileSystem", "General") )
        
    return res 

def viewer_creator():
    return scg_viewer.SCgViewer()

def editor_creator():
    return scg_editor.SCgEditor()

def scg2sc_creator():
    return scg2sc.TranslatorSCg2Sc()

def sc2scg_creator():
    return sc2scg.TranslatorSc2Scg()