from __future__ import annotations
from typing import Optional, List, Union, Tuple
from copy import deepcopy
from enum import Enum


def _slice_to_ints(a_slice: slice, max_index: int) -> list:
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


def _create_index(indexes: list, max_index: int) -> List[int]:
    index_list: List[int] = []
    if isinstance(indexes, int):
        index_list.append(indexes)
    elif isinstance(indexes, slice):
        index_list: List[int] = _slice_to_ints(indexes, max_index)
    else:
        # Mixture of both integers and slices
        for i in indexes:
            if isinstance(i, int):
                index_list.append(i)
            elif isinstance(i, slice):
                index_list.extend(_slice_to_ints(i, max_index))
    return index_list


class LogicValue(Enum):
    """
    An enumerated type of logic values including TRUE, FALSE, and UNDEFINED.

    This enumerated types includes a few methods to allow AND and OR operations and to allow LogicValues to
    have a string representation.
    """
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

    def and_op(self, other_value: LogicValue) -> LogicValue:
        """
        Usage: <LogicValue>.and_op(<LogicValue) returns an AND operation between those two values.
        :param other_value:
        :return: A LogicValue
        """
        if self == LogicValue.TRUE and other_value == LogicValue.TRUE:
            return LogicValue.TRUE
        elif self == LogicValue.FALSE or other_value == LogicValue.FALSE:
            return LogicValue.FALSE
        else:
            return LogicValue.UNDEFINED

    def or_op(self, other_value: LogicValue) -> LogicValue:
        """
        Usage: <LogicValue>.or_op(<LogicValue) returns an OR operation between those two values.
        :param other_value:
        :return: A LogicValue
        """
        if self == LogicValue.TRUE or other_value == LogicValue.TRUE:
            return LogicValue.TRUE
        elif self == LogicValue.FALSE and other_value == LogicValue.FALSE:
            return LogicValue.FALSE
        else:
            return LogicValue.UNDEFINED


def _bool_to_logic_value(value: Union[bool, LogicValue]) -> LogicValue:
    if isinstance(value, bool):
        if value:
            return LogicValue.TRUE
        else:
            return LogicValue.FALSE
    else:
        return value


class LogicSymbolError(Exception):
    def __init__(self, message):
        super().__init__(message)


class LogicSymbol:
    """
    A LogicSymbol is a class with a name (string) and value (LogicValue) for each Symbol.
    Also contains and_op and or_op functions to perform AND and OR operations on LogicSymbol(s)
    """
    def __init__(self, name: str, value: LogicValue = LogicValue.UNDEFINED) -> None:
        if name.isalnum() and name[0].isalpha():
            self._name = name
        else:
            raise LogicSymbolError("Logic symbols must start with an alpha and then be alphanumeric.")
        self.value = value

    def __repr__(self) -> str:
        return self.name + ": " + repr(self.value)

    def __eq__(self, other) -> bool:
        if type(self) == type(other) and self.name == other.name and self.value == other.value:
            return True
        else:
            return False

    def __hash__(self) -> int:
        return hash(repr(self))

    def __lt__(self, other):
        return self.name < other.name

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

    def and_op(self, other_value: LogicValue) -> LogicValue:
        """
        Usage: <LogicValue>.and_op(<LogicValue) returns an AND operation between those two values.
        :param other_value:
        :return: A LogicValue
        """
        return self.value.and_op(other_value)

    def or_op(self, other_value: LogicValue) -> LogicValue:
        """
        Usage: <LogicValue>.or_op(<LogicValue) returns an OR operation between those two values.
        :param other_value:
        :return: A LogicValue
        """
        return self.value.or_op(other_value)


class SymbolListError(Exception):
    def __init__(self, message):
        super().__init__(message)


class _SymbolListIterator:
    def __init__(self, symbol_list: SymbolList):
        self._symbol_list: List[str] = symbol_list.get_keys()
        self._index: int = 0

    def __next__(self):
        result: str
        if self._index < len(self._symbol_list):
            result = self._symbol_list[self._index]
            self._index += 1
            return result
        else:
            raise StopIteration


