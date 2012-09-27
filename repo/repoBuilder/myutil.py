
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
import warnings
import shutil
import string

import defines

def printPipe(out, pipe):
    for line in pipe.readlines():
        print >> out, string.strip(line)
    out.flush()

def fileType(fileName, type):
    """Return true if fileName have extension type"""
    ext = fileName.split(".")[-1]
    if ext == type:
        return True
    else:
        return False

def convertToPathBin(pathSrc, type):
    """Convert
    from    fs_repo_src/.../file.ext
    to              fs_repo/.../file
    """
    lenRepoSrc = len(defines.PATH_REPO_SRC) + 1
    lenType = len(type) + 1
    pathBin = defines.PATH_REPO_BIN + "/" + pathSrc[lenRepoSrc:-lenType]
    return pathBin

def getTree(pathBin):
    """Return tree dirs of file without filename
    WARNING: all separators ("\" or "/") replace to "/"
    It is func was created specialty for shutil.os.makedirs which don't work whith "\"-separators
    """
    backSlash = "\\"
    rightSlash = "/"

    if os.path.isdir(pathBin):
        pathBin = pathBin.replace(backSlash, rightSlash)
        return pathBin

    indexBackSlash = pathBin.rfind(backSlash)
    indexRightSlash = pathBin.rfind(rightSlash)
    if indexBackSlash > indexRightSlash:
        separator = backSlash
    else:
        separator = rightSlash

    arrayDirs = pathBin.split(separator)[:-1]
    strDirs = rightSlash.join(arrayDirs)
    strDirs = strDirs.replace(backSlash, rightSlash)
    return strDirs

def createDirs(path):
    """Create dirs tree"""
    if not os.path.exists(path) and os.path.isdir(path):
        os.mkdir(path)
        return True

    pathTree = getTree(path)
    if len(pathTree) != 0 and not os.path.exists(pathTree):
        shutil.os.makedirs(pathTree)
        return True
    return False

def cleanDir(directory):
    """delete all files from directory"""
    # TODO: try: ... except: ...
    if os.path.exists(directory):
        shutil.rmtree(directory, True, True)
    createDirs(directory)

def showWarning(message):
    msg = "!!! WARNING: " + message
    warnings.warn(msg)
