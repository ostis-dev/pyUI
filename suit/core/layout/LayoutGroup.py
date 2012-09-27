
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
Created on 26.10.2009

@author: Denis Koronchik
'''

import suit.core.objects as objects
import thread
import LayoutOrder
from LayoutManager import LayoutManager

class LayoutGroup:
    """Class to grouping object for layout.
     
    @attention: To delete layout group you need to call delete function.
    There are events, that user can subscribe:
        - eventStart - function that calls when layout started. Signature:
            function(LayoutGroup).
        - eventFinish - function that calls when layout finished. Signature:
            function(LayoutGroup)
        - eventOrder - function that calls when need to make layout objects order. 
            It returns list of ordered objects. Signature:
            function(LayoutGroup)
    """
    def __init__(self):
        """Constructor
        @param _objects: list of group objects
        @type _object: list  
        """
        self.lock = thread.allocate_lock()  # lock object for multithreading layout
        
        self.objects = []   # list of group objects   
        
        self.need_layout = False
        
  
        # callbacks
        self.eventStart = None
        self.eventFinish = None
        self.eventOrder = None
        
        self.deleted = False
        
        self.playing = True 
        
        # appending to layout manager
        LayoutManager.getSingleton().addLayoutGroup(self)
    
    def __del__(self):
        """Destructor
        """
        print "__del__ in %s" % str(self)
    
    def delete(self):
        """Layout group deletion
        """
        LayoutManager.getSingleton().removeLayoutGroup(self)
        import time
        self.lock.acquire()
        self.deleted = True        
        self.objects = None
        self.lock.release()
    
    def _addObjectToGroup(self, _object):
        """Adds object to list 
        """
        if isinstance(_object, objects.Object):
            self.objects.append(_object)
        else:
            return False
        
        return True
        
    def _removeObjectFromGroup(self, _object):
        """Removes object from list
        """
        if isinstance(_object, objects.Object):
            self.objects.remove(_object)
        else:
            return False
        
        return True
    
    def _removeAllObjectsFromGroup(self):
        """Removes all objects from group
        """
        self.objects = []
    
    def appendObject(self, _object):
        """Appends object to group.
        @param _object: object that adds to group
        @type _object: ObjectDepth           
        """
        self.lock.acquire()
        
        self.need_layout = True
        
        try:
            res = self._addObjectToGroup(_object)
        except:
            res = False
        if not res:
            self.lock.release()
            raise TypeError("Type '%s' doesn't supported by group '%s'" % (type(_object), str(self)))
        
        self.lock.release()
        
    def appendListOfObjects(self, _objects):
        """Appends list of objects.
        It's more faster than append objects one by one, because
        it makes one lock for all objects.
        """
        self.lock.acquire()
        
        self.need_layout = True
        
        for obj in _objects:
            try:
                res = self._addObjectToGroup(obj)
            except:
                import sys, traceback
                print "Error:", sys.exc_info()[0]
                traceback.print_exc(file=sys.stdout)
            if not res:
                self.lock.release()
                raise TypeError("Type '%s' doesn't supported by group '%s'" % (type(_object), str(self)))
        
        self.lock.release()
        
    def removeObject(self, _object):
        """Removes object from a group.
        @param _object: object to remove
        @type _object: ObjectDepth  
        """
        self.lock.acquire()
        
        self.need_layout = True
        
        try:
            res = self._removeObjectFromGroup(_object)
        except:
            import sys, traceback
            print "Error:", sys.exc_info()[0]
            traceback.print_exc(file=sys.stdout)
        if not res:
            self.lock.release()
            raise TypeError("Type '%s' doesn't supported by group '%s'" % (type(_object), str(self)))
            
        self.lock.release()
        
    def removeAllObjects(self):
        """Removes all objects from group
        """
        self.lock.acquire()
        
        try:
            self._removeAllObjectsFromGroup()
        except:
            self.lock.release()
            import sys, traceback
            print "Error:", sys.exc_info()[0]
            traceback.print_exc(file=sys.stdout)
        
        self.lock.release()
        
    def _mode_changed(self):
        """Notification of mode changing 
        """
        # FIXME:    make notification with layout manager
        self.lock.acquire()
        try:
            self._mode_changed_impl()
        except:
            import sys, traceback
            print "Error:", sys.exc_info()[0]
            traceback.print_exc(file=sys.stdout)
        finally:
            self.lock.release()
            
        
    def _mode_changed_impl(self):
        """Implementation of mode changing
        """
        self.need_layout = True
    
    def _layout_start(self):
        """Layout start notification
        """
        self.lock.acquire()
        if self.eventStart is not None:
            try:
                self.eventStart(self)
            except:
                import sys, traceback
                print "Error:", sys.exc_info()[0]
                traceback.print_exc(file=sys.stdout)
        
    def _layout_finish(self):
        """Layout finish notification
        """
        self.lock.release()
        if self.eventFinish is not None:
            try:
                self.eventFinish(self)
            except:
                import sys, traceback
                print "Error:", sys.exc_info()[0]
                traceback.print_exc(file=sys.stdout)
    
    def play(self):
        self.playing = True
        
    def stop(self):
        self.playing = False
        
    def isPlaying(self):
        return self.playing
                
    def _apply(self):
        """Applies layout for a group. It calls from _layout function.
        @attention: Only for internal usage. Not thread safely if it called directly.
        """
        self.need_layout = False
                
    def _layout(self, _force = False):
        """Layout objects in group.
        @param _force: flag to force layout process if even it doesn't need.
        @type _force: bool  
        """
        # skipping layout
        if (not self.need_layout and not _force) or not self.playing:
            return 
        
        self._layout_start()
        try:
            self._apply()
        finally:
            self._layout_finish()
        
    def _update(self, _timeSinceLastUpdate):
        """Updates layouting
        """
        if self.need_layout and not self.deleted:
            self._layout(True)
            
    def relayout(self):
        """Realyout group
        """
        self.need_layout = True
        self.play = True
        
class LayoutGroupDepth(LayoutGroup):
    """Base layout group for depth objects
    All objects sorted by types:
        - line objects - line objects, that linked to their begin and end objects. Base class ObjectLine
        - node objects - objects, that represents nodes (point, scg-node, cube, ...). Base class ObjectDepth
        - sheet objects - objects that represents sheet. Base class ObjectSheet.
        - group objects - object groups. Base class LayoutGroup.
    """
    
    def __init__(self):
        LayoutGroup.__init__(self)
        
        self.lines = []     # list of line objects
        self.nodes = []     # list of node objects
        self.sheets = []    # list of sheet objects
        self.groups = []    # list of group objects
        
        
    def __del__(self):
        LayoutGroup.__del__(self)
        
        
    def delete(self):
        """Deletion message
        """
        LayoutGroup.delete(self)
        self.lines = None
        self.nodes = None
        self.sheets = None
        self.groups = None
        
    def _addObjectToGroup(self, _object):
        """Adds object to group and sort them by types            
        """
        LayoutGroup._addObjectToGroup(self, _object)
        
        if isinstance(_object, objects.ObjectSheet):
            self.sheets.append(_object)
        elif isinstance(_object, objects.ObjectLine):
            self.lines.append(_object)
        elif isinstance(_object, LayoutGroupDepth):
            self.groups.append(_object)
        elif isinstance(_object, objects.ObjectDepth):
            self.nodes.append(_object)
        else:
            return False
        
        return True
    
    def _removeObjectFromGroup(self, _object):
        """Removes object from group
        """
        LayoutGroup._removeObjectFromGroup(self, _object)
        
        if isinstance(_object, objects.ObjectSheet):
            self.sheets.remove(_object)
        elif isinstance(_object, objects.ObjectLine):
            self.lines.remove(_object)
        elif isinstance(_object, LayoutGroupDepth):
            self.groups.remove(_object)
        elif isinstance(_object, objects.ObjectDepth):
            self.nodes.remove(_object)
        else:
            return False
        
        return True
    
    def _removeAllObjectsFromGroup(self):
        """Remove all objects from group
        """
        LayoutGroup._removeAllObjectsFromGroup(self)
        self.sheets = []
        self.lines = []
        self.groups = []
        self.nodes = []
    
class LayoutGroupOverlay(LayoutGroup):
    """Base layout group for an overlay objects
    """
    
    def __init__(self):
        """Constructor
        """
        LayoutGroup.__init__(self)
        self.overlays = []
    
    def __del__(self):
        """Destructor
        """
        LayoutGroup.__del__(self)
        
    def delete(self):
        """Deletion message
        """
        LayoutGroup.delete(self)
        self.overlays = None
    
    def _addObjectToGroup(self, _object):
        """Adds object to group
        """
        LayoutGroup._addObjectToGroup(self, _object)
        if isinstance(_object, objects.ObjectOverlay):
            self.overlays.append(_object)
        else:
            return False
        
        return True
    
    def _removeObjectFromGroup(self, _object):
        """Removes object from group
        """
        LayoutGroup._removeObjectFromGroup(self, _object)
        if isinstance(_object, objects.ObjectOverlay):
            self.overlays.remove(_object)
        else:
            return False
        
        return True
        
    def _removeAllObjectsFromGroup(self):
        """Removes all objects from group
        """
        LayoutGroup._removeAllObjectsFromGroup(self)
        self.overlays = []