
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


import math
import suit.core.objects as objects

'''
Created on 29.11.2009

@author: Andrei Glazunov
'''


# Useful constants
LEFT = 0
TOP = 1
RIGHT = 2
BOTTOM = 3
X = 0
Y = 1


'''
	Classifier links codes with the classes.
	Classifier contains:
		- object classes
		- attribute classes
		- object class groups
''' 
class Classifier(object):
    TYPE_UNDEFINED = -1

'''
	This is the base classifier implementation
	All codes are based on MID/MIF format classifier
'''
class CommonClassifier(Classifier):
    TYPE_RAILWAY = 61111000
    TYPE_RAILROAD = 61112000
    TYPE_AREA = 83120000
    TYPE_DISTRICT = 83130000
    TYPE_TOWN = 41100000
    TYPE_SMALL_TOWN = 41200000
    TYPE_VILLAGE_TOWN = 42100000
    TYPE_HOLIDAY_VILLAGE_TOWN = 43100000
    TYPE_SMALL_TOWN_UNCATEGORIZED = 43200000
    TYPE_ROAD_WITHOUT_SURFACE = 61310000
    TYPE_ROAD_WITH_SURFACE = 61230000
    TYPE_ROAD_WITH_IMPROVED_SURFACE = 61220000
    TYPE_ROAD_MAGISTRAL = 61210000
    
    TYPES_RAILWAY = [TYPE_RAILWAY, TYPE_RAILROAD]
    TYPES_TOWN = [TYPE_TOWN, TYPE_SMALL_TOWN, TYPE_VILLAGE_TOWN, TYPE_HOLIDAY_VILLAGE_TOWN,
                  TYPE_SMALL_TOWN_UNCATEGORIZED]
    TYPES_ROAD = [TYPE_ROAD_WITHOUT_SURFACE, TYPE_ROAD_WITH_SURFACE, 
                  TYPE_ROAD_WITH_IMPROVED_SURFACE, TYPE_ROAD_MAGISTRAL]
    
    ATTRIBUTE_NAME_CODE = "NAME_CODE"
    ATTRIBUTE_ALTITUDE = "F4"
    ATTRIBUTE_RELATIVE_HEIGHT = "F1"
    ATTRIBUTE_DEPTH = "F7"
    ATTRIBUTE_STATE = "F3"
    ATTRIBUTE_LOCATION = "F35"
    ATTRIBUTE_COASTLINE = "F36"
    ATTRIBUTE_SIGN_NAVIGATION = "F32"
    ATTRIBUTE_NAME_SIGN_NAVIGATION = "NAME_F32"
    ATTRIBUTE_NAME_COASTLINE = "NAME_F36"
    ATTRIBUTE_AREA = "AREA"
    ATTRIBUTE_DISTRICT = "DISTRICT"
    ATTRIBUTE_INHABITANTS = "F38"
    ATTRIBUTE_TOWN_NAME = "F9"
    ATTRIBUTE_ROAD_IMPORTANCE = "F57"
    ATTRIBUTE_ADMINISTRATIVE_IMPORTANCE = "F39"
    ATTRIBUTE_NAME_ADMINISTRATIVE_IMPORTANCE = "NAME_F39"
    ATTRIBUTE_POLITIC_IMPORTANCE = "F43"
    ATTRIBUTE_NAME_POLITIC_IMPORTANCE = "NAME_F43"
    ATTRIBUTE_VOLTAGE = "НапРяжение"
    ATTRIBUTE_NAME_STATE = "NAME_F3"
    ATTRIBUTE_NAME = "NAME"
    ATTRIBUTE_ROAD_NUMBER = "F53"
    ATTRIBUTE_CUSTOMS = "F246"
    ATTRIBUTE_NUMBER_WAYS = "F51"
    ATTRIBUTE_THRUST_TYPE = "F54"
    ATTRIBUTE_BOUNDARY = "BOUNDARY"
    
    atributes = {ATTRIBUTE_NAME_CODE: "наименование_классификационного_кода",
                 ATTRIBUTE_ALTITUDE: "абсолютная_высота",
                 ATTRIBUTE_RELATIVE_HEIGHT: "относительная_высота",
                 ATTRIBUTE_DEPTH: "Глубина",
                 ATTRIBUTE_STATE: "Состояние",
                 ATTRIBUTE_LOCATION: "характер_расположения_объекта",
                 ATTRIBUTE_COASTLINE: "характер_береговой_линии",
                 ATTRIBUTE_SIGN_NAVIGATION: "признак_судоходства",
                 ATTRIBUTE_NAME_SIGN_NAVIGATION: "расшифровка_признака_судоходства",
                 ATTRIBUTE_NAME_COASTLINE: "расшифровка_характера_береговой_линии",
                 ATTRIBUTE_AREA: "наименование_области",
                 ATTRIBUTE_DISTRICT: "наименование_района",
                 ATTRIBUTE_INHABITANTS: "количество_жителей",
                 ATTRIBUTE_TOWN_NAME: "собственное_название",
                 ATTRIBUTE_ROAD_IMPORTANCE: "собственное_название",
                 ATTRIBUTE_ADMINISTRATIVE_IMPORTANCE: "административно_хозяйственное_значение",
                 ATTRIBUTE_NAME_ADMINISTRATIVE_IMPORTANCE: "расшифровка_административно_хозяйственного_значения",
                 ATTRIBUTE_POLITIC_IMPORTANCE: "политико_административное_значение_н_п_",
                 ATTRIBUTE_NAME_POLITIC_IMPORTANCE: "расшифровка_политико_административного_значения_н_п_",
                 ATTRIBUTE_VOLTAGE: "напряжение_кабеля_сети",
                 ATTRIBUTE_NAME_STATE: "наименование_состояния",
                 ATTRIBUTE_NAME: "собственное_название",
                 ATTRIBUTE_ROAD_NUMBER: "номер_дороги",
                 ATTRIBUTE_CUSTOMS: "тип_пограничного_пункта",
                 ATTRIBUTE_NUMBER_WAYS: "число_путей",
                 ATTRIBUTE_THRUST_TYPE: "вид_тяги",
                 ATTRIBUTE_BOUNDARY: "приграничное_государство"}
    
    ROAD_M = "M"
    ROAD_REPUBLIC = "R"
    ROAD_MEDIUM = "I"
    ROAD_SMALL = "O"
    
