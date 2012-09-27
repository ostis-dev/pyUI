
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
Created on 01.12.2009

@author: Denis Koronchik
'''

import ogre.renderer.OGRE as ogre
import suit.core.kernel as core
import suit.core.render.engine as render_engine
import scg_objects
import suit.core.objects as objects


# elements description
elementsDescMap = {}
# number of created elements
createdElementsCount = 0
# kernel object
kernel = core.Kernel.getSingleton()

def initialize_code():
    """SCg code initialization
    @todo: make code description from sc-memory
    """
   
    # create description for nodes
   
    addElementDescription('mnode', ['scg_struct_struct.mesh'])
    addElementDescription('mpair', [objects.ObjectLine.LET_NONE])

    addElementDescription('node/-/elem', ['scg_struct_struct.mesh'])    
    # constant nodes
    addElementDescription('node/const/elem', ['scg_node_const.mesh'])
    addElementDescription('node/const/sheaf', ['scg_node_const.mesh', 'scg_struct_linker.mesh'])
    addElementDescription('node/const/abstract', ['scg_node_const.mesh', 'scg_struct_abstract_const.mesh'])
    addElementDescription('node/const/binary', ['scg_node_const.mesh', 'scg_struct_binary.mesh'])
    addElementDescription('node/const/real', ['scg_node_const.mesh', 'scg_struct_real_const.mesh'])
    addElementDescription('node/const/role', ['scg_node_const.mesh', 'scg_struct_role.mesh'])
    addElementDescription('node/const/struct', ['scg_node_const.mesh', 'scg_struct_struct.mesh'])
    addElementDescription('node/const/term', ['scg_node_const.mesh', 'scg_struct_term.mesh'])
    # variable nodes
    addElementDescription('node/var/elem', ['scg_node_var.mesh'])
    addElementDescription('node/var/sheaf', ['scg_node_var.mesh', 'scg_struct_linker.mesh'])
    addElementDescription('node/var/abstract', ['scg_node_var.mesh', 'scg_struct_abstract_var.mesh'])
    addElementDescription('node/var/binary', ['scg_node_var.mesh', 'scg_struct_binary.mesh'])
    addElementDescription('node/var/real', ['scg_node_var.mesh', 'scg_struct_real_var.mesh'])
    addElementDescription('node/var/role', ['scg_node_var.mesh', 'scg_struct_role.mesh'])
    addElementDescription('node/var/struct', ['scg_node_var.mesh', 'scg_struct_struct.mesh'])
    addElementDescription('node/var/term', ['scg_node_var.mesh', 'scg_struct_term.mesh'])
    # meta nodes
    addElementDescription('node/meta/elem', ['scg_node_meta.mesh'])
    addElementDescription('node/meta/sheaf', ['scg_node_meta.mesh', 'scg_struct_linker.mesh'])
    addElementDescription('node/meta/abstract', ['scg_node_meta.mesh', 'scg_struct_abstract_meta.mesh'])
    addElementDescription('node/meta/binary', ['scg_node_meta.mesh', 'scg_struct_binary.mesh'])
    addElementDescription('node/meta/real', ['scg_node_meta.mesh', 'scg_struct_real_meta.mesh'])
    addElementDescription('node/meta/role', ['scg_node_meta.mesh', 'scg_struct_role.mesh'])
    addElementDescription('node/meta/struct', ['scg_node_meta.mesh', 'scg_struct_struct.mesh'])
    addElementDescription('node/meta/term', ['scg_node_meta.mesh', 'scg_struct_term.mesh'])
    
    # @todo: remove materials from pair description
    
    # pair/<pos|neg|fuz|->/<time|->/<orient|noorient>/<const|var|meta|->/
    # constant lines
    addElementDescription('pair/-/-/-/-', [objects.ObjectLine.LET_NONE])
    
    addElementDescription('pair/-/-/-/const', [objects.ObjectLine.LET_NONE])
    addElementDescription('pair/-/-/-/var', [objects.ObjectLine.LET_NONE])
    addElementDescription('pair/-/-/-/meta', [objects.ObjectLine.LET_NONE])
    
    addElementDescription('pair/-/-/orient/const', [objects.ObjectLine.LET_END])
    addElementDescription('pair/-/-/orient/var', [objects.ObjectLine.LET_END])
    addElementDescription('pair/-/-/orient/meta', [objects.ObjectLine.LET_END])
    
    addElementDescription('pair/fuz/-/orient/const', [objects.ObjectLine.LET_END])
    addElementDescription('pair/fuz/-/orient/var', [objects.ObjectLine.LET_END])
    addElementDescription('pair/fuz/-/orient/meta', [objects.ObjectLine.LET_END])
    
    addElementDescription('pair/fuz/time/orient/const', [objects.ObjectLine.LET_END])
    addElementDescription('pair/fuz/time/orient/var', [objects.ObjectLine.LET_END])
    addElementDescription('pair/fuz/time/orient/meta', [objects.ObjectLine.LET_END])
    
    addElementDescription('pair/neg/-/orient/const', [objects.ObjectLine.LET_END])
    addElementDescription('pair/neg/-/orient/var', [objects.ObjectLine.LET_END])
    addElementDescription('pair/neg/-/orient/meta', [objects.ObjectLine.LET_END])
                          
    addElementDescription('pair/neg/time/orient/const', [objects.ObjectLine.LET_END])
    addElementDescription('pair/neg/time/orient/var', [objects.ObjectLine.LET_END])
    addElementDescription('pair/neg/time/orient/meta', [objects.ObjectLine.LET_END])
    
    addElementDescription('pair/pos/-/orient/const', [objects.ObjectLine.LET_END])
    addElementDescription('pair/pos/-/orient/var', [objects.ObjectLine.LET_END])
    addElementDescription('pair/pos/-/orient/meta', [objects.ObjectLine.LET_END])
                          
    addElementDescription('pair/pos/time/orient/const', [objects.ObjectLine.LET_END])
    addElementDescription('pair/pos/time/orient/var', [objects.ObjectLine.LET_END])
    addElementDescription('pair/pos/time/orient/meta', [objects.ObjectLine.LET_END])
    
    
    
    
def addElementDescription(name, desc):
    """Add new element description to scg-code
    @raise NameError:
    """
    if (elementsDescMap.has_key(name)):
        raise   NameError('description for node \'' + name + '\' already exists')
        return
    
    # store description
    elementsDescMap[name] = desc
    kernel.logManager.message('added new scg element \'' + name + '\' with description: ' + str(desc))
    

def removeElementDescription(name):
    """Remove element description
    @raise NameError: 
    """
    global nodesDescriptionMap 
    if (not elementsDescMap.has_key(name)):
        raise   NameError('Can\'t find description for element \'' + name + '\'')
        return
    
    # remove from map
    elementsDescMap.pop(name)
    
def createElementSceneNode(el_name):
    """Create new scene node for element
    @raise NameError:  
    """
    # get description
    global elementsDescMap
    if (not elementsDescMap.has_key(el_name)):
        raise   NameError('Can\'t find element \'' + el_name + '\'')
    
    # create new scene node
    global createdElementsCount
    sceneNode = render_engine.SceneManager.createSceneNode()
    desc = elementsDescMap[el_name]
    i = 0
    for mesh in desc:
        entity = render_engine.SceneManager.createEntity(el_name + str(createdElementsCount) + str(i), mesh)
        entity.setMaterialName('scg_empty')
        sceneNode.attachObject(entity)
        i = i + 1
#    sceneNode.setScale(0.5, 0.5, 0.5)
    
    createdElementsCount = createdElementsCount + 1 
        
    return sceneNode

def createSCgNode(type_name):
    """Create scg-node by type name
    @param type_name: node type name
    """
    return scg_objects.SCgNode(createElementSceneNode(type_name),type_name)

def createSCgPair(type_name):
    """Create scg-pair by type name
    @param type_name: pair type name
    
    @change: 18.09.09 renamed createSCgLine to createSCgPair
    """
    # find description
    descr = elementsDescMap[type_name]
    if (not descr) or (len(descr) != 1):
        raise AssertionError('Invalid pair description \'' + type_name + '\'' )
    return scg_objects.SCgPair(render_engine.SceneManager.createSceneNode(),
                   'scg_empty', descr[0], type_name)
    
def createContour():
    """Create scg-contour
    """
    return scg_objects.SCgContour(render_engine.SceneManager.createSceneNode())

def changeObjectType(_obj, _type):
    """Changing node type
    """
    _type = str(_type)
    if _type[:4] == "node":
        #pos = self.sceneNode.getPosition()
        #sn = sceneManager.createSceneNode()
        n = _obj.sceneNode.numAttachedObjects()
        for i in range(n):
            obj = _obj.sceneNode.getAttachedObject(0)
            _obj.sceneNode.detachObject(0)
            render_engine.SceneManager.destroyEntity(obj)
        #self.sceneNode.detachAllObjects()
        global createdElementsCount        
        desc = elementsDescMap[_type]
        i = 0
        for mesh in desc:
            entity = render_engine.SceneManager.createEntity(_type + str(createdElementsCount) + str(i), mesh)
            #entity.setMaterialName('empty')
            _obj.sceneNode.attachObject(entity)
            i = i + 1
        createdElementsCount = createdElementsCount + 1 
        #sn.setPosition(pos)
        #self.setSceneNode(sn)
        _obj.type = _type
        _obj.needStateUpdate = True
        
    elif _type[:4] == "pair":
        descr = elementsDescMap[_type]
        if (not descr) or (len(descr) != 1):
            raise AssertionError('Invalid pair description \'' + _type + '\'' )
        _obj._lineEndsType = descr[0]
        _obj.setType(_type)
        # recreating arrows
        _obj._recreateArrows2d(False)
        
def get_pair_types():
    """Return list of pair type aliases
    @return: list of pair type aliases
    @rtype: list
    """
    res = []
    for alias in elementsDescMap.iterkeys():
        if alias.startswith('pair'):
            res.append(alias)
    return res

def get_node_types():
    """Return list of node type aliases
    @return: list of node type aliases
    @rtype: list
    """
    res = []
    for alias in elementsDescMap.iterkeys():
        if alias.startswith('node'):
            res.append(alias)
    return res