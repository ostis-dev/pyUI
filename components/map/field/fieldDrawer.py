
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


import field as fieldModule
import cairo

class FieldDrawer:
    field = 0
    standardConstrainPx = 512
    
    def __init__(self):
        self.standardField = 0
        self.manager = fieldModule.ScaleManager()
    
    def createStandardField(self):
        bounds = self.field.getBounds()
        minx = bounds[0]
        miny = bounds[1]
        # Maximum length of field from hor/ver lengths
        xDif = bounds[2] - minx
        yDif = bounds[3] - miny
        
        maxDif = max(xDif, yDif)
        #scale = self.standardConstrainPx / maxDif;
        if xDif >= yDif:
            addX = -minx
            addY = -miny + (maxDif - yDif) / 2
        else:
            addX = -minx + (yDif - xDif) / 4
            addY = -miny
        mult = self.standardConstrainPx / maxDif;
        
        cnt = 1
        # creating standard field
        standardField = fieldModule.Field()
        for layer in self.field.layers:
            #if layer.visible:
            newLayer = fieldModule.Layer()
            newLayer.visible = layer.visible
            newLayer.name = layer.name
            for fieldItem in layer.items:
                #if isinstance(fieldItem, fieldModule.FieldLine):
                #    pts = self.transformPoints([fieldItem.fromPt, fieldItem.toPt], addX, addY, maxDif)                        
                #    newObj = fieldModule.FieldLine(pts[0], pts[1])
                #    #print "    created line"
                if isinstance(fieldItem, fieldModule.LineItem):
                    pts = self.transformPointsArr(fieldItem.points, addX, addY, maxDif)
                    newObj = fieldModule.LineItem(pts, (1, 1))
                    cnt += 1                        
                elif isinstance(fieldItem, fieldModule.PolygonItem):
                    pts = self.transformPointsArr(fieldItem.points, addX, addY, maxDif)
                    newObj = fieldModule.PolygonItem(pts, (1, 1))
                    #print "    created region"
                elif isinstance(fieldItem, fieldModule.PointItem):
                    pts = self.transformPoints([fieldItem.point], addX, addY, maxDif)
                    newObj = fieldModule.PointItem(pts[0])
                    #print "    created point" 
                
                newObj.visible = fieldItem.visible
                newObj.drawText = fieldItem.drawText
                newObj.type = fieldItem.type
                newObj.attributes = fieldItem.attributes
                newLayer.addItem(newObj)        
            standardField.addLayer(newLayer)
        return standardField
    
    
    def transformPoints(self, points, addX, addY, maxDif):
        newPoints = []
        for point in points:
            x = (addX + point[0]) / maxDif
            y = 1 - ((addY + point[1])) / maxDif
            newPoints.append((x, y))
        return newPoints
    
    def transformPointsArr(self, points, addX, addY, maxDif):
        newPoints = []
        for pointlist in points:
            newList = []
            for point in pointlist:
                x = (addX + point[0]) / maxDif
                y = 1 - ((addY + point[1])) / maxDif
                newList.append((x, y))
            newPoints.append(newList)
        return newPoints
    
    def getRGBFromId(self, id):
        x = id % 10
        r = x * 0.1
        g = x * 0.2
        b = 1 - (x * 0.3)                                
        r = 1 - (r - int(r)) / 5
        g = 1 - (g - int(g)) / 5
        b = 1 - (b - int(b)) / 5
        
        
        return r, g, b
    
    
    
    def getObjectAtPoint(self, pt):
        field = self.standardField
        classifier = field.classifier
        # applying scale manager (setting visibility of objects and labels)
        #field.applyScaleManager(self.manager)
            
        #print 'getting object at ' + str(pt) 
        
        res = []
        
        # iterating through visible layers
        for layer in field.layers:
            if (layer.visible):
                # iterating through visible objects
                for fieldItem in layer.items:
                    if (fieldItem.visible):
                        reg = isinstance(fieldItem, fieldModule.PolygonItem)
                        line = isinstance(fieldItem, fieldModule.LineItem)                  
                        if reg or line: 
                            bounds = fieldItem.getBounds()
                            cnd = 0
                            if pt[0] > bounds[0] and pt[0] < bounds[2] and pt[1] > bounds[1] and pt[1] < bounds[3]:                                
                                for pointlist in fieldItem.points:
                                    if reg:
                                        if self.inRegion(pointlist, pt):
