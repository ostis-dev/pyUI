
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
Created on 29.06.2010

@author: Denis Koronchik
'''
import chem_keynodes
import chem_editor, chem_viewer, chem2sc
import chem_env

def initialize():
    """Module initialization function
    """
    import suit.core.kernel as core
    import suit.core.keynodes as keyn
    from suit.core.objects import Factory
    
    global view_factory
    global edit_factory
    global chem2sc_factory
    
    kernel = core.Kernel.getSingleton()
    
    view_factory = Factory(viewer_creator)
    edit_factory = Factory(editor_creator)
    chem2sc_factory = Factory(chem2sc_creator)
    
    kernel.registerViewerFactory(view_factory, [chem_keynodes.format])
    kernel.registerEditorFactory(edit_factory, [chem_keynodes.format])
    kernel.registerTranslatorFactory(chem2sc_factory, [chem_keynodes.format], [keyn.ui.format_sc])
    
    
def shutdown():
    """Module unloading function
    """
    import suit.core.kernel as core
    
    global view_factory
    global edit_factory
    global chem2sc_factory
    
    kernel = core.Kernel.getSingleton()
    
    kernel.unregisterViewerFactory(view_factory)
    kernel.unregisterEditorFactory(edit_factory)
    kernel.unregisterTranslatorFactory(chem2sc_factory)

def _resourceLocations():
    """Specified resources for a geometry module
    """
    res = []
    for path in chem_env.resource_dirs:
        res.append((path, "FileSystem", chem_env.resource_group))
            
    return res

def viewer_creator():
    return chem_view.ChemistryViewer()

def editor_creator():
    return chem_editor.ChemistryEditor()

def chem2sc_creator():
    return chem2sc.TranslatorChemistry2Sc()
