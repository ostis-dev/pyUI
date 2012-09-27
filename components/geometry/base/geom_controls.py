
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
Created on 12.02.2012
@author: Denis Koronchik
'''

from suit.core.objects import ObjectOverlay
import suit.core.render.engine as render_engine
import suit.core.render.mygui as mygui

class ObjectInfoPanel(ObjectOverlay):
    
    def __init__(self):
        ObjectOverlay.__init__(self)
        
        self.width = 250
        self.height = 450
        self._widget = render_engine.Gui.createWidgetT("Window", "Panel",
                                                        mygui.IntCoord(-10, (render_engine.Window.height - self.height) / 2,
                                                                       self.width, self.height),
                                                        mygui.Align())
        self.infoText = self._widget.createWidgetT("StaticText", "StaticText",
                                                   mygui.IntCoord(15, 15, self.width - 30, self.height - 30),
                                                   mygui.Align())
        self.setVisible(False)
        self.setEnabled(True)
        
        self.object = None
        
        # flag to update information
        self.needInfoUpdate = False
    
    def __del__(self):
        ObjectOverlay.__del__(self)
    
    def delete(self):
        ObjectOverlay.delete(self)
    
    def setObject(self, _object):
        """Sets new object to show information
        """
        self.object = _object
        self.needInfoUpdate = True
        self.needViewUpdate = True
        
    def getObject(self):
        return self.object
        
    def update(self):
        self.needInfoUpdate = True
        self.needViewUpdate = True
    
    def _updateView(self):
        ObjectOverlay._updateView(self)
        
        if self.needInfoUpdate:
            if self.object is not None:
                self.infoText.setCaption(self.object.getPropertiesAsString())
            else:
                self.infoText.setCaption("")
            self.needInfoUpdate = False
        
    