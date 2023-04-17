from unittest import TestCase
from utils.listdict import ListDict, ListDictError, IterDict


class ComboListDictTestCase(TestCase):
    def setUp(self):
        self.dict: ListDict[dict] = ListDict()
        self.dict[1] = {'name': 'John', 'age': 30}
        self.dict[2] = {'name': 'Alice', 'age': 25}
        self.dict[3] = {'name': 'Bob', 'age': 40}
        self.dict[4] = {'age': 20}
        self.not_in = {'name': 'Bob', 'age': 44}

    def test_getitem(self):
        self.assertEqual(self.dict[1], {'name': 'John', 'age': 30})
        self.assertEqual(self.dict[2], {'name': 'Alice', 'age': 25})
        self.assertEqual(self.dict[3], {'name': 'Bob', 'age': 40})
        self.assertEqual(self.dict[4], {'age': 20})
        self.assertRaises(KeyError, self.dict.__getitem__, 5)
        self.assertRaises(KeyError, self.dict.__getitem__, 0)

    def test_setitem(self):
        self.dict[1] = {'name': 'Mary', 'age': 35}
        self.assertEqual(self.dict[1], {'name': 'Mary', 'age': 35})
        self.assertEqual(len(self.dict), 4)

    def test_delitem(self):
        del self.dict[1]
        self.assertNotIn(1, self.dict._id_map)
        self.assertNotIn({'name': 'John', 'age': 30}, self.dict)
        self.assertEqual(len(self.dict), 3)

    def test_contains(self):
        self.assertTrue(self.dict[1] in self.dict)
        self.assertTrue(self.dict[3] in self.dict)
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
        self.assertEqual(self.dict.filter('John', attr_name='name')[0], self.dict[1])
        self.assertEqual(self.dict.filter(20, attr_name='age'), [{'age': 20}])
        self.assertEqual(self.dict.filter('David', attr_name='name'), [])

    def test_index(self):
        self.assertEqual(self.dict.index(0), {'name': 'John', 'age': 30})
        self.assertEqual(self.dict.index(1), {'name': 'Alice', 'age': 25})
        self.assertEqual(self.dict.index(2), {'name': 'Bob', 'age': 40})
        self.assertEqual(self.dict.index(3), {'age': 20})
        self.assertRaises(ListDictError, self.dict.index, 4)

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
        list_dict1[0] = 1
        list_dict1[1] = 2
        list_dict1[2] = 3

        list_dict2 = ListDict()
        list_dict2[0] = 1
        list_dict2[1] = 2
        list_dict2[2] = 3

        list_dict3 = ListDict()
        list_dict3[0] = 1
        list_dict3[1] = 2

        self.assertTrue(list_dict1 == list_dict2)
        self.assertFalse(list_dict1 == list_dict3)
        self.assertFalse(list_dict1 == "not a ListDict")

    def test_ne_returns_false_if_same(self):
        ld1 = ListDict()
        ld1[0] = 'foo'
        ld2 = ListDict()
        ld2[0] = 'foo'
        self.assertFalse(ld1 != ld2)

    def test_ne_returns_true_if_different(self):
        ld1 = ListDict()
        ld1[0] = 'foo'
        ld2 = ListDict()
        ld2[0] = 'bar'
        self.assertTrue(ld1 != ld2)

    def test_values(self):
        ld = ListDict()
        ld[1] = "one"
        ld[2] = "two"
        ld[3] = "three"
        self.assertEqual(ld.values(), ["one", "two", "three"])

    def test_items(self):
        lst_dict = ListDict()
        lst_dict[1] = "hello"
        lst_dict[2] = "world"
        lst_dict[3] = "python"
        items = lst_dict.items()
        self.assertIsInstance(items, list)
        self.assertEqual(len(items), 3)
        self.assertEqual(items[0], (1, "hello"))
        self.assertEqual(items[1], (2, "world"))
        self.assertEqual(items[2], (3, "python"))


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
