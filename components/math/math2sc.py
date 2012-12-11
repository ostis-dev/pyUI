# -*- coding: utf-8 -*-
import suit.core.kernel as core
from xml.dom.minidom import *
import suit.core.sc_utils as sc_utils
import sc_core.pm as sc
import sc_core.constants as sc_constants
import binary_expression_generator as b_generator
import function_generator as f_generator
import suit.core.keynodes as keynodes
import suit.core.objects as objects

variables = []
operations = []
last = []
lastop = ""
binoperands = []
variables_sc = {}
rowcount = 0
isroot = False
isfrac = False

translation_errors = []


operation_priority = {"+":1, "-":1, "*":2, "/":2, "^":3, "=":0, "frac":2}

#result string for inverse poland notation
parse_result = []
#stack for inverse poland notation
stack = []

#mapping from operations to functions that generate appropriate sc-constructions
binary_expression_gen = {"+":b_generator.genSumRelation,
                         "-":b_generator.genDifferenceRelation,
                         "*":b_generator.genMultiplyRelation,
                         "/":b_generator.genDivideRelation,
                         "^":b_generator.genPowerRelation,
                         "=":b_generator.genEqualityRelation,
                         "frac": b_generator.gen_fracture_relation}

#the list of supported functions and the number of arguments they need
functions = {"sin": 1,
            "cos": 1,
            "tg": 1,
            "ctg": 1}

def close_power(_xmlnode, tag, session, segment):
    """
    Postprocess msup tag
    @param _xmlnode:
    @param tag:
    @param session:
    @param segment:
    @return:
    """
    while stack[-1]!="(":
        parse_result.append(stack.pop(-1))
        if len(stack) == 0:
            translation_errors.append("Incorrect input string: can't find close bracket")
            return
    stack.pop(-1)
    parse_result.append("^")
    return

def close_sqrt(_xmlnode, tag, session, segment):
    """
    Postrprocess msqrt tag
    """

    while stack[-1]!="(":
        parse_result.append(stack.pop(-1))
        if len(stack) == 0:
            translation_errors.append("Incorrect input string: can't find close bracket")
            return
    stack.pop(-1)
    variables.append(["0.5",[]])

    findElement = sc_utils.getElementByIdtf("Num0.5", segment)
    if findElement == None:
        node = session.create_el_idtf(core.Kernel.segment(), sc.SC_NODE, "Num0.5")[1]
        sc_utils.createPair(session,core.Kernel.segment(), el, node, sc.SC_CONST)
        variables_sc["0.5"] = node
    else:
        sc_utils.createPair(session,core.Kernel.segment(), el, findElement, sc.SC_CONST)
        variables_sc["0.5"] = findElement

    parse_result.append("0.5")
    parse_result.append("^")
    return

def close_bracket(_xmlnode, tag, session, segment):
    """
    Postprocess mfenced tag

    """
    while stack[-1]!="(":
        parse_result.append(stack.pop(-1))
        if len(stack) == 0:
            translation_errors.append("Incorrect input string: can't find close bracket")
            return
    stack.pop(-1)
    if stack[-1] in functions:
        parse_result.append(stack.pop(-1))
    return


