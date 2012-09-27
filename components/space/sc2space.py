
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

@author: Kate Romanenko
'''

"""sc -> space translator component
"""
from suit.core.objects import Translator
import suit.core.objects as objects
import suit.core.kernel as core
import space_env as env
import sc_core.pm as sc
import sc_core.constants as sc_constants
import suit.core.keynodes as keynodes
import suit.core.sc_utils as sc_utils
import space_keynodes as space_keynodes
import space_objects
import suit.core.exceptions as exceptions
import ogre.renderer.OGRE as ogre
import suit.core.render.engine as render_engine
from space_objects import SpaceObject

# resource group manager
resourceGroupManager = None
# scene manager
sceneManager = None
# kernel
kernel = core.Kernel.getSingleton()
# log manager
logManager = kernel.logManager
# light source
light = render_engine._ogreLight
viewBackground = None
# counter of all sheets with format SPACEx 
spaceSheetCount = 0


###############################################
# functions that need to be reviewed
def searchPosArcFrom(_session, _el):
    """Returns all elements include in current _el
    @param _el    element for searching in
    @type _el:    sc_global_addr
    @param _session:    current session
    @type _session:    MThreadSession
    
    @return: all elements includes in _el by positive arc
    @rtype: list[sc_global_addr]
    """
    resultSet = []
    it = _session.create_iterator(_session.sc_constraint_new(sc_constants.CONSTR_3_f_a_a,
                                                               _el,
                                                               sc.SC_A_CONST | sc.SC_POS,
                                                               0), True)
    while not it.is_over():
        resultSet.append(it.value(2))
        it.next()
    return resultSet

def searchOneShotPosArcAttrFrom(_session, _el, _attr):
    """Searches positive arc with attribute
    @see: searchPosArcAttrFrom
    """
    return sc_utils.searchOneShot(searchPosArcAttrFrom(_session, _el, _attr))

def searchPosArcAttrFrom(_session, _el, _attr):
    """Returns all elements with attribute _attr include in current _el
    @param _session:    current session
    @type _session:    MThreadSession
    @param _el    element for searching in
    @type _el:    sc_global_addr
    @param _attr    attribute
    @type _attr:    sc_global_addr
    @return: all elements includes in _el by positive arc with attribute _attr
    @rtype: list[sc_global_addr]
    """

    resultSet = []
    it = _session.create_iterator(_session.sc_constraint_new(sc_constants.CONSTR_5_f_a_a_a_f,
                                                                _el,
                                                               sc.SC_A_CONST | sc.SC_POS,
                                                               0,
                                                               sc.SC_A_CONST | sc.SC_POS,
                                                               _attr), True)
    while not it.is_over():
       resultSet.append(it.value(2))
       it.next()
    
    return resultSet

def searchBinPairsFromNode(_session, _beg, _const):
    """Searches full data for all binary orient pairs with specified begin element
    @param _session:    session to work with
    @type _session: MThreadSession
    @param _beg:    begin element of pair
    @type _beg:    sc_global_addr
    @param _const:    pair constant type
    @type _const:    int
        
    @return:    list of tuple(rel, end)
    @rtype:     list
    
    @raise RuntimeWarning:    if structure of binary orient pair is wrong
    
    template:
                x ? rel
                |
                v
        O =============> ? (node to find)
     _beg                
    """
    
    res = []
    # finding sheaf node
    it1 = _session.create_iterator(_session.sc_constraint_new(sc_constants.CONSTR_5_a_a_f_a_f,
                                                           sc.SC_NODE | _const,
                                                           sc.SC_ARC | sc.SC_POS | _const,
                                                           _beg,
                                                           sc.SC_ARC | sc.SC_POS | _const,
                                                           keynodes.n_1), True)
    while not it1.is_over():
        # check if founded node is sheaf
        sheaf_node = it1.value(0)
        if sc_utils.isNodeSheaf(_session, sheaf_node):
            #finding relation node
            list1 = searchPosArcTo(_session, sheaf_node)
            rel_node = None
            for el in list1:
                idtf = str(sc_utils.cp1251ToUtf8(_session.get_idtf(el)))
                if not idtf.__eq__("stype_sheaf"):
                    rel_node=el
                                
            # finding end node
            it2 = _session.create_iterator(_session.sc_constraint_new(sc_constants.CONSTR_5_f_a_a_a_f,
                                                                   sheaf_node,
                                                                   sc.SC_ARC | sc.SC_POS | _const,
                                                                   sc.SC_NODE,
                                                                   sc.SC_ARC | sc.SC_POS | _const,
                                                                   keynodes.n_2), True)
            end_el = None
            while not it2.is_over():
                if end_el is None:
                    end_el = it2.value(2)
                else:
                    raise RuntimeWarning("Invalid binary orient pair")
                it2.next()
                
            if end_el is not None:   res.append((rel_node, end_el))
            
        it1.next()
   
    return res

def searchPosArcTo(_session, _el):
    """Returns all "1" element    
    1?--------->_el
    @param _el    element for searching in
    @type _el:    sc_global_addr
    @param _session:    current session
    @type _session:    MThreadSession
    
    @return: 
    @rtype: list[sc_global_addr]
    """
    resultSet = []
    it = _session.create_iterator(_session.sc_constraint_new(sc_constants.CONSTR_3_a_a_f,
                                                               0,
                                                               sc.SC_A_CONST | sc.SC_POS,
                                                               _el), True)
    while not it.is_over():
        resultSet.append(it.value(0))
        it.next()
    return resultSet

def searchFullPosArcFrom(_session, _beg, _end):
    """Returns all elements include in current _el
    @param _el    element for searching in
    @type _el:    sc_global_addr
    @param _session:    current session
    @type _session:    MThreadSession
        ? attr
        |
        |
        v
    _beg------>_end
    @return: list[tuple(_beg,attr,_end),...]
    @rtype: list
    """
    resultSet = []
    it = _session.create_iterator(_session.sc_constraint_new(sc_constants.CONSTR_5_f_a_f_a_a,
                                                               _beg,
                                                               sc.SC_A_CONST | sc.SC_POS,
                                                               _end,
                                                               sc.SC_A_CONST | sc.SC_POS,
                                                               sc.SC_NODE), True)
    while not it.is_over():
        resultSet.append((_beg,it.value(4),_end))
        it.next()
    return resultSet

###############################################

def checkInputObjects(session, objects):
    """Check if objects contains sc_global_addr variable, which could became
    an instance of class SpaceObject
    @param session:  current workable session
    @type session:   sc_session
    @param objects:   list of input objects which we are checking
    @type objects:    list[sc_global_addr,..]
        
    @return: true if it's contains, false otherwise
    @rtype: bool
    """
    starKey = space_keynodes.SpaceRelation.star
    planetKey = space_keynodes.SpaceRelation.planet
    
    result = False
    for object in objects:
        incl1 = sc_utils.checkIncToSets(session, object, [starKey], sc.SC_A_CONST | sc.SC_POS)
        incl2 = sc_utils.checkIncToSets(session, object, [planetKey], sc.SC_A_CONST | sc.SC_POS)
        if incl1 or incl2: 
            result = True
            break
    return result            
    

def findAllPlanetProperties(session, planet):
    """
    @param session:  current workable session
    @type session:   sc_session
    @param planet:   planet which properties we are finding
    @type planet:    sc_global_addr
        
    @return: list of the planet properties
    @rtype: list[tuple(key,value,unit),...]
    """
    
    identficationKey = keynodes.common.nrel_identification
    dec_system = space_keynodes.DefaultAttr.dec_system
    properties=[]
 
    list1 = searchBinPairsFromNode(session, planet, sc.SC_CONST)
    
    for el in list1:
         list2 = searchPosArcFrom(session, el[1])
         if len(list2)>0:
             addr1 = list2[0]
             list3 = searchFullPosArcFrom(session, el[1], addr1)
             attr = list3[0][1]
             rel = el[0]
             prop_name = str(sc_utils.cp1251ToUtf8(session.get_idtf(rel)))
             prop_name = prop_name.rstrip('*')
             unit_name = str(sc_utils.cp1251ToUtf8(session.get_idtf(attr)))
             unit_name = unit_name.rstrip('_')
             unit_name = unit_name.replace("значение", "")
             prop_value = str(findPlanetProperty(session, planet, rel, attr))
           
             properties.append((prop_name, prop_value, unit_name))   
    
    chemistry = findPlanetAtmosphChemistry(session, planet);
    properties.append(chemistry)
     
    return properties


def findPlanetProperty(session, planet, property, unit_attr):
    """
    @param session:  current workable session
    @type session:   sc_session
    @param planet:   planet which property we are finding
    @type planet:    sc_global_addr
    @param property:   property keynode
    @type property:    sc_global_addr
    @param unit_attr:   property unit attribute keynode
    @type unit_attr:    sc_global_addr
    
    @return: property value of the planet
    @rtype: str 
    """
    
    identficationKey = keynodes.common.nrel_identification
    dec_system = space_keynodes.DefaultAttr.dec_system
 
    addr1 = sc_utils.searchOneShotBinPairAttrFromNode(session, planet, property, sc.SC_N_CONST)
    if addr1 is not None:
        addr2 = searchOneShotPosArcAttrFrom(session, addr1, unit_attr)
        addr3 = sc_utils.searchOneShotBinPairAttrToNode(session, addr2, identficationKey, sc.SC_N_CONST)
        addr4 = searchPosArcAttrFrom(session, addr3, dec_system)
        for addr in addr4:
            content = session.get_content_str(addr)
            if content is not None:
                return sc_utils.cp1251ToUtf8(str(content))
        
    return None

def findFloatPlanetProperty(session, planet, property, unit_attr):
    """
    @param session:  current workable session
    @type session:   sc_session
    @param planet:   planet which property we are finding
    @type planet:    sc_global_addr
    @param property:   property keynode
    @type property:    sc_global_addr
    @param unit_attr:   property unit attribute keynode
    @type unit_attr:    sc_global_addr
    
    @return: property of the planet
    @rtype: float 
    """
    
    prop = findPlanetProperty(session, planet, property, unit_attr)
    if prop is not None:
        return float(prop)
    else:
        return 0
    
def findPlanetAtmosphChemistry(session, planet):
    """
    @param session:  current workable session
    @type session:   sc_session
    @param planet:   planet which radius we are finding
    @type planet:    sc_global_addr
    
    @return: chemistry of the planet
    @rtype: tuple(property_name, [tuple(substance_name, percent),...],unit_name) 
    """
    atmosphereKey = space_keynodes.SpaceRelation.atmosphere
    chemistryKey = space_keynodes.SpaceRelation.chemistry
    
    prop_name = str(sc_utils.cp1251ToUtf8(session.get_idtf(atmosphereKey)))
    prop_name = prop_name.replace('*', '')
        
    result=None
    
    addr1 = sc_utils.searchOneShotBinPairAttrFromNode(session, planet, atmosphereKey, sc.SC_N_CONST)    
    if addr1 is not None:
        addr2 = sc_utils.searchOneShotBinPairAttrFromNode(session, addr1, chemistryKey, sc.SC_N_CONST)
        chemistry = findAllPlanetProperties(session, addr2)
        items = []
        unit_name = ""
        for chem in chemistry:
            if chem is not None:
                name, value, unit_name = chem
                item = (name, value)
                items.append(item)
                result = (prop_name, items, unit_name)
    return result
        
def findPlanetTitle(session, planet, language):
    """
    @param session:  current workable session
    @type session:   sc_session
    @param planet:   planet which title we are finding
    @type planet:    sc_global_addr
    @param language:   language of title
    @type language:    sc_global_addr
    
    @return: title of the planet
    @rtype: string 
    """
    identficationKey = keynodes.common.nrel_identification
    
    addr1 = sc_utils.searchOneShotBinPairAttrToNode(session, planet, identficationKey, sc.SC_N_CONST)
    if addr1 is not None:
        addr2 = searchPosArcFrom(session, addr1) 
        for addr in addr2:
            is_spec_lang = sc_utils.checkIncToSets(session, addr, [language], sc.SC_A_CONST)
            if is_spec_lang is True:
                content = session.get_content_str(addr)
                if content is not None:
                    return sc_utils.cp1251ToUtf8(content)
    return None
 

def findCentralStar(session, planets):
    """ 
    Finds parent planet. Another planets turn around it.
    @param session:  current workable session
    @type session:   sc_session
    @param planets:   all planets 
    @type planets:    list[sc_global_addr]
    
    @return: parent planet
    @rtype: sc_global_addr 
    """
    parent = None
    star = space_keynodes.SpaceRelation.star
    for planet in planets:
        isStar = sc_utils.checkIncToSets(session, planet, [star], sc.SC_A_CONST)
        if isStar:
            parent = planet
    return parent        
    
def findChildPlanets(session, parent):
    """
    Find planets which turn around parent planet.
    @param session:  current workable session
    @type session:   sc_session
    @param parent:   parent planet 
    @type parent:    sc_global_addr
    
    @return: child planets
    @rtype: list[sc_global_addr] 
    """
    turn_around = space_keynodes.SpaceRelation.turn_around
    childs = addr2 = sc_utils.searchBinPairsAttrToNode(session, parent, turn_around, sc.SC_N_CONST)
    return childs
   
def createSystem(session, parent):
    """
    @param session:  current workable session
    @type session:   sc_session
    @param parent:   parent planet 
    @type parent:    sc_global_addr
    
    @return: system of planets
    @rtype: tuple([String],[tuple]);
    """
    parentData = createPlanetData(session, parent)
    parentSystem = (parentData, []) 
    
    childs = findChildPlanets(session, parent)
    for child in childs:
        childSystem = createSystem(session, child)
        parentSystem[1].append(childSystem);
        
    return parentSystem;      
        
def createPlanetData(session, planet):
    """ 
    Create list of planet properties, which uses when 
    new SpaceObject is creating    
    @param session:  current workable session
    @type session:   sc_session
    @param planet:   planet 
    @type planet:    sc_global_addr
    
    @return: list of planet properties 
    @rtype: list[]
    """
    lang = core.Kernel.getSingleton().getCurrentTranslation()#keynodes.common.group_russian_language
    title = findPlanetTitle(session, planet, lang)
    
    radiusKey = space_keynodes.SpaceRelation.radius
    unit = space_keynodes.DefaultAttr.unit_kilometre
    radius = findFloatPlanetProperty(session, planet, radiusKey, unit)
    
    sidPeriodKey = space_keynodes.SpaceRelation.sidereal_period
    unit = space_keynodes.DefaultAttr.unit_day
    siderPeriod = findFloatPlanetProperty(session, planet, sidPeriodKey, unit)
    
    bigAxleKey = space_keynodes.SpaceRelation.big_axle
    unit = space_keynodes.DefaultAttr.unit_kilometre
    bigAxle = findFloatPlanetProperty(session, planet, bigAxleKey, unit)
    bigAxle = bigAxle/1000.0
    
    dayKey = space_keynodes.SpaceRelation.period_of_revol
    unit = space_keynodes.DefaultAttr.unit_day
    day = findFloatPlanetProperty(session, planet, dayKey, unit)
        
    properties = findAllPlanetProperties(session, planet)
        
    data = [bigAxle,bigAxle,(0,0,0),siderPeriod,day,title,radius,properties,planet]
    
    return data

def _buildSystem(data, parent):
    """Builds system for data and parent object
    """
    global spaceSheetCount
    global sceneManager
    info = data[0]
    childs = data[1]
    
    oscale = 0.001
    rscale = 0.0001
    timeScale = 1.0
            
    A = info[0] * oscale
    B = info[1] * oscale
    orbitPos = info[2]
    year = info[3] * timeScale
    day = info[4] * timeScale
    title = info[5]
    scale = info[6] * rscale / 2.0
    prop = info[7]
    addr = info[8]

    if parent is None:
        sn = sceneManager.createSceneNode()
        name = "Sun"+str(spaceSheetCount)
        psystem = sceneManager.createParticleSystem(name, "Space/Sun")
        sn.attachObject(psystem)
        scale = 1.0
        spaceSheetCount=spaceSheetCount+1
    else:
        # creating scene node
        sn = sceneManager.createSceneNode()
        entity = sceneManager.createEntity(str(sn), "Sphere_32x32.mesh")
        matName = 'space/None'
        sn.attachObject(entity)
    
    object = SpaceObject(sn, None, A, B, orbitPos, year, day, title, scale, prop)
    object._setScAddr(addr)
    object.needStateUpdate = True
    if parent is not None:  parent.addChild(object)
    
    for child in childs:
        _buildSystem(child, object)
    
    return object  

class TranslatorSc2Space(Translator):
    """Class that realize translation from SC-code directly to scg-window
    """    
    def __init__(self):
        Translator.__init__(self)
        global sceneManager
        sceneManager = render_engine._ogreSceneManager    
 
        
    def __del__(self):
        Translator.__del__(self)
        
    def translate_impl(self, input, output):
        """Translator implementation
        @param input:    input data set
        @type input:    sc_global_addr
        @param output:    output window (must be created)
        @type output:    sc_global_addr
        
        @return: list of errors each element of list is a tuple(object, error)
        @rtype: list
        """
        global sun
        errors = []
        
        # FIXME:    think about multiply windows for one sc-element
        # get SheetObject from the output
        objs = objects.ScObject._sc2Objects(output)
        
        assert len(objs) > 0
        sheet = objs[0]
        assert isinstance(sheet, objects.ObjectSheet)
        
        session = core.Kernel.session()
        
        space_segment = session.open_segment(env.segment_root)
        input_objects = searchPosArcFrom(session, input)
        if len(input_objects)!= 0:
            if not checkInputObjects(session, input_objects):
                msg = u"Cannot create any SpaceObject from input"
                errors.append((input_objects, msg))
            else:    
                parent = findCentralStar(session, input_objects)
                if parent is None:
                    parent = input_objects[0]
                system = createSystem(session, parent)
                sun = _buildSystem(system, None)
                sheet.addChild(sun)
                sheet.getLogic().play()
        else:
            msg = u"Input is empty"
            errors.append((input_objects, msg))
       
        return errors
       
            