'''
	True if x in [lower, upper]
'''
def between(x, lower, upper):
    return x >= lower and x <= upper

'''
	True if x in [one, two] or in [wto, one]
'''
def xbetween(x, one, two):
    return between(x, one, two) or between(x, two, one)

	

'''
	Rectangle on a field. Each field has a rectangle assosiated with it.
	Each rectangle is divided into several (e.g. 2x2), hence one can iterate 
	through all nested rectangles recursively.
'''
class FieldRect(object):
	# number of nested rects, for 2 dimensions
    childNum = (2, 2)

    '''
		This method is called from the base rect when 
		we want to create and populate all the nested
		rectangles. We specify the depth and create
		children recursively, until the necessary depth 
		level is reached. We also calculate, what rectangle
		items should belong to each child, and add this
		items to the correspondent children
		
		@param depth the maximum nest level
	'''
    def appendChildren(self, depth):
        #print 'depth ' + str(depth)
        rect = self
        
        # init chilren array 
        rect.children = []
        # children matrix sizes
        lenVer = FieldRect.childNum[0]
        lenHor = FieldRect.childNum[1]
        # sides of child in pixels
        horSize = (rect.bounds[2] - rect.bounds[0]) / lenHor
        verSize = (rect.bounds[3] - rect.bounds[1]) / lenVer
        
        # main cycle for children filling    
        for i in xrange (0, lenVer):
            app = []
            # secondary cycle for children filling
            for j in xrange (0, lenHor):
                # create a child
                newRect = FieldRect()
                # setting its bounds
                left = rect.bounds[0] + j * horSize
                top = rect.bounds[1] + i * verSize
                newRect.bounds = (left, top, left + horSize, top + verSize)
                # append child to matrix
                app.append(newRect)
            rect.children.append(app)
                
        # links to each rect
        tlRect = rect.children[0][0]
        trRect = rect.children[0][1]
        blRect = rect.children[1][0]
        brRect = rect.children[1][1]
        
        # append items to children!
        self.appendItems(tlRect, trRect, blRect, brRect)
        
        # recursion
        if depth < Field.rectDepth:
            tlRect.appendChildren(depth + 1)
            trRect.appendChildren(depth + 1)
            blRect.appendChildren(depth + 1)
            brRect.appendChildren(depth + 1)        
            
    
	'''
		Here we calculate, what rectangle items should belong 
		to each child, and add this items to the correspondent children
		
		NOTE: implementation for 2x2 children only!
		
		@param tlRect top-left child of current rect
		@param trRect top-right child of current rect
		@param blRect bottom-left child of current rect
		@param brRect bottom-right child of current rect
	'''
    def appendItems(self, tlRect, trRect, blRect, brRect):        
        # iterate items of this rectangle, we'll distribute them to children
        for item in self.items:
            if type(item) == LineItem or type(item) == PolygonItem:
                bl, tl, tr, br, all, milk = self.doThePoints(item, tlRect, trRect, blRect, brRect)
                # if not trivial invisible, process the lines
                if not all and (milk or (tl and br) or (tr and bl)):
                    self.doTheLines(item, tl, tr, bl, br, tlRect, trRect, blRect, brRect)

                    
    '''
		Returns true if the line between two poins belongs to rect
		
		@param p1 first point of the line
		@param p2 second point of the line
	'''
    def lineInRect(self, p1, p2):
        # checks whether line has points in rect
        if self.contains(p1) or self.contains(p2):
            return True
        return (xbetween(self.bounds[LEFT], p1[0], p2[0]) or xbetween(self.bounds[RIGHT], p1[0], p2[0])) and\
                    (xbetween(self.bounds[TOP], p1[1], p2[1]) or xbetween(self.bounds[BOTTOM], p1[1], p2[1]))
        
    
	'''
		Append the lines contained by the rect to the correspondent child rects
	'''
    def doTheLines(self, item, tl, tr, bl, br, tlRect, trRect, blRect, brRect):
        # iterating segments
        for points in item.points:
            length = len(points)            
            for ptNum in xrange(0, length):
                # two incident points
                p1 = points[ptNum]
                if ptNum == length - 1:
                    p2 = points[0]
                else:
                    p2 = points[ptNum + 1]
                
				# append
                if not tl and tlRect.lineInRect(p1, p2):
                    tl = True
                    tlRect.items.append(item)
                if not tr and trRect.lineInRect(p1, p2):
                    tr = True
                    trRect.items.append(item)
                if not bl and blRect.lineInRect(p1, p2):
                    bl = True
                    blRect.items.append(item)
                if not br and brRect.lineInRect(p1, p2):
                    br = True
                    brRect.items.append(item)
        return (bl, tl, tr, br)                        
                    
    
	'''
		Append the points contained by the rect to the correspondent child rects
	'''	
    def doThePoints(self, item, tlRect, trRect, blRect, brRect):
        all = False
        milk = False
            
        tl, tr, bl, br = False, False, False, False
        for points in item.points:
            any = False            
            for point in points:
                if tl and tr and bl and br:
                    all = True
                    break
                
                if not tl:
                    if tlRect.contains(point):
                        tl = True
                        tlRect.items.append(item)                       
                        any = True
                if not tr:
                    if trRect.contains(point):
                        tr = True
                        trRect.items.append(item)
                        any = True
                if not bl:
                    if blRect.contains(point):
                        bl = True
                        blRect.items.append(item)
                        any = True
                if not br:
                    if brRect.contains(point):
                        br = True
                        brRect.items.append(item)
                        any = True
                if not any:
                    milk = True
                    #print 'premature'
                    break
            if all:
                break
        return (bl, tl, tr, br, all, milk)
        
                
    
    def __init__(self):
        self.children = None
        self.bounds = (0, 0, 0, 0)
        self.items = []
        
    '''
		Returns true if the contains specified points
	'''
    def contains(self, point):
        return between(point[X], self.bounds[LEFT], self.bounds[RIGHT]) and \
    between(point[Y], self.bounds[TOP], self.bounds[BOTTOM]) 
        
		
		
