
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
Created on 
26.01.11
@author: Zhitko V.A. 
'''

import sc_core.pm as sc
import sc_core.constants as sc_constants
import suit.core.kernel as sc_core
import suit.core.sc_utils as sc_utils
import suit.core.keynodes as sc_key

import components.LUI.keynodes as keys

import time

session = sc_core.Kernel.session()
segment = sc_core.Kernel.segment()

def madeNewNSMCommand(sc_pattern_set, 
                      command_elem_list = [], 
                      str_command_short_name = "", 
                      str_command_comment = ""):
    print "[NSM] Register new NSM command"
#    print segment.get_full_uri()
    # создание узла нсм комманды
    sc_nsm_command = session.create_el(segment, sc.SC_N_CONST)
    session.gen3_f_a_f(segment,keys.nsm.nsm_command,sc_nsm_command, sc.SC_A_CONST|sc.SC_POS|sc.SC_ACTUAL)
    # создание узла связки нсм комманды
    sc_nsm_command_sheaf = session.create_el(segment, sc.SC_N_CONST)
    # соединяем узлы, под атрибутом attr_nsm_command_
    arc = session.gen3_f_a_f(segment, sc_nsm_command, sc_nsm_command_sheaf, sc.SC_A_CONST|sc.SC_POS|sc.SC_ACTUAL)[1]
    session.gen3_f_a_f(segment, keys.nsm.attr_nsm_command, arc, sc.SC_A_CONST|sc.SC_POS|sc.SC_ACTUAL)
    # создаем узел шаблона поиска нсм комманды
#    print "sc_nsm_pattern"
    sc_nsm_pattern = session.create_el(segment, sc.SC_N_CONST)
    # добавляем узел в нсм комманду под атрибутом
    arc = session.gen3_f_a_f(segment, sc_nsm_command_sheaf, sc_nsm_pattern, sc.SC_A_CONST|sc.SC_POS|sc.SC_ACTUAL)[1]
    session.gen3_f_a_f(segment, keys.nsm.attr_nsm_command_pattern, arc, sc.SC_A_CONST|sc.SC_POS|sc.SC_ACTUAL)
    # копируем шаблон поиска в нсм комманду
    q = session.copySetToSet(segment,sc_pattern_set,sc_nsm_pattern)
    # создаем узел параметров нсм комманды
#    print "sc_nsm_command_elem"
    sc_nsm_command_elem = session.create_el(segment, sc.SC_N_CONST)
    # добавляем узел в нсм комманду под атрибутом
    arc = session.gen3_f_a_f(segment, sc_nsm_command_sheaf, 
                             sc_nsm_command_elem, sc.SC_A_CONST|sc.SC_POS|sc.SC_ACTUAL)[1]
    session.gen3_f_a_f(segment, keys.nsm.attr_nsm_command_elem, arc, sc.SC_A_CONST|sc.SC_POS|sc.SC_ACTUAL)    
    # копируем атрибуты комманды
    for i, el in enumerate(command_elem_list):
        if i < 10:
#            print i
            arc = session.gen3_f_a_f(segment, sc_nsm_command_elem, el, sc.SC_A_CONST|sc.SC_POS|sc.SC_ACTUAL)[1]
            session.gen3_f_a_f(segment, keys.nsm.attr[i], arc, sc.SC_A_CONST|sc.SC_POS|sc.SC_ACTUAL)
    # создаем узел краткого названия нсм комманды и добавляем его
#    print "sc_nsm_command_short_name"
    sc_nsm_command_short_name = session.create_el(segment, sc.SC_N_CONST)
    session.set_content_str(sc_nsm_command_short_name, str_command_short_name)
    arc = session.gen3_f_a_f(segment, sc_nsm_command_sheaf, 
                             sc_nsm_command_short_name, sc.SC_A_CONST|sc.SC_POS|sc.SC_ACTUAL)[1]
    session.gen3_f_a_f(segment, keys.nsm.attr_nsm_command_shortname, arc, sc.SC_A_CONST|sc.SC_POS|sc.SC_ACTUAL)
    # создаем узел комментария нсм комманды и добавляем его
#    print "sc_nsm_command_comment"
    sc_nsm_command_comment = session.create_el(segment, sc.SC_N_CONST)
    session.set_content_str(sc_nsm_command_comment, str_command_comment)
    arc = session.gen3_f_a_f(segment, sc_nsm_command_sheaf, 
                             sc_nsm_command_comment, sc.SC_A_CONST|sc.SC_POS|sc.SC_ACTUAL)[1]
    session.gen3_f_a_f(segment, keys.nsm.attr_nsm_command_comment, arc, sc.SC_A_CONST|sc.SC_POS|sc.SC_ACTUAL)
    return sc_nsm_command

def runNSMCommandWithParams(sc_nsm_command, 
                  command_elem_list = [], 
                  search = True):
    #print "[NSM] run NSM command with params"
    sc_nsm_request = session.create_el(segment, sc.SC_N_CONST)
    session.gen3_f_a_f(segment, keys.nsm.goals, sc_nsm_request, sc.SC_A_CONST|sc.SC_POS|sc.SC_ACTUAL)
    
    sc_nsm_request_sheaf = session.create_el(segment, sc.SC_N_CONST)
    arc_sheaf = session.gen3_f_a_f(segment, sc_nsm_request, sc_nsm_request_sheaf, sc.SC_A_CONST|sc.SC_POS|sc.SC_ACTUAL)[1]
    
    
    for i, el in enumerate(command_elem_list):
        arc = session.gen3_f_a_f(segment, sc_nsm_request_sheaf, el, sc.SC_A_CONST|sc.SC_POS|sc.SC_ACTUAL)[2]
        session.gen3_f_a_f(segment, keys.nsm.attr[i], arc, sc.SC_A_CONST|sc.SC_POS|sc.SC_ACTUAL)
    
    session.gen3_f_a_f(segment, sc_nsm_command, arc_sheaf, sc.SC_A_CONST|sc.SC_POS|sc.SC_ACTUAL)
    session.gen3_f_a_f(segment, keys.nsm.attr_active, arc_sheaf, sc.SC_A_CONST|sc.SC_POS|sc.SC_ACTUAL)
    if search:
        session.gen3_f_a_f(segment, keys.nsm.attr_search, arc_sheaf, sc.SC_A_CONST|sc.SC_POS|sc.SC_ACTUAL)
    else:
        session.gen3_f_a_f(segment, keys.nsm.attr_generate, arc_sheaf, sc.SC_A_CONST|sc.SC_POS|sc.SC_ACTUAL)
    return sc_nsm_request

def runNSMwithPattern(sc_pattern,
                      search = True, patternName = None):
    #print "[NSM] run NSM with pattern"
    sc_nsm_request = session.create_el(segment, sc.SC_N_CONST)
    if patternName is not None:
        session.set_content_str(sc_nsm_request, patternName)
    session.gen3_f_a_f(segment, keys.nsm.goals, sc_nsm_request, sc.SC_A_CONST|sc.SC_POS|sc.SC_ACTUAL)
    
    sc_nsm_request_sheaf = session.create_el(segment, sc.SC_N_CONST)
    arc_sheaf = session.gen3_f_a_f(segment, sc_nsm_request, sc_nsm_request_sheaf, sc.SC_A_CONST|sc.SC_POS|sc.SC_ACTUAL)[1]
    
    pat_els = session.search3_f_a_a(sc_pattern, sc.SC_A_CONST|sc.SC_POS|sc.SC_ACTUAL, sc.SC_EMPTY)
    for el in pat_els:
        session.gen3_f_a_f(segment, sc_nsm_request_sheaf, el[2], sc.SC_A_CONST|sc.SC_POS|sc.SC_ACTUAL)
    
    session.gen3_f_a_f(segment, keys.nsm.attr_active, arc_sheaf, sc.SC_A_CONST|sc.SC_POS|sc.SC_ACTUAL)
    session.gen3_f_a_f(segment, keys.nsm.attr_confirm_, arc_sheaf, sc.SC_A_CONST|sc.SC_POS|sc.SC_ACTUAL)
    if search:
        session.gen3_f_a_f(segment, keys.nsm.attr_search, arc_sheaf, sc.SC_A_CONST|sc.SC_POS|sc.SC_ACTUAL)
    else:
        session.gen3_f_a_f(segment, keys.nsm.attr_generate, arc_sheaf, sc.SC_A_CONST|sc.SC_POS|sc.SC_ACTUAL)
    return sc_nsm_request
    
def getNSMRequestScResult(sc_nsm_request, wait_for_result = True, wait_time = 0.1):
    print "[NSM] search for NSM request result"
    # wait for searched_
    res = session.search5_f_a_a_a_f(sc_nsm_request,
                                    sc.SC_A_CONST|sc.SC_POS,
                                    sc.SC_N_CONST,
                                    sc.SC_A_CONST|sc.SC_POS,
                                    keys.nsm.attr_searched)
    while not res:
        if wait_for_result:
            print "[NSM] wait for result" 
            time.sleep(wait_time)
        else:
            return None
        res = session.search5_f_a_a_a_f(sc_nsm_request,
                                        sc.SC_A_CONST|sc.SC_POS,
                                        sc.SC_N_CONST,
                                        sc.SC_A_CONST|sc.SC_POS,
                                        keys.nsm.attr_searched)
    # search for confirmed_
    sc_nsm_arc_sheaf = res[0][1]
    res = session.search3_f_a_f(keys.nsm.attr_confirmed,
                        sc.SC_A_CONST|sc.SC_POS,
                        sc_nsm_arc_sheaf)
    if not res:
        print "[nsm] no any results found" 
        return None
    
    res = session.search3_a_a_f(sc.SC_N_CONST,
                                sc.SC_A_CONST|sc.SC_POS,
                                sc_nsm_arc_sheaf)
    
    for set in res:
        if session.search3_f_a_f(keys.nsm.result,sc.SC_A_CONST|sc.SC_POS,set[0]):
            print "[NSM] find result"
            return set[0]
        
    print "[nsm] no any results found"
    return None
    
def convertNsmResult2SimpleSet(sc_nsm_result):
    res = []
    result_variants = session.search3_f_a_a(sc_nsm_result, sc.SC_A_CONST|sc.SC_POS, sc.SC_N_CONST)
    if result_variants is None: return None
    for res_variant in result_variants:
        cur_element_sheafs = session.search3_f_a_a(res_variant[2], sc.SC_A_CONST|sc.SC_POS, sc.SC_N_CONST)
        if not cur_element_sheafs: continue
        #print cur_element_sheafs
        for cur_element_sheaf in cur_element_sheafs:
            #print cur_element_sheaf
            cur_find_element = session.search5_f_a_a_a_f(cur_element_sheaf[2], 
                                                         sc.SC_A_CONST|sc.SC_POS, 
                                                         sc.SC_EMPTY,
                                                         sc.SC_A_CONST|sc.SC_POS,
                                                         sc_key.n_2)
            if not cur_find_element: continue
            res.append(cur_find_element[0][2])
    const_elements = getConstPatternElsByScResult(sc_nsm_result)
    if const_elements:
        res = res + const_elements
    return res

def convertNsmResult2Sets(sc_nsm_result):
    res = []
    result_variants = session.search3_f_a_a(sc_nsm_result, sc.SC_A_CONST|sc.SC_POS, sc.SC_N_CONST)
    if result_variants is None: return None
    for res_variant in result_variants:
        v_res = []
        cur_element_sheafs = session.search3_f_a_a(res_variant[2], sc.SC_A_CONST|sc.SC_POS, sc.SC_N_CONST)
        if not cur_element_sheafs: continue
        for cur_element_sheaf in cur_element_sheafs:
            s_res = []
            cur_find_element = session.search5_f_a_a_a_f(cur_element_sheaf[2], 
                                                         sc.SC_A_CONST|sc.SC_POS, 
                                                         sc.SC_EMPTY,
                                                         sc.SC_A_CONST|sc.SC_POS,
                                                         sc_key.n_1)
            if not cur_find_element: continue
            s_res.append(cur_find_element[0][2])
            cur_find_element = session.search5_f_a_a_a_f(cur_element_sheaf[2], 
                                                         sc.SC_A_CONST|sc.SC_POS, 
                                                         sc.SC_EMPTY,
                                                         sc.SC_A_CONST|sc.SC_POS,
                                                         sc_key.n_2)
            if not cur_find_element: continue
            s_res.append(cur_find_element[0][2])
            v_res.append(s_res)
        res.append(v_res)
    return res
    
def getConstPatternElsByScResult(sc_nsm_result):
    temp = session.search3_f_a_a(sc_nsm_result, sc.SC_A_CONST|sc.SC_POS, sc.SC_A_CONST|sc.SC_POS)
    if not temp: return None
    print temp
    sheafArc = temp[0][2]
    print sheafArc
    sc_pattern = session.search3_a_f_a(sc.SC_N_CONST, sheafArc, sc.SC_N_CONST)[0][2]
    consts = session.search3_f_a_a(sc_pattern, sc.SC_A_CONST|sc.SC_POS, sc.SC_CONST)
    res = []
    for els in consts:
        res.append(els[2])
    if len(res) is 0: return None
    return res
    
    
    