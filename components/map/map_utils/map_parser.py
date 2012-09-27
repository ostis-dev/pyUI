
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
Created on 16.06.2010

@author: Sergius
'''
import map_utils.midmif_parser

class LayersParser():
    def __init__(self):
        self.layers = []
        self.layer_name = []
    def parseLayers(self, data):
        list = []
        for i in range(len(data)):

            if '#layer' in data[i]:
                if len(list)>0:
                    parser = map_utils.midmif_parser.MapParser()
                    parser.parseFromString(list)
                    self.layers.append(parser)
                    list = []
                self.layer_name.append(data[i][7:len(data[i])])
            else:  
                list.append(data[i])
        if len(list)>0:
            parser = map_utils.midmif_parser.MapParser()
            parser.parseFromString(list)
            self.layers.append(parser)