'''
	Field class stores items of the following types:
		Polygon (region): see PolygonItem
		PolyLine (line): see LineItem
		Point: see PointItem
	This items are stored on layers (see Layer)
	Field is divided into rects (see FieldRect) for
	improving rendering perfomance
	Field contains classifier (see Classifier)
	
	Field is a general term while this class is majorly
	used to store maps. 
'''
class Field(object):
	# Level of nested rects
    rectDepth = 2
    
    def __init__(self):
        self.classifier = CommonClassifier()
        self.layers = []
        self.rect = FieldRect()
        self.rects = []

	'''
		Adds layer to field
	'''
    def addLayer(self, lr):
        self.layers.append(lr)
        self.rect.items += lr.items
        
    ''' 
		Distributes items between child rects
	'''
    def distributeItems(self):
        self.rect.bounds = self.getBounds()
        self.rect.appendChildren(0)
        
        self.rects = []
        
	'''
		Output children list
		FOR DEBUG PURPOSES
	'''
    def outChildren(self, rect, depth, par):
        if rect.children != None:
            sum = 0
            for children in rect.children:            
                for child in children:
                    sz = len(child.items)
                    sum += sz
                    if sz != 0:
                        self.rects.append(child)
                    print "  "*depth + str(sz)
                    self.outChildren(child, depth + 1, sz)                    
            if par == 0:
                print "  "*depth + 'parent: ' + str(par) + ', sz: ' + str(sz)
            else:  
                print "  "*depth + '[' + str((.0 + sum - par) / par * 100) + ' %]' 
        
	'''
		Get the bounds of the field
		
		@return array of the following: [min(X), min(Y), max(X), max(Y)]
	'''
    def getBounds(self):
		if len(self.layers) < 1:
			return None
		
		bnd = self.layers[0].getBounds()
		minx = bnd[0]
		miny = bnd[1]
		maxx = bnd[2]
		maxy = bnd[3] 
		
		for lr in self.layers:
		    bnds = lr.getBounds()
		    minx = min(minx, bnds[0])
		    miny = min(miny, bnds[1])
		    maxx = max(maxx, bnds[2])
		    maxy = max(maxy, bnds[3])
		    
		return [minx, miny, maxx, maxy]
    
    
	#Applying Scale Manager means assigning visibility 
	#to all items based on drawing rules (see ScaleManager)
    def applyScaleManager(self, manager):
        for layer in self.layers:
            if layer.visible:
                for fieldObj in layer.items:
                    self.applySMToItem(manager, fieldObj)
                    
    def applySMToRect(self, manager, rect):
        for fieldObj in rect.items:
            self.applySMToItem(manager, fieldObj)
                    
    
    '''
        This function applies scale manager to the map item.
        It means that it sets visibility of the item and of item text.
        The visibility is determined using drawing rules (see DrawingRule class)
        It depends of the values of specific attribites and the current scale 
    '''
    def applySMToItem(self, manager, fieldObj):
        fieldObj.visible = True
        fieldObj.drawText = False
        
        """
            If classifier type is not defined 
        """        
        if fieldObj.type == self.classifier.TYPE_UNDEFINED:
            fieldObj.visible = True
            fieldObj.drawText = False
        else: # If classifier type is defined
            # trying to find suitable rules
            if not fieldObj.type in manager.rules:
                return
            
            rules = manager.rules[fieldObj.type]
            
            '''
                Setting invisible by default. Going through the rules
                can bring the visibility
            '''
            fieldObj.visible = False
            
            # iterate through the rules
            for rule in rules: 
                if rule.attributeName == ScaleManager.DRAW_TEXT: # specific rule type
                    if manager.scale >= rule.startScale:
                        fieldObj.drawText = True
                elif rule.attributeName == ScaleManager.DRAW_OBJECT:  # specific rule type
                    if manager.scale >= rule.startScale:  
                        fieldObj.visible = True
                elif rule.attributeName in fieldObj.attributes: 
                    '''
                    rule.attributeName represents a determinant attribute,
                    rule.threshold represents a threshold, starting from which the rule is applied
                    rule.direction represents a direction: descending or acscending. E.g. If direction
                        is ScaleManager.DIR_ASC the rule will only be applied for the items,
                        for which the value of determinant attribute is more than threshold
                    rule.comparator is an optional parameter that represents a comparator                                
                    '''
                     
                    value = fieldObj.attributes[rule.attributeName]
                    
                    if not rule.comparator: # it means that values can be compared simply
                        suitsAscComparator = int(value) >= rule.threshold
                    else:   # it means that custom comparator should be used
                        try:
                            suitsAscComparator = rule.comparator[value] >= rule.comparator[rule.threshold]
                        except KeyError:
                            #print "key fail, attrs: " + str(fieldObj.attributes)
                            suitsAscComparator = False
                            #print "Key error, cmp:" + str(rule.comparator) + ", value: " + str(value) 
                    
                    ascending = rule.direction != ScaleManager.DIR_DESC                                         
                    
                    if rule.textRule:
                        if manager.scale >= rule.startScale:                                             
                            if ascending and suitsAscComparator:
                                fieldObj.drawText = True
                                break
                            elif not ascending and not suitsAscComparator:
                                fieldObj.drawText = True
                                break
                    else:
                        if manager.scale >= rule.startScale:                                    
                            if ascending and suitsAscComparator:
                                fieldObj.visible = True
                                break
                            elif not ascending and not suitsAscComparator:
                                fieldObj.visible = True                                                
                                break    
        
