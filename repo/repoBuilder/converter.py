
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


import myutil
from abc import ABCMeta
from abc import abstractproperty
from abc import abstractmethod

class Converter:
    __metaclass__ = ABCMeta

    @abstractmethod
    def type(self):
        pass

    @abstractmethod
    def runConvertation(self, pathSrc, pathBin):
        pass

    def convert(self, pathSrc):
        if not self.type(pathSrc):
            raise UserWarning, "BAD PARSER. Can't convert file:" + pathSrc
        pathBin = myutil.convertToPathBin(pathSrc, pathSrc.split(".")[-1])
        return self.runConvertation(pathSrc, pathBin)

class SkipConverter(Converter):

    def __init__(self):
        self.skip = ["gwf", "m4", "scsy"]

    def type(self, filePath):
        for e in self.skip:
            if myutil.fileType(filePath, e):
                return True

    def runConvertation(self, pathSrc, pathBin):
        return True
