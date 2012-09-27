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
Created on 01.02.2010

@author: Denis Koronchik
'''

from suit.core.objects import Translator
import suit.core.sc_utils as sc_utils
import suit.core.objects as objects
import suit.core.kernel as core
import sc_core.pm as sc
import geom_keynodes
import geom_objects
import geom_env as env
import suit.core.keynodes as keynodes

def get_sc_element(_segment, _idtf, _object, _sc_type):
    """Generates scs-element, that represent geometry object
    @param _segment:    segment to work with data in sc-memory
    @type _segment:    sc_segment
    @param _idtf:    identificator for search
    @type _idtf:    str
    @param _object:    object to create sc-element for
    @type _object:    Object
    @param _sc_type:    sc-type for element
    @type _sc_type:    sc_type
    
    @return: addr of create sc-element
    @rtype: sc_global_addr
    """
    session = core.Kernel.session()
    
    # getting node idtf
    sc_object = None
    el = None
    isUri = False
    
    # if idtf empty, then creating new element
    if _idtf is None:
        el = session.create_el(_segment, _sc_type)
    else:
        # check if idtf if full uri
        isUri = _idtf.startswith('/')
    
    # trying to find object by idtf, if it doesn't exists, then creating it
    try:
        if el is None:
           
            
            if isUri:
                el = session.find_el_full_uri(_idtf)
                if el is None:
                    el = session.create_el_full_uri(_idtf, _sc_type)[1]
            else:
                _segs = [_segment.get_full_uri()]
                _segs.extend(env.search_segments)
                # trying to find element
                el = sc_utils.getElementByIdtf(_idtf, _segs)
                if el is None:
                    el = session.create_el_idtf(_segment, _sc_type, _idtf)[1]
    except:
        import sys, traceback
        print sys.exc_info()[0]
        traceback.print_exc(file=sys.stdout)
        return None
    
    _object._setScAddr(el)
    
    return el

def _resolve_sc_addr(_segment, _object):
    """Resolve sc_adr for specified object
    @param _segment: sc-segment to work with sc-elements. It will be used to
                    generate sc_addr for object, if it doesn't has one.
    @type _segment: sc-segment
    @param _object: Object that need to resolve sc_addr
    @type _object: ObjectDepth  
    """
    assert _object is not None
    idtf = None
    idtf = _object.build_text_idtf()  
    
    assert get_sc_element(_segment, idtf, _object, sc.SC_N_CONST) is not None
    
def addToSets(_session, _segment, _addr, _sets):
    """Create positive pair between each element of \p _sets list and \p _addr
    """
    for _set in _sets:
        if not sc_utils.checkIncToSets(_session, _addr, [_set], sc.SC_A_CONST | sc.SC_POS | sc.SC_PERMANENT):
            sc_utils.createPairPosPerm(_session, _segment, _set, _addr, sc.SC_CONST)

def translateChildPoints(_session, _segment, _object):
    """Translate points, that lies on \p _object
    """
    assert isinstance(_object, geom_objects.GeometryAbstractObject)
    
    obj_addr = _object._getScAddr()
    assert obj_addr is not None
    
    for _point, _pos in _object.getPoints():
        pt_addr = _point._getScAddr()
        assert pt_addr is not None
        
        if not sc_utils.checkIncToSets(_session, pt_addr, [obj_addr], sc.SC_A_CONST | sc.SC_POS | sc.SC_PERMANENT):
            sc_utils.createPairPosPerm(_session, _segment, obj_addr, pt_addr, sc.SC_CONST)

def translate_point(_segment, _object, _params):
    """Translates point object to sc-memory
    """    
    _addr = _object._getScAddr()
    assert _addr is not None
    
    # include sc-element to points
    session = core.Kernel.session()
    addToSets(session, _segment, _addr, [geom_keynodes.Objects.point, keynodes.info.stype_ext_obj_abstract])
    
    return True

def translate_line_sec(_segment, _object, _params):
    """Translates line section to sc-memory
    """
    _addr = _object._getScAddr()

    session = core.Kernel.session()
    if not _addr:   
        _addr = sc_utils.createNodeStruct(session, _segment, sc.SC_CONST)
        _object._setScAddr(_addr)
        
    addToSets(session, _segment, _addr, [geom_keynodes.Objects.line_sector, keynodes.info.stype_struct])
    
    # end begin points
    addr_begin = _object.getBegin()._getScAddr()
    addr_end = _object.getEnd()._getScAddr()
    
    assert addr_begin and addr_end
    
    a1 = sc_utils.createPairBinaryOrient(session, _segment, _addr, addr_begin, sc.SC_CONST)
    sc_utils.createPairPosPerm(session, _segment, geom_keynodes.Relation.nrel_border_point, a1, sc.SC_CONST)
    a2 = sc_utils.createPairBinaryOrient(session, _segment, _addr, addr_end, sc.SC_CONST)
    sc_utils.createPairPosPerm(session, _segment, geom_keynodes.Relation.nrel_border_point, a2, sc.SC_CONST)
    
    # check if line have length and build it value
        # set value if it exists
#    if _object.getLength() is not None:
#        len_node = sc_utils.createNodeElement(session, _segment, sc.SC_CONST)
#        sheaf = sc_utils.createPairBinaryOrient(session, _segment, _addr, len_node, sc.SC_CONST)
#        sc_utils.createPairPosPerm(session, _segment, geom_keynodes.Relation.nrel_length, sheaf, sc.SC_CONST)
#        
#        len_val_node = sc_utils.createNodeElement(session, _segment, sc.SC_CONST)
#        sheaf = sc_utils.createPairBinaryOrient(session, _segment, len_val_node, len_node, sc.SC_CONST)
#        sc_utils.createPairPosPerm(session, _segment, keynodes.common.nrel_value, sheaf, sc.SC_CONST)
#        
#        len_val_cm_node = sc_utils.createNodeElement(session, _segment, sc.SC_CONST)
#        a = sc_utils.createPairPosPerm(session, _segment, len_val_node, len_val_cm_node, sc.SC_CONST)
#        sc_utils.createPairPosPerm(session, _segment, geom_keynodes.Relation.rrel_cm, a, sc.SC_CONST)
#        
#        idtf_node = sc_utils.createNodeSheaf(session, _segment, sc.SC_CONST)
#        sheaf = sc_utils.createPairBinaryOrient(session, _segment, idtf_node, len_val_cm_node, sc.SC_CONST)
#        sc_utils.createPairPosPerm(session, _segment, keynodes.common.nrel_identification, sheaf, sc.SC_CONST)
#        
#        dec_val_node = sc_utils.createNodeElement(session, _segment, sc.SC_CONST)
#        session.set_content_real(dec_val_node, _object.getLength())
#        a = sc_utils.createPairPosPerm(session, _segment, idtf_node, dec_val_node, sc.SC_CONST)
#        sc_utils.createPairPosPerm(session, _segment, keynodes.common.rrel_dec_number, a, sc.SC_CONST)
    
    # translate child points
    translateChildPoints(session, _segment, _object)    
    
    return True
    
def translate_circle(_segment, _object, _params):
    """Translates circle object to sc-memory
    """
    _addr = _object._getScAddr()
    
    # include sc-element to points
    session = core.Kernel.session()
    addToSets(session, _segment, _addr, [geom_keynodes.Objects.circle, keynodes.info.stype_ext_obj_abstract])    
    
    # add relation to center point
    addr_begin = _object.center_point._getScAddr()
    if not sc_utils.checkOutBinaryPairAttr(session, _addr, geom_keynodes.Relation.nrel_center, sc.SC_CONST):
        a1 = sc_utils.createPairBinaryOrient(session, _segment, _addr, addr_begin, sc.SC_CONST)
        sc_utils.createPairPosPerm(session, _segment, geom_keynodes.Relation.nrel_center, a1, sc.SC_CONST)
        
    if not sc_utils.checkOutBinaryPairAttr(session, _addr, geom_keynodes.Relation.nrel_radius, sc.SC_CONST):
        radius_obj = _object.getRadiusObject()
        if radius_obj is not None:
            a1 = sc_utils.createPairBinaryOrient(session, _segment, _addr, radius_obj._getScAddr(), sc.SC_CONST)
            sc_utils.createPairPosPerm(session, _segment, geom_keynodes.Relation.nrel_radius, a1, sc.SC_CONST)
    
    # translate child points
    translateChildPoints(session, _segment, _object)
    
    # translate radius if it exist
    
    return True

def translate_triangle(_segment, _object, _params):
    """Translates circle object to sc-memory
    """    
    _addr = _object._getScAddr()
    
    # include sc-element to points
    session = core.Kernel.session()
    addToSets(session, _segment, _addr, [geom_keynodes.Objects.plane_triangle, keynodes.info.stype_ext_obj_abstract])
 
    sides = _object.getSides()
    for obj in sides:
        sheaf = sc_utils.createPairBinaryOrient(session, _segment, _addr, obj._getScAddr(), sc.SC_CONST)
        sc_utils.createPairPosPerm(session, _segment, geom_keynodes.Relation.nrel_side, sheaf, sc.SC_CONST)
            
    # build square relation
    #sq_node = sc_utils.createNodeElement(session, _segment, sc.SC_CONST)
    #sheaf = sc_utils.createPairBinaryOrient(session, _segment, _addr, sq_node, sc.SC_CONST)
    #sc_utils.createPairPosPerm(session, _segment, geom_keynodes.Relation.nrel_square, sheaf, sc.SC_CONST)
    
    return True

def translate_quadrangle(_segment, _object, _params):
    """Translates circle object to sc-memory
    """    
    _addr = _object._getScAddr()
    
    # include sc-element to points
    session = core.Kernel.session()
    addToSets(session, _segment, _addr, [geom_keynodes.Objects.plane_quadrangle, keynodes.info.stype_ext_obj_abstract])
 
    sides = _object.getSides()
    for obj in sides:
        sheaf = sc_utils.createPairBinaryOrient(session, _segment, _addr, obj._getScAddr(), sc.SC_CONST)
        sc_utils.createPairPosPerm(session, _segment, geom_keynodes.Relation.nrel_side, sheaf, sc.SC_CONST)
            
    # build square relation
    #sq_node = sc_utils.createNodeElement(session, _segment, sc.SC_CONST)
    #sheaf = sc_utils.createPairBinaryOrient(session, _segment, _addr, sq_node, sc.SC_CONST)
    #sc_utils.createPairPosPerm(session, _segment, geom_keynodes.Relation.nrel_square, sheaf, sc.SC_CONST)
    
    return True

def translate_angle(_segment, _object, _params):
    """Translates point object to sc-memory
    """    
    _addr = _object._getScAddr()
    assert _addr is not None
    
    # include sc-element to points
    session = core.Kernel.session()
    addToSets(session, _segment, _addr, [geom_keynodes.Objects.angle, keynodes.info.stype_ext_obj_abstract])
    
    return True

def translate_value(_segment, _value_node, _value):
    
    session = core.Kernel.session()
    
    v_node = sc_utils.createNodeElement(session, _segment, sc.SC_CONST)
    sheaf = sc_utils.createPairBinaryOrient(session, _segment, v_node, _value_node, sc.SC_CONST)
    sc_utils.createPairPosPerm(session, _segment, keynodes.common.nrel_value, sheaf, sc.SC_CONST)
    
    vu_node = sc_utils.createNodeElement(session, _segment, sc.SC_CONST)
    a = sc_utils.createPairPosPerm(session, _segment, v_node, vu_node, sc.SC_CONST)
    sc_utils.createPairPosPerm(session, _segment, geom_keynodes.Relation.rrel_cm2, a, sc.SC_CONST)
    
    # make identification
    idtf_node = sc_utils.createNodeSheaf(session, _segment, sc.SC_CONST)
    sheaf = sc_utils.createPairBinaryOrient(session, _segment, idtf_node, vu_node, sc.SC_CONST)
    sc_utils.createPairPosPerm(session, _segment, keynodes.common.nrel_identification, sheaf, sc.SC_CONST)
    
    # set value
    val = sc_utils.createNodeElement(session, _segment, sc.SC_CONST)
    sc_utils.setContentReal(session, _segment, val, _value)
    a = sc_utils.createPairPosPerm(session, _segment, idtf_node, val, sc.SC_CONST)
    sc_utils.createPairPosPerm(session, _segment, keynodes.common.rrel_dec_number, a, sc.SC_CONST)

def translate_square(_segment, _object):
    
    session = core.Kernel.session()
    _value = _object.getPropertyValue(geom_objects.GeometryAbstractObject.PropSquare)
    
    _addr = _object._getScAddr()
    
    # build square relation
    if not sc_utils.checkOutBinaryPairAttr(session, _addr, geom_keynodes.Relation.nrel_square, sc.SC_CONST):
        sq_node = sc_utils.createNodeElement(session, _segment, sc.SC_CONST)
        sheaf = sc_utils.createPairBinaryOrient(session, _segment, _addr, sq_node, sc.SC_CONST)
        sc_utils.createPairPosPerm(session, _segment, geom_keynodes.Relation.nrel_square, sheaf, sc.SC_CONST)
        
        translate_value(_segment, sq_node, _value)
        
    else:
        pass

def translate_perimeter(_segment, _object):
    
    session = core.Kernel.session()
    _value = _object.getPropertyValue(geom_objects.GeometryAbstractObject.PropPerimeter)
    
    _addr = _object._getScAddr()
    
    # build square relation
    if not sc_utils.checkOutBinaryPairAttr(session, _addr, geom_keynodes.Relation.nrel_perimeter, sc.SC_CONST):
        p_node = sc_utils.createNodeElement(session, _segment, sc.SC_CONST)
        sheaf = sc_utils.createPairBinaryOrient(session, _segment, _addr, p_node, sc.SC_CONST)
        sc_utils.createPairPosPerm(session, _segment, geom_keynodes.Relation.nrel_perimeter, sheaf, sc.SC_CONST)
        
        translate_value(_segment, p_node, _value)
        
    else:
        pass
    
def translate_length(_segment, _object):
    session = core.Kernel.session()
    _value = _object.getPropertyValue(geom_objects.GeometryAbstractObject.PropLength)
    
    _addr = _object._getScAddr()
    
    # build square relation
    if not sc_utils.checkOutBinaryPairAttr(session, _addr, geom_keynodes.Relation.nrel_length, sc.SC_CONST):
        p_node = sc_utils.createNodeElement(session, _segment, sc.SC_CONST)
        sheaf = sc_utils.createPairBinaryOrient(session, _segment, _addr, p_node, sc.SC_CONST)
        sc_utils.createPairPosPerm(session, _segment, geom_keynodes.Relation.nrel_length, sheaf, sc.SC_CONST)
        
        translate_value(_segment, p_node, _value)
        
    else:
        pass

def translate_object(_segment, _object, _params):
    """Translates specified geometry object to SC-code.
    @param _segment:    segment to translate object in
    @type _segment:    sc_segment
    @param _object:    geometry object to translate
    @type _object:    SCgObject or SCgPair
    @param _params:    additional parameters to translate object. It contains list of sc-elements, that
    designates semantic types for specified object. sc-element, that designate translated object will be included to
    sets from _params
    @type _params:    list
    
    @return: if object translated successfully, then return True, else - False
    @rtype: bool
    """
    
    if isinstance(_object, geom_objects.GeometryPoint):
        return translate_point(_segment, _object, _params)
    elif isinstance(_object, geom_objects.GeometryLineSection):
        return translate_line_sec(_segment, _object, _params)
    elif isinstance(_object, geom_objects.GeometryCircle):
        return translate_circle(_segment, _object, _params)
    elif isinstance(_object, geom_objects.GeometryTriangle):
        return translate_triangle(_segment, _object, _params)
    elif isinstance(_object, geom_objects.GeometryQuadrangle):
        return translate_quadrangle(_segment, _object, _params)
    elif isinstance(_object, geom_objects.GeometryAngle):
        return translate_angle(_segment, _object, _params)
    else:
        return False
    
    return True

def translete_congr(_segment, _obj1, _obj2):
    
    # check if it have relation
    session = core.Kernel.session()
    
    res = sc_utils.searchPairsBinaryNoOrient(session, _obj1._getScAddr(), _obj2._getScAddr(), sc.SC_CONST)

    if res is not None:
        for result in res:
            if sc_utils.checkIncToSets(session, result[2], [geom_keynodes.Relation.nrel_congr], sc.SC_A_CONST | sc.SC_POS | sc.SC_PERMANENT):
                return
    
    # create new relation
    a = sc_utils.createPairBinaryNoOrient(session, _segment, _obj1._getScAddr(), _obj2._getScAddr(), sc.SC_CONST)
    sc_utils.createPairPosPerm(session, _segment, geom_keynodes.Relation.nrel_congr, a, sc.SC_CONST)
    
    return

class TranslatorGeom2Sc(Translator):
    
    property_translators = {geom_objects.GeometryAbstractObject.PropSquare: translate_square,
                            geom_objects.GeometryAbstractObject.PropPerimeter: translate_perimeter,
                            geom_objects.GeometryAbstractObject.PropLength: translate_length}
    
    def __init__(self):
        Translator.__init__(self)
                
    def __del__(self):
        Translator.__del__(self)
        
    def translate_impl(self, _input, _output):
        """Translator implementation
        """
        # translating objects
        objs = objects.ScObject._sc2Objects(_input)
        
        assert len(objs) > 0
        sheet = objs[0]
        assert type(sheet) is objects.ObjectSheet
    
        segment = sheet.getTmpSegment()
    
        errors = []
        session = core.Kernel.session()
    
        # getting objects, that need to be translated
        trans_obj = []
        for obj in sheet.getChilds():
            _addr = obj._getScAddr()
            if _addr is None:
                trans_obj.append(obj)
                # remove old translation data
            else:
                if _addr.seg == segment:
                    obj._setScAddr(None)
                    session.erase_el(_addr)
                

        # resolve sc_addrs
        for obj in trans_obj:
            _resolve_sc_addr(segment, obj)
                
        # make translation
        for obj in trans_obj:
            
            if not translate_object(segment, obj, None):
                errors.append( ((obj, "Error while translate object %s" % str(obj))) )
                
            # translate object properties
            for prop, value in obj.properties.items():
                
                if not TranslatorGeom2Sc.property_translators.has_key(prop):
                    errors.append((obj, "Error property %s can't be translated" % str(prop)))
                    continue # go to next property
                
                TranslatorGeom2Sc.property_translators[prop](segment, obj)
            
        # make equivalence
        for _objType in geom_objects.GeometryAbstractObject.groups.values():
            for group in _objType.values():
                objs = group
                for idx1 in xrange(len(objs)):
                    for idx2 in xrange(idx1 + 1, len(objs)):
                        obj1 = objs[idx1]
                        obj2 = objs[idx2]
                        if obj1 is not obj2:
                            translete_congr(segment, obj1, obj2)
                
        print "Translation errors:"    
        for obj, error in errors:
            print error 

        return errors