#                                            print 'hooray from ' + str(cnd)
                                            #selected = not selected
                                            res.append((layer, fieldItem)) 
#                                            print fieldItem.attr 
                                    elif line:
                                        if self.onLine(pointlist, pt):
#                                            print 'line hooray from ' + str(cnd)
#                                            fieldItem.selected = not fieldItem.selected
                                            res.append((layer, fieldItem))
#                                            print fieldItem.attr
                                    
                            #for pointlist in points:
                            #   for point in pointlist:
                                     
#        print '-end-'
        return res
        
        
    def onLine(self, points, pt):
        result = False
        lng = len(points)
        X = 0
        Y = 1
        x = pt[X]
        y = pt[Y]
        i = 1
        thres = 0.0001
        while i < lng:
            pi = points[i]
            pj = points[i - 1]
            distI = (pi[X] - pt[X]) ** 2 + (pi[Y] - pt[Y]) ** 2
            distJ = (pj[X] - pt[X]) ** 2 + (pj[Y] - pt[Y]) ** 2
            distL = (pj[X] - pi[X]) ** 2 + (pj[Y] - pi[Y]) ** 2
            if distI + distJ - distL < thres:
                return True
            i += 1
        return False
            
        
    def inRegion(self, points, pt):
        result = False
        lng = len(points)
        j = lng - 1
        i = 0
        X = 0
        Y = 1
        x = pt[X]
        y = pt[Y]
        while i < lng:
            pi = points[i]
            pj = points[j]
            if ((((pi[Y] <= y) and (y < pj[Y])) or 
                 ((pj[Y] <= y) and (y < pi[Y]))) and
                 (x > (pj[X] - pi[X]) * (y - pi[Y]) / (pj[Y] - pi[Y]) + pi[X])):
                result = not result
            j = i
            i += 1            
        return result


        
    def drawLayerData(self, data, selectionOnly = False):
        layer = data["layer"]
        ctx = data["context"]
        selCtx = data["selected-context"]
        
        scale = self.manager.scale
        # getting resizing factor
        factor = self.manager.getFactor()
        
        # setting variables SIZEX and SIZEY to the size of field in pixels 
        SIZEX = SIZEY = self.standardConstrainPx * factor

        # always using standard field for drawing
        field = self.standardField
        classifier = field.classifier
        
        if (layer.visible):
            # iterating through visible items
            if not data["drawn"] and not selectionOnly:
                for fieldItem in layer.items:
                    if fieldItem.visible:
                        self.drawItem(fieldItem, ctx, classifier,
                                      SIZEX, SIZEY, None, scale)
            for selItem in layer.selected:
                self.drawItem(selItem, selCtx, classifier,
                                  SIZEX, SIZEY, None, scale, True)
                #print " drawn " + str(selItem.attributes)
            data["drawn"] = True
            
    
    def drawIt(self, scale, layerData, applyManager = True):    
        ''' 
        This function does all the field drawing. After it the field
        is tiled and saved to cache folder
        scale parameter stores the index of scale to apply
        '''
        
        # settings scale to the scale manager 
        self.manager.scale = scale
        # getting resizing factor
        factor = self.manager.getFactor()
        
        # setting variables SIZEX and SIZEY to the size of field in pixels 
        SIZEX = SIZEY = self.standardConstrainPx * factor
        
        # always using standard field for drawing
        field = self.standardField
        classifier = field.classifier
        # applying scale manager (setting visibility of items and labels)
        if applyManager:
            field.applyScaleManager(self.manager)
        
        #print 'before draw'
        cnt = 0
        FieldDrawer.ex = 0;
        FieldDrawer.fx = 0
        # iterating through visible layers
        #for layer in field.layers:
        i = 0
        for data in layerData:
            self.drawLayerData(data)
        #print 'drawn ' + str(cnt) + " items, " + str(FieldDrawer.ex) + " from paths, " + str(FieldDrawer.fx) + " without"  

    ex = 0
    fx = 0    
    
    
    def lineToPoint(self, point, boundRect, ctx, SIZEX, SIZEY):
        if boundRect == None:
            x = (point[0]) 
            y = (point[1]) 
        else:
            x = (point[0] - boundRect[0]) / (boundRect[2] - boundRect[0])
            y = (point[1] - boundRect[3]) / (boundRect[1] - boundRect[3])
        ctx.line_to(x * SIZEX, y * SIZEY)
        
    
    def drawItem(self, fieldItem, ctx, classifier, SIZEX, SIZEY,
                 boundRect, scale, selected = False):
        # if the object is either region or polyline, the processing is quite similar
        if type(fieldItem) == fieldModule.PolygonItem or type(fieldItem) == fieldModule.LineItem:
            # region = True if the object is region                            
            region = type(fieldItem) == fieldModule.PolygonItem
            # getting points variable which in turn stores array of 
            # independent regions or polylines                                                  
            points = fieldItem.points
            # iterating through this independent regions/polylines
            
            FieldDrawer.fx = FieldDrawer.fx + 1
            
            #print 'draw item ' + str(fieldItem)
            
            
            for pointlist in points:
                #print 'draw points: ' + str(pointlist)
                # remove dashes if any                            
                ctx.set_dash([], 0)
                
                # if it's region we create new path which'll be closed after drawing
                
                
                if boundRect == None:
                    x = (pointlist[0][0])
                    y = (pointlist[0][1])
                else:
                    x = (pointlist[0][0] - boundRect[0]) / (boundRect[2] - boundRect[0])
                    y = (pointlist[0][1] - boundRect[3]) / (boundRect[1] - boundRect[3])
                # move to first point    
                ctx.move_to(x * SIZEX, y * SIZEY)
                
                i = 0
                # for every point draw a line to it from previous one
                for point in pointlist:
                    # counting pixel coordinates
                    self.lineToPoint(point, boundRect, ctx, SIZEX, SIZEY)
                if isinstance(fieldItem, fieldModule.PolygonItem) and len(pointlist) > 0:
                    self.lineToPoint(pointlist[0], boundRect, ctx, SIZEX, SIZEY)
                
                    
                #if isinstance(fieldItem, fieldModule.PolygonItem):
                    #ctx.close_path()
                    #fieldItem.path = ctx.copy_path()
                    
            # implementation of different behavior in dependence 
            # of type of the object follows
            if (fieldItem.type == classifier.TYPE_AREA):
                # if currently being drawn object is area
                # fill it with colors that depend on object id
                r, g, b = self.getRGBFromId(fieldItem.id)
                if selected:
                    r = 1.8 - r
                    g = 1.8 - g
                    b = 1.8 - b
                ctx.set_source_rgba (r, g, b, 1)
                ctx.fill_preserve()
                
                # set line width in correspondence to scale
                if scale > 1:
                    wid = 4
                else:
                    wid = 2
                ctx.set_line_width (wid)
                
                # tinge of green
                ctx.set_source_rgba (0.2, 0.7, 0.2, 1)
                if selected:
                    ctx.set_source_rgba (0.8, 0.3, 0.8, 1)
            elif (fieldItem.type in classifier.TYPES_RAILWAY):
                # if the object is railway
                # draw it as black dashed line 
                dashes = [5.0, 2.0, 1.0, 1.0]
                ndash = len(dashes)
                offset = 10.0
                ctx.set_dash(dashes, offset)
                if scale > 3:
                    wid = 3
                else:                            
                    wid = scale - 1                
                ctx.set_line_width (wid)
                ctx.set_source_rgba (0, 0, 0, 1)
                if selected:
                    ctx.set_source_rgba (0.7, 0.7, 0.7, 1)
            elif (fieldItem.type in classifier.TYPES_ROAD):
                # if the object is road                               
                
                # default width
                wid = 2
                
                # get the type of road's surface and  
                # set line width and color in accordint to it                                
                if fieldItem.type == fieldModule.CommonClassifier.TYPE_ROAD_MAGISTRAL:
                    wid = 3
                    ctx.set_source_rgba (0.8, 0, 0, 1)
                    if selected:
                        ctx.set_source_rgba (0.2, 1, 1, 1)
                elif fieldItem.type == fieldModule.CommonClassifier.TYPE_ROAD_WITH_IMPROVED_SURFACE:
                    wid = 2
                    ctx.set_source_rgba (0.8, 0, 1, 1)
                    if selected:
                        ctx.set_source_rgba (0.2, 1, 0, 1)
                elif fieldItem.type == fieldModule.CommonClassifier.TYPE_ROAD_WITH_SURFACE:
                    wid = 1
                    ctx.set_source_rgba (0.7, 0.7, 0.7, 1)
                    if selected:
                        ctx.set_source_rgba (0.3, 0.3, 0.3, 1)
                elif fieldItem.type == fieldModule.CommonClassifier.TYPE_ROAD_WITHOUT_SURFACE:
                    wid = 1
                    ctx.set_source_rgba (1, 1, 0, 1)
                    if selected:
                        ctx.set_source_rgba (0, 0, 1, 1)
                
                # decrease width if the scale's too low
                if scale <= 2:
                    wid = 1
                
                ctx.set_line_width (wid)
            elif (fieldItem.type in classifier.TYPES_TOWN):
                # if the object is town
                # get it's name
                nameAttr = fieldModule.CommonClassifier.ATTRIBUTE_TOWN_NAME
                if not nameAttr in fieldItem.attributes:
                    name = "----"
                else:
                    name = unicode(fieldItem.attributes[nameAttr])
                               
                # fill it with red             
                ctx.set_source_rgba (1, 0, 0, 1)
                if selected:
                    ctx.set_source_rgba (0.2, 1, 0.2, 1)
                ctx.fill_preserve()
                
                # if the name should be drawn
                if fieldItem.drawText:
                    # get the bounds of town and calculate center
                    # of it in pixels
                    bnds = fieldItem.getBounds()
                    if boundRect == None:
                        x = (bnds[2] + bnds[0]) / 2
                        y = bnds[1]
                    else:
                        x = ((bnds[2] + bnds[0]) / 2 - boundRect[0]) / (boundRect[2] - boundRect[0]) 
                        y = (bnds[1] - boundRect[3]) / (boundRect[1] - boundRect[3])
                    x *= SIZEX
                    y *= SIZEY
                    
                    # choose font
                    ctx.select_font_face ("Verdana",
                        cairo.FONT_SLANT_NORMAL,
                        cairo.FONT_WEIGHT_NORMAL)
                    fontSize = 14
                    
                    # choose font size in dependence
                    # of number of inhabitants
                    inhabs = fieldModule.CommonClassifier.ATTRIBUTE_INHABITANTS
                    if int(fieldItem.attributes[inhabs]) > 100000:
                        fontSize = 18
                    elif int(fieldItem.attributes[inhabs]) < 5000:
                        fontSize = 12
                    elif int(fieldItem.attributes[inhabs]) > 50000:
                        fontSize = 16
                    
                    # decrease font size if the scale's low
                    if scale < 3:
                        fontSize -= 4 - scale
                        
                    ctx.set_font_size (fontSize)
                    ctx.set_source_rgba (0, 0, 0, 1)
                    
                    
                    # get text extents and calculate the 
                    # position where to draw the text
                    
                    extents = ctx.text_extents (name)
                    x -= (extents[2] / 2 + extents[0])
                    y -= (extents[3] / 2 + extents[1]) - 10
