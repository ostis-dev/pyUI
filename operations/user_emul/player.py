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
Created on 15.01.2011

@author: Denis Koronchik
'''
from suit.core.kernel import Kernel
from suit.core.event_handler import ScEventHandlerSetMember
from suit.core.objects import ScObject
import suit.core.keynodes as keynodes
import suit.core.sc_utils as sc_utils
import sc_core.pm, sc_core.constants
import suit.core.render.engine as render_engine

import commands

cmds = {}   # map of active commands (command implementation, command sc_addr)

def initialize():
    kernel = Kernel.getSingleton()
    kernel.registerOperation(ScEventHandlerSetMember(u"операция перехода к следующей команде при выполнении протокола действий",
                                                     keynodes.ui.finish_base_user_cmd,
                                                     cmd_finished, []))

def shutdown():
    pass


def cmd_finished(_params, _segment):
    
    session = Kernel.session()
    
    # getting command node
    command = session.search_one_shot(session.sc_constraint_new(sc_core.constants.CONSTR_5_f_a_a_a_f,
                                                                     keynodes.ui.finish_base_user_cmd,
                                                                     sc_core.pm.SC_A_CONST,
                                                                     sc_core.pm.SC_N_CONST,
                                                                     sc_core.pm.SC_A_CONST,
                                                                     _params), True, 5)
    if not command:
        return
    
    # remove finished state (that need to replay it in future)
    session.erase_el(command[1])
    
    command = command[2] 
    
    # trying to find next command
    res = sc_utils.searchOneShotFullBinPairsAttrFromNode(session, command, keynodes.common.nrel_base_order, sc_core.pm.SC_CONST)
    
    if res is None:
        return
    
    next_command = res[2]
    
    # check if command isn't active
    if sc_utils.checkIncToSets(session, next_command, [keynodes.ui.active_base_user_cmd], sc_core.pm.SC_CONST):
        raise RuntimeWarning("Command %s is active" % str(next_command))
    
    # if next command included into finished commands set, then we need to remove it from that set
    if sc_utils.checkIncToSets(session, next_command, [keynodes.ui.finish_base_user_cmd], sc_core.pm.SC_CONST):
        sc_utils.removeFromSet(session, next_command, keynodes.ui.finish_base_user_cmd)
    
    # append command into set of initialized commands
    sc_utils.appendIntoSet(session, Kernel.segment(), next_command, keynodes.ui.init_base_user_cmd, sc_core.pm.SC_CONST)
    

    