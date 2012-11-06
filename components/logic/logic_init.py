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

from components.logic import logic_viewer, logic_editor
import logic2sc

def initialize():

    import suit.core.kernel as core
    import suit.core.keynodes as keyn
    from suit.core.objects import Factory

    global logic2sc_factory

    kernel = core.Kernel.getSingleton()

    logic2sc_factory=Factory(logic2sc_creator)

    view_factory = Factory(viewer_creator)
    edit_factory = Factory(editor_creator)

    kernel.registerTranslatorFactory(logic2sc_factory,[keyn.ui.format_logic] , [keyn.ui.format_sc])
    kernel.registerViewerFactory(view_factory, [keyn.ui.format_logic])

    kernel.registerEditorFactory(edit_factory, [keyn.ui.format_logic])

#    translator=logic2sc_creator()
#
#    translator.translate("ololo",)



def shutdown():
    import suit.core.kernel as core
    kernel = core.Kernel.getSingleton()
    global logic2sc_factory
    # unregister components
    kernel.unregisterTranslatorFactory(logic2sc_factory)

def logic2sc_creator():
    return logic2sc.TranslatorLoogic2Sc()

def viewer_creator():
    return logic_viewer.TextViewer()

def editor_creator():
    return logic_editor.TextEditor()
