
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
Created on 06.10.2009

@author: Denis Koronchik
'''

"""Realization of scg-viewer component
"""
import os

from suit.cf import BaseModeLogic

import suit.core.kernel as core
import suit.core.utils as utils
import suit.core.objects as objects
import ogre.renderer.OGRE as ogre
import ogre.io.OIS as ois
import scg_modes
import scg_objects
import scg_environment as env

# store log manager to make it more useful
logManager = utils.LogManager.getSingleton()

#############
# resources #
#############
def getResourceLocation():
    """Return resource location folder
    """
    return core.Kernel.getResourceLocation() + 'scg'

def getResourceGroup():
    """Return resource group name
    """
    return 'scg'


###########
# classes #
###########
class SCgViewer(BaseModeLogic):
    """Class that represents logic of scg-viewer.

    When we creating viewer it registers in sc-memory.
    """
    def __init__(self):
        """Constructor
        """
        BaseModeLogic.__init__(self)

        # addr of viewed set
        self.view_set_addr = None

        # view modes
        self.appendMode(ois.KC_V, scg_modes.SCgViewMode(self))
        self.switchMode(ois.KC_V)

        self.materialName = None
        self.material = None
        self.textureName = None
        self.texture = None

    def __del__(self):
        """Destructor
        """
        BaseModeLogic.__del__(self)

    def delete(self):
        """Deletion message
        """
        BaseModeLogic.delete(self)
        self._destroyMaterial()
        self._destroyTexture()

    def _setSheet(self, _sheet):
        """Sets sheet that controls by this logic
        """
        BaseModeLogic._setSheet(self, _sheet)

        _sheet.eventContentUpdate = self._onContentUpdate

        self.createTextureAndMaterialNames()

    def createTextureAndMaterialNames(self):
        kernel = core.Kernel.getSingleton()

        file_name = "%s.%s" %(str(self)[1:-1],'png')

        path = os.path.join(kernel.cache_path, 'scg_preview')
        if not os.path.exists(path):
            os.makedirs(path)
        self.textureName  = os.path.join(path, file_name)
        self.materialName = "scg_preview_" + str(self)

    def _onContentUpdate(self):
        import suit.core.keynodes as keynodes
        sheet = self._getSheet()

        sheet.content_type = objects.ObjectSheet.CT_String
        sheet.content_data = str("") # make translation into gwf
        sheet.content_format = keynodes.ui.format_scgx

    def _destroyMaterial(self):
        """Destroys material
        """
        if self.material is None: return
        ogre.MaterialManager.getSingleton().remove(self.material)
        del self.material

    def _destroyTexture(self):
        if self.texture is None: return
        ogre.TextureManager.getSingleton().remove(self.texture)

    def _createMaterial(self):
        """Creates material for image viewing
        """
        self.material = ogre.MaterialManager.getSingleton().create(self.materialName, env.resource_group)
        mpass = self.material.getTechnique(0).getPass(0)
        mpass.setLightingEnabled(False)
        mpass.setDepthWriteEnabled(True)
        tus = mpass.createTextureUnitState(self.textureName[:-3])
        self._getSheet()._setMaterialShowName(self.materialName)
        self._getSheet()._setMaterialShowName(self.materialName)

    def _updateTexture(self):
        if self.texture is None:
            txtrMngr = ogre.TextureManager.getSingleton()
            self.texture = txtrMngr.createManual(self.textureName[:-3], env.resource_group, ogre.TEX_TYPE_2D,
                                                 128, 128, 0, ogre.PF_X8R8G8B8, ogre.TU_RENDERTARGET);
            self._createMaterial()
        self._readFromScreenshotPictureToTexture()

    def _readFromScreenshotPictureToTexture(self):
        f = open(self.textureName, 'rb')
        data = f.read()
        f.close()

        stream = ogre.MemoryDataStream("%s" % str(self), len(data), False)
        stream.setData(data)
        img = ogre.Image()
        img.load(stream, ogre.Image.getFileExtFromMagic(stream))

        txtrMngr = ogre.TextureManager.getSingleton()
        screenshot = txtrMngr.loadImage(self.textureName, env.resource_group, img)
        self.texture.getBuffer().blit(screenshot.getBuffer())
        txtrMngr.remove(screenshot)
        screenshot.unload()

    def makeNewScreenshot(self):
        try:
            window = ogre.Root.getSingleton().getAutoCreatedWindow()
            window.writeContentsToFile(self.textureName)
            self._updateTexture()
        except WindowsError as err:
            print err
            print "can't create prewiew"
