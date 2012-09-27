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
Created on 15.02.2012

@author: Denis Koronchik
'''

import suit.core.kernel as core
from suit.core.event_handler import ScEventHandlerSetMember
import suit.core.keynodes as keynodes
import sc_core.pm, sc_core.constants

key_cmd_user_play = core.Kernel.session().find_keynode_full_uri(u'/ui/core/ui_cmd_play_user_command')

def initialize():
    kernel = core.Kernel.getSingleton()
    kernel.registerOperation(ScEventHandlerSetMember(u"operation that run user command interpretation",
                                                     keynodes.ui.init_user_cmd,
                                                     run_command, []))

def shutdown():
    pass

def run_command(_params, _segment):
    # trying to find command node
    session = core.Kernel.session()
    segment = core.Kernel.segment()
    # getting answer sheaf node
    command_sheaf = session.search_one_shot(session.sc_constraint_new(sc_core.constants.CONSTR_5_f_a_a_a_f,
                                                                     keynodes.ui.init_user_cmd,
                                                                     sc_core.pm.SC_A_CONST,
                                                                     sc_core.pm.SC_N_CONST,
                                                                     sc_core.pm.SC_A_CONST,
                                                                     _params), True, 5)
    if command_sheaf is None: return # do nothing
    
    cmd = command_sheaf[2]
    
    # check if it's command to play commands sequence
    command = session.search_one_shot(session.sc_constraint_new(sc_core.constants.CONSTR_3_f_a_f,
                                                                 key_cmd_user_play,
                                                                 sc_core.pm.SC_A_CONST,
                                                                 cmd), True, 3)
    
    if command is None: return # do nothing
    
    command = session.search_one_shot(session.sc_constraint_new(sc_core.constants.CONSTR_3_f_a_a,
                                                                 cmd,
                                                                 sc_core.pm.SC_A_CONST,
                                                                 sc_core.pm.SC_N_CONST), True, 3)
    
    if command is None: return # do nothing
    cmd = command[2]
    
    import suit.core.sc_utils as sc_utils
    
    sc_utils.createPairPosPerm(session, segment, keynodes.ui.init_base_user_cmd, cmd, sc_core.pm.SC_CONST)
    