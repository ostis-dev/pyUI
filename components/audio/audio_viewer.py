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
Created on 06.02.2010

@author: Pavel Karpan
'''

import suit.core.kernel as core
import suit.core.render.engine as render_engine
import suit.core.render.mygui as mygui
import suit.core.render.OgreAL as audiocod
import suit.core.objects as objects
from suit.core.kernel import Kernel
from suit.cf import BaseModeLogic
from suit.core.objects import BaseLogic
import ogre.io.OIS as ois
import ogre.renderer.OGRE as ogre

# material manager
materialManager = ogre.MaterialManager.getSingleton()


def initialize():
    pass


def shutdown():
    pass
    
def _createViever():    
    return AudioViewer()    


# viewer for audio files
class AudioViewer(BaseModeLogic):
    
    def __init__(self):
        """Constructor
        """
        BaseModeLogic.__init__(self)
        self.gui = render_engine._gui
        self.x, self.y = render_engine._ogreRenderWindow.getWidth(), render_engine._ogreRenderWindow.getHeight()
        self.panel = False
        self.isRoot = False
        # audio player
        self.audioPlayer = None
        self.audioFile = ""
        self.playing = False
        self.runTime = 0
        self.needUpdateMaterial = True
        self.manager = None
        
        # attach flags
#        self.listenerRegistered = False
        self.rectAttached = False
        
        # creating rectangle (surface)
        self.rect = ogre.Rectangle2D(True)
        self.rect.setCorners(-1.0, 1.0, 1.0, -1.0)
        self.rect.setRenderQueueGroup(ogre.RENDER_QUEUE_8)
        self.rect.setBoundingBox(ogre.AxisAlignedBox(ogre.Vector3(-100000.0, -100000.0, -100000.0), ogre.Vector3(100000.0, 100000.0, 100000.0)))
        # @todo: remove bounding box hack
        
    def __del__(self):
        """Destructor
        """
        print "Deleted audio_viewer"
        self.stop()
        self.audioPlayer = None
        # detaching objects
        if self.rectAttached:
            self.sceneNode.detachObject(self.rect)
#        # removing listeners
#        if self.listenerRegistered:
#            ogre.Root.getSingleton().removeListener(self)
        self.destroyPanel()
        BaseModeLogic.__del__(self)
                    
    def _setSheet(self, _sheet):
        """Sets sheet for a logic
        """
        BaseModeLogic._setSheet(self, _sheet)
        
        _sheet.eventRootChanged = self._onRootChanged
        #_sheet.eventUpdate = self._onUpdate
    
    def _onRootChanged(self, isRoot):
        """Root mode switching.
        Creating interface and surface for playing in root mode.
        """        
        #objects.ObjectSheet._onRoot(self, isRoot)
        if isRoot:
            self._getSheet().sceneNodeChilds.attachObject(self.rect)
            self.rectAttached = True
            self.controlPanel()
            self.isRoot = True
        else:
            if self.rectAttached:
                self._getSheet().sceneNodeChilds.detachObject(self.rect)
                self.rectAttached = False
                #self.hidePanel()
                self.destroyPanel()
            self.isRoot = False    
            
        # set flag to update material
        self.needUpdateMaterial = True
        
    def play(self):
        """Starts to play audio
        """
        self.audioPlayer.play()
        self.playing = True
#        self.runTime = 0
    
    def stop(self):
        """Stops playing of audio
        """    
        self.audioPlayer.stop()
        self.playing = False
        
    def pause(self):
        """Pause audio
        """
        self.audioPlayer.pause()
        self.playing = False
    
    def _play_pause(self, widget):
        if self.audioPlayer.isPlaying():
            self.pause()
            self.plbut.setCaption("Play")
        else:
            self.play()
            self.plbut.setCaption("Pause")

    def _stop(self, widget):
        self.stop()
        self.plbut.setCaption("Play")            

    def setAudio(self, _filename):
        """Sets audio for playing
        @param _filename: audio file name for playing
        @type _filename: str
        """
        # recreating video player if new file name
        if _filename != self.audioFile:
            self.audioFile = _filename
            self._createPlayer()            
    
    def _createPlayer(self):
        """Creates audio player for a audio
        """
        self.manager = audiocod.SoundManager()
        self.audioPlayer = self.manager.getSingleton().createSound(self.audioFile, self.audioFile, False)
        print dir(self.audioPlayer)
        print self.audioPlayer.getMaxDistance()
        print self.audioPlayer.getMaxGain()
        print self.audioPlayer.getName()
        
    def controlPanel(self):
                      
        self.butWidth = 80
        self.butHeight = 20
        self.butAmount = 5
        begin = (self.x - self.butWidth*self.butAmount) 
        begin = begin/2
        self.wpanel = self.gui.createWidgetT("Widget", "Panel", mygui.IntCoord(1, self.y - 40, self.x, 40), mygui.Align(), "Popup", '')
        self.wpanel.setAlpha(0.5)
        
        self.slider = self.wpanel.createWidgetT("HScroll", "HSlider", mygui.IntCoord(50, 5, 700, 5), mygui.Align())
        self.slider.setScrollRange(100)
        
        self.stopbut = self.wpanel.createWidgetT("Button", "Button", mygui.IntCoord(begin, 15, self.butWidth, self.butHeight), mygui.Align())
        self.stopbut.setCaption("Stop")
        self.stopbut.subscribeEventMouseButtonClick(self,'_stop')
        begin  = begin + self.butWidth
        
        self.backbut = self.wpanel.createWidgetT("Button", "Button", mygui.IntCoord(begin, 15, self.butWidth, self.butHeight), mygui.Align())
        self.backbut.setCaption("Back")        
        begin  = begin + self.butWidth
        
        self.plbut = self.wpanel.createWidgetT("Button", "Button", mygui.IntCoord(begin, 15, self.butWidth, self.butHeight), mygui.Align())
        if self.audioPlayer.isPlaying():
            self.plbut.setCaption("Pause")
        else:
            self.plbut.setCaption("Play")
        self.plbut.subscribeEventMouseButtonClick(self,'_play_pause')     
        begin  = begin + self.butWidth
                          
        self.forwbut = self.wpanel.createWidgetT("Button", "Button", mygui.IntCoord(begin, 15, self.butWidth, self.butHeight), mygui.Align())
        self.forwbut.setCaption("Forward")        
        begin  = begin + self.butWidth
        
        self.volslider = self.wpanel.createWidgetT("HScroll", "HSlider", mygui.IntCoord(begin, 23, self.butWidth, 5), mygui.Align())
        self.volslider.setScrollRange(100)        
#        print dir(self.slider)
#        print self.volslider.setState.__doc__        
        #self.controller = mygui.ControllerFadeAlpha(0, 1, True)        
        #mygui.ControllerManager.getInstance().addItem(self.wpanel, self.controller)        
        self.panel = True        
        
    def destroyPanel(self):        
        if self.panel:
            self.gui.destroyWidget(self.wpanel)
      
    
    def hidePanel(self):      
        if self.panel:
            self.wpanel.setVisible(False)
        
    def showPanel(self):
        if self.panel:
            self.wpanel.setVisible(True)
    
    def _updateState(self):    
        state = render_engine._oisMouse.getMouseState()
        x = state.X.abs
        y = state.Y.abs
#        if self.panel and self.isRoot:
#            if self.y - y < 50:                        
#                self.showPanel()
#            else: self.hidePanel()
        return True
    
