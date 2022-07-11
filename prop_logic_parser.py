from __future__ import annotations
from pyparsing import alphas, alphanums, Word, ZeroOrMore, Forward, OneOrMore, Group, exceptions
from enum import Enum
from typing import Optional

# Original Grammar for the Propositional Logic Parser
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


class SentenceType(Enum):
    AtomicSentence = 1
    ComplexSentence = 2


class LogicOperatorTypes(Enum):
    NoOperator = 1
    And = 2
    Or = 3
    Implies = 4
    # noinspection SpellCheckingInspection
    Biconditional = 5


class SentenceError(Exception):
    def __init__(self, message=None):
        self.message = message
        super().__init__(self.message)


class PropLogicParser:
    def __init__(self, input_str: str) -> None:
        input_str = input_str.upper()
        symbol = Word(alphas.upper(), alphanums.upper())
        logical_sentence = Forward()
        term = "~" + symbol | symbol | "(" + logical_sentence + ")"
        and_operands = term + ZeroOrMore("AND" + term)
        or_and_operands = and_operands + ZeroOrMore("OR" + and_operands)
        logical_sentence << (or_and_operands + "=>" + or_and_operands
                             | or_and_operands + "<=>" + or_and_operands
                             | or_and_operands)
        line = logical_sentence + "\n" | logical_sentence
        self.lines = OneOrMore(Group(line))
        try:
            self._tokens = self.lines.parse_string(input_str, parse_all=True)
        except exceptions.ParseException:
            raise ParseError
        self._token_list = self._tokens.asList()
        self._current_line = self._token_list[0]
        self._current_token = self._current_line[0]

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
        elif str_token == "NOT":
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
            return "NOT"
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
    def current_token(self) -> str:
        self._current_line = self._token_list[0]
        self._current_token = self._current_line[0]
        return self._current_token

    def consume_token(self, check: PLTokenType = None) -> str:
        # Note: passing in a 'check' value will verify that the token you are about to consume was of the expected type
        # If not passed or set to None, then it is ignored and you just consume the next token
        if len(self._token_list) == 0:
            if check is not None and check != PLTokenType.EOF:
                raise ParseError("Expected EOF")
            return "EOF"
        self._current_line = self._token_list[0]
        if len(self._current_line) == 0:
            self._token_list.pop(0)
            if len(self._token_list) == 0:
                if check is not None and check != PLTokenType.EOF:
                    raise ParseError("Expected EOF")
                return "EOF"
            self._current_line = self._token_list[0]
            if check is not None and check != PLTokenType.ENDLINE:
                raise ParseError("Expected EOF")
            return "END LINE"

        current_token: str = self._current_line.pop(0)
        if check is not None and PropLogicParser._str_to_token_type(current_token) != check:
            raise ParseError("Expected " + PropLogicParser._token_type_to_str(check))
        return current_token

    @property
    def token_list(self) -> list:
        return self._token_list

    def get_original_token_list(self) -> list:
        return self._tokens.asList()

    # def sentence_from_input(self, token_list: list) -> None:
    #     if token_list is None:
    #         raise SentenceError("Illegal parameter. The input string must not be null or empty.")
    #     for line in token_list:
    #         pass
    #         self.sentence_from_line(line)
    #
    # def sentence_from_line(self, line: list) -> Sentence:
    #     sentence: Sentence = self.logical_sentence(line)
    #     return sentence
    #
    # def logical_sentence(self, line: list) -> Sentence:
    #     or_and_operands: Sentence = self.or_and_operands(line)
    #     return or_and_operands
    #
    # def or_and_operands(self, line: list) -> Sentence:
    #     and_operands: Sentence = self.and_operands
    #     if not self.is_end_of_sub_sentence():


class Sentence:
    def __init__(self, symbol: str = None, negated: bool = False):
        if symbol == "":
            symbol = None
        # Declare instance variables and set defaults
        self._logic_operator: LogicOperatorTypes = LogicOperatorTypes.NoOperator
        self._negation: bool = negated
        self._symbol: str = symbol
        self._sentence_type: SentenceType = SentenceType.AtomicSentence
        self._first_sentence: Optional[Sentence] = None
        self._second_sentence: Optional[Sentence] = None
        self._parent_sentence: Optional[Sentence] = None

    @property
    def logic_operator(self) -> LogicOperatorTypes:
        return self._logic_operator

    @logic_operator.setter
    def logic_operator(self, value: LogicOperatorTypes) -> None:
        self._logic_operator = value

    @property
    def negation(self) -> bool:
        return self._negation

    @negation.setter
    def negation(self, value: bool) -> None:
        self._negation = value

    @property
    def symbol(self) -> str:
        return self._symbol

    @symbol.setter
    def symbol(self, value: str) -> None:
        self._symbol = value

    @property
    def sentence_type(self) -> SentenceType:
        return self._sentence_type

    @sentence_type.setter
    def sentence_type(self, value: SentenceType) -> None:
        self._sentence_type = value

    @property
    def first_sentence(self) -> Sentence:
        return self._first_sentence

    @first_sentence.setter
    def first_sentence(self, value: Sentence) -> None:
        self._first_sentence = value
        self._first_sentence._parent_sentence = self

    @property
    def second_sentence(self) -> Sentence:
        return self._second_sentence

    @second_sentence.setter
    def second_sentence(self, value: Sentence) -> None:
        self._second_sentence = value
        self._second_sentence._parent_sentence = self

    def sentence_from_tokens(self, token1: str, operator: LogicOperatorTypes, token2: str) -> None:
        if not (operator == LogicOperatorTypes.NoOperator or token1 == "" or token2 == ""
                or token1 is None or token2 is None):
            self.sentence_from_sentences(Sentence(token1), operator, Sentence(token2))
        else:
            raise SentenceError("Illegal parameters. Operator cannot be 'None' and Tokens cannot be blank.")

    def sentence_from_sentences(self, sentence1: Sentence, operator: LogicOperatorTypes, sentence2: Sentence):
        if not (operator == LogicOperatorTypes.NoOperator or sentence1 is None or sentence2 is None):
            self._logic_operator = operator
            self._negation = False
            self._symbol = None
            self._sentence_type = SentenceType.ComplexSentence
            self._first_sentence = sentence1
            self._second_sentence = sentence2
        else:
            raise SentenceError("Illegal parameters. Operator cannot be 'None' and Tokens cannot be blank.")

    def negate_sentence(self, sentence: Sentence) -> None:
        if sentence is None:
            raise SentenceError("Illegal parameters. The sentence parameter can't be None.")
        self._negation = True
        self._logic_operator = LogicOperatorTypes.NoOperator
        self._symbol = None
        self._sentence_type = SentenceType.ComplexSentence
        self._first_sentence = sentence
        self._second_sentence = None

