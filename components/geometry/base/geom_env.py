
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
Created on 17.12.2009

@author: Denis Koronchick
'''
import os
import suit.core.kernel as core

# resources
resource_group      =   'geometry'
resource_dir        =   os.path.join(os.path.dirname(__file__), "media")

res_mesh_dir        =   os.path.join(resource_dir, 'meshes')
res_mat_dir         =   os.path.join(resource_dir, 'materials')
res_mat_programs_dir  =   os.path.join(res_mat_dir, 'programs')
res_mat_script_dir  =   os.path.join(res_mat_dir, 'scripts')
res_mat_texture_dir =   os.path.join(res_mat_dir, 'textures')
res_gui_dir         =   os.path.join(resource_dir, 'gui')

# list of resource directories
resource_dirs = [res_mesh_dir, res_mat_dir, res_mat_programs_dir,
                 res_mat_script_dir, res_mat_texture_dir]

# meshes
mesh_point = "geom_point.mesh"
mesh_lsect = "geom_line_seg.mesh"

# materials
material_grid = "geometry_back_grid"

material_state_pat = "geometry_%s"

# segment for searching
search_segments     =   ["/seb/planimetry"]

########################
# Gui Configuration
########################
gui_skin_panel  =   'geom_panel_skin.xml'
gui_language    =   os.path.join(res_gui_dir, 'geom_ru.cfg')
gui_lang_section    =   "geometry"