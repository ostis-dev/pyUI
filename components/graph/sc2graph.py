
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
from suit.core import sc_utils


'''
Created on 21.05.2012

@author: Denis Koronchick
'''
from suit.core.objects import Translator
import suit.core.objects as objects
import suit.core.kernel as core
import sc_core.constants as sc_constants
import sc_core.pm as sc

import graph_keynodes
import graph_objects

def translate_node(_session, _el):
    """Translate node from sc-representation into graphical object
    """
    res = graph_objects.GraphVertex()
    res._setScAddr(_el)

    return res 

def translate_edge(_session, _el, _sc2Node):
    """Translate edge from sc-representation into graphical object
    """
    # TODO: support of edge orientation
    
    res = graph_objects.GraphLink()
    it = _session.create_iterator(_session.sc_constraint_new(sc_constants.CONSTR_3_f_a_a,
                                                           _el,
                                                           sc.SC_A_CONST | sc.SC_POS,
                                                           sc.SC_NODE), True)
    if it.is_over():
        raise RuntimeError("Invalid graph structure edge")
    
    res.setBegin(_sc2Node[str(it.value(2).this)])

    it.next()
    if it.is_over():
        raise RuntimeError("Invalid graph structure edge")
    res.setEnd(_sc2Node[str(it.value(2).this)])

    it.next()
    
    if not it.is_over():
        raise RuntimeError("Invalid graph structure edge")
        
    res._setScAddr(_el)
        
    return res

class TranslatorSc2Graph(Translator):
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
        
        # remove old graph
        while len(sheet.getChilds()) > 0:
            sheet._deleteObject(sheet.getChilds()[0])
        
        # trying to fin graph node
#        graph = session.search_one_shot(session.sc_constraint_new(sc_constants.CONSTR_5_f_a_a_a_f,
#                                                                     graph_keynodes.Common.graph,
#                                                                     sc.SC_A_CONST,
#                                                                     sc.SC_N_CONST,
#                                                                     sc.SC_A_CONST,
#                                                                     _input), True, 5)
        it = session.create_iterator(session.sc_constraint_new(sc_constants.CONSTR_3_f_a_a,
                                                               _input,
                                                               sc.SC_A_CONST | sc.SC_POS,
                                                               sc.SC_NODE), True)
        graph = None
        while not it.is_over():
            if sc_utils.checkIncToSets(session, it.value(2), [graph_keynodes.Common.graph], sc.SC_CONST):
                graph = it.value(2)
                break
            it.next()
        
        
        if graph is not None:
            
            # get all nodes and translate them
            it = session.create_iterator(session.sc_constraint_new(sc_constants.CONSTR_5_f_a_a_a_f,
                                                                   graph,
                                                                   sc.SC_A_CONST | sc.SC_POS,
                                                                   sc.SC_NODE,
                                                                   sc.SC_A_CONST | sc.SC_POS,
                                                                   graph_keynodes.Common.rrel_vertex), True)
            sc2Obj = {} 
            while not it.is_over():
                sc_node = it.value(2)
                
                if sc_utils.checkIncToSets(session, sc_node, [_input], sc.SC_CONST | sc.SC_POS):
                    sc2Obj[str(sc_node.this)] = translate_node(session, sc_node)
                    
                it.next()
                
            # get all edges and translate them
            it = session.create_iterator(session.sc_constraint_new(sc_constants.CONSTR_5_f_a_a_a_f,
                                                                   graph,
                                                                   sc.SC_A_CONST | sc.SC_POS,
                                                                   sc.SC_NODE,
                                                                   sc.SC_A_CONST | sc.SC_POS,
                                                                   graph_keynodes.Common.rrel_edge), True)
            while not it.is_over():
                sc_edge = it.value(2)
                
                if sc_utils.checkIncToSets(session, sc_edge, [_input], sc.SC_CONST | sc.SC_POS):
                    sc2Obj[str(sc_edge.this)] = translate_edge(session, sc_edge, sc2Obj)
                it.next()
            
            
            for obj in sc2Obj.values():
                obj.setWasInMemory(True)
                sheet.addChild(obj)
        else:
            errors.append("There are no graph structure to translate")                   
        
        return errors