'''
	Layer stores items of the following types:
		Polygon (region): see PolygonItem
		PolyLine (line): see LineItem
		Point: see PointItem
'''
class Layer(object):        
    def addItem(self, obj):
        self.items.append(obj)
    
    '''
		Get the bounds of the layer
		
		@return array of the following: [min(X), min(Y), max(X), max(Y)]
	'''
    def getBounds(self):
        bnd = self.items[0].getBounds()
        minx = bnd[0]
        miny = bnd[1]
        maxx = bnd[2]
        maxy = bnd[3]
        
        for obj in self.items:
            bnds = obj.getBounds()
            minx = min(minx, bnds[0])
            miny = min(miny, bnds[1])
            maxx = max(maxx, bnds[2])
            maxy = max(maxy, bnds[3])
            
        return [minx, miny, maxx, maxy]
    
    def toggleObjectSelection(self, obj):
    	if obj in self.selected:
    		self.selected.remove(obj)
    		return False
    	else:
    		self.selected.append(obj)
    		return True
    
    def __init__(self):
        self.items = []
        self.selected = []
        self.name = "new layer"
        self.visible = 1
        pass    
    
'''
	Item that can be stored on a field (more exactly, on a layer)
	Each item has a visibility, text visibility, id, selected, type
	options	and attibutes dictionary
'''        
class FieldObject(object, objects.Object):
    id = 0
    
	# Abstract method
    def getBounds(self):
        pass
    
    def __init__(self):
        objects.Object.__init__(self)
		
        # classifier type (class)
        self.type = Classifier.TYPE_UNDEFINED
		# attributes dictionary
        self.attributes = {}
		
		# set new id
        FieldObject.id += 1
        self.id = FieldObject.id
        self.path = None
		
		#default parameters for visibility, drawtext and selected options
        self.visible = True
        self.selected = False
        self.drawText = False
      
	'''
		Attributes must be set with this method. It assigns it
		to the 'attribures' options, but with some alterations
	'''
    def setAttributes(self, newAttrs):
        self.attributes = newAttrs
		
		# Alterations to be made
        attr = CommonClassifier.ATTRIBUTE_ROAD_IMPORTANCE
        if attr in self.attributes:
            if self.attributes[attr] != "":
                map = {
                       '\xec\xe0\xe3\xe8\xf1\xf2\xf0\xe0\xeb\xfc\xed\xe0\xff': CommonClassifier.ROAD_M,
                       '\xf0\xe5\xf1\xef\xf3\xe1\xeb\xe8\xea\xe0\xed\xf1\xea\xe0\xff': CommonClassifier.ROAD_REPUBLIC,
                       '\xe2\xe0\xe6\xed\xe5\xe9\xf8\xe0\xff \xec\xe5\xf1\xf2\xed\xe0\xff': CommonClassifier.ROAD_MEDIUM,
                       '\xef\xf0\xee\xf7\xe0\xff': CommonClassifier.ROAD_SMALL
                       }
                self.attributes[attr] = map[self.attributes[attr]]
        
        '''
        for key in replaceKeys:
            if key in self.attributes:
                currentValue = self.attributes[key]
                replacementMap = replaceKeys[key]
                if currentValue in replacementMap:
                    # assign a new value 
                    self.attributes[key] = replacementMap[currentValue]
        '''
        


