
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
Created on 20.01.2010

@author: Maxim Kaskevich
'''


import os
import suit.core.kernel as core

# resources
resource_group      =   'space'
resource_dir        =   os.path.join(os.path.dirname(__file__), "media")

res_mesh_dir        =   os.path.join(resource_dir, 'meshes')
res_mat_dir         =   os.path.join(resource_dir, 'materials')
res_mat_script_dir  =   os.path.join(res_mat_dir, 'scripts')
res_mat_texture_dir =   os.path.join(res_mat_dir, 'textures')
res_gui_dir         =   os.path.join(resource_dir, 'gui')

#sc memory segments
segment_root        =   "/seb/space"
#segment_keynodes    =   u"/seb/space_keynodes"
search_segments     =   [segment_root]

# list of resource directories
resource_dirs = [res_mesh_dir, res_mat_dir,res_mat_script_dir, 
                 res_mat_texture_dir]

# meshes

# materials

#GUI directories
gui_skin_panel  =   'space_panel_skin.xml'
