
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
Created on 08.03.2010

@author: Denis Koronchik
@summary: Realization of tools panel for geometry editor
'''

import suit.core.render.mygui as mygui
import suit.core.exceptions
import suit.core.render.engine


class Panel:
    
    def __init__(self):
        
        self.objects = []
    
    def __del__(self):
        pass
    
    def delete(self):
        pass
    
    def add_object(self, _object):
        """Adds object into panel
        """
        self.objects.append(_object)
    
    def remove_object(self, _object):
        """Removes object from panel
        """
        self.objects.remove(_object)
    
    def update_object(self):
        pass
        