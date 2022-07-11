from parser_interfaces import Token, TokenTable
from enum import IntEnum


class PLTokenType(IntEnum):
    SYMBOL = 1
    LPAREN = 2
    RPAREN = 3
    AND = 4
    OR = 5
    NOT = 6
    IMPLIES = 7
    BICONDITIONAL = 8
    EOF = 9
    NEWLINE = 10


def pl_token_to_string(token_type: PLTokenType):
    if token_type == PLTokenType.SYMBOL:
        return "Symbol"
    elif token_type == PLTokenType.LPAREN:
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
        return "End of File"
    elif token_type == PLTokenType.NEWLINE:
        return "New Line"
    else:
        raise Exception("Invalid Token Type")


class PLToken(Token):
    def __init__(self, token_name: str, token_type: PLTokenType):
        super().__init__(token_name, token_type)


class PLTokenTable(TokenTable):
    def init_symbol_table(self):
        # Add the reserved keywords for propositional logic
        self.add_token("~", PLTokenType.NOT)
        self.add_token("and", PLTokenType.AND)
        self.add_token("or", PLTokenType.OR)
        self.add_token("=>", PLTokenType.IMPLIES)
        self.add_token("<=>", PLTokenType.BICONDITIONAL)
        self.add_token("(", PLTokenType.LPAREN)
        self.add_token(")", PLTokenType.RPAREN)
        self.add_token("End of File", PLTokenType.EOF)
        self.add_token("New Line", PLTokenType.NEWLINE)
