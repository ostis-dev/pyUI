
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
Created on 31.12.2009

@author: Denis Koronchik
'''


# ***************************
# * Additional functions    * 
# ***************************


def _getFirstObjectTypeFromList(_list, _types):
    """Gets first object with specified type from objects list
    @param _list: list that represents results of _getObjectsUnderMouse function. Tuple: ()
    @type _list: list
    @param _type: list of available types
    @type _type: list
    
    @return: returns first object in list with specified type. If there is no any
    object with specified type in list, then returns None 
    """
    for obj in _list:
        if type(obj[1]) in _types:
            return obj[1]
    
    return None
