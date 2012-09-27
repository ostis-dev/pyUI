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


import pm
'''
Created on Apr 18, 2009

@author: Kolb Dmitry
'''
class constraints:
    """
     # PyUML: Do not remove this line! # XMI_ID:_ENX4r0SuEd6cjr8i1rsWVA
    """
    def __init__(self):
        '''
        Constructor
        '''
        x=0
        while x< 8192:
            constr  = pm.sc_constraint_get_info(x)
            if constr!=None:
               s = str(constr.name)
               self.__dict__[s] = constr.id
               #print s
               x=x+1
            else:
                x=x+1
                continue 
            
            
            


           
