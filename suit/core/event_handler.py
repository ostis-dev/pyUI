
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
Created on 16.11.2009

@author: Denis Koronchik
'''

import kernel
import sc_core.pm
import types

# event handler
class ScEventHandlerSetMember(sc_core.pm.ScOperationActSetMember):
    """Class represents handler to wait adding member to specified set.
    Just for example:
    We have set A, that class representing wait for creating arc from it.
    A ------- > C or A ---------> B  
    """
    
    def __init__(self, _name, _aset, _impl_func, _checkers_list):
        """Constructor
        @param _name:    operation name
        @type _name:    str
        @param _aset:    sc-element that represents set that we will waiting for members adding
        @type _aset:    sc_addr
        @param _impl_func:    Function that implement operation logic and will be called, when
                                operation activates. 
        @type _impl_func:    function
        @param _checkers_list:    list of functions that check operation run conditions
        @type _checkers_list:    list
        """
        sc_core.pm.ScOperationActSetMember.__init__(self, _name.encode("cp1251"), _aset)
        
        self._impl_func = _impl_func
        self._checkers = _checkers_list
        
    def __del__(self):
        sc_core.pm.ScOperationActSetMember.__del__(self)
        
    def activateImpl(self, _paramSystem, _tmpSegment):
        """Activate implementation. Appends operation to scheduler.
        """
        kernel.Kernel.getSingleton().opers_sched._appendOperation(self._impl_func, self._checkers, _paramSystem, _tmpSegment)
        
        
class ScEventHandlerActInSet(sc_core.pm.ScOperationActInSet):
    """Class represents handler to wait adding specified element to any set.
    Just for example:
    We have element A, that class representing wait for creating arc from it.
    C ------- > A or B ---------> A  
    """
    
    def __init__(self, _name, _el, _impl_func, _checkers_list):
        """Constructor
        @param _name:    operation name
        @type _name:    str
        @param _el:    sc-element that will be waited for adding into set
        @type _el:    sc_addr
        @param _impl_func:    Function that implement operation logic and will be called, when
                                operation activates. 
        @type _impl_func:    function
        @param _checkers_list:    list of functions that check operation run conditions
        @type _checkers_list:    list
        """
        sc_core.pm.ScOperationActInSet.__init__(self, _name.encode("cp1251"), _el)
        
        self._impl_func = _impl_func
        self._checkers = _checkers_list
        
    def __del__(self):
        sc_core.pm.ScOperationActInSet.__del__(self)
        
    def activateImpl(self, _paramSystem, _tmpSegment):
        """Activate implementation. Appends operation to scheduler.
        """
        kernel.Kernel.getSingleton().opers_sched._appendOperation(self._impl_func, self._checkers, _paramSystem, _tmpSegment)
        
        
class ScEventHandlerCont(sc_core.pm.ScOperationCont):
    """Class represents handler to wait changing of content for a specified element.      
    """
    
    def __init__(self, _name, _el, _impl_func, _checkers_list):
        """Constructor
        @param _name:    operation name
        @type _name:    str
        @param _el:    sc-element is waiting for content changing
        @type _el:    sc_addr
        @param _impl_func:    Function that implement operation logic and will be called, when
                                operation activates. 
        @type _impl_func:    function
        @param _checkers_list:    list of functions that check operation run conditions
        @type _checkers_list:    list
        """
        sc_core.pm.ScOperationCont.__init__(self, _name.encode("cp1251"), _el)
        
        self._impl_func = _impl_func
        self._checkers = _checkers_list
        
    def __del__(self):
        sc_core.pm.ScOperationCont.__del__(self)
        
    def activateImpl(self, _paramSystem, _tmpSegment):
        """Activate implementation. Appends operation to scheduler.
        """
        kernel.Kernel.getSingleton().opers_sched._appendOperation(self._impl_func, self._checkers, _paramSystem, _tmpSegment)
        
        
class ScEventHandlerIdtf(sc_core.pm.ScOperationIdtf):
    """Class represents handler to wait changing of identifier for a specified element.      
    """
    
    def __init__(self, _name, _el, _impl_func, _checkers_list):
        """Constructor
        @param _name:    operation name
        @type _name:    str
        @param _el:    sc-element is waiting for identifier changing
        @type _el:    sc_addr
        @param _impl_func:    Function that implement operation logic and will be called, when
                                operation activates. 
        @type _impl_func:    function
        @param _checkers_list:    list of functions that check operation run conditions
        @type _checkers_list:    list
        """
        sc_core.pm.ScOperationIdtf.__init__(self, _name.encode("cp1251"), _el)
        
        self._impl_func = _impl_func
        self._checkers = _checkers_list
        
    def __del__(self):
        sc_core.pm.ScOperationIdtf.__del__(self)
        
    def activateImpl(self, _paramSystem, _tmpSegment):
        """Activate implementation. Appends operation to scheduler.
        """
        kernel.Kernel.getSingleton().opers_sched._appendOperation(self._impl_func, self._checkers, _paramSystem, _tmpSegment)


class ScEventHandlerDie(sc_core.pm.ScOperationDie):
    """Class represents handler to wait deletion of specified element.      
    """
    
    def __init__(self, _name, _el, _impl_func, _checkers_list):
        """Constructor
        @param _name:    operation name
        @type _name:    str
        @param _el:    sc-element that is waiting for deletion  
        @type _el:    sc_addr
        @param _impl_func:    Function that implement operation logic and will be called, when
                                operation activates. 
        @type _impl_func:    function
        @param _checkers_list:    list of functions that check operation run conditions
        @type _checkers_list:    list
        """
        sc_core.pm.ScOperationDie.__init__(self, _name.encode("cp1251"), _el)
        
        self._impl_func = _impl_func
        self._checkers = _checkers_list
        
    def __del__(self):
        sc_core.pm.ScOperationDie.__del__(self)
        
    def activateImpl(self, _paramSystem, _tmpSegment):
        """Activate implementation. Appends operation to scheduler.
        """
        kernel.Kernel.getSingleton().opers_sched._appendOperation(self._impl_func, self._checkers, _paramSystem, _tmpSegment)


class ScEventHandlerChangeType(sc_core.pm.ScOperationChangeType):
    """Class represents handler to wait type changing of specified element.      
    """
    
    def __init__(self, _name, _el, _impl_func, _checkers_list):
        """Constructor
        @param _name:    operation name
        @type _name:    str
        @param _el:    sc-element that we are waiting for type changing  
        @type _el:    sc_addr
        @param _impl_func:    Function that implement operation logic and will be called, when
                                operation activates. 
        @type _impl_func:    function
        @param _checkers_list:    list of functions that check operation run conditions
        @type _checkers_list:    list
        """
        sc_core.pm.ScOperationChangeType.__init__(self, _name.encode("cp1251"), _el)
        
        self._impl_func = _impl_func
        self._checkers = _checkers_list
        
    def __del__(self):
        sc_core.pm.ScOperationChangeType.__del__(self)
        
    def activateImpl(self, _paramSystem, _tmpSegment):
        """Activate implementation. Appends operation to scheduler.
        """
        kernel.Kernel.getSingleton().opers_sched._appendOperation(self._impl_func, self._checkers, _paramSystem, _tmpSegment)