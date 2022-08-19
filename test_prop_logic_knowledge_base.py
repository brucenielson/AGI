from unittest import TestCase
from prop_logic_knowledge_base import LogicSymbol, LogicValue, PLKnowledgeBase, Sentence, \
    KnowledgeBaseError, SymbolList, SymbolListError


class TestLogicSymbol(TestCase):
    def test_logic_symbol_class(self):
        symbol: LogicSymbol = LogicSymbol("P1", LogicValue.TRUE)
        self.assertEqual(LogicValue.TRUE, symbol.value)
        self.assertNotEqual(LogicValue.FALSE, symbol.value)
        self.assertEqual("P1", symbol.name)
        self.assertNotEqual("P2", symbol.name)

    def test_operators(self):
        # And
        symbol1: LogicSymbol = LogicSymbol('A', LogicValue.TRUE)
        self.assertEqual(LogicValue.TRUE, symbol1.and_op(LogicValue.TRUE))
        self.assertEqual(LogicValue.FALSE, symbol1.and_op(LogicValue.FALSE))
        self.assertEqual(LogicValue.UNDEFINED, symbol1.and_op(LogicValue.UNDEFINED))
        symbol2: LogicSymbol = LogicSymbol('B', LogicValue.FALSE)
        self.assertEqual(LogicValue.FALSE, symbol2.and_op(LogicValue.TRUE))
        self.assertEqual(LogicValue.FALSE, symbol2.and_op(LogicValue.FALSE))
        self.assertEqual(LogicValue.FALSE, symbol2.and_op(LogicValue.UNDEFINED))
        symbol3: LogicSymbol = LogicSymbol('C', LogicValue.UNDEFINED)
        self.assertEqual(LogicValue.UNDEFINED, symbol3.and_op(LogicValue.TRUE))
        self.assertEqual(LogicValue.FALSE, symbol3.and_op(LogicValue.FALSE))
        self.assertEqual(LogicValue.UNDEFINED, symbol3.and_op(LogicValue.UNDEFINED))
        # Or
        symbol1: LogicSymbol = LogicSymbol('A', LogicValue.TRUE)
        self.assertEqual(LogicValue.TRUE, symbol1.or_op(LogicValue.TRUE))
        self.assertEqual(LogicValue.TRUE, symbol1.or_op(LogicValue.FALSE))
        self.assertEqual(LogicValue.TRUE, symbol1.or_op(LogicValue.UNDEFINED))
        symbol2: LogicSymbol = LogicSymbol('B', LogicValue.FALSE)
        self.assertEqual(LogicValue.TRUE, symbol2.or_op(LogicValue.TRUE))
        self.assertEqual(LogicValue.FALSE, symbol2.or_op(LogicValue.FALSE))
        self.assertEqual(LogicValue.UNDEFINED, symbol2.or_op(LogicValue.UNDEFINED))
        symbol3: LogicSymbol = LogicSymbol('C', LogicValue.UNDEFINED)
        self.assertEqual(LogicValue.TRUE, symbol3.or_op(LogicValue.TRUE))
        self.assertEqual(LogicValue.UNDEFINED, symbol3.or_op(LogicValue.FALSE))
        self.assertEqual(LogicValue.UNDEFINED, symbol3.or_op(LogicValue.UNDEFINED))


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
        self.assertEqual('A2', symbols[0].name)
        self.assertEqual('H356', symbols[1].name)
        self.assertEqual('P1', symbols[2].name)
        self.assertEqual('P14', symbols[3].name)
        self.assertEqual('P2', symbols[4].name)
        self.assertEqual('P4', symbols[5].name)
        self.assertEqual('Q23', symbols[6].name)
        self.assertEqual('Q3', symbols[7].name)
        self.assertEqual('UA45', symbols[8].name)

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

    def test_repr_symbol_list(self):
        sentence: Sentence = Sentence.string_to_sentence("a and c and b => d")
        symbol_list: SymbolList = sentence.get_symbol_list()
        self.assertEqual("A: Undefined; B: Undefined; C: Undefined; D: Undefined; ", repr(symbol_list))
        symbol_list.set_value("A", True)
        symbol_list.set_value("B", False)
        self.assertEqual("A: True; B: False; C: Undefined; D: Undefined; ", repr(symbol_list))

    def test_indexing_and_slicing(self):
        symbols = SymbolList()
        symbols.add("B")
        symbols.add("D")
        symbols.add("C")
        symbols.add("E")
        # Test Setting and Getting with an index
        self.assertEqual("B", symbols[0].name)
        self.assertEqual(LogicValue.UNDEFINED, symbols[0].value)
        symbols[1] = True
        self.assertEqual("C", symbols[1].name)
        self.assertEqual(LogicValue.TRUE, symbols[1].value)
        symbols[2] = False
        self.assertEqual("D", symbols[2].name)
        self.assertEqual(LogicValue.FALSE, symbols[2].value)
        self.assertEqual("E", symbols[3].name)
        self.assertEqual(LogicValue.UNDEFINED, symbols[3].value)
        # Test Setting and Getting with a slice
        new_symbols = symbols[1:3]
        self.assertEqual("C", new_symbols[0].name)
        self.assertEqual(LogicValue.TRUE, symbols[1].value)
        self.assertEqual("D", new_symbols[1].name)
        self.assertEqual(LogicValue.FALSE, symbols[2].value)
        self.assertEqual(2, new_symbols.length)
        new_symbols = symbols[1, 3]
        self.assertEqual("C", new_symbols[0].name)
        self.assertEqual(LogicValue.TRUE, symbols[1].value)
        self.assertEqual("E", new_symbols[1].name)
        self.assertEqual(LogicValue.FALSE, symbols[2].value)
        self.assertEqual(2, new_symbols.length)
        # Test set items
        symbols[1, 3] = True
        self.assertEqual("B", symbols[0].name)
        self.assertEqual(LogicValue.UNDEFINED, symbols[0].value)
        self.assertEqual("C", symbols[1].name)
        self.assertEqual(LogicValue.TRUE, symbols[1].value)
        self.assertEqual("D", symbols[2].name)
        self.assertEqual(LogicValue.FALSE, symbols[2].value)
        self.assertEqual("E", symbols[3].name)
        self.assertEqual(LogicValue.TRUE, symbols[3].value)
        # Test set item
        symbols[1, 3] = False
        self.assertEqual("B", symbols[0].name)
        self.assertEqual(LogicValue.UNDEFINED, symbols[0].value)
        self.assertEqual("C", symbols[1].name)
        self.assertEqual(LogicValue.FALSE, symbols[1].value)
        self.assertEqual("D", symbols[2].name)
        self.assertEqual(LogicValue.FALSE, symbols[2].value)
        self.assertEqual("E", symbols[3].name)
        self.assertEqual(LogicValue.FALSE, symbols[3].value)
        # Test slice to end
        new_symbols = symbols[0, 2:]
        self.assertEqual("B", new_symbols[0].name)
        self.assertEqual(LogicValue.UNDEFINED, symbols[0].value)
        self.assertEqual("D", new_symbols[1].name)
        self.assertEqual(LogicValue.FALSE, symbols[2].value)
        self.assertEqual("E", new_symbols[2].name)
        self.assertEqual(LogicValue.FALSE, symbols[2].value)
        self.assertEqual(3, new_symbols.length)
        # Test slice from start
        new_symbols = symbols[:2, 3]
        self.assertEqual("B", new_symbols[0].name)
        self.assertEqual(LogicValue.UNDEFINED, symbols[0].value)
        self.assertEqual("C", new_symbols[1].name)
        self.assertEqual(LogicValue.FALSE, symbols[2].value)
        self.assertEqual("E", new_symbols[2].name)
        self.assertEqual(LogicValue.FALSE, symbols[2].value)
        self.assertEqual(3, new_symbols.length)
        # Test del
        del new_symbols[1]
        self.assertEqual("B", new_symbols[0].name)
        self.assertEqual(LogicValue.UNDEFINED, symbols[0].value)
        self.assertEqual("E", new_symbols[1].name)
        self.assertEqual(LogicValue.FALSE, symbols[1].value)
        self.assertEqual(2, new_symbols.length)


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
        self.assertEqual(2, kb.line_count)
        # Test exists
        self.assertEqual(True, kb.exists(sentence))
        self.assertEqual(True, kb.exists("a or b and c => d"))
        # Test clear
        kb.clear()
        self.assertEqual(0, kb.line_count)

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
        self.assertEqual(2, kb2.line_count)
        # Test exists
        self.assertEqual(True, kb2.exists(sentence))
        self.assertEqual(True, kb2.exists("a or b and c => d"))
        # Test clear
        kb2.clear()
        self.assertEqual(0, kb2.line_count)

    def test_kb_exists(self):
        kb: PLKnowledgeBase = PLKnowledgeBase()
        kb.add("a or b and c => d")
        sentence = Sentence.string_to_sentence("c and a or d => b")
        kb.add(sentence)
        # Test count
        self.assertEqual(2, kb.line_count)
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

    def test_evaluate_knowledge_base(self):
        # Tests for evaluate_knowledge_base(model), is_true(model), is_false(model)
        # Incidentally tests get_symbol_list
        kb = PLKnowledgeBase()
        input_str: str
        input_str = "A"
        input_str += "\n"
        input_str = input_str + "B"
        input_str = input_str + "\n"
        input_str = input_str + "A AND B => L"
        input_str = input_str + "\n"
        input_str = input_str + "A AND P => L"
        input_str = input_str + "\n"
        input_str = input_str + "B AND L => M"
        input_str = input_str + "\n"
        input_str = input_str + "L AND M => P"
        input_str = input_str + "\n"
        input_str = input_str + "P => Q"
        input_str = input_str + "\n"
        input_str = input_str + "~A => Z"
        input_str = input_str + "\n"
        input_str = input_str + "A and Z => W"
        input_str = input_str + "\n"
        input_str = input_str + "A or Z => ~X"

        kb.add(input_str)
        sl: SymbolList = kb.get_symbol_list()

        # Test symbol list
        self.assertEqual("A", sl.get_symbol(0).name)
        self.assertEqual("B", sl.get_symbol(1).name)
        self.assertEqual("L", sl.get_symbol(2).name)
        self.assertEqual("M", sl.get_symbol(3).name)
        self.assertEqual("P", sl.get_symbol(4).name)
        self.assertEqual("Q", sl.get_symbol(5).name)
        self.assertEqual("W", sl.get_symbol(6).name)
        self.assertEqual("X", sl.get_symbol(7).name)
        self.assertEqual("Z", sl.get_symbol(8).name)

        # Test if there is a 9th symbol (there shouldn't be)
        error = False
        try:
            sl.get_symbol(9)
        except SymbolListError:
            error = True
        self.assertEqual(True, error)

        # Now test evaluate knowledge base
        # Test an undefined set
        sl.set_value("a", True)
        sl.set_value("b", True)
        self.assertTrue(kb.evaluate_knowledge_base(sl) == LogicValue.UNDEFINED)
        self.assertFalse(kb.is_false(sl))
        self.assertFalse(kb.is_true(sl))

        # Test a valid set
        sl.set_value("l", True)
        sl.set_value("m", True)
        sl.set_value("p", True)
        sl.set_value("q", True)
        sl.set_value("w", True)
        sl.set_value("x", False)
        sl.set_value("z", False)
        self.assertTrue(kb.evaluate_knowledge_base(sl) == LogicValue.TRUE)
        self.assertTrue(kb.is_true(sl))
        self.assertFalse(kb.is_false(sl))

        # Now test an invalid set of symbols
        sl.set_value("b", False)
        self.assertTrue(kb.evaluate_knowledge_base(sl) == LogicValue.FALSE)
        self.assertFalse(kb.is_true(sl))
        self.assertTrue(kb.is_false(sl))

        # Test having only partial info, but still at least one clause is know to be false
        sl = kb.get_symbol_list()
        sl.set_value("b", False)
        self.assertTrue(kb.evaluate_knowledge_base(sl) == LogicValue.FALSE)
        self.assertFalse(kb.is_true(sl))
        self.assertTrue(kb.is_false(sl))

    def test_truth_table_entails(self):
        # This tests out "TruthTableEntails()" plus it's "IsQueryTrue()" and "IsQueryFalse()" counterparts.
        # I  need to keep the tests to a minimum because this is an expensive action time wise
        # since it's an NP-Complete Exponential problem. So most of the tests will stay commented out and
        # the tests I run over and over will stay to a minimum to make sure things haven't broken.
        kb = PLKnowledgeBase()
        input_str: str
        input_str = "A"
        input_str += "\n"
        input_str = input_str + "B"
        input_str = input_str + "\n"
        input_str = input_str + "A AND B => L"
        input_str = input_str + "\n"
        input_str = input_str + "A AND P => L"
        input_str = input_str + "\n"
        input_str = input_str + "B AND L => M"
        input_str = input_str + "\n"
        input_str = input_str + "L AND M => P"
        input_str = input_str + "\n"
        input_str = input_str + "P => Q"
        input_str = input_str + "\n"
        input_str = input_str + "~A => Z"
        input_str = input_str + "\n"
        input_str = input_str + "A and Z => W"
        input_str = input_str + "\n"
        input_str = input_str + "A or Z => ~X"

        kb.add(input_str)
        # evaluates to True
        self.assertEqual(LogicValue.TRUE, kb.truth_table_entails('q'))
        self.assertEqual(LogicValue.TRUE, kb.truth_table_entails('~x'))
        # Z is Undefined
        self.assertEqual(LogicValue.UNDEFINED, kb.truth_table_entails('z'))
        self.assertEqual(LogicValue.UNDEFINED, kb.truth_table_entails('~z'))
        self.assertEqual(LogicValue.UNDEFINED, kb.truth_table_entails('w'))
        self.assertEqual(LogicValue.UNDEFINED, kb.truth_table_entails('~w'))
        # Always True even if otherwise undefined
        self.assertEqual(LogicValue.TRUE, kb.truth_table_entails('~w or w'))
        self.assertEqual(LogicValue.TRUE, kb.truth_table_entails('~z or z'))
        self.assertEqual(LogicValue.TRUE, kb.truth_table_entails('a or ~a'))
        # Y is Undefined because it is not in the model
        self.assertEqual(LogicValue.UNDEFINED, kb.truth_table_entails('y'))
        # False
        self.assertEqual(LogicValue.FALSE, kb.truth_table_entails('x'))
        # Entailments
        self.assertEqual(LogicValue.TRUE, kb.truth_table_entails('a'))
        self.assertEqual(LogicValue.TRUE, kb.truth_table_entails('l'))
        self.assertEqual(LogicValue.TRUE, kb.truth_table_entails('p'))
        self.assertEqual(LogicValue.TRUE, kb.truth_table_entails('a and b and l and m and p and q'))
        self.assertEqual(LogicValue.FALSE, kb.truth_table_entails('a and b and l and m and p and q and ~a'))
        self.assertEqual(LogicValue.UNDEFINED, kb.truth_table_entails('a and b and l and m and p and q and z'))
        # False statements
        self.assertEqual(LogicValue.FALSE, kb.truth_table_entails('~a'))
        # Always False
        self.assertEqual(LogicValue.FALSE, kb.truth_table_entails('a and ~a'))
        self.assertEqual(LogicValue.FALSE, kb.truth_table_entails('z and ~z'))
        # Always False even though not in the model
        self.assertEqual(LogicValue.FALSE, kb.truth_table_entails('y and ~y'))
        # Always True even though not in the model
        self.assertEqual(LogicValue.TRUE, kb.truth_table_entails('y or ~y'))
