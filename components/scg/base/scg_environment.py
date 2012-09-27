
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
Created on 06.10.2009

@author: Denis Koronchik
'''

"""
"""
import os
import suit.core.kernel as core

resource_group      =   'scg'
resource_dir        =   os.path.join(os.path.dirname(__file__), "media")

res_code_dir        =   os.path.join(resource_dir, 'code')
res_tex_dir         =   os.path.join(resource_dir, 'textures')
res_mat_dir         =   os.path.join(resource_dir, 'materials')

resource_dirs       =   [res_code_dir, res_tex_dir, res_mat_dir]

res_vismenu_dir     =   os.path.join(resource_dir, "vis_menu")

vis_menu_tex_name   =   "scg_vis_menu.png"
vis_menu_resources  =   "visual_menu_resources.xml"
vis_menu_item_size  =   (34, 34)


search_segments     =   ["/ui/core",
                         "/seb/belarus",
                         "/seb/planimetry",
                         "/seb/graph",
                         "/seb/rus",
                         "/etc/questions",
                         "/etc/com_keynodes",
                         "/seb/test",
                         "/proc/agents/nsm/keynode"]