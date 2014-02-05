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


from utils import *
import environment
import sys
#sys.path.append(environment.PATH_external)
import os.path
import ogre.renderer.OGRE as ogre
import render.engine as render_engine
import ogre.io.OIS as ois
import traceback, types
import processor, sc_core
import opers_sched, event_handler
import exceptions
from layout.LayoutManager import LayoutManager
import sc_core.pm
import thread

# window panel (used for storing module or object that provides buttons for windows selection and navigation)
windows_panel = None
# task panel (used for storing all tasks)
task_panel = None
        
# kernel class
class Kernel(Singleton):

    # component types
    CT_Viewer, CT_Editor, CT_Translator, CT_Count = range(4)
    
    # work segment
    __segment_core = None
    __segment_tmp = None
    __msession = None

    def __init__(self):
        """Constructor
        """
        Singleton.__init__(self)
        
        # operations
        #self.__operationFactories = {}
        
        # list of loaded modules
        self.__modules = {}
        # registered operations
        self.__operations = {}
        
        self.raySceneQuery = None 
        
        # operations scheduler
        self.__opers_sched = None
        
        # root sheet
        self.__rootSheet = None
        self.__prevRootSheet = None
        self.__processor = None
        
        # layout manager
        self.__layoutManager = None
        
        # overlay objects
        self.__addOverlayQueue = []
        self.__overlayObjects = []
        self.__removeOverlayQueue = []
        
        # lock objects
        self.__addOverlayQueueLock = thread.allocate_lock()
        
        # update listeners
        self.__updateListeners = []        
        
        # registered components
        self.__registeredComponents = {}
                
        self.__renderInitialized = False
        self.mainWindow = None
        
        self._user_addr =   None
        self.cache_path = None
        
        # list of arguments
        self._arguments =   []  # store list of tuples (argument, label)
        self._arg_mode  =   False
        
        # exit button widget
        self._exit_button = None
        
        # absolute path to executable directory
        self._exec_path = None
        
        
        """@todo: make scene manager protected, or make all attributes public""" 
        
    def __del__(self):    
        """Object deletion
        """
        pass
    
    @staticmethod
    def operations():
        return Kernel.__operationsDir
    
    @staticmethod
    def session():
        return Kernel.__msession
    
    @staticmethod
    def segment():
        return Kernel.__segment_core
    
    @staticmethod
    def segment_tmp():
        return Kernel.__segment_tmp
    
    def __getattr__(self, name):
        if name == 'logManager':
            return self.__logManager
        elif name == 'opers_sched':
            return self.__opers_sched
        elif name == 'rootSheet':
            return self.__rootSheet
        else:
            raise AttributeError("There are no attribute '%s'" % name)
        
    @staticmethod 
    def getResourceLocation():
        """Return resource location folder
        """
        return '../media/'
    
    def initialize(self, log_file = 'srs_engine.log', modules = [], repo_path = 'repo/fs_repo',
					resource_cfg = 'resources.cfg', exec_path = './', cache_path = "./chache",
                    segments = []):
        """Kernel initialization method
        
            @param log_file path to log file
            @param modules	list of modules to load
        """
        self.__logManager = LogManager()
        if (log_file != None):
            self.__logManager.start_file_logging(log_file)
        logManager = self.__logManager
        
        import version
        logManager.logInit('kernel version: ' + str(version.version))  
        
        # initialize chache directory
        self.cache_path = cache_path
        if os.path.isdir(self.cache_path):
            import shutil
            try:
                shutil.rmtree(self.cache_path)
                os.mkdir(self.cache_path)
            except:
                logManager.logWarning("Can't clear cache")
        else:
            os.mkdir(self.cache_path)        
        
        logManager.logInit('Operations scheduler')
        self.__opers_sched = opers_sched.OperationScheduler()
        self.__opers_sched.start()
        
        logManager.logInit('Processor module')
        self.__processor = processor.Processor({'repo_path': repo_path})
        import time
        while not self.__processor.started:
            time.sleep(0.05)
            
        logManager.logInit('Multithreaded session')
        import sc_core.msession
        Kernel.__msession = sc_core.msession.MThreadSession(sc_core.pm.get_session())
        
        # open segments
        for seg in segments:
            self.__msession.open_segment(seg)
        
        # initializing sc memory
        self.initSCMemory()
        
#        self.loadOperationModule('module_op')

        logManager.logInit("Layout manager")
        self.__layoutManager = LayoutManager()
        
        # initialize graphical subsystem
        self.__renderInitialized = render_engine.initialize(self, self.__logManager, Kernel.session(), Kernel.segment(), _resource_cfg = resource_cfg)
        if not self.__renderInitialized:
            return       
        
#        print "Operations tree:"
#        opers.operations._print(1)        
#        opers.operations.module.load("test_start")
#        self.loadModule("test_start")

        render_engine._coreUpdateFunc = self._update
        render_engine.addKeyboardListener(self)
        render_engine.addMouseListener(self)
        
        import loading_bar
        
        self.load_bar = loading_bar.LoadingBar()
        self.load_bar.start()
        
        # FIXME:    loading of modules
        self.initializeModules(modules) 
        self.load_bar.num_groups_init = len(ogre.ResourceGroupManager.getSingleton().getResourceGroups())
        
        render_engine.ResourceGroupManager.initialiseAllResourceGroups()
        self.load_bar.finish()
        del self.load_bar
        
        # initializing main window
        self.initMainWindow()
               
        #render_engine.ResourceGroupManager.initialiseAllResourceGroups()
                
        # creating exit button
        import render.mygui as mygui
        self._exit_button = render_engine.Gui.createWidgetT("Button",
                                                            "GlobalExitButton",
                                                            mygui.IntCoord(render_engine.Window.width - 33, -6, 39, 39),
                                                            mygui.Align(),
                                                            "Popup")
        self._exit_button.subscribeEventMouseButtonClick(self, "_onExitButton")
        
	# creates explain panel        
        explain = Explain()
        explainThread = threading.Thread(target=explain.slideExplains)
        explainThread.start()

        render_engine._start_rendering()        

    
    def initSCMemory(self):
        """Initialization of sc memory
        """   
        # creating directories for user interface
        self.__logManager.logInfo("Creating temporary directory for user interface '%s'" % self.getDirUITmpUri())
        if not Kernel.__msession.mkdir_full_uri('/tmp'):
            raise RuntimeError("Can't create temporary directory '/tmp'")
        if not Kernel.__msession.mkdir_full_uri(self.getDirUITmpUri()):
            raise RuntimeError("Can't create temporary directory for ui '%s'" % self.getDirUITmpUri())
        if not Kernel.__msession.create_segment_full_uri(Kernel.getDirUIUri() + '/core'):
            raise RuntimeError("Can't create temporary directory for ui '%s'" % (self.getDirUIUri() + '/core'))
        
        # store ui segment core
        Kernel.__segment_core = self.__msession.open_segment(environment.URI_ui_core)
        if Kernel.__segment_core is None:
            raise RuntimeError("Can't open ui core segment by uri '%s'" % environment.URI_ui_core)
        
        # find user node
        import sc_utils
        self._user_addr = sc_utils.getCurentUserNode(self.session())


    def initializeModules(self, _modules):
        """Loads and initialize extension modules
        """
        
        mods_count = len(_modules)
            
        self.__logManager.logInit("extension modules")
        for _mod in _modules:
            self.__logManager.logLoad("extension module '%s'" % (_mod), 1)
            self.load_bar.loadModuleStarted(_mod, mods_count)
            self.loadModule(_mod)
            self.load_bar.loadModuleFinished()
            
    def initMainWindow(self):
        """Initialize main window
        """
        import objects, keynodes
        self.mainWindow = objects.ObjectSheet("Main window")
        self.mainWindow._setScAddr(self.session().create_el(self.segment(), sc_core.pm.SC_N_CONST))
        
        # registering main window in main window set
        import sc_utils
        sc_utils.createPairPosPerm(self.session(), self.segment(), keynodes.ui.main_window, self.mainWindow._getScAddr(), sc_core.pm.SC_CONST)
                
        # creating scg-editor for main window
