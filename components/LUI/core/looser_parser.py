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

#import parser
#from parser import Parser
import parser

import sc_core.pm as sc
import sc_core.constants as sc_constants
import suit.core.kernel as sc_core
import suit.core.sc_utils as sc_utils
session = sc_core.Kernel.session()
session.open_segment(u"/etc/questions")
session.open_segment(u"/etc/com_keynodes")
session.open_segment(u"/seb/planimetry")
session.open_segment(u"/seb/rus")
session.open_segment(u"/seb/bel")
session.open_segment(u"/seb/lingv")
segment = sc_core.Kernel.segment()
kernel = sc_core.Kernel.getSingleton()

import components.LUI.keynodes as keynodes

import re

#class LooserParser(parser.Parser):
class LooserParser(parser.Parser):
    def __init__(self):
        super(LooserParser, self).__init__()
        global patterns
        self.patterns = patterns
        print "[init] LooserParser"
        
    def run(self):
        # self.q_text
        # self.targets
        #while self.isRun:
        #    pass
#        f = open('c:/tmp5.txt','w')
#        for key in self.targets.keys():
#            outstr = key + "\n"
#            f.write(outstr)
#        f.close()
#        return
        print "[LooserParser] I find next: "
        print "[LooserParser] Input: %s" % self.q_text
        #for word in self.findTargetInQuestion(self.q_text):
        targets = self.findTheMostCloser(self.q_text,self.targets,1)
        for word in targets:
            #print word
            print "[LooserParser] target: " + str(word[0]) + " <> " + str(session.get_idtf(word[1])) + " <> " + str(word[2])
        
        questions = self.findTheMostCloser(self.q_text,self.patterns,1)
        for word in questions:
            #print word
            print "[LooserParser] question: " + str(word[0]) + " <> " + str(session.get_idtf(word[1])) + " <> " + str(word[2])
        
        target = self.findMax(targets,0)[1]
        question = self.findMax(questions,0)[1]
        if target[1] is None or question[1] is None: return
        #print target
        #print question
        
        #language stored in question[2]
        langsMap = {}
        for lang in question[2]:
            if not langsMap.has_key(lang):
                langsMap[lang] = 0
            langsMap[lang] += 1
        maxCount = -1
        maxLang = None
        for k in langsMap.keys():
            if langsMap[k] > maxCount:
                maxLang = k
                
        usedLang = keynodes.langs[maxLang]
        self.setUsedLanguage(usedLang)
        
        self.buidQuestion([question[1]], [target[1]])
        print "[LooserParser] OK, I'm Looser"
        
    def findTheMostCloser(self, input_string, targets_list, count = 1):
        findedTargets = []
        # чистим строку от лишних символов
        nStr = ' '.join(re.sub('[\(\)\*\.,]', ' ', input_string).split())
        # разбиваем строку на слова, удирая повторяющиеся пробелы
        words = nStr.split()
        # ищем каждое слово в списке целей
        for word in words:
            if targets_list.has_key(word):
                # если таковое есть запоминаем его
                # составляем список всех объектов на которые ссылаются найденные цели
                findedTargets += targets_list[word]
                #print targets_list[word]
        # подсчитываем количество упоминаний на каждое понятие из БЗ
        scNodeCounts = {}
        # перебираем все элементы
        for target in findedTargets:
            # если элемента нет в хэше, создаем начальный элемент
            #print target[0]
            if not scNodeCounts.has_key(hash(str(target[0].this))):
                scNodeCounts[hash(str(target[0].this))] = [0.0, target[0],[]]                    
            # увеличиваем счетчик на коэфициент данного элемента
            scNodeCounts[hash(str(target[0].this))][0] += target[1] 
            if len(target)>2:
                scNodeCounts[hash(str(target[0].this))][2] += target[2:]
        # ищем элементы с наибольшим количеством упоминаний
        maxCountElement = []
        for i in range(count):
            maxCountElement += [[0.0,None,[]]]
        for k in scNodeCounts.keys():
            # если элемент имеет равное число упоминаний
            [minNum, minEl] = self.findMin(maxCountElement, 0)
            #print minNum
            if minEl[0] < scNodeCounts[k][0]:
                maxCountElement[minNum] = scNodeCounts[k]
            
#        searchedWords = []
#        for node in maxCountElement:
#            if node[1] is None: continue
#            searchedWords.append(session.get_idtf(node[1]))
#        return searchedWords
        return maxCountElement
    
    def findMin(self, els, el_num):
        minEl = els[0]
        minNum = 0
        for i in range(1,len(els)):
            if minEl[el_num] > els[i][el_num]:
                minEl = els[i]
                minNum = i
        return [minNum, minEl]
    
    def findMax(self, els, el_num):
        minEl = els[0]
        maxNum = 0
        for i in range(1,len(els)):
            if minEl[el_num] < els[i][el_num]:
                minEl = els[i]
                maxNum = i
        return [maxNum, minEl]
        
patterns = {}
koef = 1.0   

def loadPatterns():
    sentanses = []
    global patterns
    # просмотр всех классов вопросов 
    questions = session.search3_f_a_a(keynodes.questions_class, sc.SC_A_CONST|sc.SC_POS, sc.SC_CONST|sc.SC_NODE)
    for question in questions:
        # поиск отношения трансляции
        transls = session.search11_f_a_a_a_a_a_f_a_f_a_f(question[2], sc.SC_A_CONST|sc.SC_POS, sc.SC_CONST|sc.SC_NODE,
                                               sc.SC_A_CONST|sc.SC_POS, sc.SC_CONST|sc.SC_NODE,
                                               sc.SC_A_CONST|sc.SC_POS, keynodes.nsm.attr[1],
                                               sc.SC_A_CONST|sc.SC_POS, keynodes.nsm.attr[0],
                                               sc.SC_A_CONST|sc.SC_POS, keynodes.nrel_translation)
        if transls is None: continue
        # если оно есть, просмотр самих трансляций
        for transl in transls:
            phrases = session.search3_f_a_a(transl[4], sc.SC_A_CONST|sc.SC_POS, sc.SC_CONST|sc.SC_NODE)
            for phrase in phrases:
                # получение контента трансляции
                str_phrase = session.get_content_str(phrase[2])
                if str_phrase is None: continue
                # если оно есть, определяем язык
                lang = -1
                for k in keynodes.langs.keys():
                    r = session.search3_f_a_f(keynodes.langs[k], sc.SC_A_CONST|sc.SC_POS, phrase[2])
                    if r is not None: lang = k
                # добавляем в список:
                # узел вопроса, фразу трансляции, язык трансляции
                sentanses.append([question[2], str_phrase, lang])
    #for k in parser.linksToWords.keys():
    #    print k
    # перебираем все найденные трансляции
    for s in sentanses:
        # удаляем лишнее, разбиваем на слова
        sent = ' '.join(re.sub('[\(\)\*\.,?]', ' ', s[1]).split())
        words = sent.split()
        k = koef / len(words)
        # перебираем слова
        for word in words:
            # ищем их в словаре
            if parser.linksToWords.has_key(word):
                # добавляем каждую словоформу
                for altWord in parser.linksToWords[word]:
                    addWordToTarget(altWord,s[0],k,s[2]) 
            else:
                addWordToTarget(word,s[0],k,s[2])
    #print "words count "+str(len(patterns.keys()))
#    f = open('c:/patterns.txt','w')
#    f.write(str(patterns))
#    f.close()   

def addWordToTarget(word,q,k,l):
    global patterns
    if patterns.has_key(word):
        patterns[word] += [[q,k,l]]
    else:
        patterns[word] = [[q,k,l]]
    

loadPatterns()