#                    print 'x, y: ' + str((x,y))
                    # draw the text
                    ctx.move_to (x, y)
                    ctx.show_text (name)
                    
                
                # decide whether to draw the outline                               # draw line
                if scale > 1:
                    wid = 1
                else:
                    wid = 0
                    
                ctx.set_source_rgba (0, 0, 0, 0.7)
                ctx.set_line_width (wid)
                
            else:
                if not selected:
                    ctx.set_source_rgba (0, 0, 0, 1)
                    ctx.set_line_width (1)
                else:
                    ctx.set_source_rgba (1, 0, 0, 1)
                    ctx.set_line_width (2)
                
                    
            # stroke (draw with the pen)    
            ctx.stroke()
#    
#    def tile(self, image, n, scale):
#        tileSize = image.size[0] / n        
#        for x in range (0, n):
#            for y in range (0, n):
#                tile = image.crop((x * tileSize, y * tileSize, (x + 1) * tileSize, (y + 1) * tileSize))
#                tile.save("fieldcache/image" + str(scale) + "-1_" + str(x) + "-" + str(y) + ".png")
#    
    
    
    
#    def basicFill(self):
#        self.field = fieldModule.Field()
#        transformScale = (0.6, 1)
#        layer = fieldModule.Layer()
#        classifier = self.field.classifier
#    
#        print 'basic begin'
#        #line = self.field.FieldLine((23.5, 55), (29, 56)) 
#        #layer.AddItem(line)
#        
#        points = [[20., 55.], [25., 50.], [30., 55.], [25., 60.]]
#        region = fieldModule.PolygonItem([points], transformScale)
#        region.type = classifier.TYPE_AREA
#        layer.AddItem(region)

