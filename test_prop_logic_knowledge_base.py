from unittest import TestCase
from prop_logic_knowledge_base import LogicSymbol, LogicValue


class TestLogicSymbol(TestCase):
    def test_logic_symbol_class(self):
        symbol: LogicSymbol = LogicSymbol("P1", LogicValue.TRUE)
        self.assertEqual(LogicValue.TRUE, symbol.value)
        self.assertNotEqual(LogicValue.FALSE, symbol.value)
        self.assertEqual("P1", symbol.name)
        self.assertNotEqual("P2", symbol.name)


class TestSymbolList(TestCase):
    pass
