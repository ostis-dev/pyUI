# -*- coding: utf-8 -*-

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
Created on 21.09.2010

@author: Zhitko V.A.
'''

from components.questions import operation
import sc_core.pm as sc
import suit.core.kernel as core
import sc_core.constants as sc_constants
import suit.core.keynodes as keynodes

session = core.Kernel.session()
session.open_segment(u"/etc/operations")
session.open_segment(u"/etc/questions")

sc_main_question = session.find_el_full_uri(u"/etc/questions/поиск полной семантической окрестности")
sc_operation_node = session.find_el_full_uri(u"/etc/operations/операция поиска полной семантической окрестности")

class Op_search_full_semantic(operation.Operation):
    
    def __init__(self):
        print "init: Search full semantic square"
        pass

    @classmethod
    def checking(self, question):
        print "checking: Search full semantic square"
        # проверка входит ли вопрос в множество вопросов "поиск выходящих дуг"
        res = session.search3_f_a_f(sc_main_question,sc.SC_A_CONST|sc.SC_POS,question)
        if res is not None: return True
        else: return False
    
    def running(self, question):
        print "runing: Search full semantic square"
        # создаем множество для ответа
        res = []        
        # получаем элементы текущего вопроса
        targets = session.search3_f_a_a(question, sc.SC_A_CONST|sc.SC_POS, sc.SC_CONST|sc.SC_NODE)        
        # перебираем найденые элементы
        for target in targets:
            _a = sc.SC_A_CONST
            els = session.search3_f_a_a(target[2],_a,sc.SC_EMPTY)
            if els is not None:
                for el in els:
                    res = res + el
            rel_to_node = session.search11_f_a_a_a_a_a_f_a_f_a_a(target[2], _a, sc.SC_NODE, _a, sc.SC_NODE,
                                                                  _a, keynodes.n_2, _a, keynodes.n_1, _a, sc.SC_NODE)
            if rel_to_node is not None:
                for rel in rel_to_node:
                    #print len(rel)
                    res = res + rel
                    attrs = session.search3_f_a_a(rel[4],_a,sc.SC_EMPTY)
                    #print attrs
                    if attrs is not None:
                        for attr in attrs:
                            #print len(attr)
                            res = res + attr
            rel_from_node = session.search11_f_a_a_a_a_a_f_a_f_a_a(target[2], _a, sc.SC_NODE, _a, sc.SC_NODE,
                                                                  _a, keynodes.n_1, _a, keynodes.n_2, _a, sc.SC_NODE)
            if rel_from_node is not None:
                for rel in rel_from_node:
                    #print len(rel)
                    res = res + rel 
                    attrs = session.search3_f_a_a(rel[4],_a,sc.SC_EMPTY)
                    #print attrs
                    if attrs is not None:
                        for attr in attrs:
                            #print len(attr)
                            res = res + attr
        return res
    
    @classmethod
    def getOperationNode(self):
        return sc_operation_node
    
def searchAllPairsBinaryOrientFromNode(_session, _beg, _const):
    """Finds binary orient pairs between two elements
    @param _session:    session to fire search
    @type _session:    MThreadSession
    @param _beg:    begin element
    @type _beg:    sc_global_addr
    @param _const:    constant type
    @type _const:    int
    
    @return: return list of Pairs. Each pair contains search results in format (see template, 
    numbers is a position of element sc_global_addr in result tuple). If there are no any results founded,
    then return None
    
    template (number - index in tuple):
                     6 1_    10     8 2_
                     |       |      |
                     5       9      7
                     |       |      |
                     v       v      v
             0 <-----1------ 2 -----3-----> 4
           _beg 
    """
    res_pairs = []
    it = _session.create_iterator(session.sc_constraint_new(sc_constants.CONSTR_5_a_a_f_a_f, 
                                                            sc.SC_NODE | _const,    # 2 
                                                            sc.SC_ARC | sc.SC_POS | _const, # 1
                                                            _beg, # 0
                                                            sc.SC_ARC | sc.SC_POS | _const, # 5
                                                            keynodes.n_1),          # 6
                                                            True)
    while not it.is_over():
        r_pair = []
        it2 = _session.create_iterator(session.sc_constraint_new(sc_constants.CONSTR_5_f_a_a_a_f,
                                                                it.value(0),    # 2 
                                                                sc.SC_ARC | sc.SC_POS | _const, # 3
                                                                sc.SC_NODE | _const, # 4
                                                                sc.SC_ARC | sc.SC_POS | _const, # 7
                                                                keynodes.n_2),          # 8
                                                                True)
        if not it2.is_over():
            r_pair.append(_beg)         # 0
            r_pair.append(it.value(1))  # 1
            r_pair.append(it.value(0))  # 2
            r_pair.append(it2.value(1)) # 3
            r_pair.append(it2.value(2)) # 4
            r_pair.append(it.value(3))  # 5
            r_pair.append(keynodes.n_1) # 6
            r_pair.append(it2.value(3)) # 7
            r_pair.append(keynodes.n_2) # 8
            it3 = _session.create_iterator(session.sc_constraint_new(sc_constants.CONSTR_3_a_a_f,
                                                                    sc.SC_NODE | _const,    # 10
                                                                    sc.SC_ARC | sc.SC_POS | _const, # 9
                                                                    it.value(0)),    # 2
                                                                    True)
            rel_is_find = False
            while not it3.is_over():
                if isNodeBinOrientNoroleRel(_session, it3.value(0)):
                    if not rel_is_find:
                        rel_is_find = True
                        r_pair.append(it3.value(1)) # 9
                        r_pair.append(it3.value(0)) # 10
                it3.next()
            res_pairs.append(r_pair)
        it.next()
    if len(res_pairs) is 0: return None
    return res_pairs

def searchAllPairsBinaryOrientToNode(_session, _end, _const):
    """Finds binary orient pairs between two elements
    @param _session:    session to fire search
    @type _session:    MThreadSession
    @param _end:    begin element
    @type _end:    sc_global_addr
    @param _const:    constant type
    @type _const:    int
    
    @return: return list of Pairs. Each pair contains search results in format (see template, 
    numbers is a position of element sc_global_addr in result tuple). If there are no any results founded,
    then return None
    
    template (number - index in tuple):
                     6 2_    10     8 1_
                     |       |      |
                     5       9      7
                     |       |      |
                     v       v      v
             0 <-----1------ 2 -----3-----> 4
           _end 
    """
    res_pairs = []
    it = _session.create_iterator(session.sc_constraint_new(sc_constants.CONSTR_5_a_a_f_a_f, 
                                                            sc.SC_NODE | _const,    # 2 
                                                            sc.SC_ARC | sc.SC_POS | _const, # 1
                                                            _end, # 0
                                                            sc.SC_ARC | sc.SC_POS | _const, # 5
                                                            keynodes.n_2),          # 6
                                                            True)
    while not it.is_over():
        r_pair = []
        it2 = _session.create_iterator(session.sc_constraint_new(sc_constants.CONSTR_5_f_a_a_a_f,
                                                                it.value(0),    # 2 
                                                                sc.SC_ARC | sc.SC_POS | _const, # 3
                                                                sc.SC_NODE | _const, # 4
                                                                sc.SC_ARC | sc.SC_POS | _const, # 7
                                                                keynodes.n_1),          # 8
                                                                True)
        if not it2.is_over():
            r_pair.append(_end)         # 0
            r_pair.append(it.value(1))  # 1
            r_pair.append(it.value(0))  # 2
            r_pair.append(it2.value(1)) # 3
            r_pair.append(it2.value(2)) # 4
            r_pair.append(it.value(3))  # 5
            r_pair.append(keynodes.n_1) # 6
            r_pair.append(it2.value(3)) # 7
            r_pair.append(keynodes.n_2) # 8
            it3 = _session.create_iterator(session.sc_constraint_new(sc_constants.CONSTR_3_a_a_f,
                                                                    sc.SC_NODE | _const,    # 10
                                                                    sc.SC_ARC | sc.SC_POS | _const, # 9
                                                                    it.value(0)),    # 2
                                                                    True)
            rel_is_find = False
            while not it3.is_over():
                if isNodeBinOrientNoroleRel(_session, it3.value(0)):
                    if not rel_is_find:
                        rel_is_find = True
                        r_pair.append(it3.value(1)) # 9
                        r_pair.append(it3.value(0)) # 10
                it3.next()
            res_pairs.append(r_pair)
        it.next()
    if len(res_pairs) is 0: return None
    return res_pairs

def isNodeBinOrientNoroleRel(_session, _node):
    """Check if node have a sheaf structure type
    @param _node:    node for checking
    @type _node:    sc_global_addr
    
    @return: if node have sheaf structure type, then return True, else - False
    @rtype: bool
    """
    return checkIncToSets(_session, _node, [keynodes.info.stype_bin_orient_norole_rel], sc.SC_A_CONST | sc.SC_POS)