# -*- coding: utf-8 -*-
import suit.core.kernel as core
import suit.core.sc_utils as sc_utils
import sc_core.pm as sc
import sc_core.constants as sc_constants
import math2sc
import suit.core.keynodes as keynodes

def genEqualityRelation(session, segment, operation, _result):
    el1 = math2sc.variables_sc[operation[0]]
    el2 = math2sc.variables_sc[operation[1]]

    setNode = session.create_el_idtf(core.Kernel.segment(), sc.SC_NODE, "")[1]
    sc_utils.createPair(session,core.Kernel.segment(), _result, setNode, sc.SC_CONST)

    arc1 = sc_utils.createPair(session,core.Kernel.segment(), setNode, el1, sc.SC_CONST)
    arc2 = sc_utils.createPair(session,core.Kernel.segment(), setNode, el2, sc.SC_CONST)
    sc_utils.createPair(session,core.Kernel.segment(), _result, arc1, sc.SC_CONST)
    sc_utils.createPair(session,core.Kernel.segment(), _result, arc2, sc.SC_CONST)

    idtf = "равенство*"
    idtf = sc_utils.utf8ToCp1251(str(idtf))
    eqNode = sc_utils.getElementByIdtf(idtf, segment)
    if eqNode == None:
        eqNode = session.create_el_idtf(core.Kernel.segment(), sc.SC_NODE, idtf)[1]
        for param in [keynodes.info.stype_bin_orient_norole_rel]:
            sc_utils.createPairPosPerm(session, core.Kernel.segment(), param, eqNode, sc.SC_CONST)
    sc_utils.createPair(session,core.Kernel.segment(), _result, eqNode, sc.SC_CONST)

    relarc = sc_utils.createPair(session,core.Kernel.segment(), eqNode, setNode, sc.SC_CONST)
    sc_utils.createPair(session,core.Kernel.segment(), _result, relarc, sc.SC_CONST)
    return el1

def gen_fracture_relation(session, segment, operation, _result):
    el1 = math2sc.variables_sc[operation[0]]
    el2 = math2sc.variables_sc[operation[1]]

    #gen node that represents fracture
    setNode = session.create_el_idtf(core.Kernel.segment(), sc.SC_NODE, "")[1]
    sc_utils.createPair(session,core.Kernel.segment(), _result, setNode, sc.SC_CONST)

    arc1 = sc_utils.createPair(session,core.Kernel.segment(), setNode, el1, sc.SC_CONST)
    arc2 = sc_utils.createPair(session,core.Kernel.segment(), setNode, el2, sc.SC_CONST)
    sc_utils.createPair(session,core.Kernel.segment(), _result, arc1, sc.SC_CONST)
    sc_utils.createPair(session,core.Kernel.segment(), _result, arc2, sc.SC_CONST)

    #find or generate ordinal fracture node
    idtf = "обыкновенная дробь"
    idtf = sc_utils.utf8ToCp1251(str(idtf))
    powNode = sc_utils.getElementByIdtf(idtf, segment)
    if powNode == None:
        powNode = session.create_el_idtf(core.Kernel.segment(), sc.SC_NODE, idtf)[1]
    sc_utils.createPair(session,core.Kernel.segment(), _result, powNode, sc.SC_CONST)
    relarc = sc_utils.createPair(session,core.Kernel.segment(), powNode, setNode, sc.SC_CONST)
    sc_utils.createPair(session,core.Kernel.segment(), _result, relarc, sc.SC_CONST)

    #find or generate numerator
    numIdtf = "числитель_"
    numIdtf = sc_utils.utf8ToCp1251(str(numIdtf))
    numNode = sc_utils.getElementByIdtf(numIdtf, segment)
    if numNode == None:
        numNode = session.create_el_idtf(core.Kernel.segment(), sc.SC_NODE, numIdtf)[1]
    sc_utils.createPair(session,core.Kernel.segment(), _result, numNode, sc.SC_CONST)
    a = sc_utils.createPair(session,core.Kernel.segment(), numNode, arc1, sc.SC_CONST)
    sc_utils.createPair(session,core.Kernel.segment(), _result, a, sc.SC_CONST)

    #find or generate denominator
    numIdtf = "знаменатель_"
    numIdtf = sc_utils.utf8ToCp1251(str(numIdtf))
    numNode = sc_utils.getElementByIdtf(numIdtf, segment)
    if numNode == None:
        numNode = session.create_el_idtf(core.Kernel.segment(), sc.SC_NODE, numIdtf)[1]
    sc_utils.createPair(session,core.Kernel.segment(), _result, numNode, sc.SC_CONST)
    a = sc_utils.createPair(session,core.Kernel.segment(), numNode, arc2, sc.SC_CONST)
    sc_utils.createPair(session,core.Kernel.segment(), _result, a, sc.SC_CONST)

    return setNode

