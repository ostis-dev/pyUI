
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

"""SCg-code to SC-code translator component
"""
from suit.core.objects import Translator
import suit.core.objects as objects
import suit.core.kernel as core
import scg_environment as env
import sc_core.pm as sc
import suit.core.keynodes as keynodes
import scg_objects

def translate_object(_segment, _object, _type, _params):
    """Translates specified scg-object to SC-code.
    @param _segment:    segment to translate object in
    @type _segment:    sc_segment
    @param _object:    scg-object to translate
    @type _object:    SCgObject or SCgPair
    @param _type:    object type
    @type _type:    sc_type
    @param _params:    additional parameters to translate object. It contains list of sc-elements, that
    designates semantic types for specified object. sc-element, that designate translated object will be included to
    sets from _params
    @type _params:    list
    
    @return: if object translated successfully, then return True, else - False
    @rtype: bool
    """
    import suit.core.sc_utils as sc_utils
    session = core.Kernel.session()
    
    # getting node idtf
    idtf = _object.getText()
    
    sc_object = None
    el = None
    isUri = False
    created  = False
    
    # if idtf empty, then creating new element
    if idtf is None:
        el = session.create_el(_segment, _type)
        created = True
    else:
        # encode idtf to cp1251
        idtf = sc_utils.utf8ToCp1251(str(idtf))

        # check if idtf if full uri
        isUri = idtf.startswith('/')
    
    # trying to find object by idtf, if it doesn't exists, then creating it
    try:
        if el is None:
            if isUri:
                el = session.find_el_full_uri(idtf)
                if el is None:
                    el = session.create_el_full_uri(idtf, _type)[1]
                    created = True
            else:
                _segs = [_segment.get_full_uri()]
                _segs.extend(env.search_segments)
                # trying to find element
                el = sc_utils.getElementByIdtf(idtf, _segs)
                if el is None:
                    el = session.create_el_idtf(_segment, _type, idtf)[1]
                    created = True
    except:
        import sys, traceback
        print sys.exc_info()[0]
        traceback.print_exc(file=sys.stdout)
        return False
        
    assert el is not None
    
    _object._setScAddr(el)
    _object.setMerged(not created)
    
    # including to sets for structure type
    for param in _params:
        sc_utils.createPairPosPerm(session, _segment, param, el, sc.SC_CONST)
    
    return True
        