#        pth = os.path.join(environment.PATH_components, 'scg')
#        sys.path.append(pth)
#        import scg_editor
#        sys.path.remove(pth)
#        
        editor = self.createEditor(keynodes.ui.format_scgx)
        self.mainWindow.setLogic(editor)
       
        # including to SCg format set
        sc_utils.createPairPosPerm(self.session(), self.segment(), keynodes.ui.format_scgx, self.mainWindow._getScAddr(), sc_core.pm.SC_CONST)
        # including sc-windows set
        #sc_utils.createPairPosPerm(self.session(), self.segment(), keynodes.ui.sc_window, self.mainWindow._getScAddr(), sc_core.pm.SC_CONST)
         
        # temporary
        # FIXME:    remove that
        self.session().set_idtf(self.mainWindow._getScAddr(), u"Главное окно")
        # temporary 
         
        # test
        import layout.LayoutGroupForceDirected as layout
        self.mainWindow.setLayoutGroup(layout.LayoutGroupForceSimple())
        # test
        
        self.setRootSheet(self.mainWindow)
         
#        
#        # initializing scg-menu
#        import srs_engine.opers as opers
#        _kernel.loadModule('scg_menu', '../components/scg/')

        # initialing menu
        #self.loadModule("scg_menu", os.path.join(environment.PATH_components, "scg"))
        
    def shutdownMainWindow(self):
        """Destroys main window
        """
        session = self.session()
        self.mainWindow.delete()
        session.erase_el(self.mainWindow._getScAddr())
        
    def getMainWindow(self):
        return self.mainWindow
        
    @staticmethod
    def getDirUIOperUri():
        """Returns segment for user interface operations
        """
        return "/ui/operations"
    
    @staticmethod    
    def getDirUIUri():
        """Returns segment uri
        """
        return "/ui"
    
    @staticmethod
    def getDirUITmpUri():
        """Returns uri of user interface temporary segment 
        """
        return "/tmp/ui"
    
    def getUserAddr(self):
        """Return sc-element that designate user
        """
        return self._user_addr
        
    def shutdown(self):
        """Shutdown kernel
        """
        self.__logManager.logShutdown('kernel')
        self.__rootSheet = None
        
        # remove arguments
        self._clearArguments()
        
        # shutting down main window
        if self.mainWindow is not None:
            self.shutdownMainWindow()
            
        if self._exit_button:
            render_engine.Gui.destroyWidget(self._exit_button)
            self._exit_button = None
        
        import time
        # shutting down operations scheduler and wait all operations finished
        self.opers_sched.stop()
        while not self.__opers_sched.finished:
            time.sleep(0.5)
        
        # shutting down modules
        for module in self.__modules.iterkeys():
            self.__logManager.logShutdown("module '%s'" % (module), 1)
            self.__modules[module].shutdown()            
        
        # unregistering factories, that wasn't unregistered in modules shutdown
        # FIXME: make unregistering unified with lambda functions to minimize duplicate code
        if self.__registeredComponents.has_key(Kernel.CT_Editor):
            editors = []
            editors.extend(self.__registeredComponents[Kernel.CT_Editor].itervalues())

            for edit_f in editors:
                self.__logManager.logWarning("editor factory %s wasn't unregister in module shutdown" % str(edit_f))
                self.unregisterEditorFactory(edit_f)
        if self.__registeredComponents.has_key(Kernel.CT_Viewer):
            viewers = []
            viewers.extend(self.__registeredComponents[Kernel.CT_Viewer].itervalues())
            for view_f in viewers:
                self.__logManager.logWarning("viewer factory %s wasn't unregister in module shutdown" % str(view_f))
                self.unregisterViewerFactory(view_f)
        if self.__registeredComponents.has_key(Kernel.CT_Translator):
            translators = []
            translators.extend(self.__registeredComponents[Kernel.CT_Translator].itervalues())
            for trans_f in translators:
                self.__logManager.logWarning("translator factory %s wasn't unregister in module shutdown" % str(trans_f))
                self.unregisterTranslatorFactory(trans_f)
        
        # TODO:    user removing
        
        # shutting down layout manager
        if self.__layoutManager is not None:
            self.__logManager.logShutdown("Layout manager...")
            self.__layoutManager.stop()
            while not self.__layoutManager.finished:
                time.sleep(0.5)
                self.__logManager.message("Finished", 1)
        
        # shutting down graphical subsystem
        if self.__renderInitialized:
            render_engine.removeKeyboardListener(self)
            render_engine.removeMouseListener(self)
            render_engine.shutdown()        
             
        # destroying processor module
        self.__logManager.logShutdown("Processor module...")
        self.__processor.stop()
        while not self.__processor.finished:
            time.sleep(0.5)
        self.__logManager.message("Finished", 1)
        
    def addOverlayObject(self, _obj):
        """Adds overlay object to get updates
        @param _obj: overlay object to add
        @type _obj: objects.ObjectOverlay  
        """
        self.__addOverlayQueueLock.acquire()
        if _obj in self.__overlayObjects:
            self.__addOverlayQueueLock.release()   
            raise RuntimeError("Overlay object '%s' already exists" % str(_obj))
        self.__addOverlayQueue.append(_obj)
        self.__addOverlayQueueLock.release()
        
    def removeOverlayObject(self, _obj):
        """Removes overlay object
        @param _obj: overlay object
        @type _obj: objects.ObjectOverlay  
        """
        self.__addOverlayQueueLock.acquire()
        self.__removeOverlayQueue.append(_obj)
        self.__addOverlayQueueLock.release()
        
    def addUpdateListener(self, _listener):
        """Adds update listener
        @param _listener: listener object. (must have function _update(timeSinceLastFrame))
        @type _listener: object
        """
        if _listener in self.__updateListeners: raise RuntimeError("Update object '%s' already exists" % str(_listener))
        self.__updateListeners.append(_listener)
        
    def removeUpdateListener(self, _listener):
        """Removes update listener
        @param _listener: listener object
        @type _listener: object  
        """
        self.__updateListeners.remove(_listener)
        
    def _onExitButton(self, widget):
        """Subscriber to exit button click
        """
        render_engine._stop_rendering()
        
        
    def _notifyModeChanged(self, _newMode, _oldMode):
        """Notification about mode changed
        """
        if self.__rootSheet is not None:    
            self.__rootSheet._needModeUpdate = True
            self.__rootSheet._needViewUpdate = True
            
        self.__layoutManager.mode_changed()
    
    def _update(self, _dt):
        """Update function.
        Calls from rendering engine
        
        @param _dt: time since last frame in seconds
        @type _dt: float  
        """
        
        if self.__prevRootSheet is not None:
            self.__prevRootSheet._update(_dt)
            self.__prevRootSheet = None
        
        if (self.__rootSheet != None):
            self.__rootSheet._update(_dt)
        
        # update overlay objects
        self.__addOverlayQueueLock.acquire()
        self.__overlayObjects.extend(self.__addOverlayQueue)
        self.__addOverlayQueue = []
        self.__addOverlayQueueLock.release()
        
        for obj in self.__overlayObjects:
            if obj.isEnabled():# and obj.isVisible():
                obj._update(_dt)
            
        for obj in self.__removeOverlayQueue:
            self.__overlayObjects.remove(obj)
        self.__removeOverlayQueue = []
            
        for list in self.__updateListeners:
            list._update(_dt)
            
        # update argument labels
        if (len(self._arguments) > 0):
            import objects
            import render.mygui as mygui
            for arg, label in self._arguments:
                objs = objects.ScObject._scAddrThis2Objects(arg)
                n_objs = len(objs)
                if n_objs == 0:  # do nothing
                    label.setVisible(False)
                    continue
                
                updated = False
                
                objs.reverse()
                _object = None
                for _obj in objs:
                    if isinstance(_obj, objects.ObjectDepth):
                        if self.__rootSheet.haveChild(_obj):                           
                            pos = render_engine.pos3dTo2dWindow(_obj.getPosition())
                            if pos is not None:
                                x, y = pos 
                                label.setPosition(x, y)
                                
                            updated = True
                                                            
                            break
                    elif isinstance(_obj, objects.ObjectOverlay):
                        label.setVisible(_obj.isVisible())
                        if not _obj.isVisible(): # do not update hidden objects
                            continue

                        pos = _obj.getCenter()
                        label.setPosition(pos[0], pos[1])
                        
                        updated = True
                        
                        break
                
                if not updated:
                    label.setVisible(False)
        
    def prepareForScMachine(self):
        """Prepares user interface for sc-machine startup.
        This process contains next stages:
        - translate root sheet to SC-code
        """
        self.translateToSc(self.__rootSheet._getScAddr())
        