def genPowerRelation(session, segment, operation, _result):
    el1 = math2sc.variables_sc[operation[0]]
    el2 = math2sc.variables_sc[operation[1]]

    #gen set of sum components
    setNode = session.create_el_idtf(core.Kernel.segment(), sc.SC_NODE, "")[1]
    sc_utils.createPair(session,core.Kernel.segment(), _result, setNode, sc.SC_CONST)

    arc1 = sc_utils.createPair(session,core.Kernel.segment(), setNode, el1, sc.SC_CONST)
    arc2 = sc_utils.createPair(session,core.Kernel.segment(), setNode, el2, sc.SC_CONST)
    sc_utils.createPair(session,core.Kernel.segment(), _result, arc1, sc.SC_CONST)
    sc_utils.createPair(session,core.Kernel.segment(), _result, arc2, sc.SC_CONST)

    #gen sum relations
    res = session.create_el_idtf(core.Kernel.segment(), sc.SC_NODE, "")[1]  #add result node
    sc_utils.createPair(session,core.Kernel.segment(), _result, res, sc.SC_CONST)

    relation = sc_utils.createPair(session,core.Kernel.segment(), setNode, res, sc.SC_CONST)
    sc_utils.createPair(session,core.Kernel.segment(), _result, relation, sc.SC_CONST)

    idtf = "возведение в степень*"
    idtf = sc_utils.utf8ToCp1251(str(idtf))
    powNode = sc_utils.getElementByIdtf(idtf, segment)
    if powNode == None:
        powNode = session.create_el_idtf(core.Kernel.segment(), sc.SC_NODE, idtf)[1]
        for param in [keynodes.info.stype_bin_orient_norole_rel]:
            sc_utils.createPairPosPerm(session, core.Kernel.segment(), param, powNode, sc.SC_CONST)
    sc_utils.createPair(session,core.Kernel.segment(), _result, powNode, sc.SC_CONST)

    relarc = sc_utils.createPair(session,core.Kernel.segment(), powNode, setNode, sc.SC_CONST)

    baseIdtf = "основание_"
    baseIdtf = sc_utils.utf8ToCp1251(str(baseIdtf))
    baseNode = sc_utils.getElementByIdtf(baseIdtf, segment)
    if baseNode == None:
        baseNode = session.create_el_idtf(core.Kernel.segment(), sc.SC_NODE, baseIdtf)[1]
    sc_utils.createPair(session,core.Kernel.segment(), _result, baseNode, sc.SC_CONST)
    a = sc_utils.createPair(session,core.Kernel.segment(), baseNode, arc1, sc.SC_CONST)
    sc_utils.createPair(session,core.Kernel.segment(), _result, a, sc.SC_CONST)


    expIdtf = "показатель_"
    expIdtf = sc_utils.utf8ToCp1251(str(expIdtf))
    expNode = sc_utils.getElementByIdtf(expIdtf, segment)
    if expNode == None:
        expNode = session.create_el_idtf(core.Kernel.segment(), sc.SC_NODE, expIdtf)[1]
    sc_utils.createPair(session,core.Kernel.segment(), _result, expNode, sc.SC_CONST)
    a = sc_utils.createPair(session,core.Kernel.segment(), expNode, arc2, sc.SC_CONST)
    sc_utils.createPair(session,core.Kernel.segment(), _result, a, sc.SC_CONST)


    powerIdtf = "результат_"
    powerIdtf = sc_utils.utf8ToCp1251(str(powerIdtf))
    powerNode = sc_utils.getElementByIdtf(powerIdtf, segment)
    if powerNode == None:
        powerNode = session.create_el_idtf(core.Kernel.segment(), sc.SC_NODE, powerIdtf)[1]
    sc_utils.createPair(session,core.Kernel.segment(), _result, powerNode, sc.SC_CONST)
    a = sc_utils.createPair(session,core.Kernel.segment(), powerNode, relation, sc.SC_CONST)
    sc_utils.createPair(session,core.Kernel.segment(), _result, a, sc.SC_CONST)

    sc_utils.createPair(session,core.Kernel.segment(), _result, relarc, sc.SC_CONST)
    return res

