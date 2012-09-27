
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
Created on 27.10.2009

@author: Denis Koronchik
'''
import LayoutGroup
import suit.core.render.engine as render_engine

class LayoutGroupLine2dX(LayoutGroup.LayoutGroupOverlay):
    """Layout group for linear layout.
    It makes possible to layout objects by X axis direction.
    It has many possible layout schemes. All of them depends on parameters:
    - max_length - maximum length of group in units (including distance between objects).
        If value of maximum length is -1, then group wouldn't have length constraint. 
    - dist - distance between objects in group.
    - pos - position of group layout (x, y). Depends on alignment:
        @todo: alignment description
    - direction - layout direction. Can be combined with values:
        Dir_pos - positive X axis direction
        Dir_neg - negative X axis direction
    - fit - flag to fit objects in maximum length. If that flag it True, then 
    size of objects will be proportionally changed to fit maximum length 
    (just in case when maximum length isn't -1).    
    - align - horizontal alignment in rect 
    
    Just group and node objects used for layout. Other objects will be ignored.
    
    @todo: finish description
    """
    
    # direction constants
    Dir_pos, Dir_neg    =   range(2)

    # alignment constants
    Align_left, Align_right, Align_center = range(3)
    
    def __init__(self, _objects = [], _max_length = -1, _dist = 0, _pos = (0, 0),
                 _direction = None, _fit = False, _align = None):
        """Constructor
        """
        LayoutGroup.LayoutGroupOverlay.__init__(self)
        
        # maximum length
        self.max_lengh = _max_length
        self.dist = _dist
        self.pos = _pos
        self.direction = _direction
        self.fit = _fit
        self.align = _align        
        
    def __del__(self):
        LayoutGroup.LayoutGroupOverlay.__del__(self)    
    
    def _apply(self):
        """Apply layout group to objects 
        """
            
        dx = None
        dy = None
        
        positions = []
        sizes = []
            
        # getting information about objects (x, y, width, height) 
        # getting maximum height and width
        # count sum width and height
        max_width = 0
        all_width = 0
        objects_info = []
        for obj in self.overlays:
            w, h = obj.getScale()
            x, y = obj.getPosition()
            max_width = max([max_width, w])
            all_width += w
            objects_info.append([x, y, w, h])
            
        # object positions
        obj_pos = [(0, 0)] * len(self.overlays)

        # check maximum length
        if self.max_lengh > 0:
            length = self.max_lengh
            # check distance
            if self.dist > 0:
                length -= (len(self.overlays) - 1) * self.dist
            
            # changing objects size
            if length < all_width or self.fit:
                ratio = length / (float(all_width))
                # set new size
                for obj in objects_info:
                    obj[2] = int(float(obj[2] * ratio))
            
        # count position for objects
        x = 0
        for obj in objects_info:
            
            dx = 0
            if self.align == self.Align_center:
                dx = (render_engine.Window.width - all_width) / 2
            
            if self.direction == self.Dir_neg:
                obj[0] = self.pos[0] - x - obj[2] + dx
            else:
                obj[0] = self.pos[0] + x + dx
            obj[1] = self.pos[1]
            x += self.dist + obj[2]
            
        # apply objects changing
        i = 0
        for obj_i in objects_info:
            obj = self.overlays[i]
            obj.setPosition((obj_i[0], obj_i[1]))
            obj.setScale((obj_i[2], obj_i[3]))
            i += 1

        self.need_layout = False


class LayoutGroupLine2dY(LayoutGroup.LayoutGroupOverlay):
    """Layout group for linear layout.
    It makes possible to layout objects by Y axis direction.
    It has many possible layout schemes. All of them depends on parameters:
    - max_length - maximum length of group in units (including distance between objects).
        If value of maximum length is -1, then group wouldn't have length constraint. 
    - dist - distance between objects in group.
    - pos - position of group layout (x, y). Depends on alignment:
        @todo: alignment description
    - direction - layout direction. Can be combined with values:
        Dir_pos - positive Y axis direction
        Dir_neg - negative Y axis direction
    - fit - flag to fit objects in maximum length. If that flag it True, then 
    size of objects will be proportionally changed to fit maximum length 
    (just in case when maximum length isn't -1).    
    - align - vertical alignment in rect 
    
    Just group and node objects used for layout. Other objects will be ignored.
    
    @todo: finish description
    """
    
    # direction constants
    Dir_pos, Dir_neg    =   range(2)

    # alignment constants
    Align_top, Align_bottom, Align_center = range(3)
    
    def __init__(self, _objects = [], _max_length = -1, _dist = 0, _pos = (0, 0),
                 _direction = None, _fit = False, _align = None):
        """Constructor
        """
        LayoutGroup.LayoutGroupOverlay.__init__(self)
        
        # maximum length
        self.max_lengh = _max_length
        self.dist = _dist
        self.pos = _pos
        self.direction = _direction
        self.fit = _fit
        self.align = _align        
        
    def __del__(self):
        LayoutGroup.LayoutGroupOverlay.__del__(self)    
    
    def _apply(self):
        """Apply layout group to objects 
        """
            
        dx = None
        dy = None
        
        positions = []
        sizes = []
            
        # getting information about objects (x, y, width, height) 
        # getting maximum height and width
        # count sum width and height
        max_height = 0
        all_height = 0
        objects_info = []
        for obj in self.overlays:
            w, h = obj.getScale()
            x, y = obj.getPosition()
            max_height = max([max_height, h])
            all_height += h
            objects_info.append([x, y, w, h])
            
        # object positions
        obj_pos = [(0, 0)] * len(self.overlays)

        # check maximum length
        if self.max_lengh > 0:
            length = self.max_lengh
            # check distance
            if self.dist > 0:
                length -= (len(self.overlays) - 1) * self.dist
            
            # changing objects size
            if length < all_height or self.fit:
                ratio = length / (float(all_height))
                # set new size
                for obj in objects_info:
                    obj[3] = int(float(obj[3] * ratio))
            
        # count position for objects
        y = 0
        for obj in objects_info:
            if self.direction == self.Dir_neg:
                obj[1] = self.pos[1] - y - obj[3]
            else:
                obj[1] = self.pos[1] + y
            obj[0] = self.pos[0]
            y += self.dist + obj[3]
            
        # apply objects changing
        i = 0
        for obj_i in objects_info:
            obj = self.overlays[i]
            obj.setPosition((obj_i[0], obj_i[1]))
            obj.setScale((obj_i[2], obj_i[3]))
            i += 1

        self.need_layout = False
