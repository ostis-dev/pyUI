
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
Created on 24.11.2009

@author: Denis Koronchick

Modified on 8.04.2010
by Maxim Kaskevich
'''

from suit.core.kernel import Kernel 
from suit.cf import BaseModeLogic
from suit.core.objects import BaseLogic
import ogre.io.OIS as ois
import ogre.renderer.OGRE as ogre
import graph_env

def initialize():
    """Initialize module function
    """
    pass

def shutdown():
    """Shutting down module function
    """
    pass


class GraphViewer(BaseModeLogic):
    """Graph viewer logic realization
    """
    def __init__(self):
        BaseModeLogic.__init__(self)
        
        # view modes
        self._modes = {}
        self.mode = None

        self.is_root = False    # flag for root mode, need to store there for grow speed up
        
    
    def __del__(self):
        """Destruction
        """
        BaseModeLogic.__del__(self)
    
    def delete(self):
        """Deletion message
        """        
        BaseModeLogic.delete(self)
    
    def _setSheet(self, _sheet):
        BaseModeLogic._setSheet(self, _sheet)
        
        _sheet.eventRootChanged = self._onRootChanged
        
    def _onRootChanged(self, _isRoot):
        """Notification message on sheet root changed
        """
        if _isRoot:
            sheet = self._getSheet()
        else:
            sheet = self._getSheet()
            
        self.is_root = _isRoot
