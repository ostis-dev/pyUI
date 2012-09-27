
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
Created on 12.02.2010

@author: Denis Koronchik
'''
import ogre.io.OIS as ois
from suit.cf import BaseViewMode


class MapViewMode(BaseViewMode):
    """Mode that allows user to view and navigate in scg window
    """
    def __init__(self, _logic):
        BaseViewMode.__init__(self, _logic, "View mode")
        self.moving = False
        self.zooming = False
        
    def __del__(self):
        BaseViewMode.__del__(self)
        
    def delete(self):
        """Deletion message
        """
        BaseViewMode.delete(self)
        
        
    def activate(self):
        """Activation message
        """
        BaseViewMode.activate(self)
        
    def deactivate(self):
        """Deactivation message
        """
        BaseViewMode.deactivate(self)
        
    def _onKeyPressed(self, _evt):
        viewer = self._logic
        
        if (_evt.key == ois.KC_EQUALS): # increase scale
            #print dir(self._logic)
            viewer.zoomIn()
        elif (_evt.key == ois.KC_MINUS): # decrease scale
            viewer.zoomOut()
        elif (_evt.key == ois.KC_LEFT): 
            viewer.moveOrigin(-1, 0)
        elif (_evt.key == ois.KC_RIGHT): 
            viewer.moveOrigin(1, 0)
        elif (_evt.key == ois.KC_UP): 
            viewer.moveOrigin(0, -1)
        elif (_evt.key == ois.KC_DOWN): 
            viewer.moveOrigin(0, 1)
        elif (_evt.key == ois.KC_D): # default scale
            viewer.scaleManager.scale = 1
        elif (_evt.key == ois.KC_R): # refresh
            print 'refresh'
            viewer._redraw()
        else:
            #print "KEY PRESSED " + str(_evt.key)
            return
        
        viewer._redraw()
         
        
    def _onMouseMoved(self, _evt):
        mstate = _evt.get_state()
        viewer = self._logic
        
        if mstate.Z.rel:    
            pt = (float(mstate.X.abs), float(mstate.Y.abs))    
            viewer.setOrigin(viewer.screenToMap(pt))
            
            if (mstate.Z.rel > 0):
                if viewer.zoomIn():
                    viewer._redraw()
                    
            else:
                if viewer.zoomOut():
                    viewer._redraw()
        else:
            if self.moving:
                pt = (float(mstate.X.abs), float(mstate.Y.abs))
                pt = viewer.screenToMap(pt)
                
                viewer.setOrigin(pt)
            
            if self.zooming:
                pt = (float(mstate.X.abs), float(mstate.Y.abs))        
                pt = viewer.screenToMap(pt)
                
                viewer.zoomRect(self.startPt, pt)
                
            
            
  
    
    
    def _onMousePressed(self, _evt, _id):
        """Mouse button pressed event
        """
        mstate = _evt.get_state()
        
        
        viewer = self._logic
        
        if mstate.buttons == 1:
            tex_size = viewer.tex_size
            fieldDrawer = viewer.drawer
            pt = (float(mstate.X.abs), float(mstate.Y.abs))
            res = fieldDrawer.getObjectAtPoint(viewer.screenToMap(pt))
            if len(res) > 0:
                tpl = res.pop()
                if tpl != None:
                    layer, obj = tpl
                    #if ('attributes' in dir(obj)):
                    #    print 'Object attributes: ' + str(obj.attributes)
                    if layer.toggleObjectSelection(obj):
                        self._logic._getSheet().select(obj)
                    else:
                        self._logic._getSheet().unselect(obj)
                    viewer.drawLayerSelection(layer)
                        
                    #viewer._redraw()
                        
                #    print 'Object attributes: ' + str(obj.attributes)
                #if not obj.selected:
                #    self._logic._getSheet().select(obj)
                #else:
                #    self._logic._getSheet().unselect(obj)
                #obj.selected = not obj.selected
                #if ('attributes' in dir(obj)):
                #    print 'Object attributes: ' + str(obj.attributes)
        if mstate.buttons == 3 or mstate.buttons == 2:
            self.zooming = True
            pt = (float(mstate.X.abs), float(mstate.Y.abs))
            self.startPt = viewer.screenToMap(pt)
        if mstate.buttons == 4:
            self.moving = True
        
        
    def _onMouseReleased(self, _evt, _id):
        if self.zooming:
            self._logic.zoomToRect() 
        self.moving = False
        self.zooming = False