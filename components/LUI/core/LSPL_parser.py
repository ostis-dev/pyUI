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

import LSPL_parse_bin.LsplParser as Lspl
import components.LUI.keynodes as keynodes

#import parser
from parser import Parser

import sc_core.pm as sc
import sc_core.constants as sc_constants
import suit.core.kernel as sc_core
import suit.core.sc_utils as sc_utils

session = sc_core.Kernel.session()
session.open_segment(u"/etc/questions")
session.open_segment(u"/etc/com_keynodes")
session.open_segment(u"/seb/planimetry")
segment = sc_core.Kernel.segment()
kernel = sc_core.Kernel.getSingleton()
        
import os

#class LsplParser(parser.Parser):
class LsplParser(Parser):
    def __init__(self):
        super(LsplParser, self).__init__()
        print "[init] LUI core"
        self.parser = None
        self.lastQuestion = None
        try:
            self.loadParser()
        except:
            print "[fail] load LsplParser"
        self.loadPatterns()
        
    def loadParser(self):
        rml_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),"LSPL_parse_bin")
        Lspl.setRMLpath(rml_dir)
        self.parser = Lspl.LsplParser()
        self.parser.loadMorphology()
        self.nsID = self.createNewNamespace()
        
    def loadPatterns(self):
        self.questionPatterns = {}
        it = session.create_iterator(session.sc_constraint_new(sc_constants.CONSTR_3_f_a_a,
                                                           keynodes.questions_types,
                                                           sc.SC_A_CONST | sc.SC_POS,
                                                           sc.SC_CONST | sc.SC_NODE
                                                           ), True)
        #questions = []
        print "[scan questions]"
        while not it.is_over():
            #questions.append(it.value(2))
            qIdtf = session.get_idtf(it.value(2))
            print "[scan] %s" % qIdtf
            syns = sc_utils.searchBinPairsAttrToNode(session,it.value(2),keynodes.nrel_identification,sc.SC_CONST)
            altqIdtf = None
            for syn in syns:
                it3 = session.create_iterator(session.sc_constraint_new(sc_constants.CONSTR_5_f_a_a_a_f,
                                                                        syn,
                                                                        sc.SC_A_CONST | sc.SC_POS,
                                                                        sc.SC_CONST | sc.SC_NODE,
                                                                        sc.SC_A_CONST | sc.SC_POS,
                                                                        keynodes.rrel_nl_idtf
                                                                        ), True)
                while not it3.is_over():
                    altqIdtf = session.get_content_str(it3.value(2))
                    it3.next()
            els = sc_utils.searchBinPairsAttrToNode(session,it.value(2),keynodes.nrel_pattern,sc.SC_CONST)
            for el in els:
                it2 = session.create_iterator(session.sc_constraint_new(sc_constants.CONSTR_3_f_a_a,
                                                           el,
                                                           sc.SC_A_CONST | sc.SC_POS,
                                                           sc.SC_CONST | sc.SC_NODE
                                                           ), True)
                while not it2.is_over():
                    if altqIdtf is None: altqIdtf = "XXX"
                    self.questionPatterns[altqIdtf] = it.value(2)
                    pattern = altqIdtf + " = " + session.get_content_str(it2.value(2))
                    self.addNewPattern(pattern)
                    it2.next()
            it.next()
        
    def addNewPattern(self, pattern, namespace = -1):
        if namespace is -1: namespace = self.nsID
        print "[register pattern] %s" % pattern
        self.parser.addPatternToNamespace(namespace, unicode(pattern).encode("CP1251"))
        
    def createNewNamespace(self):
        ident = self.parser.createNewNamespace()
        self.addNewPattern("TARGET = {N}N", ident)
        self.addNewPattern("TARGET = [A]N", ident)
        return ident
    
    def deleteNamespace(self, namespace = -1):
        if namespace is -1: namespace = self.nsID
        self.parser.eraseNamespace(namespace)
        
    def parseQuestion(self, question, namespace = -1):
        if namespace is -1: namespace = self.nsID
        res = self.parser.parseTextInNamespace(namespace, question)
        q = res.getQuestionVariants()
        o = res.getObjectsVariants()
        return (q, o)
    
    # main input function 
    def run(self):
        if not self.isRun: return
        print "[NL question] %s" % self.q_text
        questions, targets = self.parseQuestion(self.q_text)
        if not self.isRun: return
        self.makeQuestion(questions, targets)
        
    def makeQuestion(self, listQuestions, listTargets):
        questions = []
        targets = []
        for question in listQuestions:
            if self.questionPatterns.has_key(question):
                print "[Question] = %s" % question
                questions.append(self.questionPatterns[question])
        for target in listTargets:
            if self.targets.has_key(target):
                print "[Object] = %s" % target
                targets.append(self.targets[target][0][0])
        if len(questions) is not 0 and len(targets) is not 0:
            self.lastQuestion = self.buidQuestion(questions, targets)
            print self.lastQuestion
        #else:
        #    print "[Error] Bad NL question (q: %s, o: %s)" % (questions, targets)