import suit.core.kernel as core
import suit.core.sc_utils as sc_utils
import sc_core.pm as sc
import sc_core.constants as sc_constants
import math2sc
import suit.core.keynodes as keynodes


def gen_function(name, params, session, segment, _result):
    """

    @param name: function name
    @param params: list of function params
    @param _result: an output node of the translator
    @return:
    """


    #gen function node
    idtf = name+"*"
    idtf = sc_utils.utf8ToCp1251(str(idtf))
    funcNode = sc_utils.getElementByIdtf(idtf, segment)
    if funcNode == None:
        funcNode = session.create_el_idtf(core.Kernel.segment(), sc.SC_NODE, idtf)[1]
        for param in [keynodes.info.stype_bin_orient_norole_rel]:
            sc_utils.createPairPosPerm(session, core.Kernel.segment(), param, funcNode, sc.SC_CONST)
    sc_utils.createPair(session,core.Kernel.segment(), _result, funcNode, sc.SC_CONST)

    #gen args set
    argsSet = session.create_el_idtf(core.Kernel.segment(), sc.SC_NODE, "")[1]
    sc_utils.createPair(session,core.Kernel.segment(), _result, argsSet, sc.SC_CONST)

    for x in params:
        param = math2sc.variables_sc[x]
        arc = sc_utils.createPair(session, core.Kernel.segment(), argsSet, param, sc.SC_CONST)
        sc_utils.createPair(session,core.Kernel.segment(), _result, param, sc.SC_CONST)
        sc_utils.createPair(session,core.Kernel.segment(), _result, arc, sc.SC_CONST)
        pass

    #gen relation arc
    result = session.create_el_idtf(core.Kernel.segment(), sc.SC_NODE, "")[1]
    relation = sc_utils.createPair(session, core.Kernel.segment(), argsSet, result, sc.SC_CONST)
    sc_utils.createPair(session,core.Kernel.segment(), _result, relation, sc.SC_CONST)
    arc = sc_utils.createPair(session,core.Kernel.segment(), funcNode, relation, sc.SC_CONST)
    sc_utils.createPair(session,core.Kernel.segment(), _result, arc, sc.SC_CONST)

    return result
