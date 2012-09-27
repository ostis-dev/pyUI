#! /usr/bin/env python
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

import os
import os.path
from subprocess import Popen
from subprocess import PIPE
import sys

import myutil
import defines
from m4scp_converter import M4ScpConverter
from scs_converter import ScsConverter
from scg_converter import ScgConverter
from converter import SkipConverter

class Builder:
    """General class
    Class contein all objects of converters
    Class parse all files and run current converter
    """
    
    def _init_builder(self, fs_repo_src):
        defines.PATH_REPO_SRC = fs_repo_src
        # If repository src path ends with '_src' then just remove '_src' for bin path
        # else add '_bin'
        if len(fs_repo_src) > 4 and fs_repo_src.endswith("_src"):
            defines.PATH_REPO_BIN = fs_repo_src[:len(fs_repo_src) - 4]
        else:
            defines.PATH_REPO_BIN = fs_repo_src + "_bin"

        # Search sc-core module home and get paths for needed utils
        sc_core_home = os.environ.get('SC_CORE_HOME')
        if sc_core_home:
            def check_dir(path):
                if not os.path.isdir(path):
                    print "Not found '%s' for enviroment var SC_CORE_HOME" % (path)
                    sys.exit(3)
                return path

            bin = check_dir(os.path.join(sc_core_home, "bin"))
            share_dir = check_dir(os.path.join(sc_core_home, "share", "sc-core"))

            def check_file(path):
                if not os.path.isfile(path):
                    print "Not found '%s' for enviroment var SC_CORE_HOME" % (path)
                    sys.exit(4)
                return path

            defines.SCS2TGF = check_file(os.path.join(bin, "scs2tgf.exe"))
            defines.M4 = check_file(os.path.join(bin, "m4.exe"))
            defines.M4SCP = check_file(os.path.join(share_dir, "m4scp.m4"))

            defines.INCLUDES = os.path.join(defines.PATH_REPO_SRC, "include")
        else:
            def check_file(path):
                if not os.path.isfile(path):
                    print "Not found '%s'" % (path)
                    sys.exit(4)
            check_file(defines.SCS2TGF)
            check_file(defines.M4)
            check_file(defines.M4SCP)
    
    def __init__(self):
        self.converters = [ScsConverter(), M4ScpConverter(), ScgConverter(), SkipConverter()]
        self.errors = 0

    def run(self, fs_repo_src=None):
        if fs_repo_src is None:
            fs_repo_src = defines.PATH_REPO_SRC
        self._init_builder(fs_repo_src)
        myutil.cleanDir(defines.PATH_REPO_BIN)
        self.scan(fs_repo_src)
        os.mkdir(defines.PATH_REPO_BIN + "/tmp")
        os.mkdir(defines.PATH_REPO_BIN + "/proc")
        self.createMetaFiles(defines.PATH_REPO_BIN)
        sys.stderr.flush()
        print "Find", self.errors, "errors"

    def scan(self, path):
        """find current files and run converters"""
        if os.path.isfile(path):
            converter = self.defineConverter(path)
            if not converter is None:
                if not converter.convert(path):
                    self.errors = self.errors + 1
            else:
                print >> sys.stderr, "Not handled", path
        elif os.path.isdir(path) and path != defines.INCLUDES and (os.path.basename(path).startswith(".") is False):
            listDirs = os.listdir(path)
            for i in listDirs:
                self.scan(path + "/" + i)

    def defineConverter(self, filePath):
        """Return instance of converter"""
        for c in self.converters:
            if c.type(filePath):
                return c

    def createMetaFiles(self, dir):
        """Create META File in directory"""
        listDirs = os.listdir(dir)
        metaStr = self.collectMeta(listDirs)
        pathBin = dir + "/" + defines.META
        cmdScs = "%s -nc - %s" % (defines.SCS2TGF, pathBin)
        process = Popen(cmdScs, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        process.stdin.write(metaStr)
        process.stdin.close()
        process.wait()
        for i in listDirs:
            path = dir + "/" + i
            if os.path.isdir(path):
                self.createMetaFiles(path)

    def collectMeta(self, listDirs):
        """Return str of META"""
        if defines.META not in listDirs:
            listDirs.insert(0, defines.META)
        else:
            myutil.showWarning("META file is exists and has been rewrited")
        meta = ""
        meta = meta + ('\"/info/dirent\" = {\n')
        meta = meta + ('\t"' + listDirs[0] + '\"={}')
        for i in listDirs[1:]:
            meta = meta + (',\n\t\"' + i + '\"={}')
        meta = meta + ('\n};\n')
        return meta

if __name__ == "__main__":
    if len(sys.argv) == 2:
        fs_repo_src = sys.argv[1]
    else:
        fs_repo_src = defines.PATH_REPO_SRC

    if not os.path.isdir(fs_repo_src):
        print "'%s' isn't source repository directory" % (fs_repo_src)
        sys.exit(2)

    builder = Builder()
    builder.run(fs_repo_src)
