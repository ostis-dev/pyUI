
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
Created on 08.02.2010

@author: Denis Koronchik
'''

import render.engine as render_engine
import ogre.renderer.OGRE as ogre
import suit.core.render.mygui as mygui

class LoadingBar(ogre.ResourceGroupListener):
    
    def __init__(self):
        ogre.ResourceGroupListener.__init__(self)
        
        self.window = None
        self.label = None
        self.progress = None
    
    def __del__(self):
        ogre.ResourceGroupListener.__del__(self)
        
    def start(self):
        """starts loading bar
        """
        # Turn off rendering of everything except overlays
        render_engine._ogreSceneManager.clearSpecialCaseRenderQueues()
        render_engine._ogreSceneManager.addSpecialCaseRenderQueue(ogre.RENDER_QUEUE_OVERLAY)
        render_engine._ogreSceneManager.setSpecialCaseRenderQueueMode(ogre.SceneManager.SCRQM_INCLUDE)
        
        # creating widgets
        cx = render_engine.Window.width / 2
        cy = render_engine.Window.height / 2
        
        width = 250
        height = 70
        
        self.window = render_engine.Gui.createWidgetT("Window",
                                                      "Panel",
                                                      mygui.IntCoord(cx - width / 2, cy - height / 2, width, height),
                                                      mygui.Align(),
                                                      "Main")
        
        self.label = self.window.createWidgetT("StaticText",
                                               "StaticText",
                                               mygui.IntCoord(15, 10, width - 30, 20),
                                               mygui.Align())
        
        self.progress = self.window.createWidgetT("Progress",
                                                  "Progress",
                                                  mygui.IntCoord(10, 35, width - 20, 21),
                                                  mygui.Align())
        
        
        self.progress_range = 1000
        self.modules_loaded = 0
        self.num_groups_init = 0
        self.num_groups_parsed = 0
        self.num_scripts_init = 0
        self.num_scripts_parsed = 0
        self.progress_inc = 0.0
        self.group_steps = 100
        
        self.progress.setProgressRange(self.progress_range)
        
        # self is listener for callbacks from resource loading
        ogre.ResourceGroupManager.getSingleton().addResourceGroupListener(self)
    
    def finish(self):
        """Finishes loading bar
        """
        
        render_engine.Gui.destroyWidget(self.window)
        
        # Back to full rendering
        render_engine._ogreSceneManager.clearSpecialCaseRenderQueues()
        render_engine._ogreSceneManager.setSpecialCaseRenderQueueMode(ogre.SceneManager.SCRQM_EXCLUDE)
        
        # Unregister listener
        ogre.ResourceGroupManager.getSingleton().removeResourceGroupListener(self)
    
    def _updateProgress(self):
        if self.num_groups_init > 0 and self.num_scripts_init > 0:
            pg = self.progress_range * 0.5 / self.num_groups_init
            pos = int( self.progress_range * 0.5 * (1.0 + (self.num_groups_parsed + 1) / float(self.num_groups_init)) + pg * ((self.num_scripts_parsed + 1) / float(self.num_scripts_init)) )
            self.progress.setProgressPosition(pos)
    
    def _updateWindow(self):
        render_engine._ogreRenderWindow.update()
    
    def loadModuleStarted(self, module_name, _count):
        if _count > 0:
            self.label.setCaption(unicode("Loading %s" % module_name))
            self.progress.setProgressPosition(int(0.5 * self.progress_range * (self.modules_loaded / float(_count))))
            self._updateWindow()        
    
    def loadModuleFinished(self):
        self.modules_loaded += 1
    
    
    # ResourceGroupListener callbacks
    def resourceGroupScriptingStarted(self, groupName, scriptCount):
#        if self.mNumGroupsInit > 0 and scriptCount > 0:
#            # Lets assume script loading is 70%
#            self.mProgressBarInc = self.mProgressBarMaxSize * self.mInitProportion / scriptCount
#            self.mProgressBarInc /= self.mNumGroupsInit
#            self.mLoadingDescriptionElement.setCaption(ogre.UTFString("Parsing scripts.."))
#            self.mWindow.update()
        self.label.setCaption(unicode("Parsing scripts in group %s" % groupName))
        self.num_scripts_init = scriptCount
        self.num_scripts_parsed = 0
        self._updateProgress()
        self._updateWindow()
    
    def scriptParseStarted(self, scriptName, skipThisScript):
#        self.mLoadingCommentElement.setCaption(ogre.UTFString(scriptName))
#        self.mWindow.update()
        self.label.setCaption(unicode(scriptName))
        self._updateProgress()
        self._updateWindow()

    def scriptParseEnded(self, scriptName, skipped):
#        self.mLoadingBarElement.setWidth(
#            self.mLoadingBarElement.getWidth() + self.mProgressBarInc)
#        self.mWindow.update()
        self.num_scripts_parsed += 1
        self._updateWindow()

    def resourceGroupScriptingEnded(self, groupName):
        self.num_groups_parsed += 1
    
    def resourceGroupLoadStarted(self, groupName, resourceCount):
#        ogre.LogManager.getSingleton().logMessage("GroupLoadStarted " + groupName )
#        if self.mNumGroupsLoad >0 :
#            self.mProgressBarInc = self.mProgressBarMaxSize * (1-self.mInitProportion) / resourceCount
#            self.mProgressBarInc /= self.mNumGroupsLoad
#            self.mLoadingDescriptionElement.setCaption(ogre.UTFString("Loading resources.."))
#            self.mWindow.update()
        self._updateWindow()
        
    def resourceLoadStarted(self, resource):
#        ogre.LogManager.getSingleton().logMessage("GroupLoadEnded" )
#        self.mLoadingCommentElement.setCaption(ogre.UTFString(resource.getName()))
#        self.mWindow.update()
        self._updateWindow()
    
    def resourceLoadEnded(self):
        pass
        
    def worldGeometryStageStarted(self, description):
#        ogre.LogManager.getSingleton().logMessage("StageStarted " + description )
#        self.mLoadingCommentElement.setCaption(ogre.UTFString(description))
#        self.mWindow.update()
        self._updateWindow()
        
    def worldGeometryStageEnded(self):
#        ogre.LogManager.getSingleton().logMessage("StageEnded")
#        self.mLoadingBarElement.setWidth(
#            self.mLoadingBarElement.getWidth() + self.mProgressBarInc)
#        self.mWindow.update()
        self._updateWindow()
        
    def resourceGroupLoadEnded(self, groupName):
        pass
