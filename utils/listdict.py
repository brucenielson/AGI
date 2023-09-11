from __future__ import annotations
from typing import List, Union, Dict, TypeVar, Any, Type, get_origin, Tuple, Generic
import uuid
import copy

T = TypeVar('T')


class ListDictError(Exception):
    def __init__(self, message):
        super().__init__(message)


class ListDict:
    def __init__(self) -> None:
        # The __init__ method should save the type T being used for this ListDict.
        self._values: List[T] = []
        self._id_map: Dict[Union[uuid.UUID, str], int] = {}
        self._item_type: Type[T] = get_origin(T)

    def __getitem__(self, key: Union[uuid.UUID, str, int]) -> T:
        index: int
        if isinstance(key, (str, uuid.UUID)):
            try:
                index = self._id_map[key]
            except KeyError:
                raise KeyError(f"Key {key} not found")
        elif isinstance(key, int):
            if key < 0 or key >= len(self._values):
                raise KeyError(f'Index {key} out of range')
            index = key
        else:
            raise TypeError(f'Invalid key type: {type(key)}')

        return self.get_by_index(index)

    # implement __setitem__ but check that the right type is being set.
    def __setitem__(self, key: Union[uuid.UUID, str, int], value: T) -> None:
        if self._item_type is None:
            self._item_type = type(value)
        elif type(value) is not self._item_type:
            raise ListDictError(f'Invalid type for value: {type(value)}. Needs to be {self._item_type}')
        if isinstance(key, (uuid.UUID, str)):
            if key in self._id_map:
                index = self._id_map[key]
                self._values[index] = value
            else:
                self._values.append(value)
                self._id_map[key] = len(self._values) - 1
        elif isinstance(key, int):
            if key < 0 or key >= len(self._values):
                raise ListDictError(f'Index {key} out of range')
            self._values[key] = value

    def __delitem__(self, key: Union[uuid.UUID, str, int]) -> None:
        if isinstance(key, (uuid.UUID, str)):
            index = self._id_map[key]
        elif isinstance(key, int):
            index = key
            # Find the key for this value
            for k, i in self._id_map.items():
                if i == index:
                    key = k
                    break
        else:
            raise TypeError(f'Invalid key type: {type(key)}')
        del self._id_map[key]
        # Update the indexes in the id map
        for k, i in self._id_map.items():
            if i > index:
                self._id_map[k] = i - 1
        del self._values[index]

    def __contains__(self, key: T) -> bool:
        return key in self._values

    def __len__(self) -> int:
        return len(self._values)

    def __iter__(self) -> T:
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

    def get_by_index(self, index: int) -> T:
        if index < 0 or index >= len(self._values):
            raise ListDictError(f'Index {index} out of range')
        return self._values[index]

    def index(self, value: T) -> int:
        try:
            return self._values.index(value)
        except ValueError:
            raise ListDictError(f'Value {value} not found')

    def keys(self) -> List[uuid.UUID]:
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
            if self._values[i] != other._values[i]:
                return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def get(self, key: uuid.UUID, default: T = None) -> T:
        if key in self._id_map:
            return self[key]
        else:
            return default

    def values(self) -> List[T]:
        return self._values

    def items(self) -> List[Tuple[uuid.UUID, T]]:
        result: List[Tuple[uuid.UUID, T]] = []
        for key in self._id_map:
            result.append((key, self[key]))
        return result


class IterDict(Dict[Union[uuid.UUID, str, int], T], Generic[T]):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __iter__(self) -> T:
        return iter(self.values())

    def __reversed__(self) -> T:
        return reversed(self.values())

    def __getitem__(self, key: Union[uuid.UUID, str, int]) -> T:
        if isinstance(key, (uuid.UUID, str)):
            return self.get(key)
        elif isinstance(key, int):
            return self.get_by_index(key)
        else:
            raise TypeError(f'Invalid key type: {type(key)}')

    # implement __setitem__ but check that the right type is being set.
    def __setitem__(self, key: Union[uuid.UUID, str, int], value: T) -> None:
        super().__setitem__(key, value)

    def __delitem__(self, key: Union[uuid.UUID, str, int]) -> None:
        super().__delitem__(key)

    def __contains__(self, item_or_key: Union[T, uuid.UUID, str]) -> bool:
        if isinstance(item_or_key, int):
            return item_or_key in self.keys()
        elif isinstance(item_or_key, str):
            return item_or_key in self.keys()
        else:
            return item_or_key in self.values()

    def __len__(self) -> int:
        return len(self.keys())

    def filter(self, value: Any, attr_name: str = 'name', ) -> Union[List[T], T]:
        result = []
        for item in self.values():
            if getattr(item, attr_name) == value:
                result.append(item)
        if len(result) == 1:
            return result[0]
        else:
            return result

    def to_list(self) -> List[T]:
        return self.values()

    def get_by_index(self, index: Union[int, str]) -> T:
        if index < 0 or index >= len(self.values()):
            raise IndexError(f'Index {index} out of range')
        return self.values()[index]

    def index(self, value: T) -> int:
        return self.values().index(value)

    def keys(self) -> List[int]:
        return list(super().keys())

    def clear(self) -> None:
        super().clear()

    def __str__(self) -> str:
        return super().__str__()

    def __repr__(self) -> str:
        return super().__repr__()

    def __eq__(self, other):
        return self.values() == other.values()

    def __ne__(self, other):
        return self.values() != other.values()

    def get(self, key: Union[uuid.UUID, str, int], default: T = None) -> T:
        return super().get(key, default)

    def values(self) -> List[T]:
        return list(super().values())

    def items(self) -> List[Tuple[int, T]]:
        return list(super().items())

    def __copy__(self) -> IterDict[T]:
        return IterDict(self)

    def copy(self) -> IterDict[T]:
        return copy.deepcopy(IterDict(self))

    def update(self, other: Union[Dict[uuid.UUID, T], Dict[int, T], Dict[str, T], T, List[T]],
               **kwargs: Union[Dict[uuid.UUID, T], Dict[int, T], Dict[str, T], T, List[T]]) -> None:
        super().update(other, **kwargs)
