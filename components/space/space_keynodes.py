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
from lib2to3.pgen2.token import STAR


'''
Created on 09.04.2010

@author: Kate Romanenko
'''

import suit.core.kernel as core
import space_env as env

session = core.Kernel.session()
seg_root = session.open_segment(env.segment_root)

        
class SpaceRelation:
    radius             =   session.find_keynode_full_uri(u"/seb/space/средний радиус*")
    turn_around     	=   session.find_keynode_full_uri(u"/seb/space/вращаться вокруг*")
    orbital_eccentr    =   session.find_keynode_full_uri(u"/seb/space/орбитальный эксцентриситет*")
    aphelion    		=   session.find_keynode_full_uri(u"/seb/space/афелий*")
    perihelion     	=   session.find_keynode_full_uri(u"/seb/space/перигелий*")
    big_axle     		=   session.find_keynode_full_uri(u"/seb/space/большая полуось*")
    sidereal_period    =   session.find_keynode_full_uri(u"/seb/space/сидерический период*")
    orbital_speed     	=   session.find_keynode_full_uri(u"/seb/space/орбитальная скорость*")
    inclination     	=   session.find_keynode_full_uri(u"/seb/space/наклонение*")
    long_ascend_node   =   session.find_keynode_full_uri(u"/seb/space/долгота восходящего узла*")
    pericentre_arg    	=   session.find_keynode_full_uri(u"/seb/space/аргумент перицентра*")
    satellite_amount   =   session.find_keynode_full_uri(u"/seb/space/число спутников*")
    pressure    		=   session.find_keynode_full_uri(u"/seb/space/сжатие*")
    synodic_period    	=   session.find_keynode_full_uri(u"/seb/space/синодический период*")
    surface_area		=   session.find_keynode_full_uri(u"/seb/space/площадь поверхности*")
    capacity			=   session.find_keynode_full_uri(u"/seb/space/объём*")

    mass    	=   session.find_keynode_full_uri(u"/seb/space/масса*")
    average_density		=   session.find_keynode_full_uri(u"/seb/space/средняя плотность*")
    period_of_revol			=   session.find_keynode_full_uri(u"/seb/space/период вращения*")
    grav_acceleration    	=   session.find_keynode_full_uri(u"/seb/space/ускорение свободного падения на экваторе*")
    surface_area		=   session.find_keynode_full_uri(u"/seb/space/вторая космическая скорость*")
    axial_pitch			=   session.find_keynode_full_uri(u"/seb/space/наклон оси вращения*")
    albedo			=   session.find_keynode_full_uri(u"/seb/space/альбедо*")
    chemistry    =   session.find_keynode_full_uri(u"/seb/space/химический состав*")
    atmosphere            =   session.find_keynode_full_uri(u"/seb/space/атмосфера*")
    star   =   session.find_keynode_full_uri(u"/seb/space/звезда")
    planet            =   session.find_keynode_full_uri(u"/seb/space/планета")

#class DefaultKeynode:
#    english = session.find_keynode_full_uri(u"/seb/space/англоязычный терм")
#    russian = session.find_keynode_full_uri(u"/seb/space/русскоязычный терм")
#    
#  
class DefaultAttr:
    unit_kilometre = session.find_keynode_full_uri(u"/seb/space/км_")
    unit_day = session.find_keynode_full_uri(u"/seb/space/день_")
    dec_system = session.find_keynode_full_uri(u"/seb/space/представление в десятичной системе счисления_")    
#  
#class DefaultRelation:
#    identification     =   session.find_keynode_full_uri(u"/seb/planimetry/идентификация*")
#    synonym     =   session.find_keynode_full_uri(u"/seb/planimetry/синонимы*")
#         