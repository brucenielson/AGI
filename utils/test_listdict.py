from unittest import TestCase
from utils.listdict import ListDict, ListDictError, IterDict
import uuid


class ComboListDictTestCase(TestCase):
    def setUp(self):
        # Generate 4 uuids in a List
        self.uuids = [uuid.uuid4() for _ in range(4)]
        self.dict: ListDict[dict] = ListDict()
        self.dict[self.uuids[0]] = {'name': 'John', 'age': 30}
        self.dict[self.uuids[1]] = {'name': 'Alice', 'age': 25}
        self.dict[self.uuids[2]] = {'name': 'Bob', 'age': 40}
        self.dict[self.uuids[3]] = {'age': 20}
        self.not_in = {'name': 'Bob', 'age': 44}

    def test_getitem(self):
        self.assertEqual(self.dict[self.uuids[0]], {'name': 'John', 'age': 30})
        self.assertEqual(self.dict[self.uuids[1]], {'name': 'Alice', 'age': 25})
        self.assertEqual(self.dict[self.uuids[2]], {'name': 'Bob', 'age': 40})
        self.assertEqual(self.dict[self.uuids[3]], {'age': 20})
        self.assertEqual(self.dict[0], {'name': 'John', 'age': 30})
        self.assertEqual(self.dict[1], {'name': 'Alice', 'age': 25})
        self.assertEqual(self.dict[2], {'name': 'Bob', 'age': 40})
        self.assertEqual(self.dict[3], {'age': 20})

        self.assertRaises(KeyError, self.dict.__getitem__, 5)
        self.assertRaises(KeyError, self.dict.__getitem__, -1)

    def test_setitem(self):
        self.dict[self.uuids[0]] = {'name': 'Mary', 'age': 35}
        self.assertEqual(self.dict[self.uuids[0]], {'name': 'Mary', 'age': 35})
        self.assertEqual(len(self.dict), 4)
        self.dict[0] = {'name': 'Judy', 'age': 29}
        self.assertEqual(self.dict[0], {'name': 'Judy', 'age': 29})
        self.assertEqual(len(self.dict), 4)

    def test_delitem(self):
        del self.dict[self.uuids[0]]
        self.assertNotIn(self.uuids[0], self.dict._id_map)
        self.assertNotIn({'name': 'John', 'age': 30}, self.dict)
        self.assertEqual(len(self.dict), 3)
        self.assertNotIn(self.uuids[0], self.dict._id_map)
        del self.dict[0]
        self.assertEqual(len(self.dict), 2)
        self.assertNotIn(self.uuids[1], self.dict._id_map)
        self.assertIn(self.uuids[2], self.dict._id_map)
        self.assertIn(self.uuids[3], self.dict._id_map)

    def test_contains(self):
        self.assertTrue(self.dict[self.uuids[0]] in self.dict)
        self.assertTrue(self.dict[self.uuids[2]] in self.dict)
        self.assertFalse(self.not_in in self.dict)

    def test_len(self):
        self.assertEqual(len(self.dict), 4)

    def test_iter(self):
        result = []
        for item in self.dict:
            result.append(item)
        self.assertEqual(result, [{'name': 'John', 'age': 30}, {'name': 'Alice', 'age': 25},
                                  {'name': 'Bob', 'age': 40}, {'age': 20}])

    def test_to_list(self):
        self.assertEqual(self.dict.to_list(), [{'name': 'John', 'age': 30}, {'name': 'Alice', 'age': 25},
                                               {'name': 'Bob', 'age': 40}, {'age': 20}])

    def test_filter(self):
        self.assertEqual(self.dict.filter('John', attr_name='name')[0], self.dict[self.uuids[0]])
        self.assertEqual(self.dict.filter(20, attr_name='age'), [{'age': 20}])
        self.assertEqual(self.dict.filter('David', attr_name='name'), [])

    def test_get_by_index(self):
        self.assertEqual(self.dict.get_by_index(0), {'name': 'John', 'age': 30})
        self.assertEqual(self.dict.get_by_index(1), {'name': 'Alice', 'age': 25})
        self.assertEqual(self.dict.get_by_index(2), {'name': 'Bob', 'age': 40})
        self.assertEqual(self.dict.get_by_index(3), {'age': 20})
        self.assertRaises(ListDictError, self.dict.get_by_index, 4)

    def test_clear(self):
        self.dict.clear()
        self.assertEqual(len(self.dict), 0)

    def test_str(self) -> None:
        self.assertEqual(str(self.dict),
                         "[{'name': 'John', 'age': 30}, {'name': 'Alice', 'age': 25}, {'name': 'Bob', 'age': 40}, "
                         "{'age': 20}]")

    def test_repr(self) -> None:
        self.assertEqual(repr(self.dict),
                         "[{'name': 'John', 'age': 30}, {'name': 'Alice', 'age': 25}, {'name': 'Bob', 'age': 40}, "
                         "{'age': 20}]")

    def test_eq(self):
        list_dict1 = ListDict()
        list_dict1[uuid.uuid4()] = 1
        list_dict1[uuid.uuid4()] = 2
        list_dict1[uuid.uuid4()] = 3

        list_dict2 = ListDict()
        list_dict2[uuid.uuid4()] = 1
        list_dict2[uuid.uuid4()] = 2
        list_dict2[uuid.uuid4()] = 3

        list_dict3 = ListDict()
        list_dict3[uuid.uuid4()] = 1
        list_dict3[uuid.uuid4()] = 2

        self.assertTrue(list_dict1 == list_dict2)
        self.assertFalse(list_dict1 == list_dict3)
        self.assertFalse(list_dict1 == "not a ListDict")

    def test_ne_returns_false_if_same(self):
        ld1 = ListDict()
        ld1[uuid.uuid4()] = 'foo'
        ld2 = ListDict()
        ld2[uuid.uuid4()] = 'foo'
        self.assertFalse(ld1 != ld2)

    def test_ne_returns_true_if_different(self):
        ld1 = ListDict()
        ld1[uuid.uuid4()] = 'foo'
        ld2 = ListDict()
        ld2[uuid.uuid4()] = 'bar'
        self.assertTrue(ld1 != ld2)

    def test_values(self):
        ld = ListDict()
        ld[uuid.uuid4()] = "one"
        ld[uuid.uuid4()] = "two"
        ld[uuid.uuid4()] = "three"
        self.assertEqual(ld.values(), ["one", "two", "three"])

    def test_items(self):
        lst_dict = ListDict()
        lst_dict[self.uuids[0]] = "hello"
        lst_dict[self.uuids[1]] = "world"
        lst_dict[self.uuids[2]] = "python"
        items = lst_dict.items()
        self.assertIsInstance(items, list)
        self.assertEqual(len(items), 3)
        self.assertEqual(items[0], (self.uuids[0], "hello"))
        self.assertEqual(items[1], (self.uuids[1], "world"))
        self.assertEqual(items[2], (self.uuids[2], "python"))

    def test_index(self):
        # Test indexing a value that exists in the ListDict
        self.assertEqual(self.dict.index({'name': 'Alice', 'age': 25}), 1)

        # Test indexing a value that does not exist in the ListDict
        with self.assertRaises(ListDictError):
            self.dict.index({'name': 'David', 'age': 30})

    def test_keys(self):
        # Test getting keys from a non-empty ListDict
        keys = self.dict.keys()
        self.assertIsInstance(keys, list)
        self.assertEqual(len(keys), len(self.dict))
        for key in keys:
            self.assertIsInstance(key, uuid.UUID)
            self.assertIn(key, self.dict._id_map)

        # Test getting keys from an empty ListDict
        empty_dict = ListDict()
        self.assertEqual(empty_dict.keys(), [])

    def test_clear_advanced(self):
        # Test clearing a non-empty ListDict
        initial_length = len(self.dict)
        self.dict.clear()
        self.assertEqual(len(self.dict), 0)
        self.assertEqual(len(self.dict._values), 0)
        self.assertEqual(len(self.dict._id_map), 0)

        # Test clearing an already empty ListDict
        empty_dict = ListDict()
        empty_dict.clear()
        self.assertEqual(len(empty_dict), 0)
        self.assertEqual(len(empty_dict._values), 0)
        self.assertEqual(len(empty_dict._id_map), 0)


