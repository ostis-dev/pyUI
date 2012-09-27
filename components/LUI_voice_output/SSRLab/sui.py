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
Created on 08.12.10
@author:  Zhitko V.A.
'''

import threading
import time
import _wrapper as wr

global ss

global voices
voices = {
          'rus':'Boris',
          'bel':'Boris_Bel'
          }

def say(expr, lang = 'rus'):
    ss = Speech_thread(expr, lang)
    ss.start()

class Speech_thread(threading.Thread):
    
    def __init__(self, expr, lang):
        self.tosay = expr
        global voices
        print "[SSRLab] voice %s" % voices[lang]
        print "[SSRLab] %s" % self.tosay
        threading.Thread.__init__(self) 
        self.tts = wr.new_TTS()
        wr.TTS_SetVoice(self.tts, voices[lang])
        
    def run(self):       
        wr.TTS_Speak(self.tts, self.tosay.encode("CP1251"))
        time.sleep(5)
        while wr.TTS_IsSpeaking(self.tts):
            time.sleep(1)
        print "[SSRLab] Stop talking =("
        time.sleep(1)
        wr.delete_TTS(self.tts)