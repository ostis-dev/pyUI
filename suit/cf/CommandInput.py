
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
Created on 24.12.2012

@author: Oleg Pischicov
'''
import suit.core.render.engine as render_engine
import suit.core.render.mygui as mygui
import suit.core.sc_utils as sc_utils
import suit.core.keynodes as keynodes
import suit.core.kernel as core
import sc_core.pm as sc
import sc_core.constants as sc_constants
import components.common.menu_cmds as menu_cmds
import components.common.menu as menu
class CommandInput:
    def __init__(self, _callback):
        """Constructor
        @param _callback: function that will be called when value
        input finished. This function takes two parameters - object, text value.
        @type _callback: function
        """
        self._callback = _callback
        self.menu_item = []
        self.result = []
        self.button = []
        self.list = None
        self.panel = None
        self.result_panel = None
        self.command_line = None
        self.kernel = core.Kernel.getSingleton()
        self.session = self.kernel.session()
        path = u""
        root = self.session.find_keynode_full_uri(u"/ui/menu/main menu")
        self.scgMenuItemToList(self.session, root, self.menu_item, path)
        self.createWidget()

    def createWidget(self):
        self.panel = render_engine.Gui.createWidgetT("Window", "Panel",
                                                     mygui.IntCoord(0, 30, 750, 520), mygui.Align(),
                                                     "Info", "")
        self.command_line = self.panel.createWidgetT("Edit", "Edit",
            mygui.IntCoord(20, 25, 710, 30), mygui.Align())
        self.command_line.subscribeEventSelectAccept(self, '_commandAccept')

    def _commandAccept(self, _widget):
        for item in self.menu_item:
            if item[1].find(unicode(self.command_line.getCaption())) is not -1:
                self.result.append(item)
        self.createButtonList(self.result)


    def destroyWidget(self):
        render_engine.Gui.destroyWidget(self.panel)
        self.panel = None
        self.command_line = None

    def scgMenuItemToList(self, session, sc_addr, menu_list, path):
        decomp = sc_utils.searchOneShotBinPairAttrToNode(session, sc_addr, keynodes.common.nrel_decomposition, sc.SC_CONST)
        value, is_system = sc_utils.getLocalizedIdentifier(core.Kernel.session(), sc_addr)
        unicode(value)
        path = path + u" -> " + value

        if decomp is not None:
            it = session.create_iterator(session.sc_constraint_new(sc_constants.CONSTR_3_f_a_a,
                decomp,
                sc.SC_A_CONST | sc.SC_POS,
                sc.SC_N_CONST), True)
            while not it.is_over():
                item_addr = it.value(2)
                self.scgMenuItemToList(session, item_addr, menu_list, path)
                it.next()
        else:
            menu_list.append([sc_addr, path])

    def createButtonList(self, menu_item):

        self.types_list = self.panel.createWidgetT("List", "List", mygui.IntCoord(10, 70, 680, 400), mygui.Align())
        self.types_list.subscribeEventChangePosition(self, 'item_selected')
        self.types_list.removeAllItems()
        for title in menu_item:
          self.types_list.addItem(title[1])
        self.types_list.clearIndexSelected()

    def item_selected(self, _widget, _idx):
        command = menu.SCgMenuItem(None, self.result[_idx][0], None)
        menu_cmds.start_menu_cmd(command)
        print _idx
        self.destroyWidget()
