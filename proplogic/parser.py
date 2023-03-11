from __future__ import annotations
from pyparsing import alphas, alphanums, Word, ZeroOrMore, Forward, OneOrMore, Group, exceptions, oneOf, Literal
from enum import Enum
from typing import Optional, List
from proplogic.sentence import Sentence, LogicOperatorTypes

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


class TokenType(Enum):
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


class LogicParser:
    """
    The LogicParser class is used to convert input strings in the for of propositional logic into a list of
    logical Sentence(s)

    Usage
    _____
    parser: pl_parser.LogicParser = pl_parser.LogicParser(input_str)

    result: Sentence = parser.parse_line()

    or

    result_list: List[Sentence] = parser.parse_input()
    """
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

    def set_input(self, input_str: str) -> None:
        """
        This method allows you to pass in a string that the parser can then parse.

        :param input_str: The input string to be converted into a list of Sentence(s)
        :return: None
        """
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
    def _str_to_token_type(str_token: str) -> TokenType:
        str_token = str_token.upper()
        if str_token == "(":
            return TokenType.LPAREN
        elif str_token == ")":
            return TokenType.RPAREN
        elif str_token == "AND":
            return TokenType.AND
        elif str_token == "OR":
            return TokenType.OR
        elif str_token == "~":
            return TokenType.NOT
        elif str_token == "=>":
            return TokenType.IMPLIES
        elif str_token == "<=>":
            return TokenType.BICONDITIONAL
        elif str_token == "EOF":
            return TokenType.EOF
        elif str_token == "END LINE":
            return TokenType.ENDLINE
        else:
            return TokenType.SYMBOL

    @staticmethod
    def _token_type_to_str(token_type: TokenType) -> str:
        if token_type == TokenType.LPAREN:
            return "("
        elif token_type == TokenType.RPAREN:
            return ")"
        elif token_type == TokenType.AND:
            return "AND"
        elif token_type == TokenType.OR:
            return "OR"
        elif token_type == TokenType.NOT:
            return "~"
        elif token_type == TokenType.IMPLIES:
            return "=>"
        elif token_type == TokenType.BICONDITIONAL:
            return "<=>"
        elif token_type == TokenType.EOF:
            return "EOF"
        elif token_type == TokenType.ENDLINE:
            return "END LINE"
        elif token_type == TokenType.SYMBOL:
            return "a symbol"

    @property
    def current_token_type(self) -> TokenType:
        """
        This method allows you to pass in a string that the parser can then parse.
        :return: A TokenType of the current token
        """
        return self._str_to_token_type(self.current_token)

    @property
    def current_token(self) -> str:
        """
        Gets the current token that will be parsed next.
        :return: A string that contains the next token.
        """
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
        """
        Gets the count of lines of text to be parsed
        :return: An integer that is a count of lines.
        """
        return len(self._token_list)

    def token_look_head(self, look_ahead: int) -> Optional[TokenType]:
        """
        Returns the token look_ahead number of tokens out.
        :return: A TokenType of the token found
        """
        if len(self._token_list[0]) <= look_ahead:
            return None
        return self._str_to_token_type(self._current_line[look_ahead])

    def consume_token(self, check: TokenType = None) -> str:
        """
        Returns the next token (in the form of a string) to be parsed.

        :param check: Passing in the optional 'check' value will verify that the token you are about to consume
        was of the expected type. If not passed or set to None, then it is ignored and
        you just consume the next token. If the expected type if not matched, an ParseError is raised.
        :return: A string containing the next token
        """
        # Note:
        if len(self._token_list) == 0:
            if check is not None and check != TokenType.EOF:
                raise ParseError("Expected EOF")
            return "EOF"
        self._current_line = self._token_list[0]
        if len(self._current_line) == 0 and len(self._token_list) == 0:
            if check is not None and check != TokenType.EOF:
                raise ParseError("Expected EOF")
            return "EOF"
        elif len(self._current_line) == 0:
            if check is not None and check != TokenType.ENDLINE:
                raise ParseError("Expected END LINE")
            self._token_list.pop(0)
            return "END LINE"
        else:
            current_token: str = self._current_line.pop(0)
            if check is not None and LogicParser._str_to_token_type(current_token) != check:
                raise ParseError("Expected " + LogicParser._token_type_to_str(check))
            return current_token

    @property
    def token_list(self) -> list:
        """
        A property that returns the current list of tokens.
        :return: A list containing the unprocessed tokens.
        """
        return self._token_list

    def get_original_token_list(self) -> list:
        """
        Same as token_list property except it gives what the original list looked like.
        :return: A list containing the unprocessed tokens.
        """
        return self._tokens.asList()

    def is_end_of_file(self) -> bool:
        """
        Returns True if you have reached the end of the file
        :return: a boolean value
        """
        return LogicParser._str_to_token_type(self.current_token) == TokenType.EOF

    def parse_input(self) -> List[Sentence]:
        """
        Parses the input (set by set_input or by the constructor) and return a list of Sentence(s)
        :return: A list of parsed Sentence(s)
        """
        while not self.is_end_of_file():
            self._sentences.append(self.parse_line())
        return self._sentences

    def parse_line(self) -> Sentence:
        """
        Parses the input (set by set_input or by the constructor) and return a single Sentence that is parsed
        :return: A parsed Sentence
        """
        if self.is_end_of_file():
            raise ParseError("No Line Found.")
        return self._line()

    def _line(self) -> Sentence:
        line: Sentence = self._logical_sentence()
        if self.current_token_type == TokenType.ENDLINE:
            self.consume_token(TokenType.ENDLINE)
        elif self.current_token_type == TokenType.EOF:
            self.consume_token(TokenType.EOF)
        else:
            raise ParseError("Expected EOF or End Line")
        return line

    def _logical_sentence(self) -> Sentence:
        or_and_phrase: Sentence = self._or_and_phrase()
        if self.current_token_type == TokenType.IMPLIES:
            self.consume_token(TokenType.IMPLIES)
            sentence: Sentence = Sentence(or_and_phrase, LogicOperatorTypes.IMPLIES, self._or_and_phrase())
            return sentence
        elif self.current_token_type == TokenType.BICONDITIONAL:
            self.consume_token(TokenType.BICONDITIONAL)
            sentence: Sentence = Sentence(or_and_phrase, LogicOperatorTypes.BI_CONDITIONAL, self._or_and_phrase())
            return sentence
        else:
            return or_and_phrase

    def _or_and_phrase(self) -> Optional[Sentence]:
        sentence1: Optional[Sentence] = None
        # First try to process an and phrase
        if self.current_token_type != TokenType.OR:
            sentence1: Sentence = self._and_phrase()

        # After processing an "and phrase", try to process an "or phrase"
        if sentence1 is not None and self.current_token_type == TokenType.OR:
            self.consume_token(TokenType.OR)
            sentence: Sentence = Sentence(sentence1, LogicOperatorTypes.OR, self._or_and_phrase())
            return sentence
        else:
            return sentence1

    def _and_phrase(self) -> Sentence:
        term1: Sentence = self._term()
        if self.current_token_type == TokenType.AND:
            self.consume_token(TokenType.AND)
            sentence: Sentence = Sentence(term1, LogicOperatorTypes.AND, self._and_phrase())
            return sentence
        else:
            return term1

    def _term(self) -> Sentence:
        sentence: Sentence
        negate_sentence: bool = False

        # Deal with a not symbol
        if self.current_token_type == TokenType.NOT:
            self.consume_token(TokenType.NOT)
            negate_sentence = True
            logical_sentence = self._term()
            if negate_sentence and logical_sentence.negation:
                # Double negation, so make this sentence a level above
                sentence = Sentence()
                sentence.first_sentence = logical_sentence
            else:
                sentence = logical_sentence
        # Is this a parenthetical sentence?
        elif self.current_token_type == TokenType.LPAREN:
            # This is a parenthetical sentence
            self.consume_token(TokenType.LPAREN)
            sentence = self._logical_sentence()
            self.consume_token(TokenType.RPAREN)
        else:
            # This must be a symbol
            symbol: str = self.consume_token(TokenType.SYMBOL)
            sentence = Sentence(symbol)

        # Deal with the negation if there was one
        if negate_sentence:
            sentence.negation = True

        return sentence