def generate_exppressions(_xmlnode, tag, session, segment) :
    """
    Process math tag. Generate relations between variables and numbers
    """
    global  parse_result
    while len(stack)>0:
        parse_result.append(stack.pop(-1))

    #generate unary expressions
    for var in variables:
        varname = var[0]
        while len(var[1]) > 0:
            op = var[1].pop(0)
            expr = op+var[0]
            key = var[0]
            var[0] = expr

            for operation in operations:
                for arg in operation[1]:
                    if arg==key:
                        operation[1][operation[1].index(key)] = expr

            for elem in parse_result:
                if elem==key:
                    parse_result[parse_result.index(key)] = expr

            if op=="-":
                #generate unary minus relation
                #find unary minus relation node, if not find create
                idtf = "обратное число*"
                idtf = sc_utils.utf8ToCp1251(str(idtf))
                unMinusNode = sc_utils.getElementByIdtf(idtf, segment)
                if unMinusNode == None:
                    unMinusNode = session.create_el_idtf(core.Kernel.segment(), sc.SC_NODE, idtf)[1]
                    for param in [keynodes.info.stype_bin_orient_norole_rel]:
                        sc_utils.createPairPosPerm(session, core.Kernel.segment(), param, unMinusNode, sc.SC_CONST)
                sc_utils.createPair(session,core.Kernel.segment(), el, unMinusNode, sc.SC_CONST)
                #gen node for result
                varSC = variables_sc[key]
                res = session.create_el_idtf(core.Kernel.segment(), sc.SC_NODE, "")[1]  #node for result
                pair = sc_utils.createPair(session,core.Kernel.segment(), varSC, res, sc.SC_CONST) #arc between processed node and result
                relBelong = sc_utils.createPair(session,core.Kernel.segment(), unMinusNode, pair, sc.SC_CONST)
                sc_utils.createPair(session,core.Kernel.segment(), el, res, sc.SC_CONST)
                sc_utils.createPair(session,core.Kernel.segment(), el, pair, sc.SC_CONST)
                sc_utils.createPair(session,core.Kernel.segment(), el, relBelong, sc.SC_CONST)

                variables_sc[expr] = res

    #generate operations
    expr = ""
    for elem in parse_result:
        if (not elem in operation_priority.keys() and not elem in functions.keys()):
            stack.append(elem)
        else:
            op = elem
            if (op not in functions.keys()):
                operand1 = stack.pop(-1)
                operand2 = stack.pop(-1)
                expr = operand2+op+operand1
                stack.append(expr)

                if op in binary_expression_gen.keys():
                    gen_operation = binary_expression_gen[op]
                    res = gen_operation(session, segment, [operand2,operand1], el)
                    variables_sc[expr] = res
                else:
                    translation_errors.append("Unsupported operation")
            else:
                operands = []
                expr = op+"("
                for i in range(0, functions[op], 1):
                    operands.append(stack.pop(-1))
                    expr += operands[-1]
                    expr += ","
                expr+=")"
                stack.append(expr)

                res = f_generator.gen_function(op, operands, session, segment, el)
                variables_sc[expr] = res

    return

def generate_variable(_xmlnode, tag, session, segment):
    """
    Process mi and mn tags. Generate variable or number and add it to result string
    @return:
    """
    #here should be generation of sc-node that represents variable
    global last, binoperands,lastop,el

    if session==None or segment==None:
        return

    nodename = _xmlnode.childNodes[0].nodeValue
    if not nodename in functions.keys():
        parse_result.append(nodename)

    if tag!="mi" and tag!="mn":
        translation_errors.append("Unknown tag")
        return
    #start generation
    if tag=="mi":
        if not nodename in functions.keys():
            findElement = sc_utils.getElementByIdtf(nodename, segment)
            if findElement == None:
                node = session.create_el_idtf(core.Kernel.segment(), sc.SC_NODE, nodename)[1]
                sc_utils.createPair(session,core.Kernel.segment(), el, node, sc.SC_CONST)
                variables_sc[nodename] = node
            else:
                sc_utils.createPair(session,core.Kernel.segment(), el, findElement, sc.SC_CONST)
                variables_sc[nodename] = findElement
        else:
            stack.append(nodename)
    if tag=="mn":
        findElement = sc_utils.getElementByIdtf("Num"+nodename, segment)
        if findElement == None:
            node = session.create_el_idtf(core.Kernel.segment(), sc.SC_NODE, "Num"+nodename)[1]
            #sc_utils.setContentInt(session, core.Kernel.segment(), node, int(nodename))
            sc_utils.createPair(session,core.Kernel.segment(), el, node, sc.SC_CONST)
            variables_sc[nodename] = node
        else:
            sc_utils.createPair(session,core.Kernel.segment(), el, findElement, sc.SC_CONST)
            variables_sc[nodename] = findElement

    variables.append([nodename, last])

    if (len(binoperands)==1):
        binoperands.append(variables[-1][0])
        operations.append((lastop,binoperands))
        binoperands = []
    last = []
    lastop = ""
    return

def generate_operator(_xmlnode,tag, session, segment):
    """
    Process op tag. Adds operator to stack or result string
    @param _xmlnode:
    @param tag:
    @param session:
    @param segment:
    @return:
    """
    global last, lastop
    op = _xmlnode.childNodes[0].nodeValue

    if (len(variables) != 0 and lastop==""):
        binoperands.append(variables[-1][0])
        lastop = op
        last = []
        if len(stack)>0:
            if (stack[-1] in operation_priority.keys()):
                while operation_priority[stack[-1]] > operation_priority[op] :
                    parse_result.append(stack.pop(-1))
                    if len(stack) == 0:
                        break
        stack.append(op)
    else :
        last.append(op)
    return

def close_row(_xmlnode,tag, session, segment):
    """
    Postprocess mrow tag
    @param _xmlnode:
    @param tag:
    @param session:
    @param segment:
    @return:
    """
    global rowcount, isroot, isfrac
    rowcount -= 1
    if rowcount == 0 and isroot==True:
        while stack[-1] != "(":
            parse_result.append(stack.pop(-1))
            if len(stack) == 0:
                translation_errors.append("Incorrect input string: can't find close bracket")
                break
            if not isfrac:
                parse_result.append("1")

        findElement = sc_utils.getElementByIdtf("Num1", segment)
        if findElement == None:
            node = session.create_el_idtf(core.Kernel.segment(), sc.SC_NODE, "Num1")[1]
            variables_sc["1"] = node
        else:
            variables_sc["1"] = findElement

    isroot = False
    return