class AdditionalListDictTestCase(TestCase):
    def setUp(self):
        self.dict = ListDict()
        self.uuid1 = uuid.uuid4()
        self.uuid2 = uuid.uuid4()
        self.uuid3 = uuid.uuid4()
        self.uuid4 = uuid.uuid4()
        self.dict[self.uuid1] = {'name': 'John', 'age': 30}

    def test_getitem_nonexistent_key(self):
        with self.assertRaises(KeyError):
            _ = self.dict[self.uuid2]  # Accessing a key that does not exist should raise KeyError

    def test_delitem_nonexistent_key(self):
        with self.assertRaises(KeyError):
            del self.dict[self.uuid2]  # Deleting a key that does not exist should raise KeyError

    def test_setitem_existing_key(self):
        self.dict[self.uuid1] = {'name': 'Mary', 'age': 35}
        self.assertEqual(self.dict[self.uuid1], {'name': 'Mary', 'age': 35})  # Existing item should be updated

    def test_setitem_duplicate_key(self):
        # Setting over an existing key should overwrite the existing item
        self.dict[self.uuid1] = {'name': 'David', 'age': 28}
        self.assertEqual(self.dict[self.uuid1], {'name': 'David', 'age': 28})  # Original item should remain

    def test_setitem_different_data_type(self):
        with self.assertRaises(ListDictError):
            self.dict[self.uuid1] = 42  # Setting a different data type should raise ListDictError


