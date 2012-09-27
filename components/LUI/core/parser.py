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

import sc_core.pm as sc
import sc_core.constants as sc_constants
import suit.core.kernel as sc_core
import suit.core.sc_utils as sc_utils
import suit.core.keynodes as sc_key

import components.LUI.keynodes as keynodes

session = sc_core.Kernel.session()
session.open_segment(u"/etc/questions")
session.open_segment(u"/etc/com_keynodes")
session.open_segment(u"/seb/planimetry")
session.open_segment(u"/seb/rus")
session.open_segment(u"/seb/bel")
segLingv = session.open_segment(u"/seb/lingv")
segment = sc_core.Kernel.segment()
kernel = sc_core.Kernel.getSingleton()

import threading
import re

# Magic Numbers.... I ugly, I know it =((
badWordsKoef = {'утв':[0.6,6.0],'опр':[0.4,6.0]}
koef = 0.8
baseKoef = 1.1

badWordsKoef_ = badWordsKoef.copy()
badWordsKoef = {}
for k in badWordsKoef_.keys():
    badWordsKoef[k.decode('utf-8').encode('cp1251')] = badWordsKoef_[k]

#class Parser(object):
class Parser(threading.Thread):
    def __init__(self, *args):
        super(Parser, self).__init__(*args)
        self.isRun = False
        global targets
        self.targets = targets
        
    def start_process(self, q_str, stop_func):
        self.stop_func = stop_func
        self.isRun = True
        self.q_text = q_str
        self.start()
    
    def run(self):
        pass
    
    def buidQuestion(self, questionNode, objectsNodes):
        print "[Parser] Buid question"
        self.stop_func()
        return buildUserAtomQuestion(questionNode, objectsNodes)
    
    def setUsedLanguage(self, lang):
        setUsedLanguage(lang)
    
def setUsedLanguage(usedLang):
    langs = session.search3_f_a_a(keynodes.used_lang,sc.SC_A_CONST|sc.SC_POS,sc.SC_N_CONST)
    if langs is not None:
        for lang in langs:
            session.erase_el(lang[1])
    session.gen3_f_a_f(segLingv,keynodes.used_lang,usedLang,sc.SC_A_CONST|sc.SC_POS)
    print "[Parser] Set language to %s" % session.get_idtf(usedLang)
    

def getAnswerByQuestion(sc_question):
    _a = sc.SC_A_CONST|sc.SC_POS
    answer_rel = session.search11_f_a_a_a_a_a_f_a_f_a_f(sc_question, _a, sc.SC_N_CONST, 
                                                         _a, sc.SC_N_CONST,
                                                         _a, sc_key.n_1, _a, sc_key.n_2, 
                                                         _a, sc_key.questions.nrel_answer)
    res = []
    if answer_rel is None: return None
    for ans in answer_rel:
        res.append(ans[4]) 
    if len(res) is 0: return None
    else: return res
    
def buildUserAtomQuestion(sc_qustions, sc_q_objects):
    # узел вопроса
    q_node = sc_utils.createNodeElement(session, segment, sc.SC_CONST)
    # добавляем во множество вопрос
    session.gen3_f_a_f(segment, sc_key.questions.question, q_node, sc.SC_A_CONST | sc.SC_POS)
    # добавляем во множество атомарный вопрос
    session.gen3_f_a_f(segment, sc_key.questions.atom, q_node, sc.SC_A_CONST | sc.SC_POS)
    # добавляем типы вопросов
    for sc_q in sc_qustions:
        session.gen3_f_a_f(segment, sc_q, q_node, sc.SC_A_CONST | sc.SC_POS)
    # добавляем объекты вопроса
    for sc_o in sc_q_objects:
        session.gen3_f_a_f(segment, q_node, sc_o, sc.SC_A_CONST | sc.SC_POS)
    # добавляем автора (пользователь)
    authors_node = sc_utils.createNodeElement(session, segment, sc.SC_CONST)
    sc_utils.createPairPosPerm(session, segment, authors_node, 
                               sc_core.Kernel.getSingleton().getUserAddr(), sc.SC_CONST)
    authors_pair_sheaf = sc_utils.createPairBinaryOrient(session, segment, 
                               q_node, authors_node, sc.SC_CONST)
    sc_utils.createPairPosPerm(session, segment, sc_key.common.nrel_authors, 
                               authors_pair_sheaf, sc.SC_CONST)
    # добавляем окна для вывода    
    output_node = sc_utils.createNodeElement(session, segment, sc.SC_CONST)
    
    
    output_count = 0
    it = session.create_iterator(session.sc_constraint_new(sc_constants.CONSTR_3_f_a_a,
                                                       sc_key.ui.set_output_windows,
                                                       sc.SC_ARC,
                                                       0), True)
    while not it.is_over():
        sc_utils.createPair(session, segment, output_node, it.value(2), session.get_type(it.value(1)))
        output_count += 1
        it.next()
       
    if output_count == 0:
        sc_utils.createPairPosPerm(session, segment, output_node, kernel.getMainWindow()._getScAddr(), sc.SC_CONST )
    #sc_utils.copySet(session, sc_key.ui.set_output_windows, output_node, segment)
    # link output windows set to question
    output_sheaf = sc_utils.createPairBinaryOrient(session, segment, output_node, 
                                q_node, sc.SC_CONST)
    sc_utils.createPairPosPerm(session, segment, sc_key.ui.nrel_set_of_output_windows, 
                                output_sheaf, sc.SC_CONST) 
    # initiate question
    sc_utils.createPairPosPerm(session, segment, sc_key.questions.initiated, 
                               q_node, sc.SC_CONST)
    return q_node

