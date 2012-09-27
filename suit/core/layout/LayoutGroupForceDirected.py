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
Created on 29.01.2010

@author: Denis Koronchik
'''

from LayoutGroup import LayoutGroupDepth
import ogre.renderer.OGRE as ogre
import math, random
import suit.core.render.engine as render_engine
from suit.core.objects import Object

class LayoutGroupForceSimple(LayoutGroupDepth):
    
    def __init__(self,
                 _step_max = 0.1,
                 _step_min = 0.0125, 
                 _max_rep_length = 24.0,
                 _max_force = 0.7,
                 _repulsion = 27.7,
                 _rigidity = 1.1,
                 _length = 5.5,
                 _gravity = 0.01):
        
        LayoutGroupDepth.__init__(self)
        
        # map of forces
        self.step_max = _step_max
        self.step = self.step_max
        self.step_min = _step_min
        
        self.max_rep_length = _max_rep_length
        self.max_force = _max_force
        
        self.repulsion = _repulsion
        self.rigidity = _rigidity
        self.length = _length
        self.gravity = _gravity
        
        self.radius = 1
        self.angle = 0.0
        
        self.needModeUpdate = True
        
    def __del__(self):
        LayoutGroupDepth.__del__(self)

    def _addObjectToGroup(self, _object):
        """Append object to layout group
        """
        res = LayoutGroupDepth._addObjectToGroup(self, _object)
#        self.step = self.step_max
        self.need_layout = True
        
#        if render_engine.viewMode is render_engine.Mode_Isometric:
#            _object.setPosition(ogre.Vector3(math.cos(self.angle), math.sin(self.angle), 0.0) * self.radius)
#        else:
#            _object.setPosition(ogre.Vector3(math.cos(self.angle), math.sin(self.angle), math.sin(self.angle) + math.cos(self.angle)) * self.radius)
        #self.radius += 1.0 / 36.0
        #self.angle += 0.17
        
        # calculate object position as an geometrical center of connected to it objects
        pos = None
        count = 0
        objs = _object.getLinkedObjects(Object.LS_IN)
        for obj in objs:
            if obj.getBegin() in self.objects:
                if pos is None:
                    pos = obj.getPosition()
                    count += 1
                else:
                    pos += obj.getPosition()
                    count += 1
                
            
        objs = _object.getLinkedObjects(Object.LS_OUT)
        for obj in objs:
            if obj.getBegin() in self.objects:
                if pos is None:
                    pos = obj.getPosition()
                    count += 1
                else:
                    pos += obj.getPosition()
                    count += 1
                    
        if pos is not None:
            pos = pos / float(count)
        else:
            if render_engine.viewMode is render_engine.Mode_Isometric:
                pos = ogre.Vector3(2 * math.cos(len(objs)), 2 * math.sin(len(objs)), 0.0)
            else:
                pos = ogre.Vector3(2 * math.cos(len(objs)), 2 * math.sin(len(objs)), math.cos(len(objs)) + math.sin(len(objs)))
        _object.setPosition(pos)
   
        return res
        
    def _removeObjectFromGroup(self, _object):
        """Removes object from layout group
        """
        res = LayoutGroupDepth._removeObjectFromGroup(self, _object)
#        self.step = self.step_max
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
        
        
#        import math
#        items_count = len(self.nodes)
#        
#        if items_count != 0:
#            da = 2 * math.pi / items_count
#            angle = 0
#            radius = 5
#            for obj in self.nodes:
#                # set new position
#                x = radius * math.cos(angle) - obj.scale.x / 2
#                y = radius * math.sin(angle) - obj.scale.y / 2
#                z = 0
#                obj.setPosition(ogre.Vector3(x, y, z))
#                angle += da
#
        
                
        
        n_obj = []
        n_obj.extend(self.nodes)
        n_obj.extend(self.sheets)
        n = len(n_obj)
        
        #if n == 0:
        #    self.needModeUpdate = False 
        #    return
        
        forces = [ogre.Vector3(0, 0, 0)] * n
        obj_f = {}
        
        
#        self.step = self.step * 0.99
        
        o_pos = []
        # updating on mode
        if self.needModeUpdate:
            angle = 0.0
            radius = 1.0
            
            for obj in n_obj:
                pos = obj.getPosition()
                if render_engine.viewMode is render_engine.Mode_Isometric:
                    o_pos.append(ogre.Vector3(pos.x, pos.y, 0.0))
                else:
                    o_pos.append(ogre.Vector3(pos.x, pos.y, math.cos(angle) * radius))
                    angle += 0.25
                    radius += 0.1
                    
            self.needModeUpdate = False
        else:
            for obj in n_obj:
                o_pos.append(obj.getPosition())
            
        
        # calculating repulsion forces
        for idx in xrange(n):
            obj_f[n_obj[idx]] = idx
            
            p1 = o_pos[idx]
            
            l = p1.length()
            
            #if l > 3:
            f = (p1) * self.gravity * (l - 3.0)
            forces[idx] = forces[idx] - f
            
            for jdx in xrange(idx + 1, n):
                
                
                p2 = o_pos[jdx]
                p = (p1 - p2)
                p.normalise()
                
                l = p1.distance(p2)
                
                if l > self.max_rep_length: continue    # don't calculate repulsion if distance between objects is to
                
                if l > 0.5:
                    f = p * self.repulsion / l / l
                else:
                    f = ogre.Vector3(math.cos(0.17 * idx) * self.length * 7, math.sin(0.17 * (idx + 1)) * self.length * 7, 0) 
                
                # append forces to nodes
#                if idx != 0:
                forces[idx] = forces[idx] + f
                forces[jdx] = forces[jdx] - f
                
        
        # calculating springs
        for line in self.lines:
            
            ob = line.getBegin()
            oe = line.getEnd()
            if ob is None or oe is None:    continue
            
            p1 = ob.getPosition()
            p2 = oe.getPosition()
            
            l = p1.distance(p2)

            if l > 0:
                p = (p2 - p1)
                p.normalise()
#                f = p*(self.rigidity * (l - self.length) / l)
                #cnt = self.getLinkedCount(ob) + self.getLinkedCount(oe)
                #f = p*(self.rigidity * (l - self.getLineLength(cnt)) / l)
                f = p * self.rigidity * math.log(l)
                
                if (f.length() > 10):
                    f = p * self.rigidity / l
            else:
                f = ogre.Vector3(0, 0, 0)
                
            if obj_f.has_key(ob):
                idx = obj_f[ob]
                forces[idx] = forces[idx] + f
            if obj_f.has_key(oe):
                idx = obj_f[oe]
                forces[idx] = forces[idx] - f

        
        # apply forces to objects
#        df = forces[0]
        maxf = 0.0
        for idx in xrange(n):
            f = forces[idx]
            # getting maximum force
            maxf = max([maxf, f.length()])
            pos = o_pos[idx] + (f) * self.step
            if render_engine.viewMode is render_engine.Mode_Isometric:
                pos = pos * ogre.Vector3(1, 1, 0)
            n_obj[idx].setPosition(pos)            
        
        if maxf >= self.max_force:
            self.step = self.step_max
        else:
            self.step = self.step * 0.97
        self.need_layout = self.step > self.step_min

    def getLineLength(self, cnt):
        """Calculates length for a line depending on output/input arcs count
        """
        return max([self.length, cnt / 3.0])
    
    def getLinkedCount(self, obj):
        return len(obj.linkedObjects[Object.LS_OUT]) + len(obj.linkedObjects[Object.LS_IN])