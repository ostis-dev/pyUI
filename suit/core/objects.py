
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
Created on 18.11.2009

@author: Denis Koronchik
'''

import kernel as core
import ogre.renderer.OGRE as ogre
import render.mygui as mygui
import ogre.io.OIS as ois
import suit.core.render.engine as render_engine
import sc_core.pm
import keynodes
import sc_utils
import thread
import math
from suit.core.utils import AnimationUtils

# store global kernal object
kernel = core.Kernel.getSingleton()


class ScObject:
    """Base object that integrates with sc-memory
    """
    # map of sc_addr -> objects
    sc2obj = {}
    lock = thread.allocate_lock()
    
    def __init__(self):
        # sc_addr of object
        self.__sc_addr = None
            
    def __del__(self):
        pass
        
    def delete(self):
        """Calls when need to delete object
        """
        self._setScAddr(None)
               
    def _setScAddr(self, _sc_addr):
        """Sets new sc_addr for object
        @param _sc_addr: new sc_addr
        @type _sc_addr: sc_addr  
        """        
        # remove old sc_addr
        if self.__sc_addr is not None:
            ScObject.lock.acquire()
            self.sc2obj[str(self.__sc_addr.this)].remove(self)
            ScObject.lock.release()
            
        _old_addr = self.__sc_addr
        self.__sc_addr = _sc_addr
        
        # add new sc_addr
        if self.__sc_addr is not None:
            ScObject.lock.acquire()
            if not self.sc2obj.has_key(str(self.__sc_addr.this)):
                self.sc2obj[str(self.__sc_addr.this)] = []
            
            self.sc2obj[str(self.__sc_addr.this)].append(self)
            ScObject.lock.release()
                    
    def _getScAddr(self):
        """Gets object sc_addr
        """
        return self.__sc_addr  
    
    @staticmethod
    def _sc2Objects(_addr):
        """Returns list of objects that has specified sc_addr
        """
        res = []
        ScObject.lock.acquire()
        res.extend(ScObject.sc2obj[str(_addr.this)])
        ScObject.lock.release()
        return res
    
    @staticmethod
    def _scAddrThis2Objects(_addr_this):
        """Returns list of objects that has specified sc_addr.this
        """
        res = []
        ScObject.lock.acquire()
        res.extend(ScObject.sc2obj[str(_addr_this)])
        ScObject.lock.release()
        return res
    
    
# base class for objects
class Object(ScObject):
    """@author: Denis Koronchik
    
    
    Events:
    - eventScAddrChanged - calls when sc_addr of object changed.
    Syntax: function(<old_addr>, <new_addr>)
    
    Linked object semantics:
    - LS_IN     -    input lines
    - LS_OUT    -    output lines
    - LS_BASEONTHIS - objects based on this one
    """
    # link semantics
    LS_IN, LS_OUT, LS_OTHER, LS_BASEONTHIS, LS_COUNT = range(5)
      
    # object states
    OS_Normal, OS_Selected, OS_Highlighted, OS_WasInMemory, OS_NewInMemory, OS_Merged, OS_Count = range(7)
    
    def __init__(self):
        """Constructor
        """
        ScObject.__init__(self)
        # linked objects
        self.linkedObjects = {self.LS_IN: [], self.LS_OUT: [], self.LS_OTHER: [], self.LS_BASEONTHIS: []}
        # flag to update
        self.needUpdate = True
        self.needViewUpdate = True
        self.parent = None

        self.textValue = None
        self.textColor = None

        # delete event function(<object>)
        self.eventDelete = None

        # state
        self.__state = Object.OS_Normal
        self.__merged = False
        self.__wasInMemory = False

        # view parameters
        self.position = None
        self.scale = None
        self.newScale = None
        self.oldScale = None

        # animation parameters
        self.isAnimated = True
        self.animationScaleProgress = (0, 0, 0)
        self.animationTime = 0.3
        self.animationType = AnimationUtils.BACK
        self.easeAnimationType = AnimationUtils.EASE_IN_OUT

        # selection flag
        self.__selected = False

        self.needPositionUpdate = False
        self.needScaleUpdate = False
        self.needStateUpdate = True
        self.needModeUpdate = True
        self.needLocalizationUpdate = False
        self.needTextUpdate = False

        # events
        self.eventSCAddrChanged = None

        # additional sc-addrs
        self.additionalScAddrs = []

    def __del__(self):
        """Destructor
        """
        ScObject.__del__(self)        
        
        print "__del__ in %s" % str(self)
    
    def delete(self):
        """Remove event.
            Calls when need to remove object
            @attention: Only for internal usage. Calls only from sheet objects
        """
        if self.eventDelete is not None:
            self.eventDelete(self)
        
#        if self.parent is not None: self.parent.removeChild(self)
        
        # removing from linked lines
        lines = []
        lines.extend(self.linkedObjects[self.LS_IN])
        for line in lines:
            line.setEnd(None)
            
        lines = []
        lines.extend(self.linkedObjects[self.LS_OUT])
        for line in lines:
            line.setBegin(None)
            
        kernel.onObjectDelete(self)
        
        ScObject.delete(self)
              
    def isMerged(self):
        return self.__merged
    
    def setMerged(self, value):
        self.__merged = value
        self.resetState()
              
    def isWasInMemory(self):
        return self.__wasInMemory
    
    def setWasInMemory(self, value):
        self.__wasInMemory = value
        self.resetState()
            
    def _setScAddr(self, _sc_addr):
        """Sets new sc_addr for object
        @param _sc_addr: new sc_addr
        @type _sc_addr: sc_addr  
        """
        # notification about sc_addr changing
        if self.eventSCAddrChanged:
            _old_addr = self._getScAddr()
            ScObject._setScAddr(self, _sc_addr)
            self.eventSCAddrChanged(_old_addr, self.__sc_addr)
        else:
            ScObject._setScAddr(self, _sc_addr)
        
        self.resetState()
        self._needLocalizationUpdate()
            
    def _relinkToObject(self, _obj):
        """Re-links all linked objects to another one
        @param _obj:    object that get links
        @type _obj:    Object
        """
        assert _obj is not None
        # re-linking lines
        lin = []
        lin.extend(self.linkedObjects[Object.LS_IN])
        for obj in lin:
            obj.setEnd(_obj)
            
        lout = []
        lout.extend(self.linkedObjects[Object.LS_OUT])
        for obj in lout:
            obj.setBegin(_obj) 
               
            
    def _setSelected(self, _selected):
        """Sets selection status to object.
        This is system function you need be accurate with using it. It is normal to
        call that function from ObjectSheet.select function.
        Only for internal usage.
        
        @param _selected: new selection status
        @type _selected: bool  
        """
        self.__selected = _selected
        if self.__selected:
            self.setState(self.OS_Selected)
        else:
            self.resetState()
        
    def _getSelected(self):
        """Return selection status
        """
        return self.__selected
    
    def getLinkedObjects(self, semantic):
        """Get linked objects by semantic
        """
        return self.linkedObjects[semantic]
    
    def addLinkedObject(self, semantic, object):
        """Adds object as linked
        """
        if (self.linkedObjects[semantic] == None):
            self.linkedObjects[semantic] = [object]
        else:
            self.linkedObjects[semantic].append(object)
    
    def removeLinkedObject(self, semantic, object):
        """Removes linked object
        """
        if (self.linkedObjects[semantic].count(object) == 0):
            raise AssertionError('Haven\'t object')
        else:
            self.linkedObjects[semantic].remove(object)
    
    def _update(self, _timeSinceLastFrame):
        """Update object state
        """
        self.needUpdate = False

        if self.isAnimated: self._animate(_timeSinceLastFrame)

        if self.needViewUpdate: self._updateView()
        
    def _updateView(self):
        """Updates view object representation
        """
        #self.needViewUpdate = False
        
        # change localization    
        if self.needLocalizationUpdate:
#            kernel = core.Kernel.getSingleton()
#            addr = self._getScAddr()
#            if addr is not None:
#                self.__caption = sc_utils.getIdentifier(kernel.session(), addr, kernel.getCurrentTranslation())
#                if self.__caption is None:
#                    caption = kernel.session().get_idtf(addr)
#                    if not sc_utils.isSystemId(caption):
#                        self.__caption = unicode(caption)
#                    else:
#                        self.__caption = ""
            addr = self._getScAddr()
            if addr is not None:
                value, is_system = sc_utils.getLocalizedIdentifier(core.Kernel.session(), addr)
                self.setText(value)
                if is_system:
                    self.setTextColor("#aa0000")
                else:
                    self.setTextColor(None)
            
            # reset localization update flag
            self.needLocalizationUpdate = False
            
        self.needViewUpdate = False


    def _animate(self, _timeSinceLastFrame):
        if self.scale is not None:
            self._animateScale(_timeSinceLastFrame)


    def _animateScale(self, _timeSinceLastFrame):
        if self.oldScale is None or self.newScale is None or self.scale == self.newScale:
            return

        self.animationScaleProgress = (
            self._increaseAnimationProgress(self.animationScaleProgress[0], _timeSinceLastFrame),
            self._increaseAnimationProgress(self.animationScaleProgress[1], _timeSinceLastFrame),
            self._increaseAnimationProgress(self.animationScaleProgress[2], _timeSinceLastFrame)
            )

        # animate x coordinate
        progressX = float(self.animationScaleProgress[0]) / float(self.animationTime)
        animatedX = AnimationUtils().animateValue(
            self.newScale[0] - self.oldScale[0], progressX, self.animationType, self.easeAnimationType)
        self.scale = (self.oldScale[0] + animatedX, self.scale[1], 0)

        # animate y coordinate
        progressY = float(self.animationScaleProgress[1]) / float(self.animationTime)
        animatedY = AnimationUtils().animateValue(
            self.newScale[1] - self.oldScale[1], progressY, self.animationType, self.easeAnimationType)
        self.scale = (self.scale[0], self.oldScale[1] + animatedY, 0)

        # animate z coordinate (if exist)
        if isinstance(self.oldScale, ogre.Vector3):
            progressZ = float(self.animationScaleProgress[2]) / float(self.animationTime)
            animatedZ = AnimationUtils().animateValue(
                self.newScale[2] - self.oldScale[2], progressZ, self.animationType, self.easeAnimationType)
            self.scale = ogre.Vector3(self.scale[0], self.scale[1], self.oldScale[2] + animatedZ)

        self.setCurrentScale(self.scale)

    def _increaseAnimationProgress(self, animationProgress, _timeSinceLastFrame):
        if animationProgress < self.animationTime:
            return animationProgress + _timeSinceLastFrame
        else:
            return self.animationTime

    def _needLinkedUpdate(self):
        """Reset flag to True in linked objects
        """
        for v in self.linkedObjects.itervalues():
            if (v):
                for obj in v:
                    obj.needUpdate = True
                    obj._needLinkedUpdate()
                    
    def _needLocalizationUpdate(self):
        """Notify object about localization change
        """
        self.needLocalizationUpdate = True
        self.needViewUpdate = True
                    
    def _needModeUpdate(self):
        """Notification to update object for new mode
        """
        self.needModeUpdate = True
        self.needViewUpdate = True
        
        self.needStateUpdate = True
        self.needScaleUpdate = True
        self.needPositionUpdate = True
        self.needUpdate = True
    
    def setPosition(self, pos):
        """Sets object position
        @param pos:Ogre::Vector3 value of position 
        """
        self.needUpdate = True
        self._needLinkedUpdate()
        
        self.needViewUpdate = True
        self.needPositionUpdate = True
        assert pos
        self.position = pos
            
    def getPosition(self):
        """ Return object position 
        """
        return self.position

    def setScale(self, sz):
        """Sets object size
        @param size: Ogre::Vector3 value of size  
        """

        if self.isAnimated:
            self._refreshScaleAnimationProperties(self.newScale, sz)
        else:
            self.setCurrentScale(sz)

        self.newScale = sz


    def _refreshScaleAnimationProperties(self, oldScale, newScale):
        if oldScale is None:
            self.setCurrentScale(newScale)

        if oldScale is None or newScale is None or oldScale == newScale:
            return

        self.oldScale = self.newScale
        self.animationScaleProgress = (0.0, 0.0, 0.0)


    def setCurrentScale(self, sz):
        self.needUpdate = True
        self._needLinkedUpdate()

        self.needViewUpdate = True
        self.needScaleUpdate = True
        self.scale = sz

    def getScale(self):
        """Returns object size
        """
        return self.newScale if self.newScale is not None else self.scale
    
    def setState(self, _state):
        """Sets object state
        @param _state: new object state. Can be one of possible object states.
        They are: OS_Normal, OS_Selected, OS_Highlighted
        @type _state: int  
        """
        if _state < 0 or _state >= Object.OS_Count:
            raise RuntimeError('Unknown object state %d' % _state)
        self.__state = _state
        self.needUpdate = True
        self.needStateUpdate = True
        self.needViewUpdate = True
#        self.needUpdate = True
    
    def getState(self):
        """Returns object state
        """
        return self.__state
    
    def resetState(self):
        """Reset state to default value.
        Default value depend on scAddr, and merged flags 
        """
        if self._getSelected():
            self.setState(self.OS_Selected)
        elif self._getScAddr() is not None:
            if self.isMerged():
                self.setState(self.OS_Merged)
            elif self.isWasInMemory():
                self.setState(self.OS_WasInMemory)
            else:
                self.setState(self.OS_NewInMemory)
        else:
            self.setState(self.OS_Normal)
            
    def setText(self, _text):
        """Sets text to object
        """
        self.textValue = _text
        self.needTextUpdate = True
        self.needViewUpdate = True
        self.needUpdate = True
    
    def getText(self):
        """Returns object text
        @rtype: string
        """
        return self.textValue
        
    def setTextColor(self, _color):
        """Sets color for text
        @param _color: String that contains hex (html) representation of color. Example: #ff0000 (red).
                        If color is None, then there are default color will be used
        @type _color: string 
        """
        self.textColor = _color
        self.needTextUpdate = True
        self.needViewUpdate = True
        self.needUpdate = True
    
    def getTextColor(self):
        """Return used text color
        @rtype: string
        """
        return self.textColor
        
#    def _setParent(self, parent):
#        """Sets new parent object.
#        @since: 18.09.09
#        @attention:  Only for internal usage. It doesn't add object to parent childs
#        
#        """
#        if self.parent is not None:
#                self.parent.removeChild(self)
#        self.parent = parent

        
# base class for overlay (2d) objects
class ObjectOverlay(Object):
    """Base class for overlay objects.
    
    @note:   In delete function you need to remove widget.
    """
    def __init__(self, parent = None):
        """Constructor
        @param parent:    parent overlay object
        @type parent:    ObjectOverlay
        """
        Object.__init__(self)
        
        self.oldWidget = None
        self._widget = None     # mygui widget that represents overlay object
        self.needShowUpdate = False
        
        self.showValue = False
        self.enabled = False
        self.needEnabledUpdate = False
       
        self.autoSize = True
        
        self.parent = parent
        self._childs = []
        
        # delegates for updates
        self.textUpdateImpl = None
        
        if self.parent is not None:
            self.parent._childs.append(self)
            
        self.tooltip = None
        self.tooltip_value = None
        
        self.needTooltipUpdate = False
        
        kernel.addOverlayObject(self)
        
    def __del__(self):
        """Destructor
        """
        Object.__del__(self)
        
    def delete(self):
        """Object deletion
        """
        
        if self.tooltip is not None:
            self._widget.subscribeEventToolTip(None, "")
            render_engine.Gui.destroyWidget(self.tooltip)
            self.tooltip = None
            
        Object.delete(self)
        
        kernel.removeOverlayObject(self)
        if self.parent:
            self.parent._childs.remove(self)
            self.parent = None
            
        if self._widget is not None:
            render_engine.Gui.destroyWidget(self._widget)
            self._widget = None
            
    def _setScAddr(self, _addr):
        
        Object._setScAddr(self, _addr)
        
        self.needViewUpdate = True
        self.needTooltipUpdate  = True
        
    def _needLocalizationUpdate(self):
        """@see: objects.Object._needLocalizationUpdate
        """
        Object._needLocalizationUpdate(self)
        for child in self._childs:
            child._needLocalizationUpdate()
    
    def setVisible(self, _value):
        """Sets visibility flag for object
        @param _value:    visibility flag value
        @type _value:    bool
        """
        self.showValue = _value
        self.needShowUpdate = True
        self.needViewUpdate = True
        
    def isVisible(self):
        """Returns visibility flag value
        @return: visibility flag value
        @rtype: bool
        """
        return self.showValue
    
    def isEnabled(self):
        """Check if item is enabled
        @return: if item is enabled, then return True, else - False
        @rtype: bool 
        """
        return self.enabled
    
    def setEnabled(self, _value):
        """Enables/disables menu item
        @param _value:    enabled flag value
        @type _value:    bool
        """
        self.enabled = _value
        self.needEnabledUpdate = True
        self.needViewUpdate = True
    
    def _update(self, _timeSinceLastFrame):
        """Updates object
        """
        Object._update(self, _timeSinceLastFrame)
        
        if self._widget is not self.oldWidget:
            self.oldWidget = self._widget
            if self._widget is not None and self.tooltip_value is not None:
                self._widget.setNeedToolTip(True)
                self._widget.subscribeEventToolTip(self, "_eventToolTip")
                    
    def _updateView(self):
        """Updates view
        """
        Object._updateView(self)
                
        if not self._widget:
            return
        
        if self.needTextUpdate:
            self._updateTextValue()
            self.needTextUpdate = False
            
        if self.needShowUpdate:
            self._updateShow()
            self.needShowUpdate = False
            
        if self.needPositionUpdate:
            self.needPositionUpdate = False
            self._updatePosition()
            
        if self.needScaleUpdate:
            self.needScaleUpdate = False
            self._updateScale()
            
        if self.needEnabledUpdate:
            self.needEnabledUpdate = False
            self._widget.setVisible(self.isVisible() and self.enabled)
            
        if self.needTooltipUpdate:
            session = core.Kernel.session()
            if self._getScAddr() is not None:
                # get tooltip info by explanation* relation
                expl_set = sc_utils.searchOneShotBinPairAttrToNode(session, self._getScAddr(), keynodes.common.nrel_explanation, sc_core.pm.SC_CONST)
                if expl_set is not None:
                    self.tooltip_value = sc_utils.getLocalizedTextFromSet(session, expl_set, core.Kernel.getSingleton().getCurrentTranslation())
                                
    def _updateTextValue(self):
        """Updates text value
        """
        if self.textUpdateImpl is not None:
            self.textUpdateImpl()
        else:
            _caption = self.textValue
            if self.textColor is not None:
                _caption = self.textColor + _caption
            self._widget.setCaption(_caption)
            if self.autoSize:
                # calculate new size
                tsize = self._widget.getTextSize()
                self.setScale((tsize.width + 15, tsize.height + 10))
    
    def _updateShow(self):
        """Update widget visibility
        """
        self._widget.setVisible(self.showValue)
    
    def _updatePosition(self):
        """Updates menu item position on screen
        """
        assert self.position
        self._widget.setPosition(self.position[0], self.position[1])
                
    def _updateScale(self):
        """Updates object scale
        """
        self._widget.setSize(self.scale[0], self.scale[1])
        
    def _eventToolTip(self, _widget, _info):
        """Event on tooltip state change
        """
        if self.tooltip_value is None:
            return
        
        if _info.type == mygui.ToolTipInfo.Show:
            if self.tooltip is not None: return
            self.tooltip = render_engine.Gui.createWidgetT("Window",
                                                           "ToolTipPanel",
                                                           mygui.IntCoord(0, 0, 10, 10),
                                                           mygui.Align(),
                                                           "ToolTip")           
            
            text = self.tooltip.createWidgetT("StaticText",
                                              "ToolTipText",
                                              mygui.IntCoord(12, 12, 0, 0),
                                              mygui.Align())
            
            text.setCaption(self.tooltip_value)
            tsize = text.getTextSize()
            self.tooltip.setSize(tsize.width + 24, tsize.height + 24)
            text.setSize(tsize)
            
            x = _info.point.left + 20
            y = _info.point.top + 20
            
            x = min([x, render_engine.Window.width - tsize.width - 30])
            y = min([y, render_engine.Window.height - tsize.height - 30])
            
            self.tooltip.setPosition(x, y)       
            self.tooltip.setVisible(True)
            self.tooltip.setAlpha(1.0)
            
        elif _info.type == mygui.ToolTipInfo.Hide and self.tooltip is not None:
            render_engine.Gui.destroyWidget(self.tooltip)
            self.tooltip = None
            self.tooltip_widget_name = None
        
    def _checkPoint(self, _point):
        """Check if specified point is in object shape
        @param _point:    tuple that contains point coordinates
        @type _point: tuple
        @return: Return true, if object shape contains point; otherwise return false 
        """
        return self._widget._findLayerItem(_point[0], _point[1]) is not None
#        rect = self._widget.getAbsoluteRect()
#        dx = _point[0] - rect.left
#        dy = _point[1] - rect.top
#        
#        return dx >= 0 and dx <= rect.width() and dy >= 0 and dy <= rect.height()
        
    def getCenter(self):
#        return (self.position[0] + self.scale[0] / 2,
#                self.position[1] + self.scale[1] / 2)
        rect = self._widget.getAbsoluteRect()
        return (rect.left + rect.width() / 2,
                rect.top + rect.height() / 2)
            
    
class ObjectDepth(Object, ogre.Node.Listener):
    """Base 3d object class implementation
    """   
    def __init__(self, _sceneNode = None):
        """Constructor
        """
        Object.__init__(self)
        ogre.Node.Listener.__init__(self)      
        # scene node for Ogre
        if _sceneNode is None: 
            self.sceneNode = render_engine.SceneManager.createSceneNode()
        else:
            self.sceneNode = _sceneNode
        
        # debug
#        self.sceneNode.showBoundingBox(True)
        # debug
        
        #self.sceneNode.setListener(self)
        # store last position to optimize listening 
        self.__lastPos = self.sceneNode.getPosition()
        
        # text object
        self.text_obj = None
        
        self.position = ogre.Vector3(0, 0, 0)
        self.scale = ogre.Vector3(1, 1, 1)
        
        # attached scene flag
        self.isSceneAttached = False
        self.needSceneAttachUpdate = False
        
        # update flags
        self.needTextUpdate = False
        self.needTextPositionUpdate = False
        
        # object's level in graph radial layout
        self.level = -1
        
    def __del__(self):
        """Destructor
        """
        Object.__del__(self)

                    
    def delete(self):
        """Delete object
        @summary: Removes node listener
        """
        Object.delete(self)

        if self.text_obj is not None:
            self.text_obj.delete() 
            self.text_obj = None
#        if self.sceneNode:
#            self.sceneNode.setListener(None)

        # removing ogre scene node
        if self.sceneNode:
            render_engine.SceneManager.destroySceneNode(self.sceneNode)
            self.sceneNode = None
        
    
    def _checkRayIntersect(self, ray):
        """Check if ray intersects object
        @param ray: ray to check intersection with
        @type ray: ogre.Ray  
        @returns tuple (intersection result, intersection point)
        """
        res = ogre.Math.intersects(ray, self.sceneNode._getWorldAABB())
        return res.first, ray.getPoint(res.first)
    
    def _getCross(self, pos):
        """Count cross position
        @param pos:    Position for another end of line object
        """
        c = self.position#self.sceneNode.getPosition()
        v = pos - c
        sz = self.scale / 2.0
        radius = max([sz.x, sz.y, sz.z])
        v.normalise()
        return c + (v * radius)
    

    def _update(self, timeSinceLastFrame):
        """Updates object state
        @param timeSinceLastFrame: time since last frame
        @type timeSinceLastFrame: float  
        """
#        if not self.needUpdate: return
        # update text position
        Object._update(self, timeSinceLastFrame)
        
#        if self._getSelected():
#            self.sceneNode.yaw(ogre.Radian(ogre.Degree(90 * timeSinceLastFrame)))
#        else:
#            self.sceneNode.resetOrientation()
        
        if self.needViewUpdate: self._updateView()
        if self.text_obj is not None: 
            self.text_obj._update(timeSinceLastFrame)
    
    def _updatePosition(self):
        """Synchronize graphical object position
        """
        self.sceneNode.setPosition(self.position)
            
    def _updateView(self):
        """Updates scene node with parameters
        """
        Object._updateView(self)

        if self.needPositionUpdate:
            # need to set last position to skip nodeUpdated event 
            self.__lastPos = self.position
            self._updatePosition()
            self.needPositionUpdate = False
            self.needTextPositionUpdate = True
            
        if self.needScaleUpdate:
            self.sceneNode.setScale(self.scale)
            self.needScaleUpdate = False
            self.needTextPositionUpdate = True
            
        if self.needSceneAttachUpdate:
            self.needTextUpdate = True
            self.needSceneAttachUpdate = False
            self.needTextPositionUpdate = True
            
        if self.needTextUpdate:
            self._updateTextValue()
            self.needTextUpdate = False
            
        if self.needTextPositionUpdate:
            if self.text_obj:
                self.text_obj.update_position() 
            self.needTextPositionUpdate = False
                        
    def nodeUpdated(self, node):
        """Notify that node updated
        """
        pos = self.sceneNode.getPosition()
        # position doesn't changed, then we doesn't need update
        if self.__lastPos == pos:
            return
        
        self.__lastPos = pos
        self.needUpdate = True
        self._needLinkedUpdate()
        # text notification
        if self.text_obj is not None:   self.text_obj.needPositionUpdate = True
        
    
    def nodeDestroyed(self, node):
        pass
    
    def nodeAttached(self, node):
        pass
    
    def nodeDetached(self, node):
        pass
        
        
    def setSceneNode(self, node):
        """Set scene node for object
        """
        self.__sceneNode = node
        #self.__sceneNode.setUserAny(self)
        self.needUpdate = True

    def getSceneNode(self):
        return self.sceneNode
               
    def setTextVisible(self, _visibility):
        """Shows object text
        @param _visibility: text visibility flag
        @type _visibility: bool  
        """
        if self.text_obj is None:   return
        
        if _visibility:
            self.text_obj.show()
        else:
            self.text_obj.hide()
    
    def setState(self, _state):
        """@see Object.setState
        """
        Object.setState(self, _state)
        
        if self.text_obj is None: # do nothing
            return
        
        self._update_text_alpha()
            
    def _updateTextValue(self):
        """Updates text value
        """
        if self.textValue and self.isSceneAttached:                
            if not self.text_obj:
                self.text_obj = ObjectText(self.getPosition(), self)
                self.text_obj.show()
                self.needPositionUpdate = True
                self.needViewUpdate = True
                self._update_text_alpha()
            
            _caption = self.textValue
            if self.textColor is not None:
                _caption = self.textColor + _caption
            self.text_obj.setText(_caption)
        else:
            if self.text_obj is not None:
                self.text_obj.delete()
            self.text_obj = None
            
    def _update_text_alpha(self):
        """Updates text alpha
        """
        _state = self.getState()
        if _state == Object.OS_Highlighted:
            self.text_obj.setAlpha(1.0)
        elif _state == Object.OS_Selected:
            self.text_obj.setAlpha(0.8)
        else:
            self.text_obj.setAlpha(0.5)
        
    def _attachedScene(self):
        """Notification on attaching object to scene
        """
        self.isSceneAttached = True
        self.needSceneAttachUpdate = True
        self.needViewUpdate = True
        self.needUpdate = True
    
    def _detachedScene(self):
        """Notification on detaching object from scene
        """
        self.isSceneAttached = False
        self.needSceneAttachUpdate = True
        self.needViewUpdate = True
        self.needUpdate = True

    @staticmethod
    def getDistance(a, b):
        delta = a - b
        dist2d = math.sqrt(delta[0] * delta[0] + delta[1] * delta[1])
        return math.sqrt(dist2d * dist2d + delta[2] * delta[2])
        
# base class for line objects
class ObjectLine(ObjectDepth):
    """Object for lines in 3D.
    
    @attention: If you use it as base class, then you must store
    position of begin and end connection point in self.begPos and self.endPos,
    when they changed
    """
    
    # line ending types
    LET_NONE, LET_END, LET_BEGIN, LET_BOTH, LET_Count = range(5)
    
    def __init__(self, sceneNode):
        """Constructor
        """
        ObjectDepth.__init__(self, sceneNode)
        self.beginObject = None
        self.endObject = None
        
        self.begin_pos = None
        self.end_pos = None
        
        self.radius = 0.15
    
    def __del__(self):
        """Destructor
        """
        ObjectDepth.__del__(self)
        
        print "__del__ in %s" % str(self)
    
    def delete(self):
        """Delete object event. Removes link in begin and end objects
        """
        ObjectDepth.delete(self)
        if self.beginObject:
            self.beginObject.removeLinkedObject(Object.LS_OUT, self)
            self.beginObject = None
            
        if self.endObject:
            self.endObject.removeLinkedObject(Object.LS_IN, self)
            self.endObject = None
    
    def _getCross(self, pos):
        """Count cross position
        @param pos:    Position for another end of line object
        """
        return (self.begin_pos + self.end_pos) / 2.0
        
    def _update(self, timeSinceLastFrame):
        """Update scene node
        """
        if self.needUpdate:
#            if self.beginObject is not None and self.beginObject.needUpdate:
#                self.beginObject._update(timeSinceLastFrame)
#            if self.endObject is not None and self.endObject.needUpdate:
#                self.endObject._update(timeSinceLastFrame)
            
            if self.begin_pos and self.end_pos and self.text_obj:
                self.text_obj.setPosition((self.begin_pos + self.end_pos) / 2.0 + self.radius * 1.2 * ogre.Vector3(1.0, 1.0, 0.0))
            
        if self.needViewUpdate:
            self.needPositionUpdate = False
            self.needScaleUpdate = False
            self._updateView()
            
        if self.text_obj is not None: 
            self.text_obj._update(timeSinceLastFrame)
        
        self.needUpdate = False
        
#        ObjectDepth._update(self, timeSinceLastFrame)      
    
    def _checkRayIntersect(self, ray):
        """Check if ray intersects object
        @param ray: ray to check intersection with
        @type ray: ogre.Ray  
        @returns tuple (intersection result, distance to intersection point)
        """
        
        res = ogre.Math.intersects(ray, self.sceneNode._getWorldAABB())
        if not res.first or self.beginObject is None or self.endObject is None:
            return False, -1
        
        if self.begin_pos is None or self.end_pos is None:
            return False, -1
            
        # FIXME:    resolve problem when line goes to line
            
        # calculating distance
#        scale = render_engine.scale()
#        p1 = self.begin_pos * render_engine.scale()
#        p2 = self.end_pos * render_engine.scale()
        v1 = self.end_pos - self.begin_pos        
        v2 = ray.getDirection()
       
        r = v1.crossProduct(v2)
        s = self.begin_pos - ray.getOrigin()
        d = abs(r.normalisedCopy().dotProduct(s))
        
        # @ todo: calculate distance to intersection point
        if d <= self.radius:
            return True, 0
                        
        return False, -1
    
    def setBegin(self, object):
        """Set begin object
        """
        if self.beginObject:
            self.beginObject.removeLinkedObject(Object.LS_OUT, self)
        self.beginObject = object
        if self.beginObject:
            self.beginObject.addLinkedObject(Object.LS_OUT, self)
            self.beginObject.sceneNode._updateBounds()
            
        self.needUpdate = True
    
    def getBegin(self):
        """Get begin object
        """
        return self.beginObject
    
    def setEnd(self, object):
        """Set end object
        """
        if self.endObject:
            self.endObject.removeLinkedObject(Object.LS_IN, self)
        self.endObject = object
        if self.endObject:
            self.endObject.addLinkedObject(Object.LS_IN, self)
            self.endObject.sceneNode._updateBounds()
            
        self.needUpdate = True
    
    def getEnd(self):
        """Get end object
        """
        return self.endObject

    def getLineLength(self):
        assert self.beginObject
        assert self.endObject
        return ObjectDepth.getDistance(self.endObject.getPosition(), self.beginObject.getPosition())
    
# base class for sheet objects
class ObjectSheet(ObjectDepth, ois.KeyListener, ois.MouseListener):
    """@author: Denis Koronchik
    
    @todo: make functions thread safely
    
    Structure of scene nodes:
            Sheet scene node
                    |
                    |
            Childs scene node
            /                \
           /                  \
    Child 1 Scene node ...   Child N Scene node
    
    Sheet scene node used to represent it in none root mode. It contains border object.
    Also it position is a position of sheet in parent sheet.
    Childs scene node attaches to root scene node in root mode and represents child objects.
    It position represents sheet offset in root mode. 
    
    Events:
    - eventLogicChanged - is calling when logic for a sheet changed.
    Syntax: function(<previous_logic>, <new_logic>)
    - eventRootChanged - is calling when get _onRoot notification from kernel to 
    notify about that changing
    Syntax: function(<new_state>)
    - eventUpdate - is calling on sheet update.
    Syntax: function(<timeSinceLastFrame>)
    - eventUpdateView - is calling when sheet updates view
    Syntax: function()
    - eventChildAppend - is calling after object appended
    Syntax: function(<object>)
    - eventChildDelete - is calling after object deletion
    Syntax: function(<object>)
    - eventSelectionChanged - is calling when selection changed
    Syntax: function()
    - eventContentUpdate - is calling when need to update window content. In that event you need to update
    content_data and content_type values.
    Syntax: function()
    - eventModeUpdate - is calling when view mode changed
    Syntax: function()
    
    Input device events (if method do anything, then it return True, else - False):
    - eventMousePressed - is calling when mouse pressed on sheet.
    Syntax: function(<ois.MouseEvent>, <ois.MouseButtonId>)
    - eventMouseReleased - is calling when mouse released on sheet.
    Syntax: function(<ois.MouseEvent>, <ois.MouseButtonId>)
    - eventMouseMoved - is calling when mouse moved on sheet.
    Syntax: function(<ois.MouseEvent>)
    - eventKeyPressed - is calling when key pressed on sheet.
    Syntax: function(<ois.KeyEvent>)
    - eventKeyReleased - is calling when key released on sheet.
    Syntax: function(<ois.KeyEvent>)
    - eventObjectUnderMouse - is calling on object mouse function call. 
    It must return list of objects that also be need to check. We need that situation,
    when any objects not a child for sheet, they make big hierarchy.
    Syntex: function()
    - eventHaveChild - is calling when need to check if sheet have a child object
    Syntex: function(<objects.Object>)
    """
    
    # content types
    CT_Unknown, CT_String, CT_Binary, CT_Real, CT_Int, CT_Count = range(6)
    
    def __init__(self, title = "Untitled"):
        """Constructor
        """
        ObjectDepth.__init__(self)
        ois.KeyListener.__init__(self)
        ois.MouseListener.__init__(self)
        # child objects
        self.__childObjects = []
        self.sceneNodeChilds = render_engine.SceneManager.createSceneNode()
        # sheet title
        self.title = title
        self.isRoot = False
        self.__underMouseUpdated = False
        self.ray = None
        
        # objects for a none root mode
        self.manualBorder = None
        self.manualPlane = None
        self.sceneNodeBorder = None
        self.material_show = None
        self.material_border = 'scg_Normal'
        self.sceneNodeNode = None
        self.entitiesNode = []
        
        # object that represents sheet logic
        self.__logic = None
        
        # list of selected elements
        self.selectedObjects = [] 
        
        # creating temporary segment
        self.__tmpSegUri = kernel.getDirUITmpUri() + "/%s" % str(self)
        self.__tmpSegment = kernel.session().create_segment_full_uri(self.__tmpSegUri)
        kernel.session().open_segment(self.__tmpSegUri)        
        
        # event handlers
        self.eventLogicChanged = None
        self.eventRootChanged = None
        self.eventUpdate = None
        self.eventUpdateView = None
        self.eventChildAppend = None
        self.eventChildRemove = None
        self.eventSelectionChanged = None
        self.eventContentUpdate = None
        self.eventObjectUnderMouse = None
        self.eventHaveChild = None
        self.eventModeUpdate = None
        
        # mouse events
        self.eventMousePressed = None
        self.eventMouseReleased = None
        self.eventMouseMoved = None
        # keyboard events
        self.eventKeyPressed = None
        self.eventKeyReleased = None
        
        # update flags
        self.needShowMaterialUpdate = False
        
        # layout
        self.__layoutGroup = None
        
        # current scale
        self.root_scale2d = render_engine.scale2d
        self.root_scale3d = render_engine.scale3d
        
        # store camera position and mode
        self.camera_pos = render_engine.camera_iso_init_pos
        self.camera_orient = render_engine.camera_iso_init_orient
        self.view_mode = render_engine.Mode_Isometric
               
        self.sceneNodeQuest = None
        self.entityQuest = None
        self._createNode()
        self.isContentShow = False
        
        # content
        self.content_data = None
        self.content_type = ObjectSheet.CT_Unknown
        self.content_format = None
    
    def __del__(self):
        """Destructor
        """
        ObjectDepth.__del__(self)
                
        print "__del__ in %s" % str(self)
        
    def delete(self):
        """Deletion message
        """        
        #ois.KeyListener.__del__(self)
        
        if self.__layoutGroup is not None:
            self.__layoutGroup.delete()
            self.__layoutGroup = None
                        
        # deleting logic
        if self.__logic is not None:
            self.__logic.delete()
            self.__logic = None
                        
        # deleting child objects
        childs = []
        childs.extend(self.__childObjects)
        for obj in childs:
            #obj.delete()
            self.removeChild(obj)
            obj.delete()
        self.__childObjects = []
        self.selected = False
        
        # deleting from memory
        addr = self._getScAddr()
        kernel = core.Kernel.getSingleton()
        if addr is not None:
            session = core.Kernel.session()
            self._setScAddr(None)
            if kernel.haveOutputWindow(addr):
                kernel.removeOutputWindow(addr)
#            if core.Kernel.segment().this == addr.seg.this:
#                session.erase_el(addr)
       
        if self.manualBorder is not None:
            render_engine.SceneManager.destroyManualObject(self.manualBorder)
        if self.manualPlane is not None:
            render_engine.SceneManager.destroyManualObject(self.manualPlane)
        if self.sceneNodeBorder:
            render_engine.SceneManager.destroySceneNode(self.sceneNodeBorder)
        if self.sceneNodeChilds:
            render_engine.SceneManager.destroySceneNode(self.sceneNodeChilds)
        
        for ent in self.entitiesNode:
            render_engine.SceneManager.destroyEntity(ent)    
        if self.sceneNodeNode:
            render_engine.SceneManager.destroySceneNode(self.sceneNodeNode)
        if self.sceneNodeQuest:
            render_engine.SceneManager.destroySceneNode(self.sceneNodeQuest)
        if self.entityQuest:
            render_engine.SceneManager.destroyEntity(self.entityQuest)
            
        # removing temporary segment
        kernel.session().unlink(self.__tmpSegUri)
            
        ObjectDepth.delete(self)
    
    def _update(self, timeSinceLastFrame):
        """Calls _update method for all child object
        @param timeSinceLastFrame: time since last frame
        @type timeSinceLastFrame: float
        """
        self.__underMouseUpdated = False
        
        if self.isRoot and render_engine.viewMode is render_engine.Mode_Perspective:
            self._updateChildTexts()
        
        ObjectDepth._update(self, timeSinceLastFrame)
        for child in self.__childObjects:
            child._update(timeSinceLastFrame)
        
        if self.eventUpdate is not None:    self.eventUpdate(timeSinceLastFrame)
            
    def _updateView(self):
        """Updates sheet view
        """
        ObjectDepth._updateView(self)
        
        if self.eventUpdateView is not None:    self.eventUpdateView()
        
        # material for a none root mode
        if self.needShowMaterialUpdate:
            self.needShowMaterialUpdate = False
            self._update_show_material()
          
        # update state  
        if self.needStateUpdate:
            self.needStateUpdate = False
            self._update_state()    
            
        if self.needModeUpdate:    
            if render_engine.viewMode is render_engine.Mode_Perspective:
                self.sceneNode.setAutoTracking(True, render_engine._ogreCameraNode, ogre.Vector3(0, 0, 1))
            else:
                self.sceneNode.setAutoTracking(False)
                self.sceneNode.resetOrientation()
                
                self.resetState()
                
                if self.eventModeUpdate:
                    self.eventModeUpdate()
                    
            self.needModeUpdate = False
    
    def _update_show_material(self):
        """Updates material for none root mode
        """
        if self.manualPlane:
            self.manualPlane.setMaterialName(0, self.material_show)
        else:
            self.needShowMaterialUpdate = True
    
    def _update_state(self):
        """Updates state
        """
        st = self.getState()
        postfix = "Normal"
        if st == self.OS_Selected:
            postfix = "Selected"
        elif st == self.OS_Highlighted:
            postfix = "Highlighted"
        elif st == self.OS_WasInMemory:
            postfix = "WasInMemory"
        elif st == self.OS_NewInMemory:
            postfix = "NewInMemory"
        elif st == self.OS_Merged:
            postfix = "Merged"
        
        mat_name = "scg_Node_" + postfix
            
        # changing material
        self.material_border = mat_name
        if self.isContentShow:
            if self.manualBorder is not None:
                self.manualBorder.setMaterialName(0, self.material_border)
        else:
            n = len(self.entitiesNode) - 1
            for idx in xrange(n):
                self.entitiesNode[idx].setMaterialName(mat_name)
            self.entitiesNode[n].setMaterialName("scg_content_cube")
            
            self.entityQuest.setMaterialName("scg_content_unknown")
            
    def _updateChildTexts(self):
        """Notification for child text update
        
        @summary: Only for internal usage. Calls in 3d mode to update text positions
        """
        for child in self.__childObjects:
            child.needTextPositionUpdate = True
            child.needViewUpdate = True
            
    def _needLocalizationUpdate(self):
        """@see: objects.Object._needLocalizationUpdate
        """
        ObjectDepth._needLocalizationUpdate(self)
        
        if self.__childObjects is None:
            return
        
        for child in self.__childObjects:
            child._needLocalizationUpdate()
            
    def _deleteObject(self, object):
        """Delete object from window
        """
        objects = [] + object.linkedObjects[Object.LS_IN] + object.linkedObjects[Object.LS_OUT] + object.linkedObjects[Object.LS_BASEONTHIS]
        
        # remove duplicates (processing reflexive)
        del_map = {}
        for obj in objects:
            del_map[obj] = None
        
        # delete all connected line objects
        for obj in del_map.iterkeys():
            # check if object deleted
            if obj in self.__childObjects:
                self._deleteObject(obj)
                
        # remove object from sheet and call delete method
        self.removeChild(object)
            
        object.delete()
                    
    def _getObjectsUnderMouse(self, sortDistance = True, forced = False, mpos = None):
        """Returns objects under mouse. By default it's caching results for frame, but
        if you need to find objects anyway, then set forced parameter to True.
        @warning: You must be accurate with using this function. It's not thread safe, because
        it gets mouse state
        @param forced: flag to force finding
        @type forced: bool  
        @param sortDistance: flag to sort founded object by distance from near to far
        @type sortDistance: bool 
        @param mpos: mouse position. If you set it to None, then mouse position will be given for
        current mouse state. If you set parameters to None, then it will be work in forced mode
        automatically.
        @type mpos: tuple (x, y)  
        @return: list of tuples (distance, object)
        @rtype: tuple
        """        
        if not self.__underMouseUpdated or forced or mpos is not None:
            # building intersection ray 
            if mpos is None:
                mstate = render_engine._getMouseState()
                self.ray = render_engine.pos2dToViewPortRay((mstate.X.abs, mstate.Y.abs))
            else:
                self.ray = render_engine.pos2dToViewPortRay(mpos)
            #x = mstate.X.abs / float(mstate.width)
            #y = mstate.Y.abs / float(mstate.height)
            
            
            # iterating through objects and finding intersections
            self.founded = []
            check_list = []
            check_list.extend(self.__childObjects)
            if self.eventObjectUnderMouse:
                check_list.extend(self.eventObjectUnderMouse())
            for child in check_list:
                res, dist = child._checkRayIntersect(self.ray)
                if res:
                    self.founded.append((dist, child))
            
            # distance compare function
            def distCmp(x, y):
                d1, o1 = x
                d2, o2 = y
                if d1 < d2:
                    return -1
                elif d1 > d2:
                    return 1
                return 0
            # sorting if need
            if sortDistance: 
                self.founded.sort()
                    
            self.__underMouseUpdated = True
            
        return self.founded
    
    def _setMaterialShowName(self, _matName):
        """Sets name of material to show on plane when sheet isn't root
        @param _matName: material name
        @type _matName: str
        """
        self.material_show = _matName
        self.needShowMaterialUpdate = True
        
    def _getCross(self, pos):
        """Count cross position
        @param pos:    Position for another end of line object
        """
        if self.isContentShow:
            aabb = self.sceneNodeBorder._getWorldAABB()
#            scale = render_engine.scale()
#            aabb.scale((1.0, 1.0, 1.0))
            c = aabb.getCenter()
            v = c - pos
#            v = v / scale
            v.normalise()
            ray = ogre.Ray(pos, v)
            res = ogre.Math.intersects(ray, aabb)
            if res.first:
                return ray.getPoint(res.second - 0.1)
            else:
                return c
        else:
            return ObjectDepth._getCross(self, pos)
        
    def getContent(self):
        """Return content data and type.
        @return: (content type, content data, content format)
        """
        if self.eventContentUpdate:
            self.eventContentUpdate()
            
        return (self.content_type, self.content_data, self.content_format)
        
    def changeMode(self, _newMode):
        """Changes view mode for current sheet
        """
        old_mode = render_engine.viewMode
        render_engine.setMode(_newMode)
        
        if render_engine.viewMode is render_engine.Mode_Isometric:
            render_engine._ogreSceneManager.setFog(ogre.FOG_NONE)
        else:
            render_engine._ogreSceneManager.setFog(ogre.FOG_LINEAR, ogre.ColourValue(1.0, 1.0, 1.0, 1.0), 0.12, 10.0, 12.0)
        
        for child in self.__childObjects:
            child._needModeUpdate()
        
    def getType(self):
        """Returns object type
        """
        return "sheet"
        
    def getTmpSegment(self):
        return self.__tmpSegment
        
    def setLogic(self, _logic):
        """Sets new logic for a sheet
        """
        if _logic is None:  raise RuntimeError("Invalid logic object '%s'" % str(_logic))
        
        old = self.__logic
        self.__logic = _logic
        
        self.__logic._setSheet(self)
        if old is not None: old._setSheet(None)
        
        if old is None:
            render_engine.SceneNode.removeChild(self.sceneNodeNode, self.sceneNodeQuest)
        if self.__logic is None and old is not None:
            render_engine.SceneNode.addChild(self.sceneNodeNode, self.sceneNodeQuest) 
        
        if self.eventLogicChanged:  self.eventLogicChanged(old, _logic)
    
    def getLogic(self):
        return self.__logic
                   
    def mouseMoved(self, evt):
        """Mouse moved notification
        @param evt: event object with mouse state
        @type evt: OIS.MouseEvent
        @return: if message handled, then return True, else - False
        @see: OIS.MouseListener  
        """
        if self.eventMouseMoved:    return self.eventMouseMoved(evt)
        
        return False
    
    def mousePressed(self, evt, _id):
        """Mouse button pressed notification
        @param evt: event object with mouse state
        @type evt: OIS.MouseEvent
        @param _id: mouse button identificator
        @type _id: OIS.MouseButtonId
        @return: if message handled, then return True, else - False
        @see: OIS.MouseListener
        """
        if self.eventMousePressed:  return self.eventMousePressed(evt, _id)
        
        return False
    
    def mouseReleased(self, evt, _id):
        """Mouse button released notification
        @param evt: event object with mouse state
        @type evt: OIS.MouseEvent
        @param _id: mouse button identificator
        @type _id: OIS.MouseButtonId
        @return: if message handled, then return True, else - False
        @see: OIS.MouseEvent   
        """
        if self.eventMouseReleased: return self.eventMouseReleased(evt, _id)
        
        return False
    
    def keyPressed(self, evt):
        """Keyboard button pressed notification
        @param evt: event object with keyboard state
        @type evt: OIS.KeyEvent
        @return: if message handled, then return True, else - False
        @see: OIS.KeyboardListener  
        """
        if self.eventKeyPressed:    return self.eventKeyPressed(evt)
        
        return False
    
    def keyReleased(self, evt):
        """Keyboard button released notification
        @param evt: event object with keyboard state
        @type evt: OIS.KeyEvent
        @return: if message handled, then return True, else - False
        @see: OIS.KeyboardListener  
        """
        if self.eventKeyReleased:   self.eventKeyReleased(evt)
        
        return False
    
    def _intersectNodes(self, ray):
        """Finds nodes that intersects with ray
        @param ray: intersection ray
        @type ray: ogre.Ray  
        """
        pass  

    def _createBorder(self, width, height):
        """Creates border for a sheet when it's not in a root mode
        @param width: border width
        @type width: float
        @param heigt: border height
        @type height: float    
        """
        if self.manualBorder:    render_engine.SceneManager.destroyManualObject(self.manualBorder)
        self.manualBorder = render_engine.SceneManager.createManualObject("SheetBorder_" + str(self))        
        dx = 0.25
        dy = 0.25
        dz = 0.25
        x = width/2
        y = height/2

        verts = [ 
                 # front side
                    ((-x,       -y,         dz),     (-0.57735,-0.57735,0.57735)),
                    ((-x + dx,  -y + dy,    dz),     (0.57735,0.57735,0.57735)),
                    ((-x,       y,          dz),     (-0.57735,0.57735,0.57735)),
                    ((-x + dx,  y - dy,     dz),     (0.57735,-0.57735,0.57735)),     
                    ((x,        y,          dz),     (0.57735,0.57735,0.57735)),
                    ((x - dx,   y - dy,     dz),     (-0.57735,-0.57735,0.57735)),
                    ((x,        -y,         dz),     (0.57735,-0.57735,0.57735)),
                    ((x - dx,   -y + dy,    dz),     (-0.57735,0.57735,0.57735)),

                 # back side
                    ((-x,       -y,         -dz),    (-0.57735,-0.57735,-0.57735)),
                    ((-x + dx,  -y + dy,    -dz),    (0.57735,0.57735,-0.57735)),
                    ((-x,       y,          -dz),    (-0.57735,0.57735,-0.57735)),
                    ((-x + dx,  y - dy,     -dz),    (0.57735,-0.57735,-0.57735)),     
                    ((x,        y,          -dz),    (0.57735,0.57735,-0.57735)),
                    ((x - dx,   y - dy,     -dz),    (-0.57735,-0.57735,-0.57735)),
                    ((x,        -y,         -dz),    (0.57735,-0.57735,-0.57735)),
                    ((x - dx,   -y + dy,    -dz),    (-0.57735,0.57735,-0.57735)),
                ]
# vertexes:        
#            10________________12
#             /|  ________    /|
#            / | |11    13|  / |
#           /  | |9_____15| /  |
#          /  8|___________/   |14
#       2 /___/___________/4  / 
#        |   ________    |   /
#        |  |3      5|   |  /
#        |  |1______7|   | /
#        |_______________|/
#       0                 6
        indexs = [0,1,2,3,4,5,6,7,1,
                  9,3,11,5,13,7,15,9,
                  8,11,10,13,12,15,14,8,
                  0,10,2,12,4,14,6,0,1]

        self.manualBorder.begin(self.material_border, ogre.RenderOperation.OT_TRIANGLE_STRIP)        
        
        for v, n in verts:
            self.manualBorder.position(v)
            self.manualBorder.normal(n)
            
        for i in indexs:
            self.manualBorder.index(i)
        
        self.manualBorder.end()
#        SceneNode = sceneManager.createSceneNode()
#        
#        SceneNode.attachObject(self.manualBorder)        
#        sceneManager.getRootSceneNode().addChild(SceneNode)
#        self.border = SceneNode
        
    def _createPlane(self, width, height):
        """Creates plane for a none root mode, that will contain screen
        @param width: plane width
        @type width: float
        @param height: plane height
        @type height: float    
        """
        if self.manualPlane:    render_engine.SceneManager.destroyManualObject(self.manualPlane)
        self.manualPlane = render_engine.SceneManager.createManualObject("SheetPlane_" + str(self))
        
        dx = width / 2.0
        dy = height / 2.0
        
        self.manualPlane.begin("empty", ogre.RenderOperation.OT_TRIANGLE_STRIP)
        
        # vertexes
        vpos = [(-dx, -dy, 0), (dx, -dy, 0), (dx, dy, 0), (-dx, dy, 0)]
        vtex = [[0, 1], [1, 1], [1, 0], [0, 0]]
        self.manualPlane.position(vpos[0])
        self.manualPlane.textureCoord(vtex[0][0], vtex[0][1])
        self.manualPlane.position(vpos[1])
        self.manualPlane.textureCoord(vtex[1][0], vtex[1][1])
        self.manualPlane.position(vpos[2])
        self.manualPlane.textureCoord(vtex[2][0], vtex[2][1])
        self.manualPlane.position(vpos[3])
        self.manualPlane.textureCoord(vtex[3][0], vtex[3][1])
        # indexes    
        vind = [0, 1, 2, 3, 0]
        for ind in vind:
            self.manualPlane.index(ind)
        
        self.manualPlane.end()
        
    def _createNode(self):
        """Creates node for minimized content mode
        """
        # FIXME: make function thread safe
        
        import suit.core.environment as env
        self.sceneNodeNode = render_engine.SceneManager.createSceneNode()
        for mesh in env.cont_min_node:
            ent = render_engine.SceneManager.createEntity(str(self) + str(mesh), mesh) 
            self.entitiesNode.append(ent)
            self.sceneNodeNode.attachObject(ent)
        
        self.sceneNodeQuest = render_engine.SceneManager.createSceneNode()
        self.entityQuest = render_engine.SceneManager.createEntity("%s_quest" % str(self), env.cont_min_node_quet)
        self.sceneNodeQuest.attachObject(self.entityQuest)
        render_engine.SceneNode.addChild(self.sceneNodeNode, self.sceneNodeQuest)
        
    def hideContent(self):
        """Hides border in root mode
        """ 
        if self.isRoot:
            raise RuntimeWarning("Sheet isn't in root mode")
        
        if self.sceneNodeBorder:
            self.sceneNode.removeChild(self.sceneNodeBorder)
        self.sceneNode.addChild(self.sceneNodeNode)
        self.sceneNode._update(True, False)
        
        self.isContentShow = False
        self.needStateUpdate = True
        self.needViewUpdate = True
        self.needPositionUpdate = True
        self.needUpdate = True
        
        self._needLinkedUpdate()
    
    def showContent(self):
        """Shows border in none root mode
        """
        # creating border 
        if self.manualBorder is None:
            self._createBorder(5, 5)
        # creating surface for an image    
        if self.manualPlane is None:
            self._createPlane(3.5, 3.5)
            
        # creating scene node
        if self.sceneNodeBorder is None:
            self.sceneNodeBorder = render_engine.SceneManager.createSceneNode()
            # attaching objects
            self.sceneNodeBorder.attachObject(self.manualBorder)
            self.sceneNodeBorder.attachObject(self.manualPlane)
            
        # attaching border node to object node
        self.sceneNode.removeChild(self.sceneNodeNode)
        self.sceneNode.addChild(self.sceneNodeBorder)
        
        self.sceneNode._update(True, False)
        
        self.isContentShow = True
        self.needStateUpdate = True
        self.needViewUpdate = True
        self.needPositionUpdate = True
        self.needUpdate = True
        
        self._needLinkedUpdate()
        
    def isContentShowing(self):
        """Return True, if content is showing; otherwise return False
        """
        return self.isContentShow
    
    def _onRoot(self, isRoot):
        """Calls when changing root mode
        """
        if isRoot:
            render_engine.SceneNode.addRootChild(self.sceneNodeChilds)
            # updating child objects
            for child in self.__childObjects:
                child._attachedScene()
            
            if render_engine.viewMode is render_engine.Mode_Isometric:
                render_engine.SceneManager.setScale(self.root_scale2d)
            else:
                render_engine.SceneManager.setScale(self.root_scale3d)
            
            # restore camera settings
            render_engine._ogreCameraNode.setPosition(self.camera_pos)
            render_engine._ogreCamera.setOrientation(self.camera_orient)
            render_engine.setMode(self.view_mode)
        else:
            render_engine.SceneNode.removeRootChild(self.sceneNodeChilds)
            # updating child objects
            for child in self.__childObjects:
                child._detachedScene()
                
            render_engine.SceneManager.resetScale()
            
            # store camera settings
            self.camera_pos = render_engine._ogreCameraNode.getPosition()
            self.camera_orient = render_engine._ogreCamera.getOrientation()
            self.view_mode = render_engine.viewMode
                            
        self.isRoot = isRoot
        if self.eventRootChanged:   self.eventRootChanged(self.isRoot)
        
    def setScale(self, _scale):
        """Sets new scale
        """
        if render_engine.viewMode is render_engine.Mode_Isometric:
            self.root_scale2d = _scale
            render_engine.SceneManager.setScale(self.root_scale2d)
        else:
            self.root_scale3d = _scale
            render_engine.SceneManager.setScale(self.root_scale3d)
        # updating childs
        for obj in self.__childObjects:
            obj.setPosition(obj.getPosition())
            
    def getScale(self):
        if render_engine.viewMode is render_engine.Mode_Isometric:
            return self.root_scale2d
        else:
            return self.root_scale3d
    
    def resetScale(self):
        """Resets scale to default
        """
        if render_engine.viewMode is render_engine.Mode_Isometric:
            self.root_scale2d = render_engine.scale2d_init
        else:
            self.root_scale3d = render_engine.scale3d_init
            
        render_engine.SceneManager.resetScale()
        # updating childs
        for obj in self.__childObjects:
            obj.setPosition(obj.getPosition())
    
    def addChildList(self, childs):
        """Adds list of child objects
        @see: ObjectSheet.addChild
        """
        for child in childs:
            self.addChild(child)
    
    def addChild(self, child):
        """Adds child object
        """
        if (child in self.__childObjects):
            raise AssertionError('Child object already exists. Please use \'haveChild\' method')
        
        # register object in childs
        self.__childObjects.append(child)
        # remove old parent
        if child.parent is not None:
            childparent.removeChild(child)
        child.parent = self 
        self.sceneNodeChilds.addChild(child.sceneNode)
        # notify listener
        if self.eventChildAppend is not None:   self.eventChildAppend(child)
        
        # notify that node attached to scene if sheet is root
        if self.isRoot:
            child._attachedScene()
        else:
            child._detachedScene()
            
        # adding child to layout group
        if self.__layoutGroup:  self.__layoutGroup.appendObject(child)
        
        # synchronizing windows hierarchy and sc-representation of hierarchy
        if isinstance(child, ObjectSheet) and child._getScAddr() is not None:
            self.addScChildSheet(child)
            
    def addScChildSheet(self, child):
        p_addr = self._getScAddr()
        c_addr = child._getScAddr()
        
        if p_addr is None:  raise RuntimeError("Parent addr is None, you need to add it to another window as child at first")
        
        kernel = core.Kernel.getSingleton()
        session = kernel.session()
        segment = kernel.segment()
        import suit.core.sc_utils as sc_utils
        import suit.core.keynodes as keynodes
        import sc_core.pm as sc
        
        # creating sc-node that will be designate child window
        if c_addr is None:    
            c_addr = sc_utils.createNodeElement(session, segment, sc.SC_CONST)
            child._setScAddr(c_addr)
            
        # creating hierarchy
        sheaf = sc_utils.createPairBinaryOrient(session, segment, p_addr, c_addr, sc.SC_CONST)
        sc_utils.createPairPosPerm(session, segment, keynodes.ui.nrel_child_window, sheaf, sc.SC_CONST)
        #sc_utils.createPair(session, segment, keynodes.ui.sc_window, c_addr, sc.SC_A_CONST | sc.SC_POS | sc.SC_TEMPORARY)
    
    def removeChildList(self, childs):
        """Removes list of child objects
        @see: ObjectSheet.removeChild
        """
        for child in childs:
            self.removeChild(child)
    
    def removeChild(self, child):
        """Removes child object from sheet
        """
        child.parent = None
        self.__childObjects.remove(child)
        self.sceneNodeChilds.removeChild(child.sceneNode)
        if self.eventChildRemove is not None:   self.eventChildRemove(child)
        
        # removing object from layout group
        if self.__layoutGroup is not None:  self.__layoutGroup.removeObject(child)
        
        # remove from selected objects
        if child in self.selectedObjects:
            self.selectedObjects.remove(child)
            # notify about selection changed
            if self.eventSelectionChanged is not None:
                self.eventSelectionChanged()
        
        # synchronizing windows hierarchy and sc-representation of hierarchy
        if isinstance(child, ObjectSheet) and child._getScAddr() is not None:
            self.removeScChildSheet(child)
            
    def removeScChildSheet(self, child):
        p_addr = self._getScAddr()
        c_addr = child._getScAddr()
        
        assert p_addr is not None
        assert c_addr is not None
        
        kernel = core.Kernel.getSingleton()
        session = kernel.session()
        segment = kernel.segment()
        import suit.core.sc_utils as sc_utils
        import suit.core.keynodes as keynodes
        import sc_core.pm as sc
        
        sr = sc_utils.searchFullBinPairsAttrToNode(session, c_addr, keynodes.ui.nrel_child_window, sc.SC_CONST)
        if sr is None:  raise RuntimeError("Can't find parent window designation in sc-memory")
#        if sr[0].this != p_addr.this: raise RuntimeError("Knowledge base is broken. It has invalid parent for window %s" % str(c_addr))
        
        for res in sr:
            if res[0].this != p_addr.this: raise RuntimeError("Knowledge base is broken. It has invalid parent for window %s" % str(c_addr))
            session.erase_el(res[1]) 
            
            
    def setLayoutGroup(self, _layout_group):
        """Sets new layout group to sheet
        
        @param _layout_group:    new layout group
        @type _layout_group:    LayoutGroup
        """
        if self.__layoutGroup is not None:
            self.__layoutGroup.removeAllObjects()
            
        if _layout_group is not None:
            _layout_group.removeAllObjects()
            _layout_group.appendListOfObjects(self.__childObjects)
        # FIXME:    make thread safe by using queues for child add/remove or using lock objects
        
        self.__layoutGroup = _layout_group
        
    def getLayoutGroup(self):
        """Returns current layout group
        """
        return self.__layoutGroup         
        
    def haveChild(self, child):
        """Check if child object already exists
        """
        if self.eventHaveChild is not None:
            return self.eventHaveChild(child)
        
        return self.__childObjects.count(child) > 0
    
    def getChilds(self):
        """Returns list of existing childs 
        """        
        return self.__childObjects
    
    def getRoot(self):
        return self.isRoot
    
    def _setScAddr(self, sc_addr):
        """@see: ScObject._setScAddr
        """
        if self._getScAddr():
            self._removeFromScWindows()
            if self.parent is not None:
                self.parent.removeScChildSheet(self)
        
        ObjectDepth._setScAddr(self, sc_addr)
        
        if self._getScAddr():
            self._addToScWindows()
            if self.parent is not None:
                self.parent.addScChildSheet(self)

    def  _addToScWindows(self):
        """Adds sc_addr that designate sheet into sc-windows set
        """
        sc_utils.createPairPosPerm(kernel.session(), self.__tmpSegment, keynodes.ui.sc_window, self._getScAddr(), sc_core.pm.SC_CONST)
    
    def _removeFromScWindows(self):
        """Removes sc_addr that designate sheet from sc-windows set
        """
        # remove from sc-window set
        session = kernel.session()
        res = session.search_one_shot(session.sc_constraint_new(sc_core.constants.CONSTR_3_f_a_f,
                                                                                        keynodes.ui.sc_window,
                                                                                        sc_core.pm.SC_A_CONST | sc_core.pm.SC_POS,
                                                                                        self._getScAddr()), True, 3)
        assert res is not None
        session.erase_el(res[1])
    
    # *************
    # * Selection *
    # *************
    def getSelected(self):
        """Returns list of selected objects
        """
        return self.selectedObjects
    
    def haveSelected(self):
        """Check if there are any selection on sheet
        """
        return len(self.selectedObjects) > 0
    
    def select(self, _obj):
        """Append object to selected on sheet 
        """
        if _obj._getSelected() is True:
            raise RuntimeError("Object '%s' already selected" % str(_obj))
        self.selectedObjects.append(_obj)
        _obj._setSelected(True)
#        _obj.setState(Object.OS_Selected)
        
        if self.eventSelectionChanged is not None:  self.eventSelectionChanged()
    
    def selectAll(self):
        """Selecting all objects on sheet
        """
        for obj in self.selectedObjects:
            obj._setSecleted(False)
        self.selectedObjects = []
        for obj in self.__childObjects:
            self.selectedObjects.append(obj)
            obj._setSelected(True)
#            obj.setState(Object.OS_Selected)
            
        if self.eventSelectionChanged is not None:  self.eventSelectionChanged()
    
    def unselect(self, _obj):
        """Remove object from selected on sheet
        """
        if _obj._getSelected() is False:
            raise RuntimeError("Object '%s' isn't selected" % str(_obj))
        self.selectedObjects.remove(_obj)
        _obj._setSelected(False)
#        _obj.resetState()
        
        if self.eventSelectionChanged is not None:  self.eventSelectionChanged()
        
    def unselectAll(self):
        """Unselecting all objects on sheet
        """
        for obj in self.selectedObjects:
            obj._setSelected(False)
#            obj.resetState()#setState(Object.OS_Normal)
                
        self.selectedObjects = []
        
        if self.eventSelectionChanged is not None:  self.eventSelectionChanged()
            

class ObjectText(Object):
    """Represents object to show overlay text
    There is screen_pos variable. It stores tuple of current text coordinates in window.
    """
    #@todo: Rewrite text object
    def __init__(self, pos, owner):
        Object.__init__(self)
        self.owner = owner
        self.position = pos
        self.textValue = ""
        
        # variable to store current position on screen
        self.screen_pos = None
        
        # update flags
        self.needTextValueUpdate = False
        self.needShowUpdate = False
        self.needTextSizeReset = False
        self.needAlphaUpdate = False
        
        # default font height
        self.fontHeightDefault = 0
        
        #default distance to owner
        self.distToOwner = 5
        
        #possible relative positions for identifier
        self.idtfPositions = {}
        
        #current relative position of identifier
        self.currentPos = "BottomRight"
        
        #tooltip for identifier
        self.tooltip = None
        
        #visible length of identifier  
        self.idtfVisibleLen = 10
        
        # widgets
        self.__panel = None
        self.__text = None
        self.__visibility = True
       
        # events for edit finishing
        self.eventEditApply = None
        self.eventEditCancel = None
        self.eventEditFinished = None
    
    def __del__(self):
        Object.__del__(self)
        if self.__text:  self._destroy_text()
        
    def delete(self):
        """Deletion message
        """
        Object.__del__(self)
        
        self.owner = None
        if self.__text:
            self._destroy_text()
            
    def _updateSize(self, dist):
        """Updates font size depend on distance
        """
        if not self.__visibility or self.__text is None or self.__panel is None:
            return
        
        r = max([55 - dist * 1.5, 10])
        self.__text.setFontHeight(int(r))
        self._updateWidgets()
        alpha = 1.0
        if dist > 12.0: 
            alpha = r / 35.0
        alpha = max([0.0, min([1.0, alpha])])
        self.__panel.setAlpha(alpha)
        
    def _eventToolTip(self, _widget, _info):
        """Event on tooltip state change
        """ 
        if self.textValue is None:
            return
          
        if _info.type == mygui.ToolTipInfo.Show:
            if self.tooltip is not None: return
            self.tooltip = render_engine.Gui.createWidgetT("Window",
                                                           "ToolTipPanel",
                                                           mygui.IntCoord(0, 0, 10, 10),
                                                           mygui.Align(),
                                                           "ToolTip")           
            
            text = self.tooltip.createWidgetT("StaticText",
                                              "ToolTipText",
                                              mygui.IntCoord(12, 12, 0, 0),
                                              mygui.Align())
            
            text.setCaption(self.textValue)
            tsize = text.getTextSize()
            self.tooltip.setSize(tsize.width + 24, tsize.height + 24)
            text.setSize(tsize)
            
            x = _info.point.left + 20
            y = _info.point.top + 20
            
            x = min([x, render_engine.Window.width - tsize.width - 30])
            y = min([y, render_engine.Window.height - tsize.height - 30])
            
            self.tooltip.setPosition(x, y)       
            self.tooltip.setVisible(True)
            self.tooltip.setAlpha(1.0)
        
        elif _info.type == mygui.ToolTipInfo.Hide and self.tooltip is not None:
            render_engine.Gui.destroyWidget(self.tooltip)
            self.tooltip = None
            self.tooltip_widget_name = None
            
    def _update(self, timeSinceLastFrame):
        """Update text object
        """
        if render_engine.viewMode is render_engine.Mode_Perspective:
            if self.owner is not None:
                self._updateSize(self.owner.getPosition().distance(render_engine._ogreCameraNode.getPosition()))
                self.needTextSizeReset = True
        else:
            if self.needTextSizeReset:
                self.__text.setFontHeight(self.fontHeightDefault)
                self.__panel.setAlpha(1.0)
                self._updateWidgets()
                self.needTextSizeReset = False
        
        Object._update(self, timeSinceLastFrame)
        
    def _updateWidgets(self):
        """Update widgets depending on new text size
        """
        sz = self.__text.getTextSize()
        self.__text.setSize(sz.width + 5, sz.height)
        self.__panel.setSize(sz.width + 20, sz.height + 8)
                
    def _updateView(self):
        """Updates view representation of text.
        @warning: By default it calls from _update function. In this case it's thread safe.
        @attention: Function is thread safe just if it calls in main thread.
        """
        Object._updateView(self)
        
        if self.needTextValueUpdate:
            self.update_text_value()
            self.update_IdtfPositions()
            self.needTextValueUpdate = False
        
        if self.needPositionUpdate:
            self.update_position()
            self.needPositionUpdate = False
            
        if self.needShowUpdate:
            self.update_show()
            self.needShowUpdate = False
            
        if self.needAlphaUpdate:
            self.update_alpha()
            self.needAlphaUpdate = False
    
    def update_position(self):
        """Updates text position.
        @warning: By default it calls from _updateView function. In this case it's thread safe.
        @attention: Function is thread safe just if it calls in main thread.
        """
        if self.__text is None: return
        
        pos = render_engine.pos3dTo2dWindow(self.owner.getPosition())
        if pos is not None:
            x, y = pos
            idtfPos = self.idtfPositions[self.currentPos]
            self.__panel.setPosition(x + idtfPos[0], y + idtfPos[1])
            self.screen_pos = pos
            
    def update_text_value(self):
        """Updates widget text
        @warning: By default it calls from _updateView function. In this case it's thread safe.
        @attention: Function is thread safe just if it calls in main thread.
        """
        if self.__text is None: self._create_text()
        visiblePart = self.textValue[:self.idtfVisibleLen]
        if not visiblePart == self.textValue:
            visiblePart += u"..."
            
        self.__text.setCaption(visiblePart)
        self._updateWidgets()
#        sz = self.__text.getTextSize()
#        self.__text.setSize(sz.width, sz.height)
        
        if self.__panel is not None:
            if self.isNeedToolTip():
                self.__panel.setNeedToolTip(True)
            else:
                self.__panel.setNeedToolTip(False)
        
    def isNeedToolTip(self):
        if self.idtfVisibleLen < len(str(self.textValue)):
            return True
        return False   
    
    def update_show(self):
        """Updates text visibility
        @warning: By default it calls from _updateView function. In this case it's thread safe.
        @attention: Function is thread safe just if it calls in main thread.
        """
        if self.__text is not None: self.__panel.setVisible(self.__visibility)
        
    def update_alpha(self):
        """Updates alpha
        """
        if self.__panel is not None:
            self.__panel.setAlpha(self.alpha)
    
    def _eventMouseButtonPressed(self, _sender, _left, _top, _id):
        """Event on identifier pressed
        """ 
        if self.tooltip is not None:
            render_engine.Gui.destroyWidget(self.tooltip)  
            self.tooltip = None
        self.__panel.setNeedToolTip(False)
        
    
    def _eventMouseButtonReleased(self, _sender, _left, _top, _id):
        """Event on identifier released
        """ 
        if self.isNeedToolTip():
            self.__panel.setNeedToolTip(True)
         
    
    def _eventMouseDrag(self, _sender, _left, _top):
        """Event on identifier drag 
        """ 
        if _left <= self.screen_pos[0] and _top >= self.screen_pos[1]:
            self.currentPos = "BottomLeft"
        
        elif _left <= self.screen_pos[0] and _top < self.screen_pos[1]:
            self.currentPos = "TopLeft"
       
        elif _left > self.screen_pos[0] and _top < self.screen_pos[1]:
            self.currentPos = "TopRight"
            
        elif _left > self.screen_pos[0] and _top >= self.screen_pos[1]:
            self.currentPos = "BottomRight"
        
        self.update_position()
       
    def update_IdtfPositions(self):
        """Updates possible identifier positions
        @warning: By default it calls from _updateView function. In this case it's thread safe.
        @attention: Function is thread safe just if it calls in main thread.
        """
        dx, dy = self.__panel.getWidth(), self.__panel.getHeight() 
        self.idtfPositions = {"BottomLeft" : (-dx - self.distToOwner, self.distToOwner),
                    "TopLeft" : (-dx - self.distToOwner, -dy - self.distToOwner),
                    "TopRight" : (self.distToOwner, -dy -self.distToOwner),
                    "BottomRight" : (self.distToOwner, self.distToOwner)}
        self.needPositionUpdate = True
    
    def _create_text(self):
        """Creates text widget
        """
        assert self.__text is None
        self.__panel = render_engine.Gui.createWidgetT("Widget", "IdtfPanel", mygui.IntCoord(0, 0, 0, 0), mygui.Align(), "Middle", "")
        self.__text = self.__panel.createWidgetT("StaticText", "Idtf", mygui.IntCoord(6, 3, 0, 0), mygui.Align())
        # disabling widget to disable gui event processing on it
        self.__text.setEnabled(False)
        
        self.__panel.subscribeEventToolTip(self, "_eventToolTip")
        self.__panel.subscribeEventMouseButtonPressed(self, "_eventMouseButtonPressed")
        self.__panel.subscribeEventMouseButtonReleased(self, "_eventMouseButtonReleased")
        self.__panel.subscribeEventMouseDrag(self, "_eventMouseDrag")
        
        self.needPositionUpdate = True
        self.fontHeightDefault = self.__text.getFontHeight()
    
    def _destroy_text(self):
        """Destroys text widget
        """
        assert self.__text is not None
        render_engine.Gui.destroyWidget(self.__text)
        render_engine.Gui.destroyWidget(self.__panel)
        self.__text = None
        self.__panel = None
        
    def show(self):
        """Makes text visible
        This function is thread safe. You can call it from any thread. 
        """
        self.needViewUpdate = True
        self.needShowUpdate = True
        self.__visibility = True
        
    def hide(self):
        """Makes text invisible
        This function is thread safe. You can call it from any thread.
        """
        self.needViewUpdate = True
        self.needShowUpdate = True
        self.__visibility = False
        
    def setText(self, _text):
        """Sets text value
        This function is thread safe. You can call it from any thread.
        """
        self.needTextValueUpdate = True
        self.needViewUpdate = True
        self.textValue = _text
        
    def getText(self):
        """Returns text value
        This function is thread safe. You can call it from any thread.
        """
        return self.textValue
    
    def setAlpha(self, _alpha):
        """Set new text alpha
        """
        self.alpha = _alpha
        self.needUpdate = True
        self.needViewUpdate = True
        self.needAlphaUpdate = True
        
    def getAlpha(self):
        """Return current alpha value
        """
        return self.alpha
    

class BaseLogic(Object):
    """Base class implementation for logic
    """
    def __init__(self):
        """Constructor
        """
        Object.__init__(self)
        self.__sheet = None
    
    def __del__(self):
        Object.__del__(self)
    
    def delete(self):
        """Deletion message
        """
        pass
    
    def _setSheet(self, _sheet):
        """Method to set sheet for logic
        @attention: don't use that method to set sheet for a logic. You need to call
        setLogic method in ObjectSheet 
        """
        self.__sheet = _sheet
        
    def _getSheet(self):
        """Returns sheet object
        """
        return self.__sheet
    
        
class Factory(ScObject):
    """Base class for factories
    """
    def __init__(self, _func_creat):
        ScObject.__init__(self)        
        self.type = None
        # function of object instance creating
        self.__func_creat = _func_creat
        
    def __del__(self):
        ScObject.__del__(self)
            
    def _createInstance(self, *args):
        """Create instance of object
        """
        return self.__func_creat(*args) 


class Translator:
    def __init__(self):
        pass
    
    def __del__(self):
        pass
    
    def translate(self, _input, _output):
        """Translates input data to output
        @param _input:    input data
        @type _input:    sc_global_addr
        @param _output:    output data
        @type _output:    sc_global_addr
        
        @return: if there were any errors during translation, then return list of errors, else - None.
        Each error is a tuple <object, error description>
        @rtype: list 
        """
        res = self.translate_impl(_input, _output)
        if len(res) == 0:   return None 
        return res
    
    def translate_impl(self, _input, _output):
        """Translation implementation.
        @attention: only for internal usage. Don't call it directly, use translate function instead.
        @return: return list of errors. Each error is a tuple <object, error description>
        @rtype: list
        """
        return []