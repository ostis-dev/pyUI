
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
Created on 03.06.2011

@author: Zhitko V.A.
'''

from suit.core.objects import Translator
import sc_core.pm as sc
import suit.core.kernel as sc_core

import keynodes as keys

session = sc_core.Kernel.session()
#session.open_segment(u"/ui/menu")
#session.open_segment(u"/etc/operations")
session.open_segment(u"/etc/questions")
session.open_segment(u"/ui/lui")

import sys

class TranslatorSc2Voice(Translator):
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
        speak(_input)
        
        return errors
    
#import vo_init
#print dir(vo_init)
#modules = vo_init.getModules()
    
def speak(_input):
    from components.LUI_voice_output.vo_init import getModules
    modules = getModules()
    
    els = session.search3_f_a_a(_input, sc.SC_A_CONST|sc.SC_POS, sc.SC_NODE)
    expr = ""
    lang = None
    for el in els:
        s = session.get_content_str(el[2])
        if s is not None:
            for k in keys.langs.keys():
                r = session.search3_f_a_f(k, sc.SC_A_CONST|sc.SC_POS, el[2])
                if r is not None:
                    lang = keys.langs[k]
            expr = expr + s
        
    print "[Sc2Voice] Output phrase: %s" % expr
    name = ""
    activeTTS = session.search3_f_a_a(keys.ui.activeTTS, sc.SC_A_CONST|sc.SC_POS, sc.SC_NODE)
    for tts in activeTTS:
        name = session.get_idtf(tts[2])
    if name == "":
        print "[Sc2Voice] Can't find active TTS"
        return errors
    print "[Sc2Voice] Output by %s" % name
    module = modules[name]
    try: 
        if lang is None:
            module.say(expr)
        else:
            module.say(expr,lang)
    except:
        print "[Sc2Voice] Error in %s" % name
        bug_report()
    
def bug_report():
    if sys.exc_info() != (None,None,None) : last_type, last_value, last_traceback = sys.exc_info()
    else : last_type, last_value, last_traceback = sys.last_type, sys.last_value, sys.last_traceback 
    tb, descript = last_traceback, []
    while tb :
        fname, lno = tb.tb_frame.f_code.co_filename, tb.tb_lineno
        descript.append('\tFile "%s", line %s, in %s\n'%(fname, lno, tb.tb_frame.f_code.co_name))
        tb = tb.tb_next
    descript.append('%s : %s\n'%(last_type.__name__, last_value))
    for i in descript : print i