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
Created on 11.10.2010

@author: Denis Koronchik
'''
from suit.core.event_handler import ScEventHandlerSetMember
import suit.core.kernel as core
import suit.core.keynodes as keynodes
import suit.core.sc_utils as sc_utils
import sc_core.pm, sc_core.constants

def initialize():
    kernel = core.Kernel.getSingleton()
    kernel.registerOperation(ScEventHandlerSetMember(u"операция вывода ответов пользователю",
                                                     keynodes.questions.nrel_answer,
                                                     user_output_answer, []))

def shutdown():
    pass


def user_output_answer(_params, _segment):
    # trying to find question node
    session = core.Kernel.session()
    # getting answer sheaf node
    answer_sheaf = session.search_one_shot(session.sc_constraint_new(sc_core.constants.CONSTR_5_f_a_a_a_f,
                                                                     keynodes.questions.nrel_answer,
                                                                     sc_core.pm.SC_A_CONST,
                                                                     sc_core.pm.SC_N_CONST,
                                                                     sc_core.pm.SC_A_CONST,
                                                                     _params), True, 5)
    if answer_sheaf is None:
        raise Exception("Can't find answer sheaf node")
    answer_sheaf = answer_sheaf[2]
    # go to begin of pair
    question_node = session.search_one_shot(session.sc_constraint_new(sc_core.constants.CONSTR_5_f_a_a_a_f,
                                                                      answer_sheaf,
                                                                      sc_core.pm.SC_A_CONST,
                                                                      sc_core.pm.SC_N_CONST,
                                                                      sc_core.pm.SC_A_CONST,
                                                                      keynodes.n_1), True, 5)
    if question_node is None:
        raise Exception("Can't find question node")
    question_node = question_node[2]
    if question_node is None:
        return
    
    # get author and check if it's a user
    authors_set = sc_utils.searchOneShotBinPairAttrFromNode(session, question_node, keynodes.common.nrel_authors, sc_core.pm.SC_CONST)
    if authors_set is None:
        return
    is_user = False
    it = session.create_iterator(session.sc_constraint_new(sc_core.constants.CONSTR_3_f_a_a,
                                                       authors_set,
                                                       sc_core.pm.SC_A_CONST | sc_core.pm.SC_POS,
                                                       sc_core.pm.SC_N_CONST), True)
    while not it.is_over():
        
        author = it.value(2)
        if sc_utils.checkIncToSets(session, author, [keynodes.ui.user], sc_core.pm.SC_CONST):
            is_user = True
        it.next()
    
    if not is_user:
        return
    
    # get answer node
    answer_node = session.search_one_shot(session.sc_constraint_new(sc_core.constants.CONSTR_5_f_a_a_a_f,
                                                                    answer_sheaf,
                                                                    sc_core.pm.SC_A_CONST,
                                                                    sc_core.pm.SC_N_CONST,
                                                                    sc_core.pm.SC_A_CONST,
                                                                    keynodes.n_2), True, 5)
    if answer_node is None:
       return
    answer_node = answer_node[2]
    
    # get output windows
    output_set = sc_utils.searchOneShotBinPairAttrToNode(session, question_node, keynodes.ui.nrel_set_of_output_windows, sc_core.pm.SC_CONST)
    if output_set is None:
        return
    
    it = session.create_iterator(session.sc_constraint_new(sc_core.constants.CONSTR_3_f_a_a,
                                                           output_set,
                                                           sc_core.pm.SC_A_CONST | sc_core.pm.SC_POS,
                                                           sc_core.pm.SC_N_CONST), True)
    while not it.is_over():
        try:
            core.Kernel.getSingleton().translateFromSc(answer_node, it.value(2))
        except:
            import sys, traceback
            print "Error:", sys.exc_info()[0]
            traceback.print_exc(file=sys.stdout)
        it.next()
    
