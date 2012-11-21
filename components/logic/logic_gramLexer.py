# $ANTLR 3.1.3 Mar 18, 2009 10:09:25 logic_gram.g 2012-11-10 17:59:37

import sys
from antlr3 import *
from antlr3.compat import set, frozenset


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


class logic_gramLexer(Lexer):

    grammarFileName = "logic_gram.g"
    antlr_version = version_str_to_tuple("3.1.3 Mar 18, 2009 10:09:25")
    antlr_version_str = "3.1.3 Mar 18, 2009 10:09:25"

    def __init__(self, input=None, state=None):
        if state is None:
            state = RecognizerSharedState()
        super(logic_gramLexer, self).__init__(input, state)


        self.dfa2 = self.DFA2(
            self, 2,
            eot = self.DFA2_eot,
            eof = self.DFA2_eof,
            min = self.DFA2_min,
            max = self.DFA2_max,
            accept = self.DFA2_accept,
            special = self.DFA2_special,
            transition = self.DFA2_transition
            )






    # $ANTLR start "T__6"
    def mT__6(self, ):

        try:
            _type = T__6
            _channel = DEFAULT_CHANNEL

            # logic_gram.g:7:6: ( '^' )
            # logic_gram.g:7:8: '^'
            pass 
            self.match(94)



            self._state.type = _type
            self._state.channel = _channel

        finally:

            pass

    # $ANTLR end "T__6"



    # $ANTLR start "T__7"
    def mT__7(self, ):

        try:
            _type = T__7
            _channel = DEFAULT_CHANNEL

            # logic_gram.g:8:6: ( '&' )
            # logic_gram.g:8:8: '&'
            pass 
            self.match(38)



            self._state.type = _type
            self._state.channel = _channel

        finally:

            pass

    # $ANTLR end "T__7"



    # $ANTLR start "T__8"
    def mT__8(self, ):

        try:
            _type = T__8
            _channel = DEFAULT_CHANNEL

            # logic_gram.g:9:6: ( '->' )
            # logic_gram.g:9:8: '->'
            pass 
            self.match("->")



            self._state.type = _type
            self._state.channel = _channel

        finally:

            pass

    # $ANTLR end "T__8"



    # $ANTLR start "T__9"
    def mT__9(self, ):

        try:
            _type = T__9
            _channel = DEFAULT_CHANNEL

            # logic_gram.g:10:6: ( '<-' )
            # logic_gram.g:10:8: '<-'
            pass 
            self.match("<-")



            self._state.type = _type
            self._state.channel = _channel

        finally:

            pass

    # $ANTLR end "T__9"



    # $ANTLR start "T__10"
    def mT__10(self, ):

        try:
            _type = T__10
            _channel = DEFAULT_CHANNEL

            # logic_gram.g:11:7: ( '<->' )
            # logic_gram.g:11:9: '<->'
            pass 
            self.match("<->")



            self._state.type = _type
            self._state.channel = _channel

        finally:

            pass

    # $ANTLR end "T__10"



    # $ANTLR start "T__11"
    def mT__11(self, ):

        try:
            _type = T__11
            _channel = DEFAULT_CHANNEL

            # logic_gram.g:12:7: ( '(' )
            # logic_gram.g:12:9: '('
            pass 
            self.match(40)



            self._state.type = _type
            self._state.channel = _channel

        finally:

            pass

    # $ANTLR end "T__11"



    # $ANTLR start "T__12"
    def mT__12(self, ):

        try:
            _type = T__12
            _channel = DEFAULT_CHANNEL

            # logic_gram.g:13:7: ( ')' )
            # logic_gram.g:13:9: ')'
            pass 
            self.match(41)



            self._state.type = _type
            self._state.channel = _channel

        finally:

            pass

    # $ANTLR end "T__12"



    # $ANTLR start "T__13"
    def mT__13(self, ):

        try:
            _type = T__13
            _channel = DEFAULT_CHANNEL

            # logic_gram.g:14:7: ( '!' )
            # logic_gram.g:14:9: '!'
            pass 
            self.match(33)



            self._state.type = _type
            self._state.channel = _channel

        finally:

            pass

    # $ANTLR end "T__13"



    # $ANTLR start "ID"
    def mID(self, ):

        try:
            _type = ID
            _channel = DEFAULT_CHANNEL

            # logic_gram.g:63:5: ( ( 'a' .. 'z' | 'A' .. 'Z' | '_' ) ( 'a' .. 'z' | 'A' .. 'Z' | '0' .. '9' | '_' )* )
            # logic_gram.g:63:7: ( 'a' .. 'z' | 'A' .. 'Z' | '_' ) ( 'a' .. 'z' | 'A' .. 'Z' | '0' .. '9' | '_' )*
            pass 
            if (65 <= self.input.LA(1) <= 90) or self.input.LA(1) == 95 or (97 <= self.input.LA(1) <= 122):
                self.input.consume()
            else:
                mse = MismatchedSetException(None, self.input)
                self.recover(mse)
                raise mse

            # logic_gram.g:63:31: ( 'a' .. 'z' | 'A' .. 'Z' | '0' .. '9' | '_' )*
            while True: #loop1
                alt1 = 2
                LA1_0 = self.input.LA(1)

                if ((48 <= LA1_0 <= 57) or (65 <= LA1_0 <= 90) or LA1_0 == 95 or (97 <= LA1_0 <= 122)) :
                    alt1 = 1


                if alt1 == 1:
                    # logic_gram.g:
                    pass 
                    if (48 <= self.input.LA(1) <= 57) or (65 <= self.input.LA(1) <= 90) or self.input.LA(1) == 95 or (97 <= self.input.LA(1) <= 122):
                        self.input.consume()
                    else:
                        mse = MismatchedSetException(None, self.input)
                        self.recover(mse)
                        raise mse



                else:
                    break #loop1



            self._state.type = _type
            self._state.channel = _channel

        finally:

            pass

    # $ANTLR end "ID"



    # $ANTLR start "WS"
    def mWS(self, ):

        try:
            _type = WS
            _channel = DEFAULT_CHANNEL

            # logic_gram.g:66:5: ( ( ' ' | '\\t' | '\\r' | '\\n' ) )
            # logic_gram.g:66:9: ( ' ' | '\\t' | '\\r' | '\\n' )
            pass 
            if (9 <= self.input.LA(1) <= 10) or self.input.LA(1) == 13 or self.input.LA(1) == 32:
                self.input.consume()
            else:
                mse = MismatchedSetException(None, self.input)
                self.recover(mse)
                raise mse

            #action start
            _channel=HIDDEN;
            #action end



            self._state.type = _type
            self._state.channel = _channel

        finally:

            pass

    # $ANTLR end "WS"



    def mTokens(self):
        # logic_gram.g:1:8: ( T__6 | T__7 | T__8 | T__9 | T__10 | T__11 | T__12 | T__13 | ID | WS )
        alt2 = 10
        alt2 = self.dfa2.predict(self.input)
        if alt2 == 1:
            # logic_gram.g:1:10: T__6
            pass 
            self.mT__6()


        elif alt2 == 2:
            # logic_gram.g:1:15: T__7
            pass 
            self.mT__7()


        elif alt2 == 3:
            # logic_gram.g:1:20: T__8
            pass 
            self.mT__8()


        elif alt2 == 4:
            # logic_gram.g:1:25: T__9
            pass 
            self.mT__9()


        elif alt2 == 5:
            # logic_gram.g:1:30: T__10
            pass 
            self.mT__10()


        elif alt2 == 6:
            # logic_gram.g:1:36: T__11
            pass 
            self.mT__11()


        elif alt2 == 7:
            # logic_gram.g:1:42: T__12
            pass 
            self.mT__12()


        elif alt2 == 8:
            # logic_gram.g:1:48: T__13
            pass 
            self.mT__13()


        elif alt2 == 9:
            # logic_gram.g:1:54: ID
            pass 
            self.mID()


        elif alt2 == 10:
            # logic_gram.g:1:57: WS
            pass 
            self.mWS()







    # lookup tables for DFA #2

    DFA2_eot = DFA.unpack(
        u"\12\uffff\1\14\2\uffff"
        )

    DFA2_eof = DFA.unpack(
        u"\15\uffff"
        )

    DFA2_min = DFA.unpack(
        u"\1\11\3\uffff\1\55\5\uffff\1\76\2\uffff"
        )

    DFA2_max = DFA.unpack(
        u"\1\172\3\uffff\1\55\5\uffff\1\76\2\uffff"
        )

    DFA2_accept = DFA.unpack(
        u"\1\uffff\1\1\1\2\1\3\1\uffff\1\6\1\7\1\10\1\11\1\12\1\uffff\1"
        u"\5\1\4"
        )

    DFA2_special = DFA.unpack(
        u"\15\uffff"
        )

            
    DFA2_transition = [
        DFA.unpack(u"\2\11\2\uffff\1\11\22\uffff\1\11\1\7\4\uffff\1\2\1"
        u"\uffff\1\5\1\6\3\uffff\1\3\16\uffff\1\4\4\uffff\32\10\3\uffff\1"
        u"\1\1\10\1\uffff\32\10"),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u"\1\12"),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u"\1\13"),
        DFA.unpack(u""),
        DFA.unpack(u"")
    ]

    # class definition for DFA #2

    class DFA2(DFA):
        pass


 



def main(argv, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr):
    from antlr3.main import LexerMain
    main = LexerMain(logic_gramLexer)
    main.stdin = stdin
    main.stdout = stdout
    main.stderr = stderr
    main.execute(argv)


if __name__ == '__main__':
    main(sys.argv)