# map that contains translation rules
# key - type name
# value - tuple (function, data)
# each function takes segment, object and data as parameters and translates object 
translate_rules = {'node/elem':             (translate_object, sc.SC_NODE, []),
                   'node/const/elem':       (translate_object, sc.SC_N_CONST, []),
                   'node/const/sheaf':      (translate_object, sc.SC_N_CONST, [keynodes.info.stype_sheaf]),
                   'node/const/abstract':   (translate_object, sc.SC_N_CONST, [keynodes.info.stype_ext_obj_abstract]),
                   'node/const/binary':     (translate_object, sc.SC_N_CONST, [keynodes.info.stype_bin_orient_norole_rel]),
                   'node/const/real':       (translate_object, sc.SC_N_CONST, [keynodes.info.stype_ext_obj_real]),
                   'node/const/role':       (translate_object, sc.SC_N_CONST, [keynodes.info.stype_bin_orient_role_rel]),
                   'node/const/struct':     (translate_object, sc.SC_N_CONST, [keynodes.info.stype_struct]),
                   'node/const/term':       (translate_object, sc.SC_N_CONST, [keynodes.info.stype_concept_norel]),
                   
                   'node/var/elem':         (translate_object, sc.SC_N_VAR, []),
                   'node/var/sheaf':        (translate_object, sc.SC_N_VAR, [keynodes.info.stype_sheaf]),
                   'node/var/abstract':     (translate_object, sc.SC_N_VAR, [keynodes.info.stype_ext_obj_abstract]),
                   'node/var/binary':       (translate_object, sc.SC_N_VAR, [keynodes.info.stype_bin_orient_norole_rel]),
                   'node/var/real':         (translate_object, sc.SC_N_VAR, [keynodes.info.stype_ext_obj_real]),
                   'node/var/role':         (translate_object, sc.SC_N_VAR, [keynodes.info.stype_bin_orient_role_rel]),
                   'node/var/struct':       (translate_object, sc.SC_N_VAR, [keynodes.info.stype_struct]),
                   'node/var/term':         (translate_object, sc.SC_N_VAR, [keynodes.info.stype_concept_norel]),
                   
                   'node/meta/elem':        (translate_object, sc.SC_N_METAVAR, []),
                   'node/meta/sheaf':       (translate_object, sc.SC_N_METAVAR, [keynodes.info.stype_sheaf]),
                   'node/meta/abstract':    (translate_object, sc.SC_N_METAVAR, [keynodes.info.stype_ext_obj_abstract]),
                   'node/meta/binary':      (translate_object, sc.SC_N_METAVAR, [keynodes.info.stype_bin_orient_norole_rel]),
                   'node/meta/real':        (translate_object, sc.SC_N_METAVAR, [keynodes.info.stype_ext_obj_real]),
                   'node/meta/role':        (translate_object, sc.SC_N_METAVAR, [keynodes.info.stype_bin_orient_role_rel]),
                   'node/meta/struct':      (translate_object, sc.SC_N_METAVAR, [keynodes.info.stype_struct]),
                   'node/meta/term':        (translate_object, sc.SC_N_METAVAR, [keynodes.info.stype_concept_norel]),
                   
                   'pair/-/-/-/-':                  (translate_object, sc.SC_ARC, []),
                   # no orient pairs (for orient and no orient binary pairs
                   # creating just sheaf node in rules, another arcs will be created later
                   # on next stage)
                   'pair/-/-/-/const':            (translate_object, sc.SC_N_CONST, [keynodes.info.stype_sheaf]),
                   'pair/-/-/-/var':              (translate_object, sc.SC_N_VAR, [keynodes.info.stype_sheaf]),
                   'pair/-/-/-/meta':             (translate_object, sc.SC_N_METAVAR, [keynodes.info.stype_sheaf]),
                   # orient pairs
                   'pair/-/-/orient/const':     (translate_object, sc.SC_N_CONST, [keynodes.info.stype_sheaf]),
                   'pair/-/-/orient/var':       (translate_object, sc.SC_N_VAR, [keynodes.info.stype_sheaf]),
                   'pair/-/-/orient/meta':      (translate_object, sc.SC_N_METAVAR, [keynodes.info.stype_sheaf]),
                   
                   'pair/fuz/-/orient/const':        (translate_object, sc.SC_A_CONST | sc.SC_FUZ, []),
                   'pair/fuz/-/orient/var':          (translate_object, sc.SC_A_VAR | sc.SC_FUZ, []),
                   'pair/fuz/-/orient/meta':         (translate_object, sc.SC_A_METAVAR | sc.SC_FUZ, []),
                   'pair/neg/-/orient/const':        (translate_object, sc.SC_A_CONST | sc.SC_NEG, []),
                   'pair/neg/-/orient/var':          (translate_object, sc.SC_A_VAR | sc.SC_NEG, []),
                   'pair/neg/-/orient/meta':         (translate_object, sc.SC_A_METAVAR | sc.SC_NEG, []),
                   'pair/pos/-/orient/const':        (translate_object, sc.SC_A_CONST | sc.SC_POS, []),
                   'pair/pos/-/orient/var':          (translate_object, sc.SC_A_VAR | sc.SC_POS, []),
                   'pair/pos/-/orient/meta':         (translate_object, sc.SC_A_METAVAR | sc.SC_POS, []),
                   
                   'pair/pos/time/orient/const':   (translate_object, sc.SC_A_CONST | sc.SC_POS | sc.SC_TEMPORARY, []),
                   'pair/pos/time/orient/var':     (translate_object, sc.SC_A_VAR | sc.SC_POS | sc.SC_TEMPORARY, []),
                   'pair/pos/time/orient/meta':    (translate_object, sc.SC_A_METAVAR | sc.SC_POS | sc.SC_TEMPORARY, []),
                   'pair/neg/time/orient/const':   (translate_object, sc.SC_A_CONST | sc.SC_NEG | sc.SC_TEMPORARY, []),
                   'pair/neg/time/orient/var':     (translate_object, sc.SC_A_VAR | sc.SC_NEG | sc.SC_TEMPORARY, []),
                   'pair/neg/time/orient/meta':    (translate_object, sc.SC_A_METAVAR | sc.SC_NEG | sc.SC_TEMPORARY, []),
                   'pair/fuz/time/orient/const':   (translate_object, sc.SC_A_CONST | sc.SC_FUZ | sc.SC_TEMPORARY, []),
                   'pair/fuz/time/orient/var':     (translate_object, sc.SC_A_VAR | sc.SC_FUZ | sc.SC_TEMPORARY, []),
                   'pair/fuz/time/orient/meta':    (translate_object, sc.SC_A_METAVAR | sc.SC_FUZ | sc.SC_TEMPORARY, [])                   
                   }


