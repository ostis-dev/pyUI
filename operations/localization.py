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
Created on 11.06.2011

@author: Denis Koronchik
'''

from suit.core.kernel import Kernel
from suit.core.event_handler import ScEventHandlerSetMember
import suit.core.keynodes as keynodes

def initialize():
    kernel = Kernel.getSingleton()
    kernel.registerOperation(ScEventHandlerSetMember(u"operation that update UI after localization change",
                                                     keynodes.ui.translate_lang_current,
                                                     translation_changed, []))

def shutdown():
    pass

def translation_changed(_params, _segment):
    kernel = Kernel.getSingleton()
    kernel.translationChanged()