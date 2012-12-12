
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
Created on 21.04.2011

@author: Denis Koronchik
'''

_version_   =   "0.1.0"
_name_      =   "Math-interface"

import suit.core.kernel as core
import math2sc
import os


def initialize():
    kernel = core.Kernel.getSingleton()
    import suit.core.keynodes as keyn
    from suit.core.objects import Factory

    global transmath2sc_factory

    transmath2sc_factory = Factory(mathToSCCreator)
    kernel.registerTranslatorFactory(transmath2sc_factory, [keyn.ui.format_mathML], [keyn.ui.format_sc])


def shutdown():
    global transmath2sc_factory
    # unregister components
    kernel = core.Kernel.getSingleton()
    kernel.unregisterTranslatorFactory(transmath2sc_factory)

    
def _resourceLocations():
    """Specified resources for a math module
    """
    res = []

    return res

def mathToSCCreator():
    return math2sc.TranslatorMath2Sc