# load in global var targets 
# all names of object and object itself
def loadTargets():
    global targets
    targets = {}
    for key in keynodes.listOfObjects:
        it = session.create_iterator(session.sc_constraint_new(sc_constants.CONSTR_3_f_a_a,
                                                               key,
                                                               sc.SC_A_CONST | sc.SC_POS,
                                                               sc.SC_CONST | sc.SC_NODE
                                                               ), True)
        while not it.is_over():
            idtf = session.get_idtf(it.value(2)).lower()
            targets[idtf] = [[it.value(2),baseKoef]]
            #print "[Object basic] %s" % idtf
            syns = sc_utils.searchBinPairsAttrToNode(session,it.value(2),keynodes.nrel_identification,sc.SC_CONST)
            for syn in syns:
                it2 = session.create_iterator(session.sc_constraint_new(sc_constants.CONSTR_3_f_a_a,
                                                                        syn,
                                                                        sc.SC_A_CONST | sc.SC_POS,
                                                                        sc.SC_CONST | sc.SC_NODE
                                                                        ), True)
                while not it2.is_over():
                    idtf = session.get_content_str(it2.value(2))
                    if idtf is not None: targets[idtf.lower()] = [[it.value(2),baseKoef]]
                    #print "[Object alter] %s" % idtf
                    it2.next()
            it.next()
            
def unique(seq):
    result = []
    seen = set()
    for elem in seq:
        key = hash(str(elem.this))
        if key not in seen:
            seen.add(key)
            result.append(elem)
    return result
            
# update global var targets
# add word forms from dictionary
def updateTargets():
    scWordForms = session.find_keynode_full_uri(u"/seb/lingv/словоформы*")
    
    setWordsForms = session.search3_f_a_a(scWordForms,sc.SC_A_CONST | sc.SC_POS, sc.SC_CONST | sc.SC_NODE)
    
    global linksToWords
    global AllWords
    linksToWords = {}
    AllWords = []
    
    for setWordForms in setWordsForms:
        wordForms = session.search3_f_a_a(setWordForms[2],sc.SC_A_CONST | sc.SC_POS, sc.SC_CONST | sc.SC_NODE)
        words = []
        for wordForm in wordForms:
            idtf = session.get_idtf(wordForm[2]).decode('cp1251').encode('utf-8')
            idtf = re.search('(?<=слово\()[^\)]+', idtf).group()
            idtf = idtf.decode('utf-8').encode('cp1251').lower()
            #print idtf
            words.append(idtf)
        AllWords.append(words)
        for word in words:
            linksToWords[word] = words
            
#    f = open('c:/tmp2.txt','w')
#    for k in linksToWords.keys():
#        outstr = k + " :"
#        for word in linksToWords[k]:
#            outstr += " " + word
#        outstr += "\n" 
#        f.write(outstr)
#    f.close()
    megaKeys = []
    global targets
    updTargets = targets.copy()
    # обрабатываем каждую цель
    keys = targets.keys()
    for key in keys:
        # добавить замену "левых" символов на пробелы
        # убрать повторяющиеся пробелы 
        tKey = ' '.join(re.sub('[\(\)\*\.,]', ' ', key).split())
        # если это словосочетание разбиваем на слова
        subKeys = tKey.split()
        
# WARNING!!!! MAGIC CODE!!!!        
        # высчитываем коэффициент
        kf = koef / len(subKeys)
        if len(subKeys) == 1: kf = baseKoef
        for k in badWordsKoef.keys():
            if k in subKeys:
                kf = badWordsKoef[k][0] / len(subKeys)
# I promise do not use magic code any more.... 
# <}:-| =======|X     ->=O>         O_o -OMG!
                
        # обрабатываем каждое слово
        for subKey in subKeys:
            #print subKey
            #megaKeys.append(subKey)
            
            # DAMN.. Another spell... =((
            if badWordsKoef.has_key(subKey):
                kf = kf * badWordsKoef[subKey][1] / badWordsKoef[subKey][0]
                  
            # ищем словоформы для этого слова
            if linksToWords.has_key(subKey):
                megaKeys.append(subKey)
                # нашли словоформы, надо добавить новые в список целей
                #print subKey + " -in- " + key
                # смотрим каждую словоформу
                for newWord in linksToWords[subKey]:
                    # если ее нет с списке целей, добавляем пустой масив
                    if not updTargets.has_key(newWord): updTargets[newWord] = []
                    # добавляем узлы к найденой цели
                    updTargets[newWord] += [[targets[key][0][0],kf]]
                    #targets[newWord]  = unique(targets[newWord])
            else:
                # если ее нет с списке целей, добавляем пустой масив
                if not updTargets.has_key(subKey): updTargets[subKey] = []
                # добавляем узлы к найденой цели
                updTargets[subKey] += [[targets[key][0][0],kf]]
    targets = updTargets
    
#    f = open('c:/tmp3.txt','w')
#    for k in megaKeys:
#        outstr = k
#        outstr += "\n" 
#        f.write(outstr)
#    f.close()    
    
    
#    f = open('c:/tmp4.txt','w')
#    for key in targets.keys():
#        outstr = key + " :"
#        for node in targets[key]:
#            outstr += " <> " + session.get_idtf(node)
#        outstr += "\n" 
#        f.write(outstr)
#    f.close()
    
    #for key in targets.keys():
    #    print key + " : " + str(len(targets[key]))
                
loadTargets()
updateTargets()