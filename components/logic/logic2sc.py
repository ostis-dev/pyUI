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
import antlr3
from components.geometry.base.geom2sc import _resolve_sc_addr

from suit.core.objects import Translator
import suit.core.objects as objects
import suit.core.kernel as core
import sc_core.pm as sc

import suit.core.sc_utils as sc_utils

from logic_gramLexer import logic_gramLexer as Lexer
from logic_gramParser import logic_gramParser as Parser

class TranslatorLogic2Sc(Translator):

    def __init__(self):
        Translator.__init__(self)

    def __del__(self):
        Translator.__del__(self)

    def translate_impl(self, _input, _output):

        """Translator implementation
        """
        # translating objects
        objs = objects.ScObject._sc2Objects(_input)

        assert len(objs) > 0
        sheet = objs[0]
        assert type(sheet) is objects.ObjectSheet

        segment = sheet.getTmpSegment()

        errors = []
        session = core.Kernel.session()

        # getting objects, that need to be translated
        trans_obj = []
        for obj in sheet.getChilds():
            _addr = obj._getScAddr()
            if _addr is None:
                trans_obj.append(obj)
                # remove old translation data
            else:
                if _addr.seg == segment:
                    obj._setScAddr(None)
                    session.erase_el(_addr)


        # resolve sc_addrs
        for obj in trans_obj:
            _resolve_sc_addr(segment, obj)

        # make translation
        for obj in trans_obj:
            errors = []
            char_stream = antlr3.ANTLRStringStream(obj)
            lexer = Lexer(char_stream)
            parser = Parser(antlr3.CommonTokenStream(lexer))
            parser.formula()
            kernel = core.Kernel.getSingleton()
            session = kernel.session()
            segment = kernel.segment()
            for node in parser.nodeList:
                sc_utils.createPairPosPerm(session, segment,_output,node , sc.SC_CONST)
        return errors
