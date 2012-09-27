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


import ogre.renderer.OGRE as ogre
import ogre.io.OIS as OIS
import array
import code
import sys
import suit.core.kernel as core
import suit.core.render.mygui as mygui
import re
 
 
# resource group manager
resourceGroupManager = None
console = None

stdin = None
stdout = None
stderr = None

def getResourceLocation():
    """Return resource location folder
    """
    return core.Kernel.getResourceLocation() + 'console' 

def getResourceGroup():
    """Return resource group name
    """
    return 'console'
 
def initialize():
    core.logMessage_init('Console')
 
    
    # initialize console object
    global console, stdin, stdout, stderr
    stdout = sys.stdout
    stderr = sys.stderr
    console = Console(ogre.Root.getSingleton())
    #sys.stdout = console
    #sys.stderr = console
    # register listener
    core.Kernel.getSingleton().addKeyboardListener(console)
 
def shutdown():
    pass
 
 
## PythonOgre Console
# Usage:
#   console = console.Console(self.root)
#   console.addLocals({'root':self.root})
#   console.show()
#   # Then inject the keys pressed in your keyboard handler
#   console.keyPressed(evt)
#
# PythonOgre Console is sort of singleton. All instances of Console objects
# share the same state. So simply create a console object anywhere you wish
# to use it and they will all point to whichever one was created first.
#
## TODO
# - Key repeating
# - PGUP PGDOWN history viewing
# - Linewrap if prompt too long
# - Write history to file
# - Read history from file
# - Make font look better
 
