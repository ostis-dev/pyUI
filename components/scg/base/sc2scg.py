
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

@author: Denis Koronchik
'''

"""sc -> scg translator component
"""
from suit.core.objects import Translator
import suit.core.objects as objects
import suit.core.kernel as core
import scg_environment as env
import sc_core.pm as sc
import sc_core.constants as sc_constants
import suit.core.keynodes as keynodes
import suit.core.sc_utils as sc_utils
import scg_alphabet
import scg_objects
import suit.core.exceptions as exceptions


def getConstStr(_type):
    _const = None
    if _type & sc.SC_CONST:
        _const = "const"
    elif _type & sc.SC_VAR:
        _const = "var"
    elif _type & sc.SC_A_METAVAR:
        _const = "meta"
    else:
        _const = "-"
    return _const

def getPosStr(_type):
    _pos = None
    if _type & sc.SC_POS:
        _pos = "pos"
    elif _type & sc.SC_NEG:
        _pos = "neg"
    elif _type & sc.SC_FUZ:
        _pos = "fuz"
    else:
        _pos = "-"
    return _pos

def build_node(_session, _el, _type):
    """Builds SCgNode based on sc-element
    """
    
    # check if it isn't content node
    _cnt_type = sc_utils.getContentFormat(_session, _el)
    
    
    if _cnt_type is not None:
        obj = objects.ObjectSheet()
        obj.hideContent()
        obj._setScAddr(_el)
        
        # creating viewer
        try:
            logic = core.Kernel.getSingleton().createViewer(_cnt_type)
            obj.setLogic(logic)
        except exceptions.UnsupportedFormatError:
            core.Kernel.getSingleton().logManager.logWarning("Format %s not supported for viewing" % (_session.get_idtf(_cnt_type)))
        
        return obj
    else:
        type_name = "node/const/elem"
        
        # creating type name based on element type    
        _const = getConstStr(_type)
                
        _stype = "elem"
        if sc_utils.checkIncToSets(_session, _el, [keynodes.info.stype_sheaf], sc.SC_A_CONST | sc.SC_POS | sc.SC_PERMANENT):
            _stype = "sheaf"
        elif sc_utils.checkIncToSets(_session, _el, [keynodes.info.stype_ext_obj_abstract], sc.SC_A_CONST | sc.SC_POS | sc.SC_PERMANENT):
            _stype = "abstract"
        elif sc_utils.checkIncToSets(_session, _el, [keynodes.info.stype_bin_orient_norole_rel], sc.SC_A_CONST | sc.SC_POS | sc.SC_PERMANENT):
            _stype = "binary"
        elif sc_utils.checkIncToSets(_session, _el, [keynodes.info.stype_ext_obj_real], sc.SC_A_CONST | sc.SC_POS | sc.SC_PERMANENT):
            _stype = "real"
        elif sc_utils.checkIncToSets(_session, _el, [keynodes.info.stype_bin_orient_role_rel], sc.SC_A_CONST | sc.SC_POS | sc.SC_PERMANENT):
            _stype = "role"
        elif sc_utils.checkIncToSets(_session, _el, [keynodes.info.stype_struct], sc.SC_A_CONST | sc.SC_POS | sc.SC_PERMANENT):
            _stype = "struct"
        elif sc_utils.checkIncToSets(_session, _el, [keynodes.info.stype_concept_norel], sc.SC_A_CONST | sc.SC_POS | sc.SC_PERMANENT):
            _stype = "term"
        
        if _const is not None:
            type_name = "node/%s/%s" % (_const, _stype)
        else:
            type_name = "node/elem"
        
        obj = scg_alphabet.createSCgNode(type_name)
        obj._setScAddr(_el)
        return obj
    
    return None

def build_pair(_session, _el, _type):
    """Builds SCgPair based on sc-element
    """
    type_name = "pair/-/-/-/-"
    
    _const = getConstStr(_type)
    _pos = getPosStr(_type)
    _orient = "orient"
    
    assert _pos is not None and _const is not None
    
    if _type & sc.SC_TEMPORARY:
        type_name = "pair/%s/time/%s/%s" % (_pos, _orient, _const)
    else:
        type_name = "pair/%s/-/%s/%s" % (_pos, _orient, _const)     
    
    obj = scg_alphabet.createSCgPair(type_name)
    obj._setScAddr(_el)
    return obj

def translate_obj(_session, _el, _type):
    """Translates sc-element to object
    
    @param _session:    current workable session
    @type _session:    sc_session
    @param _el:    sc-element to translate into object
    @type _el:    sc_global_addr    
    @param _type:    sc-element type (gets for growing speed)
    @type _type:    sc_type
    @return: created object that represent sc-element
    @rtype: ObjectDepth
    """  
		
    if _type & sc.SC_NODE:
        return build_node(_session, _el, _type)
    elif _type & sc.SC_ARC:
        return build_pair(_session, _el, _type) 
    
    return build_node(_session, _el, _type|sc.SC_NODE)
    raise RuntimeError("Unknown element type")
    
    
def get_pair_binary(session, _sheaf_node, _addrs_list):
    """Trying to get binary pair based on sheaf node.
    
    Elements ids:
                   6 1_           8 2_
                     |              |
                     5              7
                     |              |
                     v              v
             O <-----1------ 2 -----3-----> 4
    
    @param _session:    current session
    @type _session:    sc_session
    @param _sheaf_node:    sheaf node of pair
    @type _sheaf_node:    sc_global_addr
    @param _addrs_list:    list of string addrs representation of objects that exists on window
    @type _addrs_list:    list
    
    @return: if pair was founded, then returns tuple of (sc-elements list that was included to pair and orient flag), else
    returns None
    @rtype: tuple (list, bool)
    """
    it = session.create_iterator(session.sc_constraint_new(sc_constants.CONSTR_3_f_a_a,
                                                           _sheaf_node,
                                                           sc.SC_ARC | sc.SC_POS,
                                                           0), True)
    cnt = 0
    res = []
    while not it.is_over():
        cnt += 1
        if cnt > 2 or (not str(it.value(2).this) in _addrs_list):
            return None
        res.append( (it.value(0), it.value(1), it.value(2)) )
        it.next()
    
    if cnt < 2:
        return None
    
    
    a1 = a2 = None
    if str(keynodes.n_1.this) in _addrs_list and str(keynodes.n_2.this) in _addrs_list:
        a1 = session.search_one_shot(session.sc_constraint_new(sc_constants.CONSTR_3_f_a_f,
                                                               keynodes.n_1,
                                                               sc.SC_ARC | sc.SC_POS,
                                                               res[0][1]), True, 3)
        if a1 is None:
            a2 = session.search_one_shot(session.sc_constraint_new(sc_constants.CONSTR_3_f_a_f,
                                                                   keynodes.n_2,
                                                                   sc.SC_ARC | sc.SC_POS,
                                                                   res[0][1]), True, 3)
            a1 = session.search_one_shot(session.sc_constraint_new(sc_constants.CONSTR_3_f_a_f,
                                                                   keynodes.n_1,
                                                                   sc.SC_ARC | sc.SC_POS,
                                                                   res[1][1]), True, 3)
        else:
            a2 = session.search_one_shot(session.sc_constraint_new(sc_constants.CONSTR_3_f_a_f,
                                                                   keynodes.n_2,
                                                                   sc.SC_ARC | sc.SC_POS,
                                                                   res[1][1]), True, 3)
    if a1 is not None or a2 is not None:
        return ([res[0][2], res[0][1], res[0][0], res[1][1], res[1][2],
                 a1[1], a1[0], a2[1], a2[0]], True)
        
#    return ([res[0][2], res[0][1], res[0][0], res[1][1], res[1][2]], True)
    return None
    
class TranslatorSc2Scg(Translator):
    """Class that realize translation from SC-code directly to scg-window
    """    
    def __init__(self):
        Translator.__init__(self)
        
    def __del__(self):
        Translator.__del__(self)
        
    def translate_impl(self, _input, _output):
        """Translator implementation
        @param _input:    input data set
        @type _input:    sc_global_addr
        @param _output:    output window (must be created)
        @type _output:    sc_global_addr
        
        @return: list of errors each element of list is a tuple(object, error)
        @rtype: list
        """
        errors = []
        
        # FIXME:    think about multiply windows for one sc-element
        objs = objects.ScObject._sc2Objects(_output)
        
        assert len(objs) > 0
        sheet = objs[0]
        assert type(sheet) is objects.ObjectSheet
        
        session = core.Kernel.session()
        
        trans_objs = []
        result_objs = []
        
        
        # creating list of element to translate
        it = session.create_iterator(session.sc_constraint_new(sc_constants.CONSTR_3_f_a_a,
                                                               _input,
                                                               sc.SC_A_CONST | sc.SC_POS,
                                                               0), True)
        list_of_addrs = []
        while not it.is_over():
            trans_objs.append(it.value(2))
            list_of_addrs.append(str(it.value(2).this))
            it.next()
            
        # getting objects on sheet
        childs = sheet.getChilds()
        sc_scg = {}
        object_types = {}
        for obj in childs:
            addr = obj._getScAddr()
            if addr is not None:
                s_addr = str(addr.this)    
                sc_scg[s_addr] = obj
                object_types[s_addr] = session.get_type(addr)
                list_of_addrs.append(s_addr)
        
        ignore_list = []
        process_pairs = []

        # translating binary and noorient pairs and store types
        for obj in trans_objs:
            _type = session.get_type(obj)
            object_types[str(obj.this)] = _type
            
            if str(obj.this) in ignore_list: 
                continue
            
            # checking for sheaf nodes
            if _type & sc.SC_NODE and sc_utils.isNodeSheaf(session, obj):
                res = get_pair_binary(session, obj, list_of_addrs)
                if res is not None:
                    for idx in xrange(len(res[0])):
                        if idx != 0 and idx != 4:
                            ignore_list.append(str(res[0][idx].this))
                        
                    #ignore_list.extend(res[0])
                    # creating pair
                    _const = "const"
                    if _type & sc.SC_VAR:
                        _const = "var"
                    elif _type & sc.SC_METAVAR:
                        _const = "meta"
                    
                    _orient = "-"
                    if res[1]:
                        _orient = "orient"
                    type_name = "pair/-/-/%s/%s" % (_orient, _const)
                                        
                    # creating pair
                    scg_obj = scg_alphabet.createSCgPair(type_name)
                    scg_obj._setScAddr(obj)
                    sc_scg[str(obj.this)] = scg_obj
                    
                    # append additional sc-addrs
                    for addr in res[0]:
                        if addr.this != obj.this:
                            scg_obj.additionalScAddrs.append(addr)
                    
                    #scg_obj.setWasInMemory(True)
                    
                    # appending to sheet
                    #sheet.addChild(scg_obj)
                    result_objs.append(scg_obj)
                    
                    process_pairs.append( (res[0][2], res[0][0], res[0][4]) )
                
        
        # translating objects
        for obj in trans_objs:
            if sc_scg.has_key(str(obj.this)) or (str(obj.this) in ignore_list):
                continue
            
            _type = object_types[str(obj.this)]
                        
            # checking pairs
            if _type & sc.SC_ARC:
                beg = session.get_beg(obj)
                end = session.get_end(obj)
                if (beg is not None) and (end is not None):
                    if (str(beg.this) in list_of_addrs) and (str(end.this) in list_of_addrs):
                        process_pairs.append((obj, beg, end)) 
                    else:
                        continue    # skipping dead (haven't begin or end element) pairs
                         
                    
            # translating sc-element to scg-object
            scg_obj = translate_obj(session, obj, object_types[str(obj.this)])
            
            sc_scg[str(obj.this)] = scg_obj
            # translating identificators
#            idtf = session.get_idtf(obj)
#            if not sc_utils.isSystemId(idtf):
#                scg_obj.setText(idtf)
            
            #scg_obj.setWasInMemory(True)
            
            # adding to window
            #sheet.addChild(scg_obj)
            result_objs.append(scg_obj)
            
        # linking pairs
        for pair, beg, end in process_pairs:
            scg_pair = sc_scg[str(pair.this)]
            if sc_scg.has_key(str(beg.this)) and sc_scg.has_key(str(end.this)):
                scg_beg = sc_scg[str(beg.this)]
                scg_end = sc_scg[str(end.this)]
                assert scg_end is not None and scg_beg is not None
                scg_pair.setBegin(scg_beg)
                scg_pair.setEnd(scg_end)
            
        # get all pairs from sheet and link them to begin and end object if they are present in translated set
        for obj in sheet.getChilds():
            if isinstance(obj, scg_objects.SCgPair):
                addr = obj._getScAddr()
                if addr is not None:
                    beg_addr = session.get_beg(addr)
                    end_addr = session.get_end(addr)
                    
                    if (beg_addr is not None) and sc_scg.has_key(str(beg_addr.this)):
                        obj.setBegin(sc_scg[str(beg_addr.this)])
                    if (end_addr is not None) and sc_scg.has_key(str(end_addr.this)):
                        obj.setEnd(sc_scg[str(end_addr.this)])
        
        
        # append into sheet
        for obj in result_objs:
            obj.setWasInMemory(True)
            sheet.addChild(obj)
        
        return errors
       
            