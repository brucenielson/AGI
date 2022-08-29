from __future__ import annotations
from pyparsing import alphas, alphanums, Word, ZeroOrMore, Forward, OneOrMore, Group, exceptions, oneOf, Literal
from enum import Enum
from typing import Optional, List
from sentence import Sentence, LogicOperatorTypes

# Original Grammar for the Propositional Logic Parser (I've changed it a bit since)
#
# Line -> LogicalSentence EndOfLine
# LogicalSentence -> OrAndOperands => OrAndOperands | OrAndOperands <=> OrAndOperands
# OrAndOperands -> AndOperands OR AndOperands MoreOrOperators
# MoreOrOperators -> OR AndOperands | ""
# AndOperands -> Term AND Term MoreAndOperators
# MoreAndOperators -> AND Term | ""
# Term -> ~Term | (LogicalSentence) | Symbol
# Symbol -> <any string consisting of one letter and then any combination of letters and numbers>


class ParseError(Exception):
    def __init__(self, message):
        super().__init__(message)


class PLTokenType(Enum):
    SYMBOL = 1
    # noinspection SpellCheckingInspection
    LPAREN = 2
    # noinspection SpellCheckingInspection
    RPAREN = 3
    AND = 4
    OR = 5
    NOT = 6
    IMPLIES = 7
    # noinspection SpellCheckingInspection
    BICONDITIONAL = 8
    EOF = 9
    # noinspection SpellCheckingInspection
    ENDLINE = 10


