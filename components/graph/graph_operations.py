
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
from glob import glob


'''
Created on 20.05.2012

@author: Denis Koronchick
'''
import os
import suit.core.kernel as core
import suit.core.sc_utils as sc_utils
import sc_core.pm as sc
import sc_core.constants as sc_constants
import networkx as nx
from suit.core.event_handler import ScEventHandlerSetMember
import suit.core.keynodes as keynodes
import graph_keynodes
import random

class Graph:
    
    """Class that wraps convertation of graphs between sc and netwokx representations 
    """
    
    def __init__(self, _segment = None, _sc_addr = None, _graph_nx = None):
        """
        @param _segment: segment to work with sc representation 
        @param _sc_addr: sc-addr of sc-node that designate graph  structure
        @param _graph_nx: networkx graph object  
        """
        self.graphNx = _graph_nx
        self.graphSc = _sc_addr
        self.segment = _segment 
    
    def makeNxGraph(self):
        """Construct networkX graph object from sc representation
        """
        assert self.graphNx is None
        assert self.graphSc is not None
        
        session = core.Kernel.session()
        
        # get all nodes and translate them
        it = session.create_iterator(session.sc_constraint_new(sc_constants.CONSTR_5_f_a_a_a_f,
                                                               self.graphSc,
                                                               sc.SC_A_CONST | sc.SC_POS,
                                                               sc.SC_NODE,
                                                               sc.SC_A_CONST | sc.SC_POS,
                                                               graph_keynodes.Common.rrel_vertex), True)
        sc2Obj = {} 
        idx = 0
        self.graphNx = nx.Graph()
        while not it.is_over():
            sc_node = it.value(2)
            
            sc2Obj[str(sc_node.this)] = idx
            self.graphNx.add_node(idx)
            idx += 1
            
                
            it.next()
            
        # get all edges and translate them
        it = session.create_iterator(session.sc_constraint_new(sc_constants.CONSTR_5_f_a_a_a_f,
                                                               self.graphSc,
                                                               sc.SC_A_CONST | sc.SC_POS,
                                                               sc.SC_NODE,
                                                               sc.SC_A_CONST | sc.SC_POS,
                                                               graph_keynodes.Common.rrel_edge), True)
        while not it.is_over():
            sc_edge = it.value(2)
            
            it1 = session.create_iterator(session.sc_constraint_new(sc_constants.CONSTR_3_f_a_a,
                                                       sc_edge,
                                                       sc.SC_A_CONST | sc.SC_POS,
                                                       sc.SC_NODE), True)
            if it1.is_over():
                raise RuntimeError("Invalid graph structure edge")
            
            b = sc2Obj[str(it1.value(2).this)]
        
            it1.next()
            if it1.is_over():
                raise RuntimeError("Invalid graph structure edge")
            e = sc2Obj[str(it1.value(2).this)]
        
            it1.next()
            
#            if not it.is_over():
#                raise RuntimeError("Invalid graph structure edge")
            
            self.graphNx.add_edge(b, e)
                            
            it.next()
            
        return sc2Obj
    
    def makeScGraph(self):
        """Construct sc representation of netwokX graph
        @return: Return sc_addr of structure, that include all elements of generated sc-graph construction
        """
        assert self.graphSc is None
        assert self.graphNx is not None
               
        _session = core.Kernel.session()
        
        result = sc_utils.createNode(_session, self.segment, sc.SC_CONST, "element")

        self.graphSc = sc_utils.createNode(_session, self.segment, sc.SC_CONST, "struct")
        a = sc_utils.createPairPosPerm(_session, self.segment, graph_keynodes.Common.graph, self.graphSc, sc.SC_CONST)
        
        res_list = [self.graphSc, a]
        nx2sc = {}
        
        # create all nodes
        for node in self.graphNx.nodes():
            
            sc_node = sc_utils.createNode(_session, self.segment, sc.SC_CONST, "element")
            nx2sc[node] = sc_node
            # append into graph with vertex attribute
            a = sc_utils.createPairPosPerm(_session, self.segment, self.graphSc, sc_node, sc.SC_CONST)
            a1 = sc_utils.createPairPosPerm(_session, self.segment, graph_keynodes.Common.rrel_vertex, a, sc.SC_CONST)
            
            res_list.extend([sc_node, a, a1])
            
        # create edges
        for edge in self.graphNx.edges():
            
            sc_edge = sc_utils.createNodeSheaf(_session, self.segment, sc.SC_CONST)
            
            # append into graph with edge attribute
            a = sc_utils.createPairPosPerm(_session, self.segment, self.graphSc, sc_edge, sc.SC_CONST)
            a1 = sc_utils.createPairPosPerm(_session, self.segment, graph_keynodes.Common.rrel_edge, a, sc.SC_CONST)
            
            # setup begin and end objects
            beg, end = edge
            a2 = sc_utils.createPairPosPerm(_session, self.segment, sc_edge, nx2sc[beg], sc.SC_CONST)
            a3 = sc_utils.createPairPosPerm(_session, self.segment, sc_edge, nx2sc[end], sc.SC_CONST)
        
            res_list.extend([sc_edge, a, a1, a2, a3])
            
        res_list.extend([graph_keynodes.Common.rrel_edge, 
                         graph_keynodes.Common.rrel_vertex, 
                         graph_keynodes.Common.graph
                         ])
        # create result set
        for r in res_list:
            sc_utils.createPairPosPerm(_session, self.segment, result, r, sc.SC_CONST)
            
        return result

