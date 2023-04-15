from __future__ import annotations
from typing import List, Union, Dict, TypeVar, Any, Type, get_origin, Tuple

T = TypeVar('T')


class ListDictError(Exception):
    def __init__(self, message):
        super().__init__(message)


class ListDict:
    def __init__(self) -> None:
        # The __init__ method should save the type T being used for this ListDict.
        self._values: List[T] = []
        self._id_map: Dict[Union[int, str], int] = {}
        self._item_type: Type[T] = get_origin(T)

    def __getitem__(self, key: int) -> T:
        try:
            index = self._id_map[key]
        except KeyError:
            raise KeyError(f"Key {key} not found")
        return self._values[index]

    # implement __setitem__ but check that the right type is being set.
    def __setitem__(self, key: int, value: T) -> None:
        if self._item_type is None:
            self._item_type = type(value)
        elif type(value) is not self._item_type:
            raise ListDictError(f'Invalid type for value: {type(value)}. Needs to be {self._item_type}')
        if key in self._id_map:
            index = self._id_map[key]
            self._values[index] = value
        else:
            self._values.append(value)
            self._id_map[key] = len(self._values) - 1

    def __delitem__(self, key: int) -> None:
        index = self._id_map[key]
        del self._id_map[key]
        del self._values[index]

    def __contains__(self, key: T) -> bool:
        return key in self._values

    def __len__(self) -> int:
        return len(self._values)

    def __iter__(self):
        return iter(self._values)

    def filter(self, value: Any, attr_name: str = 'name', ) -> Union[List[T], T]:
        result: List[T] = []
        for item in self._values:
            if hasattr(item, attr_name) and getattr(item, attr_name) == value:
                result.append(item)
            elif isinstance(item, dict) and attr_name in item and item[attr_name] == value:
                result.append(item)
        return result

    def to_list(self):
        result: List[T] = []
        for item in self._values:
            result.append(item)
        return result

    def index(self, index: int) -> T:
        if index < 0 or index >= len(self._values):
            raise ListDictError(f'Index {index} out of range')
        return self._values[index]

    def index_by_value(self, value: T) -> int:
        for key in self.keys():
            if self[key] == value:
                return key
        raise ListDictError(f'Value {value} not found')

    def keys(self) -> List[int]:
        return list(self._id_map.keys())

    def clear(self):
        self._values = []
        self._id_map = {}

    def __str__(self):
        return str(self._values)

    def __repr__(self):
        return str(self._values)

    def __eq__(self, other):
        if not isinstance(other, ListDict):
            return False
        if len(self) != len(other):
            return False
        for i in range(len(self)):
            if self[i] != other[i]:
                return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def get(self, key: int, default: T = None) -> T:
        if key in self._id_map:
            return self[key]
        else:
            return default

    def values(self) -> List[T]:
        return self._values

    def items(self) -> List[Tuple[int, T]]:
        result: List[Tuple[int, T]] = []
        for key in self._id_map:
            result.append((key, self[key]))
        return result

    # def pop(self, key: int, default: T = None) -> T:
    #     if key in self._id_map:
    #         index = self._id_map[key]
    #         del self._id_map[key]
    #         return self._values.pop(index)
    #     else:
    #         return default
    #
    # # pop last item
    # def popitem(self, default: T = None) -> T:
    #     if not self._values:
    #         return default
    #     key = list(self._id_map.keys())[-1]
    #     return self.pop(key, default)

    # def update(self, other: Union[ListDict[T], List[Dict[str, Any]]]):
    #     if isinstance(other, ListDict):
    #         for key in other.keys():
    #             self[key] = other[key]
    #     elif isinstance(other, list):
    #         for item in other:
    #             if 'id' in item:
    #                 self[item['id']] = item
    #             else:
    #                 raise KeyError('Missing "id" key in item')
    #     else:
    #         raise TypeError('Unsupported type for "other" argument')
    #
    # def copy(self) -> ListDict[T]:
    #     result = ListDict()
    #     result.update(self)
    #     return result
    #
    # def append(self, value: T):
    #     self[len(self)] = value
    #
    # def extend(self, other: Union[ListDict[T], List[Dict[str, Any]]]):
    #     if isinstance(other, ListDict):
    #         for value in other:
    #             self.append(value)
    #     else:
    #         for value in other:
    #             self.append(value)
    #
    # def insert(self, index: int, value: T):
    #     if index < 0 or index >= len(self):
    #         raise ListDictError(f'Index {index} out of range')
    #     self[len(self)] = self[index]
    #     self[index] = value
    #
    # def remove(self, value: T):
    #     for key in self.keys():
    #         if self[key] == value:
    #             del self[key]
    #             return
    #     raise ListDictError(f'Value {value} not found')
    #
    # def reverse(self):
    #     self._values.reverse()
    #     self._id_map = {self._id_map[key]: key for key in self._id_map}
    #
    # def sort(self, key=None, reverse=False):
    #     self._values.sort(key=key, reverse=reverse)
    #     self._id_map = {self._id_map[key]: key for key in self._id_map}
    #
    # def count(self, value: T) -> int:
    #     result = 0
    #     for item in self._values:
    #         if item == value:
    #             result += 1
    #     return result
    #
    # def __add__(self, other: ListDict[T]) -> ListDict[T]:
    #     result = self.copy()
    #     result.extend(other)
    #     return result
    #
    # def __iadd__(self, other: ListDict[T]) -> ListDict[T]:
    #     self.extend(other)
    #     return self
    #
    # def __mul__(self, other: int) -> ListDict[T]:
    #     result = self.copy()
    #     for i in range(other - 1):
    #         result.extend(self)
    #     return result
    #
    # def __imul__(self, other: int) -> ListDict[T]:
    #     for i in range(other - 1):
    #         self.extend(self)
    #     return self
