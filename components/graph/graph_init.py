
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

Modified on 8.04.2010
by Maxim Kaskevich
'''
import os
import graph_viewer
import graph_editor
import graph_env
import graph2sc
import sc2graph
import graph_operations


trans_graph2sc_factory = None
trans_sc2graph_factory = None

def initialize():
        
    import suit.core.kernel as core
    import suit.core.keynodes as keyn
    from suit.core.objects import Factory

    global view_factory
    global edit_factory
    global trans_graph2sc_factory
    global trans_sc2graph_factory
    
    # register viewers and editors
    kernel = core.Kernel.getSingleton()
    # registering components
    view_factory = Factory(viewer_creator)
    edit_factory = Factory(editor_creator)
    trans_graph2sc_factory = Factory(transGraph2Sc_creator)
    trans_sc2graph_factory = Factory(transSc2Graph_creator)

    kernel.registerViewerFactory(view_factory, [keyn.ui.format_graph])
    kernel.registerEditorFactory(edit_factory, [keyn.ui.format_graph])
    kernel.registerTranslatorFactory(trans_graph2sc_factory, [keyn.ui.format_graph], [keyn.ui.format_sc])
    kernel.registerTranslatorFactory(trans_sc2graph_factory, [keyn.ui.format_sc], [keyn.ui.format_graph])

    graph_operations.initialize()
    
def shutdown():
    import suit.core.kernel as core    
    kernel = core.Kernel.getSingleton()
    
    global view_factory
    global edit_factory
    global trans_graph2sc_factory
    global trans_sc2graph_factory
    
    #TODO:    make language unloading
    
    # unregister components
    kernel.unregisterViewerFactory(view_factory)
    kernel.unregisterEditorFactory(edit_factory)
    kernel.unregisterTranslatorFactory(trans_graph2sc_factory)
    kernel.unregisterTranslatorFactory(trans_sc2graph_factory)

    graph_operations.shutdown()
  


def _resourceLocations():
    """Specified resources for a graph module
    """
    res = []
    for path in graph_env.resource_dirs:
        res.append((path, "FileSystem", getResourceGroup()))
        
    return res

def getResourceLocation():
    """Return resource location folder
    """
    return os.path.join(core.Kernel.getResourceLocation(), graph_env.resource_dir) 

def getResourceGroup():
    """Return resource group name
    """
    return graph_env.resource_group

def viewer_creator():
    return graph_viewer.GraphViewer()

def editor_creator():
    return graph_editor.GraphEditor()

def transGraph2Sc_creator():
    return graph2sc.TranslatorGraph2Sc()

def transSc2Graph_creator():
    return sc2graph.TranslatorSc2Graph()