graph_generators = []
graph_prop_calculators = []
graph_element_prop_calculators = []

def generate_any():
    return nx.gnm_random_graph(random.randint(5, 15), random.randint(3, 25))

def generate_regular():
    return nx.random_regular_graph(random.randint(1, 5), random.randint(3, 8) * 2)

def generate_cycle():
    return nx.cycle_graph(random.randint(5, 15))

def generate_cubic():
    return nx.cubical_graph()



def calculate_diameter(g):
    return nx.diameter(g)

def calculate_radius(g):
    return nx.radius(g)

def calculate_connected_components(g):
    return nx.number_connected_components(g)



def calculate_vertex_degree(graph, vertex):
    print graph
    print vertex
    return nx.degree(graph)[vertex]

def initialize():
    kernel = core.Kernel.getSingleton()
    kernel.registerOperation(ScEventHandlerSetMember(u"operation that generate random graph structure",
                                                     keynodes.ui.init_user_cmd,
                                                     generate_graph, []))
    
    kernel.registerOperation(ScEventHandlerSetMember(u"operation that found whole graph structure",
                                                     keynodes.questions.initiated,
                                                     find_graph, []))
    
    kernel.registerOperation(ScEventHandlerSetMember(u"operation that calculates any properties of a graph",
                                                     keynodes.questions.initiated,
                                                     calculate_graph_prop, []))
    
    kernel.registerOperation(ScEventHandlerSetMember(u"operation that calculate any properties of a graph element",
                                                     keynodes.questions.initiated,
                                                     calculate_graph_element_prop, []))
    
    global graph_generators
    # register generators
    graph_generators = [(graph_keynodes.Command.generate_any_graph, generate_any),
                        (graph_keynodes.Command.generate_regular_graph, generate_regular),
                        (graph_keynodes.Command.generate_cycle_graph, generate_cycle),
                        (graph_keynodes.Command.generate_cubic_graph, generate_cubic)
                        ]
    
    global graph_prop_calculators
    graph_prop_calculators = [(graph_keynodes.Command.calculate_graph_diameter, calculate_diameter, graph_keynodes.Common.nrel_diameter),
                              (graph_keynodes.Command.calculate_graph_radius, calculate_radius, graph_keynodes.Common.nrel_radius),
                              #(graph_keynodes.Command.calculate_graph_connected_components, calculate_connected_components, graph_keynodes.Common.nrel_connected_components_num)
                              ]
    
    global graph_element_prop_calculators
    graph_element_prop_calculators = [(graph_keynodes.Command.calculate_graph_vertex_degree, calculate_vertex_degree, graph_keynodes.Common.nrel_vertex_degree),
                                      ]

def shutdown():
    pass


def generate_graph(_params, _segment):

    kernel = core.Kernel.getSingleton()
    session = kernel.session()
    segment = kernel.segment()
        
    # check type
    command = session.search_one_shot(session.sc_constraint_new(sc_constants.CONSTR_5_f_a_a_a_f,
                                                                     keynodes.ui.init_user_cmd,
                                                                     sc.SC_A_CONST,
                                                                     sc.SC_N_CONST,
                                                                     sc.SC_A_CONST,
                                                                     _params), True, 5)
    
    assert command is not None
    command = command[2]
    
    
    
    G = None
    # run one of generators
    global graph_generators
    for keynode, generator in graph_generators:
        # check type
        if not sc_utils.checkIncToSets(session, command, [keynode], sc.SC_CONST):
            continue
        
        G = generator()
    
    if G is None:
        return
    
    # create graph randomly
    g = Graph(segment, None, G)
    res = g.makeScGraph()
    
    # get current window
    output = kernel.getRootSheet()
    assert output is not None
    
    # make output set, that include whole graph construction
    
    kernel.translateFromSc(res, output._getScAddr())   


