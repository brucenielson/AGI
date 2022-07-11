from __future__ import annotations
from typing import List
from abc import abstractmethod
from typing import Optional


class Token:
    def __init__(self, token_name: str, token_type: int) -> None:
        # properties
        self._token_name: str = token_name.lower()
        self._token_type: int = token_type

    @property
    def token_name(self) -> str:
        return self._token_name.lower()

    @token_name.setter
    def token_name(self, value: str) -> None:
        self._token_name = value

    @property
    def token_type(self) -> int:
        return self._token_type

    @token_type.setter
    def token_type(self, value: int) -> None:
        self._token_type = value

    def match_name(self, token_name: str) -> bool:
        if self._token_name.lower() == token_name.lower():
            return True
        else:
            return False

    def match_type(self, token_type: int) -> bool:
        if self._token_type == token_type:
            return True
        else:
            return False

    def __eq__(self, other: Token) -> bool:
        if self == other:
            return True
        elif other is None or self._token_type != other.token_type:
            return False
        else:
            return other.token_type == self.token_type and other.token_name == self.token_name

    def __str__(self) -> str:
        return "[ " + str(self.token_type) + " " + self.token_name + " ]"


class TokenTable:
    def __init__(self) -> None:
        self.symbol_table: List[Token] = []
        self.init_symbol_table()

    @abstractmethod
    def init_symbol_table(self) -> None:
        """Initialize Symbol Table"""

    def add_token(self, token_name: str, token_type: int) -> None:
        token: Token = Token(token_name, token_type)
        self.add(token)

    def add(self, token: Token) -> None:
        # Don't add token if already in symbol table
        if self.find(token) is None:
            self.symbol_table.append(token)

    def find_by_name(self, token_name: str) -> Optional[Token]:
        for token in self.symbol_table:
            if token.token_name == token_name:
                return token
        return None

    def find_by_type(self, token_type: int) -> Optional[Token]:
        for token in self.symbol_table:
            if token.token_type == token_type:
                return token
        return None

    def find(self, token: Token) -> Optional[Token]:
        return self.find_by_name(token.token_name)

    def find_or_add(self, token_name: str, token_type: int) -> Token:
        new_token: Token = Token(token_name, token_type)
        token: Token = self.find(new_token)
        # If it wasn't found in the symbol table already, add it
        if token is None:
            self.add(new_token)
            token = new_token
        return token

    def sort(self) -> None:
        self.symbol_table.sort(key=lambda x: x.token_name)


# class Lexer:
#     white_space: int = int(' ')
#     tab: int = int('\t')
#
#     def __init__(self, input_string: str) -> None:
#         look_ahead: int = 4
#         self.token_table: TokenTable
#         self.input_string: str = input_string
#         self.next_char: int = self.white_space  # Initialize to white space
#         self.line_number: int = 1
#         self.token_pipeline: List[Token] = Token[look_ahead]
#
#     @abstractmethod
#     def get_next_token(self) -> Token:
#         """Function to get next token"""
#
#     def next_start_of_token(self) -> None:
#         # All this function does is move to the next token start if we are now on whitespace
#         # If this is a newline, line number is incremented
#         # Note: this function does nothing if EOF is reached
#         while self.next_char == Lexer.white_space or self.next_char == Lexer.tab:
#             self.next_char
#
#
#     def init_pipeline(self) -> None:
#         # Only do initialization if the pipeline is empty
#         if self.token_pipeline[0] == None:
#             self.next_start_of_token()
#             # Read in look ahead number of tokens and fill up the pipeline
#             for i in range(4):
#                 self.token_pipeline[i] = self.get_next_token()
