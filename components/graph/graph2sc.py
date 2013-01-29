
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
Created on 21.05.2012

@author: Denis Koronchick
'''
from suit.core.objects import Translator
import suit.core.sc_utils as sc_utils
import suit.core.objects as objects
import suit.core.kernel as core

import sc_core.pm as sc

import graph_objects
import graph_keynodes

class TranslatorGraph2Sc(Translator):
    
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
                    #session.erase_el(_addr)
                    trans_obj.append(obj)
                

        # sort objects to nodes and edges
        verticies = []
        edges = []
        
        for obj in trans_obj:
            
            if isinstance(obj, graph_objects.GraphVertex):
                verticies.append(obj)
            elif isinstance(obj, graph_objects.GraphLink):
                edges.append(obj)
                
        
        graph = sc_utils.createNode(session, segment, sc.SC_CONST, "struct")
        sc_utils.createPairPosPerm(session, segment, graph_keynodes.Common.graph, graph, sc.SC_CONST)        
        
        # create all nodes
        for node in verticies:
            
            sc_node = sc_utils.createNode(session, segment, sc.SC_CONST, "element")
            node._setScAddr(sc_node)
            # append into graph with vertex attribute
            a = sc_utils.createPairPosPerm(session, segment, graph, sc_node, sc.SC_CONST)
            a1 = sc_utils.createPairPosPerm(session, segment, graph_keynodes.Common.rrel_vertex, a, sc.SC_CONST)
                        
        # create edges
        for edge in edges:
            
            sc_edge = sc_utils.createNodeSheaf(session, segment, sc.SC_CONST)
            
            # append into graph with edge attribute
            a = sc_utils.createPairPosPerm(session, segment, graph, sc_edge, sc.SC_CONST)
            a1 = sc_utils.createPairPosPerm(session, segment, graph_keynodes.Common.rrel_edge, a, sc.SC_CONST)
            
            # setup begin and end objects
            beg = edge.getBegin()._getScAddr()
            end = edge.getEnd()._getScAddr()
            
            a2 = sc_utils.createPairPosPerm(session, segment, sc_edge, beg, sc.SC_CONST)
            a3 = sc_utils.createPairPosPerm(session, segment, sc_edge, end, sc.SC_CONST)
            
            edge._setScAddr(sc_edge)

                
        print "Translation errors:"    
        for obj, error in errors:
            print error 

        return errors