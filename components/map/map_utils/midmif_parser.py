
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
Created on 13.04.2010

@author: Sergius & Pavel Karpan
'''
import sys
import re
import codecs

class MapParser():
    def __init__(self):
        '''
        Constructor
        '''
        #MIF ========
        #VERSION
        self.mif_version = 0
        #DELIMITER    
        self.mif_delimiter = ""
        #CoordSys Earth             
        self.mif_coords_sys = -1
        #Projection
        self.mif_projection = -1
        #COLUMNS
        self.mif_columns = []
        #DATA
        self.mif_data = []
        self.object_type = [] 
        
        #MID ========
        
        #MID-file data        
        self.mid_data = []
        
    def __del__(self):
        pass
    
    def setMifVersion(self, version):
        self.mif_version = version
        
    def setMifDelimiter(self, delimiter):
        self.mif_delimiter = delimiter
        
    def setMifCoord_Projection(self, coord, projection):
        self.mif_coords_sys, self.mif_projection = coord, projection
        
    def setMifColumns(self, columns):
        self.mif_columns = columns
        
    def setMifData(self, data):
        self.mif_data.append(data)        
    
    def setMidData(self, data):
        dict = {}
        columns = self.getMifColumns()
        for i in range(len(columns)):
            dict[columns[i][0]] = data[i]
        self.mid_data.append(dict)        
    
    def getMifVersion(self):
        return self.mif_version
        
    def getMifDelimiter(self):
        return self.mif_delimiter
        
    def getMifCoord_Projection(self):
        return self.mif_coords_sys, self.mif_projection
        
    def getMifColumns(self):
        return self.mif_columns
        
    def getMifData(self):
        return self.mif_data
        
    def getMidData(self):
        return self.mid_data
    
    def mifParser(self, mifData):  
        self.setMifVersion(int(re.findall(r'\d+', mifData[0])[0]))        
        self.setMifDelimiter(mifData[1].strip()[-2])        
        items = re.findall(r'(\d+), *(\d+)', mifData[2])[0]
        self.setMifCoord_Projection(int(items[0]), int(items[1]))        
        columns = []
        regions = []
        readLine = 3  
        while readLine < len(mifData):
            if 'COLUMNS' in mifData[readLine]:
                columns_num = int(re.findall(r'\d+', mifData[readLine])[0])
                for i in range(columns_num):
                    readLine = readLine + 1            
                    column_name, column_value = mifData[readLine].strip().split()
                    columns.append((column_name, column_value))
                self.setMifColumns(columns)      
            if 'REGION' in mifData[readLine]:
                region_num = int(re.findall(r'\d+', mifData[readLine])[0])
                region = [] 
                readLine = readLine + 1
                while 'BRUSH' not in mifData[readLine]:
                    points = []
                    lines_num = int(re.findall(r'\d+', mifData[readLine])[0])
                    for i in range(lines_num):
                        readLine = readLine + 1
                        x, y = mifData[readLine].strip().split()
                        points.append([float(x), float(y)])
                    region.append(points)
                    readLine = readLine + 1
                self.setMifData(region)
                self.object_type.append('REGION')              
            if 'LINE' in mifData[readLine][0:4] :
                x1,y1,x2,y2 = mifData[readLine][4:len(mifData[readLine])].strip().split()
                line = [] 
                points = []
                points.append([float(x1), float(y1)])
                points.append([float(x2), float(y2)])
                line.append(points)
                self.setMifData(line)
                self.object_type.append('LINE')
            if 'PLINE' in mifData[readLine]:
                pline = [] 
                points = []
                if 'MULTIPLE' in mifData[readLine]:
                    num_plines = int(mifData[readLine][14:len(mifData[readLine])].strip())
                    while num_plines > 0:
                        points = []
                        readLine = readLine + 1
                        num_points = mifData[readLine].strip()
                        for i in range(int(num_points)):
                            readLine = readLine + 1
                            x, y = mifData[readLine].strip().split()
                            points.append([float(x), float(y)])
                        pline.append(points)
                        num_plines = num_plines - 1
                else:
                    num_points = mifData[readLine][5:len(mifData[readLine])].strip()
                    for i in range(int(num_points)):
                        readLine = readLine + 1
                        x, y = mifData[readLine].strip().split()
                        points.append([float(x), float(y)])
                    pline.append(points)  
                self.setMifData(pline)
                self.object_type.append('PLINE')   
            if 'POINT' in mifData[readLine]:
                point = [] 
                points = []
                x,y = mifData[readLine][5:len(mifData[readLine])].strip().split()
                points.append([float(x), float(y)])
                point.append(points)
                self.setMifData(point)
                self.object_type.append('POINT')  
            readLine = readLine+1
            
    def midParser(self, midData):     
        for line in midData:
            items = line.split(',')
            if(len(items[-1])>2):
                if '"' in items[-1][-3]:
                    items[-2] = items[-2] + "," + items[-1]
                    items = items [:-1]                          
                self.setMidData(items)
            else:                 
                self.setMidData(items)
                
    def parseFromFiles(self, mifPath = "", midPath = ""):

        mifFile = codecs.open(mifPath, mode='r')#, encoding='cp1251')
        mifData = mifFile.readlines()
        mifFile.close()
        self.mifParser(mifData)
        midFile = codecs.open(midPath, mode='r')#, encoding='cp1251')
        midData = midFile.readlines()
        midFile.close()
        self.midParser(midData)              
    
    def parseFromString(self, data):      
        for i in range(len(data)):
            if '#mif' in data[i]:
                f = i+1
            if '#mid' in data[i]:
                d = i+1
        self.mifParser(data[f:d-1])
        self.midParser(data[d:])