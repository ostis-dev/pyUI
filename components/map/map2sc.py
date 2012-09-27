
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
Created on 12.02.2010

@author: Denis Koronchik
'''


from suit.core.objects import Translator
import suit.core.objects as objects
import suit.core.core as core
import pm.pm as sc
import suit.core.keynodes as keynodes
import map_keynodes
import map_environment as env

class TranslatorMap2Sc(Translator):
    """Translator from map to SC-code.
    
    Translates constructions in map-window directly to SC-code.
    """
    def __init__(self):
        Translator.__init__(self)
		
    
    def __del__(self):
        Translator.__del__(self)
        
    def translate_impl(self, _input, _output):
        """Translator implementation
        """
        
        errors = []
        
        objs = objects.ScObject._sc2Objects(_input)
        
        assert len(objs) > 0
        sheet = objs[0]
        assert isinstance(sheet, objects.ObjectSheet)
    
        seg = sheet.getTmpSegment()
        
        import suit.core.sc_utils as sc_utils
    
        errors = []
        session = core.Kernel.session()
        
        # getting data and translate to sc
        field = sheet.getLogic().field
        
        print field
    
        # remove old objects
        for layer in field.layers:
            for item in layer.items:
                _addr = item._getScAddr()
                if _addr is not None:
                    if _addr.seg.this == seg.this:
                        item._setScAddr(None)
                        session.erase_el(_addr)
        
        classifier = field.classifier
        _segs = [seg.get_full_uri()]
        _segs.extend(env.search_segments)
        
        for layer in field.layers:
            for item in layer.items:
#                if (not item.type in classifier.TYPES_TOWN):
#                    continue
                
                # creating node in sc-memory
                _addr = sc_utils.createNodeElement(session, seg, sc.SC_CONST)
                item._setScAddr(_addr)
                if (item.type in classifier.TYPES_TOWN):
                    sc_utils.createPairPosPerm(session, seg, map_keynodes.ObjectType.town, _addr, sc.SC_CONST)
                elif (item.type in classifier.TYPES_RAILWAY):
                    sc_utils.createPairPosPerm(session, seg, map_keynodes.ObjectType.railway, _addr, sc.SC_CONST)                      
                elif item.type == classifier.TYPE_DISTRICT:
                    sc_utils.createPairPosPerm(session, seg, map_keynodes.ObjectType.district, _addr, sc.SC_CONST)
                elif item.type == classifier.TYPE_AREA:
                    sc_utils.createPairPosPerm(session, seg, map_keynodes.ObjectType.area, _addr, sc.SC_CONST)    
                elif item.type in classifier.TYPES_ROAD:
                    sc_utils.createPairPosPerm(session, seg, map_keynodes.ObjectType.road, _addr, sc.SC_CONST)                    

                
                for atribute in item.attributes:
                    if ((atribute in classifier.atributes)  and  (item.attributes[atribute]!="")):
                        _atr=sc_utils.getElementByIdtf(classifier.atributes[atribute], _segs)
                        if _atr is None:
                            _atr = sc_utils.createNodeRoleRelation(session, seg, sc.SC_CONST)
                            session.set_idtf(_atr, classifier.atributes[atribute])
                        _val=sc_utils.getElementByIdtf(item.attributes[atribute], _segs)
                        if _val is None:
                            _val = sc_utils.createNodeElement(session, seg, sc.SC_CONST)
                            session.set_idtf(_val, item.attributes[atribute])
                        #print classifier.atributes[atribute], item.attributes[atribute]
                        pair = sc_utils.createPairPosPerm(session, seg, _addr, _val, sc.SC_CONST)
                        sc_utils.createPairPosPerm(session, seg, _atr, pair, sc.SC_CONST)
        return errors