class TranslatorSCg2Sc(Translator):
    """Translator from SCg-code to SC-code.
    
    Translates constructions in scg-window directly to SC-code.
    """
    
    def __init__(self):
        Translator.__init__(self)
    
    def __del__(self):
        Translator.__del__(self)
        
    def translate_impl(self, _input, _output):
        """Translator implementation
        """
        # FIXME:    append type changing. Element type will be changing, if it is temporary segment
        #            or is in semantic equivalent construction set
        
        # FIXME:    think about multiply windows for one sc-element
        objs = objects.ScObject._sc2Objects(_input)
        
        assert len(objs) > 0
        sheet = objs[0]
        assert isinstance(sheet, objects.ObjectSheet)
    
        seg = sheet.getTmpSegment()
    
        errors = []
        session = core.Kernel.session()
        import suit.core.sc_utils as sc_utils
    
        # removing old objects
#        for obj in sheet.getChilds():
#            _addr = obj._getScAddr()
#            if _addr is not None:
#                if _addr.seg.this == seg.this or isinstance(obj, scg_objects.SCgPair):
#                    obj._setScAddr(None)
#                    session.erase_el(_addr)
                
    
        # getting objects, that need to be translated
        trans_obj = []
        for obj in sheet.getChilds():
            if obj._getScAddr() is None:
                trans_obj.append(obj)
                if not isinstance(obj, objects.ObjectSheet):
                    # translating objects
                    obj_type = obj.getType()
                    
                    if obj_type == "sheet": continue
                    
                    if not translate_rules.has_key(obj_type):
                        errors.append((obj, "There are no any rules for type %s" % obj_type))
                    else:
                        #try:
                        func, obj_type, params = translate_rules[obj_type]
                        func(seg, obj, obj_type, params)
                        #except:
#                            import sys
#                            errors.append((obj, "Error: %s" % str(sys.exc_info()[0])))
                else:
                    # sheet translation
                    translate_object(seg, obj, sc.SC_NODE, [])
                    content_type, content_data, content_format = obj.getContent()
                    
                    assert content_type is not objects.ObjectSheet.CT_Unknown
                    addr = obj._getScAddr()
                    assert addr is not None
                    
                    if content_type == objects.ObjectSheet.CT_String:
                        session.set_content_str(addr, content_data)
                    elif content_type == objects.ObjectSheet.CT_Real:
                        session.set_content_real(addr, content_data)
                    elif content_type == objects.ObjectSheet.CT_Int:
                        session.set_content_int(addr, content_data)
                    elif content_type == objects.ObjectSheet.CT_Binary:
                        pass # FIXME: add binary content
                    
                    sc_utils.createPairPosPerm(session, seg, content_format, addr, sc.SC_CONST)
                
        # linking objects
        noorient_pairs = ['pair/-/-/-/const', 'pair/-/-/-/var', 'pair/-/-/-/meta']
        orient_pairs = ['pair/-/-/orient/const', 'pair/-/-/orient/var', 'pair/-/-/orient/meta']
        for obj in trans_obj:
            obj_type = obj.getType()
            
            # check if object is orient pair
            isPair = obj_type.startswith("pair")
            isOrient = False
            isNoorient = False
            
            # skipping no pair objects
            if not isPair:  continue
            
            if obj_type in noorient_pairs:
                isNoorient = True    
            if obj_type in orient_pairs:
                isOrient = True
                
            el = obj._getScAddr()            
            
            if isOrient or isNoorient:
                _const = sc.SC_CONST
                if obj_type.find('var') != -1:
                    _const = sc.SC_VAR
                elif obj_type.find('meta') != -1:
                    _const = sc.SC_METAVAR  
            
                            
                # generating arguments
                a1 = sc_utils.createPairPosPerm(session, seg, el, obj.getBegin()._getScAddr(), _const)
                a2 = sc_utils.createPairPosPerm(session, seg, el, obj.getEnd()._getScAddr(), _const)
                obj.additionalScAddrs = [a1, a2]
                if isOrient:
                    p1 = sc_utils.createPairPosPerm(session, seg, keynodes.n_1, a1, _const)
                    p2 = sc_utils.createPairPosPerm(session, seg, keynodes.n_2, a2, _const)
                    obj.additionalScAddrs.extend([p1, p2])
            else:
                # set begin and end objects for pair
                session.set_beg(el, obj.getBegin()._getScAddr())
                session.set_end(el, obj.getEnd()._getScAddr())
                
        return errors
        
        