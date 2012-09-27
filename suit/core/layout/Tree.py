'''
Created on 09.04.2010

@author: Uomo
'''

class TreeNode:
    _object = None
    parent = None
    offspring = None
    leftSibling = None
    rightSibling = None
    xCoordinate = None
    yCoordinate = None
    prev = None
    flPrelim = None
    flModifier = None
    '''
    def __init__(self, _object, parent, offspring, leftSibling, rightSibling, xCoordinate, yCoordinate, prev):        
        self.data = _object
        #----------------------------------------------------------
        self.parent = parent                #ptr: node's parent
        self.offspring = offspring          #ptr: leftmost child
        self.leftSibling = leftSibling      #ptr: sibling on left
        self.rightSibling = rightSibling    #ptr: sibling on right
        self.xCoordinate = xCoordinate      #node's current x coord
        self.yCoordinate = yCoordinate      #node's current y coord
        #----------------------------------------------------------
        self.prev = prev                    #ptr: lefthand neighbor
        self.flPrelim                       #preliminary x coord
        self.flModifier                     #temporary modifier
    '''    
    def __init__(self, _object, xCoordinate, yCoordinate):
        self._object = _object
        self.xCoordinate = xCoordinate      #node's current x coord
        self.yCoordinate = yCoordinate      #node's current y coord

    def getObject(self):
        return self._object
        
    def getParent(self):
        return self.parent
    #TODO:
    def addChild(self, _object):
        self.children.append(_object)
        
    def hasChild(self):
        if self.offspring:
            return True
        return False
    
    def isLeaf(self):
        if self.offspring:
            return False
        return True
    
    def hasLeftSibling(self):
        if self.leftSibling:
            return True
        return False
    
    def hasRightSibling(self):
        if self.rightSibling:
            return True
        return False
    
    def getFirstChild(self):
        # skoree vsego lishnii metod, mona oboitis' prosto obrascheniem k atributu
        return self.offspring
    
    def getLeftNeighbor(self):
        return self.prev


class Tree:
    def __init__(self):
        #self.RootOrientation=0
        self.root = None
        
    def setRoot(self, rootNode):
        self.root = rootNode
        
    def getRoot(self):
        return self.root
    
    def addNode(self, newNode, parentNode):        
        if self.root == None:
            self.root = parentNode
        #check if such node as parentNode already have been added to the tree
        #else raise something
        newNode.parent = parentNode
        if parentNode.offspring == None:
            parentNode.offspring = newNode
            #trying to set node's lefthand neighbor - self.prev
            #newNode.prev =self.getPrev(parentNode)
            '''
            leftSibling = parentNode.leftSibling
            if leftSibling != None:
                if leftSibling.offspring != None:
                    newNode.prev = self.getRightMostOfParent(leftSibling.offspring)
                    print "setted prev: ", newNode.prev._object
            '''
        else:
            #set leftSibling and, if it exist - rightSibling
            leftSibling = self.getRightMostOfParent(parentNode.offspring)         
            newNode.leftSibling = leftSibling
            leftSibling.rightSibling = newNode
            '''
            rightSibling = parentNode.rightSibling
            if rightSibling != None:
                if rightSibling.offspring != None:
                    rightSibling.offspring.prev = newNode
                    #newNode.prev = self.getRightMostOfParent(leftSibling.offspring)
                    print "setted new prev: ", rightSibling.offspring.prev._object
            '''
    def getRightMostOfParent(self, node):        
        if node.rightSibling != None:            
            return self.getRightMostOfParent(node.rightSibling)
        else: return node

    def insert(self, root, data):
        # inserts a new data
        if root == None:
            # it there isn't any data
            # adds it and returns
            return self.addNode(data)
        else:
            # enters into the tree
            if data <= root.data:
                # if the data is less than the stored one
                # goes into the left-sub-tree
                root.left = self.insert(root.left, data)
            else:
                # processes the right-sub-tree
                root.right = self.insert(root.right, data)
            return root

    def getLeftmost(self, pThisNode, nCurrentLevel, nSearchDepth):    
        '''
        Determine the leftmost descendant of a node at a
        given depth. This is implemented using a post-order
        walk of the subtree under pThisNode, down to the
        level of nSearchDepth. If we've searched to the
        proper distance, return the currently leftmost node.
        Otherwise, recursively look at the progressively
        lower levels.
        '''
        # pLeftmost    - leftmost descendant at level 
        # pRightmost   - rightmost offspring in search
        if nCurrentLevel == nSearchDepth:
            pLeftmost = pThisNode   # searched far enough. 
        else:
            if pThisNode.isLeaf():#~
                pLeftmost = None # This node has no descendants
            else:
                # Do a post - order walk of the subtree.
                pRightmost = pThisNode.getFirstChild()
                pLeftmost = self.getLeftmost(pRightmost, nCurrentLevel + 1, nSearchDepth)
                while (pLeftmost == None) and (pRightmost.hasRightSibling()):
                    pRightmost = pRightmost.rightSibling
                    pLeftmost = self.getLeftmost(pRightmost, nCurrentLevel + 1, nSearchDepth)
                    #Nothing inside this for - loop.
        return pLeftmost
