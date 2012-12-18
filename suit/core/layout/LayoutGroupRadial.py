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
Created on 28.11.2012

@author: Vitaly Pylinsky
'''

from LayoutGroup import LayoutGroupDepth
import ogre.renderer.OGRE as ogre
import math
from suit.core.objects import Object, ObjectLine


class LayoutGroupRadialSimple(LayoutGroupDepth):
    """Radial graph layout implementation
    """ 
    
    def __init__(self,
                 _distance = 4.0):
        """Constructor
        """
        LayoutGroupDepth.__init__(self)
        
        self.initDistance = self.distance = _distance
        self.delta = 0.5
        
        self.needModeUpdate = True
        
        self.root = None
        
        # node radius
        self.radius = 1.0
      
        
    def __del__(self):
        LayoutGroupDepth.__del__(self)

    def _addObjectToGroup(self, _object): 
        """Appends object to layout group
        """ 
        res = LayoutGroupDepth._addObjectToGroup(self, _object)
        self.need_layout = True
        
        return res
        
    def _removeObjectFromGroup(self, _object):
        """Removes object from layout group
        """
        res = LayoutGroupDepth._removeObjectFromGroup(self, _object)
        self.distance = self.initDistance
        self.need_layout = True
        
        return res
        
    def _removeAllObjectsFromGroup(self):
        """Removes all objects from layout group
        """
        res = LayoutGroupDepth._removeAllObjectsFromGroup(self)
        self.need_layout = True
        
        return res
    
    def _mode_changed_impl(self):
        """Sets flag to update Z axis positions 
        """
        self.needModeUpdate = True

        LayoutGroupDepth._mode_changed_impl(self)
    
    def _apply(self):
        """Applies radial layout to group
        """
        LayoutGroupDepth._apply(self)
       
        n_obj = []
        n_obj.extend(self.nodes)
        n_obj.extend(self.sheets)
        ln = len(n_obj)

        if self.root is None and ln == 0:
            return
          
        # choose first node in list as the graph root
        if self.root is None:
            self.root = n_obj[0]
            
        # reset level attribute 
        for obj in n_obj:
            obj.level = -1 
        self.root.level = 0
        
        # levels count
        numLevels = self.calculateLevels()
            
        # iterate through the levels
        for lvl in range(numLevels + 1):
            
            if lvl == 0:
                # set graph root in the center
                self.root.setPosition(ogre.Vector3(0, 0, 0))   
                
            if lvl == 1: 
                # all nodes at this level
                nodes = [obj for obj in n_obj if obj.level == lvl]
                # check to resize graph
                if self.isNeedToResize(2 * math.pi, lvl, len(nodes)):
                    return
                
                self.calculate(nodes, lvl, 2 * math.pi, 0.0, 0.0)
                     
            if lvl >= 2:  
                # parents of nodes at this level
                parents = [obj for obj in n_obj if obj.level == lvl - 1 and self.hasChildsInGraph(obj)]
                if len(parents) == 0:
                    # all nodes at this level
                    nodes = [obj for obj in n_obj if obj.level == lvl]
                    # check to resize graph
                    if self.isNeedToResize(2 * math.pi, lvl, len(nodes)):
                        return
                
                    self.calculate(nodes, lvl, 2 * math.pi, 0.0, 0.0)
                
                else:
                    # loop through all childs for the every parent 
                    for parent in parents:                           
                        # childs of parent
                        childs = self.getChilds(parent)
                        # angle limits for the childs nodes
                        leftlimit = parent.leftLim
                        rightlimit = parent.rightLim
                        # check to resize graph
                        if self.isNeedToResize(leftlimit - rightlimit, lvl, len(childs)):
                            return
                        
                        self.calculate(childs, lvl, leftlimit - rightlimit, rightlimit, 0.5)
                        
                       
    def calculate(self, _nodes, _lvl, _limitangle, _rightlimit, _k):
        '''Performs calculation nodes position and nodes limits
            @param _nodes: nodes for calculating
            @param _lvl: level of the nodes
            @param _limitangle: angle sector of nodes
            @param _rightlimit: angle which is right limit for the nodes
            @param _k: coefficient for calculating
        '''
        # nodes with childs
        nodesWithChilds = [node for node in _nodes if self.hasChildsInGraph(node)]
        # nodes with childs list length
        nLen = len(nodesWithChilds)
        # leaves
        leaves = [node for node in _nodes if not self.hasChildsInGraph(node)]
        # leaves list length
        cLen = len(leaves)
        # space that occupies one node
        leafSpace = self.radius / (self.distance * _lvl)
        
        if nLen == 0:
            angleSpace = _limitangle / cLen
            self.calculatePositions(leaves, _lvl, angleSpace, _rightlimit + _k * angleSpace)
        elif cLen == 0:
            angleSpace = _limitangle / nLen
            self.calculatePositions(nodesWithChilds, _lvl, angleSpace, _rightlimit + _k * angleSpace)
        else:
            angleSpace = (_limitangle - cLen * leafSpace) / (nLen + 1.0)
            self.calculatePositions(leaves, _lvl, leafSpace, _rightlimit + angleSpace)
            self.calculatePositions(nodesWithChilds, _lvl, angleSpace, _rightlimit
                                     + (2.0 - _k) * angleSpace + cLen * leafSpace  - (0.5 - _k) * leafSpace)
        
        self.calculateLimits(nodesWithChilds, _lvl)
           
                              
    def calculatePositions(self, _nodes, _lvl, _angleSpace, _rightlimit): 
        '''Calculates position for the everyone node in list at the specified level
            @param _nodes: nodes to calculate positions
            @param _lvl: level of the nodes
            @param _angleSpace: angle sector of the each node
            @param _rightlimit: angle which is right limit for the nodes
        '''
        # Loop through all nodes
        i = 0       
        for node in _nodes: 
            # calculate x, y position
            x = self.root.getPosition().x + self.distance * _lvl * math.cos(_angleSpace * i + _rightlimit)
            y = self.root.getPosition().y + self.distance * _lvl * math.sin(_angleSpace * i + _rightlimit)
    
            node.setPosition(ogre.Vector3(x, y, 0))
            node.angle = _angleSpace * i + _rightlimit
            i += 1
        
                
    
    def calculateLimits(self, _nodes, _lvl): 
        '''Loop through the nodes with childs calculating bisector limits
             and tangent limits for the everyone child and as result calculate left and right limits
             @param _nodes: nodes with childs
             @param _lvl: level of the nodes
        '''
        # calculate tangent limit arc
        arc = math.acos(_lvl / (_lvl + 1.0))
        
        # calculate bisector and tangent limits for the node
        firstNode = None
        lastNodeAngle = 0.0
        prevNode = None        
        for node in _nodes:        
            # the first node
            if firstNode is None:
                firstNode = node
                    
            # get angle to previous node
            angleToPrevNode = node.angle - lastNodeAngle
            # calculate right bisector limit
            node.rightBisLim = node.angle - angleToPrevNode / 2
            
            if prevNode is not None:
                # set left bisector limit
                prevNode.leftBisLim = node.rightBisLim
            
            # calculate left tangent limit
            node.leftTanLim = node.angle + arc
            # calculate right tangent limit
            node.rightTanLim = node.angle - arc
            
            lastNodeAngle = node.angle
            prevNode = node
        
        if firstNode is not None: 
            # add remaining angel to first node
            remainingAngle = 2 * math.pi - prevNode.angle
            angleToFirstNode = remainingAngle + firstNode.angle

            firstNode.rightBisLim = firstNode.angle - angleToFirstNode / 2
           
            if _nodes[0] is firstNode and _nodes[-1] is prevNode:
                leftBisLimit = firstNode.rightBisLim
            elif firstNode.rightBisLim < 0:
                leftBisLimit = firstNode.rightBisLim + 2 * math.pi
            else:
                leftBisLimit = firstNode.rightBisLim
            
            prevNode.leftBisLim = leftBisLimit + 2 * math.pi
        
        # calculate right and left limits             
        for node in _nodes:
            node.leftLim = min([node.leftTanLim, node.leftBisLim])
            node.rightLim = max([node.rightTanLim, node.rightBisLim])
   
   
    def isNeedToResize(self, _arc, _lvl, _count):
        """Return True, if nodes count more then arc capacity; otherwise return False
            @param _arc: arc to check capacity
            @param _lvl: graph level
            @param _count: nodes count at the specified level within the specified arc
            @rtype: bool
        """
        if _count > int(_arc * self.distance * _lvl / self.radius):
            self.distance += self.delta
            self.need_layout = True
            return True
        
        return False
    
    def calculateLevels(self):
        """Calculates levels for the everyone graph component
            @return: number of levels
        """
        maxLevel = 0
        
        # calculate levels for the central graph
        maxRootLevel = self.calculateComponentLevels(self.root)
        maxLevel = max([maxLevel, maxRootLevel])
        
        # calculate levels for the connected components      
        for comp in self.nodes:
            if comp.level == -1:
                comp.level = maxRootLevel + 1
                
                maxCompLevel = self.calculateComponentLevels(comp)
                maxLevel = max([maxLevel, maxCompLevel])
                
        return maxLevel
    
    def calculateComponentLevels(self, _root):
        """Calculates level for the everyone object in the graph component 
            with specified root. Breadth-first search strategy is used
            @param _root: root object of the graph component to start calculation
            @return: number of levels in the component
        """
        lvlCount = _root.level
        Q = []  # queue to store intermediate results when traverses the graph component
        Q.append(_root)
        while Q != []:
                node = Q.pop(0)
                for v in self.getLinkedNodes(node):
                        if v.level == -1:
                                v.level = node.level + 1
                                lvlCount = max([lvlCount, v.level]) 
                                Q.append(v)
        return lvlCount
    
    def getLinkedNodes(self, _node):
        """Gets nodes linked with the specified node
            @param _node: node to get linked nodes with
            @return: list of linked nodes
        """ 
        linkedNodes = []
        linkedNodes.extend([x.getEnd() for x in _node.linkedObjects[Object.LS_OUT] 
                            if x.getEnd() is not None and not isinstance(x.getEnd(), ObjectLine)])
        linkedNodes.extend([x.getBegin() for x in _node.linkedObjects[Object.LS_IN] 
                            if x.getBegin() is not None and not isinstance(x.getBegin(), ObjectLine)])
        
        return linkedNodes
    
    def hasChildsInGraph(self, _node): 
        """Return True, if the specified node has childs in graph; otherwise return False
            @param _node: node to check
            @rtype: bool
        """
        for x in self.getLinkedNodes(_node):
            if x.level == _node.level + 1:
                return True
            
        return False
    
    def getChilds(self, _node):
        """Gets childs for the specified node in graph 
            @param _node: node with childs
            @return: node's childs
        """   
        childs = [] 
        for x in self.getLinkedNodes(_node):
            if x.level == _node.level + 1:
                childs.append(x)
                
        return childs
    
    def setRoot(self, _node):
        """Sets specified node as the graph root
            @param _node: node to set as the graph root  
        """
        self.root = _node
        self.distance = self.initDistance
        self.need_layout = True
        
        