
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
Created on 06.10.2009

@author: Denis Koronchik
'''

"""Realization of scg-viewer component
"""
from suit.cf import BaseModeLogic

import suit.core.kernel as core
import suit.core.utils as utils
import suit.core.objects as objects
import ogre.renderer.OGRE as ogre
import ogre.io.OIS as ois
import scg_modes
import scg_objects

# store log manager to make it more useful
logManager = utils.LogManager.getSingleton()

#############
# resources #
#############
def getResourceLocation():
    """Return resource location folder
    """
    return core.Kernel.getResourceLocation() + 'scg' 

def getResourceGroup():
    """Return resource group name
    """
    return 'scg'


###########
# classes #
###########
class SCgViewer(BaseModeLogic):
    """Class that represents logic of scg-viewer.
    
    When we creating viewer it registers in sc-memory.
    """
    def __init__(self):
        """Constructor
        """
        BaseModeLogic.__init__(self)
        
        # addr of viewed set
        self.view_set_addr = None
        
        # view modes
        self.appendMode(ois.KC_V, scg_modes.SCgViewMode(self))
        self.switchMode(ois.KC_V)
    
    def __del__(self):
        """Destructor
        """
        BaseModeLogic.__del__(self)
       
    def _setSheet(self, _sheet):
        """Sets sheet that controls by this logic
        """
        BaseModeLogic._setSheet(self, _sheet)
        
        _sheet.eventContentUpdate = self._onContentUpdate
        
    def _onContentUpdate(self):
        
        import suit.core.keynodes as keynodes
        sheet = self._getSheet()
        
        sheet.content_type = objects.ObjectSheet.CT_String
        sheet.content_data = str("") # make translation into gwf
        sheet.content_format = keynodes.ui.format_scgx
