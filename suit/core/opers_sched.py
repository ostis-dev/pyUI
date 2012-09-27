
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
Created on 01.11.2009

@author: Denis Koronchik
'''
import kernel
import thread
import threading
import traceback
import sys
import time

log_manager = None 

class OperationScheduler(threading.Thread):
    """Scheduler for operations start.
    
    Scheduler starts operations from queue.
    """
    
    # priority constants
    OP_VeryHight, OP_Hight, OP_Normal, OP_Low, OP_VeryLow, OP_Count = range(6)
    
    def __init__(self):
        """Constructor
        """
        threading.Thread.__init__(self)
        # operations queue
        self.__queue = [[]] * self.OP_Count
        # thread lock
        self.__lock = thread.allocate_lock()
        # flag to stop scheduler
        self.needStop = False
        self.finished = False
          
    def _appendOperation(self, _impl_func, _checkers, _params, _segment, _priority = 2):
        """Append operation to queue
        @param _impl_func:    function that implements operation
        @type _impl_func:    function
        @param _checkers:    list of functions that check start condition of operation
        @type _checkers:    list
        @param _params:    set of parameters that will be passed to function
        @type _params:    sc_addr
        @param _segment:    temporary segment for operation temporary structures
        @type _segment:    sc_segment
        @param _priority:    operation priority. Default priority is OP_Normal. There a list of available
        priorities:
        -    OP_VeryHight
        -    OP_Hight
        -    OP_Normal
        -    OP_Low
        -    OP_VeryLow
        @type _priority:    int
        """
        
        if _priority < 0 or _priority >= OperationScheduler.OP_Count:
            log_manager.logWarning("Unknown priority for operation '%s' so it will be set to 'normal'" % str(_event))
            _priority = OperationScheduler.OP_Normal
        
        self.__lock.acquire()
        self.__queue[_priority].append((_impl_func, _checkers, _params, _segment))
        self.__lock.release()
        
    def run(self):
        """Thread loop to run operations
        """
        global log_manager
        log_manager = kernel.Kernel.getSingleton().logManager
        
        while not self.needStop:
            self.__lock.acquire()
        
            queue = self.__queue
            # clear queue
            self.__queue = [[]] * self.OP_Count
            
            self.__lock.release()
            
            # staring operations
            for _prior in xrange(self.OP_Count):
                while len(queue[_prior]) > 0:                
                    try:
                        op = queue[_prior].pop(0)
                        
                        _impl_func, _checkers, _params, _segment = op
                        _impl_func(_params, _segment)
                        
                        # @todo: Segment deletion
                        # deleting segment
                        session = kernel.Kernel.session()
                        
                        
                    except:
                        log_manager.logError("Error to run event with function '%s'" % (str(_impl_func)))
                        print "Error:", sys.exc_info()[0]
                        traceback.print_exc(file=sys.stdout)
                        
            # sleeps thread for some time
            time.sleep(0.01)
        
        self.finished = True
        
    def stop(self):
        """Stops scheduler
        """
        self.needStop = True
    
    def _startOperations(self):
        """Starts operations from queue
        """
        pass