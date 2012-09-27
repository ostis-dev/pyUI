
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
Created on 28.01.2010

@author: Denis Koronchik
'''
from suit.core.utils import Singleton
import threading, thread
import time

class LayoutManager(Singleton, threading.Thread):
    """Class that controls layouting and run it in different thread.
    
    All layout group will be appended to layout manager for getting 
    updates in different from main thread. That will help to get layouting in other processor, so
    make system working more useful on multiprocessor systems.
    """
    def __init__(self):
        Singleton.__init__(self)
        threading.Thread.__init__(self)
        
        self.stoped = False
        self.finished = False
        self.started = False
        
        self.needModeChange = False
        
        # list of active layout groups
        self.__layoutGroups = []
        self.__addQueue = []
        self.__removeQueue = []
        
        # locks
        self.__add_lock = thread.allocate_lock()
        self.__remove_lock = thread.allocate_lock()
        
        # starting thread
        self.start()
    
    def run(self):
        self.started = True
        
        while not self.stoped:
            
            # updating groups
            for group in self.__layoutGroups:
                if self.needModeChange: group._mode_changed()
                group._update(0)    # FIXME:    make getting time since last update
            
            # removing groups
            self.__remove_lock.acquire()
            for group in self.__removeQueue:
                self.__layoutGroups.remove(group)
            self.__removeQueue = []
            self.__remove_lock.release()
            
            # adding groups from queue
            self.__add_lock.acquire()
            for group in self.__addQueue:
                group._mode_changed()
                self.__layoutGroups.append(group)
            self.__addQueue = []
            self.__add_lock.release()
            
            self.needModeChange = False
            
            time.sleep(0.03)            
        
        self.finished = True
        
    def stop(self):
        self.stoped = True
        
    def addLayoutGroup(self, _group):
        """Appends layout group for updates
        """
        self.__addQueue.append(_group)
        
    def removeLayoutGroup(self, _group):
        """Removes layout groups
        """
        self.__removeQueue.append(_group)
        
    def mode_changed(self):
        """Notification on mode changed
        """
        self.needModeChange = True