def find_graph(_params, _segment):

    kernel = core.Kernel.getSingleton()
    session = kernel.session()
    segment = kernel.segment()
        
    # check type
    question = session.search_one_shot(session.sc_constraint_new(sc_constants.CONSTR_5_f_a_a_a_f,
                                                                 keynodes.questions.initiated,
                                                                 sc.SC_A_CONST,
                                                                 sc.SC_N_CONST,
                                                                 sc.SC_A_CONST,
                                                                 _params), True, 5)
    
    assert question is not None
    question = question[2]
    
    # check command type
    if sc_utils.checkIncToSets(session, question, [graph_keynodes.Command.search_graph_full], sc.SC_CONST):
        
        graph = session.search_one_shot(session.sc_constraint_new(sc_constants.CONSTR_3_f_a_a,
                                                                  question,
                                                                  sc.SC_A_CONST,
                                                                  sc.SC_N_CONST), True, 5)
        
        if graph is None:
            return
        
        struct = sc_utils.createNodeElement(session, segment, sc.SC_CONST)
        
        graph = graph[2]
        
        sc_utils.createPairPosPerm(session, segment, struct, graph, sc.SC_CONST)
        sc_utils.createPairPosPerm(session, segment, struct,  graph_keynodes.Common.rrel_edge, sc.SC_CONST)
        sc_utils.createPairPosPerm(session, segment, struct,  graph_keynodes.Common.rrel_vertex, sc.SC_CONST)
        
        # collect verticies
        it = session.create_iterator(session.sc_constraint_new(sc_constants.CONSTR_5_f_a_a_a_f,
                                                               graph,
                                                               sc.SC_A_CONST | sc.SC_POS,
                                                               sc.SC_NODE,
                                                               sc.SC_A_CONST | sc.SC_POS,
                                                               graph_keynodes.Common.rrel_vertex), True)
        while not it.is_over():
           for i in xrange(1, 4):
               sc_utils.createPairPosPerm(session, segment, struct, it.value(i), sc.SC_CONST)
           it.next()
           
        it = session.create_iterator(session.sc_constraint_new(sc_constants.CONSTR_5_f_a_a_a_f,
                                                               graph,
                                                               sc.SC_A_CONST | sc.SC_POS,
                                                               sc.SC_NODE,
                                                               sc.SC_A_CONST | sc.SC_POS,
                                                               graph_keynodes.Common.rrel_edge), True)
        # collect edges                                          
        while not it.is_over():
            for i in xrange(1, 4):
                sc_utils.createPairPosPerm(session, segment, struct, it.value(i), sc.SC_CONST)
               
            it1 = session.create_iterator(session.sc_constraint_new(sc_constants.CONSTR_3_f_a_a,
                                                                    it.value(2),
                                                                    sc.SC_A_CONST | sc.SC_POS,
                                                                    sc.SC_NODE), True)
            while not it1.is_over():
                sc_utils.createPairPosPerm(session, segment, struct, it1.value(1), sc.SC_CONST)
                it1.next() 
                   
            it.next()
        
        sc_utils.makeAnswer(session, segment, question, struct)
        
        
def translate_value(session, _segment, _value_node, _value):
    """Setup value \p _value to \p _value_node
    @return: Return list of creates sc-elements
    """   
    v_node = sc_utils.createNodeElement(session, _segment, sc.SC_CONST)
    bin_pair = sc_utils.createPairBinaryOrientFull(session, _segment, v_node, _value_node, sc.SC_CONST)
    a = sc_utils.createPairPosPerm(session, _segment, keynodes.common.nrel_value, bin_pair[0], sc.SC_CONST)
    
    res = [v_node, a, keynodes.common.nrel_value]
    res.extend(bin_pair) 
    
    vu_node = sc_utils.createNodeElement(session, _segment, sc.SC_CONST)
    a = sc_utils.createPairPosPerm(session, _segment, v_node, vu_node, sc.SC_CONST)
    
    res.extend([vu_node, a])
    
    # make identification
    idtf_node = sc_utils.createNodeSheaf(session, _segment, sc.SC_CONST)
    bin_pair = sc_utils.createPairBinaryOrientFull(session, _segment, idtf_node, vu_node, sc.SC_CONST)
    a = sc_utils.createPairPosPerm(session, _segment, keynodes.common.nrel_identification, bin_pair[0], sc.SC_CONST)
    
    res.extend([idtf_node, a, keynodes.common.nrel_identification])
    res.extend(bin_pair)
    
    # set value
    val = sc_utils.createNodeElement(session, _segment, sc.SC_CONST)
    sc_utils.setContentReal(session, _segment, val, _value)
    a = sc_utils.createPairPosPerm(session, _segment, idtf_node, val, sc.SC_CONST)
    a1 = sc_utils.createPairPosPerm(session, _segment, keynodes.common.rrel_dec_number, a, sc.SC_CONST)
    
    res.extend([val, a, a1, keynodes.common.rrel_dec_number])
    
    return res