#        for i in range (0, 6):
#            points = pointsModule.pointsRgn[i]
#            region = fieldModule.PolygonItem([points], transformScale)
#            region.type = classifier.TYPE_AREA
#            layer.AddItem(region)
            
#        for pts in pointsModule.polylines:
#            line = fieldModule.LineItem([pts], transformScale)
#            line.type = classifier.TYPE_RAILWAY
#            layer.AddItem(line)
#            
#        ind = 0
#        for pts in roadPoints.roads:
#            line = fieldModule.LineItem(pts, transformScale)
#            line.type = classifier.TYPE_ROAD
#            line.attr[2] = roadPoints.roadTypes[ind]
#            line.attr[3] = roadPoints.surfaces[ind]
#            layer.AddItem(line)
#            ind += 1
#            
#        names = []
#        f = open('towns.txt', 'r')
#        for line in f:
#            names.append(line.strip())
#        f.close()
#
#        
#        ind = 0
#        for townPts in townPoints.towns:
#            town = fieldModule.PolygonItem(townPts, transformScale)
#            town.type = classifier.TYPE_TOWN
#            town.attr[0] = names[ind]
#            town.attr[2] = townPoints.inhabs[ind]
#            #names[ind]
#            #sizes[ind]
#            layer.AddItem(town)
#            ind += 1
#        #for i in range (0, 6):
        
