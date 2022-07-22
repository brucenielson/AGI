from __future__ import annotations
from pyparsing import alphas, alphanums, Word, ZeroOrMore, Forward, OneOrMore, Group, exceptions, oneOf, Literal
from enum import Enum
from typing import Optional, List

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
        not_sign = Literal('~')
        input_str = input_str.upper()
        symbol = Word(alphas.upper(), alphanums.upper())
        logical_sentence = Forward()
        term = not_sign + symbol | symbol | not_sign + "(" + logical_sentence + ")" | "(" + logical_sentence + ")"
        or_and_operator = oneOf(["AND", "OR"])
        or_and_phrase = term + ZeroOrMore(or_and_operator + term)
        logical_sentence << (or_and_phrase + "=>" + or_and_phrase
                             | or_and_phrase + "<=>" + or_and_phrase
                             | or_and_phrase)
        line = logical_sentence + "\n" | logical_sentence
        self.lines = OneOrMore(Group(line))
        try:
            self._tokens = self.lines.parse_string(input_str, parse_all=True)
        except exceptions.ParseException:
            raise ParseError("Incorrect syntax")
        self._token_list = self._tokens.asList()
        self._current_line = self._token_list[0]
        self._current_token = self._current_line[0]
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

    def token_look_head(self, look_ahead: int) -> PLTokenType:
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
            # TODO: I dislike this syntax
            sentence: Sentence = Sentence(or_and_phrase, LogicOperatorTypes.Implies, self.or_and_phrase())
            return sentence
        elif self.current_token_type == PLTokenType.BICONDITIONAL:
            self.consume_token(PLTokenType.BICONDITIONAL)
            # TODO: I dislike this syntax
            sentence: Sentence = Sentence(or_and_phrase, LogicOperatorTypes.Biconditional, self.or_and_phrase())
            return sentence
        else:
            return or_and_phrase

    def or_and_phrase(self) -> Sentence:
        sentence1: Sentence = None
        # First try to process an and phrase
        if self.current_token_type != PLTokenType.OR:
            sentence1: Sentence = self.and_phrase()

        # After processing an and phrase, try to process an or phrase
        if sentence1 is not None and self.current_token_type == PLTokenType.OR:
            self.consume_token(PLTokenType.OR)
            # TODO: I dislike this syntax
            sentence: Sentence = Sentence(sentence1, LogicOperatorTypes.Or, self.or_and_phrase())
            return sentence
        # elif self.token_look_head(1) == PLTokenType.OR:
        #     term1: Sentence = self.term()
        #     self.consume_token(PLTokenType.OR)
        #     # TODO: I dislike this syntax
        #     sentence: Sentence = Sentence()
        #     sentence.sentence_from_sentences(term1, LogicOperatorTypes.Or, self.or_and_phrase())
        #     return sentence
        # elif self.current_token_type == PLTokenType.SYMBOL:
        #     return self.term()
        else:
            return sentence1

    def and_phrase(self) -> Sentence:
        term1: Sentence = self.term()
        if self.current_token_type == PLTokenType.AND:
            self.consume_token(PLTokenType.AND)
            # TODO: I dislike this syntax
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
        # Is this a single symbol or a parenthetical sentence?
        if self.current_token_type == PLTokenType.LPAREN:
            # This is a parenthetical sentence
            self.consume_token(PLTokenType.LPAREN)
            sentence = self.logical_sentence()
            self.consume_token(PLTokenType.RPAREN)
        else:
            # This must be a symbol
            symbol: str = self.consume_token(PLTokenType.SYMBOL)
            sentence: Sentence = Sentence(symbol)

        # Deal with the negation if there was one
        if negate_sentence:
            sentence.negation = True

        return sentence


class Sentence:
    def __init__(self, symbol1_or_sentence1, logical_operator: LogicOperatorTypes = None, sentence2 = None, negated: bool = False):
        # set default values
        self._symbol: Optional[str] = None
        self._first_sentence: Optional[Sentence] = None
        self._second_sentence: Optional[Sentence] = None
        self._parent_sentence: Optional[Sentence] = None
        self._logic_operator: LogicOperatorTypes = LogicOperatorTypes.NoOperator
        # Set negation
        self._negation: bool = negated

        # A blank symbol should be treated as a None
        if symbol1_or_sentence1 == "":
            symbol1_or_sentence1 = None

        # Handle logical operator
        if sentence2 is not None and (logical_operator is None or logical_operator == LogicOperatorTypes.NoOperator):
            # We have a sentence2 but no logical operator, which is illegal
            SentenceError("You must have a logical operator if you have a second sentence in the constructor.")
        elif logical_operator is None:
            # No operator passed but also no sentence2 so just pass
            pass
        else:
            # Store the logic operator passed
            self._logic_operator = logical_operator

        # Handle sentence2
        if sentence2 is not None and isinstance(sentence2, str) and sentence2 != "":
            # Do we have a second sentence that is a string? If so, create it as a Sentence type
            self._second_sentence = Sentence(sentence2)
        elif isinstance(sentence2, Sentence):
            # Do we have a second sentence that is of Sentence type? If so, plug it right into place
            self._second_sentence = sentence2
        elif sentence2 is None:
            # If sentence2 is None, do nothing (i.e. don't throw error)
            pass
        else:
            # Something else entirely was passed, so throw an error
            raise SentenceError("The second sentence (sentence2) just be a string symbol, a Sentence, or None.")

        # Handle first sentence (or symbol)
        if isinstance(symbol1_or_sentence1, str):
            if self._second_sentence is None:
                # This is a symbol, so store it directly at a symbol
                self._symbol = symbol1_or_sentence1
            else:
                # This is not a lone symbol, so store it as a sentence
                self._first_sentence = Sentence(symbol1_or_sentence1)
        elif isinstance(symbol1_or_sentence1, Sentence):
            # This is a sentence, so store it as a sentence
            self._first_sentence = symbol1_or_sentence1
        else:
            # We should never have a blank first sentence/symbol
            raise SentenceError("The first parameter (symbol1_or_sentence1) must always be included.")

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

    def sentence_from_sentences(self, sentence1: Sentence, operator: LogicOperatorTypes, sentence2: Sentence) -> None:
        if not (operator == LogicOperatorTypes.NoOperator or sentence1 is None or sentence2 is None):
            self._logic_operator = operator
            self._negation = False
            self._symbol = None
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
        self._first_sentence = sentence
        self._second_sentence = None

