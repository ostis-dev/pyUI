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
Created on 15.12.2011

@author: Denis Koronchik
@version: 0.1
'''

import suit.core.render.engine as render_engine
import suit.core.render.mygui as mygui
import os
import math
import suit.core.kernel as core
import suit.core.keynodes as keynodes
import suit.core.objects as objects
import suit.core.sc_utils as sc_utils
from suit.core.event_handler import ScEventHandlerSetMember
import sc_core.pm
import sc_core.constants
import thread

_version_ = "0.1.0"
_name_ = "TaskPanel"


def initialize():
    core.task_panel = TaskPanel(core.Kernel.getSingleton())
    core.task_panel.setEnabled(True)
    core.task_panel.setVisible(True)


def shutdown():
    core.task_panel.delete()
    core.task_panel = None


class TaskItem(objects.ObjectOverlay):
    """Class that realize viewed item for task in task panel
    """
    def __init__(self, _container, kernel):
        objects.ObjectOverlay.__init__(self)
        self.kernel = kernel
        self._widget = _container.createWidgetT("Button", "Button",
                                               mygui.IntCoord(0, 0, 0, 0),
                                               mygui.Align())
        self._widget.setVisible(False)
        self._widget.setNeedMouseFocus(False)
        self.autoSize = False

    def _updateView(self):
        if self.needLocalizationUpdate:
            session = self.kernel.session()
            _caption = "#aaaaaaunknown"
            # get question class
            it = session.create_iterator(session.sc_constraint_new(sc_core.constants.CONSTR_3_a_a_f,
                                                               sc_core.pm.SC_N_CONST,
                                                               sc_core.pm.SC_A_CONST | sc_core.pm.SC_POS,
                                                               self._getScAddr()), True)
            while not it.is_over():
                _class = it.value(0)
                if sc_utils.checkIncToSets(session, _class, [keynodes.questions._class], sc_core.pm.SC_CONST):
                    _caption = sc_utils.getLocalizedIdentifier(core.Kernel.session(), _class)[0]
                    if len(_caption) == 0:
                        _caption = "#aaaaaaunknown"
                    break

                it.next()
            self.setText(_caption)
            self.needLocalizationUpdate = False

        objects.ObjectOverlay._updateView(self)

    def setInitiated(self):
        self._widget.setTextColour(mygui.Colour.Black)

    def setActive(self):
        self._widget.setTextColour(mygui.Colour.Blue)

    def setFinished(self):
        self._widget.setTextColour(mygui.Colour.Red)

    def setSuccessful(self):
        self._widget.setTextColour(mygui.Colour.Green)


class TaskPanel(objects.ObjectOverlay):
    """Class that realize task panel
    """
    def __init__(self, kernel):
        objects.ObjectOverlay.__init__(self)
        self.kernel = kernel
        self.kernel.registerOperation(ScEventHandlerSetMember(u"операция вывода вопросов на панель задач",
                                                         keynodes.questions.question,
                                                         self.registerNewTask, []))
        self.height = 400
        self.width = 250
        self.itemSize = (self.width - 16, 30)
        self.itemContainer = None  # container that contain buttons
        self.addr2item = {}        # map to translate sc_addr to item
        self.item2addr = {}        # map to translate item to sc_addr
        self.items = []
        self.maxItems = 20
        self.offset = 0
        self.createControls()
        self.registerQuestionEvents()
        self.setPosition((render_engine.Window.width - self.width,
                         (render_engine.Window.height - self.height) / 2))
        self.setScale((self.width, self.height))
        self.needItemsUpdate = False
        self.lock = thread.allocate_lock()
        self.appendQueue = []

    def registerNewTask(self, _params, _segment):
        session = self.kernel.session()
        questionNode = session.search_one_shot(session.sc_constraint_new(sc_core.constants.CONSTR_5_f_a_a_a_f,
                                                                        keynodes.questions.question,
                                                                        sc_core.pm.SC_A_CONST,
                                                                        sc_core.pm.SC_N_CONST,
                                                                        sc_core.pm.SC_A_CONST,
                                                                        _params), True, 5)
        self.addTask(questionNode[2])

    def createControls(self):
        """Create controls that will used by panel
        """
        self._widget = render_engine.Gui.createWidgetT("Window", "Panel", mygui.IntCoord(0, 0, 0, 0),
                                                       mygui.Align(), "Popup")
        self.itemContainer = self._widget.createWidgetT("Window", "WindowPanel_Container",
                                                          mygui.IntCoord(5, 25, self.width - 10, self.height - 50),
                                                          mygui.Align())

    def registerQuestionEvents(self):
        states = [(keynodes.questions.initiated, self.makeInitiated),
                      (keynodes.questions.active, self.makeActive),
                      (keynodes.questions.finished, self.makeFinished),
                      (keynodes.questions.succesful, self.makeSuccessful)]
        session = self.kernel.session()
        qMap = {}
        for q in states:
            qMap[session.get_idtf(q[0])] = q
        for statement in qMap.keys():
            print statement
            self.kernel.registerOperation(ScEventHandlerSetMember(unicode(statement),
                                                                  qMap[statement][0],
                                                                  qMap[statement][1], []))

    def _update(self, timeSinceLastFrame):
        """Update notification
        @param timeSinceLastFrame:    time since last update in ms
        @type timeSinceLastFrame:    float
        """
        with self.lock:
            objects.ObjectOverlay._update(self, timeSinceLastFrame)
            if self.needItemsUpdate:
                self.needItemsUpdate = False
                self._updateItems()

    def _checkPoint(self, _point):
        res = objects.ObjectOverlay._checkPoint(self, _point)
        if not res:
            return False
        # check if point in child object, if it True, then return False
        for item in self.item2addr.keys():
            if item._checkPoint(_point):
                return False
        return res

    def addTask(self, _task_node):
        """Add new task into list
        @param _task_node: sc-node that designate task
        @type _task_node: sc_global_addr
        """
        with self.lock:
            if self.addr2item.has_key(str(_task_node.this)):
                raise Exception("Task node %s already exist" % str(_task_node))
            item = TaskItem(self.itemContainer, self.kernel)
            item._setScAddr(_task_node)
            self.addr2item[str(_task_node.this)] = item
            self.item2addr[item] = _task_node
            self.items.insert(0, item)
            item.setVisible(self.isVisible())
            item.setEnabled(self.isEnabled())
            if len(self.items) > self.maxItems:
                item = self.items.pop()
                addr = self.item2addr.pop(item)
                self.addr2item.pop(str(addr.this))
            self.needItemsUpdate = True

    def removeTask(self, _task_node):
        """Remove task into list
        @param _task_node: sc-node that designate task
        @type _task_node: sc_global_addr
        """
        pass

    def _updateItems(self):
        """Update all items
        """
        idx = 0
        for item in self.items:
            item.setPosition((3, idx * (5 + self.itemSize[1])))
            item.setScale(self.itemSize)
            idx += 1

    def setEnabled(self, _value):
        with self.lock:
            objects.ObjectOverlay.setEnabled(self, _value)
            for item in self.item2addr.keys():
                item.setEnabled(_value)

    def setVisible(self, _value):
        with self.lock:
            objects.ObjectOverlay.setVisible(self, _value)
            for item in self.item2addr.keys():
                item.setVisible(_value)

    def makeInitiated(self, _params, *args, **kwargs):
        with self.lock:
            session = self.kernel.session()
            questionNode = session.search_one_shot(session.sc_constraint_new(sc_core.constants.CONSTR_5_f_a_a_a_f,
                                                                            keynodes.questions.initiated,
                                                                            sc_core.pm.SC_A_CONST,
                                                                            sc_core.pm.SC_N_CONST,
                                                                            sc_core.pm.SC_A_CONST,
                                                                            _params), True, 5)
            item = self.addr2item.get(str(questionNode[2].this), None)
            if item:
                item.setInitiated()

    def makeActive(self, _params, *args, **kwargs):
        with self.lock:
            session = self.kernel.session()
            questionNode = session.search_one_shot(session.sc_constraint_new(sc_core.constants.CONSTR_5_f_a_a_a_f,
                                                                            keynodes.questions.active,
                                                                            sc_core.pm.SC_A_CONST,
                                                                            sc_core.pm.SC_N_CONST,
                                                                            sc_core.pm.SC_A_CONST,
                                                                            _params), True, 5)
            item = self.addr2item.get(str(questionNode[2].this), None)
            if item:
                item.setActive()

    def makeFinished(self, _params, *args, **kwargs):
        with self.lock:
            session = self.kernel.session()
            questionNode = session.search_one_shot(session.sc_constraint_new(sc_core.constants.CONSTR_5_f_a_a_a_f,
                                                                            keynodes.questions.finished,
                                                                            sc_core.pm.SC_A_CONST,
                                                                            sc_core.pm.SC_N_CONST,
                                                                            sc_core.pm.SC_A_CONST,
                                                                            _params), True, 5)
            item = self.addr2item.get(str(questionNode[2].this), None)
            if item:
                item.setFinished()

    def makeSuccessful(self, _params, *args, **kwargs):
        with self.lock:
            session = self.kernel.session()
            questionNode = session.search_one_shot(session.sc_constraint_new(sc_core.constants.CONSTR_5_f_a_a_a_f,
                                                                            keynodes.questions.succesful,
                                                                            sc_core.pm.SC_A_CONST,
                                                                            sc_core.pm.SC_N_CONST,
                                                                            sc_core.pm.SC_A_CONST,
                                                                            _params), True, 5)
            item = self.addr2item.get(str(questionNode[2].this), None)
            if item:
                item.setSuccessful()
