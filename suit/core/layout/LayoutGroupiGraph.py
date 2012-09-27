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
Created on 14.05.2012

@author: Denis Koronchik
'''

from LayoutGroup import LayoutGroupDepth
import math, random
import suit.core.render.engine as render_engine
import ogre.renderer.OGRE as ogre
from suit.core.objects import Object
import igraph

class LayoutGroupIGraph(LayoutGroupDepth):
    
    LT_CIRCLE, LT_DRL, LT_FR, LT_GFR, LT_KK, LT_LGL, LT_RANDOM, LT_RT, LT_RTC, LT_SPHERE, LT_COUNT = range(11)
    
    def __init__(self, _type = LT_RANDOM):
        
        LayoutGroupDepth.__init__(self)
        
        # map of forces
        self.type = _type
        
        self.needModeUpdate = True
        
    def __del__(self):
        LayoutGroupDepth.__del__(self)

    def _addObjectToGroup(self, _object):
        """Append object to layout group
        """
        res = LayoutGroupDepth._addObjectToGroup(self, _object)
        self.need_layout = True   
        return res
        
    def _removeObjectFromGroup(self, _object):
        """Removes object from layout group
        """
        res = LayoutGroupDepth._removeObjectFromGroup(self, _object)
        self.need_layout = True
        return res
        
    def _removeAllObjectsFromGroup(self):
        """Removes all objects from layout group
        """
        res = LayoutGroupDepth._removeAllObjectsFromGroup(self)
#        self.step = self.step_max
        self.need_layout = True
        
        return res
    
    def _mode_changed_impl(self):
        """Sets flag to update Z axis positions 
        """
        self.needModeUpdate = True
        
        LayoutGroupDepth._mode_changed_impl(self)
    
    def _apply(self):
        """Applies force directed layout to group
        """
        LayoutGroupDepth._apply(self)
        
        # build graph representation
        g = igraph.Graph()
        verts = []
        verts.extend(self.nodes)
        verts.extend(self.sheets)
        
        g.add_vertices(len(verts))
        obj2idx = {}
        idx = 0
        for obj in verts:
            obj2idx[obj] = idx
            idx += 1
            
        edges = []
        for pair in self.lines:
            
            if not obj2idx.has_key(pair.getBegin()):
                continue
            idx_b = obj2idx[pair.getBegin()]
            
            if not obj2idx.has_key(pair.getEnd()):
                continue
            idx_e = obj2idx[pair.getEnd()]
            
            edges.append((idx_b, idx_e))
            
        g.add_edges(edges)
        
        coords = g.layout("circle")
        
        # apply results
        idx = 0
        for v in verts:
            pos = coords[idx]
            v.setPosition(ogre.Vector3(pos[0], pos[1], 0))
            idx += 1
   
        self.need_layout = False