class SymbolList:
    """
    A SymbolList is a list of LogicSymbol(s) with related methods. It can be iterated and sliced like a list with all
    symbols sorted in alphabetical order.
    """

    # See https://riptutorial.com/python/example/1571/indexing-custom-classes----getitem------setitem---and---delitem--
    # for now to implement getitem setitem related stuff
    def __init__(self) -> None:
        self._symbols: dict[str, LogicValue] = {}

    def __iter__(self) -> _SymbolListIterator:
        return _SymbolListIterator(self)

    def __repr__(self) -> str:
        repr_str: str = ""
        keys: List[str] = self.get_keys()
        for symbol_name in keys:
            repr_str += symbol_name + ": " + repr(self._symbols[symbol_name]) + "; "
        return repr_str

    def __getitem__(self, indexes: Union[Tuple[int, int], str, int, list]) \
            -> Union[LogicSymbol, LogicValue, SymbolList]:
        if isinstance(indexes, str):
            return self.get_symbol(indexes).value
        else:
            index_list: List[int] = _create_index(indexes, self.length)
            # If there is only one element in the index_list, then return a single LogicSymbol
            if len(index_list) == 1:
                return self.get_symbol(index_list[0])
            # We have a list of indexes, now turn it into a new SymbolList
            output: List[LogicSymbol] = [self.get_symbol(i) for i in index_list]
            new_symbol_list: SymbolList = SymbolList()
            new_symbol_list.add(output)
            return new_symbol_list

    def __setitem__(self, key, value):
        if isinstance(key, int):
            self.set_value(self.get_symbol(key).name, value)
        else:
            for i in key:
                self.set_value(self.get_symbol(i).name, value)

    def __delitem__(self, index: Union[str, int]) -> None:
        if isinstance(index, str):
            self._symbols.pop(index)
        else:
            keys: List[str] = self.get_keys()
            key = keys[index]
            self._symbols.pop(key)

    def get_symbols(self) -> dict[str, LogicValue]:
        """
        Returns a dictionary of symbols indexed by symbol name (str)
        :return: A dictionary of type dict[str, LogicValue]
        """
        return self._symbols

    def get_keys(self) -> List[str]:
        """
        Returns a list of all symbol names, sorted alphabetically.
        :return: A list of type List[str]
        """
        keys: list[str] = list(self._symbols.keys())
        keys.sort()
        return keys

    @property
    def length(self) -> int:
        return len(self._symbols)

    def get_symbol(self, index: Union[str, int]) -> Optional[LogicSymbol]:
        """
        Pass an index and get back the associated LogicSymbol contained within the SymbolList

        :param index: Can be a str or int. A string would reference a symbol by its name. An integer would
        reference it by its sorter order.
        :return: Returns the symbol as a type LogicSymbol. Returns None if the str symbol_name does not exist
        but raises an error if integer indexed out of bounds.
        """
        if isinstance(index, str):
            index = index.upper()
            if index in self._symbols:
                return LogicSymbol(index, self._symbols[index])
            else:
                return None
        elif isinstance(index, int):
            # index is an integer
            if index > len(self._symbols) - 1 or index < 0:
                raise SymbolListError("Call to get_symbol was out of bounds.")
            keys: List[str] = self.get_keys()
            if keys[index] in keys:
                return LogicSymbol(keys[index], self._symbols[keys[index]])
        else:
            raise SymbolListError("Passed an index for a symbol that was not a string or integer.")

    def pop(self, index: Union[str, int]) -> Optional[LogicSymbol]:
        """
        Gets the symbol from the SymbolList of with the associated symbol_name (str). Removes that symbol from the list.
        Similar to get_symbol function but removes the symbol from the SymbolList.

        :param index: Can be a str or int. A string would reference a symbol by its name. An integer would
        reference it by its sorter order.
        :return: Returns the symbol as a type LogicSymbol
        """
        symbol = self.get_symbol(index)
        self._symbols.pop(symbol.name)
        return symbol

    def get_next_symbol(self) -> Optional[LogicSymbol]:
        """
        This function returns the first symbol in the list while removing it

        :return: Returns a LogicSymbol of the next symbol in the list ordered alphabetically.
        """
        if len(self._symbols) == 0 or self._symbols is None:
            return None
        else:
            symbol_keys: List[str] = self.get_keys()
            return self.pop(symbol_keys[0])

    def index(self, symbol_name: str) -> Optional[int]:
        """
        Give the name of a symbol (symbol_name) return the associated integer index.

        :param symbol_name: A string with the name of the symbol.
        :return: Returns an integer of the index of this symbol_name. Returns None it does not exist.
        """
        symbol_name = symbol_name.upper()
        keys: List[str] = self.get_keys()
        index: Optional[int]
        try:
            index = keys.index(symbol_name)
        except ValueError:
            index = None
        return index

    def add(self, symbol_or_list: Union[LogicSymbol, str, SymbolList, List[LogicSymbol], List[str, int]],
            value: Union[LogicValue, bool] = LogicValue.UNDEFINED) -> None:
        """
        Adds to this Sentence a symbol or a list of symbols with a given LogicValue, defaulting to UNDEFINED.

        :param symbol_or_list: This is either a symbol as a str or LogicSymbol or a list of symbols
        as a List[LogicSymbol] or SymbolList.
        :param value: An optional parameter to set the LogicValue for this symbol if passed as a symbol_name str
        Defaults to UNDEFINED. For any other type of symbol_or_list passed this parameter is ignored because we're
        passing the values we want to use.
        :return: None
        """
        if isinstance(symbol_or_list, LogicSymbol):
            symbol: LogicSymbol = symbol_or_list
            self._symbols[symbol.name] = symbol.value
        elif isinstance(symbol_or_list, str):
            symbol_name: str = symbol_or_list
            symbol_name = symbol_name.upper()
            if symbol_name.isalnum() and symbol_name[0].isalpha():
                self._symbols[symbol_name] = _bool_to_logic_value(value)
            else:
                raise SymbolListError("Symbols must start with a letter.")
        elif isinstance(symbol_or_list, list):
            symbol_list: List[LogicSymbol] = symbol_or_list
            # Concatenate the SymbolList into this SymbolList
            for symbol in symbol_list:
                self.add(symbol)
        elif isinstance(symbol_or_list, SymbolList):
            symbol_list: SymbolList = symbol_or_list
            # Concatenate the SymbolList into this SymbolList
            keys: List[str] = symbol_list.get_keys()
            for key in keys:
                self.add(key, symbol_list[key])
        else:
            raise SymbolListError("The 'add' command requires a string symbol, LogicSymbol, or a SymbolList")

    def set_value(self, symbol_name: str, value: Optional[Union[LogicValue, bool]]) -> None:
        """
        Sets the value of a specific symbol in the SymbolList indexed by the name of the symbol. (i.e. symbol_name: str)

        :param symbol_name: A string with the name of the symbol to set.
        :param value: The LogicValue or boolean value to set the symbol to.
        :return: None
        """
        symbol_name = symbol_name.upper()
        logic_value: LogicValue = _bool_to_logic_value(value)
        self._symbols[symbol_name] = logic_value

    def flip_value(self, symbol_name: str) -> None:
        """
        Flips value of symbol_name from LogicValue.TRUE to LogicValue.FALSE. Does nothing if LogicValue.UNDEFINED.

        :param symbol_name: A string with the name of the symbol to flip
        :return: None
        """
        current_value: LogicValue = self.get_value(symbol_name)
        if current_value == LogicValue.TRUE:
            self.set_value(symbol_name, LogicValue.FALSE)
        elif current_value == LogicValue.FALSE:
            self.set_value(symbol_name,  LogicValue.TRUE)

    def get_value(self, symbol_name: str) -> LogicValue:
        """
        Gets the LogicValue of the symbol with symbol_name (str).

        :param symbol_name: A string with the name of the symbol you want to get.
        :return: The LogicValue of this symbol. Returns UNDEFINED if it is not found rather than None.
        """
        if symbol_name is None:
            return LogicValue.UNDEFINED
        else:
            return self._symbols[symbol_name]

    def clone(self) -> SymbolList:
        """
        Makes a clone of this SymbolList.

        :return: A new SymbolList that clones the current (self) SymbolList.
        """
        return deepcopy(self)

    def extend_model(self, symbol_name: str, value: bool) -> SymbolList:
        """
        Like set_value except that it clones the model first and returns the clone
        thereby leaving the original unchanged.

        :param symbol_name: The name (str) of the symbol to extend.
        :param value: The LogicValue you want to set symbol (symbol_name) to.
        :return: Returns a new SymbolList that now has symbol_name (str) set to value (LogicValue).
        """
        copy_model: SymbolList = self.clone()
        copy_model.set_value(symbol_name, value)
        return copy_model
