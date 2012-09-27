
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



from converter import Converter
import defines
from subprocess import Popen, PIPE
import myutil
import sys
import os.path

class ScsConverter(Converter):

    def type(self, filePath):
        return myutil.fileType(filePath, "scs")

    def runConvertation(self, pathSrc, pathBin):
        myutil.createDirs(pathBin)

        cmd = "%s -nc -I\"%s\" -I\"%s\" \"%s\" \"%s\"" % (defines.SCS2TGF, defines.INCLUDES, os.path.dirname(pathSrc), \
                                                                                                          pathSrc, \
                                                                                                          pathBin)
        process = Popen(cmd, stdout=PIPE, stderr=PIPE)
        process.stdout.close()
        process.wait()

        try:
            if process.returncode == 0:
                return True
            else:
                myutil.printPipe(sys.stderr, process.stderr)
                return False
        finally:
            process.stderr.close()
