
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

import suit.core.kernel as core
session = core.Kernel.session()

session.open_segment(u"/seb/chemistry")

format = session.find_keynode_full_uri(u"/ui/core/CHEMISTRY")

atom_H = session.find_keynode_full_uri(u"/seb/chemistry/атом водорода")
atom_O = session.find_keynode_full_uri(u"/seb/chemistry/атом кислорода")
atom_C = session.find_keynode_full_uri(u"/seb/chemistry/атом углерода")
atom_N = session.find_keynode_full_uri(u"/seb/chemistry/атом азота")
link = session.find_keynode_full_uri(u"/seb/chemistry/химическая связь")
linked_atom = session.find_keynode_full_uri(u"/seb/chemistry/связываемый атом*")
