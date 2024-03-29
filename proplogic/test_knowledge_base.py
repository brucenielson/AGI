from unittest import TestCase
from proplogic.knowledge_base import LogicSymbol, LogicValue, PLKnowledgeBase, Sentence, \
    KnowledgeBaseError, _set_symbol_in_model, _pl_resolve
from proplogic.symbol import SymbolList, SymbolListError

# How to add regions
# https://www.jetbrains.com/help/rider/Coding_Assistance__Surrounding_with_Region.html#managing-regions-in-the-editor


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
        self.assertIsNotNone(symbols.get_symbol('a'))
        self.assertIsNotNone(symbols.get_symbol('B'))
        self.assertIsNotNone(symbols.get_symbol('C'))
        self.assertIsNone(symbols.get_symbol('d'))

    def test_sort_symbol_list(self):
        symbols = SymbolList()
        symbols.add("b")
        self.assertEqual(1, symbols.length)
        symbols.add("c")
        symbols.add("c")
        self.assertEqual(2, symbols.length)
        symbols.add("A")
        self.assertEqual(3, symbols.length)

        self.assertEqual(0, symbols.index('a'))
        self.assertEqual(1, symbols.index('B'))
        self.assertEqual(2, symbols.index('C'))
        self.assertIsNone(symbols.index('d'))

        symbols.auto_sort = True
        self.assertEqual(0, symbols.index('a'))
        self.assertEqual(1, symbols.index('B'))
        self.assertEqual(2, symbols.index('C'))
        self.assertIsNone(symbols.index('d'))

        symbols = SymbolList()
        symbols.add("b")
        self.assertEqual(1, symbols.length)
        symbols.add("c")
        self.assertEqual(2, symbols.length)
        symbols.add("A")
        symbols.add("A")
        self.assertEqual(3, symbols.length)

        self.assertEqual(0, symbols.index('a'))
        self.assertEqual(1, symbols.index('B'))
        self.assertEqual(2, symbols.index('C'))
        self.assertIsNone(symbols.index('d'))

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

        self.assertEqual(0, symbols.index('a2'))
        self.assertEqual(1, symbols.index('h356'))
        self.assertEqual(2, symbols.index('P1'))
        self.assertEqual(3, symbols.index('P14'))
        self.assertEqual(4, symbols.index('P2'))
        self.assertEqual(5, symbols.index('P4'))
        self.assertEqual(6, symbols.index('Q23'))
        self.assertEqual(7, symbols.index('Q3'))
        self.assertEqual(8, symbols.index('UA45'))
        self.assertEqual(9, symbols.length)
        self.assertIsNone(symbols.index('d'))
        self.assertEqual('A2', symbols[0].name)
        self.assertEqual('H356', symbols[1].name)
        self.assertEqual('P1', symbols[2].name)
        self.assertEqual('P14', symbols[3].name)
        self.assertEqual('P2', symbols[4].name)
        self.assertEqual('P4', symbols[5].name)
        self.assertEqual('Q23', symbols[6].name)
        self.assertEqual('Q3', symbols[7].name)
        self.assertEqual('UA45', symbols[8].name)

    def test_symbol_list_doubles(self):
        symbols = SymbolList()
        symbols.add("b")
        self.assertEqual(1, symbols.length)
        symbols.add("c")
        symbols.add("c")
        self.assertEqual(2, symbols.length)
        symbols.add("A")
        self.assertEqual(3, symbols.length)
        symbols.add("B")
        self.assertEqual(3, symbols.length)
        error = False
        try:
            symbols.add("~B")
        except SymbolListError:
            error = True
        self.assertTrue(error)
        self.assertEqual(3, symbols.length)

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
        self.assertIsNone(symbols.get_symbol('d'))

    def test_find_with_index_symbol_list_insertion_point(self):
        symbols = SymbolList()
        symbols.add("B")
        symbols.add("D")
        symbols.add("C")
        symbols.add("E")

        self.assertEqual(0, symbols.index('B'))
        self.assertEqual(1, symbols.index('C'))
        self.assertEqual(2, symbols.index('D'))
        self.assertEqual(3, symbols.index('E'))

        symbols.add("A")
        self.assertEqual(0, symbols.index('A'))
        symbols.add("B1")
        self.assertEqual(2, symbols.index('B1'))
        symbols.add("A1")
        self.assertEqual(1, symbols.index('A1'))

        symbols.add("F")
        self.assertEqual(7, symbols.index('F'))
        symbols.add("E1")
        self.assertEqual(7, symbols.index('E1'))
        symbols.add("E2")
        self.assertEqual(8, symbols.index('E2'))

        self.assertEqual(10, symbols.length)
        self.assertEqual(0, symbols.index('A'))
        self.assertEqual(1, symbols.index('A1'))
        self.assertEqual(2, symbols.index('B'))
        self.assertEqual(3, symbols.index('B1'))
        self.assertEqual(4, symbols.index('C'))
        self.assertEqual(5, symbols.index('D'))
        self.assertEqual(6, symbols.index('E'))
        self.assertEqual(7, symbols.index('E1'))
        self.assertEqual(8, symbols.index('E2'))
        self.assertEqual(9, symbols.index('F'))

    def test_add_symbol_list_via_sentence(self):
        sentence1: Sentence = Sentence("a and c and b => d")
        sentence2: Sentence = Sentence("e and c and f => b and g")
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
        sentence: Sentence = Sentence("a and c and b => d")
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
        # Test del with key name
        del new_symbols['B']
        self.assertEqual("E", new_symbols[0].name)
        self.assertEqual(LogicValue.UNDEFINED, symbols[0].value)
        self.assertEqual(1, new_symbols.length)


