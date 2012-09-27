
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
Created on 13.01.2010

@author: Maxim Kaskevich
'''

import os 
import flash_viewer
import suit.core.kernel as core
import suit.core.render.hikari as hikari
import flash_env as env

def initialize():
    
    # initialize hikari engine
    initHikari()
    
    kernel = core.Kernel.getSingleton()
    
    from suit.core.objects import Factory
    import suit.core.keynodes as keynodes
    
    global view_factory
    
    view_factory = Factory(viewer_creator)
    kernel.registerViewerFactory(view_factory, [keynodes.ui.format_swf])
    
    path = os.path.join(kernel.cache_path, 'flash')
    if not os.path.isdir(path):
        os.mkdir(path)

def shutdown():
    global view_factory
    kernel = core.Kernel.getSingleton()
    kernel.unregisterViewerFactory(view_factory)
    
    # deinitialize hikari engine
    deinitHikari()

def _resourceLocations():
    """Specified resources for a geometry module
    """
    res = []
    path = os.path.join(core.Kernel.getSingleton().cache_path, 'flash')
    res.append((path, "FileSystem", 'flash'))
    return res

def initHikari():
    env.hikariMgr = hikari.HikariManager(os.path.relpath(os.path.join(core.Kernel.getSingleton().cache_path, 'flash'), ""))#flash_init.getResourceLocation()+env.res_flashes)
    env.hikariMgr.setKeyboardHookEnabled(False)
    pass
    
def deinitHikari():
    env.hikariMgr = None
    pass

def viewer_creator():
    return flash_viewer.FlashViewer()