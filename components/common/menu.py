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
Created on 21.10.2009

@author: Denis Koronchik
            Max Kaskevich
'''

import sys
import suit.core.kernel as core
import suit.core.objects as objects
import sc_core.constants as sc_constants
import sc_core.pm as sc
import ogre.io.OIS as ois
import ogre.renderer.OGRE as ogre
import suit.core.render.mygui as mygui
import suit.core.layout.LayoutGroup as layoutGroup
import suit.core.layout.LayoutGroupLine as layoutGroupLine
import suit.core.keynodes as keynodes
import suit.core.render.engine as render_engine
import menu_cmds
import suit.core.sc_utils as sc_utils


# log manager
logManager = core.Kernel.getSingleton().logManager
# session
session = core.Kernel.session()
# kernel object
kernel = core.Kernel.getSingleton()

session = kernel.session()
session.open_segment(u"/ui/menu")
main_menu				=	session.find_keynode_full_uri(u"/ui/menu/main menu")

menu_root = None
menu_layout_group = None

_version_   =   "0.2.0"
_name_      =   "Menu"

def initialize():
    # building menu
    _buildMenu()

    global menu_root
    global menu_layout_group
    
    # layout created menu 
    menu_layout_group = SCgMenuLayoutGroup(menu_root)
    menu_root.callBackExpand = menu_layout_group._onExpand
    menu_layout_group._layout(True)
    
    

def shutdown():
    global menu_root
    global menu_layout_group
    menu_root.delete()
    menu_layout_group = None
    menu_root = None
    


###################
# Generating menu #
###################
def _buildMenu():
    """Builds menu from sc memory
    """
    global menu_root
    menu_root = SCgMenuItem(u"", main_menu, None)
    
    
class Menu(objects.ObjectOverlay):
    """Class that implement main window menu
    @author: Max Kaskevich, Denis Koronchik
    """

    def __init__(self, caption = "Unknown"):
        '''
        Constructor
        '''
        objects.ObjectOverlay.__init__(self)
        self._color = None
        
        #menu-button 
        self.button = None
        self.icon = None
        self._skin = "MenuItem"
        self._icon_name = None
        
        self._icon_size = 15
        #menu-button position
        #don`t use __view position methods because __view can be destroyed in method "hide()"
        
        #callbacks(should be functions with arg Menu)
        self.callBackSetFocus = None
        self.callBackLostFocus = None
#        self.callBackRun = None
        self.callBackExpand = None
        
        #states
        self.__showed = False
        self.__draged = False
        self.__dragpoint = None
        self.atom = None
        self.question = False
        
        """self._move_time = 0.15
        self._auto_move = True
        self._auto_move_pos = None
        self._move_dt   = self._move_time"""
        self.autoSize = False
        
        self.position = (0, 0)
        self.scale = (10, 14)
        
        self.textUpdateImpl = self._textUpdateImpl
       
    def __del__(self):
        '''
        Destructor
        '''
        objects.ObjectOverlay.__del__(self)
        #if self.button:
            #self.__gui.destroyWidget(self.button)
        
    def __setActions(self):
        """set events listeners
        """
        if self.button:
            if self.callBackSetFocus:
                self.button.subscribeEventMouseSetFocus(self, "setFocus")
                self.button.subscribeEventKeySetFocus(self, "setFocus")
            
            if self.callBackLostFocus:
                self.button.subscribeEventMouseLostFocus(self,"_lostFocus")
                self.button.subscribeEventKeyLostFocus(self,"_lostFocus")
            
            self.button.subscribeEventMouseButtonClick(self,'_expandOrRun')
            #self.button.subscribeEventMouseDrag(self,'_drag')
            
    def _setFocus(self, widget):
        self.callBackSetFocus(self)

    def _lostFocus(self, widget):
        self.callBackLostFocus(self)
    
    def _expandOrRun(self, widget):
        """call run, expand or drop button in depends of states
        """
        if self.__draged:
            #drop
            self.__dragpoint = None
            self.__draged = False
        else:
            #if left alt pressed
            #if core.Kernel.getSingleton().oisKeyboard.isKeyDown(ois.KC_LMENU):
            
            #call expand
            if self.callBackExpand:
                self.callBackExpand(self)
#            else:
#                #call run
#                if self.callBackRun:
#                    self.callBackRun(self)

    def _textUpdateImpl(self):
        if self.button is not None:
            self.button.setCaption(self.getText())
            self.calculateAutoSize()
            self.needTextUpdate = False

    def _updateView(self):
        """Updates view representation of object
        """       
        """if self.needPositionUpdate:
            if self.button is not None:
                if self._auto_move:
                    self._move_dt = 0.0
                    old_pos = self.button.getPosition()
                    self._auto_move_pos = (old_pos.left, old_pos.top)
                else:
                    self.button.setPosition(self.position[0], self.position[1])
            self.needPositionUpdate = False"""           
        if self.needScaleUpdate:
            if self.button is not None:
                self.button.setSize(self.scale[0], self.scale[1])
                sz = max([0, min([self.scale[1] - 10, self._icon_size])])
                self.icon.setSize(sz, sz)
                self.icon.setPosition(5, int(max([(self.scale[1] - sz) / 2.0, 0])))
                self.needScaleUpdate = False
            
                menu_layout_group._layout(True)
                       
        objects.ObjectOverlay._updateView(self)
        
    def _update(self, _timeSinceLastFrame):
        """Updates object
        """
        objects.ObjectOverlay._update(self, _timeSinceLastFrame)
        
        # move object if need
        """if self._auto_move and self._move_dt < self._move_time and self.button is not None:
            self._move_dt += _timeSinceLastFrame
            self._move_dt = min([self._move_dt, self._move_time])
            prop = self._move_dt / self._move_time
            self.button.setPosition(int(self._auto_move_pos[0] + prop * (self.position[0] - self._auto_move_pos[0])),
                                     int(self._auto_move_pos[1] + prop * (self.position[1] - self._auto_move_pos[1])))
           """ 
            

    def setAlpha(self, _value):
        """Sets alpha value for item
        """
        if self.button is not None:
            self.button.setAlpha(_value)

    def show(self):
        """show button
        """
        if not self.__showed:
            self.button = render_engine.Gui.createWidgetT("Button",
                                                          self._skin,
                                                          mygui.IntCoord(self.position[0], self.position[1], self.scale[0], self.scale[1]),
                                                          mygui.Align(),
                                                          "Popup", "")
            self.icon = self.button.createWidgetT("StaticImage",
                                                  "StaticImage",
                                                  mygui.IntCoord(5, 5, 10, 10),
                                                  mygui.Align())
                
            self.icon.setNeedKeyFocus(False)
            self.icon.setNeedMouseFocus(False)
            
            if self._icon_name is not None:
                self.icon.setImageTexture(self._icon_name)
            
            if self.getText() is not None:
                self.button.setCaption(self.getText())
            self._widget = self.button
            self.calculateAutoSize()

            self.__setActions()
            self.__showed = True

        self.setEnabled(True)
        self.setVisible(True)
            
#            self.setScale((170, 22))
    
    def hide(self):
        """hide button
        """        
        self.setEnabled(False)
        self.setVisible(False)
        
        if self.__showed:
            render_engine.Gui.destroyWidget(self.button)
            self.__showed = False
            self.button = None
            
    def calculateAutoSize(self):
        """Set size of item to wrap caption
        """
        if self.button:
            tsize = self.button.getTextSize()
            self.setScale((tsize.width + 50, tsize.height + 10))
    
    def isShowed(self):
        return self.__showed
            
    def setCaption(self, caption):
        if self.button:
            self.button.setCaption(caption)  
            self.calculateAutoSize()


class SCgMenuItem(Menu):
    
    def __init__(self, _caption, _sc_addr, _parent):
        """Constructor
        @param _caption: menu item caption
        @type _caption: str
        @param _sc_addr: sc_addr of node that represents menu item
        @type _sc_addr: sc_addr
        @param _parent: parent item
        @type _parent: SCgMenuItem
        """
        Menu.__init__(self, _caption)
        self.childs = []
        #self.callBackExpand = self._expand
        self.visible = False
        self.parent = _parent
        
        self._color = None
               
        self._setScAddr(_sc_addr)
        # check atom flag
        self._checkAtom()       
        
        
    def __del__(self):
        """Destructor
        """
        Menu.__del__(self)
        
    def delete(self):
        Menu.delete(self)
                
    def _expandOrRun(self, widget):
        """Expands item or run event for atom class
        """
        Menu._expandOrRun(self, widget)
        if self.atom:
            try:
                self._run_event()
            except RuntimeError, exc:
                # FIXME: make more useful
                global logManager
                logManager.logError("Can't run event '%s': %s" % (self.getCaption(), str(exc)))
        
    def _run_event(self):
        """Runs event attached to menu item
        """
        menu_cmds.start_menu_cmd(self)
        
    
    def _apendChildItem(self, _item):
        """Appends child item
        @param _item: child item to append
        @type _item: SCgMenuItem  
        """
        if _item in self.childs:    
            raise RuntimeError("Item '%s' is already exists as child in item '%s'" % (item.getCaption(), self.getCaption()))
        self.childs.append(_item)
        _item.parent = self
    
    def _show(self):
        """Show menu items
        """
        if not self.visible:
            self._parse()
            for item in self.childs:
                item.show()
                
            # make items on this level transparent
            if self.parent is not None:
                for item in self.parent.childs:
                    if item is not self:
                        item.setAlpha(0.5)
        else:
            raise RuntimeWarning("Menu '%s' already showed" % self.getCaption())

        self.visible = True
        
    def _hide(self):
        """Hide menu items
        """
        if self.visible:
            for item in self.childs:
                item.hide()
            #self.childs = []
            self.visible = False
            
            # make items on this level visible
            if self.parent is not None:
                for item in self.parent.childs:
                    item.setAlpha(1.0)
            
        else:
            raise RuntimeWarning("Menu '%s' already hidden" % self.getCaption())
        
        
    def _parse(self):
        """Parse menu item from sc-memory
        @author: Denis Koronchik
        """
        if len(self.childs) > 0: return # do nothing
        
        
        current_translation = core.Kernel.getSingleton().getCurrentTranslation()
       
        # get child elements
        session = core.Kernel.session()
        #decomp = sc_utils.searchOneShotBinPairAttrFromNode(session, self._getScAddr(), keynodes.common.nrel_decomposition, sc.SC_CONST)
        decomp = sc_utils.searchOneShotBinPairAttrToNode(session, self._getScAddr(), keynodes.common.nrel_decomposition, sc.SC_CONST)
        
        # parse child items
        if decomp is not None:
            it = session.create_iterator(session.sc_constraint_new(sc_constants.CONSTR_3_f_a_a,
                                                                  decomp,
                                                                  sc.SC_A_CONST | sc.SC_POS,# | sc.SC_PERMANENT,
                                                                  sc.SC_N_CONST), True)
            while not it.is_over():
                item_addr = it.value(2)
               
                item = SCgMenuItem(None, it.value(2), self)
                item.setPosition(self.position)
                self.childs.append(item)
                
                it.next()
                

    def _checkAtom(self):
        """Checks if menu item is atom menu class
        """
        session = core.Kernel.session()
        self._skin = "MenuItem"
        self._color = "#ffffff"
        
        if sc_utils.checkIncToSets(session, self._getScAddr(), [keynodes.ui.atom_command], sc.SC_CONST):
            self.atom = True
            self._icon_name = sc_utils.getImageIdentifier(session, keynodes.ui.atom_command)
            
            # check if it is a question command
            if sc_utils.checkIncToSets(session, self._getScAddr(), [keynodes.ui.question_command], sc.SC_CONST):
                self.question = True
                self._icon_name = sc_utils.getImageIdentifier(session, keynodes.ui.question_command)
            return
        
        elif sc_utils.checkIncToSets(session, self._getScAddr(), [keynodes.ui.noatom_command], sc.SC_CONST):
            self.atom = False
            self._icon_name = sc_utils.getImageIdentifier(session, keynodes.ui.noatom_command)
            return
        else:   #object
            self.atom = False
            self.question = False
            return
        
        global logManager
        logManager.logWarning("Unknown atom class for a menu item '%s'" % self.getCaption())

    def setText(self, _text):
        Menu.setText(self, _text)
        
        self.setCaption(_text)
        
        
    def show(self):
        """Overloaded show message to control tooltips
        """
        Menu.show(self)
        
class SCgMenuLayoutGroup(layoutGroup.LayoutGroupOverlay, ogre.WindowEventListener):
    """Layouts menu by horizontal on window top
    """
    
    def __init__(self, _menuRoot):
        """Constructor
        """
        layoutGroup.LayoutGroupOverlay.__init__(self)
        ogre.WindowEventListener.__init__(self)
        
        # list of horizontal layout groups
        self.groups = {}    
        # render window size
        self._updateWindowBounds()
        
        self.item_height = None
        self.menu_root = _menuRoot
        self._onExpand(self.menu_root)
        
        
        # register listener for window events
#        ogre.WindowEventUtilities.addWindowEventListener(self.renderWindow, self)
        render_engine.registerWindowEventListener(self) 

        
    def __del__(self):
        """Destructor
        """
        layoutGroup.LayoutGroupOverlay.__del__(self)
#        ogre.WindowEventUtilities.removeWindowEventListener(self.renderWindow, self)
        render_engine.unregisterWindowEventListener(self)
        
    def _expandMain(self):
        """Expands main menu
        """
        self._onExpand(self.menu_root)
        
    def _apply(self):
        """Apply layout algorithm
        """
        for groups in self.groups.values():
            for group in groups:
                group._layout(True)
        layoutGroup.LayoutGroupOverlay._apply(self)
        
    def _onExpand(self, _menuItem):
        """Notification for item expand
        """
        
        # check if menu expanded
        if _menuItem.visible:
            self.groups.pop(_menuItem)
            # expanding child menus
            for item in _menuItem.childs:
                if self.groups.has_key(item):
                    self._onExpand(item)
            
            _menuItem._hide()
            return
        else:
            # hiding menus with the same level
            if _menuItem is not self.menu_root:
                for item in _menuItem.parent.childs:
                    if self.groups.has_key(item):
                        self._onExpand(item)
            # showing menu
            _menuItem._show()
        
        
        # update items
        for item in _menuItem.childs:
            item.calculateAutoSize()
            item.callBackExpand = self._onExpand
        
        # check if it's a menu root item
        if _menuItem is self.menu_root:
            # create group
            group = self._createGroupX((0, 0), self.width, layoutGroupLine.LayoutGroupLine2dX.Dir_pos, True)
            self.groups[_menuItem] = [group]
            width = 0
            y = 0
            # append items to groups
            for item in _menuItem.childs:
                sz = item.getScale()
                
                # store item height
                if self.item_height is None:
                    self.item_height = sz[1] 
                
                # create new group if we need
                if width + sz[0] > self.width:
                    y += sz[1]
                    group = self._createGroupX((0, y), self.width, 
                                               layoutGroupLine.LayoutGroupLine2dX.Dir_pos, True)
                    width = 0
                    self.groups[_menuItem].append(group)
                # calculate new width
                width += sz[0]
                group.appendObject(item)
            group.fit = False
    
        else:
            # getting maximum item width
            max_width = 0
            all_height = 0
            sizes = []
            for item in _menuItem.childs:
                item._updateView()  # not good, but it works, need to be redone
                sz = item.getScale()
                sizes.append(sz)
                max_width = max([max_width, sz[0]])
                all_height += sz[1]
                
            # @todo: resolve problem with long menu
            idx = 0
                       
            # if item not first level, then calculate optimal position
            if _menuItem.parent is not self.menu_root:
                sz = _menuItem.getScale()
                pos = _menuItem.getPosition()
                # calculate x position
                if pos[0] + sz[0] + max_width > self.width:
                    x = pos[0] - max_width
                else:
                    x = pos[0] + sz[0]
                # calculate y position
                if pos[1] + all_height > self.height:
                    y = self.height - all_height
                else:
                    y = pos[1]
            else:   # calculate optimal position for a first level menu items
                pos = _menuItem.getPosition()
                if pos[0] + max_width > self.width:
                    x = self.width - max_width
                else:
                    x = pos[0]  
            
                y = len(self.groups[self.menu_root]) * self.item_height
            
            group = self._createGroupY((x, y), self.height - y, 
                                       layoutGroupLine.LayoutGroupLine2dY.Dir_pos, False)
            self.groups[_menuItem] = [group]
            for item in _menuItem.childs:
                group.appendObject(item)
                item.setScale((max_width, sizes[idx][1]))
                idx += 1
                
            group._layout(True)

                
    
    def _updateWindowBounds(self):
        """Updates information about render window bounds 
        """
        self.width  =   render_engine.Window.width
        self.height =   render_engine.Window.height
        self.depth  =   render_engine.Window.depth
        self.left   =   render_engine.Window.left
        self.top    =   render_engine.Window.top
        
    def _regroup(self):
        """Regroup objects. 
        Change groups based on objects size and window width
        """
        self.hgroups = []
         
        
    def _createGroupX(self, _pos, _max_length, _dir, _fit):
        """Creates horizontal layout group
        @param _pos: group position
        @type _pos: tuple: (x, y)
        @param _max_length: maximum group length
        @type _max_length: int    
        @param _dir: layout direction
        @param _fit: fit object in length flag
        
        @return: created group  
        """
        group = layoutGroupLine.LayoutGroupLine2dX(_pos = _pos, _max_length = _max_length,
                                                   _direction = _dir, _fit = _fit, _dist = -1, 
                                                   _align = layoutGroupLine.LayoutGroupLine2dX.Align_center)
        return group
    
    def _createGroupY(self, _pos, _max_length, _dir, _fit):
        """Creates vertical layout group
        @param _pos: group position
        @type _pos: tuple: (x, y)
        @param _max_length: maximum group length
        @type _max_length: int    
        @param _dir: layout direction
        @param _fit: fit object in length flag
        
        @return: created group  
        """
        group = layoutGroupLine.LayoutGroupLine2dY(_pos = _pos, _max_length = _max_length,
                                                   _direction = _dir, _fit = _fit, _dist = -1)
        return group
        
        
    def windowResized(self, renderWindow):
        """Notification method for render window size changed
        """
        # updating window bounds
        self._updateWindowBounds()
        
        # regrouping objects
        self._regroup()
        
        # updating horizontal groups size and layout them
        for group in self.hgroups:
            group.max_length = width
            group._layout(True)
