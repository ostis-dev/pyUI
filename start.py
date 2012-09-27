
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
Created on 29.08.2010

@author: Denis Koronchik
'''

import sys
import os.path
import suit.core.kernel
import traceback
import components
import operations

import codecs
import locale as lc
lc.setlocale(lc.LC_ALL, ('English_United States', '1251'))
encoding = lc.getlocale()[1]
if not encoding:
    encoding = "utf-8"
    
reload(sys)
sys.setdefaultencoding(encoding)
sys.stdout = codecs.getwriter(encoding)(sys.stdout, errors = "replace")
sys.stderr = codecs.getwriter(encoding)(sys.stderr, errors = "replace")

if (__name__ == "__main__"):
    
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option("--fsrepo", dest = "fsrepo",
                      help = "use specified repository for system starting",
                      metavar = "FSREPO", default = 'repo/fs_repo')
    parser.add_option("--rbuild", dest = "rbuild",
                      help = "rebuild repository on system start (yes/no)",
                      metavar = "RBUILD", default = 'no')
    parser.add_option("--rules", dest = "rules",
                      help = "rules file name",
                      metavar = "RULES", default = 'build.rules')
    (options, args) = parser.parse_args()

    if options.rbuild == "yes":
        
        sys.path.append('repo')
        import rule_builder
        
        rule_builder.build(options.rules)
        
        sys.path.remove('repo')

    kernel = suit.core.kernel.Kernel()
    # make modeules list
    modules = []
    for _mod in operations.modules:
        modules.append('operations.' + _mod)
    for _mod in components.modules:
        modules.append('components.' + _mod)
    try:
        print os.path.split(sys.argv[0])[0]
        kernel.initialize("srs.log",
							repo_path = options.fsrepo,
							resource_cfg = 'resources.cfg',
							modules = modules,
                            exec_path = os.path.split(sys.argv[0])[0],
                            cache_path = "_cache",
                            segments = ["/seb/test", "/seb/demo"])
    except:
        print "Error:", sys.exc_info()[0]
        traceback.print_exc(file=sys.stdout)

    kernel.shutdown()
