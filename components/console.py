
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
import suit.core.render.engine as render_engine
 
 
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
 
    # prepare resources
    global resourceGroupManager
    resourceGroupManager = ogre.ResourceGroupManager.getSingleton()
    resourceGroupManager.addResourceLocation(getResourceLocation(),
                                             'FileSystem', getResourceGroup())
    resourceGroupManager.initialiseResourceGroup(getResourceGroup())
    
    # initialize console object
    global console, stdin, stdout, stderr
    stdout = sys.stdout
    stderr = sys.stderr
    console = Console(ogre.Root.getSingleton())
    sys.stdout = console
    #sys.stderr = console
    # register listener
    #core.Kernel.getSingleton().addKeyboardListener(console)
 
def shutdown():
    global stdout, stderr
    sys.stdout = stdout
    sys.stderr = stderr 
 
 
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
 
class Console:
    CONSOLE_LINE_LENGTH = 85
    CONSOLE_LINE_COUNT = 15
    __shared_state = {}
 
    def __init__(self, root = None):
        #self.__dict__ = self.__shared_state

 
        render_engine.addKeyboardListener(self)
        core.Kernel.getSingleton()._addUpdateListener(self)
 
#        if 'isSetup' not in self.__dict__:
#            self.isSetup = True
#        else:
#            return
 
        self.currentInputHistory = 0
        self.inputHistory = []
        self.outputHistory = []
        self.prompt = array.array('b')
        self.updateOverlay = True
        self.multiLineInput = False
        self.cursorPosition = 0
 
        self.interpreter = code.InteractiveConsole({'console':self})
 
        self.keyBinds = {
            OIS.KC_RETURN: self._runPromptText,
            OIS.KC_BACK: self._backspaceCharPrompt,
            OIS.KC_DELETE: self._deleteCharPrompt,
            OIS.KC_UP: self._prevPromptText,
            OIS.KC_DOWN: self._nextPromptText,
            OIS.KC_ESCAPE: self.hide,
            OIS.KC_LEFT: self._moveCursorLeft,
            OIS.KC_RIGHT: self._moveCursorRight,
            OIS.KC_HOME: self._moveCursorHome,
            OIS.KC_END: self._moveCursorEnd,
            OIS.KC_TAB: self._tab,
            }
 
        self.height = 0.0
        self.visible = False
        self.hide()
        
        
        
        self.overlay = ogre.OverlayManager.getSingleton().getByName('Application/ConsoleOverlay')
        self.overlay.show()
        self.textbox = ogre.OverlayManager.getSingleton().getOverlayElement("Application/ConsoleText")
        self.textoverlay = ogre.OverlayManager.getSingleton().getOverlayElement("Application/ConsoleTextOverlay")
        self.textpanel = ogre.OverlayManager.getSingleton().getOverlayElement("Application/ConsolePanel")
        self.textpanel.getMaterial().setLightingEnabled(True)
        self.textpanel.getMaterial().setSceneBlending(ogre.SBT_TRANSPARENT_ALPHA)
 
    def addLocals(self, localsDict):
        for var in localsDict:
            self.interpreter.locals[var] = localsDict[var]
 
    def _tab(self):
        self.prompt.insert(self.cursorPosition, 32) # WhiteSpace
        self.cursorPosition += 1
 
    def _moveCursorEnd(self):
        self.cursorPosition = len(self.prompt)
 
    def _moveCursorHome(self):
        self.cursorPosition = 0
 
    def _moveCursorLeft(self):
        if self.cursorPosition > 0:
            self.cursorPosition -= 1
 
    def _moveCursorRight(self):
        if self.cursorPosition < len(self.prompt):
            self.cursorPosition += 1
 
    def _deleteCharPrompt(self):
        if len(self.prompt) > 0 and self.cursorPosition < len(self.prompt):
            self.prompt.pop(self.cursorPosition)
 
    def _backspaceCharPrompt(self):
        if len(self.prompt) > 0 and self.cursorPosition > 0:
            self.prompt.pop(self.cursorPosition-1)
            self.cursorPosition -= 1
 
    def setPrompt(self, byteArray):
        self._prompt = byteArray
        self.cursorPosition = len(self._prompt)
 
    def getPrompt(self):
        return self._prompt
 
    prompt = property(getPrompt, setPrompt)
 
    def _enableSysRedirect(self):
        self._stderr, self._stdout = sys.stderr, sys.stdout
        sys.stderr, sys.stdout = self, self
 
    def _disableSysRedirect(self):
        sys.stderr, sys.stdout = self._stderr, self._stdout
 
    def _runPromptText(self):
        if  len(self.prompt) > 0 or self.multiLineInput:
            self.outputHistory += [self.promptCursor + self.prompt.tostring()]
            self._enableSysRedirect()
            self.multiLineInput = self.interpreter.push(self.prompt.tostring())
            self._disableSysRedirect()
            self.inputHistory += [self.prompt]
            self.prompt = self.prompt[0:0]
            self.currentInputHistory = len(self.inputHistory)
            self.cursorPosition = 0
 
    def _prevPromptText(self):
        if self.currentInputHistory > 0:
            self.currentInputHistory -= 1
            self.prompt = self.inputHistory[self.currentInputHistory][:]
 
    def _nextPromptText(self):
        if self.currentInputHistory+1 < len(self.inputHistory):
            self.currentInputHistory += 1
            self.prompt = self.inputHistory[self.currentInputHistory][:]
 
    def _getVisible(self):
        return self.visible
 
    def hide(self):
        self.visible = False
 
    def show(self):
        self.visible = True
 
    def keyPressed(self, evt):
               
        if evt.key == OIS.KC_GRAVE:
            if (not self.visible):
                self.show()
            else:
                self.hide()
            return True
 
        if not self.visible:
            return False
 
        try:
            self.keyBinds[evt.key]()
        except KeyError:
            if evt.text != 0:
                self.prompt.insert(self.cursorPosition, evt.text)
                self.cursorPosition += 1
                self.currentInputHistory = len(self.inputHistory)

 
        self.updateOverlay = True
        return True 
    
    def keyReleased(self, evt):
        return False
 
    def _updateConsoleText(self):
        lines = [""] * (Console.CONSOLE_LINE_COUNT - len(self.outputHistory))
        lines += self.outputHistory[-1*Console.CONSOLE_LINE_COUNT:]
        text = "\n".join(lines)
        text += u"\n%s%s" % (self.promptCursor,
                               self.prompt.tostring())
        self.textbox.setCaption(text)
 
        text = "\n".join([""] * (Console.CONSOLE_LINE_COUNT))
        text += u"\n%s%s_" % (self.promptCursor, " " * self.cursorPosition)
 
        self.textoverlay.setCaption(text)
 
    def _appear(self, amt):
        self.height += amt
        self.overlay.show()
        if self.height >= 1.0:
            self.height = 1.0
 
    def _dissapear(self, amt):
        self.height -= amt
        if self.height < 0.0:
            self.height = 0.0
            self.overlay.hide()
 
    def _updateConsolePosition(self, time):
        if self.visible and self.height < 1.0:
            self._appear(3.5*time)
        elif not self.visible and self.height > 0.0:
            self._dissapear(3.5*time)
 
        self.textpanel.setPosition(0,(self.height-1.0)*0.5)
 
    def _update(self, _dt):
        self._updateConsolePosition(_dt)
 
        if self.updateOverlay:
            self._updateConsoleText()
            self.updateOverlay = False
 
        return True
 
    def _getPromptCursor(self):
        return '... ' if self.multiLineInput else '>>> '
 
    promptCursor = property(_getPromptCursor)
 
    def write(self, text):
        for line in text.split("\n"):
            while len(line) > 0:
                self.outputHistory += [line[:Console.CONSOLE_LINE_LENGTH]]
                line = line[Console.CONSOLE_LINE_LENGTH:]
                
        stdout.write(text)
 
        self.updateOverlay = True