
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
Created on 15.11.2009

@author: Denis Koronchik
'''
import os

PATH_dir            = os.path.abspath("./") 

PATH_external       = os.path.join(PATH_dir, "external")
PATH_components     = os.path.join(PATH_dir, "components")
PATH_tests          = os.path.join(PATH_dir, "tests")
PATH_operations     = os.path.join(PATH_dir, "operations")
PATH_screens        = os.path.join(PATH_dir, "screens")
PATH_media          = os.path.join(PATH_dir, "media")
PATH_langs          = os.path.join(PATH_media, "langs")

GUI_resource_group  =   "General"

URI_ui_core         = "/ui/core"

# list of extension modules
oper_modules = [("core_op", PATH_operations),
                ]
ext_modules = []

# node for content showing
cont_min_node = ["scg_node_const.mesh", "scg_struct_abstract_const.mesh", "scg_cont_cube.mesh"]
cont_min_node_quet = "scg_cont_unknown.mesh"