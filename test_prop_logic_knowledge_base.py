from unittest import TestCase
from prop_logic_knowledge_base import LogicSymbol, LogicValue, SymbolList


class TestLogicSymbol(TestCase):
    def test_logic_symbol_class(self):
        symbol: LogicSymbol = LogicSymbol("P1", LogicValue.TRUE)
        self.assertEqual(LogicValue.TRUE, symbol.value)
        self.assertNotEqual(LogicValue.FALSE, symbol.value)
        self.assertEqual("P1", symbol.name)
        self.assertNotEqual("P2", symbol.name)


class TestSymbolList(TestCase):
    def test_add_symbol_list(self):
        symbols = SymbolList()
        symbols.auto_sort = False
        symbols.add("a")
        self.assertEqual(1, symbols.length)
        symbols.add("b")
        self.assertEqual(2, symbols.length)
        symbols.add("c")

        self.assertEqual(3, symbols.length)
        self.assertIsNotNone(symbols.find('a'))
        self.assertIsNotNone(symbols.find('B'))
        self.assertIsNotNone(symbols.find('C'))
        self.assertIsNone(symbols.find('d'))

    def test_sort_symbol_list(self):
        symbols = SymbolList()
        symbols.auto_sort = False
        symbols.add("b")
        self.assertEqual(1, symbols.length)
        symbols.add("c")
        self.assertEqual(2, symbols.length)
        symbols.add("A")
        self.assertEqual(3, symbols.length)

        self.assertEqual(2, symbols.find_with_index('a')[1])
        self.assertEqual(0, symbols.find_with_index('B')[1])
        self.assertEqual(1, symbols.find_with_index('C')[1])
        self.assertIsNone(symbols.find('d'))

        symbols.auto_sort = True
        self.assertEqual(0, symbols.find_with_index('a')[1])
        self.assertEqual(1, symbols.find_with_index('B')[1])
        self.assertEqual(2, symbols.find_with_index('C')[1])
        self.assertIsNone(symbols.find('d'))

        symbols = SymbolList()
        symbols.add("b")
        self.assertEqual(1, symbols.length)
        symbols.add("c")
        self.assertEqual(2, symbols.length)
        symbols.add("A")
        self.assertEqual(3, symbols.length)

        self.assertEqual(0, symbols.find_with_index('a')[1])
        self.assertEqual(1, symbols.find_with_index('B')[1])
        self.assertEqual(2, symbols.find_with_index('C')[1])
        self.assertIsNone(symbols.find('d'))

        symbols = SymbolList()
        symbols.add("Q3")
        symbols.add("P1")
        symbols.add("P4")
        symbols.add("Q23")
        symbols.add("P14")
        symbols.add("A2")
        symbols.add("H356")
        symbols.add("P2")
        symbols.add("UA45")

        self.assertEqual(0, symbols.find_with_index('a2')[1])
        self.assertEqual(1, symbols.find_with_index('h356')[1])
        self.assertEqual(2, symbols.find_with_index('P1')[1])
        self.assertEqual(3, symbols.find_with_index('P14')[1])
        self.assertEqual(4, symbols.find_with_index('P2')[1])
        self.assertEqual(5, symbols.find_with_index('P4')[1])
        self.assertEqual(6, symbols.find_with_index('Q23')[1])
        self.assertEqual(7, symbols.find_with_index('Q3')[1])
        self.assertEqual(8, symbols.find_with_index('UA45')[1])
        self.assertEqual(9, symbols.length)
        self.assertIsNone(symbols.find('d'))

    def test_symbol_list_set_value(self):
        symbols = SymbolList()
        symbols.add("Q3")
        symbols.add("P1")
        symbols.add("P4")
        symbols.add("Q23")
        symbols.add("P14")
        symbols.add("A2")
        symbols.add("H356")
        symbols.add("P2")
        symbols.add("UA45")

        self.assertEqual(LogicValue.UNDEFINED, symbols.get_value('P2'))
        symbols.set_value('P2', True)
        self.assertEqual(LogicValue.TRUE, symbols.get_value('P2'))
        symbols.set_value('P2', False)
        self.assertEqual(LogicValue.FALSE, symbols.get_value('P2'))
        symbols.set_value('P2', LogicValue.TRUE)
        self.assertEqual(LogicValue.TRUE, symbols.get_value('P2'))
        symbols.set_value('P2', LogicValue.UNDEFINED)
        self.assertEqual(LogicValue.UNDEFINED, symbols.get_value('P2'))
        symbols.set_value('P2', LogicValue.FALSE)
        self.assertEqual(LogicValue.FALSE, symbols.get_value('P2'))

        self.assertEqual(LogicValue.UNDEFINED, symbols.get_value('Q3'))
        self.assertEqual(LogicValue.UNDEFINED, symbols.get_value('P1'))
        self.assertEqual(LogicValue.UNDEFINED, symbols.get_value('P4'))
        self.assertEqual(LogicValue.UNDEFINED, symbols.get_value('Q3'))
        self.assertEqual(LogicValue.UNDEFINED, symbols.get_value('Q23'))
        self.assertEqual(LogicValue.UNDEFINED, symbols.get_value('P14'))
        self.assertEqual(LogicValue.UNDEFINED, symbols.get_value('A2'))
        self.assertEqual(LogicValue.UNDEFINED, symbols.get_value('H356'))
        self.assertEqual(LogicValue.UNDEFINED, symbols.get_value('UA45'))
        self.assertIsNone(symbols.find('d'))
        
