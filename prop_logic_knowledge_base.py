from prop_logic_parser import PropLogicParser, Sentence
from typing import Optional, List, Union
from enum import Enum


class LogicValue(Enum):
    FALSE = 0
    TRUE = 1
    UNDEFINED = -1


class LogicSymbol:
    def __init__(self, name: str, value: LogicValue = LogicValue.UNDEFINED):
        self._name = name
        self.value = value

    @property
    def name(self) -> str:
        return self._name

    @property
    def value(self) -> LogicValue:
        return self._value

    @value.setter
    def value(self, value: Union[LogicValue, bool]) -> None:
        final_value: LogicValue
        if isinstance(value, bool):
            if value:
                final_value = LogicValue.TRUE
            else:
                final_value = LogicValue.FALSE
        else:
            final_value = value
        self._value = final_value


class SymbolListError(Exception):
    def __init__(self, message):
        super().__init__(message)


class SymbolList:
    def __init__(self):
        self._symbols: List[LogicSymbol] = []
        self._auto_sort: bool = True
        self._is_sorted: bool = False

    def get_symbols(self) -> List[LogicSymbol]:
        return self._symbols

    @property
    def auto_sort(self) -> bool:
        return self._auto_sort

    @auto_sort.setter
    def auto_sort(self, auto_sort: bool) -> None:
        if auto_sort:
            self.sort()
        else:
            self._auto_sort = False

    @property
    def is_sorted(self) -> bool:
        return self._is_sorted

    @property
    def length(self) -> int:
        return len(self._symbols)

    def get_symbol(self, position: int) -> LogicSymbol:
        if position > len(self._symbols) - 1 or position < 0:
            raise SymbolListError("Call to get_symbol was out of bounds.")
        return self._symbols[position]

    def get_next_symbol(self) -> Optional[LogicSymbol]:
        # This function returns the first symbol in the list while removing it
        if len(self._symbols) == 0 or self._symbols is None:
            return None
        else:
            return self._symbols.pop(0)

    def find(self, symbol_name: str) -> Optional[LogicSymbol]:
        return self.find_with_index(symbol_name)[0]

    def find_with_index(self, symbol_name: str) -> (Optional[LogicSymbol], int):
        symbol_name = symbol_name.upper()
        symbol: LogicSymbol
        mid: int = -1
        if self._is_sorted:
            # List is currently sorted so do binary search
            low: int = 0
            high: int = self.length - 1
            while 0 <= low <= high < self.length:
                mid: int = (low + high) // 2
                if symbol_name == self._symbols[mid].name:
                    return self._symbols[mid], mid
                elif symbol_name > self._symbols[mid].name:
                    low = mid + 1
                else:
                    high = mid - 1
        else:
            # List is currently unsorted so do full search
            i: int = 0
            for symbol in self._symbols:
                if symbol.name == symbol_name:
                    return symbol, i
                i += 1
        # Didn't find anything
        return None, mid

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
        for i in range(left, right+1):
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
        self._symbols = self._symbols[:left] + left_symbols + [pivot_symbol] + right_symbols + self._symbols[right+1:]
        # Do recursive calls
        if left < left_counter - 1:
            self._quick_sort(left, left_counter-1)
        if left_counter + 1 < right:
            self._quick_sort(left_counter + 1, right)

    def add(self, symbol_name: str, value: Union[LogicValue, bool] = LogicValue.UNDEFINED) -> None:
        symbol_name = symbol_name.upper()
        symbol: LogicSymbol = LogicSymbol(symbol_name, value)
        found_symbol: LogicSymbol
        index: int
        # Only add if this symbol is not already in the list
        (found_symbol, index) = self.find_with_index(symbol_name)
        if found_symbol is None:
            if self._auto_sort:
                low: int = 0
                high: int = self.length - 1
                mid: int = (low + high) // 2
                if self.length == 0:
                    self._symbols.append(symbol)
                else:
                    while low < high and low <= mid <= high:
                        if symbol_name > self._symbols[mid].name:
                            low = mid + 1
                        elif symbol_name < self._symbols[mid].name:
                            high = mid - 1
                        mid = (low + high) // 2

                    if mid == -1:
                        self._symbols.insert(0, symbol)
                    elif mid == 0 and symbol_name > self._symbols[mid].name:
                        self._symbols.insert(1, symbol)
                    elif mid == high and symbol_name > self._symbols[mid].name:
                        self._symbols.append(symbol)
                    else:
                        self._symbols.insert(mid, symbol)
                self._is_sorted = True
            else:
                self._symbols.append(symbol)
                self._is_sorted = False

    def set_value(self, symbol_name: str, value: Union[LogicValue, bool]) -> None:
        symbol: LogicSymbol = self.find(symbol_name)
        symbol.value = value

    def get_value(self, symbol_name: str) -> LogicValue:
        symbol: LogicSymbol = self.find(symbol_name)
        return symbol.value


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
