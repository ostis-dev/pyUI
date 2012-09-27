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
Created on 03.11.10
@author:  Zhitko V.A.
'''

import suit.core.kernel as core
session = core.Kernel.session()

import suit.core.keynodes as keynodes

langsWords = {
         0 : session.find_keynode_full_uri(u"/seb/lingv/слова русского языка"),
         1 : session.find_keynode_full_uri(u"/seb/lingv/слова белорусского языка")
}

langs = {
         0 : session.find_keynode_full_uri(u"/etc/com_keynodes/Русский язык"),
         1 : session.find_keynode_full_uri(u"/etc/com_keynodes/Белорусский язык")
}

rus_lang = langs[0]
bel_lang = langs[1]

used_lang = session.find_keynode_full_uri(u"/seb/lingv/используемый язык")

questions_class = session.find_keynode_full_uri(u"/etc/questions/класс вопроса")

questions_types =   session.find_keynode_full_uri(u"/etc/questions/тип вопроса")

nrel_pattern      =   session.find_keynode_full_uri(u"/etc/questions/ЕЯ представление*")
nrel_identification =   session.find_keynode_full_uri(u"/etc/com_keynodes/идентификация*")
nrel_translation =   session.find_keynode_full_uri(u"/etc/com_keynodes/трансляция*")

rrel_nl_idtf    =   session.find_keynode_full_uri(u"/etc/questions/ЕЯ идентификатор_")

listOfObjects   =   [keynodes.info.stype_struct,
                     keynodes.info.stype_concept_norel,
                     session.find_keynode_full_uri(u"/seb/planimetry/Предметная область Геометрии Евклида"),
                     session.find_keynode_full_uri(u"/seb/planimetry/Предметная область Геометрия Евклида"),
                     ]

class patterns:
    ScToTextPatterns    =   session.find_keynode_full_uri(u"/ui/lui/шаблоны генерации текста")
    attr_inputPattern   =   session.find_keynode_full_uri(u"/ui/lui/входящий шаблон_")
    attr_outputPattern  =   session.find_keynode_full_uri(u"/ui/lui/выходящий шаблон_")
    attr_inputParams    =   session.find_keynode_full_uri(u"/ui/lui/входящие параметры_")
    attr_multi          =   session.find_keynode_full_uri(u"/ui/lui/множественное вхождение_")

class production_eng:
    engine      =   session.find_keynode_full_uri(u"/proc/scl/keynode/production_engine")
    rel_impl    =   session.find_keynode_full_uri(u"/proc/scl/keynode/impl*")
    attr_if     =   session.find_keynode_full_uri(u"/proc/scl/keynode/if_")
    attr_then   =   session.find_keynode_full_uri(u"/proc/scl/keynode/then_")
    
class nsm:
    goals           =   session.find_keynode_full_uri(u"/proc/agents/nsm/keynode/goals")
    attr_confirmed  =   session.find_keynode_full_uri(u"/proc/agents/nsm/keynode/confirmed_")
    attr_active     =   session.find_keynode_full_uri(u"/proc/agents/nsm/keynode/active_")
    attr_confirm_   =   session.find_keynode_full_uri(u"/proc/agents/nsm/keynode/confirm_")
    attr_search     =   session.find_keynode_full_uri(u"/proc/agents/nsm/keynode/search_")
    attr_searched   =   session.find_keynode_full_uri(u"/proc/agents/nsm/keynode/searched_")
    attr_generate   =   session.find_keynode_full_uri(u"/proc/agents/nsm/keynode/generate_")
    attr_generated  =   session.find_keynode_full_uri(u"/proc/agents/nsm/keynode/generated_")
    result          =   session.find_keynode_full_uri(u"/proc/agents/nsm/keynode/Result")
    
    nsm_command         =   session.find_keynode_full_uri(u"/proc/agents/nsm/keynode/nsm_command")
    attr_nsm_command    =   session.find_keynode_full_uri(u"/proc/agents/nsm/keynode/nsm_command_")
    attr_nsm_command_pattern    =   session.find_keynode_full_uri(u"/proc/agents/nsm/keynode/nsm_command_pattern_")
    attr_nsm_command_elem       =   session.find_keynode_full_uri(u"/proc/agents/nsm/keynode/nsm_command_elem_")
    attr_nsm_command_comment    =   session.find_keynode_full_uri(u"/proc/agents/nsm/keynode/nsm_command_comment_")
    attr_nsm_command_shortname  =   session.find_keynode_full_uri(u"/proc/agents/nsm/keynode/nsm_command_shortname_")
    
    attr = {
          0:session.find_keynode_full_uri(u"/proc/keynode/1_"),
          1:session.find_keynode_full_uri(u"/proc/keynode/2_"),
          2:session.find_keynode_full_uri(u"/proc/keynode/3_"),
          3:session.find_keynode_full_uri(u"/proc/keynode/4_"),
          4:session.find_keynode_full_uri(u"/proc/keynode/5_"),
          5:session.find_keynode_full_uri(u"/proc/keynode/6_"),
          6:session.find_keynode_full_uri(u"/proc/keynode/7_"),
          7:session.find_keynode_full_uri(u"/proc/keynode/8_"),
          8:session.find_keynode_full_uri(u"/proc/keynode/9_"),
          9:session.find_keynode_full_uri(u"/proc/keynode/10_")
          }
    