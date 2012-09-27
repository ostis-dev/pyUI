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
import ogre.io.OIS as ois
import suit.core.objects

import commands

cmds = {}   # map of active commands (command implementation, command sc_addr)

def initialize():
    kernel = Kernel.getSingleton()
    kernel.registerOperation(ScEventHandlerSetMember(u"операция эмуляции перемещения мыши на объект",
                                                     keynodes.ui.init_base_user_cmd,
                                                     mouse_move_object, []))
    kernel.registerOperation(ScEventHandlerSetMember(u"операция эмуляции нажатия(отпускания) кнопки мыши",
                                                     keynodes.ui.init_base_user_cmd,
                                                     mouse_button, []))

def shutdown():
    pass

def finish_callback(cmd):
    session = Kernel.session()
    
    # remove command from active commands set
    sc_utils.removeFromSet(session, cmds[cmd], keynodes.ui.active_base_user_cmd)
    # append command into finished command set
    sc_utils.appendIntoSet(session, Kernel.segment(), cmds[cmd], 
                           keynodes.ui.finish_base_user_cmd,
                           sc_core.pm.SC_CONST | sc_core.pm.SC_POS)
   
    cmds.pop(cmd)
    cmd.delete()

def mouse_move_object(_params, _segment):
    
    session = Kernel.session()
    
    # getting command node
    command = session.search_one_shot(session.sc_constraint_new(sc_core.constants.CONSTR_5_f_a_a_a_f,
                                                                     keynodes.ui.init_base_user_cmd,
                                                                     sc_core.pm.SC_A_CONST,
                                                                     sc_core.pm.SC_N_CONST,
                                                                     sc_core.pm.SC_A_CONST,
                                                                     _params), True, 5)
    if not command:
        return
    
    # remove from initiated set
    session.erase_el(command[1])
    
    command = command[2]
    
    # check if it's a mouse move to object command
    if not sc_utils.checkIncToSets(session, command, [keynodes.ui.cmd_mouse_move_obj], sc_core.pm.SC_CONST):
        return
    
    # remove command from initiated set
    sc_utils.removeFromSet(session, command, keynodes.ui.init_base_user_cmd)
    
    # make command activated
    sc_utils.appendIntoSet(session, _segment, command, 
                           keynodes.ui.active_base_user_cmd, 
                           sc_core.pm.SC_CONST | sc_core.pm.SC_POS)
    
    # get target object
    object = session.search_one_shot(session.sc_constraint_new(sc_core.constants.CONSTR_3_f_a_a,
                                                               command,
                                                               sc_core.pm.SC_A_CONST,
                                                               0), True, 3)
    if not object:
        return
    
    object = object[2]
    
    obj = ScObject._sc2Objects(object)
    if len(obj) == 0:
        return
        
    obj = obj[0]
    
#    print obj._getScAddr().this
    # FIXME: find element in specified window (root window)
    init_pos = (0, 0)
#    target_pos = None
#    if isinstance(obj, suit.core.objects.ObjectDepth):
#        target_pos = render_engine.pos3dTo2dWindow(obj.getPosition())
#    else:
#        target_pos = obj.getCenter()
    
    cmd = commands.MouseMove(init_pos, obj)
    cmd.eventFinished = finish_callback
    cmds[cmd] = command
    cmd.start()
    
    
def mouse_button(_params, _segment):
    
    session = Kernel.session()
    
    # getting command node
    command = session.search_one_shot(session.sc_constraint_new(sc_core.constants.CONSTR_5_f_a_a_a_f,
                                                                     keynodes.ui.init_base_user_cmd,
                                                                     sc_core.pm.SC_A_CONST,
                                                                     sc_core.pm.SC_N_CONST,
                                                                     sc_core.pm.SC_A_CONST,
                                                                     _params), True, 5)
    if not command:
        return
    command = command[2]
    
    pressed = False
    # check if it's a mouse move button press command
    if sc_utils.checkIncToSets(session, command, [keynodes.ui.cmd_mouse_button_press], sc_core.pm.SC_CONST):
        pressed = True
    elif not sc_utils.checkIncToSets(session, command, [keynodes.ui.cmd_mouse_button_release], sc_core.pm.SC_CONST):
        return
    
    # need to get button id
    button = session.search_one_shot(session.sc_constraint_new(sc_core.constants.CONSTR_3_f_a_a,
                                                               command,
                                                               sc_core.pm.SC_A_CONST,
                                                               sc_core.pm.SC_N_CONST), True, 3)
    
    if button is None:
        raise RuntimeError("There are no button id for mouse button command %s" % str(command));
    button = button[2]
       
    button_id = -1
    # translate button sc-addr into ois button id
    if button.this == keynodes.ui.mouse_button_left.this:
        button_id = ois.MB_Left
    elif button.this == keynodes.ui.mouse_button_right.this:
        button_id = ois.MB_Right
    elif button.this == keynodes.ui.mouse_button_middle.this:
        button_id = ois.MB_Middle
    else:
        raise RuntimeError("Unknown mouse button id for command %s" % str(command))
   
    cmd = commands.MouseButton(button_id, 0.1, pressed)
    cmd.eventFinished = finish_callback
    cmds[cmd] = command
    cmd.start()
    