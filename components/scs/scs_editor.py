
'''
Created on xx.xx.2012

@author: dred
'''

from suit.core.objects import BaseLogic
import suit.core.render.mygui as mygui
import suit.core.kernel as core
import suit.core.objects as objects
import suit.core.render.engine as render_engine
from scs_viewer import SCsViewer

class SCsEditor(BaseLogic):

    def __init__(self):
        BaseLogic.__init__(self)

        # setting new logic for a sheet if viewer already exists
        self.__viewer = SCsViewer()
        self.__viewer._createArea = self._createEditSCs

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
        sheet.content_data = unicode(self.__viewer.widget.getCaption()).encode('utf8')
        sheet.content_format = keynodes.ui.format_scsx

    def _createEditSCs(self):
        """Create widget to edit SCs value
        """
        self.__viewer.widget = render_engine.Gui.createWidgetT("Edit", "Edit",
            mygui.IntCoord(0, 0, 91, 91),
            mygui.Align(mygui.ALIGN_VSTRETCH),
            "Main")
        self.__viewer.widget.setVisible(False)
        self.__viewer.widget.setTextColour(mygui.Colour(0.0, 0.0, 0.0, 1.0))
        self.__viewer.widget.setEditMultiLine(True)