def genSumRelation(session, segment, operation, _result):
    """

    @param session: session
    @param segment: list of segments to search objects in
    @param operation: sum operation and list of operands
    @param _result: a node which the result of translation
    @return: a node that represents the result of summ
    """
    el1 = math2sc.variables_sc[operation[0]]
    el2 = math2sc.variables_sc[operation[1]]

    #gen set of sum components
    setNode = session.create_el_idtf(core.Kernel.segment(), sc.SC_NODE, "")[1]
    sc_utils.createPair(session,core.Kernel.segment(), _result, setNode, sc.SC_CONST)

    arc1 = sc_utils.createPair(session,core.Kernel.segment(), setNode, el1, sc.SC_CONST)
    arc2 = sc_utils.createPair(session,core.Kernel.segment(), setNode, el2, sc.SC_CONST)
    sc_utils.createPair(session,core.Kernel.segment(), _result, arc1, sc.SC_CONST)
    sc_utils.createPair(session,core.Kernel.segment(), _result, arc2, sc.SC_CONST)

    #gen sum relations
    res = session.create_el_idtf(core.Kernel.segment(), sc.SC_NODE, "")[1]  #add result node
    sc_utils.createPair(session,core.Kernel.segment(), _result, res, sc.SC_CONST)

    relation = sc_utils.createPair(session,core.Kernel.segment(), setNode, res, sc.SC_CONST)
    sc_utils.createPair(session,core.Kernel.segment(), _result, relation, sc.SC_CONST)

    idtf = "сумма*"
    idtf = sc_utils.utf8ToCp1251(str(idtf))
    sumNode = sc_utils.getElementByIdtf(idtf, segment)
    if sumNode == None:
        sumNode = session.create_el_idtf(core.Kernel.segment(), sc.SC_NODE, idtf)[1]
        for param in [keynodes.info.stype_bin_orient_norole_rel]:
            sc_utils.createPairPosPerm(session, core.Kernel.segment(), param, sumNode, sc.SC_CONST)
    sc_utils.createPair(session,core.Kernel.segment(), _result, sumNode, sc.SC_CONST)

    relarc = sc_utils.createPair(session,core.Kernel.segment(), sumNode, relation, sc.SC_CONST)
    sc_utils.createPair(session,core.Kernel.segment(), _result, relarc, sc.SC_CONST)
    return res

def genDifferenceRelation(session, segment, operation, _result):
    el1 = math2sc.variables_sc[operation[0]] #minuend
    el2 = math2sc.variables_sc[operation[1]] #subtrahend
    res = session.create_el_idtf(core.Kernel.segment(), sc.SC_NODE, "")[1]  #difference result node
    sc_utils.createPair(session,core.Kernel.segment(), _result, res, sc.SC_CONST)

    setNode = session.create_el_idtf(core.Kernel.segment(), sc.SC_NODE, "")[1]
    sc_utils.createPair(session,core.Kernel.segment(), _result, setNode, sc.SC_CONST)

    #gen input sum parameters
    arc1 = sc_utils.createPair(session,core.Kernel.segment(), setNode, res, sc.SC_CONST)
    arc2 = sc_utils.createPair(session,core.Kernel.segment(), setNode, el2, sc.SC_CONST)
    sc_utils.createPair(session,core.Kernel.segment(), _result, arc1, sc.SC_CONST)
    sc_utils.createPair(session,core.Kernel.segment(), _result, arc2, sc.SC_CONST)

    relation = sc_utils.createPair(session,core.Kernel.segment(), setNode, el1, sc.SC_CONST)
    sc_utils.createPair(session,core.Kernel.segment(), _result, relation, sc.SC_CONST)

    idtf = "сумма*"
    idtf = sc_utils.utf8ToCp1251(str(idtf))
    sumNode = sc_utils.getElementByIdtf(idtf, segment)
    if sumNode == None:
        sumNode = session.create_el_idtf(core.Kernel.segment(), sc.SC_NODE, idtf)[1]
        for param in [keynodes.info.stype_bin_orient_norole_rel]:
            sc_utils.createPairPosPerm(session, core.Kernel.segment(), param, sumNode, sc.SC_CONST)
    sc_utils.createPair(session,core.Kernel.segment(), _result, sumNode, sc.SC_CONST)

    relarc = sc_utils.createPair(session,core.Kernel.segment(), sumNode, relation, sc.SC_CONST)
    sc_utils.createPair(session,core.Kernel.segment(), _result, relarc, sc.SC_CONST)
    return res


