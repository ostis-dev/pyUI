
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
import suit.core.keynodes as sc_key
from suit.core.objects import Factory

import sc2text.sc2text as sc2text

import os
import gui.gui as GUI
import core.core as Parsers
import htk_rus.HTKm as HTKrus
import htk_bel.HTKm as HTKbel

_version_   =   "0.0.0"
_name_      =   "LUI"

kernel = core.Kernel.getSingleton()

def initialize():
    print "[init] LUI"
    
    global transc2text_factory
    transc2text_factory = Factory(sc2text_creator)
    kernel.registerTranslatorFactory(transc2text_factory, [sc_key.ui.format_sc], [sc_key.ui.format_string])
        
    global parsers
    parsers = Parsers.Core()
    
    global gui
    gui = GUI.UI(parsers.parse)
    
    #HTKrus.start(gui.setText)
    HTKbel.start(gui.setText)
    
    return
    
def shutdown():
    print "[shutdown] LUI"
    #if HTKrus.isRun: HTK.stop()
    if HTKbel.isRun: HTK.stop()

    # unregister components
    global transc2text_factory
    kernel.unregisterTranslatorFactory(transc2text_factory)
    return
    
def _resourceLocations():
    """Specified resources for a operations module
    """
    res = []       
    return res

def sc2text_creator():
    return sc2text.TranslatorSc2Text()