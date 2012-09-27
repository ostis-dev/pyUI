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
Created on 08/02/2011

@author: Sergei Zalivako, Sergei Startsev
'''

# импорт базового модуля операции
from components.questions import operation

import sc_core.pm as sc
import sc_core.nsm as nsm
import suit.core.kernel as core
import sc_core.constants as sc_constants

# получение текущей сессии
session = core.Kernel.session()

sc_operation_node = session.create_el_full_uri(u"/etc/operations/операция поиска утверждения об однозначном задании")[1]
sc_main_question = session.find_el_full_uri(u"/etc/questions/поиск утверждения об однозначном задании")
sc_nsm_command = session.find_el_full_uri(u"/etc/nsm/descr_nsm_cmd_dl11")

# класс операции поиска всех выходящих дуг
class Op_search_example(operation.Operation):
    
    # функция инициализации
    def __init__(self):
        print "init: Op_search_domain"
        pass
    
    # функция проверки условия запуска
    @classmethod
    def checking(self, question):
        print "checking: Op_search_domain"
        res = session.search3_f_a_f(sc_main_question,sc.SC_A_CONST|sc.SC_POS,question)
        if res is not None: return True
        else: return False
    
    # функция поиска ответа на вопрос
    def running(self, question):
        print "runing: Op_search_domain"
        res = []
        els = session.search3_f_a_a(question, sc.SC_A_CONST|sc.SC_POS, sc.SC_N_CONST)
        if els is not None:
            for el in els:
                request = nsm.runNSMCommandWithParams(sc_nsm_command,[el[2]])
                result = nsm.getNSMRequestScResult(request)
                if result is not None:
                    res = nsm.convertNsmResult2SimpleSet(result)
        return res
    
    # метод возвращающий узел данной операции
    @classmethod
    #@staticmethod
    def getOperationNode(self):
        return sc_operation_node