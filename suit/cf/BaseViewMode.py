
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
Created on 02.01.2010

@author: Denis Koronchik
'''
from BaseMode import BaseMode
import ogre.io.OIS as ois

class BaseViewMode(BaseMode):
    """Base class for modes
    It has binds for keys:
    - A - selecting / unselecting objects. If there are no any objects selected, then
     selects all objects, else remove selection from selected objects.
     
    It have logic for mouse:
    - 
    """
    def __init__(self, _logic, _name = "Unknown mode"):
        BaseMode.__init__(self, _logic, _name)
        
    def __del__(self):
        BaseMode.__del__(self)
    
    def _activate(self):
        """Notification on mode activate.
        Only for internal usage
        """
        self.active = True
