
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

import suit.core.kernel as core
import map2sc
import map_viewer
import map_environment

def initialize():
    kernel = core.Kernel.getSingleton()
    
    from siut.core.objects import Factory
    import suit.core.keynodes as keynodes

    
    global view_factory
    global transmap2sc_factory
    
    view_factory = Factory(viewer_creator)
    transmap2sc_factory = Factory(map2sc_creator)
    kernel.registerViewerFactory(view_factory, [keynodes.ui.format_midmif])
    kernel.registerTranslatorFactory(transmap2sc_factory, [keynodes.ui.format_midmif], [keynodes.ui.format_sc])
    


def shutdown():
    
    global view_factory
    global transmap2sc_factory
    
    kernel = core.Kernel.getSingleton()
    kernel.unregisterViewerFactory(view_factory)
    kernel.unregisterTranslatorFactory(transmap2sc_factory)


def viewer_creator():
    return map_viewer.MapViewer() 

def map2sc_creator():
    return map2sc.TranslatorMap2Sc()
