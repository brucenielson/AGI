from __future__ import annotations
from prop_logic_parser import PropLogicParser, Sentence
from typing import Optional, List, Union
from enum import Enum
from copy import deepcopy


def slice_to_ints(a_slice: slice, max_index: int):
    start: int = 0
    stop: int = max_index
    step: int = 1
    if a_slice.step is not None:
        step = a_slice.step
    if a_slice.start is not None:
        start = a_slice.start
    if a_slice.stop is not None:
        stop = a_slice.stop
    keys: range = range(start, stop, step)
    index_list = list(keys)
    return index_list


def create_index(indexes: list, max_index: int) -> List[int]:
    index_list: List[int] = []
    if isinstance(indexes, int):
        index_list.append(indexes)
    elif isinstance(indexes, slice):
        index_list: List[int] = slice_to_ints(indexes, max_index)
    else:
        # Mixture of both integers and slices
        for i in indexes:
            if isinstance(i, int):
                index_list.append(i)
            elif isinstance(i, slice):
                index_list.extend(slice_to_ints(i, max_index))
    return index_list


class LogicValue(Enum):
    FALSE = 0
    TRUE = 1
    UNDEFINED = -1

    def __repr__(self) -> str:
        if self == LogicValue.UNDEFINED:
            return "Undefined"
        elif self == LogicValue.TRUE:
            return "True"
        elif self == LogicValue.FALSE:
            return "False"


class LogicSymbol:
    def __init__(self, name: str, value: LogicValue = LogicValue.UNDEFINED):
        self._name = name
        self.value = value

    def __repr__(self) -> str:
        return self.name + ": " + repr(self.value)

    def __eq__(self, other):
        if type(self) == type(other) and self.name == other.name and self.value == other.value:
            return True
        else:
            return False

    @property
    def name(self) -> str:
        return self._name

    @property
    def value(self) -> LogicValue:
        return self._value

    @value.setter
    def value(self, value: Optional[Union[LogicValue, bool]]) -> None:
        final_value: LogicValue
        if isinstance(value, bool):
            if value:
                final_value = LogicValue.TRUE
            else:
                final_value = LogicValue.FALSE
        elif value is None:
            final_value = LogicValue.UNDEFINED
        else:
            final_value = value
        self._value = final_value


class SymbolListError(Exception):
    def __init__(self, message):
        super().__init__(message)


class KnowledgeBaseError(Exception):
    def __init__(self, message):
        super().__init__(message)


class SymbolListIterator:
    def __init__(self, symbol_list: SymbolList):
        self._symbol_list = symbol_list
        self._index: int = 0

    def __next__(self):
        result: LogicSymbol
        if self._index < self._symbol_list.length:
            result = self._symbol_list.get_symbols()[self._index]
            self._index += 1
            return result
        else:
            raise StopIteration


