
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

from subprocess import Popen, PIPE

import myutil
import defines
from converter import Converter
import os.path
import sys

class M4ScpConverter(Converter):

    def type(self, filePath):
        return myutil.fileType(filePath, "m4scp")

    def runConvertation(self, pathSrc, pathBin):
        myutil.createDirs(pathBin)
        pathSrcDir = os.path.dirname(pathSrc)

        cmdM4 = "%s -I\"%s\" \"%s\" \"%s\"" % (defines.M4, pathSrcDir, defines.M4SCP, pathSrc)
        processM4 = Popen(cmdM4, stdout=PIPE, stderr=PIPE)

        cmdScs = "%s -nc -I\"%s\" -I\"%s\" - \"%s\"" % (defines.SCS2TGF, defines.INCLUDES, os.path.dirname(pathSrc), pathBin)
        processScs = Popen(cmdScs, stdin=processM4.stdout, stdout=PIPE, stderr=PIPE)
        processScs.wait()

        processM4.stderr.close()
        processScs.stdout.close()

        try:
            if processScs.returncode == 0:
                return True
            else:
                print >> sys.stderr, "In file %s:" % (pathSrc)
                myutil.printPipe(sys.stderr, processScs.stderr)
                return False
        finally:
            processScs.stderr.close()