def calculate_graph_prop(_params, _segment):
    
    kernel = core.Kernel.getSingleton()
    session = kernel.session()
    segment = kernel.segment()
        
    # check type
    question = session.search_one_shot(session.sc_constraint_new(sc_constants.CONSTR_5_f_a_a_a_f,
                                                                 keynodes.questions.initiated,
                                                                 sc.SC_A_CONST,
                                                                 sc.SC_N_CONST,
                                                                 sc.SC_A_CONST,
                                                                 _params), True, 5)
    
    assert question is not None
    question = question[2]
    
    global graph_prop_calculators
    for question_type, calculator, relation in graph_prop_calculators:   
        # check command type
        if sc_utils.checkIncToSets(session, question, [question_type], sc.SC_CONST):
  
            graph = session.search_one_shot(session.sc_constraint_new(sc_constants.CONSTR_3_f_a_a,
                                                                      question,
                                                                      sc.SC_A_CONST,
                                                                      sc.SC_N_CONST), True, 3)
            
            if graph is None:
                return
            
            graph = graph[2]
            
            if not sc_utils.checkIncToSets(session, graph, [graph_keynodes.Common.graph], sc.SC_CONST):
                return
            
            g = Graph(segment, graph)
            g.makeNxGraph()
                        
            result = calculator(g.graphNx)
            
            if result is None:
                raise RuntimeWarning("Calculator can't calculate value")
            
            value = sc_utils.createNodeElement(session, segment, sc.SC_CONST)
            bin_rel = sc_utils.createPairBinaryOrientFull(session, segment, graph, value, sc.SC_CONST)
            a = sc_utils.createPairPosPerm(session, segment, relation, bin_rel[0], sc.SC_CONST)
            
            elements = translate_value(session, segment, value, result)
            
            elements.extend([value, graph, a, relation])
            elements.extend(bin_rel)
            
            
            answer = sc_utils.createNodeElement(session, segment, sc.SC_CONST)
            for el in elements:
                sc_utils.createPairPosPerm(session, segment, answer, el, sc.SC_CONST)
                
            sc_utils.makeAnswer(session, segment, question, answer)
            
            
def calculate_graph_element_prop(_params, _segment):
    
    kernel = core.Kernel.getSingleton()
    session = kernel.session()
    segment = kernel.segment()
        
    # check type
    question = session.search_one_shot(session.sc_constraint_new(sc_constants.CONSTR_5_f_a_a_a_f,
                                                                 keynodes.questions.initiated,
                                                                 sc.SC_A_CONST,
                                                                 sc.SC_N_CONST,
                                                                 sc.SC_A_CONST,
                                                                 _params), True, 5)
    
    assert question is not None
    question = question[2]
    
    global graph_prop_calculators
    for question_type, calculator, relation in graph_element_prop_calculators:
        # check command type
        if sc_utils.checkIncToSets(session, question, [question_type], sc.SC_CONST):
  
            element = session.search_one_shot(session.sc_constraint_new(sc_constants.CONSTR_3_f_a_a,
                                                                        question,
                                                                        sc.SC_A_CONST,
                                                                        sc.SC_N_CONST), True, 3)
            
            if element is None:
                return
            
            element = element[2]
            graph = None
            arc = None
            it = session.create_iterator(session.sc_constraint_new(sc_constants.CONSTR_3_a_a_f,
                                                                   sc.SC_NODE,
                                                                   sc.SC_A_CONST | sc.SC_POS,
                                                                   element), True)
            while not it.is_over():
                if sc_utils.checkIncToSets(session, it.value(0), [graph_keynodes.Common.graph], sc.SC_CONST):
                    graph = it.value(0)
                    arc = it.value(1)
                    break
                it.next()
                
            
            if graph is None:
                continue
            
            # make graph and calculate property value
            g = Graph(segment, graph)
            sc2obj = g.makeNxGraph()
            result = calculator(g.graphNx, sc2obj[str(element.this)])
            
            # 
            if result is None:
                raise RuntimeWarning("Calculator can't calculate value")
            
            
            value = sc_utils.createNodeElement(session, segment, sc.SC_CONST)
            bin_rel = sc_utils.createPairBinaryOrientFull(session, segment, arc, value, sc.SC_CONST)
            a = sc_utils.createPairPosPerm(session, segment, relation, bin_rel[0], sc.SC_CONST)
            
            elements = translate_value(session, segment, value, result)
            
            elements.extend([value, graph, a, relation])
            elements.extend(bin_rel)
            
            
            answer = sc_utils.createNodeElement(session, segment, sc.SC_CONST)
            for el in elements:
                sc_utils.createPairPosPerm(session, segment, answer, el, sc.SC_CONST)
                
            sc_utils.makeAnswer(session, segment, question, answer)