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
Created on 30.10.2009

@author: Denis Koronchik
'''

import suit.core.kernel as core
import suit.core.render.engine as render_engine
import suit.core.render.mygui as mygui
import suit.core.objects as objects
from suit.core.kernel import Kernel
from suit.cf import BaseModeLogic
from suit.core.objects import BaseLogic
import ogre.io.OIS as ois
import ogre.renderer.OGRE as ogre
import flash_modes
import flash_env as env
#import ogre.gui.hikari as hikari
import suit.core.render.hikari as hikari

def initialize():
    pass

def shutdown():
    pass




class FlashViewer(BaseModeLogic):
    
    def __init__(self):
        """Constructor
        """
        BaseModeLogic.__init__(self)
        
        # view modes
        self._modes = {ois.KC_V: flash_modes.FlashDefaultViewMode(self)}
        self.switchMode(ois.KC_V)
        
        
        self.gui = render_engine._gui
        self.x, self.y = render_engine._ogreRenderWindow.getWidth(),render_engine._ogreRenderWindow.getHeight()
        self.panel = False
        self.isRoot = False
        
        self.playing = False        
        self.material = None
        self.swfFile = None
        self.mat_size = [1024, 1024]
        self.coord_mult = [1.0, 1.0]
        self.coord_offset = [0, 0]
        
        
        self.rectAttached = False
        self.listenersRegistered = False
        
        # creating rectangle (surface)
        self.rect_corners = [-1.0, 1.0, 1.0, -1.0]
        self.rect = None
        self._createRect()
        # @todo: remove bounding box hack
        
    
    def __del__(self):
        """Destructor
        """
        
        self._destroyControl()
        
        if self.rectAttached:
            self.sceneNodeChilds.detachObject(self.rect)
            
        self.destroyPanel()
        BaseModeLogic.__del__(self)        
    
    def _updateCoordsMultiplier(self):
        """Updates coordinates multiplier
        """
        rw = render_engine._ogreRenderWindow.getWidth()
        rh = render_engine._ogreRenderWindow.getHeight()
        width = rw * (self.rect_corners[2] - self.rect_corners[0]) / 2.0
        height = rh * (self.rect_corners[1] - self.rect_corners[3]) / 2.0
        self.coord_mult[0] = float(self.mat_size[0]) / width
        self.coord_mult[1] = float(self.mat_size[1]) / height
        
        self.coord_offset[0] = (width - rw) / 2.0
        self.coord_offset[1] = (height - rh) / 2.0
        
    def _createRect(self):
        """Creates rectangle surface for flash
        """
        self.rect = ogre.Rectangle2D(True)
        self.rect.setCorners(self.rect_corners[0], self.rect_corners[1], self.rect_corners[2], self.rect_corners[3])
        self.rect.setRenderQueueGroup(ogre.RENDER_QUEUE_8)
        self.rect.setBoundingBox(ogre.AxisAlignedBox(ogre.Vector3(-100000.0, -100000.0, -100000.0), ogre.Vector3(100000.0, 100000.0, 100000.0)))
        
    def _onUpdate(self, _timeSinceLastFrame):
        """Notification on update
        """
        
        self.frameRenderingQueued(None)
        if self._active_mode == self._modes[ois.KC_V]:
            self._modes[ois.KC_V].updateView(_timeSinceLastFrame)
    
    def _onRootChanged(self, _isRoot):
        """Sheet root state changing
        """
        #objects.ObjectSheet._onRoot(self, _isRoot)
        global kernel

        if _isRoot:
            #self._createControl()
            if not self.rectAttached:
                self._getSheet().sceneNodeChilds.attachObject(self.rect)
                self.rectAttached = True
                self.isRoot = True           
            # add keylisteners
#            if not self.listenersRegistered:
#                self.registerListsners()
        else:
            #self._destroyControl()
            #self._setMaterialShowName("flash/icon")
            if self.rectAttached:
                self._getSheet().sceneNodeChilds.detachObject(self.rect)
                self.rectAttached = False
                self.isRoot = False
                
            # removes key listsners
#            if self.listenersRegistered:
#                self.unregisterListeners()
                
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
        if fmt is None: return
        file_name = "%s.%s" %(str(_addr.this), session.get_idtf(fmt).lower())
        
        # saving data to file
        _cont = session.get_content_const(_addr)
        assert _cont is not None
        _cont_data = _cont.convertToCont()
        data = _cont.get_data(_cont_data.d.size)
        
        path = os.path.join(kernel.cache_path, 'flash')
        out_file = os.path.join(path, file_name)
        file(out_file, "wb").write(data)
        
        ogre.ResourceGroupManager.getSingleton().initialiseResourceGroup('flash')
        self.setSwfFile(file_name)
        
    
    def _createControl(self):
        """Creates flash control
        """
        global kernel
        
        self._destroyControl()
#        print dir(env.hikariMgr)
        if not self.material:
            self.material = env.hikariMgr.createFlashMaterial("Flash_material_" + str(self),
                                                          self.mat_size[0], self.mat_size[1])
            self.material.load(self.swfFile)
            self.material.setScaleMode(hikari.SM_SHOWALL)
            self.material.focus()
            #self.material.setTransparent(True, True)
            self._getSheet()._setMaterialShowName(self.material.getMaterialName())
            self.rect.setMaterial(self.material.getMaterialName())
            self._updateCoordsMultiplier()
    
#            print dir(self.material)
    
        else:
            raise RuntimeError("Flash material already exists")
    
    def _destroyControl(self):
        """Destroys control
        """
        if self.material:
            env.hikariMgr.destroyFlashControl(self.material.getMaterialName())
            self.material = None
                
    
    def play(self):
        """Plays swf file
        """
        if not self.material:
            self._createControl()
        if self.material:
            self.material.play()
            self.playing = True
                    
    def pause(self):
        """Pause swf file
        """
        if self.material:
            self.material.pause()
            
    def stop(self):
        """Stops swf file
        """
        if self.material:
            self.material.stop()            
            self.playing = False
        
    def setSwfFile(self, _swfFile):
        """Sets name of swf file to play
        """
        self.swfFile = _swfFile
        
    def _onKeyPressed(self, _evt):
        """Key pressed event
        """
        if _evt.key == ois.KC_SPACE:
            if self.playing:
                self.pause()
            else:
                self.play()
                
    def frameStarted(self, evt):
        time = evt.timeSinceLastFrame    
        state = self.kernel.oisMouse.getMouseState()
        x = state.X.abs
        y = state.Y.abs
#        if self.panel and self.isRoot:
#            if self.y - y < 50:
#                self.showPanel()
#            else: self.hidePanel()
        return True
    
    def frameEnded(self, evt):
        return True
    
    def frameRenderingQueued(self, evt):
        #if self.isRoot:
        env.hikariMgr.update()
            
        return True

    
    