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
'''

import suit.core.kernel as core
import suit.core.render.engine as render_engine
import suit.core.render.mygui as mygui 
import suit.core.render.ogrevideoffmpeg as video
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
    return VideoViewer()

# @todo: resolve ogreffmpeg memory leak problem (memory leaks on video playing)

# viewer for video files
class VideoViewer(BaseModeLogic):
    
    def __init__(self):
        """Constructor
        """
        BaseModeLogic.__init__(self)
        #ogre.FrameListener.__init__(self)
        self.gui = render_engine._gui
        self.x, self.y = render_engine._ogreRenderWindow.getWidth(), render_engine._ogreRenderWindow.getHeight()
        self.panel = False
        self.wpanel = None
        self.isRoot = False
        #self.kernel.ogreRoot.addFrameListener(self)
        # video player
        self.videoPlayer = None
        self.videoFile = ""
        self.materialName = None
        self.playing = False
        self.runTime = 0
        self.needUpdateMaterial = True
        
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
        BaseModeLogic.__del__(self)        
        
    def delete(self):
        """Deletion message
        """
        self.stop()
        self.videoPlayer = None
        # detaching objects
        if self.rectAttached:
            self._getSheet().sceneNodeChilds.detachObject(self.rect)
#        # removing listeners
#        if self.listenerRegistered:
#            ogre.Root.getSingleton().removeListener(self)
    
    def _onUpdate(self, _timeSinceLastFrame):
        """Logic update
        """
        BaseLogic._update(self, _timeSinceLastFrame)
        self._updateVideo(_timeSinceLastFrame)
        self._updateState()
        
    def _updateVideo(self, _time):
        """Updates video on time delta since last update
        """
        if (self.videoPlayer is not None) and (self.playing):
            self.runTime += int(_time * 1000)
            self.videoPlayer.refresh(self.runTime)
            if self.needUpdateMaterial:
                if materialManager.resourceExists(self.materialName):
                    if self.isRoot:
                        self.rect.setMaterial(self.materialName)
                    else:
                        self._getSheet()._setMaterialShowName(self.materialName)
                    self.needUpdateMaterial = False
                    
    def _setSheet(self, _sheet):
        """Sets sheet for a logic
        """
        BaseModeLogic._setSheet(self, _sheet)
        
        _sheet.eventRootChanged = self._onRootChanged
        _sheet.eventUpdate = self._onUpdate
        
        
        # getting data from content and save to temporary file
        import os
        import suit.core.sc_utils as sc_utils
        
        _addr = _sheet._getScAddr()
        if _addr is None:   return
        
        kernel = Kernel.getSingleton()
        session = kernel.session()
        fmt = sc_utils.getContentFormat(session, _addr)
        assert fmt is not None
        file_name = "%s.%s" %(str(_addr.this), session.get_idtf(fmt).lower())
        
        # saving data to file
        _cont = session.get_content_const(_addr)
        assert _cont is not None
        _cont_data = _cont.convertToCont()
        data = _cont.get_data(_cont_data.d.size)
        
        path = os.path.join(kernel.cache_path, 'video')
        out_file = os.path.join(path, file_name)
        file(out_file, "wb").write(data)
        
        ogre.ResourceGroupManager.getSingleton().initialiseResourceGroup("video")
        self.setVideo(file_name)
        
    
    def _onRootChanged(self, isRoot):
        """Root mode switching.
        Creating interface and surface for playing in root mode.
        """        
        #objects.ObjectSheet._onRoot(self, isRoot)
        if isRoot:
            render_engine.SceneManager.setBackMaterial("Back/Spaces")
            self._getSheet().sceneNodeChilds.attachObject(self.rect)
            self.rectAttached = True
            self.isRoot = True
#            if self.listenerRegistered:
#                ogre.Root.getSingleton().removeFrameListener(self)
#                self.listenerRegistered = False
        else:
            render_engine.SceneManager.setDefaultBackMaterial()
            if self.rectAttached:
                self._getSheet().sceneNodeChilds.detachObject(self.rect)
                self.rectAttached = False

            self.isRoot = False    
#            ogre.Root.getSingleton().addFrameListener(self)
#            self.listenerRegistered = True
            
        # set flag to update material
        self.needUpdateMaterial = True
        
    def play(self):
        """Starts to play video
        """
        self.videoPlayer.play()
        self.playing = True
        self.runTime = 0
        self.videoPlayer.setLoop(True)
    
    def stop(self):
        """Stops playing of video
        """    
        self.videoPlayer.stop()
        self.videoPlayer.goToSecond(0)
        self.runTime = 0
        self.playing = False
        
    def pause(self):
        """Pause video
        """
        self.videoPlayer.pause()
        self.playing = False
            
    def _stop(self, widget):
        self.stop()
        self.plbut.setCaption("Play")
        
    def _onKeyPressed(self, _evt):
        """Key pressed event
        """
        if _evt.key == ois.KC_SPACE:
            if self.videoPlayer.isPlaying():
                self.pause()
            else:
                self.play()
        
    def setVideo(self, _filename):
        """Sets video for playing
        @param _filename: video file name for playing
        @type _filename: str
        """
        # recreating video player if new file name
        if _filename != self.videoFile:
            self.videoFile = _filename
            self._createPlayer()            
    
    def _createPlayer(self):
        """Creates video player for a video
        """
        self.materialName = "videoMaterial_" + str(self)
        self.videoPlayer = video.cVideoPlayer(self.materialName, self.videoFile)
        print dir(self.videoPlayer)
        self.needUpdateMaterial = True
                
    def _updateState(self):
#        self._updateVideo(evt.timeSinceLastFrame)
        #time = evt.timeSinceLastFrame    
        state = render_engine._oisMouse.getMouseState()
        x = state.X.abs
        y = state.Y.abs
        #if self.panel and self.isRoot:
            #if self.y - y < 50:                        
                #self.showPanel()
            #else: self.hidePanel()
        return True
    
