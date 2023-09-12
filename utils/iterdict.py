from __future__ import annotations
from typing import List, Union, Dict, TypeVar, Any, Tuple, Generic, Callable
import uuid
import copy

T = TypeVar('T')


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
