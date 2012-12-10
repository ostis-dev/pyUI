
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
Created on xx.xx.2012

@author: Dred
'''

"""sc -> scs translator component
"""

from suit.core.objects import Translator
import suit.core.objects as objects
import suit.core.kernel as core
import sc_core.pm as sc
import sc_core.constants as sc_constants
import suit.core.keynodes as keynodes
import suit.core.sc_utils as sc_utils
'''import scg_alphabet
import scg_objects'''
import suit.core.exceptions as exceptions

session = core.Kernel.session()

def getConstStr(_type):
    _const = None
    sc.SC
    if _type & sc.SC_CONST:
        _const = "const"
    elif _type & sc.SC_VAR:
        _const = "var"
    elif _type & sc.SC_A_METAVAR:
        _const = "meta"
    else:
        _const = "-"
    return _const

class TranslatorSc2Scs(Translator):
    '''Class for translating from SC into SCS'''
    def __init__(self):
        Translator.__init__(self)

    def __del__(self):
        Translator.__del__(self)

    def translate_impl(self, _input = None, _output = None):
        """Translator implementation
        @param _input:    input data set
        @type _input:    sc_global_addr
        @param _output:    output window (must be created)
        @type _output:    sc_global_addr

        @return: list of errors each element of list is a tuple(object, error)
        @rtype: list
        """
        errors = []
        objs = objects.ScObject._sc2Objects(_output)

        assert len(objs) > 0
        sheet = objs[0]
        assert type(sheet) is objects.ObjectSheet

        session = core.Kernel.session()

        trans_objs = []
        result_objs = []

        # creating list of element to translate
        it = session.create_iterator(session.sc_constraint_new(sc_constants.CONSTR_3_f_a_a,
                                                               _input,
                                                               sc.SC_A_CONST | sc.SC_POS,
                                                               0), True)
        list_of_addrs = []
        while not it.is_over():
            trans_objs.append(it.value(2))
            list_of_addrs.append(str(it.value(2).this))
            it.next()

        # getting objects on sheet
        childs = sheet.getChilds()
        sc_scs = {}
        object_types = {}
        for obj in childs:
            addr = obj._getScAddr()
            if addr is not None:
                s_addr = str(addr.this)
                sc_scs[s_addr] = obj
                object_types[s_addr] = session.get_type(addr)
                list_of_addrs.append(s_addr)

        ignore_list = []
        process_pairs = []