class TestPLKnowledgeBase(TestCase):
    def test_add_sentence_parentheses(self):
        kb: PLKnowledgeBase = PLKnowledgeBase()
        kb.add("a or b and c => d")
        sentence = Sentence("c and a or d => b")
        kb.add(sentence)

        self.assertEqual("((A OR (B AND C)) => D)", kb.get_sentence(0).to_string(True))
        self.assertEqual("(((C AND A) OR D) => B)", kb.get_sentence(1).to_string(True))

    def test_add_and_get_sentence(self):
        kb: PLKnowledgeBase = PLKnowledgeBase()
        kb.add("a or b and c => d")
        sentence = Sentence("c and a or d => b")
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
        sentence = Sentence("c and a or d => b")
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
        sentence = Sentence("c and a or d => b")
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
        self.assertTrue(kb.evaluate(sl) == LogicValue.UNDEFINED)
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
        self.assertTrue(kb.evaluate(sl) == LogicValue.TRUE)
        self.assertTrue(kb.is_true(sl))
        self.assertFalse(kb.is_false(sl))

        # Now test an invalid set of symbols
        sl.set_value("b", False)
        self.assertTrue(kb.evaluate(sl) == LogicValue.FALSE)
        self.assertFalse(kb.is_true(sl))
        self.assertTrue(kb.is_false(sl))

        # Test having only partial info, but still at least one clause is know to be false
        sl = kb.get_symbol_list()
        sl.set_value("b", False)
        self.assertTrue(kb.evaluate(sl) == LogicValue.FALSE)
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
        # self.assertTrue(kb.is_query_true('q'))
        # self.assertFalse(kb.is_query_false('q'))
        # Removed to speed up tests
        self.assertEqual(LogicValue.TRUE, kb.truth_table_entails('~x'))
        # Z is Undefined
        self.assertEqual(LogicValue.UNDEFINED, kb.truth_table_entails('z'))
        # self.assertFalse(kb.is_query_true('z'))
        # self.assertFalse(kb.is_query_false('z'))
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
        # Removed to speed up tests
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
        # self.assertFalse(kb.is_query_true('~a'))
        # self.assertTrue(kb.is_query_false('~a'))
        # Always False
        self.assertEqual(LogicValue.FALSE, kb.truth_table_entails('a and ~a'))
        self.assertEqual(LogicValue.FALSE, kb.truth_table_entails('z and ~z'))
        # Always False even though not in the model
        self.assertEqual(LogicValue.FALSE, kb.truth_table_entails('y and ~y'))
        # Always True even though not in the model
        self.assertEqual(LogicValue.TRUE, kb.truth_table_entails('y or ~y'))

    def test_convert_to_cnf(self):
        kb: PLKnowledgeBase = PLKnowledgeBase()
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
        # Verify before conversion
        kb.add(input_str)
        self.assertFalse(kb.is_cnf)
        self.assertEqual(7, kb.line_count)
        self.assertTrue(kb.get_sentence(0).is_atomic)
        self.assertEqual("A", kb.get_sentence(0).to_string(True))
        self.assertTrue(kb.get_sentence(1).is_atomic)
        self.assertEqual("B", kb.get_sentence(1).to_string(True))
        self.assertFalse(kb.get_sentence(2).is_atomic)
        self.assertEqual("((A AND B) => L)", kb.get_sentence(2).to_string(True))
        self.assertFalse(kb.get_sentence(3).is_atomic)
        self.assertEqual("((A AND P) => L)", kb.get_sentence(3).to_string(True))
        self.assertFalse(kb.get_sentence(4).is_atomic)
        self.assertEqual("((B AND L) => M)", kb.get_sentence(4).to_string(True))
        self.assertFalse(kb.get_sentence(5).is_atomic)
        self.assertEqual("((L AND M) => P)", kb.get_sentence(5).to_string(True))
        self.assertFalse(kb.get_sentence(6).is_atomic)
        self.assertEqual("(P => Q)", kb.get_sentence(6).to_string(True))
        # Now verify after conversion
        kb = kb.convert_to_cnf()
        self.assertTrue(kb.is_cnf)
        self.assertEqual(7, kb.line_count)
        self.assertTrue(kb.get_sentence(0).is_atomic)
        self.assertEqual("A", kb.get_sentence(0).to_string(True))
        self.assertTrue(kb.get_sentence(1).is_atomic)
        self.assertEqual("B", kb.get_sentence(1).to_string(True))
        self.assertFalse(kb.get_sentence(2).is_atomic)
        self.assertEqual("~A OR ~B OR L", kb.get_sentence(2).to_string())
        self.assertFalse(kb.get_sentence(3).is_atomic)
        self.assertEqual("~A OR ~P OR L", kb.get_sentence(3).to_string())
        self.assertFalse(kb.get_sentence(4).is_atomic)
        self.assertEqual("~B OR ~L OR M", kb.get_sentence(4).to_string())
        self.assertFalse(kb.get_sentence(5).is_atomic)
        self.assertEqual("~L OR ~M OR P", kb.get_sentence(5).to_string())
        self.assertFalse(kb.get_sentence(6).is_atomic)
        self.assertEqual("~P OR Q", kb.get_sentence(6).to_string())
        # Test a single line
        kb.clear()
        input_str = "A"
        kb.add(input_str)
        self.assertEqual(1, kb.line_count)
        self.assertTrue(kb.get_sentence(0).is_atomic)
        self.assertEqual("A", kb.get_sentence(0).to_string(True))
        kb = kb.convert_to_cnf()
        self.assertEqual(1, kb.line_count)
        self.assertTrue(kb.get_sentence(0).is_atomic)
        self.assertEqual("A", kb.get_sentence(0).to_string(True))

    def test_find_pure_symbol(self):
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
        kb = kb.convert_to_cnf()
        symbols: SymbolList = kb.get_symbol_list()
        model: SymbolList = symbols.clone()
        pure_symbol = kb.find_pure_symbol(symbols, model)
        self.assertEqual('Q', pure_symbol.name)
        self.assertEqual(LogicValue.TRUE, pure_symbol.value)
        symbols, model = _set_symbol_in_model(pure_symbol, symbols, model)
        pure_symbol = kb.find_pure_symbol(symbols, model)
        self.assertEqual('W', pure_symbol.name)
        self.assertEqual(LogicValue.TRUE, pure_symbol.value)
        symbols, model = _set_symbol_in_model(pure_symbol, symbols, model)
        pure_symbol = kb.find_pure_symbol(symbols, model)
        self.assertEqual('X', pure_symbol.name)
        self.assertEqual(LogicValue.FALSE, pure_symbol.value)
        symbols, model = _set_symbol_in_model(pure_symbol, symbols, model)
        pure_symbol = kb.find_pure_symbol(symbols, model)
        self.assertEqual('Z', pure_symbol.name)
        self.assertEqual(LogicValue.TRUE, pure_symbol.value)
        symbols, model = _set_symbol_in_model(pure_symbol, symbols, model)
        pure_symbol = kb.find_pure_symbol(symbols, model)
        self.assertEqual(None, pure_symbol)

    def test_find_unit_symbol(self):
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
        kb = kb.convert_to_cnf()
        symbols: SymbolList = kb.get_symbol_list()
        model: SymbolList = symbols.clone()
        unit_symbol = kb.find_unit_clause(model)
        self.assertEqual('A', unit_symbol.name)
        self.assertEqual(LogicValue.TRUE, unit_symbol.value)
        symbols, model = _set_symbol_in_model(unit_symbol, symbols, model)
        unit_symbol = kb.find_unit_clause(model)
        self.assertEqual('B', unit_symbol.name)
        self.assertEqual(LogicValue.TRUE, unit_symbol.value)
        symbols, model = _set_symbol_in_model(unit_symbol, symbols, model)
        unit_symbol = kb.find_unit_clause(model)
        self.assertEqual('L', unit_symbol.name)
        self.assertEqual(LogicValue.TRUE, unit_symbol.value)
        symbols, model = _set_symbol_in_model(unit_symbol, symbols, model)
        unit_symbol = kb.find_unit_clause(model)
        self.assertEqual('M', unit_symbol.name)
        self.assertEqual(LogicValue.TRUE, unit_symbol.value)
        symbols, model = _set_symbol_in_model(unit_symbol, symbols, model)
        unit_symbol = kb.find_unit_clause(model)
        self.assertEqual('P', unit_symbol.name)
        self.assertEqual(LogicValue.TRUE, unit_symbol.value)
        symbols, model = _set_symbol_in_model(unit_symbol, symbols, model)
        unit_symbol = kb.find_unit_clause(model)
        self.assertEqual('Q', unit_symbol.name)
        self.assertEqual(LogicValue.TRUE, unit_symbol.value)
        symbols, model = _set_symbol_in_model(unit_symbol, symbols, model)
        unit_symbol = kb.find_unit_clause(model)
        self.assertEqual('X', unit_symbol.name)
        self.assertEqual(LogicValue.FALSE, unit_symbol.value)
        symbols, model = _set_symbol_in_model(unit_symbol, symbols, model)
        unit_symbol = kb.find_unit_clause(model)
        self.assertEqual(None, unit_symbol)

    def test_dpll_entails(self):
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
        kb = kb.convert_to_cnf()
        # evaluates to True
        self.assertTrue(kb.dpll_entails('q'))
        self.assertTrue(kb.is_query_true('q'))
        self.assertFalse(kb.is_query_false('q'))
        # Removed to speed up tests
        self.assertTrue(kb.dpll_entails('~x'))
        # Z is Undefined
        self.assertFalse(kb.dpll_entails('z'))
        self.assertTrue(kb.is_query_undefined('z'))
        self.assertTrue(kb.is_query_undefined('~z'))
        self.assertTrue(kb.is_query_undefined('w'))
        self.assertTrue(kb.is_query_undefined('~w'))
        # Always True even if otherwise undefined
        self.assertTrue(kb.is_query_true('~w or w'))
        self.assertTrue(kb.is_query_true('~z or z'))
        self.assertTrue(kb.is_query_true('~z or z'))
        # Y is Undefined because it is not in the model
        self.assertTrue(kb.is_query_undefined('y'))
        # False
        # Removed to speed up tests
        self.assertFalse(kb.dpll_entails('x'))
        # Entailments
        self.assertTrue(kb.dpll_entails('a'))
        self.assertTrue(kb.dpll_entails('l'))
        self.assertTrue(kb.dpll_entails('p'))
        self.assertTrue(kb.dpll_entails('a and b and l and m and p and q'))
        self.assertFalse(kb.dpll_entails('a and b and l and m and p and q and ~a'))
        self.assertTrue(kb.is_query_undefined('a and b and l and m and p and q and z'))
        # False statements
        self.assertFalse(kb.dpll_entails('~a'))
        self.assertFalse(kb.is_query_true('~a'))
        self.assertTrue(kb.is_query_false('~a'))
        # Always False
        self.assertTrue(kb.is_query_false('a and ~a'))
        self.assertTrue(kb.is_query_false('z and ~z'))
        # Always False even though not in the model
        self.assertTrue(kb.is_query_false('y and ~y'))
        # Always True even though not in the model
        self.assertTrue(kb.is_query_true('y or ~y'))

    def test_split_and_lines(self):
        sentence1: Sentence = Sentence("A OR B OR C AND D")
        sentence2 = sentence1.convert_to_cnf(or_clauses_only=False)
        self.assertTrue(sentence1.is_equivalent(sentence2))
        sentences: list = sentence1.convert_to_cnf(or_clauses_only=True)
        self.assertEqual(2, len(sentences))
        self.assertEqual("C OR B OR A", sentences[0].to_string())
        self.assertEqual("D OR B OR A", sentences[1].to_string())
        sentence1: Sentence = Sentence("A AND B => D AND C")
        sentence2 = sentence1.convert_to_cnf(or_clauses_only=False)
        self.assertTrue(sentence1.is_equivalent(sentence2))
        sentences: list = sentence1.convert_to_cnf(or_clauses_only=True)
        self.assertEqual(2, len(sentences))
        self.assertEqual("D OR ~A OR ~B", sentences[0].to_string())
        self.assertEqual("C OR ~A OR ~B", sentences[1].to_string())
        sentence1: Sentence = Sentence("A AND B <=> D AND C")
        sentence2 = sentence1.convert_to_cnf(or_clauses_only=False)
        self.assertTrue(sentence1.is_equivalent(sentence2))
        sentences: list = sentence1.convert_to_cnf(or_clauses_only=True)
        self.assertEqual(4, len(sentences))
        self.assertEqual("D OR ~A OR ~B", sentences[0].to_string())
        self.assertEqual("C OR ~A OR ~B", sentences[1].to_string())
        self.assertEqual("A OR ~D OR ~C", sentences[2].to_string())
        self.assertEqual("B OR ~D OR ~C", sentences[3].to_string())

    def test_is_subset(self):
        # First knowledge base
        kb1 = PLKnowledgeBase()
        input_str: str
        input_str = "A"
        input_str += "\n"
        input_str = input_str + "B"
        input_str = input_str + "\n"
        input_str = input_str + "A AND B => L"
        kb1.add(input_str)
        # Second knowledge base
        kb2 = PLKnowledgeBase()
        input_str: str
        input_str = "A"
        input_str += "\n"
        input_str = input_str + "A AND B => L"
        kb2.add(input_str)
        # Run tests
        self.assertTrue(kb2.is_subset(kb1))
        self.assertFalse(kb1.is_subset(kb2))

    def test_get_atomic_symbols(self):
        sentence: Sentence = Sentence("A OR B OR C")
        sentence = sentence.convert_to_cnf(or_clauses_only=True)[0]
        symbols = sentence.get_atomic_symbols()
        self.assertEqual(3, len(symbols))
        # Try out duplicates
        sentence: Sentence = Sentence("A OR B OR C OR A")
        sentence = sentence.convert_to_cnf(or_clauses_only=True)[0]
        symbols = sentence.get_atomic_symbols()
        self.assertEqual(3, len(symbols))
        self.assertEqual("A", symbols[0].name)
        self.assertEqual(LogicValue.TRUE, symbols[0].value)
        self.assertEqual("B", symbols[1].name)
        self.assertEqual(LogicValue.TRUE, symbols[1].value)
        self.assertEqual("C", symbols[2].name)
        self.assertEqual(LogicValue.TRUE, symbols[2].value)
        # Try out duplicates with a negation
        sentence: Sentence = Sentence("A OR B OR C OR ~A")
        sentence = sentence.convert_to_cnf(or_clauses_only=True)[0]
        symbols = sentence.get_atomic_symbols()
        self.assertEqual(4, len(symbols))
        self.assertEqual("A", symbols[0].name)
        self.assertEqual(LogicValue.TRUE, symbols[0].value)
        self.assertEqual("B", symbols[1].name)
        self.assertEqual(LogicValue.TRUE, symbols[1].value)
        self.assertEqual("C", symbols[2].name)
        self.assertEqual(LogicValue.TRUE, symbols[2].value)
        self.assertEqual("A", symbols[3].name)
        self.assertEqual(LogicValue.FALSE, symbols[3].value)

    def test__pl_resolve(self):
        # Basic Test
        sentence1 = Sentence("A OR B OR C")
        sentence2 = Sentence("B OR C OR ~D OR ~A")
        resolvents = _pl_resolve(sentence1, sentence2)
        self.assertEqual(1, len(resolvents))
        self.assertEqual("B OR C OR ~D", resolvents[0].to_string())
        # Test multiple resolvents
        sentence1 = Sentence("A OR B OR C")
        sentence2 = Sentence("~B OR C OR ~D OR ~A")
        resolvents = _pl_resolve(sentence1, sentence2)
        self.assertEqual(0, len(resolvents))
        # self.assertTrue(resolvents[0].is_equivalent("B OR ~B OR C OR ~D"))
        # self.assertTrue(resolvents[1].is_equivalent("~A OR A OR C OR ~D"))
        # Test entails
        sentence1 = Sentence("A OR B OR ~C")
        sentence2 = Sentence("~B OR C OR ~A")
        resolvents = _pl_resolve(sentence1, sentence2)
        self.assertEqual(0, len(resolvents))
        # self.assertTrue(resolvents[0].is_equivalent("B OR ~B OR ~C OR C"))
        # self.assertTrue(resolvents[1].is_equivalent("A OR ~A OR C OR ~C"))
        # self.assertTrue(resolvents[2].is_equivalent("A OR ~A OR B OR ~B"))
        # self.assertEqual(None, resolvents[0].symbol)

    def test_basic_pl_resolution(self):
        kb = PLKnowledgeBase()
        input_str: str
        input_str = "A"
        input_str += "\n"
        input_str = input_str + "B"
        input_str = input_str + "\n"
        input_str = input_str + "A AND B => L"
        input_str = input_str + "\n"
        input_str = input_str + "B AND L => M"
        input_str = input_str + "\n"
        input_str = input_str + "L AND M => P"
        input_str = input_str + "\n"
        input_str = input_str + "P => Q"

        kb.add(input_str)
        kb.cache_resolvents(force_cnf_format=True)
        # kb = kb.convert_to_cnf()
        self.assertTrue(kb.pl_resolution('q', use_cache=True))
        self.assertTrue(kb.pl_resolution('a', use_cache=True))
        self.assertTrue(kb.pl_resolution('b', use_cache=True))
        self.assertTrue(kb.pl_resolution('l', use_cache=True))
        self.assertTrue(kb.pl_resolution('m', use_cache=True))
        self.assertTrue(kb.pl_resolution('p', use_cache=True))
        self.assertFalse(kb.pl_resolution('y', use_cache=True))
        self.assertFalse(kb.pl_resolution('a and b and ~a', use_cache=True))
        self.assertFalse(kb.pl_resolution('a and z', use_cache=True))
        self.assertFalse(kb.pl_resolution('a and b and z', use_cache=True))
        self.assertTrue(kb.pl_resolution('~w or w', use_cache=True))

        # Uncomment for 'Medium' difficulty tests.
        # self.assertFalse(kb.pl_resolution('~q', use_cache=True))
        # # Z is Undefined
        # self.assertFalse(kb.pl_resolution('z', use_cache=True))
        # self.assertFalse(kb.pl_resolution('~z', use_cache=True))
        # # False statements
        # self.assertFalse(kb.pl_resolution('~a', use_cache=True))
        # # Entailments
        # self.assertTrue(kb.pl_resolution('a and b and l and m and p and q', use_cache=True))
        # # Y is Undefined because it is not in the model
        # self.assertFalse(kb.pl_resolution('y'))
        # # Always True even if otherwise undefined
        # self.assertTrue(kb.pl_resolution('~z or z', use_cache=True))
        # self.assertTrue(kb.pl_resolution('~z or z', use_cache=True))
        # # Always False
        # self.assertFalse(kb.pl_resolution('a and ~a', use_cache=True))
        # self.assertFalse(kb.pl_resolution('z and ~z', use_cache=True))
        # # Always False even though not in the model
        # self.assertFalse(kb.pl_resolution('y and ~y', use_cache=True))
        # # Always True even though not in the model
        # self.assertTrue(kb.pl_resolution('y or ~y', use_cache=True))
        # self.assertFalse(kb.pl_resolution('x', use_cache=True))
        # self.assertFalse(kb.pl_resolution('z', use_cache=True))
        # self.assertFalse(kb.pl_resolution('a and b and l and m and p and q and ~a', use_cache=True))

        # Takes forever - so can't use even normally, even for medium tests
        # self.assertFalse(kb.pl_resolution('a and b and l and m and p and q and z', use_cache=True))

    def test_advanced_pl_resolution(self):
        kb = PLKnowledgeBase()
        input_str: str
        input_str = "A"
        input_str += "\n"
        input_str = input_str + "B"
        input_str = input_str + "\n"
        input_str = input_str + "A AND B => L"
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
        # kb.cache_resolvents(force_cnf_format=True)
        # self.assertTrue(kb.pl_resolution('~x', use_cache=True))

    def test_walk_sat(self):
        # tries = 100
        # successes = 0.0
        # for i in range(tries):
        #     if self.test_walk_sat2():
        #         successes += 1.0
        # print("% Successes: ", successes / float(tries))
        # return

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
        self.assertTrue(kb.walk_sat(seed=10))
        kb_clone: PLKnowledgeBase
        # evaluates to True
        kb_clone = kb.clone('q')
        self.assertTrue(kb_clone.walk_sat(seed=10))
        # Removed to speed up tests
        kb_clone = kb.clone('~x')
        self.assertTrue(kb_clone.walk_sat(seed=10))
        # Z is Undefined
        kb_clone = kb.clone('z')
        self.assertTrue(kb_clone.walk_sat(seed=10))
        # Always True even if otherwise undefined
        kb_clone = kb.clone('~w or w')
        self.assertTrue(kb_clone.walk_sat(seed=10))
        kb_clone = kb.clone('~z or z')
        self.assertTrue(kb_clone.walk_sat(seed=10))
        # False
        # Removed to speed up tests
        kb_clone = kb.clone('x')
        self.assertFalse(kb_clone.walk_sat(seed=10))
        # Entailments
        kb_clone = kb.clone('a')
        self.assertTrue(kb_clone.walk_sat(seed=10))
        kb_clone = kb.clone('l')
        self.assertTrue(kb_clone.walk_sat(seed=10))
        kb_clone = kb.clone('p')
        self.assertTrue(kb_clone.walk_sat(seed=10))
        kb_clone = kb.clone('a and b and l and m and p and q')
        self.assertTrue(kb_clone.walk_sat(seed=10))
        kb_clone = kb.clone('a and b and l and m and p and q and ~a')
        self.assertFalse(kb_clone.walk_sat(seed=10))
        # False statements
        kb_clone = kb.clone('~a')
        self.assertFalse(kb_clone.walk_sat(seed=10))
        # Always False
        kb_clone = kb.clone('a and ~a')
        self.assertFalse(kb_clone.walk_sat(seed=10))
        kb_clone = kb.clone('z and ~z')
        self.assertFalse(kb_clone.walk_sat(seed=10))
        # Always False even though not in the model
        kb_clone = kb.clone('y and ~y')
        self.assertFalse(kb_clone.walk_sat(seed=10))
        # Always True even though not in the model
        kb_clone = kb.clone('y or ~y')
        self.assertTrue(kb_clone.walk_sat(seed=10))

    # def test_walk_sat2(self):
    #     kb = PLKnowledgeBase()
    #     input_str: str
    #     input_str = "A"
    #     input_str += "\n"
    #     input_str = input_str + "B"
    #     input_str = input_str + "\n"
    #     input_str = input_str + "A AND B => L"
    #     input_str = input_str + "\n"
    #     input_str = input_str + "A AND P => L"
    #     input_str = input_str + "\n"
    #     input_str = input_str + "B AND L => M"
    #     input_str = input_str + "\n"
    #     input_str = input_str + "L AND M => P"
    #     input_str = input_str + "\n"
    #     input_str = input_str + "P => Q"
    #     input_str = input_str + "\n"
    #     input_str = input_str + "~A => Z"
    #     input_str = input_str + "\n"
    #     input_str = input_str + "A and Z => W"
    #     input_str = input_str + "\n"
    #     input_str = input_str + "A or Z => ~X"
    #
    #     kb.add(input_str)
    #     # kb = kb.convert_to_cnf()
    #     correct_count: int = 0
    #     if kb.walk_sat():
    #         correct_count += 1
    #     else:
    #         print("basic")
    #     kb_clone: PLKnowledgeBase
    #     # evaluates to True
    #     kb_clone = kb.clone('q')
    #     if kb_clone.walk_sat():
    #         correct_count += 1
    #     else:
    #         print("q")
    #     # Removed to speed up tests
    #     kb_clone = kb.clone('~x')
    #     if kb_clone.walk_sat():
    #         correct_count += 1
    #     else:
    #         print("~x")
    #     # Z is Undefined
    #     kb_clone = kb.clone('z')
    #     if kb_clone.walk_sat():
    #         correct_count += 1
    #     else:
    #         print("z")
    #     # Always True even if otherwise undefined
    #     kb_clone = kb.clone('~w or w')
    #     if kb_clone.walk_sat():
    #         correct_count += 1
    #     else:
    #         print("~w or w")
    #     kb_clone = kb.clone('~z or z')
    #     if kb_clone.walk_sat():
    #         correct_count += 1
    #     else:
    #         print('~z or z')
    #     # False
    #     # Removed to speed up tests
    #     kb_clone = kb.clone('x')
    #     if not kb_clone.walk_sat():
    #         correct_count += 1
    #     else:
    #         print('x')
    #     # Entailments
    #     kb_clone = kb.clone('a')
    #     if kb_clone.walk_sat():
    #         correct_count += 1
    #     else:
    #         print('a')
    #     kb_clone = kb.clone('l')
    #     if kb_clone.walk_sat():
    #         correct_count += 1
    #     else:
    #         print('l')
    #     kb_clone = kb.clone('p')
    #     if kb_clone.walk_sat():
    #         correct_count += 1
    #     else:
    #         print('p')
    #     kb_clone = kb.clone('a and b and l and m and p and q')
    #     if kb_clone.walk_sat():
    #         correct_count += 1
    #     else:
    #         print('a and b and l and m and p and q')
    #     kb_clone = kb.clone('a and b and l and m and p and q and ~a')
    #     if not kb_clone.walk_sat():
    #         correct_count += 1
    #     else:
    #         print('a and b and l and m and p and q and ~a')
    #     # False statements
    #     kb_clone = kb.clone('~a')
    #     if not kb_clone.walk_sat():
    #         correct_count += 1
    #     else:
    #         print('~a')
    #     # Always False
    #     kb_clone = kb.clone('a and ~a')
    #     if not kb_clone.walk_sat():
    #         correct_count += 1
    #     else:
    #         print('a and ~a')
    #     kb_clone = kb.clone('z and ~z')
    #     if not kb_clone.walk_sat():
    #         correct_count += 1
    #     else:
    #         print('z and ~z')
    #     # Always False even though not in the model
    #     kb_clone = kb.clone('y and ~y')
    #     if not kb_clone.walk_sat():
    #         correct_count += 1
    #     else:
    #         print('y and ~y')
    #     # Always True even though not in the model
    #     kb_clone = kb.clone('y or ~y')
    #     if kb_clone.walk_sat():
    #         correct_count += 1
    #     else:
    #         print('y or ~y')
    #
    #     # self.assertEqual(17, correct_count)
    #     return 17 == correct_count

    def test_entails_walk_sat(self):
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
        kb = kb.convert_to_cnf()
        # evaluates to True
        self.assertTrue(kb.walk_sat_entails('q', seed=10))
        # Removed to speed up tests
        self.assertTrue(kb.walk_sat_entails('~x', seed=10))
        # Z is Undefined
        self.assertFalse(kb.walk_sat_entails('z', seed=10))
        self.assertFalse(kb.walk_sat_entails('~z', seed=10))
        self.assertFalse(kb.walk_sat_entails('w', seed=10))
        self.assertFalse(kb.walk_sat_entails('~w', seed=10))
        # Always True even if otherwise undefined
        self.assertTrue(kb.walk_sat_entails('~w or w', seed=10))
        self.assertTrue(kb.walk_sat_entails('~z or z', seed=10))
        self.assertTrue(kb.walk_sat_entails('~z or z', seed=10))
        # Y is Undefined because it is not in the model
        self.assertFalse(kb.walk_sat_entails('y', seed=10))
        # False
        # Removed to speed up tests
        self.assertFalse(kb.walk_sat_entails('x', seed=10))
        # Entailments
        self.assertTrue(kb.walk_sat_entails('a', seed=10))
        self.assertTrue(kb.walk_sat_entails('l', seed=10))
        self.assertTrue(kb.walk_sat_entails('p', seed=10))
        self.assertTrue(kb.walk_sat_entails('a and b and l and m and p and q', seed=10))
        self.assertFalse(kb.walk_sat_entails('a and b and l and m and p and q and ~a', seed=10))
        self.assertFalse(kb.walk_sat_entails('a and b and l and m and p and q and z', seed=10))
        # False statements
        self.assertFalse(kb.walk_sat_entails('~a', seed=10))
        self.assertFalse(kb.walk_sat_entails('~a', seed=10))
        # Always False
        self.assertFalse(kb.walk_sat_entails('a and ~a', seed=10))
        self.assertFalse(kb.walk_sat_entails('z and ~z', seed=10))
        # Always False even though not in the model
        self.assertFalse(kb.walk_sat_entails('y and ~y', seed=10))
        # Always True even though not in the model
        self.assertTrue(kb.walk_sat_entails('y or ~y', seed=10))
