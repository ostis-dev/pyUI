
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
Created on 09.04.2010

@author: Uomo
'''
from LayoutGroup import LayoutGroupDepth

#import srs_engine.core as core
import ogre.renderer.OGRE as ogre
from suit.core.objects import Object
from suit.core.layout.Tree import TreeNode
from suit.core.layout.Tree import Tree
'''
kernel = core.Kernel.getSingleton()
kernel.getSingleton().prepareForScMachine()
session = kernel.session()
'''
#class LayoutSimple(LayoutGroupDepth):
class LayoutSimple(LayoutGroupDepth):
    tree = None
    NODE_WIDTH = 2  # Width of a node
    NODE_HEIGHT = 2  # Height of a node
    FRAME_THICKNESS = 1   # Fixed-sized node frame
    SUBTREE_SEPARATION = 4   # Gap between subtrees
    SIBLING_SEPARATION = 4   # Gap between siblings
    LEVEL_SEPARATION = 3   # Gap between levels
    MAXIMUM_DEPTH = 10  # Biggest tree
    # possible orientation
    NORTH, SOUTH, EAST, WEST = range(4)
    prev_node = []
    
    xTopAdjustment = 0  # How to adjust the apex
    yTopAdjustment = 0  #How to adjust the apex
    flMeanWidth = 0     #Ave. width of 2 nodes
    flModsum = 0.0
    
    def __init__(self):
        LayoutGroupDepth.__init__(self)
        self.show = True
        self.root_orientation = self.SOUTH   #could be: NORTH, SOUTH, EAST, WEST
        '''        
        self.node_width = 20        #width of a node
        self.node_height = 10       #height of a node
        self.frame_thickness = 1    #fixed-sized node frame
        self.subtree_separation = 5 #gap between subtrees
        self.sibling_separation = 4 #gap between siblings
        self.level_separation = 5   #gap between levels
        self.maximum_depth = 10     #biggest tree depth
        #-------------------------------------
        self.flMeanWidth = 0    #Ave. width of 2 nodes
        '''
        #-------------------------------------
        self.needModeUpdate = True
        self.marked_nodes = []
    
    def __del__(self):
        LayoutGroupDepth.__del__(self)

    def _addObjectToGroup(self, _object):
        """Append object to layout group
        """
        #if lastAddedObject == None:            
        #param = session.search_one_shot(session.sc_constraint_new(sc_constants.CONSTR_5_f_a_a_a_f, desc_prm, 0, 0, 0, attr_), True, 5)
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
        self.need_layout = True        
        return res
    
    def _mode_changed_impl(self):
        """Sets flag to update Z axis positions 
        """
        self.needModeUpdate = True        
        LayoutGroupDepth._mode_changed_impl(self)

    def _checkExtentsRange(self, lxTemp, lyTemp):
        '''
        Insert your own code here, to check when the
        tree drawing is going to be too big. My region is no
        more that 64000 units square.
        '''
        if (abs(lxTemp) > 32000) or (abs(lyTemp) > 32000):
            return False
        else: return True
    #!
    def _treeMeanNodeSize(self, pLeftNode, pRightNode):
        '''
        Write your own code for this procedure if your
        rendered nodes will have variable sizes.
        ----------------------------------------
        Here I add the width of the contents of the
        right half of the pLeftNode to the left half of the
        right node. Since the size of the contents for all
        nodes is currently the same, this module computes the
        following trivial computation.
        '''
        self.flMeanWidth = 0.0;   # Initialize this global        
        if self.root_orientation == self.NORTH or self.root_orientation == self.SOUTH:
            if pLeftNode:
                self.flMeanWidth = self.flMeanWidth + self.NODE_WIDTH / 2
                if self.show:
                    self.flMeanWidth = self.flMeanWidth + self.FRAME_THICKNESS
            if pRightNode:
                self.flMeanWidth = self.flMeanWidth + self.NODE_WIDTH / 2
                if self.show:
                    self.flMeanWidth = self.flMeanWidth + self.FRAME_THICKNESS
        else:  # self.root_orientation==EAST  or self.root_orientation==WEST:
            if pLeftNode:
                self.flMeanWidth = self.flMeanWidth + (self.NODE_HEIGHT / 2)
                if self.show:
                    self.flMeanWidth = self.flMeanWidth + self.FRAME_THICKNESS
            if pRightNode:
                self.flMeanWidth = self.flMeanWidth + (self.NODE_HEIGHT / 2)
                if self.show:
                    self.flMeanWidth = self.flMeanWidth + self.FRAME_THICKNESS

    def _treeApportion(self, pThisNode, nCurrentLevel):
        '''
        Clean up the positioning of small sibling subtrees.
        Subtrees of a node are formed independently and
        placed as close together as possible. By requiring
        that the subtrees be rigid at the time they are put
        together, we avoid the undesirable effects that can
        accrue from positioning nodes rather than subtrees.
        '''
        pLeftmost = pThisNode.getFirstChild()
        pNeighbor = pLeftmost.getLeftNeighbor()

        nCompareDepth = 1
        nDepthToStop = self.MAXIMUM_DEPTH - nCurrentLevel
        
        #while ((pLeftmost) && (pNeighbor) && (nCompareDepth <= nDepthToStop)) {
        while pLeftmost and pNeighbor and nCompareDepth <= nDepthToStop:
            '''
            Compute the location of pLeftmost and where it
            should be with respect to pNeighbor.
            '''
            flRightModsum = flLeftModsum = 0.0
            pAncestorLeftmost = pLeftmost
            pAncestorNeighbor = pNeighbor
            for i in range(nCompareDepth):
                pAncestorLeftmost = pAncestorLeftmost.getParent()#~
                pAncestorNeighbor = pAncestorNeighbor.getParent()#~
                flRightModsum = flRightModsum + pAncestorLeftmost.flModifier
                flLeftModsum = flLeftModsum + pAncestorNeighbor.flModifier
            '''
            Determine the flDistance to be moved, and apply
            it to "pThisNode's" subtree.  Apply appropriate
            portions to smaller interior subtrees
            '''                        
            #Set the global mean width of these two nodes
            self._treeMeanNodeSize(pLeftmost, pNeighbor)
            flDistance = (pNeighbor.flPrelim + flLeftModsum + self.SUBTREE_SEPARATION + self.flMeanWidth) - (pLeftmost.flPrelim + flRightModsum)
            if flDistance > 0.0:
                # Count the interior sibling subtrees
                nLeftSiblings = 0                
                #for (pTempPtr = pThisNode;
                #     pTempPtr && (pTempPtr != pAncestorNeighbor);
                #     pTempPtr = Leftsibling(pTempPtr)) {
                pTempPtr = pThisNode
                while pTempPtr and (pTempPtr != pAncestorNeighbor):
                    nLeftSiblings = nLeftSiblings + 1
                    pTempPtr = pTempPtr.leftSibling

                if pTempPtr:
                    '''
                    Apply portions to appropriate
                    leftsibling subtrees.
                    '''
                    flPortion = flDistance / nLeftSiblings
                    #for (pTempPtr = pThisNode;
                    #pTempPtr != pAncestorNeighbor;
                    #pTempPtr = LeftSibling(pTempPtr)) {
                    pTempPtr = pThisNode
                    while pTempPtr != pAncestorNeighbor:
                        pTempPtr.flPrelim = pTempPtr.flPrelim + flDistance
                        pTempPtr.flModifier = pTempPtr.flModifier + flDistance
                        flDistance = flDistance - flPortion
                        pTempPtr = pTempPtr.leftSibling
                        print "wow"
                else:
                    '''
                    Don't need to move anything--it needs
                    to be done by an ancestor because
                    pAncestorNeighbor and
                    pAncestorLeftmost are not siblings of
                    each other.
                    '''
                    return
            #end of the while
            '''
            Determine the leftmost descendant of pThisNode
            at the next lower level to compare its
            positioning against that of its pNeighbor.
            '''
            nCompareDepth = nCompareDepth + 1
            if pLeftmost.isLeaf():
                pLeftmost = self.tree.getLeftmost(pThisNode, 0, nCompareDepth)
                #pLeftmost = self.tree.getLeftmost(pThisNode, nCurrentLevel, nCompareDepth)
            else:
                pLeftmost = pLeftmost.getFirstChild()
            if pLeftmost:
                pNeighbor = pLeftmost.getLeftNeighbor()
            else: pNeighbor = None
    #!
    def _getPrevNodeAtLevel(self, nLevelNbr):
        """
        List Manipulation: Return pointer to previous node at
        this level
        """
        #~ - kalichno sdelal - prosto for i in len(self.prev_node):
        i = 0
        #for (pTempNode = pLevelZero; (pTempNode); pTempNode = pTempNode->pNextLevel)           #level counter
        for pTempNode in self.prev_node:
            if i == nLevelNbr:
                #Reached desired level.  Return its pointer
                return pTempNode
            i = i + 1
        return None #((PNODE)0); No pointer yet for this level.

    def _setPrevNodeAtLevel(self, nLevelNbr, pThisNode):
        """
        List Manipulation: Set the list element to the
        previous node at this level
        """
        print "+setPrevNodeAt Level ", nLevelNbr, " node ", pThisNode._object
        i = 0
        for pTempNode in self.prev_node:
        
            if i == nLevelNbr:
                #Reached desired level.  Return its pointer
                print "setted level ", i, pThisNode._object
                self.prev_node[i] = pThisNode
                #pTempNode = pThisNode
                return True
            #elif self.prev_node[i + 1] == None:#~
            #elif len(self.prev_node) < (i + 1):
            '''
            elif len(self.prev_node) < (i + 2):
                print "all is ok"
                #pNewNode = TreeNode("node_setPrevNodeAtLevel")#~
                #self.prev_node.append(pNewNode)
                self.prev_node.append(None)
                print "1appended->", pThisNode._object
            '''
            i = i + 1
        #Should only get here if self.prev_node list is empty
        self.prev_node.append(pThisNode)
        print "2appended->", pThisNode._object
        return True

    def _treeFirstWalk(self, pThisNode, nCurrentLevel):
        """
        In a first post-order walk, every node of the tree is
        assigned a preliminary x-coordinate (held in field
        node.flPrelim). In addition, internal nodes are
        given modifiers, which will be used to move their
        children to the right (held in field
        node.flModifier).
        Returns: TRUE if no errors, otherwise returns FALSE.    
        """
        pLeftmost = None            #left- & rightmost
        pRightmost = None           #children of a node.
        flMidpoint = None           #midpoint between left- 
                                    #& rightmost children

        #Set up the pointer to previous node at this level
        pThisNode.prev = self._getPrevNodeAtLevel(nCurrentLevel)
        s = pThisNode.prev
        if s:
            print "-getPrevNodeAt Level ", nCurrentLevel, " node ", pThisNode.prev._object
        else:   print "-getPrevNodeAt Level ", nCurrentLevel, " node None"
        #Now we're it--the previous node at this level        
        if not self._setPrevNodeAtLevel(nCurrentLevel, pThisNode):
            return False   #Can't allocate element

        #Clean up old values in a node's flModifier
        pThisNode.flModifier = 0.0

        if pThisNode.isLeaf() or nCurrentLevel == self.MAXIMUM_DEPTH:
            if pThisNode.hasLeftSibling():
                '''
                Determine the preliminary x - coordinate
                based on:
                -preliminary x - coordinate of left sibling,
                -the separation between sibling nodes, and
                -mean width of left sibling & current node.
                '''
                #Set the mean width of these two nodes 
                self._treeMeanNodeSize(pThisNode.leftSibling, pThisNode)
                pThisNode.flPrelim = pThisNode.leftSibling.flPrelim + self.SIBLING_SEPARATION + self.flMeanWidth        
            else:
                # no sibling on the left to worry about 
                pThisNode.flPrelim = 0.0;    
        else:
            #Position the leftmost of the children
            #if (TreeFirstWalk(pLeftmost = pRightmost = FirstChild(pThisNode), nCurrentLevel + 1)) {
            pLeftmost = pRightmost = pThisNode.getFirstChild()#~
            if (self._treeFirstWalk(pLeftmost, nCurrentLevel + 1)):
                #Position each of its siblings to its right
                #while (HasRightSibling(pRightmost)){
                while pRightmost.hasRightSibling():
                    pRightmost = pRightmost.rightSibling
                    if (self._treeFirstWalk(pRightmost, nCurrentLevel + 1)):
                        pass
                    else: return False#malloc() failed            

                '''
                Calculate the preliminary value between
                the children at the far left and right
                '''
                flMidpoint = (pLeftmost.flPrelim + pRightmost.flPrelim) / 2 
                #Set global mean width of these two nodes 
                self._treeMeanNodeSize(pThisNode.leftSibling, pThisNode)

                if pThisNode.hasLeftSibling():
                    #pThisNode->flPrelim = (pThisNode->leftsibling->flPreLim) + (float)SIBLING_SEPARATION + flMeanWidth;
                    pThisNode.flPrelim = (pThisNode.leftSibling.flPrelim) + self.SIBLING_SEPARATION + self.flMeanWidth
                    pThisNode.flModifier = pThisNode.flPrelim - flMidpoint
                    self._treeApportion(pThisNode, nCurrentLevel)
                else: pThisNode.flPrelim = flMidpoint

            else: return False#Couldn't get an element
        return True
    
    def _treeSecondWalk(self, pThisNode, nCurrentLevel):
        '''
        During a second pre-order walk, each node is given a
        final x-coordinate by summing its preliminary
        x-coordinate and the modifiers of all the node's
        ancestors.  The y-coordinate depends on the height of
        the tree.  (The roles of x and y are reversed for
        RootOrientations of EAST or WEST.)
        Returns: TRUE if no errors, otherwise returns FALSE.
        '''        
        # lxTemp, lyTemp    - hold calculations here
        #flNewModsum        - local modifier value
        bResult = True      # assume innocent
        #self.flModsum = 0.0
        if nCurrentLevel <= self.MAXIMUM_DEPTH:
            flNewModsum = self.flModsum  # Save the current value
            if self.root_orientation == self.NORTH:            
                lxTemp = self.xTopAdjustment + (pThisNode.flPrelim + self.flModsum)
                lyTemp = self.yTopAdjustment + (nCurrentLevel * self.LEVEL_SEPARATION)        
            elif self.root_orientation == self.SOUTH:         
                lxTemp = self.xTopAdjustment + (pThisNode.flPrelim + self.flModsum);
                lyTemp = self.yTopAdjustment - (nCurrentLevel * self.LEVEL_SEPARATION);
            elif  self.root_orientation == self.EAST:
                lxTemp = self.xTopAdjustment + (nCurrentLevel * self.LEVEL_SEPARATION);
                lyTemp = self.yTopAdjustment - (pThisNode.flPrelim + self.flModsum);
            elif  self.root_orientation == self.WEST:
                lxTemp = self.xTopAdjustment - (nCurrentLevel * self.LEVEL_SEPARATION);
                lyTemp = self.yTopAdjustment - (pThisNode.flPrelim + self.flModsum);
                
            if self._checkExtentsRange(lxTemp, lyTemp):
                # The values are within the allowable range
                pThisNode.xCoordinate = lxTemp
                pThisNode.yCoordinate = lyTemp
                pThisNode._object.setPosition(ogre.Vector3(lxTemp, lyTemp, 0))#~                 
                if pThisNode.hasChild():
                    # Apply the flModifier value for this 
                    # node to all its offspring. 
                    self.flModsum = flNewModsum = flNewModsum + pThisNode.flModifier
                    bResult = self._treeSecondWalk(pThisNode.getFirstChild(), nCurrentLevel + 1)
                    flNewModsum = flNewModsum - pThisNode.flModifier

                if (pThisNode.hasRightSibling()) and (bResult):
                    self.flModsum = flNewModsum;
                    bResult = self._treeSecondWalk(pThisNode.rightSibling, nCurrentLevel)
            else: bResult = False    #outside of extents
        return bResult

    def buildTree(self, parentNode):
        #supposed that first element in self.nodes is the root of settable tree
        #for object in self.nodes:
        
        if parentNode:
            #for ls_in in object.linkedObjects['LS_IN']:
            for ls_in in parentNode.getObject().linkedObjects[Object.LS_IN]:
                child = ls_in.getBegin()
                if not (child in self.marked_nodes): 
                    self.marked_nodes.append(child)
                    childNode = TreeNode(child, 0, 0)
                    self.tree.addNode(childNode, parentNode)
                    self.buildTree(childNode)
            #for ls_out in object.linkedObjects['LS_OUT']:
            for ls_out in parentNode.getObject().linkedObjects[Object.LS_OUT]:
                child = ls_out.getEnd()
                if not (child in self.marked_nodes): 
                    self.marked_nodes.append(child)
                    childNode = TreeNode(child, 0, 0)
                    self.tree.addNode(childNode, parentNode)
                    self.buildTree(childNode)

    def _layoutTree(self, tree):
        '''
        Determine the coordinates for each node in a tree.
        Input: Pointer to the apex node of the tree
        Assumption: The x & y coordinates of the apex node
        are already correct, since the tree underneath it
        will be positioned with respect to those coordinates.        
        Returns: TRUE if no errors, otherwise returns FALSE.
        '''
        self.tree = tree
        pApexNode = self.tree.getRoot()
        if self._treeFirstWalk(pApexNode, 0):
            '''        
            Determine how to adjust the nodes with
            respect to the location of the apex of the
            tree being positioned.
            '''
            if self.root_orientation == self.NORTH or self.root_orientation == self.SOUTH:         
                # Create the adjustment from x-coord
                self.xTopAdjustment = pApexNode.xCoordinate - pApexNode.flPrelim
                self.yTopAdjustment = pApexNode.yCoordinate
            else:            
                # Create the adjustment from y-coord
                self.xTopAdjustment = pApexNode.xCoordinate
                self.yTopAdjustment = pApexNode.yCoordinate + pApexNode.flPrelim

            return self._treeSecondWalk(pApexNode, 0)
        else: return False # Couldn't get apex (root) element

    def _setTree(self, tree):
        self.tree = tree
        #_apply and other updates
    
    def _apply(self):
        """Applies hierarchical layout to group
        """
        LayoutGroupDepth._apply(self)
        if len(self.nodes) > 0:
            self.tree = Tree()
            rootObject = self.nodes[0]
            print "rootObject.position: ", rootObject.position
            rootNode = TreeNode(rootObject, 0, 0)
            self.tree.setRoot(rootNode)
            self.marked_nodes = []
            self.buildTree(rootNode)
        if self.tree == None:
            return
        else:
            self._layoutTree(self.tree)
            self.needModeUpdate = False
            self.need_layout = False
            
    def rotate(self, cnt):
        pass

    def getLineLength(self, cnt):
        """Calculates length for a line depending on output/input arcs count
        """
        return max([self.length, cnt / 3.0])

    def getLinkedCount(self, obj):
        return len(obj.linkedObjects[Object.LS_OUT]) + len(obj.linkedObjects[Object.LS_IN])