class SymbolList:
    # See https://riptutorial.com/python/example/1571/indexing-custom-classes----getitem------setitem---and---delitem--
    # for now to implement getitem setitem related stuff
    def __init__(self):
        self._symbols: List[LogicSymbol] = []
        self._auto_sort: bool = True
        self._is_sorted: bool = False

    def __iter__(self) -> SymbolListIterator:
        return SymbolListIterator(self)

    def __repr__(self) -> str:
        repr_str: str = ""
        for symbol in self._symbols:
            repr_str += repr(symbol) + "; "
        return repr_str

    def __getitem__(self, indexes) -> Union[LogicSymbol, SymbolList]:
        index_list: List[int] = create_index(indexes, self.length)
        # If there is only one element in the index_list, then return a single LogicSymbol
        if len(index_list) == 1:
            return self.get_symbol(index_list[0])
        # We have a list of indexes, now turn it into a new SymbolList
        output: List[LogicSymbol] = [self.get_symbol(i) for i in index_list]
        new_symbol_list: SymbolList = SymbolList()
        new_symbol_list._symbols = output
        return new_symbol_list

    def __setitem__(self, key, value):
        if isinstance(key, int):
            self.set_value(self.get_symbol(key).name, value)
        else:
            for i in key:
                self.set_value(self.get_symbol(i).name, value)

    def __delitem__(self, indexes):
        index_list: List[int] = create_index(indexes, self.length)
        index_list.reverse()
        for i in index_list:
            del self._symbols[i]

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
        # Finds the symbol you ask for with the index of where it was found
        # If it doesn't find the symbol, it returns None for the symbol and the index value of where it would go
        symbol_name = symbol_name.upper()
        symbol: LogicSymbol
        mid: int = 0
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
            # If we aborted the search by going off the edge, so a correction to mid so we get insertion point right
            if low == self.length:
                mid = self.length
            elif high < 0:
                mid = 0
            elif low > high:
                mid = low

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

    def add(self, symbol_or_list: Union[str, LogicSymbol, SymbolList],
            value: Union[LogicValue, bool] = LogicValue.UNDEFINED) -> None:
        if isinstance(symbol_or_list, SymbolList):
            # Concatenate the SymbolList into this SymbolList
            symbol: LogicSymbol
            for symbol in symbol_or_list:
                self.add(symbol)
        else:
            symbol: LogicSymbol
            if isinstance(symbol_or_list, str):
                symbol_or_list = symbol_or_list.upper()
                symbol = LogicSymbol(symbol_or_list, value)
            elif isinstance(symbol_or_list, LogicSymbol):
                symbol = symbol_or_list
            else:
                raise SymbolListError("The 'add' command requires a string symbol, LogicSymbol, or a SymbolList")
            # Add the symbol to this list
            found_symbol: LogicSymbol
            index: int
            # Only add if this symbol is not already in the list
            (found_symbol, index) = self.find_with_index(symbol.name)
            if found_symbol is None:
                if self._auto_sort:
                    self._symbols.insert(index, symbol)
                    self._is_sorted = True
                else:
                    self._symbols.append(symbol)
                    self._is_sorted = False

    def set_value(self, symbol_name: str, value: Optional[Union[LogicValue, bool]]) -> None:
        symbol: LogicSymbol = self.find(symbol_name)
        symbol.value = value

    def get_value(self, symbol_name: str) -> LogicValue:
        symbol: LogicSymbol = self.find(symbol_name)
        return symbol.value

    def clone(self):
        return deepcopy(self)


class PLKnowledgeBase:
    # Static parser -- so that Sentence can parse propositional logic text
    _parser: PropLogicParser = PropLogicParser()

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

    def exists(self, sentence: Union[Sentence, str], check_logical_equivalence: bool = False) -> bool:
        if isinstance(sentence, Sentence):
            for a_sentence in self._sentences:
                if not check_logical_equivalence:
                    # Using quick check is preferred, it just makes sure the two sentences resolve to same string
                    if a_sentence.to_string(True) == sentence.to_string(True):
                        return True
                else:  # not check_logical_equivalence
                    # Slow check will instead seek if any of these sentences is logically equivalent
                    if a_sentence == sentence:
                        return True
            # Didn't find a match, so doesn't exist
            return False
        elif isinstance(sentence, str):
            self._parser.set_input(sentence)
            new_sentence: Sentence = self._parser.parse_line()
            if self._parser.line_count > 0:
                raise KnowledgeBaseError("Call to 'exists' only works for a single logical line.")
            return self.exists(new_sentence, check_logical_equivalence=check_logical_equivalence)
        else:
            raise KnowledgeBaseError("Call to 'exists' call requires a Sentence or string.")

    def add(self, sentence_or_list:  Union[Sentence, List[Sentence], str]) -> None:
        if isinstance(sentence_or_list, str):
            PLKnowledgeBase._parser.set_input(sentence_or_list)
            sentence_list: List[Sentence] = PLKnowledgeBase._parser.parse_input()
            self.add(sentence_list)
        elif isinstance(sentence_or_list, Sentence):
            if not self.exists(sentence_or_list):
                self._sentences.append(sentence_or_list)
            self._is_cnf = False
        else:
            for sentence in sentence_or_list:
                self.add(sentence)

    @property
    def line_count(self) -> int:
        return len(self._sentences)

    def get_sentence(self, index: int) -> Sentence:
        if index <= len(self._sentences):
            return self._sentences[index]
        else:
            raise KnowledgeBaseError("Attempted to use get_sentence(index) with index out of bounds.")

    def clone(self):
        return deepcopy(self)
