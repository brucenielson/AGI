from unittest import TestCase
from prop_logic_knowledge_base import LogicSymbol, LogicValue, PLKnowledgeBase, Sentence, \
    KnowledgeBaseError, SymbolList


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
        symbols.add("P4")
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

    def test_find_with_index_symbol_list_insertion_point(self):
        symbols = SymbolList()
        symbols.add("B")
        symbols.add("D")
        symbols.add("C")
        symbols.add("E")

        self.assertEqual(0, symbols.find_with_index('B')[1])
        self.assertEqual(1, symbols.find_with_index('C')[1])
        self.assertEqual(2, symbols.find_with_index('D')[1])
        self.assertEqual(3, symbols.find_with_index('E')[1])

        symbols.add("A")
        self.assertEqual(0, symbols.find_with_index('A')[1])
        symbols.add("B1")
        self.assertEqual(2, symbols.find_with_index('B1')[1])
        symbols.add("A1")
        self.assertEqual(1, symbols.find_with_index('A1')[1])

        symbols.add("F")
        self.assertEqual(7, symbols.find_with_index('F')[1])
        symbols.add("E1")
        self.assertEqual(7, symbols.find_with_index('E1')[1])
        symbols.add("E2")
        self.assertEqual(8, symbols.find_with_index('E2')[1])

        self.assertEqual(10, symbols.length)
        self.assertEqual(0, symbols.find_with_index('A')[1])
        self.assertEqual(1, symbols.find_with_index('A1')[1])
        self.assertEqual(2, symbols.find_with_index('B')[1])
        self.assertEqual(3, symbols.find_with_index('B1')[1])
        self.assertEqual(4, symbols.find_with_index('C')[1])
        self.assertEqual(5, symbols.find_with_index('D')[1])
        self.assertEqual(6, symbols.find_with_index('E')[1])
        self.assertEqual(7, symbols.find_with_index('E1')[1])
        self.assertEqual(8, symbols.find_with_index('E2')[1])
        self.assertEqual(9, symbols.find_with_index('F')[1])

    def test_add_symbol_list_via_sentence(self):
        sentence1: Sentence = Sentence.string_to_sentence("a and c and b => d")
        sentence2: Sentence = Sentence.string_to_sentence("e and c and f => b and g")
        symbol_list1: SymbolList = sentence1.get_symbol_list()
        # Test first sentence
        self.assertEqual("A", symbol_list1.get_symbol(0).name)
        self.assertEqual("B", symbol_list1.get_symbol(1).name)
        self.assertEqual("C", symbol_list1.get_symbol(2).name)
        self.assertEqual("D", symbol_list1.get_symbol(3).name)
        # Test second sentence
        symbol_list1.add(sentence2.get_symbol_list())
        self.assertEqual("A", symbol_list1.get_symbol(0).name)
        self.assertEqual("B", symbol_list1.get_symbol(1).name)
        self.assertEqual("C", symbol_list1.get_symbol(2).name)
        self.assertEqual("D", symbol_list1.get_symbol(3).name)
        self.assertEqual("E", symbol_list1.get_symbol(4).name)
        self.assertEqual("F", symbol_list1.get_symbol(5).name)
        self.assertEqual("G", symbol_list1.get_symbol(6).name)



class TestPLKnowledgeBase(TestCase):
    def test_add_sentence_parentheses(self):
        kb: PLKnowledgeBase = PLKnowledgeBase()
        kb.add("a or b and c => d")
        sentence = Sentence.string_to_sentence("c and a or d => b")
        kb.add(sentence)

        self.assertEqual("((A OR (B AND C)) => D)", kb.get_sentence(0).to_string(True))
        self.assertEqual("(((C AND A) OR D) => B)", kb.get_sentence(1).to_string(True))

    def test_add_and_get_sentence(self):
        kb: PLKnowledgeBase = PLKnowledgeBase()
        kb.add("a or b and c => d")
        sentence = Sentence.string_to_sentence("c and a or d => b")
        kb.add(sentence)

        self.assertEqual("A OR B AND C => D", kb.get_sentence(0).to_string())
        self.assertEqual("C AND A OR D => B", kb.get_sentence(1).to_string())
        # Test count
        self.assertEqual(2, kb.count())
        # Test exists
        self.assertEqual(True, kb.exists(sentence))
        self.assertEqual(True, kb.exists("a or b and c => d"))
        # Test clear
        kb.clear()
        self.assertEqual(0, kb.count())

    def test_kb_clone(self):
        kb1: PLKnowledgeBase = PLKnowledgeBase()
        kb1.add("a or b and c => d")
        sentence = Sentence.string_to_sentence("c and a or d => b")
        kb1.add(sentence)
        kb2: PLKnowledgeBase = kb1.clone()

        self.assertEqual(False, kb1 == kb2)
        self.assertEqual("A OR B AND C => D", kb2.get_sentence(0).to_string())
        self.assertEqual("C AND A OR D => B", kb2.get_sentence(1).to_string())
        # Test count
        self.assertEqual(2, kb2.count())
        # Test exists
        self.assertEqual(True, kb2.exists(sentence))
        self.assertEqual(True, kb2.exists("a or b and c => d"))
        # Test clear
        kb2.clear()
        self.assertEqual(0, kb2.count())

    def test_kb_exists(self):
        kb: PLKnowledgeBase = PLKnowledgeBase()
        kb.add("a or b and c => d")
        sentence = Sentence.string_to_sentence("c and a or d => b")
        kb.add(sentence)
        # Test count
        self.assertEqual(2, kb.count())
        # Test exists
        self.assertEqual(True, kb.exists(sentence))
        self.assertEqual(True, kb.exists("a or b and c => d"))
        # Test illegal call
        fail: bool = False
        message: str = ""
        try:
            self.assertEqual(True, kb.exists("a or b and c => d\nc or d"))
        except KnowledgeBaseError as err:
            fail = True
            message = err.args[0]
        self.assertEqual(True, fail)
        self.assertEqual("Call to 'exists' only works for a single logical line.", message)


