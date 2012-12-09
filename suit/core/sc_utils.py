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
Created on 08.01.2010

@author: Denis Koronchik
'''
import sc_core.pm as sc
import sc_core.constants as sc_constants
import keynodes

def utf8ToCp1251(text):
    """Converts utf-8 string to cp1251
    """
    return text.decode('utf-8').encode('cp1251')

def cp1251ToUtf8(text):
    """Converts cp1251 string to utf-8 string
    """
    return unicode(text.decode('cp1251'))


def createPairBinaryOrientFull(_session, _segment, _beg, _end, _const):
    """Creates binary orient pair    (O==========>O)
    @param _session:    session to create pair in
    @type _session:    MThreadSession
    @param _segment:    segment to create pair in
    @type _segment:    sc_segment
    @param _beg:    begin element for a pair
    @type _beg:    sc_global_addr
    @param _end:    end element for a pair
    @type _end:    sc_global_addr
    @param _types:    constant type
    @type _types:    int
    
    @return: returns list of all used sc-elements
    @rtype: sc_global_addr
    """
    rel_node = createNodeSheaf(_session, _segment, _const)    
    # FIXME:    positive pair constant depending on binary pair constant 
    a1 = createPairPosPerm(_session, _segment, rel_node, _beg, _const)
    a2 = createPairPosPerm(_session, _segment, rel_node, _end, _const)
    a3 = createPairPosPerm(_session, _segment, keynodes.n_1, a1, _const)
    a4 = createPairPosPerm(_session, _segment, keynodes.n_2, a2, _const)
    return [rel_node, a1, a2, a3, a4, keynodes.n_1, keynodes.n_2]

def createPairBinaryOrient(_session, _segment, _beg, _end, _const):
    """Creates binary orient pair    (O==========>O)
    @param _session:    session to create pair in
    @type _session:    MThreadSession
    @param _segment:    segment to create pair in
    @type _segment:    sc_segment
    @param _beg:    begin element for a pair
    @type _beg:    sc_global_addr
    @param _end:    end element for a pair
    @type _end:    sc_global_addr
    @param _types:    constant type
    @type _types:    int
    
    @return: returns node that designate sheaf
    @rtype: sc_global_addr
    """
    rel_node = createNodeSheaf(_session, _segment, _const)    
    # FIXME:    positive pair constant depending on binary pair constant 
    a1 = createPairPosPerm(_session, _segment, rel_node, _beg, _const)
    a2 = createPairPosPerm(_session, _segment, rel_node, _end, _const)
    createPairPosPerm(_session, _segment, keynodes.n_1, a1, _const)
    createPairPosPerm(_session, _segment, keynodes.n_2, a2, _const)
    return rel_node


def createPairBinaryNoOrientFull(_session, _segment, _beg, _end, _const):
    """Creates binary orient pair    (O==========O)
    @param _session:    session to create pair in
    @type _session:    MThreadSession
    @param _segment:    segment to create pair in
    @type _segment:    sc_segment
    @param _beg:    begin element for a pair
    @type _beg:    sc_global_addr
    @param _end:    end element for a pair
    @type _end:    sc_global_addr
    @param _types:    constant type
    @type _types:    int
    
    @return: returns list of all used sc-elements
    @rtype: sc_global_addr
    """
    rel_node = createNodeSheaf(_session, _segment, _const)    
    # FIXME:    positive pair constant depending on binary pair constant 
    a1 = createPairPosPerm(_session, _segment, rel_node, _beg, _const)
    a2 = createPairPosPerm(_session, _segment, rel_node, _end, _const)
    
    return [rel_node, a1, a2]

def createPairBinaryNoOrient(_session, _segment, _beg, _end, _const):
    """Creates binary orient pair    (O==========O)
    @param _session:    session to create pair in
    @type _session:    MThreadSession
    @param _segment:    segment to create pair in
    @type _segment:    sc_segment
    @param _beg:    begin element for a pair
    @type _beg:    sc_global_addr
    @param _end:    end element for a pair
    @type _end:    sc_global_addr
    @param _types:    constant type
    @type _types:    int
    
    @return: returns node that designate sheaf
    @rtype: sc_global_addr
    """
    rel_node = createNodeSheaf(_session, _segment, _const)    
    # FIXME:    positive pair constant depending on binary pair constant 
    a1 = createPairPosPerm(_session, _segment, rel_node, _beg, _const)
    a2 = createPairPosPerm(_session, _segment, rel_node, _end, _const)
    
    return rel_node

def createPair(_session, _segment, _beg, _end, _type):
    """Creates pair with specified type
    """
    pair = _session.create_el(_segment, sc.SC_ARC | _type)
    _session.set_beg(pair, _beg)
    _session.set_end(pair, _end)
    return pair

def createPairPosPerm(_session, _segment, _beg, _end, _const):
    """Creates positive, permanent pair
    """
    return createPair(_session, _segment, _beg, _end, sc.SC_POS | sc.SC_PERMANENT | _const)

def createPairNegPerm(_session, _segment, _beg, _end, _const):
    """Creates negative, permanent pair
    """
    return createPair(_session, _segment, _beg, _end, sc.SC_NEG | sc.SC_PERMANENT | _const)

def createPairFuzPerm(_session, _segment, _beg, _end, _const):
    """Creates fuzzy, permanent pair
    """
    return createPair(_session, _segment, _beg, _end, sc.SC_FUZ | sc.SC_PERMANENT | _const) 


node_sets = {"sheaf": keynodes.info.stype_sheaf,
             "role_relation": keynodes.info.stype_bin_orient_role_rel,
             "element": keynodes.info.stype_element,
             "abstract": keynodes.info.stype_ext_obj_abstract,
             "struct": keynodes.info.stype_struct}

def createNode(_session, _segment, _const, _type):
    """Creates node with specified semantic type
    @param _session:    session to create node in
    @type _session:    MThreadSession
    @param _segment:    segment to create pair in
    @type _segment:    sc_segment
    @param _type:    semantic type
    @type _type:    str
    @param _const:    semantic constant keynode
    @type _const:    sc_global_addr
    
    @return: node that designate sheaf
    @rtype: sc_global_addr
    """
    node = _session.create_el(_segment, sc.SC_NODE | _const)
    #_session.appendObj2Sets(_segment, node, [node_sets[_type]])
    createPairPosPerm(_session, _segment, node_sets[_type], node, sc.SC_CONST)
    return node

def createNodeElement(_session, _segment, _const):
    """Creates general node (sc-element)
    """
    return createNode(_session, _segment, _const, "element")

def createNodeRoleRelation(_session, _segment, _const):
    """Creates node that designate role relation
    """
    return createNode(_session, _segment, _const, "role_relation")

def createNodeSheaf(_session, _segment, _const):
    """Creates node that designate sheaf
    """
    return createNode(_session, _segment, _const, "sheaf")

def createNodeAbstract(_session, _segment, _const):
    """Creates node that designate abstract
    """
    return createNode(_session, _segment, _const, "abstract")

def createNodeStruct(_session, _segment, _const):
    """Creates node that designate struct
    """
    return createNode(_session, _segment, _const, "struct")
    
def addElementsToSet(_session, _segment, _set, _elements, _type):
    for elem in _elements:
        _session.gen3_f_a_f(_segment, _set, elem, _type | sc.SC_ARC)

##############################
### Finders ##################
##############################
def searchPairsBinaryOrient(_session, _beg, _end, _const):
    """Finds binary orient pairs between two elements
    @param _session:    session to fire search
    @type _session:    MThreadSession
    @param _beg:    begin element
    @type _beg:    sc_global_addr
    @param _end:    end element
    @type _end:    sc_global_addr
    @param _const:    constant type
    @type _const:    int
    
    @return: return list of tuples. Each tuple contains search results in format (see template, 
    numbers is a position of element sc_global_addr in result tuple). If there are no any results founded,
    then return None
    
    template (number - index in tuple):
                     6 1_           8 2_
                     |              |
                     5              7
                     |              |
                     v              v
             O <-----1------ 2 -----3-----> 4 
    """
    res = []
    it1 = _session.create_iterator(_session.sc_constraint_new(sc_constants.CONSTR_5_a_a_f_a_f, 
                                                            sc.SC_NODE | _const,    # 2 
                                                            sc.SC_ARC | sc.SC_POS | _const, # 1
                                                            _beg, # 0
                                                            sc.SC_ARC | sc.SC_POS | _const, # 5
                                                            keynodes.n_1),          # 6
                                                            True)
    while not it1.is_over():
        # check if node 2 is a sheaf
        if checkIncToSets(_session, it1.value(0), [keynodes.info.stype_sheaf], sc.SC_POS | sc.SC_CONST):
            # finding other nodes to end
            res2 = _session.search_one_shot(_session.sc_constraint_new(sc_constants.CONSTR_5_f_a_f_a_f,
                                                                      it1.value(0), # 2
                                                                      sc.SC_ARC | sc.SC_POS | _const, # 3
                                                                      _end, # 4
                                                                      sc.SC_ARC | sc.SC_POS | _const, # 7
                                                                      keynodes.n_2
                                                                      ), True, 5)
            if res2 is not None:
                res.append((_beg, it1.value(1), it1.value(0), res2[1], _end, 
                            it1.value(4), keynodes.n_1, res[3], keynodes.n_2))
        it1.next()
    
    if len(res) > 0:
        return res
    
    return None

def searchPairsBinaryNoOrient(_session, _beg, _end, _const):
    """Finds binary no-orient pairs between two elements
    @param _session:    session to fire search
    @type _session:    MThreadSession
    @param _beg:    begin element
    @type _beg:    sc_global_addr
    @param _end:    end element
    @type _end:    sc_global_addr
    @param _const:    constant type
    @type _const:    int
    
    @return: return list of tuples. Each tuple contains search results in format (see template, 
    numbers is a position of element sc_global_addr in result tuple). If there are no any results founded,
    then return None
    
    template (number - index in tuple):
             O <-----1------ 2 -----3-----> 4 
    """
    res = []
    it1 = _session.create_iterator(_session.sc_constraint_new(sc_constants.CONSTR_3_a_a_f, 
                                                            sc.SC_NODE | _const,    # 2 
                                                            sc.SC_ARC | sc.SC_POS | _const, # 1
                                                            _beg), # 0
                                                            True)
    while not it1.is_over():
        # check if node 2 is a sheaf
        if checkIncToSets(_session, it1.value(0), [keynodes.info.stype_sheaf], sc.SC_POS | sc.SC_CONST):
            # finding other nodes to end
            res2 = _session.search_one_shot(_session.sc_constraint_new(sc_constants.CONSTR_3_f_a_f,
                                                                      it1.value(0), # 2
                                                                      sc.SC_ARC | sc.SC_POS | _const, # 3
                                                                      _end), # 4
                                                                      True, 5)
            if res2 is not None:
                res.append((_beg, it1.value(1), it1.value(0), res2[1], _end))
        it1.next()
    
    if len(res) > 0:
        return res
    
    return None

#######################
### Search one shot ###
#######################
def searchOneShot(_search_result):
    """Returns first search result. if was founded more then one result constructions,
    then throws RuntimeError. That means that you must be confident that one result exists.
    @param _search_results:    results returned by search... function
    @type _search_results:    list
    
    @return: if constructions was founded, then returns tuple of elements, else returns None 
    """
    if _search_result is None:
        return None
    
    n = len(_search_result)
    
    if n == 0:  return None
    
    if n > 1:   raise RuntimeError("There are '%d' search results" % n)
    
    return _search_result[0]

def searchOneShotPairBinaryOrient(_session, _beg, _end, _const):
    """Searches binary orient pair between two elements.
    @see: searchPairsBinaryOrient
    """
    return searchOneShot(searchPairsBinaryOrient(_session, _beg, _end, _const))

def searchOneShotPairBinaryNoOrient(_session, _beg, _end, _const):
    """Searches binary no-orient pair between two elements.
    @see: searchPairsBinaryOrient
    """
    return searchOneShot(searchPairsBinaryNoOrient(_session, _beg, _end, _const))

def searchOneShotBinPairAttrFromNode(_session, _beg, _attr, _const):
    """Searches a binary orient pair with specified begin element and attribute
    @see: searchOneShot
    @see: searchBinPairsAttrFromNode
    """
    return searchOneShot(searchBinPairsAttrFromNode(_session, _beg, _attr, _const))
    
def searchOneShotBinPairAttrToNode(_session, _end, _attr, _const):
    """Searches a binary orient pair with specified end element and attribute
    @see: searchOneShot
    @see: searchBinPairsAttrToNode
    """
    return searchOneShot(searchBinPairsAttrToNode(_session, _end, _attr, _const))

def searchOneShotFullBinPairsAttrFromNode(_session, _beg, _attr, _const):
    """Searches full data for a binary orient pairs with specified begin element and attribute
    @see: searchOneShot
    @see: searchFullBinPairsAttrFromNode
    """
    return searchOneShot(searchFullBinPairsAttrFromNode(_session, _beg, _attr, _const))

def searchOneShotFullBinPairsAttrToNode(_session, _end, _attr, _const):
    """Searches full data for a binary orient pairs with specified end element and attribute
    @see: searchOneShot
    @see: searchFullBinPairsAttrToNode
    """
    return searchOneShot(searchFullBinPairsAttrToNode(_session, _end, _attr, _const))

###########################################
### checkers
###########################################
def checkIncToSets(_session, _el, _sets, _arc_type):
    """Check if element included to specified sets with specified arc types
    @param _el:    element to check inclusion
    @type _el:    sc_global_addr
    @param _sets:    list of sets [sc_global_addr, ...]
    @type _sets:    list
    
    @return: if element is a member of all specified sets, then return True, else - False
    @rtype: boolean
    """
    for set in _sets:
        if _session.search_one_shot(_session.sc_constraint_new(sc_constants.CONSTR_3_f_a_f,
                                                            set,
                                                            sc.SC_ARC | _arc_type,
                                                            _el), True, 3) is None:
            return False
        
    return True

def checkIfInList(_addr, _list):
    """Check if specified sc-addr is in list
    @param _addr: sc-addr, that need to be checked
    @param _list: List that contains sc-addrs, for checking inclusion
    @return: Return true, if \p _addr is in \p _list
    """
    for item in _list:
        if (_addr.this == item.this):
            return True
        
    return False

def checkOutBinaryPairAttr(_session, _beg, _attr, _const):
    """Check if any output binary pair with specified relation \b _attr exist
    """
    res = searchBinPairsAttrFromNode(_session, _beg, _attr, _const)
    return len(res) > 0

def checkInBinaryPairAttr(_session, _end, _attr, _const):
    """Check if any input binary pair with specified relation \b _attr exist
    """
    res = searchBinPairsAttrToNode(_session, _end, _attr, _const)
    return len(res) > 0

############################################
def appendIntoSet(_session, _segment, _el, _set, _arc_type, _duplicate_allow = False):
    """Appends element into set
    @param _session:    session to work with sc-memory
    @type _session:    sc_session
    @param _segment: segment that will be used to generate arc
    @param _segment: sc_segment
    @param _el: element to append into set
    @type _el: sc_addr
    @param _set: set to append element
    @type _set: sc_addr
    @param _arc_type: type of sc-arc (will be generated from _set into _el)
    @type _arc_type:    int
    @param _duplicate_allow: flag allows duplicates of element on set (if it's True and 
                                element already exists in set, then exception will be raised)
    @type _duplicate_allow: bool 
    
    @raise suit.core.exceptions.ItemAlreadyExistsError: if _duplicate_allow flag is False,
        and element already exists in set
    
    @return: return created arc between _set and _el. If arc wasn't created then return None
    """
    if not _duplicate_allow and checkIncToSets(_session, _el, [_set], 0): # check all arc types
        import suit.core.exceptions
        raise suit.core.exceptions.ItemAlreadyExistsError("element %s already exist in set %s" %
                                                          (str(_el), str(_set)))
    
    createPair(_session, _segment, _set, _el, _arc_type)
    
def removeFromSet(_session, _el, _set):
    """Removes element from set
    @param _session: session to work with sc-memory
    @type _session: sc_session
    @param _el: element that will be removed from set
    @type _el: sc_addr 
    @param _set: set for element removing
    @type _set: sc_addr
    
    @attention: removes all inclusion of element in set
    """
    it = _session.create_iterator(_session.sc_constraint_new(sc_constants.CONSTR_3_f_a_f,
                                                             _set,
                                                             sc.SC_ARC,
                                                             _el), True)
    while not it.is_over():
        _session.erase_el(it.value(1))
        it.next()
    

def getContentFormat(_session, _el):
    """Getting content format for sc-element if it exists    
    @param _session:    current session to work with sc-memory
    @type _session:    MThreadSession
    @param _el:    sc-element to check
    @type _el:    sc_global_addr
    
    @return: if sc-element has content, then return sc-element, that designate content format, else
    return None
    @rtype: sc_global_addr
    
    @raise RuntimeError:    raise exception, if there is any errors in knowledge base
    """    
    # trying to find format
    it1 = _session.create_iterator(_session.sc_constraint_new(sc_constants.CONSTR_3_a_a_f,
                                                              sc.SC_N_CONST,
                                                              sc.SC_A_CONST | sc.SC_POS,# | sc.SC_PERMANENT,
                                                              _el), True)
    while not it1.is_over():
        
        it2 = _session.create_iterator(_session.sc_constraint_new(sc_constants.CONSTR_3_f_a_f,
                                                                  keynodes.ui.format,
                                                                  sc.SC_A_CONST | sc.SC_POS,# | sc.SC_PERMANENT,
                                                                  it1.value(0)), True)
        if not it2.is_over():
            return it1.value(0)
        
        it1.next()
    
    return None

def getElementByIdtf(_idtf, _search_segments):
    """Returns element by text identificator
    @param _idtf:    text identificator
    @type _idtf:    str
    @param _search_segments:    list of segment for searching
    @type _search_segments:    list (sc_segment)
    
    @return: if element founded, then return it sc_global_addr, else return None
    @rtype: sc_global_addr
    """
    import suit.core.kernel as core
    session = core.Kernel.session()
    # trying to find in search segments
    for seg in _search_segments:
        el = session.find_el_idtf(_idtf, session.open_segment(seg))
        if el is not None:  return el

    return None

def copySet(_session, _set_src, _set_dst, _segment):
    """Copy source set to destination set
    @note: This function doesn't copy arc attributes
    @param _session: Session to work with sc-memory
    @type _session:    sc_session
    @param _set_src:    Source set
    @type _set_src:    sc_addr
    @param _set_dst:    Destination set
    @type _set_dst:    sc_addr
    @param _segment:    Segment to create copy in
    @type _segment:    sc_segment
    """
    it = _session.create_iterator(_session.sc_constraint_new(sc_constants.CONSTR_3_f_a_a,
                                                           _set_src,
                                                           sc.SC_ARC,
                                                           0), True)
    
    while not it.is_over():
#        s_el = it.value(2)
#        _idtf = _session.get_idtf(s_el)
#        el = s_el
#        if isSystemId(_idtf):
#            el = _session.create_el(_segment, _session.get_type(s_el))
        createPair(_session, _segment, _set_dst, it.value(2), _session.get_type(it.value(1)))
        it.next()

def isNodeSheaf(_session, _node):
    """Check if node have a sheaf structure type
    @param _node:    node for checking
    @type _node:    sc_global_addr
    
    @return: if node have sheaf structure type, then return True, else - False
    @rtype: bool
    """
    return checkIncToSets(_session, _node, [keynodes.info.stype_sheaf], sc.SC_A_CONST | sc.SC_POS)

def isSystemId(_idtf):
    """Check if identificator is system
    @param _idtf:    identificator for checking
    @type _idtf:    str
    
    @return: if identificator is system, then return True, else - False
    @rtype: bool
    """
    if _idtf.startswith("@@"):  return True
    if _idtf.startswith("tmp_"):    return True
    if len(_idtf) == 36 and _idtf[8] == '-' and _idtf[13] == '-' and _idtf[23] == '-':  return True
    
    return False

###########################################
### special constructions finding
###########################################
def searchBinPairsAttrFromNode(_session, _beg, _attr, _const):
    """Searches a binary orient pairs with specified begin element and attribute
    @param _session:    session to work with
    @type _session: MThreadSession
    @param _beg:    begin element of pair
    @type _beg:    sc_global_addr
    @param _attr:    pair attribute node
    @type _attr:    _sc_global_addr
    @param _const:    pair constant type
    @type _const:    int
    
    @return:    list of end elements
    @rtype:     list
    
    @raise RuntimeWarning:    if structure of binary orient pair is wrong
    
    template:
                x _attr
                |
                v
        O =============> ? (node to find)
     _beg                
    """
    
    res = []
    sr = searchFullBinPairsAttrFromNode(_session, _beg, _attr, _const)
    for item in sr:
        res.append(item[2])
   
    return res

def searchBinPairsAttrToNode(_session, _end, _attr, _const):
    """Searches a binary orient pairs with specified end element and attribute
    @param _session:    session to work with
    @type _session: MThreadSession
    @param _end:    end element of pair
    @type _end:    sc_global_addr
    @param _attr:    pair attribute node
    @type _attr:    _sc_global_addr
    @param _const:    pair constant type
    @type _const:    int
    
    @return:    list of begin elements
    @rtype:     list
    
    @raise RuntimeWarning:    if structure of binary orient pair is wrong
    
    template:
                x _attr
                |
                v
        O =============> ? _end
     (node to find)                
    """
    res = []
    
    sr = searchFullBinPairsAttrToNode(_session, _end, _attr, _const)
    for item in sr:
        res.append(item[0])
    
    return res



def searchFullBinPairsAttrFromNode(_session, _beg, _attr, _const):
    """Searches full data for a binary orient pairs with specified begin element and attribute
    @param _session:    session to work with
    @type _session: MThreadSession
    @param _beg:    begin element of pair
    @type _beg:    sc_global_addr
    @param _attr:    pair attribute node
    @type _attr:    _sc_global_addr
    @param _const:    pair constant type
    @type _const:    int
    
    @return:    list of tuple(begin, sheaf, end)
    @rtype:     list
    
    @raise RuntimeWarning:    if structure of binary orient pair is wrong
    
    template:
                x _attr
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
        if checkIncToSets(_session, sheaf_node, [_attr], sc.SC_A_CONST | sc.SC_POS) and isNodeSheaf(_session, sheaf_node):
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
                
            if end_el is not None:   res.append((_beg, sheaf_node, end_el))
            
        it1.next()
   
    return res

def searchFullBinPairsAttrToNode(_session, _end, _attr, _const):
    """Searches full data for a binary orient pairs with specified end element and attribute
    @param _session:    session to work with
    @type _session: MThreadSession
    @param _end:    end element of pair
    @type _end:    sc_global_addr
    @param _attr:    pair attribute node
    @type _attr:    _sc_global_addr
    @param _const:    pair constant type
    @type _const:    int
    
    @return:    list of tuple(begin, sheaf, end)
    @rtype:     list
    
    @raise RuntimeWarning:    if structure of binary orient pair is wrong
    
    template:
                x _attr
                |
                v
        ? =============> O _end
     (node to find)                
    """
    res = []
    # finding sheaf node
    it1 = _session.create_iterator(_session.sc_constraint_new(sc_constants.CONSTR_5_a_a_f_a_f,
                                                           sc.SC_NODE | _const,
                                                           sc.SC_ARC | sc.SC_POS | _const,
                                                           _end,
                                                           sc.SC_ARC | sc.SC_POS | _const,
                                                           keynodes.n_2), True)
    while not it1.is_over():
        # check if founded node is sheaf
        sheaf_node = it1.value(0)
        if checkIncToSets(_session, sheaf_node, [_attr], sc.SC_A_CONST | sc.SC_POS) and isNodeSheaf(_session, sheaf_node):
            # finding end node
            it2 = _session.create_iterator(_session.sc_constraint_new(sc_constants.CONSTR_5_f_a_a_a_f,
                                                                   sheaf_node,
                                                                   sc.SC_ARC | sc.SC_POS | _const,
                                                                   sc.SC_NODE,
                                                                   sc.SC_ARC | sc.SC_POS | _const,
                                                                   keynodes.n_1), True)
            beg_el = None
            while not it2.is_over():
                if beg_el is None:
                    beg_el = it2.value(2)
                else:
                    raise RuntimeWarning("Invalid binary orient pair")
                it2.next()
                
            if beg_el is not None:   res.append((beg_el, sheaf_node, _end))
            
        it1.next()
   
    return res


########################################
### Constructions printing
########################################
def strOutputIdtf(_session, _el):
    """Prints idtfs for elements that is a end of outut arcs from specified element
    @param _el:    element to print output arcs from
    @type _el:    sc_global_addr
    """
    it = _session.create_iterator(_session.sc_constraint_new(sc_constants.CONSTR_3_f_a_a,
                                                           _el,
                                                           sc.SC_A_CONST,
                                                           0), True)
    res = ""
    while not it.is_over():
        res = res + cp1251ToUtf8(_session.get_idtf(it.value(2))) + "\n"
        it.next()
        
    return res

def strInputIdtf(_session, _el):
    """Prints idtfs for elements that is a end of input arcs from specified element
    @param _el:    element to print input arcs from
    @type _el:    sc_global_addr
    """
    it = _session.create_iterator(_session.sc_constraint_new(sc_constants.CONSTR_3_a_a_f,
                                                           0,
                                                           sc.SC_ARC,
                                                           _el), True)
    res = ""
    while not it.is_over():
        res = res + cp1251ToUtf8(_session.get_idtf(it.value(0))) + "\n"
        it.next()
        
    return res
        
def strElementType(_type):
    
    _type_str = ""
    if _type & sc.SC_NODE:
        _type_str = _type_str + "node"
    elif _type & sc.SC_ARC:
        _type_str = _type_str + "arc"
    elif _type & sc.SC_UNDF:
        _type_str = _type_str + "undef"
        
    if _type & sc.SC_CONST:
        _type_str = _type_str + "|const"
    elif _type & sc.SC_VAR:
        _type_str = _type_str + "|var"
    elif _type & sc.SC_METAVAR:
        _type_str = _type_str + "|meta"
        
    if _type & sc.SC_POS:
        _type_str = _type_str + "|pos"
    elif _type & sc.SC_FUZ:
        _type_str = _type_str + "|fuz"
    elif _type & sc.SC_NEG:
        _type_str = _type_str + "|neg"
    
    return _type_str


########################################
### Content
########################################

def setContentInt(_session, _segment, _el, _data):
    """Sets int value content to element
    @param _el:    element to set content into
    @type _el:    sc_global_addr
    @param _data:    content data
    @type _data:    str
    """
    _session.set_content_int(_el, _data)
    _session.gen3_f_a_f(_segment, keynodes.ui.format_int, _el, sc.SC_A_CONST|sc.SC_POS)

def setContentReal(_session, _segment, _el, _data):
    """Sets real value content to element
    @param _el:    element to set content into
    @type _el:    sc_global_addr
    @param _data:    content data
    @type _data:    str
    """
    _session.set_content_real(_el, _data)
    _session.gen3_f_a_f(_segment, keynodes.ui.format_real, _el, sc.SC_A_CONST|sc.SC_POS)

    
def setContentStr(_session, _segment, _el, _data):
    """Sets string content to element
    @param _el:    elment to set content into
    @type _el:    sc_global_addr
    @param _data:    content data
    @type _data:    str
    """
    _session.set_content_str(_el, _data)
    _session.gen3_f_a_f(_segment, keynodes.ui.format_string, _el, sc.SC_A_CONST|sc.SC_POS)
    
    
##########################
### Identifiers & Text ###
##########################
def getLocalizedTextFromSet(_session, _set, _language):
    """Return text that contains in \p _set and \p _language sets
    
    @param _session: session to work with sc-memory
    @type _session: sc_session
    @param _set: sc-element that designate set of any contents (for example identifiers tuple)
    @type _set: sc_addr
    @param _language: sc-element that designate translation language
    @type _language: sc_addr
    
    @return:Return unicode string, if it exists; otherwise return None 
    """
    assert _set is not None
    assert _language is not None
    
    caption = None
    it1 = _session.create_iterator(_session.sc_constraint_new(sc_constants.CONSTR_3_f_a_a,
                                                              _set,
                                                              sc.SC_A_CONST,
                                                              sc.SC_N_CONST), True)
    while not it1.is_over():
        if checkIncToSets(_session, it1.value(2), [_language], sc.SC_CONST):
            caption = cp1251ToUtf8(_session.get_content_str(it1.value(2)))
        it1.next()

    return caption

def getIdentifier(_session, _el, _language):
    """Return identifier for \p el that includes in \p _language set
    @param _session: session to work with sc-memory
    @type _session: sc_session
    @param _el: sc-element that need to get identifier
    @type _el: sc_addr
    @param _language: sc-element that designate translation language
    @type _language: sc_addr
    
    @return: Return unicode string with identifier, if it exists; otherwise return None   
    """
    # get identification set
    caption = None
    idtf_set = searchOneShotBinPairAttrToNode(_session, _el, keynodes.common.nrel_identification, sc.SC_CONST)
    if idtf_set is not None:
        return getLocalizedTextFromSet(_session, idtf_set, _language)
    
    return None

def getLocalizedIdentifier(_session, _el):
    """Return tuple, that contains text identifier for \p el used for current localization and 
    flag, that is True, if returned identifier is system. 
    """
    import kernel as core
    kernel = core.Kernel.getSingleton()
    assert _el is not None
    _caption = getIdentifier(kernel.session(), _el, kernel.getCurrentTranslation())
    _system = False
    if _caption is None:
        caption = kernel.session().get_idtf(_el)
        if not isSystemId(caption):
            _caption = unicode(caption)
            _system = True
        else:
            _caption = u""
    else:
        assert isinstance(_caption, unicode)
    return _caption, _system

def getImageIdentifier(_session, _el):
    """Return image identifier for \p el
    @param _session: session to work with sc-memory
    @type _session: sc_session
    @param _el: sc-element that need to get identifier
    @type _el: sc_addr
    
    @return: Return string that contains name of texture with image. If 
    there are no image identifier, then return None
    """
    import sc_core.constants as sc_constants
    import sc_core.pm as sc
    import ogre.renderer.OGRE as ogre
    
    addr = _el
    assert addr is not None
    icon_name = "image_%s" % str(addr.this)
    
    # check if icon already loaded
    if ogre.TextureManager.getSingleton().getByName(icon_name) is not None:
        return icon_name
    
    icon = None
    idtf_set = searchOneShotBinPairAttrToNode(_session, addr, keynodes.common.nrel_identification, sc.SC_CONST)
    if idtf_set is not None:
        
        it1 = _session.create_iterator(_session.sc_constraint_new(sc_constants.CONSTR_3_f_a_a,
                                                               idtf_set,
                                                               sc.SC_A_CONST,
                                                               sc.SC_N_CONST), True)
        while not it1.is_over():
            if checkIncToSets(_session, it1.value(2), [keynodes.common.group_image], sc.SC_CONST):
                icon = it1.value(2)
                break                 
            it1.next()
        
        if icon is None:
            return None
        
        _fmt = getContentFormat(_session, icon)
        assert _fmt is not None

        _cont = _session.get_content_const(icon)
        assert _cont is not None

        _cont_data = _cont.convertToCont()

        data = _cont.get_data(_cont_data.d.size)
        stream = ogre.MemoryDataStream("%s" % str(addr.this), _cont_data.d.size, False)
        stream.setData(data)

        try:
            img = ogre.Image()
            img.load(stream, ogre.Image.getFileExtFromMagic(stream))
        except:
            import sys, traceback
            print "Error:", sys.exc_info()[0]
            traceback.print_exc(file=sys.stdout)
        
        ogre.TextureManager.getSingleton().loadImage(icon_name, "General", img)
        return icon_name
    
    return None

def makeAnswer(session, segment, question, answer):
    """Generate binary pair between answer and question
    """
    import sc_core.pm as sc
    
    pair = createPairBinaryOrient(session, segment, question, answer, sc.SC_CONST)
    createPairPosPerm(session, segment, keynodes.questions.nrel_answer, pair, sc.SC_CONST)