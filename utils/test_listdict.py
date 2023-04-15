from unittest import TestCase
from utils.listdict import ListDict, ListDictError


class ComboListDictTestCase(TestCase):
    def setUp(self):
        self.dict = ListDict()
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

    def test_values(self):
        self.assertEqual(self.dict.to_list(), [{'name': 'John', 'age': 30}, {'name': 'Alice', 'age': 25},
                                               {'name': 'Bob', 'age': 40}, {'age': 20}])

    def test_filter(self):
        self.assertEqual(self.dict.filter('John', attr_name='name')[0], self.dict[1])
        self.assertEqual(self.dict.filter(20, attr_name='age'), [{'age': 20}])
        self.assertEqual(self.dict.filter('David', attr_name='name'), [])

    def test_to_list(self):
        self.assertEqual(self.dict.to_list(), [{'name': 'John', 'age': 30}, {'name': 'Alice', 'age': 25},
                                               {'name': 'Bob', 'age': 40}, {'age': 20}])

    def test_index(self):
        self.assertEqual(self.dict.index(0), {'name': 'John', 'age': 30})
        self.assertEqual(self.dict.index(1), {'name': 'Alice', 'age': 25})
        self.assertEqual(self.dict.index(2), {'name': 'Bob', 'age': 40})
        self.assertEqual(self.dict.index(3), {'age': 20})
        self.assertRaises(ListDictError, self.dict.index, 4)

    def test_clear(self):
        self.dict.clear()
        self.assertEqual(len(self.dict), 0)

    # def test_get(self):
    #     self.assertEqual(self.dict.get(1), {'name': 'John', 'age': 30})
    #     self.assertEqual(self.dict.get(4), {'age': 20})
    #     self.assertEqual(self.dict.get(5), None)
    #     self.assertEqual(self.dict.get(5, default={'name': 'Bob', 'age': 44}), {'name': 'Bob', 'age': 44})
    #
    # def test_pop(self):
    #     self.assertEqual(self.dict.pop(1), {'name': 'John', 'age': 30})
    #     self.assertEqual(len(self.dict), 3)
    #     self.assertEqual(self.dict.pop(4), {'age': 20})
    #     self.assertEqual(len(self.dict), 2)
    #     self.assertRaises(ListDictError, self.dict.pop, 5)
    #     self.assertEqual(self.dict.pop(5, default={'name': 'Bob', 'age': 44}), {'name': 'Bob', 'age': 44})
    #     self.assertEqual(len(self.dict), 2)
    #
    # def test_popitem(self):
    #     self.assertEqual(self.dict.popitem(), {'name': 'John', 'age': 30})
    #     self.assertEqual(len(self.dict), 3)
    #     self.assertEqual(self.dict.popitem(), {'age': 20})
    #     self.assertEqual(len(self.dict), 2)
    #     self.assertEqual(self.dict.popitem(default={'name': 'Bob', 'age': 44}), {'name': 'Bob', 'age': 44})
    #     self.assertRaises(ListDictError, self.dict.popitem, 3)
    #     self.assertEqual(len(self.dict), 2)
    #
    # def test_insert(self):
    #     self.dict.insert(0, {'name': 'David', 'age': 44})
    #     self.assertEqual(self.dict[0], {'name': 'David', 'age': 44})
    #     self.assertEqual(self.dict[1], {'name': 'John', 'age': 30})
    #     self.assertEqual(self.dict[2], {'name': 'Alice', 'age': 25})
    #     self.assertEqual(self.dict[3], {'name': 'Bob', 'age': 40})
    #     self.assertEqual(self.dict[4], {'age': 20})
    #     self.assertEqual(len(self.dict), 5)
    #
    # def test_extend(self):
    #     self.dict.extend([{'name': 'David', 'age': 44}, {'name': 'Mary', 'age': 35}])
    #     self.assertEqual(self.dict[0], {'name': 'John', 'age': 30})
    #     self.assertEqual(self.dict[1], {'name': 'Alice', 'age': 25})
    #     self.assertEqual(self.dict[2], {'name': 'Bob', 'age': 40})
    #     self.assertEqual(self.dict[3], {'age': 20})
    #     self.assertEqual(self.dict[4], {'name': 'David', 'age': 44})
    #     self.assertEqual(self.dict[5], {'name': 'Mary', 'age': 35})
    #     self.assertEqual(len(self.dict), 6)
    #
    # def test_update(self):
    #     self.dict.update([{'name': 'David', 'age': 44}])
    #     self.assertEqual(self.dict[1], {'name': 'David', 'age': 44})
    #     self.assertEqual(len(self.dict), 4)
    #
    # def test_setdefault(self):
    #     self.assertEqual(self.dict.setdefault(1, {'name': 'David', 'age': 44}), {'name': 'John', 'age': 30})
    #     self.assertEqual(self.dict.setdefault(5, {'name': 'David', 'age': 44}), {'name': 'David', 'age': 44})
    #     self.assertEqual(len(self.dict), 5)
    #
    # def test_reverse(self):
    #     self.dict.reverse()
    #     self.assertEqual(self.dict[0], {'age': 20})
    #     self.assertEqual(self.dict[1], {'name': 'Bob', 'age': 40})
    #     self.assertEqual(self.dict[2], {'name': 'Alice', 'age': 25})
    #     self.assertEqual(self.dict[3], {'name': 'John', 'age': 30})
    #     self.assertEqual(len(self.dict), 4)
    #
    # def test_sort(self):
    #     self.dict.sort()
    #     self.assertEqual(self.dict[0], {'age': 20})
    #     self.assertEqual(self.dict[1], {'name': 'Alice', 'age': 25})
    #     self.assertEqual(self.dict[2], {'name': 'John', 'age': 30})
    #     self.assertEqual(self.dict[3], {'name': 'Bob', 'age': 40})
    #     self.assertEqual(len(self.dict), 4)
    #
    # def test_sort_by(self):
    #     self.dict.sort_by('age')
    #     self.assertEqual(self.dict[0], {'age': 20})
    #     self.assertEqual(self.dict[1], {'name': 'Alice', 'age': 25})
    #     self.assertEqual(self.dict[2], {'name': 'John', 'age': 30})
    #     self.assertEqual(self.dict[3], {'name': 'Bob', 'age': 40})
    #     self.assertEqual(len(self.dict), 4)
    #
    # def test_sort_by_reverse(self):
    #     self.dict.sort_by('age', reverse=True)
    #     self.assertEqual(self.dict[0], {'name': 'Bob', 'age': 40})
    #     self.assertEqual(self.dict[1], {'name': 'John', 'age': 30})
    #     self.assertEqual(self.dict[2], {'name': 'Alice', 'age': 25})
    #     self.assertEqual(self.dict[3], {'age': 20})
    #     self.assertEqual(len(self.dict), 4)
    #
    # def test_sort_by_key(self):
    #     self.dict.sort_by_key()
    #     self.assertEqual(self.dict[0], {'age': 20})
    #     self.assertEqual(self.dict[1], {'name': 'Alice', 'age': 25})
    #     self.assertEqual(self.dict[2], {'name': 'John', 'age': 30})
    #     self.assertEqual(self.dict[3], {'name': 'Bob', 'age': 40})
    #     self.assertEqual(len(self.dict), 4)
    #
    # def test_sort_by_key_reverse(self):
    #     self.dict.sort_by_key(reverse=True)
    #     self.assertEqual(self.dict[0], {'name': 'Bob', 'age': 40})
    #     self.assertEqual(self.dict[1], {'name': 'John', 'age': 30})
    #     self.assertEqual(self.dict[2], {'name': 'Alice', 'age': 25})
    #     self.assertEqual(self.dict[3], {'age': 20})
    #     self.assertEqual(len(self.dict), 4)
    #
    # def test_sort_by_value(self):
    #     self.dict.sort_by_value()
    #     self.assertEqual(self.dict[0], {'age': 20})
    #     self.assertEqual(self.dict[1], {'name': 'Alice', 'age': 25})
    #     self.assertEqual(self.dict[2], {'name': 'John', 'age': 30})
    #     self.assertEqual(self.dict[3], {'name': 'Bob', 'age': 40})
    #     self.assertEqual(len(self.dict), 4)