#        self.field.AddLayer(layer)
#        print 'finish basic fill'
#        self.standardField = self.createStandardField()
#        print 'created field'


    
#    def drawRect(self, rect, scale, addition):
#        return
#        self.manager.scale = scale
#        
#        #factor = self.manager.GetFactor()
#        # setting variables SIZEX and SIZEY to the size of field in pixels  
#        SIZEX = 500
#        SIZEY = int(SIZEX * (rect.bounds[3] - rect.bounds[1]) / (rect.bounds[2] - rect.bounds[0]))
##        print str(SIZEX) + ' x '  +str(SIZEY)
#        
#        # creating cairo surface for drawing
#        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, SIZEX, SIZEY)
#        ctx = cairo.Context(surface)
#        
#        field = self.standardField
#        classifier = field.classifier
#        # applying scale manager (setting visibility of items and labels)
#        field.ApplySMToRect(self.manager, rect)
#        
#        
#        if rect.items != []:
#            for fieldItem in rect.items:
#                if fieldItem.visible:                     
#                    self.drawItem(fieldItem, ctx, classifier, SIZEX, SIZEY, 
#                                  rect.bounds, scale)
         
        #print 'layers: ' + str(len(field.layers)) 
                
        #for layer in field.layers:
            #if layer.visible:
                # iterating through visible items
                #for fieldItem in layer.items:
                    #if not fieldItem.visible:
                        #print 'Opa Jack'                
                
        # iterating through visible layers
        #for layer in field.layers:
        #    if layer.visible:
        #        # iterating through visible items
        #        for fieldItem in layer.items:
        #            if fieldItem.visible:                        
        #                self.drawItem(fieldItem, ctx, classifier, SIZEX, SIZEY, rect.bounds, scale)
        
#        print 'to ' + rectPath(addition)
#        surface.write_to_png(rectPath(addition))
        