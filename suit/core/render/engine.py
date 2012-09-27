
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
Created on 01.12.2009

@author: Denis Koronchik
'''

"""There are functionality to work with render engine, input system and gui system.

Render Engine.
OGRE used as render engine.

Gui System.
For gui used MyGUI library. It starts with OGRE automatically.
There are some flags to control gui system:
- _gui_ignore_input_proc_result - allows to ignore results of processing input event by gui.
"""

import ogre.renderer.OGRE as ogre
import ogre.io.OIS as ois
import sc_core as sc
import sys, os, types
import mygui

# constants
# view modes
Mode_Isometric, Mode_Perspective = range(2)
viewMode = None
# root scene node scale for view modes
scale2d_init = 25
scale3d_init = ogre.Vector3(1.0, 1.0, 1.0)

scale2d = 25
scale3d = ogre.Vector3(1.0, 1.0, 1.0)

camera_iso_init_pos = ogre.Vector3(0.0, 0.0, 15.0)
camera_iso_init_orient = None
# plane for isometric mode to create objects in
iso_plane = ogre.Plane(ogre.Vector3(0, 0, -1), ogre.Vector3(0, 0, 0))

# render system
_logManager = None
_session = None
_segment = None
_kernel = None
_ogreRoot = None
_ogreRenderWindow = None
_ogreViewport = None
_ogreCamera = None
_ogreCameraNode = None
_ogreSceneManager = None
_ogreLight = None


# input system
_inputManager = None
_oisMouse = None
_oisKeyboard = None
_keyboardListners = []
_mouseListeners = []
_modeListeners = []

# input show object
_input_show = None

# gui system
_gui = None
# flag to ignore gui input events processing
_gui_ignore_input_proc_result = False
_gui_disable_input = False  # disabling of gui input

# background
_back_rect = None
_back_material_base = "Back/Base"
_back_scene_node = None
_back_scene_node_visible = False

# engine core
_frameListener = None
_windowListener = None
_inputListener = None
_needExit = False
_mainWindow = None
_coreUpdateFunc = None
_animations = []



def initialize(__kernel, __logManager, __session, __segment, _resource_cfg = 'resources.cfg'):
    """Function to initialize rendering engine
    
    @param __kernel: kernel object
    @type __kernel: Kernel
    @param __logManager: log manager object
    @type __logManager: LogManager
    @param __session: system session object
    @type __session: pm.MThreadSession
    @param __segment: user interface segment
    @type __segment: pm.sc_segment      
	@param	_resource_cfg:	path to file with resources specification
	@type	_resource_cfg:	str
    
    @return: if rendering engine initialized, then return True, else - False
    """
    # create listeners
    global _frameListener
    global _windowListener
    global _inputListener
    global _needExit
    global _logManager
    global _session
    global _kernel
    global _segment
    
    
    _logManager = __logManager
    _session = __session
    _kernel = __kernel
    _segment = __segment
    
    _frameListener = FrameListener()
    _windowListener = WindowListener()
    _inputListener = InputListener()
    _needExit = False
    
    # initialize ogre
    initOgre()
    if _ogreRoot is None:
        return False
    
    initResources(_resource_cfg)
    # initialize input system
    initOis()
    # initialize gui
    initGui()
    
    # init background
    initBack()
    
    return True


def initOgre():
    
    global _ogreRoot
    global _ogreRenderWindow
    global _ogreViewport
    global _ogreCamera
    global _ogreCameraNode
    global _ogreSceneManager
    global _ogreLight
    
    
    _logManager.logInit('Ogre renderer', 1);
    _ogreRoot = ogre.Root()
    if (not _ogreRoot.showConfigDialog()):
        _ogreRoot = None
        return
    
    import suit.core.version as version
    _ogreRenderWindow = _ogreRoot.initialise(True, 'Semantic User Interface Toolkit. Kernel version: ' + str(version.version))
    # get initial window metrics
    Window.width, Window.height, Window.depth, Window.left, Window.top = _ogreRenderWindow.getMetrics(1,1,1,1,1)
    #create scene manager
    _logManager.logInit('Scene manager', 2)
    _ogreSceneManager = _ogreRoot.createSceneManager(ogre.ST_GENERIC)
    #self.ogreSceneManager.setShadowTechnique(ogre.SHADOWTYPE_TEXTURE_ADDITIVE)
    #create camera
    _logManager.logInit('Camera', 2)
    _ogreCamera = _ogreSceneManager.createCamera('Main Camera')
    _ogreCameraNode = _ogreSceneManager.getRootSceneNode().createChildSceneNode('ogreCameraNode')
    _ogreCameraNode.attachObject(_ogreCamera)
    _ogreCamera.setFarClipDistance(150)
    _ogreCamera.setNearClipDistance(1)

    global camera_iso_init_orient
    camera_iso_init_orient = _ogreCamera.getOrientation()

    # set default 2d mode
    setMode(Mode_Isometric)

    #self._ogreCamera.setPolygonMode(ogre.PolygonMode.PM_WIREFRAME)
    #create viewport
    _logManager.logInit('Viewport', 2)
    try:
        _ogreViewport = _ogreRenderWindow.addViewport(_ogreCamera.getRealCamera())
    except:
        _ogreViewport = _ogreRenderWindow.addViewport(_ogreCamera)
    _ogreViewport.setBackgroundColour(ogre.ColourValue(0.983, 0.986, 0.994))
    # create light
    _ogreLight = _ogreSceneManager.createLight('PointLight')
    _ogreLight.type = ogre.Light.LT_POINT
    _ogreLight.position = (0, 0, 0)
    _ogreLight.diffuseColour = (1.0, 1.0, 1.0)
    _ogreLight.specularColour = (1.0, 1.0, 1.0)
    _ogreCameraNode.attachObject(_ogreLight)
        
    #register listener
    _ogreRoot.addFrameListener(_frameListener)
    ogre.WindowEventUtilities.addWindowEventListener(_ogreRenderWindow, _windowListener)


def initOis():
    
    global _inputManager
    global _oisMouse
    global _oisKeyboard
    
    # initialize input
    _logManager.logInit('Input system')
    windowHwnd = _ogreRenderWindow.getCustomAttributeInt("WINDOW")
    if sys.platform == 'win32':
        _inputManager = ois.createPythonInputSystem([("WINDOW", str(windowHwnd)), 
#                                                           ("w32_mouse", "DISCL_FOREGROUND"),
#                                                           ("w32_mouse", "DISCL_NONEXCLUSIVE"),
#                                                           ("w32_keyboard", "DISCL_FOREGROUND"),
#                                                           ("w32_keyboard", "DISCL_NONEXCLUSIVE")])
                                                           ])
    else:
        raise AssertionError("Unsupported platform")
    
    # create devices
    _oisKeyboard = _inputManager.createInputObjectKeyboard( ois.OISKeyboard, True )
    _oisMouse = _inputManager.createInputObjectMouse( ois.OISMouse, True )

    width, height, depth, left, top = _ogreRenderWindow.getMetrics(1,1,1,1,1)
    ms = _oisMouse.getMouseState() 
    ms.width = width
    ms.height = height 

    _oisMouse.setEventCallback(_inputListener) 
    _oisKeyboard.setEventCallback(_inputListener)

def initGui():
    """Initialize MyGUI library
    """
    _logManager.logInit("MyGUI")
    # initialize resources
    #resourceGroupManager = ogre.ResourceGroupManager.getSingleton()
    #resourceGroupManager.addResourceLocation(os.path.join(_kernel.getResourceLocation(), 'mygui'),
    #                                         'FileSystem', ogre.ResourceGroupManager.DEFAULT_RESOURCE_GROUP_NAME)
    #resourceGroupManager.initialiseResourceGroup(ogre.ResourceGroupManager.DEFAULT_RESOURCE_GROUP_NAME)
    
    global _gui
    _gui = mygui.Gui()
    _gui.initialise(_ogreRenderWindow)

def initResources(resource_path):
	"""Initialize resources that need to initialize kernel
	"""
	_logManager.logInit("Resources")
	resourceGroupManager = ogre.ResourceGroupManager.getSingleton()
	config = ogre.ConfigFile()
	config.load(resource_path)
	section_iter = config.getSectionIterator()
	while section_iter.hasMoreElements():
		section_name = section_iter.peekNextKey()
		settings = section_iter.getNext()
		for item in settings:
			resourceGroupManager.addResourceLocation(item.value, item.key, section_name)
			
	resourceGroupManager.initialiseResourceGroup(ogre.ResourceGroupManager.DEFAULT_RESOURCE_GROUP_NAME)
    
def initBack():
    """Initialize background
    """
    global _back_rect
    global _back_scene_node
    global _ogreSceneManager
    
    # creating background (surface)
    _back_rect = ogre.Rectangle2D(True)
    _back_rect.setCorners(-1.0, 1.0, 1.0, -1.0)
    _back_rect.setRenderQueueGroup(ogre.RENDER_QUEUE_BACKGROUND)
    _back_rect.setBoundingBox(ogre.AxisAlignedBox(ogre.Vector3(-100000.0, -100000.0, -100000.0), ogre.Vector3(100000.0, 100000.0, 100000.0)))
    _back_rect.setMaterial(_back_material_base)
    
    _back_scene_node = _ogreSceneManager.createSceneNode(str(_back_rect))
    _back_scene_node.attachObject(_back_rect)
    _ogreSceneManager.getRootSceneNode().addChild(_back_scene_node)
    global _back_scene_node_visible
    _back_scene_node_visible = True

def renderOneFrame():
    """Rendering one frame
    """
    # process rendering
    _ogreRoot.renderOneFrame()

    # process system messages
    ogre.WindowEventUtilities.messagePump()

def _start_rendering():
    """Starts and organize rendering cycle
    """
    while (not _needExit):
        # render frame
        renderOneFrame()
        # process system messages
        ogre.WindowEventUtilities.messagePump()
        # process input
        _oisMouse.capture()
        _oisKeyboard.capture()
        
def _stop_rendering():
    """Stops rendering process
    """
    global _needExit
    _needExit = True
        

def shutdown():
    """Shutting down render engine
    """
    global __frameListener
    global __windowListener
    global __inputListener
    global _inputManager
    global _oisMouse
    global _oisKeyboard
    global _ogreRoot
    global _ogreRenderWindow
    global _ogreViewport
    global _ogreCamera
    global _ogreCameraNode
    global _ogreSceneManager
    global _ogreLight
    global _back_rect
    
    if _ogreRoot is None:
        return
    
    _back_scene_node.detachObject(_back_rect)
    _ogreSceneManager.getRootSceneNode().removeChild(_back_scene_node)
    _ogreSceneManager.destroySceneNode(_back_scene_node)
    _back_rect = None
    
    __frameListener = None
    __windowListener = None
    
    # shutting down main window
    if _mainWindow is not None: shutdownMainWindow()
    
    _logManager.logShutdown("MyGUI")
    if _gui is not None:
        _gui.shutdown()
    
    # shutting down ogre
    _logManager.logShutdown('Ogre', 1)
    _ogreRoot.shutdown()
    _ogreRoot = None
    _ogreRenderWindow = None
    _ogreViewport = None
    _ogreSceneManager = None
    _ogreCamera = None
    _ogreCameraNode = None
    _ogreLight = None    
    
    # shutting down input manager
    _logManager.logShutdown("Input manager", 1)
    if(_inputManager is not None):
        _inputManager.destroyInputObject(_oisKeyboard) 
        _inputManager.destroyInputObject(_oisMouse) 
        ois.InputManager.destroyInputSystem(_inputManager) 
        _inputManager = None
        __inputListener = None
        _oisMouse = None
        _oisKeyboard = None


def shutdownMainWindow():
    """Shutting down main window
    """
    # removing main window sc_addr
    global _mainWindow
    if _session.erase_el(_mainWindow._getScAddr()) != sc.RV_OK:
        raise RuntimeError("Error to delete main window from sc-memory")
    
    _mainWindow = None


def scale():
    """Returns scale depend on mode 
    """
    if viewMode == Mode_Isometric:
        return scale2d
    if viewMode == Mode_Perspective:
        return scale3d
    
def scale_init(_mode = None):
    """Returns initial scale depend on mode
    @param _mode:    mode to get initial scale for. None value means, that 
    it will be depend on current mode
    """
    if _mode is None:
        if viewMode == Mode_Isometric:
            return scale2d_init
        if viewMode == Mode_Perspective:
            return scale3d_init
    else:
        if _mode == Mode_Isometric:
            return scale2d_init
        if _mode == Mode_Perspective:
            return scale3d_init
    
def setMode(_mode):
    """Sets new view mode
    @param _mode: new view mode. It can be one of two values:
    - Mode_Isometric - for 2d isometric perspective
    - Mode_Perspective - for 3d perspective
    """
    global viewMode
    old_mode = viewMode
    viewMode = _mode
    if (_mode == Mode_Isometric):
         _ogreCamera.setFarClipDistance(5000)
         _ogreCamera.setNearClipDistance(1)
         _ogreCamera.setProjectionType(ogre.PT_ORTHOGRAPHIC)
         _ogreCameraNode.setPosition(camera_iso_init_pos)
         _ogreCamera.setOrientation(camera_iso_init_orient)
#         _ogreSceneManager.getRootSceneNode().setScale(scale())
         _ogreCamera.setOrthoWindow(_ogreRenderWindow.getWidth() / scale2d, _ogreRenderWindow.getHeight() / scale2d)
    else:
        if (_mode == Mode_Perspective):
            _ogreCamera.setFarClipDistance(10000.0)
            _ogreCamera.setNearClipDistance(1.0)
            _ogreCamera.setProjectionType(ogre.PT_PERSPECTIVE)
#            _ogreSceneManager.getRootSceneNode().setScale(scale())
    
    # notify core about mode changed
    _kernel._notifyModeChanged(viewMode, old_mode)
    

def addAnimation(animation):
    """Add animation to update quque
    """
    if animation in _animations:
        raise AssertionError('Animation already exists')
    _animations.append(animation)
    
def removeAnimation(self, animation):
    """Remove animation from update queue
    """
    _animations.remove(animation)

def addMouseListener(listener):
    """Adds mouse listener
    @param listener: listener to add 
    """
    if listener in _mouseListeners:
        raise AssertionError('Mouse listener already exists')
    _mouseListeners.append(listener)
    
def removeMouseListener(listener):
    """Removes mouse listener
    @param listener: listener to remove
    """
    _mouseListeners.remove(listener)                
    
def addKeyboardListener(listener):
    """Adds keyboard listener
    @param listener: listener to add 
    """
    if listener in _keyboardListners:
        raise AssertionError('Keyboard listener already exists')
    _keyboardListners.append(listener)
    
def removeKeyboardListener(listener):
    """Removes keyboard listener
    @param listener: listener to remove
    """
    _keyboardListners.remove(listener)        
    
def addModeListener(_listener):
    """Adds mode listener.
    All mode listeners need to have _onModeChanged(_mode) function, that will be called when
    view mode changed.
    When listener added it will be notified about current mode.
    @param _listener: listener to add 
    """
    if _listener in _modeListeners:
        raise AssertionError('Mode listener already exists')
    _modeListeners.append(_listener)
    # first notification 
    _listener._onModeChanged(viewMode)
    
def removeModeListener(_listener):
    """Removes mode listener
    @param _listener: listener to remove 
    """
    _modeListeners.remove(_listener)


class FrameListener(ogre.FrameListener):
    
    def __init__(self):
        ogre.FrameListener.__init__(self)
        
    def __del__(self):
        pass
    
    def frameStarted(self, evt):
        
        if (_needExit):
            return False
        
        dt = evt.timeSinceLastFrame 
        # update core
        _coreUpdateFunc(dt)
        # update mygui
        global _gui
        if _gui is not None:
            _gui.injectFrameEntered(dt)
        
        # update root sheet
#        if (self.__rootSheet != None):
#            self.__rootSheet._update(evt.timeSinceLastFrame)
        
        # update animations
        for anim in _animations:
            anim.addTime(dt)
        
        return True
    
    def frameEnded(self, evt):
        # rests intersection flag
        return True
    
    def frameRenderingQueued(self, evt):
            
        return True

class InputListener(ois.KeyListener,  ois.MouseListener):
    
    def __init__(self):
        ois.KeyListener.__init__(self)
        ois.MouseListener.__init__(self)
        
    def __del__(self):
        pass
    
    def mouseMoved (self, evt):
        
        if _input_show is not None:    
            _input_show.mouseMoved(evt)
        
        if _gui and _gui.injectMouseMove(evt) and not _gui_ignore_input_proc_result and not _gui_disable_input:
            return True
            
        for listener in _mouseListeners:
            if (listener.mouseMoved(evt)):
                return True
        
        return True
    
    def mousePressed(self, evt, _id):

        if _input_show is not None:    
            _input_show.mousePressed(evt, _id)
        
        if not _kernel._arg_mode:
            if _gui and _gui.injectMousePress(evt, _id) and not _gui_ignore_input_proc_result and not _gui_disable_input:
                return True
            
        for listener in _mouseListeners:
            if (listener.mousePressed(evt, _id)):
                return True
            
        return True
    
    def mouseReleased(self, evt, _id):

        if _input_show is not None:    
            _input_show.mouseReleased(evt, _id)

        if not _kernel._arg_mode:
            if _gui and _gui.injectMouseRelease(evt, _id) and not _gui_ignore_input_proc_result and not _gui_disable_input:
                return True
            
        for listener in _mouseListeners:
            if (listener.mouseReleased(evt, _id)):
                return True
        
        return True
    
    def keyPressed (self, evt):
        
        if _input_show is not None:    
            _input_show.keyPressed(evt)  
        
        if not _kernel._arg_mode:
            if _gui and _gui.injectKeyPress(evt) and not _gui_ignore_input_proc_result and not _gui_disable_input:
                return True
        
        # notify listeners
        for listener in _keyboardListners:
            if (listener.keyPressed(evt)):
                return True
        
        return True
    
    def keyReleased(self, evt):
        
        if _input_show is not None:
            _input_show.keyReleased(evt)  
        
        if not _kernel._arg_mode:
            if _gui and _gui.injectKeyRelease(evt) and not _gui_ignore_input_proc_result and not _gui_disable_input:
                return True
        
        # notify listeners
        for listener in _keyboardListners:
            if (listener.keyReleased(evt)):
                return True
        
        return True


class WindowListener(ogre.WindowEventListener):
    
    def __init__(self):
        ogre.WindowEventListener.__init__(self)
        
    def __del__(self):
        pass
    
    def windowResized(self, renderWindow):
        """Notification method of render window size changed
        """
        Window.width, Window.height, Window.depth, Window.left, Window.top = _ogreRenderWindow.getMetrics(1,1,1,1,1)
        ms = _oisMouse.getMouseState() 
        ms.width = Window.width
        ms.height = Window.height
    
    def windowClosed(self, renderWindow):
        """Notification message of render window closed
        """
        global _needExit
        _needExit = True
        

###########################################
### Functions to work with input system ###
###########################################
def _getMouseState():
    """Returns mouse state
    """
    return _oisMouse.getMouseState()


#######################################
### Functions to work with renderer ###
#######################################
def registerWindowEventListener(_listener):
    """Registers function that will calls when render window resized
    """
    ogre.WindowEventUtilities.addWindowEventListener(_ogreRenderWindow, _listener)

def unregisterWindowEventListener(_listener):
    """Unregisters function that will calls when render window resized
    """
    ogre.WindowEventUtilities.removeWindowEventListener(_ogreRenderWindow, _listener)



def pos2dToViewPortRay(_pos):
    """Creates viewport ray for specified 2d position
    @param _pos: tuple that represents 2d coordinates (x, y)
    @type _pos: tuple
    
    @return: returns ray in viewport   
    """
    return _ogreCamera.getCameraToViewportRay(_pos[0] / float(Window.width), _pos[1] / float(Window.height))

def pos2dTo3dIsoPos(_pos):
    """Calculates position for isometric mode based on 2d window coordinates
    @param _pos: tuple of coordinates (x, y)
    @type _pos: tuple
    
    @return: returns position on isometric plane for viewport 2d position  
    """
    ray = pos2dToViewPortRay(_pos) 
    res = ogre.Math.intersects(ray, iso_plane)
    if res.first:   d = res.second
    return ray.getPoint(d)# / _ogreSceneManager.getRootSceneNode().getScale()

def pos3dTo2dViewport(_pos):
    """Calculates viewport coordinates based on world coordinates
    @param _pos: world coordinates
    @type _pos: ogre.Vector3
    
    @return: returns viewport position x[-1; 1]; y[-1;1]. Format: tuple(x, y).
    If object is have Z coordinate < 0 relative to camera, then it returns None.
    """
    if viewMode is Mode_Perspective:
        eyeSpacePos = _ogreCamera.getViewMatrix() * _pos
    else:
        eyeSpacePos = _ogreCamera.getViewMatrix() * _pos
        
    if eyeSpacePos.z < 0:
#        if viewMode is Mode_Perspective:
#            screenSpacePos = _ogreCamera.getProjectionMatrix() * eyeSpacePos * scale()
#        else:
        screenSpacePos = _ogreCamera.getProjectionMatrix() * eyeSpacePos
        x = screenSpacePos.x
        y = screenSpacePos.y            
        return x,y
    
    return None

def pos3dTo2dWindow(_pos):
    """Calculates position window coordinates based on world coordinates
    @param _pos: world coordinates
    @type _pos: ogre.Vector3
    
    @return: returns viewport position x[-1; 1]; y[-1;1]; Format: tuple(x, y).
    If object is have Z coordinate < 0 relative to camera, then it returns None.
    """
    proj = pos3dTo2dViewport(_pos)
    if proj is not None:
        return int((proj[0] / 2.0 + 0.5) * Window.width), int( (1 - (proj[1] / 2.0 + 0.5)) * Window.height)
    
    return None 
    



####################################
### Functions to work with mygui ###
####################################
def MyGUI_createWidgetT(_widgetType, _skin, _rect, _align = mygui.Align(), _layer = "Main", _name = ""):
    """Creates widget in mygui
    @param _widgetType: widget type
    @type _widgetType: str
    @param _skin: widget skin
    @type _skin: str
    @param _rect: widget bounds rectangle
    @type _rect: mygui.IntCoord
    @param _align: widget alignment
    @type _align: mygui.Align  
    @param _layer: layer to create widget in
    @type _layer: str
    """
    return _gui.createWidgetT(_widgetType, _skin, _rect, _align, _layer, _name)

def MyGUI_destroyWidget(_widget):
    """Destroys widget
    @param _widget: widget to destroy
    @type _widget: mygui.Widget  
    """
    _gui.destroyWidget(_widget)
    
def MyGUI_setPointer(_name):
    """Sets named pointer for mouse
    @param _name: pointer name
    @type _name: str
    """
    mygui.PointerManager.getInstance().setPointer(_name, None)

def Widget_createWidgetT(_widget, _widgetType, _skin, _rect, _align = mygui.Align()):
    """Create child widget for existing
    @param _widget: widget to create child for
    @type _widget: mygui.Widget
    @param _widgetType: creating widget type
    @type _widgetType: str
    @param _skin: widget skin
    @type _skin: str
    @param _rect: widget bounds rectangle
    @type _rect: mygui.IntCoord
    @param _align: widget alignment
    @type _align: mygui.Align    
    """
    return _widget.createWidgetT(_widgetType, _skin, _rect, _align)

def MyGUI_findWidgetT(_name):
    """Trying to find widget by name 
    """
    return _gui._findWidgetT(_name, False)

#####################################################
### Functions to work with resource group manager ###
#####################################################
def ResourceGroupManager_addResourceLocation(_location, _type, _group):
    """Adds resource location to resource group manager
    @param _location: resources location
    @type _location: str
    @param _type: resource location type
    @type _type: str
    @param _group: resource group name
    @type _group: str     
    """
    ogre.ResourceGroupManager.getSingleton().addResourceLocation(_location, _type, _group)
    
def ResourceGroupManager_initialiseAllResourceGroups():
    """Initialize all resource groups
    """
    ogre.ResourceGroupManager.getSingleton().initialiseAllResourceGroups()

############################################
### Functions to work with scene manager ###
############################################
def SceneManager_createEntity(_entityName, _meshName):
    """Creates entity
    @param _entityName: name of entity
    @type _entityName: str
    @param _meshName: name of mesh to create entity
    @type _meshName: str
    
    @return: returns created entity
    """
    return _ogreSceneManager.createEntity(_entityName, _meshName)

def SceneManager_createManualObject(_name = None):
    """Creates new manual object
    @param _name: manual object name (with None value of this parameter it will be get default name)
    @type _name: str
    
    @return: created manual object
    @rtype: ogre.ManulObject  
    """
    if _name is not None:   return _ogreSceneManager.createManualObject(_name)
    
    return _ogreSceneManager.createManualObject()

def SceneManager_createSceneNode(_name = None):
    """Creates ogre scene node
    @param _name: scene node name (if it will be None, then will be used default name)
    @type _name:    str
    
    @return: returns created scene node
    """   
    if _name:   return _ogreSceneManager.createSceneNode(_name)
    
    return _ogreSceneManager.createSceneNode()


def SceneManager_destroyEntity(_entity):
    """Destroys entity
    
    @param _entity: entity to destroy
    @type _entity: ogre.Entity  
    """
    _ogreSceneManager.destroyEntity(_entity)

def SceneManager_destroyManualObject(_manualObject):
    """Destroys manual object
    
    @param _manualObject: manual object to destroy
    @type _manualObject: ogre.ManualObject  
    """
    _ogreSceneManager.destroyManualObject(_manualObject)
    
def SceneManager_destroySceneNode(_node):
    """Destroys ogre scene node
    @param _node: node to destroy
    @type _node: ogre.SceneNode  
    """  
    _ogreSceneManager.destroySceneNode(_node)
    
def SceneManager_resetScale():
    """Resets scene scale to default
    """
#    if viewMode == Mode_Isometric:
#        global scale2d
#        _scale = scale2d = ogre.Vector3(scale2d_init.x, scale2d_init.y, scale2d_init.z)
#    else:
#        global scale3d
#        _scale = scale3d = ogre.Vector3(scale3d_init.x, scale3d_init.y, scale3d_init.z)
#    _ogreSceneManager.getRootSceneNode().setScale(_scale)

def SceneManager_setScale(_scale):
    """Sets new scale for a whole scene
    
    @param _scale:    new scene scale
    @type _scale:    ogre.Vector3
    """ 
    if viewMode == Mode_Isometric:
        scale2d = _scale
        _ogreCamera.setOrthoWindow(_ogreRenderWindow.getWidth() / scale2d, _ogreRenderWindow.getHeight() / scale2d)
#    else:
#        global scale3d
#        scale3d = _scale
#    _ogreSceneManager.getRootSceneNode().setScale(_scale)

def SceneManager_setBackMaterial(_material):
    """Sets new material to background object
    
    @param _material:    material name
    @type _material:    str
    """
    global _back_rect
    
    if _back_rect is not None:
        _back_rect.setMaterial(_material)
        
def SceneManager_setDefaultBackMaterial():
    """Sets default back material
    """
    SceneManager_setBackMaterial(_back_material_base)
    
def SceneManager_showBack():
    """Shows background image
    """
    _ogreSceneManager.getRootSceneNode().addChild(_back_scene_node)
    global _back_scene_node_visible
    _back_scene_node_visible = True

def SceneManager_hideBack():
    """Hides background image
    """
    _ogreSceneManager.getRootSceneNode().removeChild(_back_scene_node)
    global _back_scene_node_visible
    _back_scene_node_visible = False

def SceneManager_isBackVisible():
    """Check if background image is visible
    """
    return _back_scene_node_visible 


##########################################
### Functions to work with scene nodes ###
##########################################
def SceneNode_addChild(_parent, _node):
    """Adds child node to parent
    @param _parent: parent scene node
    @type _parent: ogre.SceneNode
    @param _child: child scene node
    @type _child: ogre.SceneNode     
    """
    _parent.addChild(_node)

def SceneNode_addRootChild(_node):
    """Adds child node to the root scene node
    @param _node: child node
    @type _node: ogre.SceneNode  
    """
    SceneNode_addChild(_ogreSceneManager.getRootSceneNode(), _node)

def SceneNode_removeChild(_parent, _node):
    """Removes child node form a parent
    @param _parent: parent scene node
    @type _parent: ogre.SceneNode
    @param _node: child scene node
    @type _node: ogre.SceneNode    
    """
    _parent.removeChild(_node)
    
def SceneNode_removeRootChild(_node):
    """Removes child from root scene node
    @param _node: child node to remove
    @type _node: ogre.SceneNode  
    """
    _ogreSceneManager.getRootSceneNode().removeChild(_node)


#############################################
### classes to simplify work with objects ###
#############################################
class Gui:
    createWidgetT = staticmethod(MyGUI_createWidgetT)
    destroyWidget = staticmethod(MyGUI_destroyWidget)
    _findWidgetT   = staticmethod(MyGUI_findWidgetT)
    setPointer    = staticmethod(MyGUI_setPointer)

class ResourceGroupManager:
    addResourceLocation = staticmethod(ResourceGroupManager_addResourceLocation)
    initialiseAllResourceGroups = staticmethod(ResourceGroupManager_initialiseAllResourceGroups)

class SceneManager:
    createEntity = staticmethod(SceneManager_createEntity)
    createManualObject = staticmethod(SceneManager_createManualObject)
    createSceneNode = staticmethod(SceneManager_createSceneNode)
    
    destroyEntity = staticmethod(SceneManager_destroyEntity)
    destroyManualObject = staticmethod(SceneManager_destroyManualObject)
    destroySceneNode = staticmethod(SceneManager_destroySceneNode)
    
    resetScale = staticmethod(SceneManager_resetScale)
    setScale = staticmethod(SceneManager_setScale)
    setBackMaterial = staticmethod(SceneManager_setBackMaterial)
    setDefaultBackMaterial = staticmethod(SceneManager_setDefaultBackMaterial)
    showBack = staticmethod(SceneManager_showBack)
    hideBack = staticmethod(SceneManager_hideBack)
    isBackVisible = staticmethod(SceneManager_isBackVisible)
    
class SceneNode:
    addChild = staticmethod(SceneNode_addChild)
    addRootChild = staticmethod(SceneNode_addRootChild)
#    create = staticmethod(SceneNode_create)
#    destroy = staticmethod(SceneNode_destroy)
    removeChild = staticmethod(SceneNode_removeChild)
    removeRootChild = staticmethod(SceneNode_removeRootChild)
    
class Widget:
    createWidgetT = staticmethod(Widget_createWidgetT)    
    
class Window:
    width = 0
    height = 0
    depth = 0
    left = 0
    top = 0