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

from suit.core.event_handler import ScEventHandlerSetMember
import suit.core.kernel as core
import suit.core.keynodes as keynodes
import sc_core.constants
import sc_core.pm

def initialize():
    kernel = core.Kernel.getSingleton()
    # register operation
    kernel.registerOperation(ScEventHandlerSetMember(u"операция добавления кнопок на панель", 
                                                     keynodes.ui.translator,
                                                     add_button, []))

def shutdown():
    pass


def add_button(_params, _segment):
    session = core.Kernel.session()
    
    # get translator class node 
    _translator = session.search_one_shot(session.sc_constraint_new(sc_core.constants.CONSTR_5_f_a_a_a_f, 
                                                                keynodes.ui.translator,
                                                                sc_core.pm.SC_A_CONST | sc_core.pm.SC_POS,
                                                                sc_core.pm.SC_N_CONST,
                                                                sc_core.pm.SC_A_CONST | sc_core.pm.SC_POS,
                                                                _params), True, 5)
    assert _translator is not None
    _translator = _translator[2]
    
    formats = core.Kernel.getSingleton()._getTranslatorFormats(_translator, False)
    for fmt in formats:
        if fmt.this == keynodes.ui.format_sc.this:
            continue
        core.windows_panel.addButton(fmt)