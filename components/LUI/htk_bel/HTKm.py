# -*- coding: utf-8 -*-
import HTK as _HTK
    
import threading
import time
import os

htk_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),"data\\")

default_phrase = "вывесці выяву квадрата "
isRun = False

def start(func):
    isRun = True
    _HTK.SetPath(htk_dir)
    global htk
    htk = HTK(func)
    htk.start()

def stop():
    if isRun:
        isRun = False
        global htk
        htk.stop()

class HTK(threading.Thread):
            
    def __init__(self, func):
        print "[HTK] init"
        threading.Thread.__init__(self)
        self.func = func
        self._stop = False
        
    def run(self):
        print "[HTK] start"
        self.caller = _HTK.Caller()
        while not self._stop:
            text = self.caller.start()
            if text is not None:
                if not text.decode('cp1251').encode('utf-8') == default_phrase:
                    self.func(text)
            time.sleep(5)
    
    def stop(self):
        self._stop = True