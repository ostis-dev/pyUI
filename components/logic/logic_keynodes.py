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

from suit.core.keynodes import *


class Objects:
    true       =   session.find_keynode_full_uri(u"/seb/logic/истина")
    false =   session.find_keynode_full_uri(u"/seb/logic/ложь")

class Relation:
    nrel_negation   =   session.find_keynode_full_uri(u"/seb/logic/отрицание*")
    nrel_conjunction   =   session.find_keynode_full_uri(u"/seb/logic/конъюнкция*")
    nrel_equivalence   =   session.find_keynode_full_uri(u"/seb/logic/эквиваленция*")
    nrel_implication   =   session.find_keynode_full_uri(u"/seb/logic/импликация*")
    nrel_disjunction   =   session.find_keynode_full_uri(u"/seb/logic/дизъюнкция*")

    rrel_if            =   session.find_keynode_full_uri(u"/seb/logic/если_")
    rrel_then            =   session.find_keynode_full_uri(u"/seb/logic/то_")