
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
Created on 11.02.2010

@author: Denis Koronchik
'''
import os
import suit.core.kernel as core

resource_group      =   'map'
resource_dir        =   os.path.join(os.path.dirname(__file__), "media")

res_tmp_dir        =   os.path.join(resource_dir, 'tmp')

resource_dirs       =   [res_tmp_dir]

segment_root        =   "/seb/map"

search_segments     =   [segment_root]