from Tix import _dummyButton
from suit.core.objects import kernel
import suit.core.render.engine as render_engine
import suit.core.render.mygui as mygui
import suit.core.kernel as core
import suit.core.keynodes as keynodes
import sc_core.pm as sc
import sc_core.constants as sc_constants
import suit.core.objects as objects
import sc_core.pm, sc_core.constants
import suit.core.sc_utils as sc_utils
from suit.core.event_handler import ScEventHandlerSetMember
from suit.core.event_handler import ScEventHandlerDie
import thread
import os, math

__author__ = 'DeathWSS'
_version_   =   "0.1.0"
_name_      =   "UserPanel"
_user_panel = None

def initialize():
    global _user_panel
    _user_panel = UserPanel()
    _user_panel.setVisible(True)
    _user_panel.setEnabled(True)

def shutdown():
    global _user_panel
    _user_panel.delete()
    _user_panel = None

class UserPanel(objects.ObjectOverlay):
    def updateUserData(self):
        """
        This function updates current user info
        @return: None
        """
        kernel = core.Kernel.getSingleton()
        session = kernel.session()
        currentUserNode = sc_utils.getCurentUserNode(session)

        name = sc_utils.getUserName(session,currentUserNode)
        password = sc_utils.getUserPassword(session,currentUserNode)
        icon = sc_utils.getImageIdentifier(session,currentUserNode)

        self._curentUser = User(name,password,icon)

    def drawUI(self):
        """
        This function draw user panel
        @return: None
        """
        panelWidth = 0
        textWidth = 0
        if self._curentUser._name is not None:
            textWidth = len(self._curentUser._name) * self._fontSize * 7/10
            panelWidth = textWidth + self._border * 4 + self._buttonSize
        else:
            textWidth = self._size[0]

        self._back = render_engine.Gui.createWidgetT("Window",
            "Button",
            mygui.IntCoord(self._pos[0], self._pos[1], panelWidth, self._size[1]),
            mygui.Align(),
            "Popup", "")
        self._button =  self._back.createWidgetT("Button",
            "Button",
            mygui.IntCoord(self._border, self._border, self._buttonSize, self._buttonSize),
            mygui.Align())

        self._icon = self._button.createWidgetT("StaticImage",
            "StaticImage",
            mygui.IntCoord(self._iconBorder, self._iconBorder, self._iconSize, self._iconSize),
            mygui.Align())

        self._text = self._back.createWidgetT("StaticText", "StaticTextBack",
            mygui.IntCoord(self._border * 2 + self._buttonSize , self._size[1]/2 - self._fontSize/2, textWidth , self._fontSize),
            mygui.Align(),
            "Main")

        self._text.setCaption(self._curentUser._name)
        self._icon.setNeedKeyFocus(False)
        self._icon.setNeedMouseFocus(False)

        if self._curentUser._icon is not None:
            self._icon.setImageTexture(self._curentUser._icon)

    def __init__(self):
        objects.ObjectOverlay.__init__(self)
        self._curentUser = None

        self._size = (200,50)
        self._pos = (0,render_engine.Window.height - self._size[1])
        self._border = 4
        self._fontSize = 12
        self._buttonSize = self._size[1]  - self._border * 2
        self._iconBorder = 4
        self._iconSize = self._buttonSize - self._iconBorder * 2

        self.updateUserData()
        self.drawUI()

    def __del__(self):
        objects.ObjectOverlay.__del__(self)

class User:
    def __init__(self,name,password,icon):
        self._name = name
        self._password = password
        self._icon = icon

    def checkAuthorization(self,password):
        """
        @param password: string that contains password of user
        @return: True if password correct else return False
        """
        if password == self._password:
            return True
        else:
            return False