'''
	FieldMultiPointObject is a base class for 
	PolygonItem and LineItem
	
	Points is an array of array of poins
	Transform scale can be applied
'''
class FieldMultiPointObject(FieldObject):    
    def __init__(self, points, transformScale):
        FieldObject.__init__(self)
        #print points
    
        if (transformScale == (1,1)):
            self.points = points
        else: 
            self.points = []
            for pointlist in points:
                newlist = []
                for point in pointlist:
                    if (transformScale[0] != 1):
                        point[0] = point[0] * transformScale[0] 
                    if (transformScale[1] != 1):
                        point[1] = point[1] * transformScale[0]
                    newlist.append(point)
                self.points.append(newlist)
        #print self.points
            
    
    def getBounds(self):
        minx = maxx = self.points[0][0][0]
        miny = maxy = self.points[0][0][1]
        
        for pointlist in self.points:
            for point in pointlist:
                minx = min(minx, point[0])
                miny = min(miny, point[1])
                maxx = max(maxx, point[0])
                maxy = max(maxy, point[1])
            
        return [minx, miny, maxx, maxy]
    
class PolygonItem(FieldMultiPointObject):
    def __init__(self, points, transformScale):
        FieldMultiPointObject.__init__(self, points, transformScale)

class LineItem(FieldMultiPointObject):  
    def __init__(self, points, transformScale):
        FieldMultiPointObject.__init__(self, points, transformScale)
        