#    def registerComponentFactory(self, _factory, _data, _comType):
#        """Register new component type.
#        
#        @param _factory: factory object that will be create instances
#        @type _factory: objects.Factory
#        @param _data: specified data that need for component registration. Depends on component type
#        @type _data: list
#        @param _comType: component type. One of CT_Viewer, CT_Editor, CT_TransToSC, CT_TransFromSC types
#        """
#        if not self.__registeredComponents.has_key(_comType):
#            self.__registeredComponents[_comType] = {}
#        
#        if not self.__registeredComponents[_comType].has_key(_dataType):
#            self.__registeredComponents[_comType][_data] = []
#         
#         # FIXME:    fix when __eq__ operator for sc_addr will be added
##        if _factory in self.__registeredComponents[_comType][_data]:
##            raise RuntimeError("factory '%s' is already registered for data type '%s'" % (str(_viewerFactory), _dataType))

    def _generateViewEditSuppFormats(self, _session, _segment, _factory_el, _formats_list):
        """Generates set of supported formats for viewer/editor factory
        @param _session:    current session to work with sc-memory
        @type _session:    MThreadSession
        @param _segment:    segment to generate constructions
        @type _segment:    sc_segment
        @param _factory_el:    sc-element that designate factory
        @type _factory_el:    sc_global_addr
        @param _formats_list:    list of sc-element that designate formats
        @type _format_list:    list
        """
        import keynodes, sc_utils
        
        # creating set of supported formats
        fmt_sheaf = sc_utils.createNodeSheaf(_session, _segment, sc_core.pm.SC_CONST)
        pair_sheaf = sc_utils.createPairBinaryOrient(_session, _segment, _factory_el, fmt_sheaf, sc_core.pm.SC_CONST)
        sc_utils.createPairPosPerm(_session, _segment, keynodes.ui.nrel_set_of_supported_formats, pair_sheaf, sc_core.pm.SC_CONST)
        
        for fmt in _formats_list:
            # checking if format is correct
            if not sc_utils.checkIncToSets(_session, fmt, [keynodes.ui.format], sc_core.pm.SC_A_CONST | sc_core.pm.SC_POS):
                raise RuntimeError("sc-element %s is not in formats set" % str(fmt))
            # including format to set
            sc_utils.createPairPosPerm(_session, _segment, fmt_sheaf, fmt, sc_core.pm.SC_CONST)

    def registerViewerFactory(self, _factory, _formats_list):
        """Registers new viewer factory
        @param _factory:    factory that will be creates an instances of viewers
        @type _factory:    Objects.Factory
        @param _formats_list:    list of sc-elements that designates supported formats. 
        @type _formats_list:    list
        """
        if not self.__registeredComponents.has_key(self.CT_Viewer):
            self.__registeredComponents[self.CT_Viewer] = {}
        
        import keynodes
        import sc_utils
        
        # creating sc-structure to describe viewer
        session = self.session()
        segment = self.segment()
        # creating viewer class node 
        _view_addr = sc_utils.createNodeElement(session, segment, sc_core.pm.SC_CONST)

        self._generateViewEditSuppFormats(session, segment, _view_addr, _formats_list)           

        # register viewer in core
        self.__registeredComponents[self.CT_Viewer][str(_view_addr.this)] = _factory
        _factory._setScAddr(_view_addr)
           
        for _fmt in _formats_list:
            self.__logManager.logRegister("Viewer for format %s (factory: %s)" % (session.get_idtf(_fmt), str(_factory)))
        
        # append viewer into viewers set    
        sc_utils.createPairPosPerm(session, segment, keynodes.ui.viewer, _view_addr, sc_core.pm.SC_CONST)
            
    def unregisterViewerFactory(self, _factory):
        """Unregisters viewer factory
        @param _factory:    factory needed to be unregistered
        @type _factory:    objects.Factory
        """
        self._unregisterViewEditFactory(_factory)       
        
        
    def registerEditorFactory(self, _factory, _formats_list):
        """Registers new editor factory
        @param _factory:    factory that will be creates an instances of editor
        @type _factory:    Objects.Factory
        @param _formats_list:    list of sc-elements that designates supported formats. 
        @type _formats_list:    list
        """
        if not self.__registeredComponents.has_key(self.CT_Editor):
            self.__registeredComponents[self.CT_Editor] = {}
            
        import keynodes
        import sc_utils
        
        # creating sc-structure to describe editor
        session = self.session()
        segment = self.segment()
        
        # creating editor class node 
        _edit_addr = sc_utils.createNodeElement(session, segment, sc_core.pm.SC_CONST)
        
        self._generateViewEditSuppFormats(session, segment, _edit_addr, _formats_list)
        
        # register editor in core
        self.__registeredComponents[self.CT_Editor][str(_edit_addr.this)] = _factory
        _factory._setScAddr(_edit_addr)
            
        for _fmt in _formats_list:
            self.__logManager.logRegister("Editor for format %s" % (session.get_idtf(_fmt)))
            
        # append editor into editors set
        sc_utils.createPairPosPerm(session, segment, keynodes.ui.editor, _edit_addr, sc_core.pm.SC_CONST)
        
    def unregisterEditorFactory(self, _factory):
        """Unregisters editor factory
        @param _factory:    factory needed to be unregistered
        @type _factory:    objects.Factory
        """
        self._unregisterViewEditFactory(_factory)
        
        
    def _unregisterViewEditFactory(self, _factory):
        """Unregisters viewer or editor factory
        """
        import keynodes, sc_utils
        
        
        session = self.session()
        segment = self.segment()
        
        # getting sc_addr of viewers class
        f_addr = _factory._getScAddr()
        
        # check type
        isViewer = sc_utils.checkIncToSets(session, f_addr, [keynodes.ui.viewer], sc_core.pm.SC_A_CONST | sc_core.pm.SC_PERMANENT | sc_core.pm.SC_POS)
        isEditor = sc_utils.checkIncToSets(session, f_addr, [keynodes.ui.editor], sc_core.pm.SC_A_CONST | sc_core.pm.SC_PERMANENT | sc_core.pm.SC_POS)
        
        if isViewer == isEditor:    raise RuntimeError("Can't resolve factory type '%s'" % str(_factory))
        
        # removing factory from map
        tp = Kernel.CT_Viewer
        ts = "viewer"
        if isEditor:
            tp = Kernel.CT_Editor
            ts = "editor"
        # FIXME:    write formats to log
        self.__logManager.logUnregister("factory for %s '%s'" % (ts, str(_factory)))
        self.__registeredComponents[tp].pop(str(f_addr.this))
        
        # trying to get elements we need to remove
        pair = sc_utils.searchOneShotFullBinPairsAttrFromNode(session, f_addr, keynodes.ui.nrel_set_of_supported_formats, sc_core.pm.SC_CONST)
        if pair is None:    raise RuntimeError("Knowledge base is broken. Can't find set of supported formats for '%s'" % str(f_addr))
                
        
        # removing elements
        for idx in xrange(3):
            session.erase_el(pair[idx])
        
    
    def _checkViewEditFactorySuppFormat(self, _factory_node, _format_node):
        """Checks if editor/viewer factory supports specified format
        @param _factory_node:    sc-element that designate viewer/editor factory
        @type _factory_node:    sc_global_addr
        @param _format_node:    sc-element that designates specified format
        @type _format_node:    sc_global_addr
        
        @return: if viewer/editor supports specified format, then return True, else - False
        @rtype: bool
        """
        import keynodes, sc_utils
        
        # trying to find specified factory
        session = self.session()
        segment = self.segment()
        
        fmt_sheaf = sc_utils.searchOneShotBinPairAttrFromNode(session, _factory_node, keynodes.ui.nrel_set_of_supported_formats, sc_core.pm.SC_CONST)
        
        if fmt_sheaf is None:   return False
        
        return sc_utils.checkIncToSets(session, _format_node, [fmt_sheaf], sc_core.pm.SC_A_CONST | sc_core.pm.SC_POS | sc_core.pm.SC_PERMANENT)
        
       
        
    def createEditor(self, _format_node):
        """Creates editor logic for a specified format
        @param _format_node:    node that designate format
        @type _format_node:    sc_global_addr
       
        @return: editor logic instance for a specified format
        @rtype: objects.BaseLogic
        
        @raise RuntimeError:    raise error when can't find factory for a specified format
        """
        
        import keynodes, sc_utils
        import sc_core.constants
        # trying to find specified factory
        session = self.session()
        segment = self.segment()
        
        # finding all editor and getting with needed format
        it = session.create_iterator(session.sc_constraint_new(sc_core.constants.CONSTR_3_f_a_a,
                                                               keynodes.ui.editor,
                                                               sc_core.pm.SC_A_CONST | sc_core.pm.SC_POS | sc_core.pm.SC_PERMANENT,
                                                               sc_core.pm.SC_N_CONST), True)
        while not it.is_over():
            if self._checkViewEditFactorySuppFormat(it.value(2), _format_node):
                return self.__registeredComponents[self.CT_Editor][str(it.value(2).this)]._createInstance()
            it.next()
        
        raise exceptions.UnsupportedFormatError("There are no editors, that supports format %s" % session.get_idtf(_format_node))
        
    def createViewer(self, _format_node):
        """Creates viewer logic for a specified format
        @param _format_node:    node that designate format
        @type _format_node:    sc_global_addr
       
        @return: viewer logic instance for a specified format
        @rtype: objects.BaseLogic
        
        @raise RuntimeError:    raise error when can't find factory for a specified format
        """
        
        import keynodes, sc_utils
        import sc_core.constants
        # trying to find specified factory
        session = self.session()
        segment = self.segment()
        
        # finding all editor and getting with needed format
        it = session.create_iterator(session.sc_constraint_new(sc_core.constants.CONSTR_3_f_a_a,
                                                               keynodes.ui.viewer,
                                                               sc_core.pm.SC_A_CONST | sc_core.pm.SC_POS | sc_core.pm.SC_PERMANENT,
                                                               sc_core.pm.SC_N_CONST), True)
        while not it.is_over():
            if self._checkViewEditFactorySuppFormat(it.value(2), _format_node):
                return self.__registeredComponents[self.CT_Viewer][str(it.value(2).this)]._createInstance()
            it.next()
        
        raise exceptions.UnsupportedFormatError("There are no viewers, that supports format %s" % session.get_idtf(_format_node))
               
    def getRegisteredViewerFormats(self):
        """Returns list of nodes that designate available for viewing formats
        @return: list of tuples (format, code way)
        @rtype: list
        """
        res = []
        
        # getting all registered classes of viewers
        import keynodes
        import sc_core.constants
        
        session = self.session()
        
        it = session.create_iterator(session.sc_constraint_new(sc_core.constants.CONSTR_3_f_a_a,
                                                               keynodes.ui.viewer,
                                                               sc_core.pm.SC_A_CONST | sc_core.pm.SC_POS,
                                                               sc_core.pm.SC_N_CONST), True)
        while not it.is_over():
            
            # getting registered types for viewer class
            # FIXME:    remove duplicates
            res.extend(self._getScSuppFormats(it.value(2)))
            it.next()
        
        return res
    
    def getRegisteredEditorFormats(self):
        """Returns list of nodes that designate available for editing formats
        @return: list of sc-elements that designates formats
        @rtype: list
        """
        res = []
        
        # getting all registered classes of editors
        import keynodes
        import sc_core.constants
        
        session = self.session()
        
        it = session.create_iterator(session.sc_constraint_new(sc_core.constants.CONSTR_3_f_a_a,
                                                               keynodes.ui.editor,
                                                               sc_core.pm.SC_A_CONST | sc_core.pm.SC_POS,
                                                               sc_core.pm.SC_N_CONST), True)
        while not it.is_over():
            
            # getting registered types for editor class
            # FIXME:    remove duplicates
            res.extend(self._getScSuppFormats(it.value(2)))
            it.next()
        
        return res
        
    
    def _getScSuppFormats(self, _object_class):
        """Returns list of supported formats for a specified object
        @param _object_class:    node that designate one of available class
        of viewers or editors
        @type _object_class:    sc_global_addr
        
        @return: list of sc-elements that designates formats
        @rtype: list        
        """
        
        res = []
        
        import sc_utils, keynodes
        import sc_core.constants
        session = self.session()
        
        # getting set of supported formats
        fmt_sheaf = sc_utils.searchOneShotBinPairAttrFromNode(session, _object_class, keynodes.ui.nrel_set_of_supported_formats, sc_core.pm.SC_CONST)
        if fmt_sheaf is None:   raise RuntimeError("Can't get sheaf for supported formats")
        if not sc_utils.isNodeSheaf(session, fmt_sheaf):    raise RuntimeError("Sheaf of supported formats has wrong structure type")
        
        it = session.create_iterator(session.sc_constraint_new(sc_core.constants.CONSTR_3_f_a_a,
                                                               fmt_sheaf,
                                                               sc_core.pm.SC_A_CONST | sc_core.pm.SC_POS | sc_core.pm.SC_PERMANENT,
                                                               sc_core.pm.SC_N_CONST), True)
        while not it.is_over():
            res.append(it.value(2))
            it.next()
        
        
        return res
        
        
    ###################
    ### Translators ###
    ###################
    def registerTranslatorFactory(self, _factory, _in_formats, _out_formats):
        """Registers new translator
        @param _factory:    callable function, that will be create an instance of translator
        @type _factory:    objects.Factory
        @param _in_formats:    list of sc-elements that designates supported input formats
        @type _in_formats:    list
        @param _out_formats:    list of sc-elements that designates supported output formats
        @type _out_formats:    list
        """
        if not self.__registeredComponents.has_key(self.CT_Translator):
            self.__registeredComponents[self.CT_Translator] = {}
        
        import sc_utils, keynodes
        
        session = self.session()
        segment = self.segment()
        
        self.__logManager.logRegister("translator")
        # creating node that designate translator class
        trans_node = sc_utils.createNodeElement(session, segment, sc_core.pm.SC_CONST)
                
        # creating input formats description 
        in_fmt_sheaf = sc_utils.createNodeSheaf(session, segment, sc_core.pm.SC_CONST)
        in_rel_sheaf = sc_utils.createPairBinaryOrient(session, segment, trans_node, in_fmt_sheaf, sc_core.pm.SC_CONST)
        sc_utils.createPairPosPerm(session, segment, keynodes.ui.nrel_set_of_supported_input_formats, in_rel_sheaf, sc_core.pm.SC_CONST)
        # including input formats to set 
        s = ""
        self.__logManager.logInfo("input formats:", 1)
        for fmt in _in_formats:
            if not sc_utils.checkIncToSets(session, fmt, [keynodes.ui.format], sc_core.pm.SC_A_CONST | sc_core.pm.SC_POS):
                raise RuntimeError("sc-element %s doesn't designates format" % str(fmt))
            sc_utils.createPairPosPerm(session, segment, in_fmt_sheaf, fmt, sc_core.pm.SC_CONST)
            s += "%s " % str(session.get_idtf(fmt))
        self.__logManager.message(s, 2)
        
        # creating output formats description
        out_fmt_sheaf = sc_utils.createNodeSheaf(session, segment, sc_core.pm.SC_CONST)
        out_rel_sheaf = sc_utils.createPairBinaryOrient(session, segment, trans_node, out_fmt_sheaf, sc_core.pm.SC_CONST)
        sc_utils.createPairPosPerm(session, segment, keynodes.ui.nrel_set_of_supported_output_formats, out_rel_sheaf, sc_core.pm.SC_CONST)
        # including output formats to set
        self.__logManager.logInfo("output formats:", 1)
        s = ""
        for fmt in _out_formats:
            if not sc_utils.checkIncToSets(session, fmt, [keynodes.ui.format], sc_core.pm.SC_A_CONST | sc_core.pm.SC_POS):
                raise RuntimeError("sc-element %s doesn't designates format" % str(fmt))
            sc_utils.createPairPosPerm(session, segment, out_fmt_sheaf, fmt, sc_core.pm.SC_CONST)
            s += "%s " % str(session.get_idtf(fmt))
        self.__logManager.message(s, 2)
            
        # registering factory
        _factory._setScAddr(trans_node)
        self.__registeredComponents[Kernel.CT_Translator][str(trans_node.this)] = _factory
        
        # append translator into translators set
        sc_utils.createPairPosPerm(session, segment, keynodes.ui.translator, trans_node, sc_core.pm.SC_CONST)
        
    def unregisterTranslatorFactory(self, _factory):
        """Unregisters translator factory
        @param _factory:    factory needed to be unregistered
        @type _factory:    objects.Factory
        """
        import keynodes, sc_utils
        
        
        session = self.session()
        segment = self.segment()
        
        # getting translators class
        t_addr = _factory._getScAddr() 
        
        # trying to get sets of supported input/output formats
        set_of_supp_in_fmts = sc_utils.searchOneShotFullBinPairsAttrFromNode(session, t_addr, keynodes.ui.nrel_set_of_supported_input_formats, sc_core.pm.SC_CONST)
        if set_of_supp_in_fmts is None: raise RuntimeError("Can't get set of supported input formats for '%s'" % str(t_addr))
        set_of_supp_out_fmts = sc_utils.searchOneShotFullBinPairsAttrFromNode(session, t_addr, keynodes.ui.nrel_set_of_supported_output_formats, sc_core.pm.SC_CONST)
        if set_of_supp_out_fmts is None: raise RuntimeError("Can't get set of supported output formats for '%s'" % str(t_addr))
        
        # removing translator factory from map
        self.__logManager.logUnregister("factory for translator %s" % str(_factory))
        self.__registeredComponents[Kernel.CT_Translator].pop(str(t_addr.this))
        
        # removing element from sc-memory
        for idx in xrange(3):
            session.erase_el(set_of_supp_in_fmts[idx])
        for idx in xrange(1, 3):
            session.erase_el(set_of_supp_out_fmts[idx])
        
        
        
        
        
    def _getTranslators(self, _in_fmt, _out_fmt):
        """Returns list of available translators for specified input and output formats
        @param _in_fmt:    sc-element that designate input format
        @type _in_fmt:    sc_global_addr
        @param _out_fmt:    sc-element that designate output format
        @type _out_fmt:    sc_global_addr
        
        @return: list of sc-element that designates registered translator classes for specified
        input and output formats
        @rtype: list
        """
        res = []
        
        import keynodes
        import sc_core.constants
        session = self.session()
        segment = self.segment()
        
        # check all translators
        it = session.create_iterator(session.sc_constraint_new(sc_core.constants.CONSTR_3_f_a_a,
                                                               keynodes.ui.translator,
                                                               sc_core.pm.SC_A_CONST | sc_core.pm.SC_POS,
                                                               sc_core.pm.SC_N_CONST), True)
        while not it.is_over():
            in_fmts = self._getTranslatorFormats(it.value(2), True)
            out_fmts = self._getTranslatorFormats(it.value(2), False)
            
            # check if seeing translator have needed input and output formats
            if (_in_fmt in in_fmts) and (_out_fmt in out_fmts):
                res.append(it.value(2))
                        
            it.next()
        
        return res
        
    def _getTranslatorFormats(self, _trans, _isInput):
        """Returns list of translator supported formats
        @param _trans:    sc-element, that designate translator class
        @type _trans:    sc_global_addr
        @param _isInput:    flag to get input (True) or output (False) formats
        @type _isInput:    bool
        """
        res = []
        
        session = self.session()
        segment = self.segment()
        
        import sc_utils, keynodes
        import sc_core.constants
        
        attr = keynodes.ui.nrel_set_of_supported_output_formats
        if _isInput:  attr = keynodes.ui.nrel_set_of_supported_input_formats
        
        # getting formats set
        _set = sc_utils.searchOneShotBinPairAttrFromNode(session, _trans, attr, sc_core.pm.SC_CONST)
        
        if _set is None:
            return res    
        
        # check if set is a sheaf
        if not sc_utils.isNodeSheaf(session, _set): 
            raise RuntimeWarning("Node that designate set of supported formats for translator %s is not sheaf" % str(_trans))
        
        it = session.create_iterator(session.sc_constraint_new(sc_core.constants.CONSTR_3_f_a_a,
                                                               _set, 
                                                               sc_core.pm.SC_A_CONST | sc_core.pm.SC_POS,
                                                               sc_core.pm.SC_N_CONST), True)
        while not it.is_over():
            res.append(it.value(2))
            it.next()
        
        return res
        
    def _getAllTransSuppFormats(self, _isInput):
        """Returns list of supported input/output formats for all registered translators.
        
        @param _isInput:    flags that make choise between input or output formats
        @type _isInput:    bool
        
        @return: list of supported by translators output formats
        @rtype: list
        """
        mp = {}
        res = []
        
        import sc_core.constants
        session = self.session()
        
        # getting output formats for all translators
        it = session.create_iterator(session.sc_constraint_new(sc_core.constants.CONSTR_3_f_a_a,
                                                               keynodes.ui.translator,
                                                               sc_core.pm.SC_A_CONST | sc_core.pm.SC_POS,
                                                               sc_core.pm.SC_N_CONST), True)
        while not it.is_over():
            fmts = self._getTranslatorFormats(it.value(2), _isInput)
            
            for fmt in fmts:
                if not mp.has_key(str(fmt.this)):
                    res.append(fmt)
                    mp[str(fmt.this)] = fmt
             
            it.next()        
        
        return res 
        
        
    def translateToSc(self, _input):
        """Gets needed translator and translates input data to SC-code
        @param _input:    node with specified content that need to be translated
        @type _input:    sc_global_addr
        
        @return: if translation finished successfully, then return True, else - False
        @rtype: bool
        """        
        # getting input sheet
        import objects, sc_utils, keynodes
        import sc_core.constants
        session = self.session()
        segment = self.segment()
        
        # FIXME:    think about multiply windows for one sc-element
        objs = objects.ScObject._sc2Objects(_input)
        
        assert len(objs) > 0
        sheet = objs[0]
        assert type(sheet) is objects.ObjectSheet
        
        # getting temporary segment from sheet
        segment = sheet.getTmpSegment()

        # getting input format
        in_fmt = None
        it = session.create_iterator(session.sc_constraint_new(sc_core.constants.CONSTR_3_a_a_f,
                                                               sc_core.pm.SC_N_CONST,
                                                               sc_core.pm.SC_A_CONST | sc_core.pm.SC_POS,
                                                               _input), True)
        while not it.is_over():
            if sc_utils.checkIncToSets(session, it.value(0), [keynodes.ui.format], sc_core.pm.SC_A_CONST | sc_core.pm.SC_POS):
                if in_fmt is not None:  raise RuntimeError("There are to many formats for sheet %s" % _input)
                in_fmt = it.value(0)
                
            it.next()
            
        # getting available translators
        assert in_fmt is not None
        translators = self._getTranslators(in_fmt, keynodes.ui.format_sc)
        
        if len(translators) == 0:   raise RuntimeError("There are no translators from %s to SC-code" % session.get_idtf(in_fmt))
        
        # trying to translate data
        for tr_class in translators:
            trans_impl = self.__registeredComponents[Kernel.CT_Translator][str(tr_class.this)]._createInstance()
            if trans_impl.translate(_input, keynodes.ui.format_sc):   return True 
            
        return False
    
    def translateFromSc(self, _input, _output):
        """Gets needed translator and translates input SC-code to specified format
        @param _input:    set that contains sc-construction for translating
        @type _input:    sc_global_addr
        @param _output:    sc-node with content, that will be receive translated construction
        @type _output:    sc_global_addr
        """
        import sc_core.constants
        import sc_utils, keynodes
        session = self.session()
        segment = self.segment()
    
        # getting output format
        out_fmt = None
        it = session.create_iterator(session.sc_constraint_new(sc_core.constants.CONSTR_3_a_a_f,
                                                               sc_core.pm.SC_N_CONST,
                                                               sc_core.pm.SC_A_CONST | sc_core.pm.SC_POS,
                                                               _output), True)
        while not it.is_over():
            if sc_utils.checkIncToSets(session, it.value(0), [keynodes.ui.format], sc_core.pm.SC_A_CONST | sc_core.pm.SC_POS):
                if out_fmt is not None:  raise RuntimeError("There are to many formats for sc-node %s" % _output)
                out_fmt = it.value(0)
                
            it.next()
            
        # getting available translators
        assert out_fmt is not None
        translators = self._getTranslators(keynodes.ui.format_sc, out_fmt)
        
        if len(translators) == 0:   raise RuntimeError("There are no translators from SC-code to %s" % session.get_idtf(out_fmt))
        
        # trying to translate data
        for tr_class in translators:
            trans_impl = self.__registeredComponents[Kernel.CT_Translator][str(tr_class.this)]._createInstance()
            if trans_impl.translate(_input, _output):   return True
    
    ##################
    ### operations ###
    ##################
    def registerOperation(self, _event_handler):
        """Registers sc-operation
        @param _event_handler:    event handler of sc-operation
        @type _event_handler:    ScOperation
        """
        name = _event_handler.getName()
        
        if self.__operations.has_key(name):
            raise RuntimeError("operation with name '%s' already registered" % name)
        
        self.__logManager.logRegister("operation '%s' (handler %s)" % (name, str(_event_handler)), 1)
        _event_handler.registerOperation()
        self.__operations[name] = _event_handler
        
    def unregisterOperation(self, _event_handler):
        """Unregisters operation
        @param _event_handler:    event handler of sc-operation
        @type _event_handler:    ScOperation
        """
        name = _event_handler.getName()
        
        self.__logManager.logUnregister("operation '%s' (handler %s)" % (name, str(_event_handler)), 1)
        self.__operations.pop(name)
        
    def haveOperationByName(self, _name):
        """Check if operation with specified name is registered
        @param _name:    operation name
        @type _name:    str
        
        @return: True if operation with name exists, else - False
        @rtype: bool
        """
        return self.__operations.has_key(_name)        
        
    def getOperationByName(self, _name):
        """Returns operation by name
        @param _name:    operation name
        @type _name:    str
        
        @return: operation event handler
        @rtype: ScOperation
        """
        return self.__operations[_name]
        

