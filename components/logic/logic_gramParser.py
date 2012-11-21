# $ANTLR 3.1.3 Mar 18, 2009 10:09:25 logic_gram.g 2012-11-10 17:59:36

import sys
from antlr3 import *
from antlr3.compat import set, frozenset
         
import suit.core.kernel as core
import sc_core.pm as sc
import suit.core.sc_utils as sc_utils
import logic_keynodes



# for convenience in actions
HIDDEN = BaseRecognizer.HIDDEN

# token types
WS=5
T__12=12
T__11=11
T__13=13
T__10=10
ID=4
EOF=-1
T__9=9
T__8=8
T__7=7
T__6=6

# token names
tokenNames = [
    "<invalid>", "<EOR>", "<DOWN>", "<UP>", 
    "ID", "WS", "'^'", "'&'", "'->'", "'<-'", "'<->'", "'('", "')'", "'!'"
]




class logic_gramParser(Parser):
    grammarFileName = "logic_gram.g"
    antlr_version = version_str_to_tuple("3.1.3 Mar 18, 2009 10:09:25")
    antlr_version_str = "3.1.3 Mar 18, 2009 10:09:25"
    tokenNames = tokenNames

    def __init__(self, input, state=None, *args, **kwargs):
        if state is None:
            state = RecognizerSharedState()

        super(logic_gramParser, self).__init__(input, state, *args, **kwargs)



              
        self.nodeList = []
        kernel=core.Kernel.getSingleton()
        self.session = kernel.session()
        self.segment = kernel.segment()




                


        



    # $ANTLR start "formula"
    # logic_gram.g:18:1: formula : expression ;
    def formula(self, ):

        try:
            try:
                # logic_gram.g:19:2: ( expression )
                # logic_gram.g:19:3: expression
                pass 
                self._state.following.append(self.FOLLOW_expression_in_formula32)
                self.expression()

                self._state.following.pop()




            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
        finally:

            pass
        return 

    # $ANTLR end "formula"


    # $ANTLR start "expression"
    # logic_gram.g:22:1: expression returns [node] : a= atom ( '^' | '&' | ( '->' | '<-' ) | '<->' ) b= atom ;
    def expression(self, ):

        node = None

        a = None

        b = None


        try:
            try:
                # logic_gram.g:23:2: (a= atom ( '^' | '&' | ( '->' | '<-' ) | '<->' ) b= atom )
                # logic_gram.g:23:3: a= atom ( '^' | '&' | ( '->' | '<-' ) | '<->' ) b= atom
                pass 
                #action start
                   
                revers=None
                relation=None
                	
                #action end
                self._state.following.append(self.FOLLOW_atom_in_expression49)
                a = self.atom()

                self._state.following.pop()
                # logic_gram.g:26:10: ( '^' | '&' | ( '->' | '<-' ) | '<->' )
                alt2 = 4
                LA2 = self.input.LA(1)
                if LA2 == 6:
                    alt2 = 1
                elif LA2 == 7:
                    alt2 = 2
                elif LA2 == 8 or LA2 == 9:
                    alt2 = 3
                elif LA2 == 10:
                    alt2 = 4
                else:
                    nvae = NoViableAltException("", 2, 0, self.input)

                    raise nvae

                if alt2 == 1:
                    # logic_gram.g:26:11: '^'
                    pass 
                    self.match(self.input, 6, self.FOLLOW_6_in_expression52)
                    #action start
                    relation=logic_keynodes.Relation.nrel_disjunction
                    #action end


                elif alt2 == 2:
                    # logic_gram.g:27:3: '&'
                    pass 
                    self.match(self.input, 7, self.FOLLOW_7_in_expression57)
                    #action start
                    relation=logic_keynodes.Relation.nrel_conjunction
                    #action end


                elif alt2 == 3:
                    # logic_gram.g:28:3: ( '->' | '<-' )
                    pass 
                    # logic_gram.g:28:3: ( '->' | '<-' )
                    alt1 = 2
                    LA1_0 = self.input.LA(1)

                    if (LA1_0 == 8) :
                        alt1 = 1
                    elif (LA1_0 == 9) :
                        alt1 = 2
                    else:
                        nvae = NoViableAltException("", 1, 0, self.input)

                        raise nvae

                    if alt1 == 1:
                        # logic_gram.g:28:4: '->'
                        pass 
                        self.match(self.input, 8, self.FOLLOW_8_in_expression64)


                    elif alt1 == 2:
                        # logic_gram.g:28:9: '<-'
                        pass 
                        self.match(self.input, 9, self.FOLLOW_9_in_expression66)
                        #action start
                        revers=True
                        #action end



                    #action start
                    relation=logic_keynodes.Relation.nrel_implication
                    #action end


                elif alt2 == 4:
                    # logic_gram.g:29:3: '<->'
                    pass 
                    self.match(self.input, 10, self.FOLLOW_10_in_expression75)
                    #action start
                    relation=logic_keynodes.Relation.nrel_equivalence
                    #action end



                self._state.following.append(self.FOLLOW_atom_in_expression84)
                b = self.atom()

                self._state.following.pop()
                #action start
                  
                if relation==logic_keynodes.Relation.nrel_implication:
                	if revers:
                		a,b=b,a
                	node=sc_utils.createPairBinaryOrient(self.session, self.segment, a ,b, sc.SC_CONST)
                else:
                	node=sc_utils.createPairBinaryNoOrient(self.session, self.segment, a ,b, sc.SC_CONST)
                self.nodeList.append(node)
                self.nodeList.append(sc_utils.createPairPosPerm(self.session, self.segment,relation, node, sc.SC_CONST))
                	
                #action end




            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
        finally:

            pass
        return node

    # $ANTLR end "expression"


    # $ANTLR start "brekets"
    # logic_gram.g:43:1: brekets returns [node] : '(' expression ')' ;
    def brekets(self, ):

        node = None

        expression1 = None


        try:
            try:
                # logic_gram.g:44:2: ( '(' expression ')' )
                # logic_gram.g:44:3: '(' expression ')'
                pass 
                self.match(self.input, 11, self.FOLLOW_11_in_brekets102)
                self._state.following.append(self.FOLLOW_expression_in_brekets104)
                expression1 = self.expression()

                self._state.following.pop()
                #action start
                node = expression1
                #action end
                self.match(self.input, 12, self.FOLLOW_12_in_brekets108)




            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
        finally:

            pass
        return node

    # $ANTLR end "brekets"


    # $ANTLR start "negation"
    # logic_gram.g:46:1: negation returns [node] : '!' atom ;
    def negation(self, ):

        node = None

        atom2 = None


        try:
            try:
                # logic_gram.g:47:2: ( '!' atom )
                # logic_gram.g:47:3: '!' atom
                pass 
                self.match(self.input, 13, self.FOLLOW_13_in_negation121)
                self._state.following.append(self.FOLLOW_atom_in_negation123)
                atom2 = self.atom()

                self._state.following.pop()
                #action start
                            
                node= self.session.create_el(self.segment, sc.SC_CONST)
                atomNode=atom2
                self.nodeList.append(sc_utils.createPairPosPerm(self.session, self.segment, logic_keynodes.Relation.nrel_negation, node, sc.SC_CONST))
                self.nodeList.append(sc_utils.createPairPosPerm(self.session, self.segment, node, atomNode, sc.SC_CONST))
                self.nodeList.append(node)
                	
                #action end




            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
        finally:

            pass
        return node

    # $ANTLR end "negation"


    # $ANTLR start "atom"
    # logic_gram.g:55:1: atom returns [node] : ( | brekets | ID | negation );
    def atom(self, ):

        node = None

        ID4 = None
        brekets3 = None

        negation5 = None


        try:
            try:
                # logic_gram.g:55:20: ( | brekets | ID | negation )
                alt3 = 4
                LA3 = self.input.LA(1)
                if LA3 == EOF or LA3 == 6 or LA3 == 7 or LA3 == 8 or LA3 == 9 or LA3 == 10 or LA3 == 12:
                    alt3 = 1
                elif LA3 == 11:
                    alt3 = 2
                elif LA3 == ID:
                    alt3 = 3
                elif LA3 == 13:
                    alt3 = 4
                else:
                    nvae = NoViableAltException("", 3, 0, self.input)

                    raise nvae

                if alt3 == 1:
                    # logic_gram.g:56:2: 
                    pass 

                elif alt3 == 2:
                    # logic_gram.g:56:4: brekets
                    pass 
                    self._state.following.append(self.FOLLOW_brekets_in_atom140)
                    brekets3 = self.brekets()

                    self._state.following.pop()
                    #action start
                    node = brekets3
                    #action end


                elif alt3 == 3:
                    # logic_gram.g:57:4: ID
                    pass 
                    ID4=self.match(self.input, ID, self.FOLLOW_ID_in_atom147)
                    #action start
                           
                    node = self.session.create_el_idtf(self.segment,sc.SC_CONST,ID4.text)[1]
                    self.nodeList.append(node)
                    #action end


                elif alt3 == 4:
                    # logic_gram.g:60:4: negation
                    pass 
                    self._state.following.append(self.FOLLOW_negation_in_atom154)
                    negation5 = self.negation()

                    self._state.following.pop()
                    #action start
                    node = negation5
                    #action end



            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
        finally:

            pass
        return node

    # $ANTLR end "atom"


    # Delegated rules


 

    FOLLOW_expression_in_formula32 = frozenset([1])
    FOLLOW_atom_in_expression49 = frozenset([6, 7, 8, 9, 10])
    FOLLOW_6_in_expression52 = frozenset([4, 11, 13])
    FOLLOW_7_in_expression57 = frozenset([4, 11, 13])
    FOLLOW_8_in_expression64 = frozenset([4, 11, 13])
    FOLLOW_9_in_expression66 = frozenset([4, 11, 13])
    FOLLOW_10_in_expression75 = frozenset([4, 11, 13])
    FOLLOW_atom_in_expression84 = frozenset([1])
    FOLLOW_11_in_brekets102 = frozenset([4, 6, 7, 8, 9, 10, 11, 13])
    FOLLOW_expression_in_brekets104 = frozenset([12])
    FOLLOW_12_in_brekets108 = frozenset([1])
    FOLLOW_13_in_negation121 = frozenset([4, 11, 13])
    FOLLOW_atom_in_negation123 = frozenset([1])
    FOLLOW_brekets_in_atom140 = frozenset([1])
    FOLLOW_ID_in_atom147 = frozenset([1])
    FOLLOW_negation_in_atom154 = frozenset([1])



def main(argv, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr):
    from antlr3.main import ParserMain
    main = ParserMain("logic_gramLexer", logic_gramParser)
    main.stdin = stdin
    main.stdout = stdout
    main.stderr = stderr
    main.execute(argv)


if __name__ == '__main__':
    main(sys.argv)
