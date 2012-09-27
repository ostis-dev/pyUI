
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
Created on 01.10.2009

@author: Denis Koronchik
'''

revision = "$Revision$"

class Version:
    
    def __init__(self, major, minor, patch):
        self.value = (major << 24) + (minor << 16) + patch

    def getMajor(self):
        return (self.value & 0xFF000000) >> 24
    
    def getMinor(self):
        return (self.value & 0x00FF0000) >> 16
    
    def getPatch(self):
        return (self.value & 0x0000FFFF) 
    
    def getRevision(self):
        return revision
    
    def __str__(self):
        return "%d.%d.%d" % (self.getMajor(), self.getMinor(), self.getPatch())
    
    def getPoorVersion(self):
        """Returns version without patch
        """
        return self.value & 0xFFFF0000
    
    # operator <
    def __lt__(self, other):
         return self.getPoorVersion() < other.getPoorVersion()
     
    # operator >
    def __gt__(self, other):
        return other < self
    
    # operator <=
    def __le__(self, other):
        return not (self > other)
    
    # operator >=
    def __ge__(self, other):
        return not (self < other)
    
    # operator ==
    def __eq__(self, other):
        return self.getPoorVersion() == other.getPoorVersion()
    
    # operator !=
    def __ne__(self, other):
        return not (self == other)
         
version = Version(0, 4, 0)        