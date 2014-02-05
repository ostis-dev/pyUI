
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
Created on 11.12.2009

@author: Denis Koronchik
'''
from suit.cf import BaseViewMode
from suit.cf import BaseEditMode
from suit.cf import TextInput
import suit.cf.utils as comutils

import suit.core.render.engine as render_engine
import ogre.renderer.OGRE as ogre
import ogre.io.OIS as ois
import suit.core.objects as objects
import suit.core.kernel as core
import scg_alphabet
import scg_objects
import scg_controls
import suit.core.render.mygui as mygui

from suit.cf.VisualMenu import VisualMenu
from suit.cf.VisualMenu import VisualMenuItem
from suit.cf.ToolBar import ToolBar

import scg_environment as env
import scg_utils


# mode show widget
_show_mode_window = None
_show_mode_text = None

def initialize():
    """Initialize mode show widget
    """
    global _show_mode_window
    global _show_mode_text
    _show_mode_window = render_engine.Gui.createWidgetT("Window", "Panel", 
                                                 mygui.IntCoord(0, 0, 0, 0), mygui.Align(),
                                                 "Popup", "")
    _show_mode_text = _show_mode_window.createWidgetT("StaticText", "StaticText",
                                               mygui.IntCoord(7, 7, 0, 0), mygui.Align())

def shutdown():
    """Shutting down mode show widget
    """
    global _show_mode_window
    global _show_mode_text
    render_engine.Gui.destroyWidget(_show_mode_window)
    _show_mode_window = None
    _show_mode_text = None

def _switchMode(_mode):
    """Shows mode description and change environment depend on mode
    """
    global _show_mode_text
    _show_mode_text.setCaption("#FF6633" + unicode(_mode.name))
    size = _show_mode_text.getTextSize()
    _show_mode_window.setSize(size.width + 14, size.height + 14)
    _show_mode_window.setPosition(render_engine.Window.width - size.width - 19,
                                  render_engine.Window.height - size.height - 19)
    _show_mode_text.setSize(size.width, size.height)
    
def hideMode():
    """Makes mode shower invisible
    """
    _show_mode_window.setVisible(False)
    
def showMode():
    """Makes mode shower visible
    """
    _show_mode_window.setVisible(True)

class SCgViewMode(BaseViewMode):
    """Mode that allows user to view and navigate in scg window
    """
    def __init__(self, _logic):
        BaseViewMode.__init__(self, _logic, "View mode")
        
    def __del__(self):
        BaseViewMode.__del__(self)
        
    

# ****************
# * Editor modes *
# ****************
class SCgEditMode(BaseEditMode):
    """Mode that allows user to edit scg-constructions
    
    """
    # states
    ES_Move         = BaseEditMode.ES_Count     # object movement state
    ES_LineCreate   = ES_Move + 1               # line creation mode
    ES_TypeChange   = ES_LineCreate + 1         # type changing mode
    ES_ContType     = ES_TypeChange + 1         # content type changing
    ES_Translate    = ES_ContType + 1           # translate camera position
    ES_ContourCreate= ES_Translate + 1          # contour creation
    ES_Count        = ES_ContourCreate + 1      # count of all states
    
    EM_Select   =   0
    EM_Pair     =   1
    EM_Bus      =   2
    EM_Contour  =   3
    EM_Count    =   4
    
    def __init__(self, _logic):
        BaseEditMode.__init__(self, _logic, "Edit mode")
        
        # mouse objects for line creation mode
        self.line_mode_beg = None
        self.line_mode_obj = scg_alphabet.createSCgNode('mnode')
        self.line_mode_obj.setScale(ogre.Vector3(0.1, 0.1, 0.1))
        self.line_mode_obj.setPosition(ogre.Vector3(0, 0, 0))
        self.line_mode_line = scg_alphabet.createSCgPair('mpair')
        self.line_mode_line.setEnd(self.line_mode_obj)
        self.line_mode_line.setState(objects.Object.OS_Normal)
        # highlighted object
        self.highlighted_obj = None
        
        # widgets
        self.type_combo = None
        self.content_combo = None
        
        # object we worked on in current state
        self.object_active = None
        # current editor state
        self.state = SCgEditMode.ES_None
        # current mouse position
        self.mouse_pos = (0, 0)
        
        # visual menu
#        self.vis_menu = None
#        self._createVisualMenu()
        
        # 3d navigation mode
        self.rotX = 0.0 
        self.rotY = 0.0
        self.move = ogre.Vector3(0.0, 0.0, 0.0)
        self.moveSpeed = 5.0
        self.moveScale = 5.0
        
        self.animationState = None
        
        # tool bar
#        self.toolbar = ToolBar()
#        self.toolbar.setVisible(False)
#        self.toolbar.setEnabled(True)
#        for idx in xrange(self.EM_Count):
#            button = self.toolbar.appendButton("", "scg_toolbar_icons.png", idx, (32, 32), (0, 0, 256, 32))
#            button.setCheckable(True)
#            button.setUserData(idx)
#            button.eventPush = self._onToolBarButtonPush
#            
#        self.toolbar.setButtonSize(38)

        #contour points
        self.contour_points = []
        self.contour_lines = []
            
        
    def __del__(self):
        BaseEditMode.__del__(self)
        
        
    def delete(self):
        """Deletion message
        """
        BaseEditMode.delete(self)
        
#        self.vis_menu.delete()
        
        self.line_mode_beg = None
        
        self.line_mode_line.delete()
        self.line_mode_line = None
        self.line_mode_obj.delete()
        self.line_mode_obj = None
        
        self.object_active = None
        
        
    def activate(self):
        """Activation message
        """
        BaseEditMode.activate(self)
#        self._updateVisualMenu()
        
    def deactivate(self):
        """Deactivation message
        """
        BaseEditMode.deactivate(self)
#        self._updateVisualMenu()
        
    def _update(self, timeSinceLastFrame):
        """Updates mode
        """
#        if self.vis_menu.isShow():
        sel_objects = self._logic._getSheet().getSelected()
        n = len(sel_objects)
#        if n == 1:
#            obj = sel_objects[0]
#            self.vis_menu.move(render_engine.pos3dTo2dWindow(sel_objects[0].getPosition()))
#        self.vis_menu._update(timeSinceLastFrame)
        
        if not self._ctrl and self.state is SCgEditMode.ES_Translate:
            if self._logic._getSheet().isRoot and render_engine.viewMode is render_engine.Mode_Perspective:
                # processing keyboard input
                if  render_engine._oisKeyboard.isKeyDown(ois.KC_A):
                    self.move.x = -self.moveScale    # Move camera left
        
                if  render_engine._oisKeyboard.isKeyDown(ois.KC_D):
                    self.move.x = self.moveScale    # Move camera RIGHT
        
                if  render_engine._oisKeyboard.isKeyDown(ois.KC_W):
                    self.move.z = -self.moveScale  # Move camera forward
        
                if  render_engine._oisKeyboard.isKeyDown(ois.KC_S):
                    self.move.z = self.moveScale    # Move camera backward
                    
                if  render_engine._oisKeyboard.isKeyDown(ois.KC_Q):
                    self.move.y = self.moveScale  # Move camera up
        
                if  render_engine._oisKeyboard.isKeyDown(ois.KC_E):
                    self.move.y = -self.moveScale    # Move camera down
            
                # updating camera position
                camera = render_engine._ogreCamera
                cameraNode = render_engine._ogreCameraNode
                cameraNode.translate(camera.getOrientation() * self.move * timeSinceLastFrame)
                camera.yaw(self.rotX)
                camera.pitch(self.rotY)
                self.move = ogre.Vector3(0, 0, 0)
                self.rotX = 0
                self.rotY = 0
                
        needMove = False
        offset = ogre.Vector3(0, 0, 0)
        dv = 1 * timeSinceLastFrame
        
#        if render_engine._oisKeyboard.isKeyDown(ois.KC_LEFT):
#            offset.x = -dv 
#            needMove = True
#        if render_engine._oisKeyboard.isKeyDown(ois.KC_RIGHT):
#            offset.x = dv
#            needMove = True
#        if render_engine._oisKeyboard.isKeyDown(ois.KC_UP):
#            offset.y = dv
#            needMove = True
#        if render_engine._oisKeyboard.isKeyDown(ois.KC_DOWN):
#            offset.y = -dv
#            needMove = True
#        if render_engine._oisKeyboard.isKeyDown(ois.KC_Z):
#            offset.z = dv
#            needMove = True
#        if render_engine._oisKeyboard.isKeyDown(ois.KC_X):
#            offset.z = -dv
#            needMove = True
#            
#        if needMove:
#            for obj in self._logic._getSheet().getSelected():
#                obj.setPosition(obj.getPosition() + render_engine._ogreCamera.getOrientation() * offset)
        
        if self.animationState is not None:
            self.animationState.addTime(timeSinceLastFrame)
        
        
    def _highlight(self):
        """Highlighting object under mouse
        """
        mobjects = self._logic._getSheet()._getObjectsUnderMouse(self.mouse_pos)
        obj = None
        if len(mobjects) > 0:
            obj = mobjects[0][1]
        
        if (obj is None) and (self.highlighted_obj is None):    return 
        if (obj is self.highlighted_obj):   return
        
        # change highlight
        if self.highlighted_obj is not None:
            self.highlighted_obj.resetState()
#            if self.highlighted_obj._getSelected():
#                self.highlighted_obj.setState(objects.Object.OS_Selected)
#            else:
#                self.highlighted_obj.setState(objects.Object.OS_Normal)
        self.highlighted_obj = obj
        if self.highlighted_obj:    self.highlighted_obj.setState(objects.Object.OS_Highlighted)
        
    def _onMouseMoved(self, _evt):
        """Mouse moved event
        """
        mstate = _evt.get_state()
        prev_pos = self.mouse_pos
        self.mouse_pos = (mstate.X.abs, mstate.Y.abs)
        
        
        # move object
        if self.state is SCgEditMode.ES_Move:
            pos = self.move_obj.getPosition()
            #self.move_obj.setPosition((pos[0] + dpos[0], pos[1] + dpos[1]))
            if render_engine.viewMode is render_engine.Mode_Isometric:
                self.move_obj.setPosition(render_engine.pos2dTo3dIsoPos(self.mouse_pos))
            else:
                self.move_obj.setPosition(render_engine.pos2dToViewPortRay(self.mouse_pos).getPoint(25.0))
#            if self.vis_menu.isShow():  self.vis_menu.move(self.mouse_pos)
            return True
                
        elif self.state is SCgEditMode.ES_LineCreate:
            pos = render_engine.pos2dTo3dIsoPos(self.mouse_pos)
            self.line_mode_obj.setPosition(pos)
            self._updateLineCreationObjects()
            self._highlight()
            return True
        
        elif self.state is SCgEditMode.ES_Translate:
            if render_engine.viewMode is render_engine.Mode_Isometric:
                render_engine._ogreCameraNode.translate(-mstate.X.rel / float(render_engine.scale2d),
                                                         mstate.Y.rel / float(render_engine.scale2d),
                                                         0.0)
                self._logic._getSheet()._updateChildTexts()
            else:
                self.rotX = ogre.Degree(-mstate.X.rel * 0.13)
                self.rotY = ogre.Degree(-mstate.Y.rel * 0.13)
            #FIXME:    add perspective mode
        
        # scaling
        if self._ctrl and mstate.Z.rel != 0 and render_engine.viewMode == render_engine.Mode_Isometric:
            sc = 1.0 + mstate.Z.rel / 1200.0            
            sheet = self._logic._getSheet()
            sheet.setScale(sheet.getScale() * sc)
        
        self._highlight()
        
        return False
    
    def _onMousePressed(self, _evt, _id):
        """Mouse button pressed event
        """
        mstate = _evt.get_state()
#        self._createNode((mstate.X.abs, mstate.Y.abs))

        # getting objects under mouse
        mobjects = self._logic._getSheet()._getObjectsUnderMouse(True)
        
        
        # * if pressed left button and there is any object under mouse, then
        # start move it
        if _id == ois.MB_Left:
            # check objects under mouse
            if self.state is SCgEditMode.ES_None:
                
                if self._ctrl:
                    sheet = comutils._getFirstObjectTypeFromList(mobjects, [objects.ObjectSheet])
                    if sheet is not None:
                        addr = sheet._getScAddr()
                        kernel = core.Kernel.getSingleton()
                        if sheet is not None and addr is not None and not kernel.haveOutputWindow(addr):
                            kernel.addOutputWindow(sheet._getScAddr())
                else:
                    if len(mobjects) is not 0:
                        self.move_obj = comutils._getFirstObjectTypeFromList(mobjects, [scg_objects.SCgNode, 
                                                                                        objects.ObjectSheet, 
                                                                                        scg_objects.SCgContour])
                        if self.move_obj is not None:
                            self.state = SCgEditMode.ES_Move
                            render_engine._gui_ignore_input_proc_result = True
                            # selecting movable object                       
                            self._selectObject(self.move_obj)
                            return True
                    
                        # selecting first object under mouse
                        self._selectObject(mobjects[0][1])
                        
                        return True
                   
        
        # * if pressed left button and there are no objects under mouse, then
        # creating new scg-node            
        elif _id == ois.MB_Right:
            #check if modifire key pressed
            is_modifire_down = render_engine._oisKeyboard.isModifierDown(render_engine._oisKeyboard.Modifier.Shift)
            # check objects under mouse
            if self.state is SCgEditMode.ES_None:
                if len(mobjects) is 0:
                    #check if contour draw mode
                    if is_modifire_down:
                        self.contour_points.append(render_engine.pos2dTo3dIsoPos([mstate.X.abs, mstate.Y.abs]))
                        self.state = SCgEditMode.ES_ContourCreate

                    else:
                        self._logic._createNode((mstate.X.abs, mstate.Y.abs))
                        self.state = SCgEditMode.ES_None
                        return True
                else:
                    if self.line_mode_beg is None:
                        self.state = SCgEditMode.ES_LineCreate
                        # setting begin object
                        self.line_mode_beg = mobjects[0][1]
                        self.line_mode_line.setBegin(self.line_mode_beg)
                        self.line_mode_obj.setPosition(render_engine.pos2dTo3dIsoPos((mstate.X.abs, mstate.Y.abs)))
                        # adding to scene
                        sheet = self._logic._getSheet() 
                        render_engine.SceneNode.addChild(sheet.sceneNodeChilds, self.line_mode_line.sceneNode)
                        
                        self._updateLineCreationObjects()
                        
                        return True
            # contour creation state
            elif self.state is SCgEditMode.ES_ContourCreate:
                sheet=self._logic._getSheet()
                self.contour_points.append(render_engine.pos2dTo3dIsoPos(((mstate.X.abs, mstate.Y.abs))))
                self.contour_lines.append(self._logic._createLine(self.contour_points[-1],self.contour_points[-2]))
                if  is_modifire_down and len(self.contour_points)>2:
                    contour = self._logic._createContour(self.contour_points)
                    for line in self.contour_lines:
                        render_engine._ogreSceneManager.getRootSceneNode().removeChild(line)
                    self.contour_lines = []
                    sheet.removeChild(contour)
                    childs = sheet.getChilds()
                    for i in range(len(childs)):
                        current = childs[0]
                        if scg_utils.checkOnPointInContour(current.position,self.contour_points):
                            sheet.removeChild(current)
                            render_engine.SceneNode.addChild(contour.sceneNode, current.sceneNode)
                    self._logic._getSheet().addChild(contour)
                    self.contour_points = []
                    self.state = SCgEditMode.ES_None
            # line creation state
            elif (self.state is SCgEditMode.ES_LineCreate) and (self.line_mode_beg is not None):
                # check if is there 
                if len(mobjects) is not 0:
                    self._logic._createPair(self.line_mode_beg, mobjects[0][1])
                    
                sheet = self._logic._getSheet()
                render_engine.SceneNode.removeChild(sheet.sceneNodeChilds, self.line_mode_line.sceneNode)
                self.line_mode_line.setBegin(None)
                self.line_mode_beg = None
                self.state = SCgEditMode.ES_None
                    
                return True
        elif _id == ois.MB_Middle:
            if self.state == SCgEditMode.ES_None:
                self.state = SCgEditMode.ES_Translate
                render_engine.Gui.setPointer("hand")
                return True
        
        if self._logic._getSheet().haveSelected() and self.state is SCgEditMode.ES_None:
            # removing selection from all nodes
            self._logic._getSheet().unselectAll()
            return True
        
            
        return False
    
    def _onMouseReleased(self, _evt, _id):
        """Mouse button released event
        """
        # getting objects under mouse
        mobjects = self._logic._getSheet()._getObjectsUnderMouse(True)
        
        # * if released left button and node moving, then
        # stopping movement 
        if _id == ois.MB_Left:
            
            # check state
            if self.state is SCgEditMode.ES_Move:
                self.state = SCgEditMode.ES_None
                render_engine._gui_ignore_input_proc_result = False
                del self.move_obj
                return True
            
                
        elif _id == ois.MB_Right:
            pass
        
        elif _id == ois.MB_Middle:
            # translation
            if self.state is SCgEditMode.ES_Translate:
                self.state = SCgEditMode.ES_None
                render_engine.Gui.setPointer("arrow")
                return True
        
        return False
    
    def _onKeyPressed(self, _evt):
        """Key pressed event
        """
        BaseEditMode._onKeyPressed(self, _evt)
        
        key = _evt.key
        
        if key == ois.KC_LSHIFT:
            self._shift = True
                    
        elif key == ois.KC_T:
            self._handlerChangeType()
            
        elif key == ois.KC_C:
            self._handlerChangeContent()
            
        elif key == ois.KC_H:
            self._handlerContentToogle()
           
        elif key == ois.KC_SPACE:
            layout_group = self._logic._getSheet().getLayoutGroup()
            if layout_group is not None:
                if layout_group.isPlaying():
                    layout_group.stop()
                else:
                    layout_group.play()
                    
        elif _evt.key == ois.KC_F9:
            if render_engine.viewMode is render_engine.Mode_Isometric:
                self._logic._getSheet().changeMode(render_engine.Mode_Perspective)
            else:
                self._logic._getSheet().changeMode(render_engine.Mode_Isometric)
            self.line_mode_line._needModeUpdate()
            
        # test code
        elif _evt.key == ois.KC_F3:# and 0:
            
            self._logic._getSheet().setLayoutGroup(None)
            
            elements = []
            node_center = scg_alphabet.createSCgNode("node/const/binary")
            node_center.setText(u"центр*")
            elements.append(node_center)
            
            node_tchk_O = scg_alphabet.createSCgNode("node/const/real")
            node_tchk_O.setText(u"Тчк О")
            elements.append(node_tchk_O)
            
            node_tchk_A = scg_alphabet.createSCgNode("node/const/real")
            node_tchk_A.setText(u"Тчк А")
            elements.append(node_tchk_A)
            
            node_tchk_B = scg_alphabet.createSCgNode("node/const/real")
            node_tchk_B.setText(u"Тчк B")
            elements.append(node_tchk_B)
            
            node_tchk_C = scg_alphabet.createSCgNode("node/const/real")
            node_tchk_C.setText(u"Тчк C")
            elements.append(node_tchk_C)
            
            node_tchk_A1 = scg_alphabet.createSCgNode("node/const/real")
            node_tchk_A1.setText(u"Тчк А1")
            elements.append(node_tchk_A1)
            
            node_tchk_B1 = scg_alphabet.createSCgNode("node/const/real")
            node_tchk_B1.setText(u"Тчк B1")
            elements.append(node_tchk_B1)
            
            node_tchk_C1 = scg_alphabet.createSCgNode("node/const/real")
            node_tchk_C1.setText(u"Тчк C1")
            elements.append(node_tchk_C1)
            
            node_tchk_A2 = scg_alphabet.createSCgNode("node/const/real")
            node_tchk_A2.setText(u"Тчк А2")
            elements.append(node_tchk_A2)
            
            node_tchk_B2 = scg_alphabet.createSCgNode("node/const/real")
            node_tchk_B2.setText(u"Тчк B2")
            elements.append(node_tchk_B2)
            
            node_tchk_C2 = scg_alphabet.createSCgNode("node/const/real")
            node_tchk_C2.setText(u"Тчк C2")
            elements.append(node_tchk_C2)
            
            node_okr_OA2 = scg_alphabet.createSCgNode("node/const/struct")
            node_okr_OA2.setText(u"Окр(ТчкO;ТчкA2)")
            elements.append(node_okr_OA2)
            
            node_okr = scg_alphabet.createSCgNode("node/const/term")
            node_okr.setText(u"окружность")
            elements.append(node_okr)
            
            node_otr = scg_alphabet.createSCgNode("node/const/term")
            node_otr.setText(u"отрезок")
            elements.append(node_otr)
            
            node_otr_AA1 = scg_alphabet.createSCgNode("node/const/struct")
            node_otr_AA1.setText(u"Отр(ТчкА;ТчкА1)")
            elements.append(node_otr_AA1)
            
            node_otr_BB1 = scg_alphabet.createSCgNode("node/const/struct")
            node_otr_BB1.setText(u"Отр(ТчкB;ТчкB1)")
            elements.append(node_otr_BB1)
            
            node_otr_CC1 = scg_alphabet.createSCgNode("node/const/struct")
            node_otr_CC1.setText(u"Отр(ТчкC;ТчкC1)")
            elements.append(node_otr_CC1)
            
            node_biss = scg_alphabet.createSCgNode("node/const/binary")
            node_biss.setText(u"биссектриса*")
            elements.append(node_biss)
            
            node_trian = scg_alphabet.createSCgNode("node/const/term")
            node_trian.setText(u"треугольник")
            elements.append(node_trian) 
            
            node_trian_ABC = scg_alphabet.createSCgNode("node/const/struct")
            node_trian_ABC.setText(u"Треугк(ТчкА;ТчкB;ТчкC)")
            elements.append(node_trian_ABC)
            
            node_vpis = scg_alphabet.createSCgNode("node/const/binary")
            node_vpis.setText(u"быть вписанным*")
            elements.append(node_vpis)
            
            node_versh_ = scg_alphabet.createSCgNode("node/const/role")
            node_versh_.setText(u"вершина_")
            elements.append(node_versh_)
            
            node_point = scg_alphabet.createSCgNode("node/const/term")
            node_point.setText(u"точка")
            elements.append(node_point)
            
            # link nodes
            points = [node_tchk_O, node_tchk_A, node_tchk_B, node_tchk_C, 
                      node_tchk_A1, node_tchk_B1, node_tchk_C1,
                      node_tchk_A2, node_tchk_B2, node_tchk_C2]
            for pt in points:
                arc = scg_alphabet.createSCgPair("pair/pos/-/orient/const")
                arc.setBegin(node_point)
                arc.setEnd(pt)
                elements.append(arc)
                
            otrs = [node_otr_AA1, node_otr_BB1, node_otr_CC1]
            for otr in otrs:
                arc = scg_alphabet.createSCgPair("pair/pos/-/orient/const")
                arc.setBegin(node_otr)
                arc.setEnd(otr)
                
                arc2 = scg_alphabet.createSCgPair("pair/pos/-/orient/const")
                arc2.setBegin(otr)
                arc2.setEnd(node_tchk_O)
                
                arc3 = scg_alphabet.createSCgPair("pair/-/-/orient/const")
                arc3.setBegin(node_trian_ABC)
                arc3.setEnd(otr)
                
                arc4 = scg_alphabet.createSCgPair("pair/pos/-/orient/const")
                arc4.setBegin(node_biss)
                arc4.setEnd(arc3)
                
                elements.append(arc)
                elements.append(arc2)
                elements.append(arc3)
                elements.append(arc4)
                
            vershs = [node_tchk_A, node_tchk_B, node_tchk_C]
            for ver in vershs:
                arc = scg_alphabet.createSCgPair("pair/pos/-/orient/const")
                arc.setBegin(node_trian_ABC)
                arc.setEnd(ver)
                
                arc2 = scg_alphabet.createSCgPair("pair/pos/-/orient/const")
                arc2.setBegin(node_versh_)
                arc2.setEnd(arc)
                
                elements.append(arc)
                elements.append(arc2)
                
            points = [node_tchk_A2, node_tchk_B2, node_tchk_C2]
            for pt in points:
                arc = scg_alphabet.createSCgPair("pair/pos/-/orient/const")
                arc.setBegin(node_okr_OA2)
                arc.setEnd(pt)
                
                elements.append(arc)
                
            arc = scg_alphabet.createSCgPair("pair/pos/-/orient/const")
            arc.setBegin(node_trian)
            arc.setEnd(node_trian_ABC)
            elements.append(arc)
            
            arc = scg_alphabet.createSCgPair("pair/pos/-/orient/const")
            arc.setBegin(node_okr)
            arc.setEnd(node_okr_OA2)
            elements.append(arc)
            
            arc = scg_alphabet.createSCgPair("pair/-/-/orient/const")
            arc.setBegin(node_trian_ABC)
            arc.setEnd(node_okr_OA2)
            elements.append(arc)
            
            arc2 = scg_alphabet.createSCgPair("pair/pos/-/orient/const")
            arc2.setBegin(node_vpis)
            arc2.setEnd(arc)
            elements.append(arc2)
            
            arc = scg_alphabet.createSCgPair("pair/-/-/orient/const")
            arc.setBegin(node_okr_OA2)
            arc.setEnd(node_tchk_O)
            elements.append(arc)
            
            arc2 = scg_alphabet.createSCgPair("pair/pos/-/orient/const")
            arc2.setBegin(node_center)
            arc2.setEnd(arc)
            elements.append(arc2)
            
            
            self._logic._getSheet().addChildList(elements)
            
            # go to 3d mode
            if render_engine.viewMode is render_engine.Mode_Isometric:
                self._logic._getSheet().changeMode(render_engine.Mode_Perspective)
            
            # disable layout
#            layout_group = self._logic._getSheet().getLayoutGroup()
#            layout_group.stop()
            
            # setup node positions manualy
            node_trian.setPosition(ogre.Vector3(0.0, 0.0, 3.0))
            
            node_otr_AA1.setPosition(ogre.Vector3(-5.0, 0.0, 2.0))
            node_otr_BB1.setPosition(ogre.Vector3(-5.0, 0.0, 0.0))
            node_otr_CC1.setPosition(ogre.Vector3(-5.0, 0.0, -2.0))
            node_otr.setPosition(ogre.Vector3(-8.0, 0.0, -2.0))
            node_biss.setPosition(ogre.Vector3(-1.0, 0.0, -2.0))
            
            node_tchk_O.setPosition(ogre.Vector3(-10.0, 0.0, 0.0))
            
            node_okr_OA2.setPosition(ogre.Vector3(-5, 3.0, 0.0))
            node_okr.setPosition(ogre.Vector3(-5, 6.0, 0.0))
            node_center.setPosition(ogre.Vector3(-8.0, 3.0, 0.0))
            node_vpis.setPosition(ogre.Vector3(-2.0, 3.0, 0.0))
            
            node_point.setPosition(ogre.Vector3(3.0, 2.0, -7.0))
            
            node_tchk_A.setPosition(ogre.Vector3(5.0, 3.0, 0.0))
            node_tchk_B.setPosition(ogre.Vector3(5.0, 0.0, 0.0))
            node_tchk_C.setPosition(ogre.Vector3(5.0, -3.0, 0.0))
            
            node_versh_.setPosition(ogre.Vector3(5.0, 2.0, 3.0))
            
            node_tchk_A2.setPosition(ogre.Vector3(1.0, 3.0, -8.0))
            node_tchk_B2.setPosition(ogre.Vector3(1.0, 0.0, -8.0))
            node_tchk_C2.setPosition(ogre.Vector3(1.0, -3.0, -8.0))
            
            node_tchk_A1.setPosition(ogre.Vector3(5.0, 3.0, -4.0))
            node_tchk_B1.setPosition(ogre.Vector3(5.0, 0.0, -4.0))
            node_tchk_C1.setPosition(ogre.Vector3(5.0, -3.0, -4.0))
            
            # configure camera
            camera = render_engine._ogreCamera
            cameraNode = render_engine._ogreCameraNode
            sceneManager = render_engine._ogreSceneManager
            
             # set up spline animation of node
            animation = sceneManager.createAnimation('CameraTrack', 23)
            animation.interpolationMode = ogre.Animation.IM_SPLINE
            
            animationTrack = animation.createNodeTrack(0, cameraNode)
            
            key = animationTrack.createNodeKeyFrame(0)
            key.setTranslate((0.441312, -0.0484183, 15.4575))
            key.setRotation((0.999381, 1.45161e-009, 0.0351611, 0.0))
            
            key = animationTrack.createNodeKeyFrame(3)
            key.setTranslate((-3.84972, -9.9938, 1.59091))
            key.setRotation((0.731662, 0.669154, 0.0960006, -0.0877989))
            
            key = animationTrack.createNodeKeyFrame(7)
            key.setTranslate((-3.84972, -9.9938, 1.59091))
            key.setRotation((0.731662, 0.669154, 0.0960006, -0.0877989))
            
            key = animationTrack.createNodeKeyFrame(10)
            key.setTranslate((-4.48132, 4.00986, 9.80443))
            key.setRotation((0.997827, -0.0657508, -0.00452801, -0.00029836))
            
            key = animationTrack.createNodeKeyFrame(14)
            key.setTranslate((-4.48132, 4.00986, 9.80443))
            key.setRotation((0.997827, -0.0657508, -0.00452801, -0.00029836))
            
            key = animationTrack.createNodeKeyFrame(17)
            key.setTranslate((-0.88816, 1.8146, 6.93933))
            key.setRotation((0.929973, -0.102752, -0.350851, -0.0387652))
            
            key = animationTrack.createNodeKeyFrame(20)
            key.setTranslate((-0.88816, 1.8146, 6.93933))
            key.setRotation((0.929973, -0.102752, -0.350851, -0.0387652))
            
            self.animationState = sceneManager.createAnimationState('CameraTrack')
            self.animationState.setEnabled (True)
            
        #test           
         
        elif key == ois.KC_F:
            # make selected sheet as root
            if self.state == SCgEditMode.ES_None:
                sheet = self._logic._getSheet()
                objs = sheet.getSelected()
                # getting object for making root
                if len(objs) == 1:
                    obj = objs[0]
                    if type(obj) == objects.ObjectSheet:
                        render_engine._kernel.setRootSheet(obj)
        
        elif key == ois.KC_ESCAPE:
            # revert state to default
            self.revertState()
            
        elif key == ois.KC_1:
            import suit.core.layout.LayoutGroupForceDirected as layout
            self._logic._getSheet().setLayoutGroup(layout.LayoutGroupForceSimple())
        elif key == ois.KC_2:
            import suit.core.layout.LayoutGroupForceDirected2 as layout
            self._logic._getSheet().setLayoutGroup(layout.LayoutGroupForceSimple())
        elif key == ois.KC_3:
            import suit.core.layout.LayoutGroupiGraph as layout
            self._logic._getSheet().setLayoutGroup(layout.LayoutGroupIGraph(layout.LayoutGroupIGraph.LT_GFR))
        elif key == ois.KC_4:
            import suit.core.layout.LayoutGroupRadial as layout
            self._logic._getSheet().setLayoutGroup(layout.LayoutGroupRadialSimple())
            
#        elif key == ois.KC_K:
#            self._logic._createContour([ogre.Vector3(-3, -2, 0),
#                                        ogre.Vector3(0, -3, 0),
#                                        ogre.Vector3(3, -1, 0),
#                                        ogre.Vector3(-3, 2, 0)
#                                        ])
        return False
    
    def _onKeyReleased(self, _evt):
        """Key released event
        """
        BaseEditMode._onKeyReleased(self, _evt)
        
        key = _evt.key
        
        if key == ois.KC_LSHIFT:
            self._shift = False
               
        return False
    
    def _updateLineCreationObjects(self):
        """Call updates for objects that draws in line creation mode
        """
        self.line_mode_obj.needUpdate = True
        self.line_mode_obj._update(0)
        self.line_mode_line.needUpdate = True
        self.line_mode_line._update(0)
        
    def revertState(self):
        
        if self.state == SCgEditMode.ES_LineCreate:
            sheet = self._logic._getSheet()
            render_engine.SceneNode.removeChild(sheet.sceneNodeChilds, self.line_mode_line.sceneNode)
            self.line_mode_line.setBegin(None)
            self.line_mode_beg = None
        
        
        self.state = SCgEditMode.ES_None
            
    def _onToolBarButtonPush(self, button):
        
        data = button.getUserData()
        for idx in xrange(self.EM_Count):
            if idx == data:
                self.toolbar[idx].setChecked(True)
            else:
                self.toolbar[idx].setChecked(False)
        
    ################
    ### handlers ###
    ################
    def _handlerChangeType(self):
        """Handler for change type event
        """
        # change type of selected element
        if self.state == SCgEditMode.ES_None:
            sheet = self._logic._getSheet()
            objs = sheet.getSelected()
            # get object for type changing 
            if len(objs) == 1:
                self._changeType(objs[0])
                
    def _handlerChangeIdtf(self):
        """Handler for change idtf event
        """
        self._setIdtf()
      
    def _handlerSelChanged(self):
        """Handler for selection changed event
        """
#        self._updateVisualMenu()
        pass
        
    def _handlerChangeContent(self):
        """Handler for changing content
        """
        if self.state == SCgEditMode.ES_None:
            sheet = self._logic._getSheet()
            objs = sheet.getSelected()
            if len(objs) == 1 and type(objs[0]) is scg_objects.SCgNode:
                self._changeContent(objs[0])
                
    def _handlerContentToogle(self):
        if self.state == SCgEditMode.ES_None:
            sheet = self._logic._getSheet()
            objs = sheet.getSelected()
            
            for obj in objs:
                if isinstance(obj, objects.ObjectSheet):
                    if obj.isContentShowing():
                        obj.hideContent()
                    else:
                        obj.showContent()
    
    def _dialog_del_callback(self):
        self.state = SCgEditMode.ES_None
        self.dialog = None
        
    #############
    ### Types ###
    #############
    def _changeType(self, _obj):
        """Creates control to change object type
        
        @param _obj: object to change type
        @type _obj: objects.ObjectDepth  
        """
        self.state = SCgEditMode.ES_TypeChange
        self.dialog = scg_controls.TypeChanger(_obj, self._dialog_del_callback)
        self.dialog.run()
           
        #self.state = SCgEditMode.ES_None
        
    ################
    ### Contents ###
    ################
    def _changeContent(self, _node):
        """Changes content type for a specified node
        @param _node:    node to change content type
        @type _node:    SCgNode
        """
        self.state = SCgEditMode.ES_ContType
        self.dialog = scg_controls.ContentChanger(_node, self._dialog_del_callback)
        self.dialog.run()
#        self._create_content_combo()
#        pos = render_engine.pos3dTo2dWindow(_node.getPosition() + _node.getScale() / 2)
#        
#        if pos is not None:
#            self.content_combo.setPosition(pos[0], pos[1])
#            self.object_active = _node
#            self.content_combo.subscribeEventAccept(self, "_contentAccept")
#            
#            # getting available for editing formats
#            session = render_engine._kernel.session()
#            self.fmts = render_engine._kernel.getRegisteredEditorFormats()
#            for fmt in self.fmts:
#                self.content_combo.addItem(unicode("#ffffff%s" % (session.get_idtf(fmt))))
#            
#        else:
#            self._destroy_content_combo()
        
    def _contentAccept(self, _widget, _v):
        """Handler for content combo accept
        """
        fmt = self.fmts[_v]
        
        assert type(self.object_active) is scg_objects.SCgNode
        window = scg_utils.createWindowFromNode(self.object_active, fmt)
        
        self._logic._getSheet().unselectAll()
        self._logic._getSheet().select(window)
    
        self._destroy_content_combo()
        self.state = SCgEditMode.ES_None
        self.object_active = None        
        del self.fmts
    
    
    ###################
    ### Visual menu ###
    ###################
    def _createVisualMenu(self):
        """Creates visual menu
        """
        self.vis_menu = VisualMenu()
        
        # identificator changing
        self.mi_idtf = VisualMenuItem()
        self.mi_idtf.callback = self._handlerChangeIdtf
        self.mi_idtf.setText("Change identifier")
        self.vis_menu.appendItem(self.mi_idtf)
        
        # type changing
        self.mi_type = VisualMenuItem()
        self.mi_type.callback = self._handlerChangeType
        self.mi_type.setText("Change type")
        self.vis_menu.appendItem(self.mi_type)
        
        # content changing
        self.mi_contentChange = VisualMenuItem()
        self.mi_contentChange.callback = self._handlerChangeContent
        self.mi_contentChange.setText("Change content")
        self.vis_menu.appendItem(self.mi_contentChange)
        
        # content showing
        self.mi_content_show = VisualMenuItem()
        self.mi_content_show.callback = self._handlerContentShow
        self.mi_content_show.setText("Show content")
        self.vis_menu.appendItem(self.mi_content_show)
        
        # content hiding
        self.mi_content_hide = VisualMenuItem()
        self.mi_content_hide.callback = self._handlerContentHide
        self.mi_content_hide.setText("Hide content")
        self.vis_menu.appendItem(self.mi_content_hide)
        
    def _updateVisualMenu(self):
        """Updates visual menu depending on selection
        """
        if self._logic is None or self._logic._getSheet() is None:
            return
        
        import types
        sel_objects = [] + self._logic._getSheet().getSelected()
        
        if self.vis_menu.isShow():
            self.vis_menu.hide()
        
        if not self.active: return
        
        n = len(sel_objects)
        if n == 1:
            obj = sel_objects[0]
            
            # check types
            isNode = isinstance(obj, scg_objects.SCgNode)
            isPair = isinstance(obj, scg_objects.SCgPair)
            isContent = isinstance(obj, objects.ObjectSheet) 
            
            # change type
            self.mi_type.setEnabled(isNode or isPair)
            # content
            self.mi_contentChange.setEnabled(isNode)
            # idtf
            self.mi_idtf.setEnabled(obj._getScAddr() is None)
            
            cs = ch = False
            if isContent:
                cs = not obj.isContentShow
                ch = obj.isContentShow
                
            self.mi_content_show.setEnabled(cs)
            self.mi_content_hide.setEnabled(ch)
        else:
            self.mi_type.setEnabled(False)
            self.mi_contentChange.setEnabled(False)
            self.mi_idtf.setEnabled(False)
            self.mi_content_show.setEnabled(False)
            self.mi_content_hide.setEnabled(False)
            
        if n > 0:   self.vis_menu.show(render_engine.pos3dTo2dWindow(sel_objects[0].getPosition()))
        