class PointItem(FieldObject):
    def __init__(self, point):
        self.point = point
    
    def getBounds(self):
        out = [self.point[0], self.point[1], self.point[0], self.point[1]]
        return out
  

'''
	Scale Manager is applied to to the field, to each item of the field
	It means that it sets visibility of the item and of item text.
	The visibility is determined using drawing rules (see DrawingRule class)
	It depends of the values of specific attribites and the current scale.
'''
class ScaleManager:
    factors = [0.5, 1, 1.3, 1.6, 2, 2.5, 3, 3.5, 4, 5, 8, 12, 16, 20, 40, 80]
    #, 1/16, 1/8, 1/4, 1/3, 1/2
    DRAW_OBJECT = 101
    DRAW_TEXT = -101
    DIR_ASC = 1
    DIR_DESC = 2
    
    '''
        Returns the scale that mathes specified factor best
    '''
    def getAppropriateScale(self, factor):
        if factor <= ScaleManager.factors[0]:
            return 1
        
        for scale in xrange(0, len(ScaleManager.factors)):
            f = ScaleManager.factors[scale]
            if factor < f:
                return scale
            elif factor == f:
                return scale
        return scale
        
    # Returns factor correspondent to specified scale
    def getScaleFactor(self, scale):
        if not scale in range (1, len(ScaleManager.factors)):
            return 1
        return ScaleManager.factors[scale]
    
	# Returns factor correspondent to current scale
    def getFactor(self):
        if not self.scale in range (1, len(ScaleManager.factors)):
            return 1
        return ScaleManager.factors[self.scale]
    
    def increaseScale(self):
        if self.scale < 10:
            self.scale += 1
            return True
        return False
    
    def decreaseScale(self):
        if self.scale > 0:
            self.scale -= 1
            return True
        return False
    
    def __init__(self):
        self.rules = {}
        self.scale = 1
        
        roadComparator = {CommonClassifier.ROAD_M: 5, CommonClassifier.ROAD_REPUBLIC: 
                          4, CommonClassifier.ROAD_MEDIUM: 3, CommonClassifier.ROAD_SMALL: 2}
        
        inhab = CommonClassifier.ATTRIBUTE_INHABITANTS
        townRules = [DrawingRule(ScaleManager.DRAW_OBJECT, 1), 
                     DrawingRule(ScaleManager.DRAW_TEXT, 6),
                     #DrawingRule(inhab, 1, 50000, ScaleManager.DIR_ASC),
                     #DrawingRule(inhab, 2, 30000, ScaleManager.DIR_ASC),
                     #DrawingRule(inhab, 3, 10000, ScaleManager.DIR_ASC),     
                     DrawingRule(inhab, 1, 100000, ScaleManager.DIR_ASC, textRule = True),
                     DrawingRule(inhab, 5, 30000, ScaleManager.DIR_ASC, textRule = True),
                     DrawingRule(inhab, 7, 5000, ScaleManager.DIR_ASC, textRule = True)]
        railwayRules = [DrawingRule(ScaleManager.DRAW_OBJECT, 2)]
        imp = CommonClassifier.ATTRIBUTE_ROAD_IMPORTANCE
        roadRules = [DrawingRule(imp, 1, CommonClassifier.ROAD_M, ScaleManager.DIR_ASC, False, roadComparator),
                     DrawingRule(imp, 4, CommonClassifier.ROAD_REPUBLIC, ScaleManager.DIR_ASC, False, roadComparator),
                     DrawingRule(imp, 6, CommonClassifier.ROAD_MEDIUM, ScaleManager.DIR_ASC, False, roadComparator),
                     DrawingRule(imp, 8, CommonClassifier.ROAD_SMALL, ScaleManager.DIR_ASC, False, roadComparator)
                     ]
        
        for townType in CommonClassifier.TYPES_TOWN:
            self.rules[townType] = townRules
            
        for roadType in CommonClassifier.TYPES_ROAD:
            self.rules[roadType] = roadRules
            
        self.rules[CommonClassifier.TYPE_RAILWAY] = railwayRules

'''
	Drawing rule tells when the item or item text should be drawn, depending
	on the value of determinant attribute
	
	attributeName represents a determinant attribute,
	threshold represents a threshold, starting from which the rule is applied
	direction represents a direction: descending or acscending. E.g. If direction
		is ScaleManager.DIR_ASC the rule will only be applied for the items,
		for which the value of determinant attribute is more than threshold
	comparator is an optional parameter that represents a comparator                                
'''
class DrawingRule:
    def __init__(self, attributeName, startScale, threshold = 0, 
                 direction = ScaleManager.DIR_ASC, textRule = False, comparator = None):
        self.threshold = threshold
        self.attributeName = attributeName
        self.textRule = textRule
        self.startScale = startScale
        self.direction = direction
        self.comparator = comparator
        
    def __str__(self):
        s = "<Rule "
        if self.textRule:
            s += "(TEXT) "
        s += ": attribute: " + str(rule.attributeName) + ": value: " + str(rule.threshold)
        if self.direction == ScaleManager.DIR_DESC:
            s += "+"
        else:
            s+= "-"
        s += ", scale: " + str(rule.startScale) + ">"
        
        return s