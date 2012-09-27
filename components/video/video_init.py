
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

import suit.core.kernel as core
import os
import video_viewer

def initialize():
    
    kernel = core.Kernel.getSingleton()
    
    from suit.core.objects import Factory
    import suit.core.keynodes as keynodes
    
    global view_factory
    
    view_factory = Factory(viewer_creator)
    kernel.registerViewerFactory(view_factory, [keynodes.ui.format_wmv,
                                                keynodes.ui.format_avi,
                                                keynodes.ui.format_mp4,
                                                keynodes.ui.format_flv,
                                                keynodes.ui.format_mpg])
    
    path = os.path.join(kernel.cache_path, 'video')
    if not os.path.isdir(path):
        os.mkdir(path)

def shutdown():
    global view_factory
    kernel = core.Kernel.getSingleton()
    kernel.unregisterViewerFactory(view_factory)
    

def _resourceLocations():
    """Specified resources for a geometry module
    """
    res = []
    path = os.path.join(core.Kernel.getSingleton().cache_path, 'video')
    res.append((path, "FileSystem", 'video'))
    return res

def getResourceLocation():
    """Return resource location folder
    """
    return os.path.join(core.Kernel.getSingleton().cache_path, 'video') 

def getResourceGroup():
    """Return resource group name
    """
    return video

def viewer_creator():
    return video_viewer.VideoViewer() 