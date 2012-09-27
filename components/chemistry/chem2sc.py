
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
Created on 29.06.2010

@author: Denis Koronchik
'''

from suit.core.objects import Translator  
#from srs_engine.objects import Translator
import suit.core.objects as objects
import suit.core.kernel as core
import sc_core.pm as sc

import chem_objects, chem_keynodes

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
    import suit.core.sc_utils as sc_utils
    session = core.Kernel.session()
    
    if isinstance(_object, chem_objects.ChemistryAtom):
        _addr = session.create_el(_segment, sc.SC_N_CONST)
        sc_utils.createPairPosPerm(session, _segment, getattr(chem_keynodes, "atom_%s" % _object._name), _addr, sc.SC_CONST)
        _object._setScAddr(_addr)
        
    elif isinstance(_object, chem_objects.ChemistryLink):
        _addr = session.create_el(_segment, sc.SC_N_CONST)
        sc_utils.createPairPosPerm(session, _segment, chem_keynodes.link, _addr, sc.SC_CONST)
        
        addr_begin = _object.getBegin()._getScAddr()
        addr_end = _object.getEnd()._getScAddr()
        
        assert addr_begin and addr_end
    
        a1 = sc_utils.createPairBinaryOrient(session, _segment, _addr, addr_begin, sc.SC_CONST)
        sc_utils.createPairPosPerm(session, _segment, chem_keynodes.linked_atom, a1, sc.SC_CONST)
        a2 = sc_utils.createPairBinaryOrient(session, _segment, _addr, addr_end, sc.SC_CONST)
        sc_utils.createPairPosPerm(session, _segment, chem_keynodes.linked_atom, a2, sc.SC_CONST)
        
        _object._setScAddr(_addr)
        
    
    return True

class TranslatorChemistry2Sc(Translator):
    
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
        import suit.core.sc_utils as sc_utils
    
        # getting objects, that need to be translated
        trans_obj = []
        for obj in sheet.getChilds():
            _addr = obj._getScAddr()
            if _addr is None:
                trans_obj.append(obj)
                # remove old translation data
            else:
                if _addr.seg == segment:
                    session.erase_el(_addr)
        
        # make translation
        links = []
        for obj in trans_obj:
            # skipping lines for now
            if isinstance(obj, chem_objects.ChemistryLink):
                links.append(obj)
                continue
            
            if not translate_object(segment, obj, None):
                errors.append( ((obj, "Error while translating object %s" % str(obj))) )
            
        for obj in links:
            if not translate_object(segment, obj, None):
                errors.append( ((obj, "Error while translating object %s" % str(obj))) )
        
        return errors