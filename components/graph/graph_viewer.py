
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

import suit.core.render.engine as render_engine
from suit.core.kernel import Kernel 
from suit.cf import BaseModeLogic

from suit.core.objects import BaseLogic
from suit.core.objects import Object

import ogre.io.OIS as ois
import ogre.renderer.OGRE as ogre

import graph_env
import graph_objects as gobjects

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
        _sheet.eventContentUpdate = self._onContentUpdate
        
        import suit.core.layout.LayoutGroupForceDirected as layout
        _sheet.setLayoutGroup(layout.LayoutGroupForceSimple())
        
    def _onRootChanged(self, _isRoot):
        """Notification message on sheet root changed
        """
        if _isRoot:
            render_engine.SceneManager.setBackMaterial("Back/Compare")
        else:
            render_engine.SceneManager.setDefaultBackMaterial()  
            
        self.is_root = _isRoot
        
    def _onContentUpdate(self):
        
        import suit.core.keynodes as keynodes
        import suit.core.objects as objects
        sheet = self._getSheet()
        
        sheet.content_type = objects.ObjectSheet.CT_String
        sheet.content_data = str("")
        sheet.content_format = keynodes.ui.format_graph
        
    def createVertex(self, _pos):
        """Creates vertex based on mouse position
        @param _pos: mouse coordinates
        @type _pos: tuple 
        
        @return: created graph vertex object
        @rtype: GraphPoint
        """
        vertex_obj = gobjects.GraphVertex()
        vertex_obj.setPosition(render_engine.pos2dTo3dIsoPos(_pos))
        vertex_obj.setState(Object.OS_Normal)
        
        return vertex_obj
    
    def createLink(self, _beg, _end):
        """Creates link
        @param _beg: begin vertex object
        @type _beg: GraphVertex
        @param _end: end vertex object
        @type _end: GraphVertex
        
        @return: created graph link object
        @rtype: GraphLink 
        """
        link_obj = gobjects.GraphLink()
        link_obj.setBegin(_beg)
        link_obj.setEnd(_end)
        link_obj.setState(Object.OS_Normal)
        
        return link_obj
