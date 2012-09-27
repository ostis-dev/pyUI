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
import os, math
import suit.core.kernel as core
import suit.core.keynodes as keynodes
import suit.core.objects as objects
import suit.core.sc_utils as sc_utils
from suit.core.event_handler import ScEventHandlerSetMember
import sc_core.pm, sc_core.constants
import thread

_task_panel = None

_version_   =   "0.1.0"
_name_      =   "TaskPanel"

def initialize():
    global _task_panel
    
    _task_panel = TaskPanel()
    core.task_panel = _task_panel
    _task_panel.setEnabled(True)
    _task_panel.setVisible(True)
    
    kernel = core.Kernel.getSingleton()
    kernel.registerOperation(ScEventHandlerSetMember(u"операция вывода вопросов на панель задач",
                                                     keynodes.questions.question,
                                                     appendTask, []))

def shutdown():
    
    global _task_panel
    _task_panel.delete()
    _task_panel = None
    
    
def appendTask(_params, _segment):
    # trying to find question node
    session = core.Kernel.session()
    question_node = session.search_one_shot(session.sc_constraint_new(sc_core.constants.CONSTR_5_f_a_a_a_f,
                                                                     keynodes.questions.question,
                                                                     sc_core.pm.SC_A_CONST,
                                                                     sc_core.pm.SC_N_CONST,
                                                                     sc_core.pm.SC_A_CONST,
                                                                     _params), True, 5)
    
    question_node = question_node[2]
    _task_panel.addTask(question_node)
    
class TaskItem(objects.ObjectOverlay):
    """Class that realize viewed item for task in task panel 
    """
    def __init__(self, _container):
        objects.ObjectOverlay.__init__(self)
        
        self._widget = _container.createWidgetT("Button", "Button",
                                               mygui.IntCoord(0, 0, 0, 0),
                                               mygui.Align())
        self._widget.setVisible(False)
        
        self.autoSize = False
        
    def __del__(self):
        objects.ObjectOverlay.__del__(self)
            
    def _update(self, timeSinceLastFrame):
        objects.ObjectOverlay._update(self, timeSinceLastFrame)
               
    def _updateView(self):
        if self.needLocalizationUpdate:
            kernel = core.Kernel.getSingleton()
            session = core.Kernel.session()
            _caption = "#aaaaaaunknown"
            # get question class
            it = session.create_iterator(session.sc_constraint_new(sc_core.constants.CONSTR_3_a_a_f,
                                                               sc_core.pm.SC_N_CONST,
                                                               sc_core.pm.SC_A_CONST | sc_core.pm.SC_POS,
                                                               self._getScAddr()), True)
            while not it.is_over():
                _class = it.value(0)
                if sc_utils.checkIncToSets(session, _class, [keynodes.questions._class], sc_core.pm.SC_CONST):
                    _caption = sc_utils.getLocalizedIdentifier(core.Kernel.session(), _class)
                    if len(_caption) == 0:
                        _caption = "#aaaaaaunknown"
                    break
                    
                it.next()
            self.setText(_caption)
            self.needLocalizationUpdate = False
        
        objects.ObjectOverlay._updateView(self)
    

class TaskPanel(objects.ObjectOverlay):
    """Class that realize task panel
    """
    def __init__(self):
        objects.ObjectOverlay.__init__(self)
        
        self.height = 400
        self.width = 250
        
        self.itemSize = (self.width - 16, 30)
        
        self.itemContainer = None # container that contain buttons
       
        self.addr2item = {}       # map to translate sc_addr to item
        self.item2addr = {}       # map to translate item to sc_addr
        self.items = []
        self.maxItems = 20
        
        self.offset = 0
        
        self.createControls()
        
        self.setPosition((render_engine.Window.width - self.width,
                         (render_engine.Window.height - self.height) / 2))
        self.setScale((self.width, self.height))
        
        self.needItemsUpdate = False
        
        self.lock = thread.allocate_lock()
        self.appendQueue = []

    def __del__(self):
        objects.ObjectOverlay.__del__(self)
    
    def createControls(self):
        """Create controls that will used by panel
        """
        self._widget = render_engine.Gui.createWidgetT("Window", "Panel",
                                                    mygui.IntCoord(0, 0, 0, 0),
                                                    mygui.Align(),
                                                    "Popup")
        self._widget.setVisible(False)
        
        self.itemContainer = self._widget.createWidgetT("Window", "WindowPanel_Container",
                                                          mygui.IntCoord(5, 25, self.width - 10, self.height - 50),
                                                          mygui.Align())
         
    def delete(self):
        """Deletes window panel
        """
        objects.ObjectOverlay.delete(self)
    
    def _update(self, timeSinceLastFrame):
        """Update notification
        @param timeSinceLastFrame:    time since last update in ms
        @type timeSinceLastFrame:    float
        """
        self.lock.acquire()            
        objects.ObjectOverlay._update(self, timeSinceLastFrame)
        
        if self.needItemsUpdate:
            self.needItemsUpdate = False
            self._updateItems()
            
        self.lock.release() 
        
    def _updateView(self):
        objects.ObjectOverlay._updateView(self)
        
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
        self.lock.acquire()
        if self.addr2item.has_key(str(_task_node.this)):
            self.lock.release() 
            raise Exception("Task node %s already exist" % str(_task_node))
        
        item = TaskItem(self.itemContainer)
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
        
        self.lock.release() 
    
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
        self.lock.acquire()
        objects.ObjectOverlay.setEnabled(self, _value)

        for item in self.item2addr.keys():
            item.setEnabled(_value)
            
        self.lock.release() 
            
    def setVisible(self, _value):
        self.lock.acquire()
        objects.ObjectOverlay.setVisible(self, _value)
        
        for item in self.item2addr.keys():
            item.setVisible(_value)
        self.lock.release() 