class Console(ogre.FrameListener, OIS.KeyListener):
    CONSOLE_LINE_LENGTH = 85
    CONSOLE_LINE_COUNT = 15
    __shared_state = {}
    
    CM_Python, CM_Operations, CM_Count = range(3)
    ModeName = ["#CC3333Python", "#33CC33Operations"]
 
    def __init__(self, root = None):
        self.__dict__ = self.__shared_state
 
        ogre.FrameListener.__init__(self)
 
        if root:
            root.addFrameListener(self)
        self.root = root
 
        if 'isSetup' not in self.__dict__:
            self.isSetup = True
        else:
            return
 
        self.currentInputHistory = -1
        self.inputHistory = []
        self.outputHistory = []
        self.keyBinds = {OIS.KC_UP: self._prevCommand,
                         OIS.KC_DOWN: self._nextCommand}
        
        self.interpreter = code.InteractiveConsole({'console':self})
 
        
        self.gui = core.Kernel.getSingleton().gui
        rwnd = core.Kernel.getSingleton().getRenderWindow()
        
        self.window = self.gui.createWidgetT("Window", "Panel", mygui.IntCoord(0, 0, rwnd.getWidth(), 250), mygui.Align(), "Info", '')
        self.window.setAlpha(0.8)
        
        # create control to select mode
        self.modeCombo = self.window.createWidgetT("ComboBox", "ComboBox", mygui.IntCoord(self.window.getWidth() - 150, self.window.getHeight() - 30, 143, 20), mygui.Align())
        self.modeCombo.setComboModeDrop(True)
        for mode in xrange(self.CM_Count):
            self.modeCombo.addItem(self.ModeName[mode])
        self.mode = self.CM_Python
        self.modeCombo.setIndexSelected(self.mode)
        self.modeCombo.subscribeEventAccept(self, "_changeMode")
        
        self.input = self.window.createWidgetT("Edit", "Edit", mygui.IntCoord(7, self.window.getHeight() - 30, self.window.getWidth() - 160, 20),mygui.Align())
        self.output = self.window.createWidgetT("Edit", "EditStretch", mygui.IntCoord(7, 7, self.window.getWidth() - 15, 210), mygui.Align())
        self.output.setEditReadOnly(True)
        self.output.setEditMultiLine(True)
        self.output.setVisibleVScroll(True)
        self.output.setVisibleHScroll(True)
        self.output.setTextAlign(mygui.Align(mygui.ALIGN_LEFT_BOTTOM))
        
        
        self.input.subscribeEventSelectAccept(self, '_input')
        
        self.moveDir = -1
        self.height = -1.1
        self.moveTime = 0.5 # time in seconds to hide/show console
        self.visible = False
        
        
        self.colors = {"(>>>)": "#3377CC>>>"}
        
    def __del__(self):
        """Destroying interface
        """
        self.root.removeFrameListener(self)
        self.gui.destroyWidget(self.window)
        
    def _changeMode(self, combo, idx):
        """Sets new console mode
        """
        self.mode = self.modeCombo.getIndexSelected()
        self.write("Console mode switched to %s#FFFFFF" % (self.ModeName[self.mode]))
       
    def _input(self, _sender):
        """Process input data
        """
        cmd = unicode(self.input.getCaption())
        if len(cmd) <= 0:
            return 
    
        # processing command
        self.inputHistory.insert(0, cmd)
        self.currentInputHistory = -1
        self.input.setCaption('')
        
        self.write(cmd, True)
        self._enableSysRedirect()
        if self.mode == self.CM_Python:
            self.interpreter.push(cmd)
        elif self.mode == self.CM_Operations:
            core.Kernel.getSingleton().runOperation_str(cmd)
        self._disableSysRedirect()

    def _enableSysRedirect(self):
        """Redirects system stdout and stderr to console  
        """ 
        self._stderr = sys.stderr
        self._stdout = sys.stdout
        
        sys.stderr = sys.stdout = self
        
    def _disableSysRedirect(self):
        """Disables system stdout and stderr redirection
        """
        sys.stderr = self._stderr
        sys.stdout = self._stdout
        
    def _prevCommand(self):
        """Going to previous command
        """
        if self.currentInputHistory < len(self.inputHistory):
            self.currentInputHistory += 1
            
        if self.currentInputHistory <> len(self.inputHistory):
            self.input.setCaption(self.inputHistory[self.currentInputHistory])
        elif self.currentInputHistory == -1:
            self.input.setCaption('')
    
    def _nextCommand(self):
        """Going to next command
        """
        if self.currentInputHistory >= 0:
            self.currentInputHistory -= 1
            
        if self.currentInputHistory <> -1:
            self.input.setCaption(self.inputHistory[self.currentInputHistory])
        elif self.currentInputHistory == -1:
            self.input.setCaption('')
        
    def _colorize(self, text):
        """Apply colors to output string
        """
        return text # temporary
    
        for templ in self.colors.keys():
            templPat = re.compile(templ, re.UNICODE | re.DOTALL)
            text = templPat.sub(self.colors[templ], text)
        
        return text
        
    def hide(self):
        # hiding console 
        self.moveDir = -1
        self.height = 0.0
        mygui.InputManager.getInstance().resetKeyFocusWidget(self.input)
    
    def show(self):
        # showing console
        self.moveDir = 1
        self.height = -1.0
        mygui.InputManager.getInstance().setKeyFocusWidget(self.input)
        
    def frameStarted(self, evt):
        
        if self.moveDir != 0:
            # updating console movements if we need
            if self.height > 0:
                self.height = 0.0
                self.moveDir = 0
                self.visible = True
            if self.height < -1:
                self.height = -1.0
                self.moveDir = 0
                self.visible = False
            
            self.height += self.moveDir * evt.timeSinceLastFrame / self.moveTime
            self.window.setPosition(0, int(self.height* self.window.getHeight()))
         
        return True
    
    def keyPressed(self, evt):
               
        if evt.key == OIS.KC_F1:
            if self.visible or self.moveDir > 0:
                self.hide()
            elif not self.visible or self.moveDir < 0:
                self.show()
            
        # check for key bindings
        if self.keyBinds.has_key(evt.key):
            self.keyBinds[evt.key]()
            
        return True 
    
    def keyReleased(self, evt):
        return False
 
    def write(self, text, command = False):
        self.outputHistory.append(text) 
        
        if command:
            self.output.addText(self._colorize('>>>'))
        for line in text.split("\n"):
            self.output.addText(self._colorize(line) + '\n')
 
        self.updateOverlay = True
        