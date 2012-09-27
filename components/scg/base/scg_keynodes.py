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
Created on 18.10.2009

@author: Denis Koronchik
'''

import srs_engine.core as core
session = core.Kernel.session()

session.open_segment(u"/ui/menu")
 
# scg segments
class segments:
    alphabet        =   u"/ui/scg_alphabet"
    proc_keynode    =   u"/proc/keynode"
    scg_menu        =   u"/ui/scg/menu"
            
            
#class core:
#    parts           =   session.find_keynode_full_uri("/ui/core/parts")
            
# menu keynodes
class menu:
    root            =   session.find_keynode_full_uri(u"/ui/menu/main menu")
    
    
