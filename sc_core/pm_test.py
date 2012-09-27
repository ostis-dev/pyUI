
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
Created on Oct 2, 2009

@author: Denis Koronchik
'''
import pm
import time
import thread
import threading
import sys, traceback

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
            pm.do_init(False, self.__repo_path)
            pm.do_dedicated(False)
        except:
            print "Error:", sys.exc_info()[0]
            traceback.print_exc(file=sys.stdout)
            return
        
        self.started = True
        
        while not self.stoped:
            pm.do_step()
            time.sleep(0.01)
            
        pm.libsc_deinit()
        self.finished = True
            
   def stop(self):
        self.stoped = True
 

class Callback(pm.sc_event_multi):
    
    def __init__(self):
        pm.sc_event_multi.__init__(self)
        self.__disown__()
        
    def activate(self, wait_type, params, len):
        print str(params)
        
class TestOp(pm.ScOperationActSetMember):
    
    def __init__(self, aset):
        pm.ScOperationActSetMember.__init__(self, "Test", aset)
    
    def activateImpl(self, arc, el):
        print "Hello"
 
Processor({'repo_path': '../repo/fs_repo'})
#call = Callback()
#time.sleep(5)
#print "Open segment"
#seg = pm.get_session().open_segment("/proc/keynode")
#print seg
#
#print "Create element"
#print pm.get_session()
#node = pm.get_session().create_el(seg, pm.SC_N_CONST)
#print node
#
#print "Attach event"
##call.attach_to(pm.get_session(), pm.SC_WAIT_HACK_SET_MEMBER, pm.ADDR_AS_PAR(node), 1)
#
#oper = TestOp(node)
#oper.registerOperation() 
#
#node1 = pm.get_session().create_el(seg, pm.SC_N_CONST)
#line = pm.get_session().create_el(seg, pm.SC_A_CONST)
#
#pm.get_session().set_beg(line, node)
#pm.get_session().set_end(line, node1)

#line = pm.get_session().gen3_f_a_f(node, line, seg, pm.SC_A_CONST, node1)

        
        


    