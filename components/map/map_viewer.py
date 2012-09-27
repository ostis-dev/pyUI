
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
Created on 11.02.2010

@author: Denis Koronchik
'''


from suit.cf import BaseModeLogic
import suit.core.exceptions as exceptions
import suit.core.kernel as core
import suit.core.objects as objects
import ogre.renderer.OGRE as ogre
import ogre.io.OIS as ois

import suit.core.render.engine as render_engine
import field.field as field
import field.fieldDrawer as fieldDrawer
import map_modes
import map_utils.map_parser
import map_utils.midmif_parser
import suit.core.render.mygui as mygui
import cairo
import wx._controls_
import map_environment as env
# FIXME:   add support for many layers

class MapViewer(BaseModeLogic):
    
    def __init__(self):
        BaseModeLogic.__init__(self)
        
        self.sceneNodeRect = render_engine.SceneManager.createSceneNode()
        self.rect = None
        self._createRect()
        
        self.material = None
        self.texture = None
        self.origin = [0.5, 0.5]
        
        self.field = None
        self.drawer = None
        
        self.mapSurface = None
        self.layerData = []
        
        self.zoomRectCorners = [[0, 0], [0, 0]] 
        
        self.tex_size = (1024, 1024)
        
        self.appendMode(ois.KC_V, map_modes.MapViewMode(self))
        self.switchMode(ois.KC_V)
    
    def __del__(self):
        BaseModeLogic.__del__(self)
    
    def delete(self):
        """Deletion message
        """
        BaseModeLogic.delete(self)
        
        
    def _setSheet(self, _sheet):
        BaseModeLogic._setSheet(self, _sheet)
        
        _sheet.eventRootChanged = self._onRoot
                
        self._createFieldFromContent()                
        self._createMaterial()
        self.rect.setMaterial(self.getMaterialName())
        self._redraw()
    
    def _onRoot(self, _isRoot):
        """Notification on sheet root state changing
        """
        if _isRoot:
            self.controlPanel()
            render_engine.SceneNode.addChild(self._getSheet().sceneNodeChilds, self.sceneNodeRect)
        else:
            render_engine.SceneNode.removeChild(self._getSheet().sceneNodeChilds, self.sceneNodeRect)
        
    def _createRect(self):
        """ Creates rectangle surface for root mode
        """
        # FIXME: make thread safe
        self.rect = ogre.Rectangle2D(True)
        self.rect.setCorners(-1.0, 1.0, 1.0, -1.0)
        self.rect.setRenderQueueGroup(ogre.RENDER_QUEUE_8)
        self.rect.setBoundingBox(ogre.AxisAlignedBox(ogre.Vector3(-100000.0, -100000.0, -100000.0), ogre.Vector3(100000.0, 100000.0, 100000.0)))
        self.sceneNodeRect.attachObject(self.rect)
    
    def _destroyRect(self):
        """ Destroys rectangle surface for root mode
        """
        self.rect = None
        # FIXME: scene node removing
        
    def getMaterialName(self):
        return str(self) + "material"
    
    def _createMaterial(self):
        self.material = ogre.MaterialManager.getSingleton().create(self.getMaterialName(), env.resource_group)
        mpass = self.material.getTechnique(0).getPass(0)
        mpass.setLightingEnabled(True) 
        mpass.setDiffuse(0.0, 1.0, 0.0, 1.0)
        
        tex_name = str(self) + "tex"
        self.texture = ogre.TextureManager.getSingleton().createManual(tex_name, env.resource_group,
                                                                       ogre.TEX_TYPE_2D, self.tex_size[0], self.tex_size[1], 32,
                                                                       5, ogre.PixelFormat.PF_A8R8G8B8,
                                                                       ogre.TU_DYNAMIC_WRITE_ONLY_DISCARDABLE)
        tus = mpass.createTextureUnitState(tex_name)
        
        
    def _layerClick(self, list, pvt):
        ind = list.getIndexSelected()
        dir(list)
        if ind >= 0 and ind < list.getItemCount():
            name = list.getItemNameAt(ind)
            for data in self.layerData:
                layer = data["layer"]
                itemName = unicode(name).split()[1]
                list.setItemNameAt(ind, itemName)
                if itemName == unicode(layer.name):
                    layer.visible = not layer.visible
                    itemName = {True:'O', False:'X'}[layer.visible] + "   " + itemName
                    list.setItemNameAt(ind, itemName)
                    pref = ""
                    if not layer.visible:
                        pref = "in"
                    if not data["drawn"]:
                        self.drawer.drawIt(self.scaleManager.scale, self.layerData)
                    buff = self.texture.getBuffer()
                    lock = buff.lock(0, buff.getSizeInBytes(), ogre.HardwareBuffer.HBL_NORMAL)
                    self.drawMap()
                    buff.unlock()
                    break
            
        
        
    def controlPanel(self):
        gui = render_engine._gui
        #self.x, self.y = render_engine._ogreRenderWindow.getWidth(), render_engine._ogreRenderWindow.getHeight()
        
        wid = 200
        hei = 400
        horOffset = 5
        window = gui.createWidgetT("Window", "Window", mygui.IntCoord(10, 10, wid + 10, hei + 10), mygui.Align(), "Overlapped", '')
        layerList = window.createWidgetT("List", "List", mygui.IntCoord(horOffset, 20, wid - 2 * horOffset, hei - 60), mygui.Align())
        layerList.subscribeEventMouseItemActivate(self,'_layerClick')
        
        for layer in self.field.layers:
            layerList.addItem("O   " + unicode(layer.name))
        
        return
        #list = self.gui.createWidgetT("List", "List", mygui.IntCoord(20, 270, 140, 100), mygui.Align())
        #list = self.gui.createWidgetT("List", "List", mygui.IntCoord(20, 270, 140, 100), mygui.Align())
        
        begin = (self.x - self.butWidth*self.butAmount) 
        begin = begin/2
        self.wpanel = self.gui.createWidgetT("Widget", "Panel", mygui.IntCoord(1, self.y - 40, self.x, 40), mygui.Align(), "Popup", '')
        self.wpanel.setAlpha(1)
        
        self.slider = self.wpanel.createWidgetT("HScroll", "HSlider", mygui.IntCoord(50, 5, 700, 5), mygui.Align())
        self.slider.setScrollRange(100)
        
        self.stopbut = self.wpanel.createWidgetT("Button", "Button", mygui.IntCoord(begin, 15, self.butWidth, self.butHeight), mygui.Align())
        self.stopbut.setCaption("Stop")
        self.stopbut.subscribeEventMouseButtonClick(self,'_stop')
        begin  = begin + self.butWidth
        
        self.backbut = self.wpanel.createWidgetT("Button", "Button", mygui.IntCoord(begin, 15, self.butWidth, self.butHeight), mygui.Align())
        self.backbut.setCaption("Back")        
        begin  = begin + self.butWidth
        
        self.plbut = self.wpanel.createWidgetT("Button", "Button", mygui.IntCoord(begin, 15, self.butWidth, self.butHeight), mygui.Align())
        if self.audioPlayer.isPlaying():
            self.plbut.setCaption("Pause")
        else:
            self.plbut.setCaption("Play")
        self.plbut.subscribeEventMouseButtonClick(self,'_play_pause')     
        begin  = begin + self.butWidth
                          
        self.forwbut = self.wpanel.createWidgetT("Button", "Button", mygui.IntCoord(begin, 15, self.butWidth, self.butHeight), mygui.Align())
        self.forwbut.setCaption("Forward")        
        begin  = begin + self.butWidth
        
        self.volslider = self.wpanel.createWidgetT("HScroll", "HSlider", mygui.IntCoord(begin, 23, self.butWidth, 5), mygui.Align())
        self.volslider.setScrollRange(100)        
#        print dir(self.slider)
#        print self.volslider.setState.__doc__        
        #self.controller = mygui.ControllerFadeAlpha(0, 1, True)        
        #mygui.ControllerManager.getInstance().addItem(self.wpanel, self.controller)        
        self.panel = True        
        
        
        
    def zoomToRect(self):
        newScale = oldScale = self.scaleManager.scale
        
        a = abs(self.zoomRectCorners[0][0] - self.zoomRectCorners[1][0])
        b = abs(self.zoomRectCorners[0][1] - self.zoomRectCorners[1][1])
        if a != 0 and b != 0: 
            factor = 1. / max(a, b)
            newScale = self.scaleManager.getAppropriateScale(factor)
            
            pt = [(self.zoomRectCorners[0][0] + self.zoomRectCorners[1][0]) / 2,
                  (self.zoomRectCorners[0][1] + self.zoomRectCorners[1][1]) / 2]
            self.setOrigin(pt)
        
        if (oldScale != newScale):
            self.scaleManager.scale = newScale
            self._redraw()
        else:
            buff = self.texture.getBuffer()
            lock = buff.lock(0, buff.getSizeInBytes(), ogre.HardwareBuffer.HBL_NORMAL)
            self.drawMap()
            buff.unlock()
            
    def drawMap(self):
        # setting variables SIZEX and SIZEY to the size of field in pixels
        factor = self.scaleManager.getFactor() 
        SIZEX = SIZEY = self.drawer.standardConstrainPx * factor
        
        self.ctx.set_source_rgba (1, 1, 1, 1)
        self.ctx.rectangle(0, 0, SIZEX, SIZEY)
        self.ctx.fill()
        
        for data in self.layerData:
            if data["layer"].visible: 
                self.ctx.set_source_surface(data["surface"])
                self.ctx.paint()
                
                self.ctx.set_source_surface(data["selected-surface"])
                self.ctx.paint()
                
        
    def zoomRect(self, fromPt, toPt): 
        buff = self.texture.getBuffer()
        lock = buff.lock(0, buff.getSizeInBytes(), ogre.HardwareBuffer.HBL_NORMAL)
        
        self.drawMap()
        
        
        factor = self.scaleManager.getFactor()
        SIZEX = SIZEY = self.drawer.standardConstrainPx * factor
        self.ctx.set_line_width(1)
        self.ctx.set_source_rgba(.2, .2, .9, .9)
        
        self.zoomRectCorners[0] = fromPt
        self.zoomRectCorners[1] = toPt
        
        tx, ty = self.getTranslation()
        
        
        self.ctx.rectangle(min(fromPt[0], toPt[0]) * SIZEX + tx, 
                           min(fromPt[1], toPt[1]) * SIZEY + ty,
                           abs(fromPt[0] - toPt[0]) * SIZEX, 
                           abs(fromPt[1] - toPt[1]) * SIZEY)
        self.ctx.stroke_preserve()
        
        self.ctx.set_source_rgba(.2, .2, .9, .1)
        self.ctx.fill()
        
        buff.unlock()
        
    def getTranslation(self):
        tx, ty = 0, 0
        factor = self.drawer.manager.getFactor()
        tx = (1 - factor) * self.origin[0] * self.drawer.standardConstrainPx;
        ty = (1 - factor) * self.origin[1] * self.drawer.standardConstrainPx;
        return tx, ty
    
    # not tested yet
    def mapToScreen(self, pt):        
        tx, ty = 0, 0
        factor = self.scaleManager.getFactor()
        tx = (factor - 1) * self.origin[0]
        ty = (factor - 1) * self.origin[1]
        
        mx = pt[0] * factor - tx, 
        my = pt[1] * factor - ty
        
        res = [mx * render_engine.Window.width,
               my * pt[1] / render_engine.Window.height]
        
        return res
    
    
    def screenToMap(self, pt):
        tx, ty = 0, 0
        factor = self.scaleManager.getFactor()
        tx = (factor - 1) * self.origin[0]
        ty = (factor - 1) * self.origin[1]
        mx = pt[0] / render_engine.Window.width
        my = pt[1] / render_engine.Window.height
         
        res = [(tx + mx) / factor,
               (ty + my) / factor]
        
        return res
         
    
    def zoomIn(self):
        return self.scaleManager.increaseScale()
        
    def zoomOut(self):
        return self.scaleManager.decreaseScale()
    
    def _redraw(self):
        for data in self.layerData:
            data["drawn"] = False
            
        """Redraws map
        """
        buff = self.texture.getBuffer()
        lock = buff.lock(0, buff.getSizeInBytes(), ogre.HardwareBuffer.HBL_NORMAL)
        
        width = self.tex_size[0]
        height = self.tex_size[1]
        
        import ctypes, cairo, math
        # creating buffer in memory from locked data
        data_buff = (ctypes.c_uint8 * (4 * width * height)).from_address(ogre.CastInt(lock))    # allocate a buffer class
    
        # creating surface for buffer in memory
        surface = cairo.ImageSurface.create_for_data(data_buff, cairo.FORMAT_ARGB32, width, height)
        
        # creating context for drawing
        self.ctx = cairo.Context(surface)
        
        # adjusting position to the center point
        tx, ty = self.getTranslation()
        
        
        #if self.mapSurface:
        #    self.mapSurface.finish()
        # creating a surface for map only
        
        
        for data in self.layerData:
            layerSurface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
            # creating a context for it
            layerCtx = cairo.Context(layerSurface)
            
            layerCtx.translate(tx, ty)
            layerCtx.rectangle(-tx, -ty, 
                               width, height)
            layerCtx.clip()
            
            selSurface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
            # creating a context for it
            selCtx = cairo.Context(selSurface)
            
            selCtx.translate(tx, ty)
            selCtx.rectangle(-tx, -ty, 
                               width, height)
            selCtx.clip()
            
            data["surface"] = layerSurface
            data["context"] = layerCtx
            
            data["selected-surface"] = selSurface
            data["selected-context"] = selCtx
        
        # drawing to a map context
        self.drawer.drawIt(self.scaleManager.scale, self.layerData)
        
        self.drawMap()
        
        buff.unlock()
    
    def setOrigin(self, pt):
        self.origin[0] = pt[0]
        self.origin[1] = pt[1]
        
        
    def moveOrigin(self, hor, ver):
        factor = self.drawer.manager.getFactor()
        if hor != 0:
            self.origin[0] += .1 * hor / factor
        if ver != 0:
            self.origin[1] += .1 * ver / factor
        print "origin: " + str(self.origin)
        

    def drawLayerSelection(self, layer):
        for data in self.layerData:
            if data["layer"] == layer:
                width = self.tex_size[0]
                height = self.tex_size[1]
                selSurface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
                # creating a context for it
                selCtx = cairo.Context(selSurface)
                tx, ty = self.getTranslation()
                selCtx.translate(tx, ty)
                selCtx.rectangle(-tx, -ty, 
                                   width, height)
                selCtx.clip()
                data["selected-surface"] = selSurface
                data["selected-context"] = selCtx
                                
                buff = self.texture.getBuffer()
                lock = buff.lock(0, buff.getSizeInBytes(), ogre.HardwareBuffer.HBL_NORMAL)
                self.drawer.drawLayerData(data, True)
                self.drawMap()
                buff.unlock()
                break;
            
   
    def _createFieldFromContent(self):
        """Creates map field for drawing from node content
        """
        data = self._getContent()
        if data is None:    return
    
        parser = map_utils.map_parser.LayersParser()
        #FIXME delete line with \n
        list = data.split('\r\n')
        parser.parseLayers(list)      
           
        self.drawer = fieldDrawer.FieldDrawer()
        #self.field = field.Field()
        self.drawer.field = field.Field()
        self.scaleManager = self.drawer.manager
        
        transformScale = (0.5, 1)
            
        #classifier = self.field.classifier
       
        self.drawer.standardConstrainPx = self.tex_size[1]
        #layer = field.Layer()

        width = self.tex_size[0]
        height = self.tex_size[1]
       
        layerNum = 0
        for lay in parser.layers:
            layer = field.Layer()
            layer.name = parser.layer_name[layerNum]
            layerNum += 1
            
            for i in range(len(lay.mif_data)):
                if lay.object_type[i] == 'REGION':
                    region = field.PolygonItem(lay.mif_data[i], transformScale)
                    region.type = int(lay.mid_data[i]['CODE'])
                    region.setAttributes(lay.mid_data[i])
                    layer.addItem(region)
                elif lay.object_type[i] == 'LINE':
                    line = field.LineItem(lay.mif_data[i], transformScale)
                    line.type = int(lay.mid_data[i]['CODE'])
                    line.setAttributes(lay.mid_data[i])
                    layer.addItem(line)
                elif lay.object_type[i] == 'PLINE':
                    pline = field.LineItem(lay.mif_data[i], transformScale)
                    pline.type = int(lay.mid_data[i]['CODE'])
                    pline.setAttributes(lay.mid_data[i])
                    #FIXME change LineItem   (draw one part)
                    layer.addItem(pline)
                elif lay.object_type[i] == 'POINT':
                    pass
                
            self.drawer.field.addLayer(layer)
            
        self.field = self.drawer.standardField = self.drawer.createStandardField()
        
        #self.field
        #print "lrs: "  + str(self.field.layers);
        
        for layer in self.field.layers:
            surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
            ctx = cairo.Context(surface)
            self.layerData.append({"layer": layer, "surface": surface, "context": ctx, "drawn": False})
                 
        
        
        
    def _getContent(self):
        """Returns node content
        """        
        session = core.Kernel.session()
        _addr = self._getSheet()._getScAddr()
        if _addr is not None:
            _cont = session.get_content_const(_addr)
            assert _cont is not None
            _cont_data = _cont.convertToCont()
            data = _cont.get_data(_cont_data.d.size)
            
            #print data
            
            return data            
            
        return None
