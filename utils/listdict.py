from __future__ import annotations
from typing import List, Union, Dict, TypeVar, Any, Type, get_origin, Tuple, Generic, Callable
import uuid
import copy

T = TypeVar('T')


class ListDictError(Exception):
    """
    Custom exception class for errors related to lists of dictionaries.

    This exception is raised when there is an issue with operations involving
    lists of dictionaries, such as indexing, manipulation, or iteration.
    """

    def __init__(self, message):
        """
        Initialize a new ListDictError instance.

        Args:
            message (str): A human-readable error message describing the issue.
        """
        super().__init__(message)


class ListDict:
    """
    A dictionary that can be indexed like a dictionary or list.
    """
    def __init__(self) -> None:
        """
        Initialize a new ListDict instance.

        The ListDict class allows storing values of a specific type T. This
        constructor initializes the ListDict with empty values and an optional
        item type (T).

        Args: None
        """
        # The __init__ method should save the type T being used for this ListDict.
        self._values: List[T] = []
        self._id_map: Dict[Union[uuid.UUID, str], int] = {}
        self._item_type: Type[T] = get_origin(T)

    def __getitem__(self, key: Union[uuid.UUID, str, int]) -> T:
        """
        Retrieve a value from the ListDict using a key or index.

        Args:
            key (Union[uuid.UUID, str, int]): The key (UUID, string) or index (int)
                to access the value.

        Returns:
            T: The value associated with the provided key or index.

        Raises:
            KeyError: If the key is not found in the ListDict or if the index is
                out of range.
            TypeError: If the key type is invalid.
        """
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
        """
        Set a value in the ListDict using a key or index.

        Args:
            key (Union[uuid.UUID, str, int]): The key (UUID, string) or index (int)
                to set the value.
            value (T): The value to set.

        Raises:
            ListDictError: If the value's type does not match the expected type for
                the ListDict or if there is an issue with the key type.
        """
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
        """
        Delete a value from the ListDict using a key or index.

        Args:
            key (Union[uuid.UUID, str, int]): The key (UUID, string) or index (int)
                of the value to delete.

        Raises:
            ListDictError: If there is an issue with the key type.
        """
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
        """
        Check if a value is present in the ListDict.

        Args:
            key (T): The value to check for in the ListDict.

        Returns:
            bool: True if the value is found, False otherwise.
        """
        return key in self._values

    def __len__(self) -> int:
        """
        Get the number of values in the ListDict.

        Returns:
            int: The number of values in the ListDict.
        """
        return len(self._values)

    def __iter__(self) -> T:
        """
        Create an iterator for the ListDict.

        Returns:
            T: An iterator for the values in the ListDict.
        """
        return iter(self._values)

    def filter(self, value: Any, attr_name: str = 'name', ) -> Union[List[T], T]:
        """
        Filter values in the ListDict based on a specific attribute.

        Args:
            value (Any): The value to filter by.
            attr_name (str): The name of the attribute to compare (default is 'name').

        Returns:
            Union[List[T], T]: A list of matching values or a single matching value.
        """
        result: List[T] = []
        for item in self._values:
            if hasattr(item, attr_name) and getattr(item, attr_name) == value:
                result.append(item)
            elif isinstance(item, dict) and attr_name in item and item[attr_name] == value:
                result.append(item)
        return result

    def to_list(self):
        """
        Convert the ListDict to a list.

        Returns:
            List[T]: A list containing all values in the ListDict.
        """
        result: List[T] = []
        for item in self._values:
            result.append(item)
        return result

    def get_by_index(self, index: int) -> T:
        """
        Get a value from the ListDict by index.

        Args:
            index (int): The index of the value to retrieve.

        Returns:
            T: The value at the specified index.

        Raises:
            ListDictError: If the index is out of range.
        """
        if index < 0 or index >= len(self._values):
            raise ListDictError(f'Index {index} out of range')
        return self._values[index]

    def index(self, value: T) -> int:
        """
        Get the index of a value in the ListDict.

        Args:
            value (T): The value to find the index of.

        Returns:
            int: The index of the value.

        Raises:
            ListDictError: If the value is not found in the ListDict.
        """
        try:
            return self._values.index(value)
        except ValueError:
            raise ListDictError(f'Value {value} not found')

    def keys(self) -> List[uuid.UUID]:
        """
        Get the keys (UUIDs) in the ListDict.

        Returns:
            List[uuid.UUID]: A list of keys (UUIDs).
        """
        return list(self._id_map.keys())

    def clear(self):
        """
        Clear all values and keys in the ListDict.
        """
        self._values = []
        self._id_map = {}

    def __str__(self):
        """
        Return a string representation of the ListDict.

        Returns:
            str: A string representation of the ListDict.
        """
        return str(self._values)

    def __repr__(self):
        """
        Return a string representation of the ListDict.

        Returns:
            str: A string representation of the ListDict.
        """
        return str(self._values)

    def __eq__(self, other):
        """
        Check if two ListDict instances are equal.

        Args:
            other: The other ListDict instance to compare.

        Returns:
            bool: True if the two ListDict instances are equal, False otherwise.
        """
        if not isinstance(other, ListDict):
            return False
        if len(self) != len(other):
            return False
        for i in range(len(self)):
            if self._values[i] != other._values[i]:
                return False
        return True

    def __ne__(self, other):
        """
        Check if two ListDict instances are not equal.

        Args:
            other: The other ListDict instance to compare.

        Returns:
            bool: True if the two ListDict instances are not equal, False otherwise.
        """
        return not self.__eq__(other)

    def get(self, key: uuid.UUID, default: T = None) -> T:
        """
        Get a value from the ListDict by key, with an optional default value.

        Args:
            key (uuid.UUID): The key (UUID) to look up.
            default (T, optional): The default value to return if the key is not found.

        Returns:
            T: The value associated with the key or the default value if the key is not found.
        """
        if key in self._id_map:
            return self[key]
        else:
            return default

    def values(self) -> List[T]:
        """
        Get all values in the ListDict.

        Returns:
            List[T]: A list of all values in the ListDict.
        """
        return self._values

    def items(self) -> List[Tuple[uuid.UUID, T]]:
        """
        Get all key-value pairs as a list of tuples.

        Returns:
            List[Tuple[uuid.UUID, T]]: A list of key-value pairs as tuples.
        """
        result: List[Tuple[uuid.UUID, T]] = []
        for key in self._id_map:
            result.append((key, self[key]))
        return result


