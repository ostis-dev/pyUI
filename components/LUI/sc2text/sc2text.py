
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

@author: 
'''

"""sc -> text translator component
"""
from suit.core.objects import Translator
import sc_core.pm as sc
import sc_core.constants as sc_constants
import suit.core.kernel as sc_core
import suit.core.sc_utils as sc_utils
import suit.core.keynodes as sc_key

import components.LUI.keynodes as keys
import nsm
import html2text

import time

session = sc_core.Kernel.session()
session.open_segment(u"/seb/test")
session.open_segment(u"/seb/planimetry")
session.open_segment(u"/seb/rus")
session.open_segment(u"/seb/bel")
session.open_segment(u"/seb/lingv")
seg = session.open_segment(u"/ui/lui")
segment = sc_core.Kernel.segment()

test_input = session.find_keynode_full_uri(u"/seb/test/s2t_test2")
test_output = session.find_keynode_full_uri(u"/seb/test/s2t_test3")
pattern_test_1 = session.find_keynode_full_uri(u"/seb/test/pattern_test_1")
input_test_1 = session.find_keynode_full_uri(u"/seb/test/input_test_1")
input_test = session.find_keynode_full_uri(u"/seb/test/input_test")

_aACP = sc.SC_A_CONST|sc.SC_POS

class TranslatorSc2Text(Translator):
    """Class that realize translation from SC-code directly to text
    """    
    def __init__(self):
        Translator.__init__(self)
        
    def __del__(self):
        Translator.__del__(self)
        
    def translate_impl(self, _input = None, _output = None):
        """Translator implementation
        @param _input:    input data set
        @type _input:    sc_global_addr
        @param _output:    output window (must be created)
        @type _output:    sc_global_addr
        
        @return: list of errors each element of list is a tuple(object, error)
        @rtype: list
        """
        errors = []     
        lang = getUsedLanguage()   
        if lang is None: lang = keys.rus_lang
        print "[sc2text] Used language %s" % session.get_idtf(lang) 
        text = str(html2text.html2text(str(Translate(_input, lang))))
        #sc_utils.setContentStr(session, segment, _output, text)
        
        session.gen3_f_a_f(seg, lang, _output, sc.SC_A_CONST|sc.SC_POS)
        session.set_content_str(_output, text)
        
        print text
        
#        res = session.create_el(segment, sc.SC_N_CONST)
#        set = session.create_el(segment, sc.SC_N_CONST)
#        #sc_utils.setContentStr(session, segment, res, str(text))
#        session.set_content_str(res, str(text))
#        session.gen3_f_a_f(segment, set, res, sc.SC_A_CONST|sc.SC_POS)
#        out_to_user(set)
        
        return errors
    
def getUsedLanguage():
    langs = session.search3_f_a_a(keys.used_lang,sc.SC_A_CONST|sc.SC_POS,sc.SC_N_CONST)
    if langs is not None:
        return langs[0][2]
    return None
    
def out_to_user(sc_set):
    windows = session.search3_f_a_a(sc_key.ui.set_output_windows, sc.SC_A_CONST|sc.SC_POS, sc.SC_N_CONST)
    if windows:
        for els in windows:
            sc_core.Kernel.getSingleton().translateFromSc(sc_set, els[2])
    
def Translate(sc_input, lang):
    print "[sc2text] Translating"
    answer = ""
    f = True
    rules = LoadRules()
    for rule in rules:
        in_pattern = GetInputPattern(rule)
        if in_pattern is None: continue
        new_pattern = UpdatePattern(in_pattern, sc_input)
        result = ExecPattern(new_pattern, session.get_idtf(rule))
        res_map = ProcessResult (result, rule)
        #print res_map
        if res_map is None: continue
        out_pattern = GetOutputPattern(rule, lang)
        if out_pattern is None: continue
        text = MakeAnswer(out_pattern, res_map, lang)
        if f:
            answer = text
            f = False
        else:
            answer = answer + "\n" + text
    return answer

def isNeededLanguage(node, lang):
    r = session.search3_f_a_f(lang, _aACP, node)
    if r is None:
        return False
    return True

def TranslateObject(sc_object, lang):
    # search translation
    text = None
    isText = False
    rels_tr = session.search11_f_a_a_a_a_a_f_a_f_a_f(sc_object, _aACP, sc.SC_N_CONST, _aACP, sc.SC_N_CONST,
                                           _aACP, sc_key.n_1, _aACP, sc_key.n_2, _aACP, keys.nrel_translation)
    if rels_tr is not None:
        for rel_tr in rels_tr:
            trs = session.search3_f_a_a(rel_tr[4], _aACP, sc.SC_EMPTY)
            for tr in trs:
                if not isNeededLanguage(tr[2], lang): continue
                t_text = session.get_content_str(tr[2])
                if t_text is not None:
                    if isText:
                        text += (", " + t_text)
                    else:
                        text = t_text
                        isText = True
    if text is not None: return text  
    
    # search identification
    text = None
    isText = False
    rels_tr = session.search11_f_a_a_a_a_a_f_a_f_a_f(sc_object, _aACP, sc.SC_N_CONST, _aACP, sc.SC_N_CONST,
                                           _aACP, sc_key.n_2, _aACP, sc_key.n_1, _aACP, keys.nrel_identification)
    if rels_tr is not None:
        for rel_tr in rels_tr:
            trs = session.search3_f_a_a(rel_tr[4], _aACP, sc.SC_EMPTY)
            for tr in trs:
                if not isNeededLanguage(tr[2], lang): continue
                t_text = session.get_content_str(tr[2])
                if t_text is not None:
                    if isText:
                        text += (", " + t_text)
                    else:
                        text = t_text
                        isText = True
    if text is not None: return text  
    # search main identification
    # search string content
    if not isNeededLanguage(sc_object, lang): return None
    text = session.get_content_str(sc_object)
    if text is not None: return text
    # search identificator
    #text = session.get_idtf(sc_object)
    #if text is not None: return text
    return None

def MakeAnswer(out_pattern, res_map, lang):
    text = ""
    ff = True
    for map in res_map:
        t = out_pattern
        has_ans = True
        for key in map.keys():
            new = None
            f = True
            for el in map[key]:
                str = TranslateObject(el, lang)
                if str is None: continue
                if f:
                    f = False
                    new = str
                else:
                    new += (", " + str)
            print "[sc2text] key: %s; new: %s text: %s" % (key, new, t)
            if new is None: 
                has_ans = False
            else:
                t = t.replace(key, new)
        if has_ans:
            text += (t + " ")
    return text#unicode(text).decode('iconv:cp1251').encode('iconv:utf-8')

def GetInputPattern(rule):
    sc_pattern = session.search5_f_a_a_a_f(rule, _aACP, sc.SC_N_CONST, _aACP, keys.patterns.attr_inputPattern)
    if sc_pattern is None:
        print "[sc2text] Error input pattern not found in %s" % session.get_idtf(rule)
        return None
    else:
        return sc_pattern[0][2]
    
def GetOutputPattern(rule, lang):
    sc_patterns = session.search5_f_a_a_a_f(rule, _aACP, sc.SC_N_CONST, _aACP, keys.patterns.attr_outputPattern)
    if sc_patterns is not None:
        for pattern in sc_patterns:
            if session.search3_f_a_f(lang,sc.SC_A_CONST|sc.SC_POS,pattern[2]) is not None:
                return session.get_content_str(pattern[2])
    print "[sc2text] Error output pattern not found in %s" % session.get_idtf(rule)
    return None

def ProcessResult(results, rule):
    need_els = session.search5_f_a_a_a_f(rule, _aACP, sc.SC_N_CONST, _aACP, keys.patterns.attr_inputParams)
    if need_els is None:
        print "[sc2text] Error input parameters not found in %s" % session.get_idtf(rule)
        return None
    need_els = need_els[0][2]
    params_info = {}
    for i in xrange(10):
        param = session.search5_f_a_a_a_f(need_els, _aACP, sc.SC_EMPTY, _aACP, keys.nsm.attr[i])
        if param is not None:
            #print "[sc2text] find %s parameter" % str(i+1) 
            param = param[0]
            multi = session.search3_f_a_f(keys.patterns.attr_multi, _aACP, param[1])
            if multi is None:
                params_info[session.get_idtf(param[2])] = ([str(i+1)+u"_",False])
            else:
                params_info[session.get_idtf(param[2])] = ([str(i+1)+u"_",True])
    
    res_maps = []
    for result in results:
        tmp_res = []
        for els in result:
            key = session.get_idtf(els[0])
            if params_info.has_key(key):
                info = params_info[key]
                tmp_res.append([info[0],[els[1]],info[1]])
        #print len(tmp_res)
        
        new = True
        for res in res_maps:
            cur = True
            for el1 in res:
                for el2 in tmp_res:
                    t1 = session.get_idtf(el1[1][0])
                    t2 = session.get_idtf(el2[1][0])
                    #if el1[0] == el2[0] and t1 == t2 and el1[2] == False and cur == True:
                    #    cur = True
                    if el1[0] == el2[0] and t1 != t2 and el1[2] == False:
                        cur = False
            if cur:
                for el1 in res:
                    for el2 in tmp_res:
                        if el1[0] == el2[0] and el1[2] == True:
                            el1[1].append(el2[1][0])
                new = False
        if new:
            res_maps.append(tmp_res)
    res = []
    for els in res_maps:
        t_res = {}
        for el in els:
            t_res[el[0]] = el[1]
        res.append(t_res)
    return res
                    

def LoadRules():
    #print "[sc2text] load patterns"
    rules = []
    els = session.search3_f_a_a(keys.patterns.ScToTextPatterns, sc.SC_A_CONST|sc.SC_POS, sc.SC_NODE)
    if els is not None:
        for el in els:
            print "[sc2text] Load '%s'" % session.get_idtf(el[2])
            rules.append(el[2])
    return rules

def ExecPattern(sc_pattern, sc_pattern_name):
    request = nsm.runNSMwithPattern(sc_pattern, sc_pattern_name)
    sc_result = nsm.getNSMRequestScResult(request)
    result = []
    if sc_result is not None:
        result = nsm.convertNsmResult2Sets(sc_result)
        if result is None:
            result = []
            print "[sc2text] Some strange warning. Answer variants disappear..."
    print "[sc2text] Apply %s find %s variants" % (sc_pattern_name, len(result))
    return result
        
def UpdatePattern(pattern, input):
    new_pattern = session.create_el(segment, sc.SC_N_CONST)
    
    all_el = [input]
    p_els = session.search3_f_a_a(pattern, _aACP, sc.SC_EMPTY)
    #print len(p_els)
    for p_el in p_els:
        arc = session.gen3_f_a_f(segment, input, p_el[2], sc.SC_ARC|sc.SC_POS|sc.SC_VAR)[1]
        all_el.append(p_el[2])
        all_el.append(arc)
        
    for el in all_el:
        session.gen3_f_a_f(segment, new_pattern, el, _aACP)
        
    return new_pattern
    
def Test1():
    print "test 1"
    sc_rules = session.create_el(segment, sc.SC_NODE | sc.SC_CONST)
    sc_rule = session.create_el(segment, sc.SC_NODE | sc.SC_CONST)
    session.gen3_f_a_f(segment, sc_rules, sc_rule, sc.SC_A_CONST | sc.SC_POS)
    session.gen3_f_a_f(segment, keys.production_eng.rel_impl, sc_rule, sc.SC_A_CONST | sc.SC_POS)
    sc_if_pattern = session.create_el(segment, sc.SC_NODE | sc.SC_CONST)
    arc = session.gen3_f_a_f(segment, sc_rule, sc_if_pattern, sc.SC_A_CONST | sc.SC_POS)[1]
    session.gen3_f_a_f(segment, keys.production_eng.attr_if, arc, sc.SC_A_CONST | sc.SC_POS)
    sc_then_pattern = session.create_el(segment, sc.SC_NODE | sc.SC_CONST)
    arc = session.gen3_f_a_f(segment, sc_rule, sc_then_pattern, sc.SC_A_CONST | sc.SC_POS)[1]
    session.gen3_f_a_f(segment, keys.production_eng.attr_then, arc, sc.SC_A_CONST | sc.SC_POS)
    sc_el_pattern = session.create_el(segment, sc.SC_VAR | sc.SC_NODE)
    session.gen3_f_a_f(segment, sc_if_pattern, sc_el_pattern, sc.SC_A_CONST | sc.SC_POS)
    session.gen3_f_a_f(segment, sc_if_pattern, test_input, sc.SC_A_CONST | sc.SC_POS)
    arc = session.gen3_f_a_f(segment, test_input, sc_el_pattern, sc.SC_A_VAR | sc.SC_POS)[1]
    session.gen3_f_a_f(segment, sc_if_pattern, arc, sc.SC_A_CONST | sc.SC_POS)
    session.gen3_f_a_f(segment, sc_then_pattern, sc_el_pattern, sc.SC_A_CONST | sc.SC_POS)
    session.gen3_f_a_f(segment, sc_then_pattern, test_output, sc.SC_A_CONST | sc.SC_POS)
    arc = session.gen3_f_a_f(segment, test_output, sc_el_pattern, sc.SC_A_VAR | sc.SC_POS)[1]
    session.gen3_f_a_f(segment, sc_then_pattern, arc, sc.SC_A_CONST | sc.SC_POS)
    session.gen3_f_a_f(segment, keys.production_eng.engine, sc_rules, sc.SC_A_CONST | sc.SC_POS)
#    while session.search_one_shot(session.sc_constraint_new(
#                sc_constants.CONSTR_3_f_a_f,keys.production_eng.engine,0,sc_rules),False,1):
#        print "[wait]"
#        time.sleep(0.5)
#    print "[done]"
            
def Test2():
    print "test 2"
    sc_nsm_command = nsm.madeNewNSMCommand(pattern_test_1,Set2List(session, input_test_1, 
                                                                   sc.SC_CONST|sc.SC_POS, 0))
    sc_nsm_request = nsm.runNSMCommand(sc_nsm_command, [input_test])
    result = nsm.getNSMRequestScResult(sc_nsm_request)
    list_result = nsm.convertNsmResult2SimpleSet(result)
    print len(list_result)
    
def Set2List(_session, set, arc_type, el_type):
    res = []
    it = _session.create_iterator(session.sc_constraint_new(sc_constants.CONSTR_3_f_a_a,
                                                           set,
                                                           sc.SC_ARC | arc_type,
                                                           el_type
                                                           ), True)
    while not it.is_over():
        res.append(it.value(2))
        it.next()
    return res