class TestIterDict(TestCase):
    def test_iteration(self):
        d = IterDict({'a': 1, 'b': 2, 'c': 3})
        items = list(iter(d))
        self.assertCountEqual(items, [1, 2, 3])

    def test_access(self):
        d = IterDict({'a': 1, 'b': 2, 'c': 3})
        self.assertEqual(d['a'], 1)
        self.assertEqual(d['b'], 2)
        self.assertEqual(d['c'], 3)

    def test_assignment(self):
        d = IterDict({'a': 1, 'b': 2, 'c': 3})
        d['d'] = 4
        self.assertEqual(d['d'], 4)

    def test_deletion(self):
        d = IterDict({'a': 1, 'b': 2, 'c': 3})
        del d['b']
        self.assertNotIn('b', d)
        self.assertEqual(len(d), 2)

    def setUp(self):
        self.d = IterDict({'a': 1, 'b': 2, 'c': 3})

    def test_iter(self):
        expected_items = [('a', 1), ('b', 2), ('c', 3)]
        for i, item in enumerate(iter(self.d)):
            self.assertEqual(item, expected_items[i][1])

    def test_reversed(self):
        expected_items = [('c', 3), ('b', 2), ('a', 1)]
        for i, item in enumerate(reversed(self.d)):
            self.assertEqual(item, expected_items[i][1])

    def test_str(self):
        self.assertEqual(str(self.d), "{'a': 1, 'b': 2, 'c': 3}")

    def test_repr(self):
        self.assertEqual(repr(self.d), "{'a': 1, 'b': 2, 'c': 3}")

    def test_eq(self):
        self.assertEqual(self.d, IterDict({'a': 1, 'b': 2, 'c': 3}))

    def test_ne(self):
        self.assertNotEqual(self.d, IterDict({'a': 1, 'b': 2}))

    def test_keys(self):
        self.assertEqual(self.d.keys(), ['a', 'b', 'c'])

    def test_values(self):
        self.assertEqual(self.d.values(), [1, 2, 3])

    def test_items(self):
        self.assertEqual(self.d.items(), [('a', 1), ('b', 2), ('c', 3)])

    def test_get(self):
        self.assertEqual(self.d.get('a'), 1)
        self.assertEqual(self.d.get('d'), None)
        self.assertEqual(self.d.get('d', 'default'), 'default')

    def test_update_dict(self):
        self.d.update({'d': 4})
        self.assertEqual(self.d, IterDict({'a': 1, 'b': 2, 'c': 3, 'd': 4}))

    def test_update_list(self):
        self.d.update([('d', 4)])
        self.assertEqual(self.d, IterDict({'a': 1, 'b': 2, 'c': 3, 'd': 4}))

    def test_update_list_missing_id(self):
        with self.assertRaises(ValueError):
            self.d.update([('d', 4, 5)])

    def test_update_other_type(self):
        with self.assertRaises(TypeError):
            # noinspection PyTypeChecker
            self.d.update(123)

    def test_copy(self):
        d_copy = self.d.copy()
        self.assertEqual(self.d, d_copy)
        self.assertIsNot(self.d, d_copy)

    def test_setdefault(self):
        d = IterDict(a=1, b=2, c=3)
        # test setting a default value
        self.assertEqual(d.setdefault('d', 4), 4)
        self.assertEqual(d['d'], 4)
        # test getting an existing value
        self.assertEqual(d.setdefault('a', 0), 1)
        self.assertEqual(d['a'], 1)

    def test_clear(self):
        d = IterDict(a=1, b=2, c=3)
        d.clear()
        self.assertEqual(len(d), 0)

    def test_contains(self):
        d = IterDict({'a': 1, 'b': 2, 'c': 3})
        self.assertTrue('a' in d)
        self.assertFalse('d' in d)

    def test_get_by_index(self):
        d = IterDict({'a': 1, 'b': 2, 'c': 3})
        self.assertEqual(d.get_by_index(0), 1)
        self.assertEqual(d.get_by_index(2), 3)
        with self.assertRaises(IndexError):
            _ = d.get_by_index(3)  # Accessing an out-of-range index should raise IndexError

    def test_index(self):
        d = IterDict({'a': 1, 'b': 2, 'c': 3})
        self.assertEqual(d.index(1), 0)
        self.assertEqual(d.index(3), 2)
        with self.assertRaises(ValueError):
            _ = d.index(4)  # Accessing a value that does not exist should raise ValueError

    def test_update_with_kwargs(self):
        d = IterDict({'a': 1, 'b': 2, 'c': 3})
        d.update({'d': 4, 'e': 5})
        self.assertEqual(d, IterDict({'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5}))

    def test_setdefault_2(self):
        d = IterDict({'a': 1, 'b': 2, 'c': 3})
        self.assertEqual(d.setdefault('d', 4), 4)
        self.assertEqual(d['d'], 4)
        self.assertEqual(d.setdefault('a', 0), 1)
        self.assertEqual(d['a'], 1)

    def test_copy_method(self):
        d = IterDict({'a': {'x': 1}, 'b': {'y': 2}})
        d_copy = d.copy()
        self.assertEqual(d, d_copy)
        self.assertIsNot(d, d_copy)  # Ensure it's a deep copy
        self.assertIsNot(d['a'], d_copy['a'])  # Ensure nested dictionaries are also deep copied
