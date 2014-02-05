# coding=utf-8
import sc_core.pm as sc
import suit.core.keynodes as keynodes
import suit.core.sc_utils as sc_utils
import sc_core.constants as sc_constants
import suit.core.kernel as core
import logic_keynodes

session = core.Kernel.session()

disjunctionNode = logic_keynodes.Relation.nrel_disjunction
conjunctionNode = logic_keynodes.Relation.nrel_conjunction
equalNode = logic_keynodes.Relation.nrel_equivalence
implicationNode = logic_keynodes.Relation.nrel_implication
negationNode = logic_keynodes.Relation.nrel_negation

def getFormula(session, node, prevOp):
    """"""
    it_attr = session.create_iterator(session.sc_constraint_new(sc_constants.CONSTR_3_a_a_f, sc.SC_CONST | sc.SC_NODE, sc.SC_A_CONST | sc.SC_POS, node), True)

    attr_node = None

    while not it_attr.is_over():
        cur_node = it_attr.value(0)
        if cur_node==disjunctionNode or cur_node==conjunctionNode or cur_node==equalNode or cur_node==implicationNode or cur_node==negationNode:
            attr_node = cur_node
            break
        it_attr.next()

    if attr_node==None:
        return getNode(session, node)
    else:
        if attr_node==disjunctionNode:
            return getDisjunction(session, node, prevOp)
        elif attr_node==conjunctionNode:
            return getConjunction(session, node, prevOp)
        elif attr_node==equalNode:
            return getEqual(session, node, prevOp)
        elif attr_node==implicationNode:
            return getImplication(session, node, prevOp)
        elif attr_node==negationNode:
            return getNegation(session, node)

def getDisjunction(session, node, prevOp):
    """"""
    first = True
    brackets = (prevOp==negationNode or prevOp==conjunctionNode)
    res = u""
    if (brackets==True):
        res+=u"("
    it = session.create_iterator(session.sc_constraint_new(sc_constants.CONSTR_3_f_a_a, node, sc.SC_A_CONST | sc.SC_POS, sc.SC_CONST | sc.SC_NODE), True)

    while not it.is_over():
        val = getFormula(session, it.value(2), disjunctionNode)
        if first==True:
            res += val
            first = False
        else:
            res += u" ^ "+val
        it.next()

    if (brackets==True):
        res+=u")"

    return res

def getConjunction(session, node, prevOp):
    """"""    
    first = True;
    brackets = (prevOp==negationNode)
    res = u"";
    if (brackets==True):
        res+=u"("
    it = session.create_iterator(session.sc_constraint_new(sc_constants.CONSTR_3_f_a_a, node, sc.SC_A_CONST | sc.SC_POS, sc.SC_CONST | sc.SC_NODE), True)
    while not it.is_over():
        val = getFormula(session, it.value(2), conjunctionNode)
        if first==True:
            res+=val
            first = False
        else:
            res+=u" & "+val
        it.next()
        
    if (brackets==True):
        res+=u" )"
        
    return res

def getImplication(session, node, prevOp):
    """"""
    ifNode = session.find_keynode_full_uri(u"/seb/logic/если_")
    thenNode = session.find_keynode_full_uri(u"/seb/logic/то_")
    ifVal = u"";
    thenVal = u"";

    if_it = session.create_iterator(session.sc_constraint_new(sc_constants.CONSTR_5_f_a_a_a_f, node, sc.SC_A_CONST | sc.SC_POS, sc.SC_CONST | sc.SC_NODE, sc.SC_A_CONST | sc.SC_POS, ifNode), True)
    ifVal = getFormula(session, if_it.value(2), implicationNode)

    then_it = session.create_iterator(session.sc_constraint_new(sc_constants.CONSTR_5_f_a_a_a_f, node, sc.SC_A_CONST | sc.SC_POS, sc.SC_CONST | sc.SC_NODE, sc.SC_A_CONST | sc.SC_POS, thenNode), True)
    thenVal = getFormula(session, then_it.value(2), implicationNode)

    res = ifVal + u" -> " + thenVal;
    if (prevOp==negationNode or prevOp==conjunctionNode or prevOp==disjunctionNode):
        res = u" (" + res + u" )"

    return res

def getEqual(session, node, prevOp):
    """"""    
    res = u""
    first = True
    brackets = (prevOp==negationNode or prevOp==conjunctionNode or prevOp==disjunctionNode or prevOp==implicationNode)

    if (brackets==True):
        res+=u"("

    it = session.create_iterator(session.sc_constraint_new(sc_constants.CONSTR_3_f_a_a, node, sc.SC_A_CONST | sc.SC_POS, sc.SC_CONST | sc.SC_NODE), True)

    while not it.is_over():
        val = getFormula(session, it.value(2), equalNode)
        if first==True:
            res+=val
            first = False
        else:
            res+=u" <-> "+val
        it.next()

    if (brackets==True):
        res+=u" )"

    return res

def getNegation(session, node):
    """"""    
    res = u" ! "

    it = session.create_iterator(session.sc_constraint_new(sc_constants.CONSTR_3_f_a_a, node, sc.SC_A_CONST | sc.SC_POS, sc.SC_CONST | sc.SC_NODE), True)

    if not it.is_over():
        res += getFormula(session, it.value(2), negationNode)

    return res

def getNode(session, node):
    """"""
    return session.get_idtf(node)
        
        
def getOrientedPair(session, begin, sheaf, end, attr):
    """"""
    result = []
    result.append(begin)
    result.append(sheaf)
    result.append(end)
    result.append(attr)
    result.append(keynodes.n_1)
    result.append(keynodes.n_2)
    it1 = session.create_iterator(session.sc_constraint_new(sc_constants.CONSTR_5_f_a_f_a_a, sheaf, sc.SC_POS, begin, sc.SC_POS, sc.SC_CONST | sc.SC_NODE), True)
    it2 = session.create_iterator(session.sc_constraint_new(sc_constants.CONSTR_5_f_a_f_a_a, sheaf, sc.SC_POS, end, sc.SC_POS, sc.SC_CONST | sc.SC_NODE), True)
    it3 = session.create_iterator(session.sc_constraint_new(sc_constants.CONSTR_3_f_a_f, attr, sc.SC_A_CONST | sc.SC_POS, sheaf), True)
    result.append(it1.value(1))
    result.append(it1.value(3))
    result.append(it2.value(1))
    result.append(it1.value(3))
    result.append(it3.value(1))
    print result
    return result