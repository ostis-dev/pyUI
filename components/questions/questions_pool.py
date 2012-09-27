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
from keynodes import session


'''
Created on 
2010
@author: Zhitko V.A.
'''

import suit.core.kernel as core
import sc_core.pm as sc
import suit.core.keynodes as sc_keys

import os
import sys
import inspect
import Queue
import threading
import time

from operation import Operation
import keynodes as keys

session = core.Kernel.session()
#segment = core.Kernel.segment()
segment = session.open_segment(u"/etc/questions")

operations_dir = os.path.join(os.path.dirname(__file__),"operations")
sys.path.append(operations_dir)

def_py = ["__init__"]

class QuestionsPool(sc.ScOperationActSetMember):
    
    modules = []
    queue = Queue.Queue()
    workers = []
    
    def __init__(self, workers=4, acceleration=0):
        print "[Questions] Initialize"
        # установка события на появление инициированного вопроса
        sc.ScOperationActSetMember.__init__(self, "questions_pool", sc_keys.questions.initiated)
        self.registerOperation()
        
        self.max_workers = workers
        self.acceleration = acceleration
        
        self.loadQuestionsModules()
        
    def loadQuestionsModules(self):
        # поиск и инициализация всех python's операций        
        # поиск файлов в дирректории
        for fname in os.listdir(operations_dir):
            if fname.endswith(".py"):
                module_name = fname[:-3]                
                # получаем модули из найденых файлов
                if module_name not in def_py:
                    try:
                        package_obj = __import__(module_name)
                        for elem in dir (package_obj):
                            obj = getattr (package_obj, elem)# Это класс?
                            if inspect.isclass (obj):
                                # Класс производный от Operation?
                                if issubclass (obj, Operation):
                                    # заполняем список модулей
                                    obj_checkers = self.__create_checkers(obj)
                                    self.modules.append((obj,obj_checkers))
                    except:
                        print "[Questions] Bad operation %s" % module_name
                        bug_report()
                    else:
                        print "[Questions] Load operation %s" % module_name
                        
    def __create_checkers(self, oper):
        #print "[Questions] Create checkers %s" % oper
        checkers = []
        checkers.append(Checker([sc_keys.questions.finished], False))
        cond_nodes = self.__get_conditions_nodes(oper.getOperationNode())
        if len(cond_nodes) != 0:
            checkers.append(Checker(cond_nodes))
        checkers.append(oper)
        return checkers 
    
    def __get_conditions_nodes(self, sc_spec):
        const_nodes = []
        rels = session.search11_f_a_a_a_a_a_f_a_f_a_f(sc_spec, 
                                                      sc.SC_A_CONST|sc.SC_POS, sc.SC_N_CONST, 
                                                      sc.SC_A_CONST|sc.SC_POS, sc.SC_N_CONST,
                                                      sc.SC_A_CONST|sc.SC_POS, sc_keys.n_2,
                                                      sc.SC_A_CONST|sc.SC_POS, sc_keys.n_1,
                                                      sc.SC_A_CONST|sc.SC_POS, keys.rel_runing_condition)
        if rels is not None:
            for rel in rels:
                els = session.search3_f_a_a(rel[4], sc.SC_A_CONST|sc.SC_POS, sc.SC_N_CONST)
                if els is not None:
                    for el in els:
                        const_nodes.append(el[2])
        return const_nodes
        
    def __create_worker(self, queue, wait_task):
        worker = Worker(queue, self.modules, wait_task)
        self.workers.append(worker)
        worker.start()
    
    def start(self, wait_task=True, wait_threads=False):
        for i in range(self.max_workers):
            if wait_task or not self.queue.empty():
                self.__create_worker(self.queue, wait_task)
                time.sleep(self.acceleration)
 
        if wait_threads:
            for worker in self.workers:
                worker.join()
        
    def stop(self):
        print "[Questions] Shutdown"
        sc.ScOperationActSetMember.__del__(self)
        for worker in self.workers:
            worker.running = False
        
    def activateImpl(self, _paramSystem, _tmpSegment):
        """Activate implementation.
        """
        print "[Questions] Add new questions"
        self.queue.put(_paramSystem)
        
