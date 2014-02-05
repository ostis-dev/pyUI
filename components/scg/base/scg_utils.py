
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
Created on 20.01.2010

@author: Denis Koronchik
'''

import scg_objects
import suit.core.kernel as core
import suit.core.objects as objects
import sc_core.pm as sc
import suit.core.sc_utils as sc_utils
import suit.core.keynodes as keynodes

# FIXME:    Move to sheet class and make sc-memory working
def createWindowFromNode(_node, _format, _is_edit):
    """Creates sc.g-window from sc.g-node
    @param _node:    node to create window from
    @type _node:    ScgNode
    @param _format:    sc-element that designate format for node content
    @type _format:    sc_global_addr
    @param _is_edit:    flag to create editor
    @type _is_edit:    boolean
    
    @return: window object
    @rtype: objects.ObjectSheet
    """
    assert type(_node) is scg_objects.SCgNode
   
    session = core.Kernel.session()
    segment = core.Kernel.segment()
    
    parent = _node.parent
    
    # creating sc-element that designate window
    el = _node._getScAddr()
    if el is not None:
        # FIXME:    changing type for variable
        session.change_type(el, sc.SC_N_CONST)
#    else:
#        el = sc_utils.createNodeElement(session, segment, sc.SC_CONST)

    sheet = objects.ObjectSheet()
    if el is not None:
        sheet._setScAddr(el)
    
    
    sheet.hideContent()
    logic = None
    if _is_edit:
        logic = core.Kernel.getSingleton().createEditor(_format)
    else:
        logic = core.Kernel.getSingleton().createViewer(_format)
    
    # including window to formats set
    sc_utils.createPairPosPerm(session, segment, _format, el, sc.SC_CONST)
    
    sheet.setLogic(logic)
    parent.addChild(sheet)
    sheet.setPosition(_node.getPosition())
    
    # FIXME:    removing for old window types    
    _node._relinkToObject(sheet)
    
    parent._deleteObject(_node)
    
    # need to remove
    if _format.this == keynodes.ui.format_scgx.this:
        import suit.core.layout.LayoutGroupForceDirected as layout
        sheet.setLayoutGroup(layout.LayoutGroupForceSimple())
    
    # linking by relation with parent
#    sheaf = sc_utils.createPairBinaryOrient(session, segment, parent._getScAddr(), el, sc.SC_CONST)
#    sc_utils.createPairPosPerm(session, segment, keynodes.ui.nrel_child_window, sheaf, sc.SC_CONST)
    
    
    return sheet

def checkOnPointInContour(point, polygon):
    if len(polygon) < 3:
        return False
    q_patt = ((0,1), (3,2));

    import ogre.renderer.OGRE as ogre

    pred_pt = ogre.Vector3(polygon[-1].x, polygon[-1].y, 0)
    pred_pt.x -= point.x
    pred_pt.y -= point.y

    pred_q=q_patt[pred_pt.y<0][pred_pt.x<0];

    w = 0

    for cur_pt in polygon:
        cur_pt = ogre.Vector3(cur_pt.x, cur_pt.y, 0)
        cur_pt.x -= point.x
        cur_pt.y -= point.y

        q=q_patt[cur_pt.y<0][cur_pt.x<0];

        if q-pred_q == -3:
            w+=1
        if q-pred_q == 3:
            w-=1
        if q-pred_q == -2:
            if pred_pt[0]*cur_pt[1]>=pred_pt[1]*cur_pt[0]: w+=1
        if q-pred_q == 2:
            if not (pred_pt[0]*cur_pt[1]>=pred_pt[1]*cur_pt[0]): w-=1

        pred_pt = cur_pt
        pred_q = q
    return w != 0