class IterDict(Dict[Union[uuid.UUID, str, int], T], Generic[T]):
    """
    A dictionary that supports iteration and additional utility methods.

    This class extends the functionality of a standard Python dictionary by
    adding methods for iteration, filtering, copying, and more.

    Args:
        *args: Variable-length arguments passed to the superclass constructor.
        **kwargs: Keyword arguments passed to the superclass constructor.

    Attributes: None
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __iter__(self) -> T:
        """
        Return an iterator for the values in the IterDict.

        Returns:
            T: An iterator for the values in the IterDict.
        """
        return iter(self.values())

    def __reversed__(self) -> T:
        """
        Return a reversed iterator for the values in the IterDict.

        Returns:
            T: A reversed iterator for the values in the IterDict.
        """
        return reversed(self.values())

    def __getitem__(self, key: Union[uuid.UUID, str, int]) -> T:
        """
        Get a value from the IterDict by key or index.

        Args:
            key (Union[uuid.UUID, str, int]): The key (UUID, string) or index (int) to access the value.

        Returns:
            T: The value associated with the provided key or index.

        Raises:
            TypeError: If the key type is invalid.
        """
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
        """
        Check if an item or key exists in the IterDict.

        Args:
            item_or_key (Union[T, uuid.UUID, str]): The item, key (UUID, string), or index (int) to check.

        Returns:
            bool: True if the item or key exists, False otherwise.
        """
        if isinstance(item_or_key, int):
            return item_or_key in self.keys()
        elif isinstance(item_or_key, str):
            return item_or_key in self.keys()
        else:
            return item_or_key in self.values()

    def __len__(self) -> int:
        """
        Get the number of items in the IterDict.

        Returns:
            int: The number of items in the IterDict.
        """
        return len(self.keys())

    def filter(self, value: Any, attr_name: str = 'name', ) -> Union[List[T], T]:
        """
        Filter values in the IterDict based on a specific attribute.

        Args:
            value (Any): The value to filter by.
            attr_name (str, optional): The name of the attribute to compare (default is 'name').

        Returns:
            Union[List[T], T]: A list of matching values or a single matching value.
        """
        result = []
        for item in self.values():
            if getattr(item, attr_name) == value:
                result.append(item)
        if len(result) == 1:
            return result[0]
        else:
            return result

    def to_list(self) -> List[T]:
        """
        Convert the IterDict to a list.

        Returns:
            List[T]: A list containing all values in the IterDict.
        """
        return self.values()

    def get_by_index(self, index: Union[int, str]) -> T:
        """
        Get a value from the IterDict by index.

        Args:
            index (Union[int, str]): The index or string key to access the value.

        Returns:
            T: The value at the specified index.

        Raises:
            IndexError: If the index is out of range.
        """
        if index < 0 or index >= len(self.values()):
            raise IndexError(f'Index {index} out of range')
        return self.values()[index]

    def index(self, value: T) -> int:
        """
        Get the index of a value in the IterDict.

        Args:
            value (T): The value to find the index of.

        Returns:
            int: The index of the value.

        Raises:
            ValueError: If the value is not found in the IterDict.
        """
        return self.values().index(value)

    def keys(self) -> List[int]:
        """
        Get the keys (UUIDs, strings, or integers) in the IterDict as a list.

        Returns:
            List[int]: A list of keys (UUIDs, strings, or integers).
        """
        return list(super().keys())

    def clear(self) -> None:
        """
        Clear all items and keys in the IterDict.
        """
        super().clear()

    def __str__(self) -> str:
        """
        Return a string representation of the IterDict.

        Returns:
            str: A string representation of the IterDict.
        """
        return super().__str__()

    def __repr__(self) -> str:
        """
        Return a string representation of the IterDict.

        Returns:
            str: A string representation of the IterDict.
        """
        return super().__repr__()

    def __eq__(self, other):
        """
        Check if two IterDict instances are equal based on their values.

        Args:
            other: The other IterDict instance to compare.

        Returns:
            bool: True if the two IterDict instances have equal values, False otherwise.
        """
        return self.values() == other.values()

    def __ne__(self, other):
        """
        Check if two IterDict instances are not equal based on their values.

        Args:
            other: The other IterDict instance to compare.

        Returns:
            bool: True if the two IterDict instances have unequal values, False otherwise.
        """
        return self.values() != other.values()

    def get(self, key: Union[uuid.UUID, str, int], default: T = None) -> T:
        """
        Get a value from the IterDict by key, with an optional default value.

        Args:
            key (Union[uuid.UUID, str, int]): The key (UUID, string, or integer) to look up.
            default (T, optional): The default value to return if the key is not found.

        Returns:
            T: The value associated with the key or the default value if the key is not found.
        """
        return super().get(key, default)

    def get_by_name(self, name: str, default: T = None) -> T:
        """
        Get a value from the IterDict by name, with an optional default value.

        Args:
            name (str): The name to look up.
            default (T, optional): The default value to return if the name is not found.

        Returns:
            T: The value associated with the name or the default value if the name is not found.
        """
        for item in self.values():
            if item.name == name:
                return item
        return default

    def values(self) -> List[T]:
        """
        Get all values in the IterDict as a list.

        Returns:
            List[T]: A list of all values in the IterDict.
        """
        return list(super().values())

    def items(self) -> List[Tuple[int, T]]:
        """
        Get all key-value pairs in the IterDict as a list of tuples.

        Returns:
            List[Tuple[int, T]]: A list of key-value pairs as tuples.
        """
        return list(super().items())

    def __copy__(self) -> 'IterDict[T]':
        """
        Create a shallow copy of the IterDict.

        Returns:
            IterDict[T]: A shallow copy of the IterDict.
        """
        return IterDict(self)

    def copy(self) -> 'IterDict[T]':
        """
        Create a deep copy of the IterDict.

        Returns:
            IterDict[T]: A deep copy of the IterDict.
        """
        return copy.deepcopy(IterDict(self))

    def update(self, other: Union[Dict[uuid.UUID, T], Dict[int, T], Dict[str, T], T, List[T]],
               **kwargs: Union[Dict[uuid.UUID, T], Dict[int, T], Dict[str, T], T, List[T]]) -> None:
        """
        Update the IterDict with values from another dictionary or keyword arguments.

        Args:
            other (Union[Dict[uuid.UUID, T], Dict[int, T], Dict[str, T], T, List[T]]): The dictionary or iterable to
                update from.
            **kwargs (Union[Dict[uuid.UUID, T], Dict[int, T], Dict[str, T], T, List[T]]): Additional keyword arguments
                for updating the IterDict.
        """
        super().update(other, **kwargs)

    def sort(self, key: Callable[[T], Any] = None, reverse: bool = False) -> None:
        """
        Sort the values in the IterDict in-place.

        Args:
            key (Callable[[T], Any], optional): A function to extract a comparison key from each element.
            reverse (bool, optional): If True, sort the values in descending order; otherwise, in ascending order.
        """
        self.values().sort(key=key, reverse=reverse)
