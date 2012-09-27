
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
Created on 29.06.2010

@author: Denis Koronchik
'''

from suit.cf import BaseModeLogic 
#from framework.BaseModeLogic import BaseModeLogic
import chem_modes, chem_objects
import chem_env

class ChemistryViewer(BaseModeLogic):
    
    def __init__(self):
        BaseModeLogic.__init__(self)
        
        self._old_color_back = None
        
        import ogre.io.OIS as ois
        self.appendMode(ois.KC_V, chem_modes.ChemistryViewMode(self))
        self.switchMode(ois.KC_V)
        
    def __del__(self):
        BaseModeLogic.__del__(self)
        
    def delete(self):
        BaseModeLogic.delete(self)
        
    def _setSheet(self, _sheet):
        BaseModeLogic._setSheet(self, _sheet)
        
        _sheet.eventRootChanged = self._onRootChanged
        _sheet.eventUpdate = self._onUpdate 
        
        # go to 3d mode
        #_sheet.changeMode(render_engine.Mode_Perspective)
        import suit.core.layout.LayoutGroupForceDirected as layout
        _sheet.setLayoutGroup(layout.LayoutGroupForceSimple(_gravity = 0.1,
                                                            _repulsion = 3.5,
                                                            _length = 2.0,
                                                            _rigidity = 10.0,
                                                            _step_max = 0.05,
                                                            _step_min = 0.001))
        
        
    def _onRootChanged(self, _isRoot):
        """Root mode changing
        """
        import suit.core.render.engine as render_engine
        import ogre.renderer.OGRE as ogre
                
        if _isRoot:
            self._old_color_back = render_engine._ogreViewport.getBackgroundColour()
            clr = chem_env.color_back
            render_engine._ogreViewport.setBackgroundColour(ogre.ColourValue(clr[0], clr[1], clr[2], clr[3]))
        else:
            if self._old_color_back is not None:
                render_engine._ogreViewport.setBackgroundColour(self._old_color_back)
                
        BaseModeLogic._onRootChanged(self, _isRoot)
        
    def _onUpdate(self, _timeSinceLastFrame):
        """Viewer update message
        """
        if self._active_mode is not None:
            self._active_mode._update(_timeSinceLastFrame)
        
    def addAtom(self, _pos, _name):
        """Adds atom to scene
        
        @param _pos:    atom position in scene
        @type _pos:    ogre.Vector3
        @param _type:    atom name from periodical table
        @type _type:    str
        
        @return: added atom object
        @rtype: ChemistryAtom
        """
        atom = chem_objects.ChemistryAtom()
        atom.setPosition(_pos)
        atom.setName(_name)
        
        self._getSheet().addChild(atom)
        return atom
    
    def addLink(self, _bAtom, _eAtom):
        """Adds link between atoms
        
        @param _bAtom:    begin atom
        @type _bAtom:    ChemistryAtom
        @param _eAtom:    end atom
        @type _eAtom:    ChemistryAtom
        
        @return: added link object
        @rtype: ChemistryLink
        """
        link = chem_objects.ChemistryLink()
        link.setBegin(_bAtom)
        link.setEnd(_eAtom)
        
        self._getSheet().addChild(link)
        return link