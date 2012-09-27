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

langs = {
         session.find_keynode_full_uri(u"/etc/com_keynodes/Русский язык") : 'rus',
         session.find_keynode_full_uri(u"/etc/com_keynodes/Белорусский язык") : 'bel'
}

class ui:
    voice =   session.find_keynode_full_uri(u"/ui/core/VOICE")
    activeTTS = session.create_el_full_uri(u"/ui/lui/activeTTS")[1]
    regTTS = session.create_el_full_uri(u"/ui/lui/regTTS")[1]
    
    menuTTS = session.find_keynode_full_uri(u"/ui/menu/tts_languages")