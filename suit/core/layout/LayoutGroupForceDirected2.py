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
import suit.core.objects as objects

class LayoutGroupForceSimple(LayoutGroupDepth):
    
    def __init__(self,
                 _step_max = 0.1,
                 _step_min = 0.0015, 
                 _max_rep_length = 10.0,
                 _max_force = 0.3,
                 _repulsion = 25,
                 _rigidity = 6,
                 _length = 6.0,
                 _gravity = 0.5):
        
        LayoutGroupDepth.__init__(self)
        
        # map of forces
        self.step_max = _step_max
        self.step = self.step_max
        self.prevMaxF = 0.0
        self.minMaxF = 0.001
        self.maxf = 0.0
        self.step_min = _step_min
        self.lengthOld = 0
        
        self.max_rep_length = _max_rep_length
        self.max_force = _max_force
        
        
        self.repulsion = _repulsion
        self.rigidity = _rigidity
        self.length = _length
        self.gravity = _gravity
        self.dr = 1.5
        self.df = 0.00001
        self.kstep = 0.9
        self.alpha = 15000
        self.beta = 0.2
        self.iterations = 20
        
        self.radius = 1
        self.angle = 0.0
        
        self.needModeUpdate = True
        
    def __del__(self):
        LayoutGroupDepth.__del__(self)

    def _addObjectToGroup(self, _object):
        """Append object to layout group
        """
        res = LayoutGroupDepth._addObjectToGroup(self, _object)
        
        if (isinstance(_object, objects.ObjectLine)):
            return True
        
#        self.step = self.step_max
        self.need_layout = True
                
        # calculate object position as an geometrical center of connected to it objects
        pos = None
        count = 0
        objs = _object.getLinkedObjects(Object.LS_IN)
        for obj in objs:
            if obj.getBegin() in self.objects:
                if pos is None:
                    pos = obj.getBegin().getPosition()
                    count += 1
                else:
                    pos += obj.getPosition()
                    count += 1
                
            
        objs = _object.getLinkedObjects(Object.LS_OUT)
        for obj in objs:
            if obj.getEnd() in self.objects:
                if pos is None:
                    pos = obj.getBegin().getPosition()
                    count += 1
                else:
                    pos += obj.getPosition()
                    count += 1
       
        if pos is not None:
            pos = pos / float(count)
        else:
            pos = ogre.Vector3(0, 0, 0)
            
        if render_engine.viewMode is render_engine.Mode_Isometric:
            pos = pos + ogre.Vector3(math.cos(len(self.objects) * (math.pi**2)), math.sin(len(self.objects)* (math.pi**2)), 0.0)
        else:
            dx = math.cos(len(self.objects) * (math.pi**2))
            dy = math.sin(len(self.objects)* (math.pi**2))
            pos = pos + ogre.Vector3(dx, dy, dx + dy)
                
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
        
        ln = len(self.objects)
        if ln == 0: return
        if not self.lengthOld == ln: 
            self.step = self.step_max / len(self.objects)
            self.prevMaxF = 0.0
            self.prevStep = self.step
            
        self.lengthOld = ln
                        
        n_obj = []
        n_obj.extend(self.nodes)
        n_obj.extend(self.sheets)
        n_obj.extend(self.lines)
        n = len(n_obj)
        
        #if n == 0:
        #    self.needModeUpdate = False 
        #    return
        
        forces = [ogre.Vector3(0, 0, 0)] * n
        obj_f = {}
        self.maxf = 0.0
        for idx in xrange(n):
            obj_f[n_obj[idx]] = idx
                
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
              
#        _iters = min([len(self.nodes) + len(self.sheets), self.iterations])
        for it in xrange(self.iterations):
        
            # calculating repulsion forces
            for idx in xrange(n):             
                p1 = o_pos[idx]
                l = p1.length()
                
                f = 0.0
                               
                for jdx in xrange(idx + 1, n):
                    p2 = o_pos[jdx]
                    p = (p1 - p2)
                    l = p.length()
                                  
                    if l > self.max_rep_length: continue    # don't calculate repulsion if distance between objects is to
                    
                    if l < 0.005: l += 0.005
                    f = p * self.repulsion / l / l / l

                    # append forces to nodes
                    forces[idx] = forces[idx] + f# * inv_mass1
                    forces[jdx] = forces[jdx] - f# * inv_mass2
                                   
            # calculating springs
            for line in self.lines:
                
                ob = line.getBegin()
                oe = line.getEnd()
                if ob is None or oe is None:    continue
#                if not obj_f.has_key(ob) or not obj_f.has_key(oe): continue
                
                p1 = ob.getPosition()
                p2 = oe.getPosition()
                
                p = (p2 - p1)
                l = p.length()
                
                if l > 0:
                    l = l - self.length
                    f = p * self.rigidity * math.log(l) #l
                else:
                    f = ogre.Vector3(1, 1, 0)
                                
                if obj_f.has_key(ob):
                    idx = obj_f[ob]
                    forces[idx] = forces[idx] + f
                if obj_f.has_key(oe):
                    idx = obj_f[oe]
                    forces[idx] = forces[idx] - f

            # apply forces to objects
            maxf = 0.0
            for idx in xrange(n):
                f = forces[idx]
                # getting maximum force
                maxf = max([maxf, f.length()])          
            
            #_step = (maxf * self.alpha + 1.0) * self.dr / (maxf * maxf * self.alpha + self.dr)#self.dr / (maxf + 0.01)
            _step = self.dr / (maxf + 0.01)
            if (maxf - self.prevMaxF) > self.df:
                self.step = _step
            else:
                self.step = min([self.kstep * self.prevStep, _step])
            
            self.maxf = maxf * self.step
            self.prevMaxF = maxf
                
            for idx in xrange(n):
                f = forces[idx]
                offset = f * self.step
                self.maxf = max([self.maxf, offset.length()])
                pos = o_pos[idx] + offset
                forces[idx] = ogre.Vector3(0, 0, 0)
                o_pos[idx] = pos
        
            self.need_layout = not (self.dr > (maxf * self.beta))
            
            if not self.need_layout:
                break
            
            # calculate geometry center
            left = 0
            top = 0
            right = 0
            bottom = 0
            for idx in xrange(n):
                pos = o_pos[idx]
                
                if pos.x < left:
                    left = pos.x
                if pos.y < top:
                    top = pos.y
                if pos.x > right:
                    right = pos.x
                if pos.y > bottom:
                    bottom = pos.y
            
            offset = ogre.Vector3(-(right + left) / 2.0, -(top + bottom) / 2.0, 0.0)
            
            # apply positions
            for idx in xrange(n):
                n_obj[idx].setPosition(o_pos[idx] + offset)


    def getLineLength(self, cnt):
        """Calculates length for a line depending on output/input arcs count
        """
        return max([self.length, cnt / 3.0])
    
    def getLinkedCount(self, obj):
        return len(obj.linkedObjects[Object.LS_OUT]) + len(obj.linkedObjects[Object.LS_IN])