def close_root(_xmlnode,tag, session, segment):
    """
    Postprocess mroot tag
    @param _xmlnode:
    @param tag:
    @param session:
    @param segment:
    @return:
    """

    while stack[-1]!="(":
        parse_result.append(stack.pop(-1))
        if len(stack) == 0:
            translation_errors.append("Incorrect input string: can't find close bracket")
            break
    stack.pop(-1)
    parse_result.append("/")
    parse_result.append("^")
    return

def close_frac(_xmlnode,tag, session, segment):
    """
    Postprocess mfrac tag
    """
    while stack[-1]!="(":
        parse_result.append(stack.pop(-1))
        if len(stack) == 0:
            translation_errors.append("Incorrect input string: can't find close bracket")
            break
    stack.pop(-1)
    parse_result.append("frac")
    isfrac = False
    return



# the list of functions that are called to postprocess certain xml node
translate_rules = {"mi" : generate_variable,
                   "mn" : generate_variable,
                   "mo" : generate_operator,
                   "math" : generate_exppressions,
                   "mfenced": close_bracket,
                   "msup": close_power,
                   "msqrt": close_sqrt,
                   "mrow":close_row,
                   "mroot": close_root,
                   "mfrac": close_frac}


def translate_node(_node,session, segment):
    """
    Process the node (do preprocess, process child nodes, do postprocess)
    @param _node: xml node that is processed in a moment
    @return:
    """
    global rowcount, isroot, isfrac

    #preprocess
    if _node.nodeName == "mfenced" or _node.nodeName=="msup" or _node.nodeName == "msqrt" :
        stack.append("(")
    if _node.nodeName == "mfrac":
        isfrac = True
    if _node.nodeName == "mroot" or _node.nodeName == "mfrac":
        stack.append("(")
        isroot = True
    if _node.nodeName == "mrow":
        rowcount += 1

    #process children
    for child in _node.childNodes :
        translate_node(child,session,segment)

    #postprocess
    if (translate_rules.has_key(_node.nodeName)) :
        func = translate_rules[_node.nodeName]
        func(_node, _node.nodeName, session, segment)
    else:
        translation_errors.append("node"+_node.nodeName+"translation is not supported")

    return


def translate_xml(_inputXML, session, segment):
    """
    Parse input xml string and run functions that generate scConstructions
    @param _inputXML: string that contains MathML representation of mathemathic expression
    @return:
    """
    try:
        xml = parseString(_inputXML)
        document = xml.getElementsByTagName("math")
        if len(document) == 1:
            translate_node(document[0], session, segment)
        else:
            translation_errors.append("The input string is not correct MathML")
    except:
        translation_errors.append("The input string is not correct MathML")
    return



from suit.core.objects import Translator

class TranslatorMath2Sc(Translator):
    """Translator from MathML to SC-code.

    """

    def __init__(self):
        Translator.__init__(self)

    def __del__(self):
        Translator.__del__(self)

    def translate_impl(self, _input, _output):
        """Translator implementation
        """

        objs = objects.ScObject._sc2Objects(_input)

        assert len(objs) > 0
        sheet = objs[0]
        assert isinstance(sheet, objects.ObjectSheet)
        seg = sheet.getTmpSegment()

        global el
        el = _output
        segment = core.Kernel.segment()
        session = core.Kernel.session()

        _segs = [segment.get_full_uri()]
        search_segments     =   ["/ui/core",
                                 "/seb/belarus",
                                 "/seb/planimetry",
                                 "/seb/graph",
                                 "/seb/rus",
                                 "/etc/questions",
                                 "/etc/com_keynodes",
                                 "/seb/test",
                                 "/proc/agents/nsm/keynode"]
        _segs.extend(search_segments)

        #erase all elements that are connected to the result node
        iterator = session.create_iterator(session.sc_constraint_new(sc_constants.CONSTR_3_f_a_a,el, sc.SC_ARC|sc.SC_CONST, sc.SC_NODE),True)
        while not iterator.is_over():
            session.erase_el(iterator.value(1))
            session.erase_el(iterator.value(2))
            iterator.next()


        #translate
        for object in sheet.getChilds():
            parseText = object.getText()
            #start parser
            translate_xml(parseText, session, _segs)


        errors = translation_errors

        return errors





