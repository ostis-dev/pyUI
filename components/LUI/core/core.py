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

import parser
from LSPL_parser import LsplParser
from looser_parser import LooserParser

#parsers = [LooserParser, LsplParser]
parsers = [LooserParser]

class Core:
    def __init__(self):
        self.tasks = []
    
    def parse(self, nl_q):
        self.tasks.append(nl_q)
        if len(self.tasks) == 1:
            self.start_parsers()
            
                
    def start_parsers(self):
        if len(self.tasks) != 0:
            nl_q = self.tasks[0]
            self.tasks.remove(nl_q)
            self.parsers = []
            for parser in parsers:
                t_parser = parser()
                self.parsers.append(t_parser)
                t_parser.start_process(nl_q, self.stop_others)
            
    def stop_others(self):
        print "STOP OTHERS LOOSERS"
        for parser in self.parsers:
            parser.isRun = False
            self.start_parsers()