class PropLogicParser:
    def __init__(self, input_str: str = None) -> None:
        self._tokens = None
        self._token_list: List = []
        self._current_line: List = []
        self._current_token: Optional[str] = None
        self._sentences: List[Sentence] = []

        not_sign = Literal('~')
        symbol = Word(alphas.upper(), alphanums.upper())
        logical_sentence = Forward()
        term = Forward()
        term << (not_sign + term | "(" + logical_sentence + ")" | symbol)
        or_and_operator = oneOf(["AND", "OR"])
        or_and_phrase = term + ZeroOrMore(or_and_operator + term)
        logical_sentence << (or_and_phrase + "=>" + or_and_phrase
                             | or_and_phrase + "<=>" + or_and_phrase
                             | or_and_phrase)
        line = logical_sentence + "\n" | logical_sentence
        self.lines = OneOrMore(Group(line))
        if input_str is not None:
            self.set_input(input_str)

    def set_input(self, input_str: str):
        input_str = input_str.upper()
        self._tokens = None
        try:
            self._tokens = self.lines.parse_string(input_str, parse_all=True)
        except exceptions.ParseException as err:
            raise ParseError("Incorrect syntax. Details: " + err.msg)
        self._token_list: List = self._tokens.asList()
        self._current_line: List = self._token_list[0]
        self._current_token: str = self._current_line[0]
        self._sentences: List[Sentence] = []

    @staticmethod
    def _str_to_token_type(str_token: str) -> PLTokenType:
        str_token = str_token.upper()
        if str_token == "(":
            return PLTokenType.LPAREN
        elif str_token == ")":
            return PLTokenType.RPAREN
        elif str_token == "AND":
            return PLTokenType.AND
        elif str_token == "OR":
            return PLTokenType.OR
        elif str_token == "~":
            return PLTokenType.NOT
        elif str_token == "=>":
            return PLTokenType.IMPLIES
        elif str_token == "<=>":
            return PLTokenType.BICONDITIONAL
        elif str_token == "EOF":
            return PLTokenType.EOF
        elif str_token == "END LINE":
            return PLTokenType.ENDLINE
        else:
            return PLTokenType.SYMBOL

    @staticmethod
    def _token_type_to_str(token_type: PLTokenType) -> str:
        if token_type == PLTokenType.LPAREN:
            return "("
        elif token_type == PLTokenType.RPAREN:
            return ")"
        elif token_type == PLTokenType.AND:
            return "AND"
        elif token_type == PLTokenType.OR:
            return "OR"
        elif token_type == PLTokenType.NOT:
            return "~"
        elif token_type == PLTokenType.IMPLIES:
            return "=>"
        elif token_type == PLTokenType.BICONDITIONAL:
            return "<=>"
        elif token_type == PLTokenType.EOF:
            return "EOF"
        elif token_type == PLTokenType.ENDLINE:
            return "END LINE"
        elif token_type == PLTokenType.SYMBOL:
            return "a symbol"

    @property
    def current_token_type(self) -> PLTokenType:
        return self._str_to_token_type(self.current_token)

    @property
    def current_token(self) -> str:
        if len(self._token_list) > 0 or len(self._current_line) > 0:
            self._current_line = self._token_list[0]
            if len(self._current_line) > 0:
                self._current_token = self._current_line[0]
            else:
                self._current_token = "END LINE"
        else:
            self._current_token = "EOF"

        return self._current_token

    @property
    def line_count(self) -> int:
        return len(self._token_list)

    def token_look_head(self, look_ahead: int) -> Optional[PLTokenType]:
        if len(self._token_list[0]) <= look_ahead:
            return None
        return self._str_to_token_type(self._current_line[look_ahead])

    def consume_token(self, check: PLTokenType = None) -> str:
        # Note: passing in a 'check' value will verify that the token you are about to consume was of the expected type
        # If not passed or set to None, then it is ignored and you just consume the next token
        if len(self._token_list) == 0:
            if check is not None and check != PLTokenType.EOF:
                raise ParseError("Expected EOF")
            return "EOF"
        self._current_line = self._token_list[0]
        if len(self._current_line) == 0 and len(self._token_list) == 0:
            if check is not None and check != PLTokenType.EOF:
                raise ParseError("Expected EOF")
            return "EOF"
        elif len(self._current_line) == 0:
            if check is not None and check != PLTokenType.ENDLINE:
                raise ParseError("Expected END LINE")
            self._token_list.pop(0)
            return "END LINE"
        else:
            current_token: str = self._current_line.pop(0)
            if check is not None and PropLogicParser._str_to_token_type(current_token) != check:
                raise ParseError("Expected " + PropLogicParser._token_type_to_str(check))
            return current_token

    @property
    def token_list(self) -> list:
        return self._token_list

    def get_original_token_list(self) -> list:
        return self._tokens.asList()

    def is_end_of_file(self):
        return PropLogicParser._str_to_token_type(self.current_token) == PLTokenType.EOF

    def parse_input(self) -> List[Sentence]:
        while not self.is_end_of_file():
            self._sentences.append(self.parse_line())
        return self._sentences

    def parse_line(self) -> Sentence:
        if self.is_end_of_file():
            raise ParseError("No Line Found.")
        return self.line()

    def line(self) -> Sentence:
        line: Sentence = self.logical_sentence()
        if self.current_token_type == PLTokenType.ENDLINE:
            self.consume_token(PLTokenType.ENDLINE)
        elif self.current_token_type == PLTokenType.EOF:
            self.consume_token(PLTokenType.EOF)
        else:
            raise ParseError("Expected EOF or End Line")
        return line

    def logical_sentence(self) -> Sentence:
        or_and_phrase: Sentence = self.or_and_phrase()
        if self.current_token_type == PLTokenType.IMPLIES:
            self.consume_token(PLTokenType.IMPLIES)
            sentence: Sentence = Sentence(or_and_phrase, LogicOperatorTypes.Implies, self.or_and_phrase())
            return sentence
        elif self.current_token_type == PLTokenType.BICONDITIONAL:
            self.consume_token(PLTokenType.BICONDITIONAL)
            sentence: Sentence = Sentence(or_and_phrase, LogicOperatorTypes.Biconditional, self.or_and_phrase())
            return sentence
        else:
            return or_and_phrase

    def or_and_phrase(self) -> Optional[Sentence]:
        sentence1: Optional[Sentence] = None
        # First try to process an and phrase
        if self.current_token_type != PLTokenType.OR:
            sentence1: Sentence = self.and_phrase()

        # After processing an "and phrase", try to process an "or phrase"
        if sentence1 is not None and self.current_token_type == PLTokenType.OR:
            self.consume_token(PLTokenType.OR)
            sentence: Sentence = Sentence(sentence1, LogicOperatorTypes.Or, self.or_and_phrase())
            return sentence
        else:
            return sentence1

    def and_phrase(self) -> Sentence:
        term1: Sentence = self.term()
        if self.current_token_type == PLTokenType.AND:
            self.consume_token(PLTokenType.AND)
            sentence: Sentence = Sentence(term1, LogicOperatorTypes.And, self.and_phrase())
            return sentence
        else:
            return term1

    def term(self) -> Sentence:
        sentence: Sentence
        negate_sentence: bool = False

        # Deal with a not symbol
        if self.current_token_type == PLTokenType.NOT:
            self.consume_token(PLTokenType.NOT)
            negate_sentence = True
            logical_sentence = self.term()
            if negate_sentence and logical_sentence.negation:
                # Double negation, so make this sentence a level above
                sentence = Sentence()
                sentence.first_sentence = logical_sentence
            else:
                sentence = logical_sentence
        # Is this a parenthetical sentence?
        elif self.current_token_type == PLTokenType.LPAREN:
            # This is a parenthetical sentence
            self.consume_token(PLTokenType.LPAREN)
            sentence = self.logical_sentence()
            self.consume_token(PLTokenType.RPAREN)
        else:
            # This must be a symbol
            symbol: str = self.consume_token(PLTokenType.SYMBOL)
            sentence = Sentence(symbol)

        # Deal with the negation if there was one
        if negate_sentence:
            sentence.negation = True

        return sentence
