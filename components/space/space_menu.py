
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
Created on 28.09.2009

@author: Maxim Kaskevich
'''
import suit.core.kernel as core
import ogre.renderer.OGRE as ogre
import suit.core.render.mygui as mygui
import math
import ogre.io.OIS as ois


def initialize():
    pass
    
def shutdown():
    pass

class Menu(object):
    '''
    menu class
    '''

    def __init__(self, caption = "Menu"):
        '''
        Constructor
        '''
        self.__gui = core.Kernel.getSingleton().gui
        
        self.__caption = caption
        
        #menu-button 
        self.__view = None
        #menu-button position
        #don`t use __view position methods because __view can be destroyed in method "hide()"
        self.__pos = 0,0
        
        #callbacks(should be functions with arg Menu)
        self.callBackSetFocus = None
        self.callBackLostFocus = None
        self.callBackRun = None
        self.callBackExpand = None
        
        #states
        self.__showed = False
        self.__draged = False
        self.__dragpoint = None
        
    def __del__(self):
        '''
        Destructor
        '''
        #if self.__view:
            #self.__gui.destroyWidget(self.__view)
        
        
    def __setActions(self):
        """set events listeners
        """
        if self.__view:
            if self.callBackSetFocus:
                self.__view.subscribeEventMouseSetFocus(self,"setFocus")
                self.__view.subscribeEventKeySetFocus(self,"setFocus")
            
            if self.callBackLostFocus:
                self.__view.subscribeEventMouseLostFocus(self,"_lostFocus")
                self.__view.subscribeEventKeyLostFocus(self,"_lostFocus")
            
            self.__view.subscribeEventMouseButtonClick(self,'_expandOrRun')
            self.__view.subscribeEventMouseDrag(self,'_drag')
            
    def _setFocus(self, widget):
        self.callBackSetFocus(self)

    def _lostFocus(self, widget):
        self.callBackLostFocus(self)

    def _drag(self,widget, v1, v2):
        if self.__dragpoint:
            #move button use dragpoint
            #its doing for button left top corner don`t jump to mouse position when draging
            # calculating origin based on drag point
            self.__pos = v1 - self.__dragpoint[0],v2-self.__dragpoint[1]
            self.__view.setPosition(self.__pos[0],self.__pos[1])
        else:
            #take point relate to left top corner in which button starts to drag
            self.__dragpoint = v1-self.__pos[0],v2-self.__pos[1]
        self.__draged = True
        pass
    
    def _expandOrRun(self, widget):
        """call run, expand or drop button in depends of states
        """
        if self.__draged:
            #drop
            self.__dragpoint = None
            self.__draged = False
        else:
            #if left alt pressed
            if core.Kernel.getSingleton().oisKeyboard.isKeyDown(ois.KC_LMENU):
                #call expand
                if self.callBackExpand:
                    self.callBackExpand(self)
            else:
                #call run
                if self.callBackRun:
                    self.callBackRun(self)

    def show(self):
        """show button
        """
        if not self.__showed:
            self.__view = self.__gui.createWidgetT("Button", "Button", mygui.IntCoord(self.__pos[0], self.__pos[1], 10, 10), mygui.Align(),"Popup","")
            self.__view.setCaption(self.__caption)
            tsize = self.__view.getTextSize()
            self.__view.setSize(tsize.width + 10,tsize.height+5)
            self.__setActions()
            self.__showed = True
    
    def hide(self):
        """hide button
        """
        if self.__showed:
            self.__gui.destroyWidget(self.__view)
            self.__showed = False
    
    def isShowed(self):
        return self.__showed
    
    def setPosition(self, x, y = None):
        """set button position
        @param x: x coord or tuple of x and y coords
        @type x: int or tuple
        @param y: y coord
        @type y: int
        """
        if y:
            self.__pos = x,y
        else:
            self.__pos = x
            
        if self.__view:
            self.__view.setPosition(self.__pos[0], self.__pos[1])
        
    def getPosition(self):
        return self.__pos
    
    def setCaption(self, caption):
        self.__caption = caption
        if self.__view:
            self.__view.setCaption(self.__caption)
        
    def getCaption(self):
        return self.__caption
    