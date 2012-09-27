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
Created on 02.02.2010

@author: Denis Koronchik
'''

from suit.core.keynodes import * 

class Objects:
    
    point       =   session.find_keynode_full_uri(u"/seb/planimetry/точка")
    line_sector =   session.find_keynode_full_uri(u"/seb/planimetry/отрезок")
    circle      =   session.find_keynode_full_uri(u"/seb/planimetry/окружность")
    plane_triangle      =   session.find_keynode_full_uri(u"/seb/planimetry/треугольник")
    plane_quadrangle    =   session.find_keynode_full_uri(u"/seb/planimetry/четырехугольник")
    angle       =   session.find_keynode_full_uri(u"/seb/planimetry/угол")
    
class Relation:
    nrel_border_point   =   session.find_keynode_full_uri(u"/seb/planimetry/граничная точка*") 
    nrel_center         =   session.find_keynode_full_uri(u"/seb/planimetry/центр*")
    nrel_side           =   session.find_keynode_full_uri(u"/seb/planimetry/сторона*")
    nrel_length         =   session.find_keynode_full_uri(u"/seb/planimetry/длина*")
    nrel_square         =   session.find_keynode_full_uri(u"/seb/planimetry/площадь*")
    nrel_perimeter      =   session.find_keynode_full_uri(u"/seb/planimetry/периметр*")
    nrel_congr          =   session.find_keynode_full_uri(u"/seb/planimetry/конгруэнтность*")
    nrel_radius         =   session.find_keynode_full_uri(u"/seb/planimetry/радиус*")
    
    rrel_cm             =   session.find_keynode_full_uri(u"/seb/planimetry/см_")
    rrel_cm2            =   session.find_keynode_full_uri(u"/seb/planimetry/см2_")
