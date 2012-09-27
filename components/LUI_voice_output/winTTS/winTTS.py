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
Created on 09.12.10
@author:  Zhitko V.A. Shukov A.S. Penkrat M.V.
'''

import threading
import time    
import sys
import pyttsx
import pythoncom

def say(expr, lang = 'rus'):
    print "[winTTS] %s" % expr
    SpeechGui(expr).start()


class SpeechGui(threading.Thread):
    text = 0
    lang = 0
    voice = 0
    def __init__(self, text): 
           self.text = text    
           #self.lang = lang
           #self.voice = voice
           threading.Thread.__init__(self)
    def run(self):
           pythoncom.CoInitialize()
           engine = pyttsx.init()
           #voices = engine.getProperty('voices')
           #for voice in voices:
           #    engine.setProperty('voice', voice.id)
           #    engine.say(self.text)
           engine.say(self.text)
           engine.runAndWait()