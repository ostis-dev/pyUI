# -*- coding: utf-8 -*-
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
Created on 
2010
@author:  Zhitko V.A.
'''

import suit.core.kernel as core
session = core.Kernel.session()

rel_runing_condition    =   session.find_keynode_full_uri(u"/etc/operations/условие выполнения*")
sc_operations   =   session.find_keynode_full_uri(u"/etc/operations/операция")

seg_system = [
              u"/etc/operations",
              u"/etc/questions",
              u"/ui/menu"
              ]