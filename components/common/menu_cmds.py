
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
Created on 02.02.2010

@author: Denis Koronchik
'''

import suit.core.keynodes as keynodes
import suit.core.kernel as core
import sc_core.constants as sc_constants
import sc_core.pm as sc
import suit.core.sc_utils as sc_utils

def get_sel_elements_set(_session, _seg):
    """ Builds set of selected elements in active window
    @param _session:    session to work with memory
    @type _session:    sc_session
    @param _seg:    segment to create set in
    @type _seg:    sc_segment
    
    @return: tuple (sc_addr of selected elements set, list of elements that need to be added to question)
    @rtype: tuple
    """
    sel_set = sc_utils.createNodeElement(_session, _seg, sc.SC_CONST)
    elements = []
    # appending selected elements to set
    kernel = core.Kernel.getSingleton()
    sel_objs = kernel.rootSheet.getSelected()
    
    for obj in sel_objs:
        _addr = obj._getScAddr()
        elements.append(sc_utils.createPairPosPerm(_session, _seg, sel_set, _addr, sc.SC_CONST))
        elements.append(_addr)
        
    return sel_set, elements

def get_all_elements_set(_session, _seg):
    """ Builds set of selected elements in active window
    @param _session:    session to work with memory
    @type _session:    sc_session
    @param _seg:    segment to create set in
    @type _seg:    sc_segment
    
    @return: tuple (sc_addr of selected elements set, list of elements that need to be added to question)
    @rtype: tuple
    """
    _set = sc_utils.createNodeElement(_session, _seg, sc.SC_CONST)
    elements = []
    # appending selected elements to set
    kernel = core.Kernel.getSingleton()
    _objs = kernel.rootSheet.getChilds()
    
    for obj in _objs:
        _addr = obj._getScAddr()
        if _addr is not None:
            elements.append(sc_utils.createPairPosPerm(_session, _seg, _set, _addr, sc.SC_CONST))
            elements.append(_addr)
        
    return _set, elements

def get_arguments_set(_session, _seg):
    """Builds set of command aguments
    @param _session:    session to work with sc-memory
    @type _session:    sc_session
    @param _seg:    segment to create set in
    @type _seg:    sc_segment
    
    @return: tuple (sc_addr of arguments set, list of elements that need to be added to question)
    @rtype: tuple
    """
    args_set = sc_utils.createNodeElement(_session, _seg, sc.SC_CONST)
    elements = []
    # appending arguments to set
    kernel = core.Kernel.getSingleton()
    arg_objs = kernel.getArguments()
    
    for obj in arg_objs:
        _addr = obj._getScAddr()
        elements.append(sc_utils.createPairPosPerm(_session, _seg, args_set, _addr, sc.SC_CONST))
        elements.append(_addr)
        
    return args_set, elements

def init_cmd(session, segment, sheet, _menu_item_addr, _general_formul, _cmd_class_set, _init_set):
    """Initialize question/command from template
    @param session: Session to work with sc-memory
    @param segment: Segment to create sc-constructions  
    @param sheet: Current root sheet (command initiated from it) 
    @param _menu_item_addr: sc-element that designate command (question) menu item
    @type _menu_item_addr: sc_addr
    @param _general_formul: sc-element that designate general formulation relation (different for questions and commands)
    @type _general_formul: sc_addr
    @param _cmd_class_set: sc-element that designate class of commands (used to search command node in template)
    @type _cmd_class_set: sc_addr 
    @param _init_set: sc-element that designate initiated commands set (different for commands and questions)
    @type _init_set: sc_addr  
    """
    kernel = core.Kernel.getSingleton()
    
    # getting question template
    q_templ = sc_utils.searchOneShotBinPairAttrToNode(session, _menu_item_addr, _general_formul, sc.SC_CONST)
    if not q_templ:
        raise RuntimeWarning("Question '%s' haven't template" % _caption)
        return

    # getting question node
    it = session.create_iterator(session.sc_constraint_new(sc_constants.CONSTR_5_f_a_a_a_f,
                                                                            _cmd_class_set,
                                                                            sc.SC_ARC,
                                                                            sc.SC_NODE,
                                                                            sc.SC_ARC,
                                                                            q_templ), True)
    question_node = None
    while not it.is_over():
        if sc_utils.checkIncToSets(session, it.value(2), [q_templ], 0):
            question_node = it.value(2)
            break
        
        it.next()
    
    if question_node is None:
        raise RuntimeError("Can't get command (question) node for a '%s' command" % str(_menu_item_addr))

    # creating question using template:
    # * iterate through elements of template set
    # * making values of parameters cmd_desc_..., add that values to addit_elements map
    # * replace var elements to const elements
    # * replace meta elements to var elements
    # * link replaced arcs
    params = {}
    addit_elements = {} # additional elements we need to add into question after params setup
    elements = []
    pairs = []
    
    it = session.create_iterator(session.sc_constraint_new(sc_constants.CONSTR_3_f_a_a,
                                                          q_templ,
                                                          sc.SC_A_CONST | sc.SC_POS,# | sc.SC_PERMANENT,
                                                          0), True)
    while not it.is_over():
        _el = it.value(2)
        elements.append(_el)
        # selected elements
        if _el.this == keynodes.ui.arg_set.this:
            params[str(_el.this)], elms = get_arguments_set(session, segment)
            addit_elements[str(_el.this)] = elms
        elif _el.this == keynodes.ui.arg_set_only.this: # place just set node into question node
            params[str(_el.this)], elms = get_arguments_set(session, segment)
        elif _el.this == keynodes.ui.arg_all_el.this:
            params[str(_el.this)], elms = get_all_elements_set(session, segment)
        elif _el.this == keynodes.ui.arg_cur_window.this:
            params[str(_el.this)] = sheet
        elif _el.this == keynodes.ui.arg_1.this:
            arguments = core.Kernel.getSingleton().getArguments()
            if len(arguments) > 0:
                params[str(_el.this)] = arguments[0]._getScAddr()
        elif _el.this == keynodes.ui.arg_2.this:
            arguments = core.Kernel.getSingleton().getArguments()
            if len(arguments) > 1:
                params[str(_el.this)] = arguments[1]._getScAddr()
        elif _el.this == keynodes.ui.arg_3.this:
            arguments = core.Kernel.getSingleton().getArguments()
            if len(arguments) > 1:
                params[str(_el.this)] = arguments[2]._getScAddr()
#            elif _el.this == keynodes.ui.cmd_desc_curr_window.this:
#                params[str(_el.this)] = kernel.rootSheet._getScAddr()
        else:
            el_type = session.get_type(_el)
            idtf = session.get_idtf(_el)
            if not sc_utils.isSystemId(idtf) or (el_type & sc.SC_CONST):
                params[str(_el.this)] = _el
            else:
                # recreate var and meta elements using rules:
                # * var -> const
                # * meta -> var
                post_type = 0
                if el_type & sc.SC_VAR:
                    post_type = sc.SC_CONST
                elif el_type & sc.SC_META:
                    post_type = sc.SC_VAR
                else:
                    raise RuntimeWarning("Unknown const type for element '%s'" % str(_el))
                
                if el_type & sc.SC_ARC:
                    pairs.append(_el)
                    params[str(_el.this)] = session.create_el(segment, sc.SC_ARC | post_type)
                elif el_type & sc.SC_NODE:
                    params[str(_el.this)] = session.create_el(segment, sc.SC_NODE | post_type)
                    # TODO: copy structure types for elements
                
        it.next()
    
    # add selected set to question set    
    q_node_new = params[str(question_node.this)]
    if sc_utils.checkIncToSets(session, keynodes.ui.arg_set, [question_node], sc.SC_POS | sc.SC_VAR) and sc_utils.checkIncToSets(session, keynodes.ui.arg_set, [q_templ], sc.SC_POS | sc.SC_CONST):
        # make pairs to additional elements
        for el in addit_elements[str(keynodes.ui.arg_set.this)]:
             assert sc_utils.createPairPosPerm(session, segment, q_node_new, el, sc.SC_CONST)
    
    
    # linking arcs
    for pair in pairs:
        # get begin and end elements
        _beg = session.get_beg(pair)
        _end = session.get_end(pair)
        
        if params.has_key(str(_beg.this)):
            _beg = params[str(_beg.this)]
        if params.has_key(str(_end.this)):
            _end = params[str(_end.this)]
            
        pair_new = params[str(pair.this)]
            
        session.set_beg(pair_new, _beg)
        session.set_end(pair_new, _end)
    
    
    # make authors set
    authors_node = sc_utils.createNodeElement(session, segment, sc.SC_CONST)
    sc_utils.createPairPosPerm(session, segment, authors_node, core.Kernel.getSingleton().getUserAddr(), sc.SC_CONST)
    assert authors_node is not None
    authors_pair_sheaf = sc_utils.createPairBinaryOrient(session, segment, params[str(question_node.this)], authors_node, sc.SC_CONST)
    assert authors_pair_sheaf is not None
    assert sc_utils.createPairPosPerm(session, segment, keynodes.common.nrel_authors, authors_pair_sheaf, sc.SC_CONST)
    
    
    # make output windows set
    output_node = sc_utils.createNodeElement(session, segment, sc.SC_CONST)
    assert output_node is not None
    
#        sc_utils.copySet(session, keynodes.ui.set_output_windows, output_node, segment)
    output_count = 0
    it = session.create_iterator(session.sc_constraint_new(sc_constants.CONSTR_3_f_a_a,
                                                       keynodes.ui.set_output_windows,
                                                       sc.SC_ARC,
                                                       0), True)
    while not it.is_over():
       sc_utils.createPair(session, segment, output_node, it.value(2), session.get_type(it.value(1)))
       output_count += 1
       it.next()
       
    if output_count == 0:
       sc_utils.createPairPosPerm(session, segment, output_node, kernel.getMainWindow()._getScAddr(), sc.SC_CONST )
    
    # link output windows set to question
    output_sheaf = sc_utils.createPairBinaryOrient(session, segment, output_node, params[str(question_node.this)], sc.SC_CONST)
    assert output_sheaf is not None
    sc_utils.createPairPosPerm(session, segment, keynodes.ui.nrel_set_of_output_windows, output_sheaf, sc.SC_CONST) 
    
    # initiate question
    assert sc_utils.createPairPosPerm(session, segment, _init_set, params[str(question_node.this)], sc.SC_CONST) is not None


def start_menu_cmd(_menu_item):
    """Starts menu command
    @param _menu_item:    menu item for run
    @type _menu_item:    SCgMenuItem
    """
    
    # check params
    _menu_item_addr = _menu_item._getScAddr()
    _caption = _menu_item.getText()
    if _menu_item_addr is None:   raise RuntimeError("There is no item sc_addr for menu item '%s'" % _caption)
    
    # preparing for sc-machine working (translating it to SC-code)
    kernel = core.Kernel.getSingleton()
    kernel.getSingleton().prepareForScMachine()
    session = kernel.session()
    segment = kernel.segment()      # TODO:    make tmp segment usage
    
    # ask question using template
    if _menu_item.question:
        init_cmd(session, segment, kernel.getRootSheet()._getScAddr(), _menu_item_addr,
                 keynodes.questions.nrel_general_formulation, keynodes.questions.question, keynodes.questions.initiated)
    elif _menu_item.atom:
        init_cmd(session, segment, kernel.getRootSheet()._getScAddr(), _menu_item_addr,
                 keynodes.ui.nrel_template_user_cmd, keynodes.ui.user_cmd, keynodes.ui.init_user_cmd)
        
def generate_output_windows_set(_session, _segment, _parent_window):
    """Generates output windows set
    @param _session:    session to work with sc-memory
    @type _session:    MThreadSession
    @param _segment:    segment in sc-memory to work in
    @type _segment:    sc_segment
    @param _parent_window:    parent window object
    @type _parent_window:    ObjectSheet
    
    @return: output windows set
    @rtype: sc_global_addr
    """
    import srs_engine.sc_utils as sc_utils
    # preparing for sc-machine working (translating it to SC-code)
    output_windows_set = sc_utils.createNodeElement(_session, _segment, sc.SC_CONST)
    
    kernel = core.Kernel.getSingleton()
    
    output_windows = kernel.getOutputWindows()
    import srs_engine.objects as objects
    
    for _addr, _exists, _edit in output_windows:
        window_node = _addr
        if not _exists:
            # creating new window
            window = objects.ObjectSheet()
            window.hideContent()
            
            if _edit:
                try:
					window.setLogic(kernel.createEditor(_addr))
                except:
					print "There are no editor for addr %s" % (str(_addr))
					window.setLogic(kernel.createViewer(_addr))
            else:
                window.setLogic(kernel.createViewer(_addr))
            
            kernel.mainWindow.addChild(window)
            sc_utils.createPairPosPerm(_session, _segment, _addr, window._getScAddr(), sc.SC_CONST)
            window_node = window._getScAddr()
            
            # test
            if _addr.this == keynodes.ui.format_scgx.this:
                import srs_engine.layout.LayoutGroupForceDirected as layout
                window.setLayoutGroup(layout.LayoutGroupForceSimple())
        else:
            # test
            fmt = sc_utils.getContentFormat(_session, _addr)
            if fmt and fmt.this == keynodes.ui.format_scgx.this:
                import srs_engine.layout.LayoutGroupForceDirected as layout
                
                # FIXME:    thinking about multiply objects for sc_addr
                windows = objects.ScObject._sc2Objects(_addr)
                assert len(windows) > 0
                window = windows[0]
                
                if window.getLayoutGroup() is None:
                    window.setLayoutGroup(layout.LayoutGroupForceSimple())
                
    
        sc_utils.createPairPosPerm(_session, _segment, output_windows_set, window_node, sc.SC_CONST)
#    # test
#    import srs_engine.objects as objects
#    sheet = objects.ObjectSheet()
#    sheet.hideContent()
#    
#    sheet.setLogic(kernel.createEditor(keynodes.ui.format_scgx))
#    kernel.rootSheet.addChild(sheet)
#    sc_utils.createPair(_session, kernel.segment(), keynodes.ui.format_scgx, sheet._getScAddr(), sc.SC_A_CONST | sc.SC_POS)
#    kernel.setRootSheet(sheet)
#    
#    import srs_engine.layout.LayoutGroupForceDirected as layout
#    sheet.setLayoutGroup(layout.LayoutGroupForceSimple())
#    # test
#    
#    sc_utils.createPairPosPerm(_session, _segment, output_windows_set, sheet._getScAddr(), sc.SC_CONST)
    
    return output_windows_set
    
    
    
