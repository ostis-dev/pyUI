
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
Created on 03.06.11
@author:  Zhitko V.A.
'''

import suit.core.keynodes as sc_key
import suit.core.kernel as core

from suit.core.objects import Factory

import sc_core.pm as pm

kernel = core.Kernel.getSingleton()
session = core.Kernel.session()
session.open_segment(u"/ui/lui")
session.open_segment(u"/ui/menu")

import sc2voice
import keynodes

_version_   =   "0.0.1"
_name_      =   "LUI Voice Output Manager"

import SSRLab.sui as SSRLab
import winTTS.winTTS as winTTS

global modules
modules = {
           "SSRLab":SSRLab,
           "winTTS":winTTS
           }

default = "SSRLab"

def getModules():
    global modules
    return modules

#class Modules:
#    def getModules():
#        global modules
#        return modules

def initialize():
    print "[init] LUI Voice Output Manager"
    #regTranslators()
    for key in modules.keys():
        regTTS(key)
    return

def shutdown():
    print "[shutdown] LUI Voice Output Manager"
    return

def addToMenu(name):
    segment = session.open_segment(u"/ui/menu")
    session.gen3_f_a_f(segment, keynodes.ui.menuTTS, name, pm.SC_A_CONST|pm.SC_POS|pm.SC_ACTUAL) 
#    tts = session.create_el_full_uri(u"/ui/menu/%s" % name)
#    print tts
#    if tts[0]:
#        print "add menu"
#        session.gen3_f_a_f(segment, keynodes.ui.menuTTS, tts[1], pm.SC_A_CONST|pm.SC_POS|pm.SC_ACTUAL) 

def regTTS(name):
    segment = session.open_segment(u"/ui/lui")
    tts = session.create_el_full_uri(u"/ui/lui/%s" % name)
    #print tts
    if tts[0]:
        session.gen3_f_a_f(segment, keynodes.ui.regTTS, tts[1], pm.SC_A_CONST|pm.SC_POS|pm.SC_ACTUAL)  
        #addToMenu(name) 
        addToMenu(tts[1])
    if default == name:
        print "LUI set default TTS"
        session.gen3_f_a_f(segment, keynodes.ui.activeTTS, tts[1], pm.SC_A_CONST|pm.SC_POS|pm.SC_ACTUAL)
    return tts[1]

#from components.text.text_init import viewer_creator

def regTranslators():
    global sc2voice_factory
    sc2voice_factory = Factory(sc2voice_creator)
    kernel.registerTranslatorFactory(sc2voice_factory, [sc_key.ui.format_sc], [keynodes.ui.voice])
    
#    view_factory = Factory(viewer_creator)
#    kernel.registerViewerFactory(view_factory, [keynodes.ui.voice])
    
    return

def sc2voice_creator():
    return sc2voice.TranslatorSc2Voice(modules)