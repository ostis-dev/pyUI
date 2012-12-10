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
Created on xx.xx.2012

@author: dred
'''

import suit.core.kernel as core
import os
import scs_viewer
import scs_editor
import sc2scs

def initialize():

    kernel = core.Kernel.getSingleton()

    from suit.core.objects import Factory
    import suit.core.keynodes as keynodes

    global view_factory
    global edit_factory
    global translateSC2SCs_factory

    view_factory = Factory(viewer_creator)
    edit_factory = Factory(editor_creator)
    translateSC2SCs_factory = Factory(sc2scs_creator)
    kernel.registerViewerFactory(view_factory, [keynodes.ui.format_scsx])
    kernel.registerTranslatorFactory(translateSC2SCs_factory, [keynodes.ui.format_sc], [keynodes.ui.format_scsx])
    kernel.registerEditorFactory(edit_factory, [keynodes.ui.format_scsx])

def shutdown():
    global view_factory
    global edit_factory
    global translateSC2SCs_factory

    kernel = core.Kernel.getSingleton()
    kernel.unregisterViewerFactory(view_factory)
    kernel.unregisterEditorFactory(edit_factory)
    kernel.unregisterTranslatorFactory(translateSC2SCs_factory)

def viewer_creator():
   ''' return text_viewer.TextViewer()'''
   return scs_viewer.SCsViewer()

def editor_creator():
    ''' return text_editor.TextEditor()'''
    return scs_editor.SCsEditor()

def sc2scs_creator():
    return sc2scs.TranslatorSc2Scs()