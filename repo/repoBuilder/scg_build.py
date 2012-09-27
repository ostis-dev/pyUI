
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
import shutil
import sys


# configure encoding
import locale as lc
import codecs
lc.setlocale(lc.LC_ALL, ('English_United States', '1251'))
encoding = lc.getlocale()[1]
if not encoding:
    encoding = "utf-8"
reload(sys)
sys.setdefaultencoding(encoding)
sys.stdout = codecs.getwriter(encoding)(sys.stdout, errors = "replace")
sys.stderr = codecs.getwriter(encoding)(sys.stderr, errors = "replace")


def generate_scg(file_name, path):

    print "Generating scg file '%s' from '%s'" % (file_name, path)

    out_file = open(file_name, "w")
    for inc in includes:
        out_file.write('#include "%s"\n' % inc)


    for root, dirs, files in os.walk(path):

        print "scanning %s" % (os.path.join(root))

        for file in files:
            if file.endswith(".gwf"):
                #print file_name + " -> " +root
                fin = os.path.join(os.path.relpath(root, os.path.dirname(file_name)), file)
                print "adding file %s" % (fin)
                out_file.write(fin + "\n")
            elif file.endswith(".scsy"):
                fin = os.path.join(os.path.relpath(root, os.path.dirname(file_name)), file)
                print "adding file %s" % (fin)
                out_file.write('#include "%s"\n' % fin)
            else:
                print "ignored %s in %s" % (file, path)

    out_file.write('\n')
    out_file.close()

#  make includes as params
includes = ["ordinal.scsy", "meta_info.scsy", "ui_keynodes.scsy"]

if __name__ == "__main__":

    if len(sys.argv) < 3:
        print "scg_build.py <source_dir> <scg_file>"
        exit(0)

    output = os.path.abspath(sys.argv[2])
    srcDir = os.path.abspath(sys.argv[1])

    generate_scg(output, srcDir)
