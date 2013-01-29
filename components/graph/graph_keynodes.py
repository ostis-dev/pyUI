
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
Created on 20.05.2012

@author: Denis Koronchick
'''
import graph_env as env
from suit.core.keynodes import *

#session.open_segment(env.segment_path)

class Common:

    graph               =   session.find_keynode_full_uri(u"/seb/graph/граф")

    rrel_vertex         =   session.find_keynode_full_uri(u"/seb/graph/вершина_")
    rrel_edge           =   session.find_keynode_full_uri(u"/seb/graph/ребро_")
    
    nrel_diameter       =   session.find_keynode_full_uri(u"/seb/graph/диаметр графа*")
    nrel_radius         =   session.find_keynode_full_uri(u"/seb/graph/радиус графа*")
    nrel_connected_components_num   =   session.find_keynode_full_uri(u"/seb/graph/количество связанных вершин*")
    
    nrel_vertex_degree  =   session.find_keynode_full_uri(u"/seb/graph/степень вершины*")
    
class Command:
    generate_any_graph  =   session.find_keynode_full_uri(u"/seb/graph/generate_any_graph")
    generate_regular_graph  =   session.find_keynode_full_uri(u"/seb/graph/generate_regular_graph")
    generate_cycle_graph    =   session.find_keynode_full_uri(u"/seb/graph/generate_cycle_graph")
    generate_cubic_graph    =   session.find_keynode_full_uri(u"/seb/graph/generate_cubic_graph")
    
    search_graph_full       =   session.find_keynode_full_uri(u"/seb/graph/search_graph_full")
    
    calculate_graph_diameter    =   session.find_keynode_full_uri(u"/seb/graph/calculate_graph_diameter")
    calculate_graph_radius    =   session.find_keynode_full_uri(u"/seb/graph/calculate_graph_radius")
    calculate_graph_connected_components = session.find_keynode_full_uri(u"/seb/graph/calculate_graph_connected_components")
    
    
    calculate_graph_vertex_degree   =   session.find_keynode_full_uri(u"/seb/graph/calculate_graph_vertex_degree")
    