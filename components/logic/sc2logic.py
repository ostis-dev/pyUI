
from suit.core.objects import Translator
import sc_core.pm as sc
import suit.core.kernel as core
import suit.core.objects as objects
import sc_core.constants as sc_constants
   
    
class TranslatorSc2Logic(Translator):
   
    def __init__(self):
        Translator.__init__(self)
        
    def __del__(self):
        Translator.__del__(self)
        
    def translate_impl(self, _input, _output):

        errors = []
        
        #getting sheet object
        objs = objects.ScObject._sc2Objects(_output)
        assert len(objs) > 0
        sheet = objs[0]
        assert type(sheet) is objects.ObjectSheet

        #getting session
        kernel = core.Kernel.getSingleton()
        session = kernel.session()
        segment = kernel.segment()
        trans_objs = []

        it = session.create_iterator(session.sc_constraint_new(sc_constants.CONSTR_3_f_a_a,_input,sc.SC_A_CONST | sc.SC_POS,0), True)
        addrsList = []
        while not it.is_over():
            trans_objs.append(it.value(2))
            addrsList.append(str(it.value(2).this))
            it.next()

        for addrs in addrsList:
            texNode = session.create_el(segment, sc.SC_N_CONST)


            texStr = Translate(addrs)
            session.set_content_str(texNode, texStr)
            session.gen3_f_a_f(segment, _output, texNode, sc.SC_A_CONST | sc.SC_POS)
            
        return errors
       
def Translate(root):

    kernel = core.Kernel.getSingleton()
    session = kernel.session()
    it=session.create_iterator(session.sc_constraint_new(sc_constants.CONSTR_3_f_a_a,
        root,
        sc.SC_ARC,
        sc.SC_CONST|sc.SC_NODE), True)
    sheaf=session.find_keynode_full_uri(u"/info/stype_sheaf")
    while not it.is_over():
        it_2=session.create_iterator(session.sc_constraint_new(sc_constants.CONSTR_3_f_a_f,
            sheaf,
            sc.SC_ARC,
            it.value(2)), True)
        if not it_2.is_over():
            node=it_2.value(2)
            break
        else:
            it.next()
    it=session.create_iterator(session.sc_constraint_new(sc_constants.CONSTR_3_a_a_f,
        sc.SC_CONST|sc.SC_NODE,
        sc.SC_ARC,
        node), True)
    while not it.is_over():
        it_2=session.create_iterator(session.sc_constraint_new(sc_constants.CONSTR_3_f_a_f,
            sheaf,
            sc.SC_ARC,
            it.value(0)), True)
        if not it_2.is_over():
            node=it_2.value(2)
            it=session.create_iterator(session.sc_constraint_new(sc_constants.CONSTR_3_a_a_f,
                sc.SC_CONST|sc.SC_NODE,
                sc.SC_ARC,
                node), True)
            break
        else:
            it.next()
    import logic_converter as convertor
    session = core.Kernel.session()
        
    return convertor.getFormula(session, node, None)