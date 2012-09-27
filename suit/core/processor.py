
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
Created on 03.10.2009

@author: Denis Koronchik
'''
import sys
import sc_core.pm
import threading
import time
import traceback

class Processor(threading.Thread):
    
   def __init__(self, params = {}):
        """Constuructor
        @param params: dictionary with parameters to start processor module
        Available parameters:
        repo_path - path to repository folder
        @type params: dict  
        """
        
        threading.Thread.__init__(self)
        self.stoped = False
        self.finished = False
        self.started = False
        
        self.__repo_path = '.'
        if params.has_key('repo_path'):
            self.__repo_path = params['repo_path']
        
        self.start()
        

   def run(self):
        try:
            #sc_core.pm.set_verb_output(True)
            sc_core.pm.do_init(False, True, self.__repo_path)
            sc_core.pm.do_dedicated(False)
        except:
            print "Error:", sys.exc_info()[0]
            traceback.print_exc(file=sys.stdout)
            return
        
        self.started = True
        
        while not self.stoped:
            sc_core.pm.do_step()
            time.sleep(0.001)
            
        sc_core.pm.libsc_deinit()
        self.finished = True
            
   def stop(self):
        self.stoped = True
 