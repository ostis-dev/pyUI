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


# singleton base class
from ogre.renderer.OGRE._ogre_ import Math

class Singleton:
    """Ensure that a class has at most one instance.
    
    @cvar instances Existing instances.
    """
    instances = {}
    def __init__(self):
        """Constructor.
        """
        assert self.__class__ not in Singleton.instances.keys(), \
            "Class \"%s\" is a singleton." % self.__class__
        Singleton.instances[self.__class__] = self
        return
    # @classmethod
    def getSingleton(singletonClass):
        """Returns singleton instance.
        """
        instance = None
        if Singleton.instances.has_key(singletonClass):
            instance = Singleton.instances[singletonClass]
        #else:
        #    instance = singletonClass()
        return instance
    
    getSingleton = classmethod(getSingleton)
    
    
# log manager
class LogManager(Singleton):
    """Logs messages and status.
    
    """
    output_file = None
    
    def start_file_logging(self, file_name):
        """Start logging to file
        """
        self.fileName = file_name
        f = file(self.fileName, "w")
        f.close()
        self.message("Start logging")
        
    def stop_file_logging(self):
        """Stop logging to file
        """
        self.message("Stop logging")
    
    def __init__(self):
        """Constructor.
        """
        Singleton.__init__(self)
        self.clear()
        return
    
    def clear(self):
        """Clears the log.
        """
        self.messageList = []
        return
    
    def message(self, message, tabs = 0):
        """Write message to log
        """
        self.output_file = file(self.fileName, "a")
        msg = tabs * '\t' + message;
        self.messageList.append(msg)
        if (self.output_file != None):
            self.output_file.write(msg + '\n')
        self.output_file.close()
        print msg
    
    def logInit(self, message, tabs = 0):
        """Logs initialize message
        """
        self.message('[Initialize]: ' + message, tabs)
    
    def logRegister(self, message, tabs = 0):
        """Logs register message
        """
        self.message('[Register]: ' + message, tabs)
    
    def logUnregister(self, message, tabs = 0):
        """Logs unregister message
        """
        self.message('[Unregister]: ' + message, tabs)
    
    def logShutdown(self, message, tabs = 0):
        """Logs shutdown message
        """
        self.message('[Shutdown]: ' + message, tabs);
    
    def logInfo(self, message, tabs = 0):
        """Logs an info message.
        
           @param message message string
        """
        self.message('[Info]: ' + message, tabs)        
    
    def logWarning(self, message, tabs = 0):
        """Logs a warning message.
        
           @param message message string
        """
        self.message('[Warning]: ' + message, tabs)
    
    def logError(self, message, tabs = 0):
        """Logs an error message.
                       
           @param message message string
        """
        self.message('[Error]: ' + message, tabs)
    
    def logLoad(self, message, tabs = 0):
        """Logs an load message.
                  
           @param message message string
        """
        self.message('[Load]: ' + message, tabs)
    
    def logUnLoad(self, message, tabs = 0):
        """Logs an unload message.
                  
           @param message message string
        """
        self.message('[Unload]: ' + message, tabs)
    
    def getMessageList(self):
        """Returns the list of log messages.
        
           @return list of tuples (status, message)
        """
        return self.messageList
    
    def write(self, message):
        self.message(message)

def logMessage_init(message, tab = 1):
    LogManager.getSingleton().logInit(message, tab)

def logMessage_shutdown(message, tab = 1):
    LogManager.getSingleton().logShutdown(message, tab)


class AnimationUtils:

    LINEAR = 1
    CIRCLE = 2
    ELASTIC = 3
    POWER_OF_TWO = 4
    POWER_OF_FIVE = 5
    SINE = 6
    BACK = 7

    EASE_IN = 1
    EASE_OUT = 2
    EASE_IN_OUT = 3

    def __init__(self):
        return

    def animateValue(self, toValue, progress, animationType, easeAnimationType):
        delta = 1

        if easeAnimationType == self.EASE_IN:
            delta = self.deltaAnimation(progress, animationType)

        elif easeAnimationType == self.EASE_OUT:
            delta = 1 - self.deltaAnimation(1 - progress, animationType)

        elif easeAnimationType == self.EASE_IN_OUT:
            if progress < 0.5:
                delta =  self.deltaAnimation(2 * progress, animationType) / 2
            else:
                delta = (2 - self.deltaAnimation(2 * (1 - progress), animationType)) / 2

        return int(toValue * delta)

    def deltaAnimation(self, progress, animationType):
        delta = 1

        if animationType == self.LINEAR:
            delta = self.deltaLinearAnimation(progress)

        elif animationType == self.CIRCLE:
            delta = self.deltaCircleAnimation(progress)

        elif animationType == self.ELASTIC:
            delta = self.deltaElasticAnimation(progress, 1.5)

        elif animationType == self.POWER_OF_TWO:
            delta = self.deltaPowerOfNAnimation(progress, 2)

        elif animationType == self.POWER_OF_FIVE:
            delta = self.deltaPowerOfNAnimation(progress, 5)

        elif animationType == self.SINE:
            delta = self.deltaSineAnimation(progress)

        elif animationType == self.BACK:
            delta = self.deltaBackAnimation(progress, 2.5)

        return delta

    def deltaLinearAnimation(self, progress):
        return progress

    def deltaCircleAnimation(self, progress):
        return 1 - Math.Sin(Math.ACos(progress))

    def deltaElasticAnimation(self, progress, x):
        return Math.Pow(2, 10 * (progress - 1)) * Math.Cos(20 * Math.PI * x / 3 * progress)

    def deltaPowerOfNAnimation(self, progress, power):
        return  Math.Pow(progress, power)

    def deltaSineAnimation(self, progress):
        return 1 - Math.Sin((1 - progress) * Math.PI / 2)

    def deltaBackAnimation(self, progress, x):
        return Math.Pow(progress, 2) * ((x + 1) * progress - x)
