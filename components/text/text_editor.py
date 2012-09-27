
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
Created on 15.05.2010

@author: Denis Koronchick
'''

from suit.core.objects import BaseLogic
import suit.core.render.mygui as mygui
import suit.core.kernel as core
import suit.core.objects as objects
import suit.core.render.engine as render_engine
from text_viewer import TextViewer

class TextEditor(BaseLogic):
    
    def __init__(self):
        BaseLogic.__init__(self)
        
        # setting new logic for a sheet if viewer already exists
        self.__viewer = TextViewer()
        self.__viewer._createArea = self._createEditText
          
    def __del__(self):
        BaseLogic.__del__(self)
        
    def delete(self):
        BaseLogic.delete(self)
        
        self.__viewer.delete()
        
    def _setSheet(self, _sheet):
        BaseLogic._setSheet(self, _sheet)
        
        self.__viewer._setSheet(_sheet)
        
        _sheet.eventRootChanged = self._onRootChanged
        _sheet.eventUpdate = self._onUpdate
        
        
    def _onRootChanged(self, _isRoot):
        """Root changing event callback
        """
        self.__viewer._onRootChanged(_isRoot)
    
    def _onUpdate(self, _timeSinceLastFrame):
        BaseLogic._update(self, _timeSinceLastFrame)
        
        self.__viewer._onUpdate(_timeSinceLastFrame)
        
    def _onContentUpdate(self):
        
        import suit.core.keynodes as keynodes
        import suit.core.sc_utils as sc_utils
        sheet = self._getSheet()
        
        sheet.content_type = objects.ObjectSheet.CT_String
        #sheet.content_data = str(self.__viewer.widget.getOnlyText())
        sheet.content_data = unicode(self.__viewer.widget.getCaption()).encode('cp1251')
        sheet.content_format = keynodes.ui.format_string        
        
    def _createEditText(self):
        """Create widget to edit text value
        """
        self.__viewer.widget = render_engine.Gui.createWidgetT("Edit", "Edit",
                                                          mygui.IntCoord(0, 0, 91, 91),
                                                          mygui.Align(mygui.ALIGN_VSTRETCH),
                                                          "Main")
        self.__viewer.widget.setVisible(False)
        self.__viewer.widget.setTextColour(mygui.Colour(0.0, 0.0, 0.0, 1.0))
        self.__viewer.widget.setEditMultiLine(True)
     
    