def genMultiplyRelation(session, segment, operation, _result):
    el1 = math2sc.variables_sc[operation[0]]
    el2 = math2sc.variables_sc[operation[1]]

    #gen set of sum components
    setNode = session.create_el_idtf(core.Kernel.segment(), sc.SC_NODE, "")[1]
    sc_utils.createPair(session,core.Kernel.segment(), _result, setNode, sc.SC_CONST)

    arc1 = sc_utils.createPair(session,core.Kernel.segment(), setNode, el1, sc.SC_CONST)
    arc2 = sc_utils.createPair(session,core.Kernel.segment(), setNode, el2, sc.SC_CONST)
    sc_utils.createPair(session,core.Kernel.segment(), _result, arc1, sc.SC_CONST)
    sc_utils.createPair(session,core.Kernel.segment(), _result, arc2, sc.SC_CONST)

    #gen sum relations
    res = session.create_el_idtf(core.Kernel.segment(), sc.SC_NODE, "")[1]  #add result node
    sc_utils.createPair(session,core.Kernel.segment(), _result, res, sc.SC_CONST)

    relation = sc_utils.createPair(session,core.Kernel.segment(), setNode, res, sc.SC_CONST)
    sc_utils.createPair(session,core.Kernel.segment(), _result, relation, sc.SC_CONST)

    idtf = "произведение*"
    idtf = sc_utils.utf8ToCp1251(str(idtf))
    sumNode = sc_utils.getElementByIdtf(idtf, segment)
    if sumNode == None:
        sumNode = session.create_el_idtf(core.Kernel.segment(), sc.SC_NODE, idtf)[1]
        for param in [keynodes.info.stype_bin_orient_norole_rel]:
            sc_utils.createPairPosPerm(session, core.Kernel.segment(), param, sumNode, sc.SC_CONST)
    sc_utils.createPair(session,core.Kernel.segment(), _result, sumNode, sc.SC_CONST)

    relarc = sc_utils.createPair(session,core.Kernel.segment(), sumNode, relation, sc.SC_CONST)
    sc_utils.createPair(session,core.Kernel.segment(), _result, relarc, sc.SC_CONST)
    return res

def genDivideRelation(session, segment, operation, _result):
    el1 = math2sc.variables_sc[operation[0]] #divident
    el2 = math2sc.variables_sc[operation[1]] #divisor
    res = session.create_el_idtf(core.Kernel.segment(), sc.SC_NODE, "")[1]  #difference result node
    sc_utils.createPair(session,core.Kernel.segment(), _result, res, sc.SC_CONST)

    setNode = session.create_el_idtf(core.Kernel.segment(), sc.SC_NODE, "")[1]
    sc_utils.createPair(session,core.Kernel.segment(), _result, setNode, sc.SC_CONST)

    #gen input sum parameters
    arc1 = sc_utils.createPair(session,core.Kernel.segment(), setNode, res, sc.SC_CONST)
    arc2 = sc_utils.createPair(session,core.Kernel.segment(), setNode, el2, sc.SC_CONST)
    sc_utils.createPair(session,core.Kernel.segment(), _result, arc1, sc.SC_CONST)
    sc_utils.createPair(session,core.Kernel.segment(), _result, arc2, sc.SC_CONST)

    relation = sc_utils.createPair(session,core.Kernel.segment(), setNode, el1, sc.SC_CONST)
    sc_utils.createPair(session,core.Kernel.segment(), _result, relation, sc.SC_CONST)

    idtf = "произведение*"
    idtf = sc_utils.utf8ToCp1251(str(idtf))
    sumNode = sc_utils.getElementByIdtf(idtf, segment)
    if sumNode == None:
        sumNode = session.create_el_idtf(core.Kernel.segment(), sc.SC_NODE, idtf)[1]
        for param in [keynodes.info.stype_bin_orient_norole_rel]:
            sc_utils.createPairPosPerm(session, core.Kernel.segment(), param, sumNode, sc.SC_CONST)
    sc_utils.createPair(session,core.Kernel.segment(), _result, sumNode, sc.SC_CONST)

    relarc = sc_utils.createPair(session,core.Kernel.segment(), sumNode, relation, sc.SC_CONST)
    sc_utils.createPair(session,core.Kernel.segment(), _result, relarc, sc.SC_CONST)
    return res