#    def unregisterComponentFactory(self, _factory, _comType):
#        """Removes viewer registration
#        @param _factory: factory object for unregister
#        @type _factory: objects.Factory
#        @param _comType: component type. One of CT_Viewer, CT_Editor, CT_TransToSC, CT_TransFromSC types
#        """
#        if not self.__registeredComponents.has_key(_comType):
#            raise RuntimeError("There are no any factories registered for type '%s'" % str(_comType))
#        
#        for value in self.__registeredComponents[_comType].itervalues():
#            if _factory in value:
#                value.remove(_factory)
#                
#                # @todo: add code for removing registration in sc-memory
#                
#                return
#            
#        raise RuntimeError("Factory '%s' is not registered" % (str(_factory)))
        
    def haveAnimation(self, animation):
        """Check if animation exists in queue
        """
        return self.__animations.count(animation) > 0
    
    def setRootSheet(self, sheet):
        """Sets root window
        """
        assert sheet is not None
        
        if (self.__rootSheet is not None):
            self.__rootSheet._onRoot(False)
            self.__prevRootSheet = self.__rootSheet
            
        #self._clearArguments()
        
        self.__rootSheet = sheet
        sheet._onRoot(True)
        
    def getRootSheet(self):
        """Returns root sheet
        """
        return self.__rootSheet
    
    def loadModule(self, module_name, _dir = None):
        """Load module and initialize
        @param name: name of module for loading
        @type name: str 
        @param _dir: directory to find module
        @type _dir: str
        @return: loaded module object
        
        
        @todo: Synchronize module loading with render thread, because it use 
        ResourceGroupManager
        """
        # if module exists then raise exception
        if (self.__modules.has_key(module_name)):
            raise   NameError('Module \'' + module_name + '\' already loaded')
        
        # load module
        #self.__logManager.logLoad('module ' + name)
        try:
            if _dir is not None:
                sys.path.append(_dir)
            module = __import__(module_name)
            module = sys.modules[module_name]
            if _dir is not None:
                sys.path.remove(_dir)
            
            # getting version
            version = "Unknown"
            name = "Unknown"
            try:
                version = module._version_
            except:
                pass
            try:
                name = module._name_
            except:
                pass
            
            self.__logManager.logInfo("%s - %s" % (name, version), 1)
            
            # getting resource locations if they exists
            try:
                func = getattr(module, "_resourceLocations")
                if func is not None:
                    res_loc = func()
                    # appending resources
                    for _loc, _type, _group in res_loc:
                        render_engine.ResourceGroupManager.addResourceLocation(_loc, _type, _group)
            except:
                self.__logManager.logWarning("can't get resources declaration for module '%s'" % name, 1)
                
            # initialize module
            module.initialize()
            
        except:
            self.__logManager.logError('load \'' + module_name + '\' module', 1)
            print "Error:", sys.exc_info()[0]
            traceback.print_exc(file=sys.stdout)
            return None
            
        
        self.__logManager.logInfo('module \'' + name + '\' loaded', 1)
        # add loaded module to map
        self.__modules[module_name] = module      
        return module  
    
    def getModule(self, name):
        """Returns module by name
        @param name: module name 
        """
        if (not self.__modules.has_key(name)):
            raise NameError('Can\'t find module \'' + name + '\'')
        return self.__modules[name]
    
    def getModulesList(self):
        """Returns list of loaded module names
        """
        return self.__modules.keys()
        
    
    def mouseMoved(self, _evt):
        """Mouse moved notification
        """
        
        if self.__rootSheet:    return self.__rootSheet.mouseMoved(_evt)
        
        return False 
    
    def mousePressed(self, _evt, _id):
        """Mouse button pressed notification
        """
        
        if self._arg_mode and _id == ois.MB_Left:
            objs = self.__rootSheet._getObjectsUnderMouse()
            if len(objs) > 0:
                dist, _arg = objs[0]
                if _arg._getScAddr() is not None:
                    self._pushArgumentBack(_arg._getScAddr().this)
                return True
            
            # check overlay objects
            for obj in self.__overlayObjects:
                if not obj.isEnabled() or not obj.isVisible():
                    continue
                
                mstate = _evt.get_state()
 
                if obj._checkPoint((mstate.X.abs, mstate.Y.abs)):
                    if obj._getScAddr() is not None:
                        self._pushArgumentBack(obj._getScAddr().this)
                    return True
        
        if self.__rootSheet:    return self.__rootSheet.mousePressed(_evt, _id)
        
        return False
    
    def mouseReleased(self, _evt, _id):
        """Mouse button released notification
        """
           
        if self.__rootSheet:    return self.__rootSheet.mouseReleased(_evt, _id)
        
        return False
    
    def keyPressed(self, _evt):
        """Key pressed event
        """      
        
        if not self._arg_mode and _evt.key == ois.KC_LMENU:
            self._arg_mode = True
            #self._clearArguments()
            return True
        
        if self._arg_mode and _evt.key == ois.KC_C:
            self._clearArguments()
            return True
        
        if _evt.key == ois.KC_RETURN and (render_engine._oisKeyboard.isKeyDown(ois.KC_RCONTROL) or render_engine._oisKeyboard.isKeyDown(ois.KC_LCONTROL)):
            self.prepareForScMachine()
        
        if _evt.key == ois.KC_BACK:
            parent_sheet = self.__rootSheet.parent
            if parent_sheet is not None:
                self.setRootSheet(parent_sheet)
                    
        elif _evt.key == ois.KC_F12:
            import time
            ltime = time.localtime()
            render_engine._ogreRenderWindow.writeContentsToFile(os.path.join(environment.PATH_screens, "screen_%s%s%s.png" % (ltime[3],
                                                                                                                              ltime[4],
                                                                                                                              ltime[5])))
        elif _evt.key == ois.KC_F2:
            if render_engine._input_show is None:
                import input_show
                render_engine._input_show = input_show.InputShow()
                render_engine._input_show.enable()
            else:
                render_engine._input_show.toggle()
            
                
        if self.__rootSheet:    return self.__rootSheet.keyPressed(_evt)
        
        return False
    
    def keyReleased(self, _evt):
        """Key released event
        """
   
        if self._arg_mode and _evt.key == ois.KC_LMENU:
            self._arg_mode = False
