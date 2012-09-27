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
Created on 07.02.2012

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
s_seg = session.open_segment(u"/ui/lui")

sc_main_question = session.find_el_full_uri(u"/ui/menu/сменить систему синтеза")
sc_operation_node = session.create_el_full_uri(u"/etc/operations/операция смены системы синтеза")[1]

activeTTS = session.create_el_full_uri(u"/ui/lui/activeTTS")[1]
regTTS = session.create_el_full_uri(u"/ui/lui/regTTS")[1]

class Op_change_tts(operation.Operation):
    
    def __init__(self):
        print "init: Change TTS"
        pass

    @classmethod
    def checking(self, question):
        print "checking: Change TTS"
        # проверка входит ли вопрос в множество вопросов "поиск выходящих дуг"
        #res = session.search3_f_a_f(sc_main_question,sc.SC_A_CONST|sc.SC_POS,question)
        #if res is not None: return True
        res = session.search3_f_a_f(sc_main_question,sc.SC_A_CONST|sc.SC_POS,question)
        if res is not None: return True
        return False
    
    def running(self, question):
        print "runing: Change TTS"
        # создаем множество для ответа
        res = []        
        
        olds = session.search3_f_a_a(activeTTS, sc.SC_A_CONST|sc.SC_POS, sc.SC_CONST|sc.SC_NODE)
        for tts in olds:
            session.erase_el(tts[1])
        
        # получаем элементы текущего вопроса
        targets = session.search3_f_a_a(question, sc.SC_A_CONST|sc.SC_POS, sc.SC_CONST|sc.SC_NODE)        
        if targets is None: return res 
        session.gen3_f_a_f(s_seg, activeTTS,targets[0][2],sc.SC_A_CONST|sc.SC_POS)
        
        return res
    
    @classmethod
    def getOperationNode(self):
        return sc_operation_node