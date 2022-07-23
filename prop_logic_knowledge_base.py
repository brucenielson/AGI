from prop_logic_parser import PropLogicParser, Sentence
from typing import Optional, List, Union
from enum import Enum


class LogicValue(Enum):
    FALSE = 0
    TRUE = 1
    UNDEFINED = -1


class LogicSymbol:
    def __init__(self, name: str = None, value: LogicValue = LogicValue.UNDEFINED):
        self.name = name
        self.value = value

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        self._name = name.upper()

    @property
    def value(self) -> LogicValue:
        return self._value

    @value.setter
    def value(self, value: LogicValue) -> None:
        self._value = value


class SymbolList:
    def __init__(self):
        self._symbols: List[LogicSymbol] = []
        self._auto_sort: bool = False
        self._is_sorted: bool = False

    def get_symbols(self) -> List[LogicSymbol]:
        return self._symbols

    @property
    def auto_sort(self) -> bool:
        return self._auto_sort

    @auto_sort.setter
    def auto_sort(self, auto_sort: bool) -> None:
        self._auto_sort = auto_sort

    @property
    def is_sorted(self) -> bool:
        return self._is_sorted

    def find(self, symbol_name: str) -> Optional[LogicSymbol]:
        # TODO: if the list is sorted, do a binary search instead of a full search
        symbol_name = symbol_name.upper()
        symbol: LogicSymbol
        for symbol in self._symbols:
            if symbol.name == symbol_name:
                return symbol
        return None

    def sort(self) -> None:
        # Do a quick sort of the list of symbols
        self._quick_sort(0, len(self._symbols)-1)
        self._is_sorted = True

    def _quick_sort(self, left: int, right: int) -> None:
        assert right >= left
        length: int = (right - left) + 1
        right_symbols: List[LogicSymbol] = []
        left_symbols: List[LogicSymbol] = []
        pivot_symbol: LogicSymbol

        # Abort once we have a single symbol we are sorting
        if length <= 1:
            return
        middle: int = (length // 2) + left
        left_counter: int = left
        right_counter: int = right
        pivot_symbol = self._symbols[middle]

        i: int
        for i in range(left, right):
            # skip over the pivot point
            if i == middle:
                continue
            elif self._symbols[i].name < pivot_symbol.name:
                # Send left
                left_symbols.append(self._symbols[i])
                left_counter += 1
            else:
                # Send right
                right_symbols.append(self._symbols[i])
                right_counter -= 1
        # Create new list
        self._symbols = left_symbols + [pivot_symbol] + right_symbols
        # Do recursive calls
        if left < left_counter - 1:
            self._quick_sort(left, left_counter-1)
        if left_counter + 1 < right:
            self._quick_sort(left_counter + 1, right)

    def add(self, symbol_name: str) -> None:
        symbol_name = symbol_name.upper()
        # Only add if this symbol is not already in the list
        if self.find(symbol_name) is not None:
            self._symbols.append(LogicSymbol(symbol_name))
        # TODO: I should insert this into the correct sorted location rather than calling sort
        if self._auto_sort:
            self.sort()
            self._is_sorted = True
        else:
            self._is_sorted = False


class PLKnowledgeBase:
    # Static parser -- so that Sentence can parse propositional logic text
    _prop_logic_parser: PropLogicParser = PropLogicParser()

    def __init__(self) -> None:
        # A propositional logic knowledge base is really just an array of propositional logic sentences
        self._sentences: List[Sentence] = []
        # These are used to determine number of true and false -- I need this to determine if
        # the query being entailed is true, false, or indeterminate
        self._query_true_count: int = 0
        self._query_false_count: int = 0
        # Used for finding symbol that is a unit clause
        self._possible_unit_clause: LogicSymbol
        self._count_of_symbols: int = 0
        self._is_cnf: bool = False

    @property
    def is_cnf(self) -> bool:
        return self._is_cnf

    def clear(self) -> None:
        self._sentences = []
        self._is_cnf = False

    def add(self, sentence: Sentence):
        pass