#            self._arguments = []
#            return True
        
        if self.__rootSheet:    return self.__rootSheet.keyReleased(_evt)
        
        return False

    def _createArgumentLabel(self):
        """Creates label for command argument
        
        @return: argument label object
        @rtype: MyGUI::Widget
        """
        import render.mygui as mygui
        _arg_label = render_engine.Gui.createWidgetT("StaticText", "ArgumentsLabel", 
                                                     mygui.IntCoord(0, 0, 40, 30),
                                                     mygui.Align(),
                                                     "Info", "")
        _arg_label.setCaption(str(len(self._arguments) + 1))
#        _arg_label.setSize(_arg_label.getTextSize() + mygui.IntSize(5, 5))
#        _arg_label._setTextAlign(mygui.Align())
        _arg_label.setNeedMouseFocus(False)
        _arg_label.setNeedKeyFocus(False)
        return _arg_label

    def _pushArgumentBack(self, _arg):
        """Push object as command argument to the end of arguments list
        @param _arg:    object that adds to arguments
        @type _arg:    ScObject
        """
        assert _arg is not None
        self._arguments.append((_arg, self._createArgumentLabel()))
            
    def _clearArguments(self):
        """Clear arguments list
        """ 
        for arg, label in self._arguments:
            render_engine.Gui.destroyWidget(label)
        self._arguments = []
        
    def getArguments(self):
        """Return arguments list
        """
        res = []
        import objects
        for arg in self._arguments:
            objs = objects.ScObject._scAddrThis2Objects(arg[0])
            assert(len(objs) > 0)
            obj = objs[-1]
            res.append(obj)
        return res

    def onObjectDelete(self, _object):
        """Object delete notification. Calls from object.delete function
        @param _object: object that deleted
        @type _object: objects.Object
        """
        addr = _object._getScAddr()
        if addr is None: # do nothing
            return
        
        for arg in self._arguments:
            if addr.this == arg[0]:
                self._clearArguments()
                return

    def addOutputWindow(self, _addr):
        """Appends output window to map
        @param _addr:    sc_addr of existing sc-window, or format
        @type _addr:    sc_global_addr
        """
        if self.haveOutputWindow(_addr):
            raise exceptions.ItemAlreadyExistsError("Output window %s already exists" % (str(_addr)))

        import sc_utils, keynodes                                              
        sc_utils.createPairPosPerm(self.session(), self.segment(), keynodes.ui.set_output_windows, _addr, sc_core.pm.SC_CONST)
        
    
    def removeOutputWindow(self, _addr):
        """Removes output window from map
        @param _addr:    sc_addr of existing sc-window, or format
        @type _addr:    sc_global_addr
        """
        session = self.session()
        import sc_core.constants
        import sc_utils, keynodes
        it = session.create_iterator(session.sc_constraint_new(sc_core.constants.CONSTR_3_f_a_f, 
                                                               keynodes.ui.set_output_windows,
                                                               sc_core.pm.SC_A_CONST,
                                                               _addr), True)
        cnt = 0
        while not it.is_over():
            if cnt > 0:
                raise exceptions.ItemAlreadyExistsError("Duplicate arc in base")
            session.erase_el(it.value(1))
            cnt += 1
            it.next()
        
            
        
    def haveOutputWindow(self, _addr):
        """Check if output window is already in map
        @param _addr:    sc_addr of list or format
        @type _addr:    sc_global_addr
        
        @return: if window exists, then return True, else - False
        @rtype: bool
        """
        import sc_utils, keynodes
        return sc_utils.checkIncToSets(self.session(), _addr, [keynodes.ui.set_output_windows], sc_core.pm.SC_CONST)
    
    def getOutputWindows(self):
        """Returns information for output windows
        """
        res = []
        session = self.session()
        import sc_core.constants
        import sc_utils, keynodes
        it = session.create_iterator(session.sc_constraint_new(sc_core.constants.CONSTR_3_f_a_a, 
                                                               keynodes.ui.set_output_windows,
                                                               sc_core.pm.SC_A_CONST,
                                                               sc_core.pm.SC_N_CONST), True)
        while not it.is_over():
            res.append(it.value(1))
            it.next()
            
        return res
    
    def getCurrentTranslation(self):
        """Returns sc-addr of current translation language
        """ 
        import sc_utils, sc_core.constants, keynodes
        session = self.session()
        res = session.search_one_shot(session.sc_constraint_new(sc_core.constants.CONSTR_3_f_a_a,
                                                                keynodes.ui.translate_lang_current,
                                                                sc_core.pm.SC_A_CONST,
                                                                sc_core.pm.SC_N_CONST), True, 3)
        assert res is not None
        
        return res[2]
    
    def translationChanged(self):
        """Notify about translation changed. Called when current translation changed to another.
        It notify all object on screen about translation changing
        """
        self.mainWindow._needLocalizationUpdate()
        for obj in self.__overlayObjects:
            obj._needLocalizationUpdate()