class Worker(threading.Thread):
    running = True
 
    def __init__(self, queue, modules, wait_task):
        super(Worker, self).__init__()
        print "[worker] start"
        self.modules = modules
        self.wait_task = wait_task
        self.queue = queue
 
    def run(self):
        while self.running:
            try:
                question = self.queue.get(self.wait_task, 0.1)
                nodes = session.search5_f_a_a_a_f(sc_keys.questions.initiated,
                                                  sc.SC_A_CONST | sc.SC_POS,
                                                  sc.SC_N_CONST,
                                                  sc.SC_A_CONST | sc.SC_POS,
                                                  question)
                if nodes is not None:
                    question = nodes[0][2]
                else:
                    continue
                #print "[worker] get %s" % session.get_idtf(question)
                self.markAsActive(question)
                # search needed operation
                for oper, checkers in self.modules:
                    # check question
                    check = True
                    for checker in checkers:
                        #print checker
                        if not checker.checking(question):
                            check = False
                    if check:
                        oper = oper()
                        result = oper.running(question)
                        if result is not None:
                            if len(result) != 0:
                                self.makeAnswer(question, result)
                                session.gen3_f_a_f(segment, sc_keys.questions.finished, question, sc.SC_A_CONST|sc.SC_POS)
                                break
                self.markAsFinish(question)
            except Queue.Empty:
                time.sleep(0.1)
                if not self.wait_task:
                    self.running = False
            except:
                self.markAsFinish(question)
                bug_report()
                
    def markAsActive(self, question):
        session.gen3_f_a_f(segment, sc_keys.questions.active, question, sc.SC_A_CONST | sc.SC_POS)
        
    def markAsFinish(self, question):
        res = session.search3_f_a_f(sc_keys.questions.active, sc.SC_ARC, question)
        if res is not None:
            session.erase_el(res[0][1])
            if len(res) is 1:
                session.gen3_f_a_f(segment, sc_keys.questions.finished, question, sc.SC_A_CONST | sc.SC_POS)
                    
    def makeAnswer(self, question, answer):
        if len(answer) is 0:
            return
        print "[Questions] Build answer"
        # создаем множество для ответа
        # создаем связку отношения между ответом и множеством ответа
        els = session.gen11_f_a_a_a_a_a_f_a_f_a_f(segment, question, 
                                            sc.SC_A_CONST|sc.SC_POS, sc.SC_N_CONST,
                                            sc.SC_A_CONST|sc.SC_POS, sc.SC_N_CONST,
                                            sc.SC_A_CONST|sc.SC_POS, sc_keys.n_1,
                                            sc.SC_A_CONST|sc.SC_POS, sc_keys.n_2,
                                            sc.SC_A_CONST|sc.SC_POS, sc_keys.info.stype_sheaf)
        el = els[4]
        sheaf_node = els[2]
        # добавляем узлы ответа в множество
        answer = cantorSet(answer)
        for item in answer:
            session.gen3_f_a_f(segment, el, item, sc.SC_A_CONST | sc.SC_POS)
        # задаем отношение как "ответ*"
        session.gen3_f_a_f(segment, sc_keys.questions.nrel_answer, sheaf_node, sc.SC_A_CONST | sc.SC_POS)
        session.gen3_f_a_f(segment, sc_keys.questions.succesful, question, sc.SC_A_CONST | sc.SC_POS)
                    
class Checker(object):
    const_nodes = []
    is_empty = True
    def __init__(self, const_nodes, incl = True):
        self.const_nodes = const_nodes
        self.incl = incl
    
    def checking(self, question):
        if self.incl:
            return session.checkIncToSets(question, self.const_nodes)
        else:
            return not session.checkIncToSets(question, self.const_nodes)

def cantorSet(set):
    res = []
    for el1 in set:
        inis = False
        for el2 in res:
            if el1.this == el2.this: inis = True
        if not inis: res.append(el1)
    return res        

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