class Explain():
    def __init__(self):
        import render.mygui as mygui
        self.explainPanel = render_engine.Gui.createWidgetT("Window", "Panel",
                                          mygui.IntCoord(0, 0, 200, 200), mygui.Align(),
                                          "Info", "")
        self.explains = self.getExplains()
        self.curExplain = 0;
        self.text = self.explainPanel.createWidgetT("StaticText",
                                       "ToolTipText",
                                       mygui.IntCoord(12, 12, 0, 0),
                                       mygui.Align())

        self.text.setCaption(self.explains[0])
        tsize = self.text.getTextSize()
        w = tsize.width + 24
        h = tsize.height + 24
        self.explainPanel.setSize(w + 24, h + 24)
        self.text.setSize(w, h)
        x = 20
        y = (render_engine.Window.height - 120)
        self.explainPanel.setPosition(x, y)
        self.explainPanel.setAlpha(1.0)
        exiteExplain = self.explainPanel.createWidgetT("Button",
                             "MainPanel_OutputWindowDelButton",
                             mygui.IntCoord(0, 5, 20, 20),
                             mygui.Align(),
                             "")
        exiteExplain.subscribeEventMouseButtonClick(self, "_onExitExplain")
        self.explainPanel.subscribeEventMouseDrag(self, "_eventMouseDragPanel")
        self.explainPanel.subscribeEventMouseButtonPressed(self, "_eventMouseButtonPressedPanel")

    def getExplains(self):
        import suit.core.sc_utils as sc_utils
        import sc_core.pm as sc
        session = Kernel.session()
        result = []
        attr = sc_utils.getElementByIdtf("next*", ["/seb/test"])
        el = sc_utils.getElementByIdtf("first", ["/seb/test"])
        result.append(sc_utils.cp1251ToUtf8(session.get_content_str(el)))
        cur = sc_utils.searchBinPairsAttrFromNode(session, el, attr, sc.SC_POS)
        while cur:
            el = cur[0]
            result.append(sc_utils.cp1251ToUtf8(session.get_content_str(el)))
            cur = sc_utils.searchBinPairsAttrFromNode(session, el, attr, sc.SC_POS)

        return result

    def slideExplains(self):
        time.sleep(5.0)
        self.explainPanel.setVisible(False)
        time.sleep(2.0)
        while self.curExplain < len(self.explains)-1 :
            self.explainPanel.setVisible(True)
            self.curExplain += 1
            self.text.setCaption(self.explains[self.curExplain])
            tsize = self.text.getTextSize()
            w = tsize.width + 24
            h = tsize.height + 24
            self.explainPanel.setSize(w + 24, h + 24)
            self.text.setSize(w, h)
            x = 20
            y = (render_engine.Window.height - 120)
            self.explainPanel.setPosition(x, y)
            self.explainPanel.setAlpha(1.0)
            self.slideExplains()


    def _eventMouseDragPanel(self, _sender, _left, _top):
        dx = _left - self.x
        dy = _top - self.y
        pos = self.explainPanel.getPosition()
        self.explainPanel.setPosition(pos.left + dx, pos.top + dy)

    def _eventMouseButtonPressedPanel(self, _sender, _left, _top, _id):
        """Event on identifier pressed
        """
        self.x = _left
        self.y = _top

    def _onExitExplain(self, widget):
        render_engine.Gui.destroyWidget(self.explainPanel)

