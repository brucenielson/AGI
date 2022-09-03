from unittest import TestCase
from pl_parser import LogicParser
from sentence import Sentence, SentenceError, LogicOperatorTypes
from pl_knowledge_base import SymbolList, LogicValue


class TestPropLogicParser(TestCase):
    def test_pyparsing(self):
        parser = LogicParser("P1U87 AND P2 AND ~P3 OR A94P => P4 AND (P6 OR P8)\nP5 AND P7")
        correct_result = [
            ['P1U87', 'AND', 'P2', 'AND', '~', 'P3', 'OR', 'A94P', '=>', 'P4', 'AND', '(', 'P6', 'OR', 'P8', ')'],
            ['P5', 'AND', 'P7']]
        self.assertEqual(correct_result, parser.token_list)

    def test_current_token(self):
        parser = LogicParser("P1U87 AND P2 AND ~P3 OR A94P => P4 AND (P6 OR P8)\nP5 AND P7")
        self.assertEqual('P1U87', parser.current_token)

    def test_line_count(self):
        parser = LogicParser("P1")
        self.assertEqual(1, parser.line_count)
        parser.parse_line()
        self.assertEqual(0, parser.line_count)
        parser = LogicParser("P1U87 AND P2 AND ~P3 OR A94P => P4 AND (P6 OR P8)\nP5 AND P7")
        self.assertEqual(2, parser.line_count)
        parser.parse_line()
        self.assertEqual(1, parser.line_count)
        parser.parse_line()
        self.assertEqual(0, parser.line_count)

    def test_consume_token(self):
        parser = LogicParser("P1U87 AND P2 AND ~P3 OR A94P => P4 AND (P6 OR P8)\nP5 AND P7")
        self.assertEqual('P1U87', parser.current_token)
        self.assertEqual('P1U87', parser.consume_token())
        self.assertEqual('AND', parser.current_token)
        self.assertEqual('AND', parser.consume_token())
        self.assertEqual('P2', parser.consume_token())
        self.assertEqual('AND', parser.consume_token())
        self.assertEqual('~', parser.consume_token())
        self.assertEqual('P3', parser.consume_token())
        self.assertEqual('OR', parser.consume_token())
        self.assertEqual('A94P', parser.consume_token())
        self.assertEqual('=>', parser.consume_token())
        self.assertEqual('P4', parser.consume_token())
        self.assertEqual('AND', parser.consume_token())
        self.assertEqual('(', parser.consume_token())
        self.assertEqual('P6', parser.consume_token())
        self.assertEqual([['OR', 'P8', ')'], ['P5', 'AND', 'P7']], parser.token_list)
        correct_result = [
            ['P1U87', 'AND', 'P2', 'AND', '~', 'P3', 'OR', 'A94P', '=>', 'P4', 'AND', '(', 'P6', 'OR', 'P8', ')'],
            ['P5', 'AND', 'P7']]
        self.assertEqual(correct_result, parser.get_original_token_list())
        self.assertEqual('OR', parser.consume_token())
        self.assertEqual('P8', parser.consume_token())
        self.assertEqual(')', parser.consume_token())
        # End of line reached
        self.assertEqual('END LINE', parser.consume_token())
        # Start new line
        self.assertEqual('P5', parser.consume_token())
        self.assertEqual('AND', parser.consume_token())
        self.assertEqual('P7', parser.consume_token())
        # End of file
        self.assertEqual('END LINE', parser.consume_token())
        self.assertEqual('EOF', parser.consume_token())

    def test_simple_phrases(self):
        parser = LogicParser("P1")
        sentence = parser.parse_line()
        self.assertEqual(None, sentence.first_sentence)
        self.assertEqual(None, sentence.second_sentence)
        self.assertEqual('P1', sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NO_OPERATOR, sentence.logic_operator)
        self.assertFalse(sentence.negation)

        parser = LogicParser("P1 AND P2")
        sentence = parser.parse_line()
        self.assertEqual('P1', sentence.first_sentence.symbol)
        self.assertFalse(sentence.first_sentence.negation)
        self.assertEqual('P2', sentence.second_sentence.symbol)
        self.assertFalse(sentence.second_sentence.negation)
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.AND, sentence.logic_operator)
        self.assertFalse(sentence.negation)

        parser = LogicParser("P1 OR P2")
        sentence = parser.parse_line()
        self.assertEqual('P1', sentence.first_sentence.symbol)
        self.assertFalse(sentence.first_sentence.negation)
        self.assertEqual('P2', sentence.second_sentence.symbol)
        self.assertFalse(sentence.second_sentence.negation)
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.OR, sentence.logic_operator)
        self.assertFalse(sentence.negation)

        parser = LogicParser("~P1")
        sentence = parser.parse_line()
        self.assertEqual(None, sentence.first_sentence)
        self.assertEqual(None, sentence.second_sentence)
        self.assertEqual('P1', sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NO_OPERATOR, sentence.logic_operator)
        self.assertTrue(sentence.negation)

        parser = LogicParser("~(P1 AND P2)")
        sentence = parser.parse_line()
        self.assertEqual('P1', sentence.first_sentence.symbol)
        self.assertFalse(sentence.first_sentence.negation)
        self.assertEqual('P2', sentence.second_sentence.symbol)
        self.assertFalse(sentence.second_sentence.negation)
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.AND, sentence.logic_operator)
        self.assertTrue(sentence.negation)

        parser = LogicParser("~(P1 OR P2)")
        sentence = parser.parse_line()
        self.assertEqual('P1', sentence.first_sentence.symbol)
        self.assertFalse(sentence.first_sentence.negation)
        self.assertEqual('P2', sentence.second_sentence.symbol)
        self.assertFalse(sentence.second_sentence.negation)
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.OR, sentence.logic_operator)
        self.assertTrue(sentence.negation)

        parser = LogicParser("~P1 AND P2")
        sentence = parser.parse_line()
        self.assertEqual('P1', sentence.first_sentence.symbol)
        self.assertTrue(sentence.first_sentence.negation)
        self.assertEqual('P2', sentence.second_sentence.symbol)
        self.assertFalse(sentence.second_sentence.negation)
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.AND, sentence.logic_operator)
        self.assertFalse(sentence.negation)

        parser = LogicParser("~P1 OR P2")
        sentence = parser.parse_line()
        self.assertEqual('P1', sentence.first_sentence.symbol)
        self.assertTrue(sentence.first_sentence.negation)
        self.assertEqual('P2', sentence.second_sentence.symbol)
        self.assertFalse(sentence.second_sentence.negation)
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.OR, sentence.logic_operator)
        self.assertFalse(sentence.negation)

        parser = LogicParser("P1 AND ~P2")
        sentence = parser.parse_line()
        self.assertEqual('P1', sentence.first_sentence.symbol)
        self.assertFalse(sentence.first_sentence.negation)
        self.assertEqual('P2', sentence.second_sentence.symbol)
        self.assertTrue(sentence.second_sentence.negation)
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.AND, sentence.logic_operator)
        self.assertFalse(sentence.negation)

        parser = LogicParser("P1 OR ~P2")
        sentence = parser.parse_line()
        self.assertEqual('P1', sentence.first_sentence.symbol)
        self.assertFalse(sentence.first_sentence.negation)
        self.assertEqual('P2', sentence.second_sentence.symbol)
        self.assertTrue(sentence.second_sentence.negation)
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.OR, sentence.logic_operator)
        self.assertFalse(sentence.negation)

    def test_simple_implications_bi_conditionals(self):
        parser = LogicParser("P1 => P2")
        sentence = parser.parse_line()
        self.assertEqual('P1', sentence.first_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NO_OPERATOR, sentence.first_sentence.logic_operator)
        self.assertFalse(sentence.first_sentence.negation)
        self.assertEqual('P2', sentence.second_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NO_OPERATOR, sentence.second_sentence.logic_operator)
        self.assertFalse(sentence.second_sentence.negation)
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.IMPLIES, sentence.logic_operator)
        self.assertFalse(sentence.negation)

        parser = LogicParser("~P1 <=> P2")
        sentence = parser.parse_line()
        self.assertEqual('P1', sentence.first_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NO_OPERATOR, sentence.first_sentence.logic_operator)
        self.assertTrue(sentence.first_sentence.negation)
        self.assertEqual('P2', sentence.second_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NO_OPERATOR, sentence.second_sentence.logic_operator)
        self.assertFalse(sentence.second_sentence.negation)
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.BI_CONDITIONAL, sentence.logic_operator)
        self.assertFalse(sentence.negation)

        parser = LogicParser("P1 <=> ~P2")
        sentence = parser.parse_line()
        self.assertEqual('P1', sentence.first_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NO_OPERATOR, sentence.first_sentence.logic_operator)
        self.assertFalse(sentence.first_sentence.negation)
        self.assertEqual('P2', sentence.second_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NO_OPERATOR, sentence.second_sentence.logic_operator)
        self.assertTrue(sentence.second_sentence.negation)
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.BI_CONDITIONAL, sentence.logic_operator)
        self.assertFalse(sentence.negation)

        parser = LogicParser("P1 <=> P2")
        sentence = parser.parse_line()
        self.assertEqual('P1', sentence.first_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NO_OPERATOR, sentence.first_sentence.logic_operator)
        self.assertFalse(sentence.first_sentence.negation)
        self.assertEqual('P2', sentence.second_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NO_OPERATOR, sentence.second_sentence.logic_operator)
        self.assertFalse(sentence.second_sentence.negation)
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.BI_CONDITIONAL, sentence.logic_operator)
        self.assertFalse(sentence.negation)

        parser = LogicParser("~P1 <=> P2")
        sentence = parser.parse_line()
        self.assertEqual('P1', sentence.first_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NO_OPERATOR, sentence.first_sentence.logic_operator)
        self.assertTrue(sentence.first_sentence.negation)
        self.assertEqual('P2', sentence.second_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NO_OPERATOR, sentence.second_sentence.logic_operator)
        self.assertFalse(sentence.second_sentence.negation)
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.BI_CONDITIONAL, sentence.logic_operator)
        self.assertFalse(sentence.negation)

        parser = LogicParser("P1 <=> ~P2")
        sentence = parser.parse_line()
        self.assertEqual('P1', sentence.first_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NO_OPERATOR, sentence.first_sentence.logic_operator)
        self.assertFalse(sentence.first_sentence.negation)
        self.assertEqual('P2', sentence.second_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NO_OPERATOR, sentence.second_sentence.logic_operator)
        self.assertTrue(sentence.second_sentence.negation)
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.BI_CONDITIONAL, sentence.logic_operator)
        self.assertFalse(sentence.negation)

    # noinspection SpellCheckingInspection
    def test_complex_implications_biconditionals(self):
        parser = LogicParser("P1 AND P3 => P2 AND P4")
        sentence = parser.parse_line()
        self.assertEqual(None, sentence.first_sentence.symbol)
        self.assertFalse(sentence.first_sentence.negation)
        self.assertEqual('P1', sentence.first_sentence.first_sentence.symbol)
        self.assertFalse(sentence.first_sentence.first_sentence.negation)
        self.assertEqual('P3', sentence.first_sentence.second_sentence.symbol)
        self.assertFalse(sentence.first_sentence.first_sentence.negation)
        self.assertEqual(None, sentence.second_sentence.symbol)
        self.assertFalse(sentence.second_sentence.negation)
        self.assertEqual('P2', sentence.second_sentence.first_sentence.symbol)
        self.assertFalse(sentence.second_sentence.first_sentence.negation)
        self.assertEqual('P4', sentence.second_sentence.second_sentence.symbol)
        self.assertFalse(sentence.second_sentence.first_sentence.negation)
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.IMPLIES, sentence.logic_operator)
        self.assertFalse(sentence.negation)

        parser = LogicParser("P1 AND P3 <=> P2 AND P4")
        sentence = parser.parse_line()
        self.assertEqual(None, sentence.first_sentence.symbol)
        self.assertFalse(sentence.first_sentence.negation)
        self.assertEqual('P1', sentence.first_sentence.first_sentence.symbol)
        self.assertFalse(sentence.first_sentence.first_sentence.negation)
        self.assertEqual('P3', sentence.first_sentence.second_sentence.symbol)
        self.assertFalse(sentence.first_sentence.first_sentence.negation)
        self.assertEqual(None, sentence.second_sentence.symbol)
        self.assertFalse(sentence.second_sentence.negation)
        self.assertEqual('P2', sentence.second_sentence.first_sentence.symbol)
        self.assertFalse(sentence.second_sentence.first_sentence.negation)
        self.assertEqual('P4', sentence.second_sentence.second_sentence.symbol)
        self.assertFalse(sentence.second_sentence.first_sentence.negation)
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.BI_CONDITIONAL, sentence.logic_operator)
        self.assertFalse(sentence.negation)

        parser = LogicParser("(P1 AND P3) => (P2 AND P4)")
        sentence = parser.parse_line()
        self.assertEqual(None, sentence.first_sentence.symbol)
        self.assertFalse(sentence.first_sentence.negation)
        self.assertEqual('P1', sentence.first_sentence.first_sentence.symbol)
        self.assertFalse(sentence.first_sentence.first_sentence.negation)
        self.assertEqual('P3', sentence.first_sentence.second_sentence.symbol)
        self.assertFalse(sentence.first_sentence.first_sentence.negation)
        self.assertEqual(None, sentence.second_sentence.symbol)
        self.assertFalse(sentence.second_sentence.negation)
        self.assertEqual('P2', sentence.second_sentence.first_sentence.symbol)
        self.assertFalse(sentence.second_sentence.first_sentence.negation)
        self.assertEqual('P4', sentence.second_sentence.second_sentence.symbol)
        self.assertFalse(sentence.second_sentence.first_sentence.negation)
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.IMPLIES, sentence.logic_operator)
        self.assertFalse(sentence.negation)

        parser = LogicParser("(P1 AND P3) <=> (P2 AND P4)")
        sentence = parser.parse_line()
        self.assertEqual(None, sentence.first_sentence.symbol)
        self.assertFalse(sentence.first_sentence.negation)
        self.assertEqual('P1', sentence.first_sentence.first_sentence.symbol)
        self.assertFalse(sentence.first_sentence.first_sentence.negation)
        self.assertEqual('P3', sentence.first_sentence.second_sentence.symbol)
        self.assertFalse(sentence.first_sentence.first_sentence.negation)
        self.assertEqual(None, sentence.second_sentence.symbol)
        self.assertFalse(sentence.second_sentence.negation)
        self.assertEqual('P2', sentence.second_sentence.first_sentence.symbol)
        self.assertFalse(sentence.second_sentence.first_sentence.negation)
        self.assertEqual('P4', sentence.second_sentence.second_sentence.symbol)
        self.assertFalse(sentence.second_sentence.first_sentence.negation)
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.BI_CONDITIONAL, sentence.logic_operator)
        self.assertFalse(sentence.negation)

        parser = LogicParser("~(P1 AND P3) => ~(P2 AND P4)")
        sentence = parser.parse_line()
        self.assertEqual(None, sentence.first_sentence.symbol)
        self.assertTrue(sentence.first_sentence.negation)
        self.assertEqual('P1', sentence.first_sentence.first_sentence.symbol)
        self.assertFalse(sentence.first_sentence.first_sentence.negation)
        self.assertEqual('P3', sentence.first_sentence.second_sentence.symbol)
        self.assertFalse(sentence.first_sentence.first_sentence.negation)
        self.assertEqual(None, sentence.second_sentence.symbol)
        self.assertTrue(sentence.second_sentence.negation)
        self.assertEqual('P2', sentence.second_sentence.first_sentence.symbol)
        self.assertFalse(sentence.second_sentence.first_sentence.negation)
        self.assertEqual('P4', sentence.second_sentence.second_sentence.symbol)
        self.assertFalse(sentence.second_sentence.first_sentence.negation)
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.IMPLIES, sentence.logic_operator)
        self.assertFalse(sentence.negation)

        parser = LogicParser("~(P1 AND P3) <=> ~(P2 AND P4)")
        sentence = parser.parse_line()
        self.assertEqual(None, sentence.first_sentence.symbol)
        self.assertTrue(sentence.first_sentence.negation)
        self.assertEqual('P1', sentence.first_sentence.first_sentence.symbol)
        self.assertFalse(sentence.first_sentence.first_sentence.negation)
        self.assertEqual('P3', sentence.first_sentence.second_sentence.symbol)
        self.assertFalse(sentence.first_sentence.first_sentence.negation)
        self.assertEqual(None, sentence.second_sentence.symbol)
        self.assertTrue(sentence.second_sentence.negation)
        self.assertEqual('P2', sentence.second_sentence.first_sentence.symbol)
        self.assertFalse(sentence.second_sentence.first_sentence.negation)
        self.assertEqual('P4', sentence.second_sentence.second_sentence.symbol)
        self.assertFalse(sentence.second_sentence.first_sentence.negation)
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.BI_CONDITIONAL, sentence.logic_operator)
        self.assertFalse(sentence.negation)

    def test_and_or_priority(self):
        parser = LogicParser("P1 AND P2 OR P3")
        sentence = parser.parse_line()
        # Top level
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.OR, sentence.logic_operator)
        self.assertFalse(sentence.negation)
        # First sentence
        self.assertEqual(None, sentence.first_sentence.symbol)
        self.assertFalse(sentence.first_sentence.negation)
        self.assertEqual(LogicOperatorTypes.AND, sentence.first_sentence.logic_operator)

        self.assertEqual('P1', sentence.first_sentence.first_sentence.symbol)
        self.assertFalse(sentence.first_sentence.first_sentence.negation)
        self.assertEqual(LogicOperatorTypes.NO_OPERATOR, sentence.first_sentence.first_sentence.logic_operator)

        self.assertEqual('P2', sentence.first_sentence.second_sentence.symbol)
        self.assertFalse(sentence.first_sentence.second_sentence.negation)
        self.assertEqual(LogicOperatorTypes.NO_OPERATOR, sentence.first_sentence.second_sentence.logic_operator)

        # Second sentence
        self.assertEqual('P3', sentence.second_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NO_OPERATOR, sentence.second_sentence.logic_operator)
        self.assertFalse(sentence.second_sentence.negation)

        parser = LogicParser("P1 OR P2 AND P3")
        sentence = parser.parse_line()
        # Top level
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.OR, sentence.logic_operator)
        self.assertFalse(sentence.negation)
        # First sentence
        self.assertEqual('P1', sentence.first_sentence.symbol)
        self.assertFalse(sentence.first_sentence.negation)
        self.assertEqual(LogicOperatorTypes.NO_OPERATOR, sentence.first_sentence.logic_operator)
        self.assertEqual(None, sentence.first_sentence.first_sentence)
        self.assertEqual(None, sentence.first_sentence.second_sentence)
        # Second sentence
        self.assertEqual(LogicOperatorTypes.AND, sentence.second_sentence.logic_operator)
        self.assertFalse(sentence.second_sentence.negation)
        self.assertEqual('P2', sentence.second_sentence.first_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NO_OPERATOR, sentence.second_sentence.first_sentence.logic_operator)
        self.assertFalse(sentence.second_sentence.first_sentence.negation)
        self.assertEqual('P3', sentence.second_sentence.second_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NO_OPERATOR, sentence.second_sentence.second_sentence.logic_operator)
        self.assertFalse(sentence.second_sentence.second_sentence.negation)
        self.assertFalse(sentence.second_sentence.second_sentence.negation)

    def test_string_of_ands(self):
        parser = LogicParser("P1 AND P2 AND P3")
        sentence = parser.parse_line()
        # Top level
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.AND, sentence.logic_operator)
        self.assertFalse(sentence.negation)
        # First sentence
        self.assertEqual('P1', sentence.first_sentence.symbol)
        self.assertFalse(sentence.first_sentence.negation)
        self.assertEqual(LogicOperatorTypes.NO_OPERATOR, sentence.first_sentence.logic_operator)
        # Second sentence
        self.assertEqual(None, sentence.second_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.AND, sentence.second_sentence.logic_operator)
        self.assertFalse(sentence.second_sentence.negation)
        self.assertEqual('P2', sentence.second_sentence.first_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NO_OPERATOR, sentence.second_sentence.first_sentence.logic_operator)
        self.assertFalse(sentence.second_sentence.first_sentence.negation)
        self.assertEqual('P3', sentence.second_sentence.second_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NO_OPERATOR, sentence.second_sentence.second_sentence.logic_operator)
        self.assertFalse(sentence.second_sentence.second_sentence.negation)

        parser = LogicParser("P1 AND (P2 AND P3)")
        sentence = parser.parse_line()
        # Top level
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.AND, sentence.logic_operator)
        self.assertFalse(sentence.negation)
        # First sentence
        self.assertEqual('P1', sentence.first_sentence.symbol)
        self.assertFalse(sentence.first_sentence.negation)
        self.assertEqual(LogicOperatorTypes.NO_OPERATOR, sentence.first_sentence.logic_operator)
        # Second sentence
        self.assertEqual(None, sentence.second_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.AND, sentence.second_sentence.logic_operator)
        self.assertFalse(sentence.second_sentence.negation)
        self.assertEqual('P2', sentence.second_sentence.first_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NO_OPERATOR, sentence.second_sentence.first_sentence.logic_operator)
        self.assertFalse(sentence.second_sentence.first_sentence.negation)
        self.assertEqual('P3', sentence.second_sentence.second_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NO_OPERATOR, sentence.second_sentence.second_sentence.logic_operator)
        self.assertFalse(sentence.second_sentence.second_sentence.negation)

        parser = LogicParser("(P1 AND P2) AND P3")
        sentence = parser.parse_line()
        # Top level
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.AND, sentence.logic_operator)
        self.assertFalse(sentence.negation)
        # First sentence
        self.assertEqual(None, sentence.first_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.AND, sentence.first_sentence.logic_operator)
        self.assertFalse(sentence.negation)

        self.assertEqual('P1', sentence.first_sentence.first_sentence.symbol)
        self.assertFalse(sentence.first_sentence.first_sentence.negation)
        self.assertEqual(LogicOperatorTypes.NO_OPERATOR, sentence.first_sentence.first_sentence.logic_operator)

        self.assertEqual('P2', sentence.first_sentence.second_sentence.symbol)
        self.assertFalse(sentence.first_sentence.second_sentence.negation)
        self.assertEqual(LogicOperatorTypes.NO_OPERATOR, sentence.first_sentence.second_sentence.logic_operator)

        # Second sentence
        self.assertEqual('P3', sentence.second_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NO_OPERATOR, sentence.second_sentence.logic_operator)
        self.assertFalse(sentence.second_sentence.negation)

    def test_string_of_ors(self):
        parser = LogicParser("P1 OR P2 OR P3")
        sentence = parser.parse_line()
        # Top level
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.OR, sentence.logic_operator)
        self.assertFalse(sentence.negation)
        # First sentence
        self.assertEqual('P1', sentence.first_sentence.symbol)
        self.assertFalse(sentence.first_sentence.negation)
        self.assertEqual(LogicOperatorTypes.NO_OPERATOR, sentence.first_sentence.logic_operator)
        # Second sentence
        self.assertEqual(None, sentence.second_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.OR, sentence.second_sentence.logic_operator)
        self.assertFalse(sentence.second_sentence.negation)
        self.assertEqual('P2', sentence.second_sentence.first_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NO_OPERATOR, sentence.second_sentence.first_sentence.logic_operator)
        self.assertFalse(sentence.second_sentence.first_sentence.negation)
        self.assertEqual('P3', sentence.second_sentence.second_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NO_OPERATOR, sentence.second_sentence.second_sentence.logic_operator)
        self.assertFalse(sentence.second_sentence.second_sentence.negation)

        parser = LogicParser("P1 OR (P2 OR P3)")
        sentence = parser.parse_line()
        # Top level
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.OR, sentence.logic_operator)
        self.assertFalse(sentence.negation)
        # First sentence
        self.assertEqual('P1', sentence.first_sentence.symbol)
        self.assertFalse(sentence.first_sentence.negation)
        self.assertEqual(LogicOperatorTypes.NO_OPERATOR, sentence.first_sentence.logic_operator)
        # Second sentence
        self.assertEqual(None, sentence.second_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.OR, sentence.second_sentence.logic_operator)
        self.assertFalse(sentence.second_sentence.negation)
        self.assertEqual('P2', sentence.second_sentence.first_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NO_OPERATOR, sentence.second_sentence.first_sentence.logic_operator)
        self.assertFalse(sentence.second_sentence.first_sentence.negation)
        self.assertEqual('P3', sentence.second_sentence.second_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NO_OPERATOR, sentence.second_sentence.second_sentence.logic_operator)
        self.assertFalse(sentence.second_sentence.second_sentence.negation)

        parser = LogicParser("(P1 OR P2) OR P3")
        sentence = parser.parse_line()
        # Top level
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.OR, sentence.logic_operator)
        self.assertFalse(sentence.negation)
        # First sentence
        self.assertEqual(None, sentence.first_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.OR, sentence.first_sentence.logic_operator)
        self.assertFalse(sentence.negation)
        self.assertEqual('P1', sentence.first_sentence.first_sentence.symbol)
        self.assertFalse(sentence.first_sentence.first_sentence.negation)
        self.assertEqual(LogicOperatorTypes.NO_OPERATOR, sentence.first_sentence.first_sentence.logic_operator)
        self.assertEqual('P2', sentence.first_sentence.second_sentence.symbol)
        self.assertFalse(sentence.first_sentence.second_sentence.negation)
        self.assertEqual(LogicOperatorTypes.NO_OPERATOR, sentence.first_sentence.second_sentence.logic_operator)
        # Second sentence
        self.assertEqual('P3', sentence.second_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NO_OPERATOR, sentence.second_sentence.logic_operator)
        self.assertFalse(sentence.second_sentence.negation)

    def test_parse_line(self):
        parser = LogicParser("P1U87 AND P2 AND ~P3 OR A94P => P4 AND (P6 OR P8)")
        sentence = parser.parse_line()
        # Top level
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.IMPLIES, sentence.logic_operator)
        self.assertFalse(sentence.negation)
        # First Sentence
        self.assertEqual(None, sentence.first_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.OR, sentence.first_sentence.logic_operator)
        self.assertFalse(sentence.first_sentence.negation)
        # First - First
        self.assertEqual(None, sentence.first_sentence.first_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.AND, sentence.first_sentence.first_sentence.logic_operator)
        self.assertFalse(sentence.first_sentence.first_sentence.negation)
        # First - First - First
        self.assertEqual('P1U87', sentence.first_sentence.first_sentence.first_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NO_OPERATOR,
                         sentence.first_sentence.first_sentence.first_sentence.logic_operator)
        self.assertFalse(sentence.first_sentence.first_sentence.first_sentence.negation)
        # First - First - Second
        self.assertEqual(None, sentence.first_sentence.first_sentence.second_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.AND, sentence.first_sentence.first_sentence.second_sentence.logic_operator)
        self.assertFalse(sentence.first_sentence.first_sentence.second_sentence.negation)
        # First - First - Second - First
        self.assertEqual('P2', sentence.first_sentence.first_sentence.second_sentence.first_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NO_OPERATOR,
                         sentence.first_sentence.first_sentence.second_sentence.first_sentence.logic_operator)
        self.assertFalse(sentence.first_sentence.first_sentence.second_sentence.negation)
        # First - First - Second - Second
        self.assertEqual('P3', sentence.first_sentence.first_sentence.second_sentence.second_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NO_OPERATOR,
                         sentence.first_sentence.first_sentence.second_sentence.second_sentence.logic_operator)
        self.assertTrue(sentence.first_sentence.first_sentence.second_sentence.second_sentence.negation)
        # First - Second
        self.assertEqual('A94P', sentence.first_sentence.second_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NO_OPERATOR, sentence.first_sentence.second_sentence.logic_operator)
        self.assertFalse(sentence.first_sentence.second_sentence.negation)
        # Second Sentence
        self.assertEqual(None, sentence.second_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.AND, sentence.second_sentence.logic_operator)
        self.assertFalse(sentence.second_sentence.negation)
        # Second - First
        self.assertEqual('P4', sentence.second_sentence.first_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NO_OPERATOR, sentence.second_sentence.first_sentence.logic_operator)
        self.assertFalse(sentence.second_sentence.first_sentence.negation)
        # Second - Second
        self.assertEqual(None, sentence.second_sentence.second_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.OR, sentence.second_sentence.second_sentence.logic_operator)
        self.assertFalse(sentence.second_sentence.second_sentence.negation)
        self.assertEqual('P6', sentence.second_sentence.second_sentence.first_sentence.symbol)
        self.assertEqual('P8', sentence.second_sentence.second_sentence.second_sentence.symbol)

    def test_parse_input(self):
        parser = LogicParser("P1U87 AND P2 AND ~P3 OR A94P => P4 AND (P6 OR P8)\nP5 AND P7")
        sentences = parser.parse_input()
        sentence = sentences[0]
        # Top level
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.IMPLIES, sentence.logic_operator)
        self.assertFalse(sentence.negation)
        # First Sentence
        self.assertEqual(None, sentence.first_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.OR, sentence.first_sentence.logic_operator)
        self.assertFalse(sentence.first_sentence.negation)
        # First - First
        self.assertEqual(None, sentence.first_sentence.first_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.AND, sentence.first_sentence.first_sentence.logic_operator)
        self.assertFalse(sentence.first_sentence.first_sentence.negation)
        # First - First - First
        self.assertEqual('P1U87', sentence.first_sentence.first_sentence.first_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NO_OPERATOR,
                         sentence.first_sentence.first_sentence.first_sentence.logic_operator)
        self.assertFalse(sentence.first_sentence.first_sentence.first_sentence.negation)
        # First - First - Second
        self.assertEqual(None, sentence.first_sentence.first_sentence.second_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.AND, sentence.first_sentence.first_sentence.second_sentence.logic_operator)
        self.assertFalse(sentence.first_sentence.first_sentence.second_sentence.negation)
        # First - First - Second - First
        self.assertEqual('P2', sentence.first_sentence.first_sentence.second_sentence.first_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NO_OPERATOR,
                         sentence.first_sentence.first_sentence.second_sentence.first_sentence.logic_operator)
        self.assertFalse(sentence.first_sentence.first_sentence.second_sentence.negation)
        # First - First - Second - Second
        self.assertEqual('P3', sentence.first_sentence.first_sentence.second_sentence.second_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NO_OPERATOR,
                         sentence.first_sentence.first_sentence.second_sentence.second_sentence.logic_operator)
        self.assertTrue(sentence.first_sentence.first_sentence.second_sentence.second_sentence.negation)
        # First - Second
        self.assertEqual('A94P', sentence.first_sentence.second_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NO_OPERATOR, sentence.first_sentence.second_sentence.logic_operator)
        self.assertFalse(sentence.first_sentence.second_sentence.negation)
        # Second Sentence
        self.assertEqual(None, sentence.second_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.AND, sentence.second_sentence.logic_operator)
        self.assertFalse(sentence.second_sentence.negation)
        # Second - First
        self.assertEqual('P4', sentence.second_sentence.first_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NO_OPERATOR, sentence.second_sentence.first_sentence.logic_operator)
        self.assertFalse(sentence.second_sentence.first_sentence.negation)
        # Second - Second
        self.assertEqual(None, sentence.second_sentence.second_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.OR, sentence.second_sentence.second_sentence.logic_operator)
        self.assertFalse(sentence.second_sentence.second_sentence.negation)
        self.assertEqual('P6', sentence.second_sentence.second_sentence.first_sentence.symbol)
        self.assertEqual('P8', sentence.second_sentence.second_sentence.second_sentence.symbol)

        # Line 2
        sentence = sentences[1]
        self.assertEqual('P5', sentence.first_sentence.symbol)
        self.assertFalse(sentence.first_sentence.negation)
        self.assertEqual('P7', sentence.second_sentence.symbol)
        self.assertFalse(sentence.second_sentence.negation)
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.AND, sentence.logic_operator)
        self.assertFalse(sentence.negation)

    def test_parse_set_input(self):
        # This tests the parser without passing in an input string right away
        parser = LogicParser()
        parser.set_input("P1U87 AND P2 AND ~P3 OR A94P => P4 AND (P6 OR P8)\nP5 AND P7")
        sentences = parser.parse_input()
        sentence = sentences[0]
        # Top level
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.IMPLIES, sentence.logic_operator)
        self.assertFalse(sentence.negation)
        # First Sentence
        self.assertEqual(None, sentence.first_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.OR, sentence.first_sentence.logic_operator)
        self.assertFalse(sentence.first_sentence.negation)
        # First - First
        self.assertEqual(None, sentence.first_sentence.first_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.AND, sentence.first_sentence.first_sentence.logic_operator)
        self.assertFalse(sentence.first_sentence.first_sentence.negation)
        # First - First - First
        self.assertEqual('P1U87', sentence.first_sentence.first_sentence.first_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NO_OPERATOR,
                         sentence.first_sentence.first_sentence.first_sentence.logic_operator)
        self.assertFalse(sentence.first_sentence.first_sentence.first_sentence.negation)
        # First - First - Second
        self.assertEqual(None, sentence.first_sentence.first_sentence.second_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.AND, sentence.first_sentence.first_sentence.second_sentence.logic_operator)
        self.assertFalse(sentence.first_sentence.first_sentence.second_sentence.negation)
        # First - First - Second - First
        self.assertEqual('P2', sentence.first_sentence.first_sentence.second_sentence.first_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NO_OPERATOR,
                         sentence.first_sentence.first_sentence.second_sentence.first_sentence.logic_operator)
        self.assertFalse(sentence.first_sentence.first_sentence.second_sentence.negation)
        # First - First - Second - Second
        self.assertEqual('P3', sentence.first_sentence.first_sentence.second_sentence.second_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NO_OPERATOR,
                         sentence.first_sentence.first_sentence.second_sentence.second_sentence.logic_operator)
        self.assertTrue(sentence.first_sentence.first_sentence.second_sentence.second_sentence.negation)
        # First - Second
        self.assertEqual('A94P', sentence.first_sentence.second_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NO_OPERATOR, sentence.first_sentence.second_sentence.logic_operator)
        self.assertFalse(sentence.first_sentence.second_sentence.negation)
        # Second Sentence
        self.assertEqual(None, sentence.second_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.AND, sentence.second_sentence.logic_operator)
        self.assertFalse(sentence.second_sentence.negation)
        # Second - First
        self.assertEqual('P4', sentence.second_sentence.first_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NO_OPERATOR, sentence.second_sentence.first_sentence.logic_operator)
        self.assertFalse(sentence.second_sentence.first_sentence.negation)
        # Second - Second
        self.assertEqual(None, sentence.second_sentence.second_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.OR, sentence.second_sentence.second_sentence.logic_operator)
        self.assertFalse(sentence.second_sentence.second_sentence.negation)
        self.assertEqual('P6', sentence.second_sentence.second_sentence.first_sentence.symbol)
        self.assertEqual('P8', sentence.second_sentence.second_sentence.second_sentence.symbol)

        # Line 2
        sentence = sentences[1]
        self.assertEqual('P5', sentence.first_sentence.symbol)
        self.assertFalse(sentence.first_sentence.negation)
        self.assertEqual('P7', sentence.second_sentence.symbol)
        self.assertFalse(sentence.second_sentence.negation)
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.AND, sentence.logic_operator)
        self.assertFalse(sentence.negation)

    def test_parsing_negations(self):
        parser = LogicParser("P1")
        sentence = parser.parse_line()
        self.assertEqual("P1", sentence.to_string(True))
        self.assertEqual("P1", sentence.to_string())
        parser = LogicParser("~P1")
        sentence = parser.parse_line()
        self.assertEqual("~P1", sentence.to_string(True))
        self.assertEqual("~P1", sentence.to_string())
        parser = LogicParser("~(~P1)")
        sentence = parser.parse_line()
        self.assertEqual("~(~P1)", sentence.to_string(True))
        self.assertEqual("~~P1", sentence.to_string())
        parser = LogicParser("~(~(~P1))")
        sentence = parser.parse_line()
        self.assertEqual("~(~(~P1))", sentence.to_string(True))
        self.assertEqual("~~~P1", sentence.to_string())
        parser = LogicParser("~~P1")
        sentence = parser.parse_line()
        self.assertEqual("~(~P1)", sentence.to_string(True))
        self.assertEqual("~~P1", sentence.to_string())


class TestSentence(TestCase):
    def test_create_sentence(self):
        # Test creation of an atomic sentence
        atomic_sentence1 = Sentence('P1')
        self.assertEqual('P1', atomic_sentence1.symbol)
        self.assertEqual(None, atomic_sentence1.first_sentence)
        self.assertEqual(None, atomic_sentence1.second_sentence)
        self.assertEqual(LogicOperatorTypes.NO_OPERATOR, atomic_sentence1.logic_operator)
        self.assertFalse(atomic_sentence1.negation)

        # Test creation of a negated atomic sentence
        atomic_sentence2 = Sentence('P2', negated=True)
        self.assertEqual('P2', atomic_sentence2.symbol)
        self.assertEqual(None, atomic_sentence2.first_sentence)
        self.assertEqual(None, atomic_sentence2.second_sentence)
        self.assertEqual(LogicOperatorTypes.NO_OPERATOR, atomic_sentence2.logic_operator)
        self.assertTrue(atomic_sentence2.negation)

        # Test creation of negation of a sentence
        negated_sentence = Sentence(atomic_sentence2, negated=True)
        self.assertEqual(None, negated_sentence.symbol)
        self.assertEqual(atomic_sentence2, negated_sentence.first_sentence)
        self.assertEqual(None, negated_sentence.second_sentence)
        self.assertEqual(LogicOperatorTypes.NO_OPERATOR, negated_sentence.logic_operator)
        self.assertTrue(negated_sentence.negation)
        # Check the sentence inside the sentence
        self.assertEqual('P2', negated_sentence.first_sentence.symbol)
        self.assertEqual(None, negated_sentence.first_sentence.first_sentence)
        self.assertEqual(None, negated_sentence.first_sentence.second_sentence)
        self.assertEqual(LogicOperatorTypes.NO_OPERATOR, negated_sentence.first_sentence.logic_operator)
        self.assertTrue(negated_sentence.first_sentence.negation)

        # Test creation of a complex sentence using two string tokens
        complex_sentence1 = Sentence('Q1', LogicOperatorTypes.AND, 'Q2')
        self.assertEqual(None, complex_sentence1.symbol)
        self.assertNotEqual(None, complex_sentence1.first_sentence)
        self.assertNotEqual(None, complex_sentence1.second_sentence)
        self.assertEqual(LogicOperatorTypes.AND, complex_sentence1.logic_operator)
        self.assertFalse(complex_sentence1.negation)
        # Check the sentences inside
        self.assertEqual('Q1', complex_sentence1.first_sentence.symbol)
        self.assertEqual(None, complex_sentence1.first_sentence.first_sentence)
        self.assertEqual(None, complex_sentence1.first_sentence.second_sentence)
        self.assertEqual(LogicOperatorTypes.NO_OPERATOR, complex_sentence1.first_sentence.logic_operator)
        self.assertFalse(complex_sentence1.first_sentence.negation)
        self.assertEqual('Q2', complex_sentence1.second_sentence.symbol)
        self.assertEqual(None, complex_sentence1.second_sentence.first_sentence)
        self.assertEqual(None, complex_sentence1.second_sentence.second_sentence)
        self.assertEqual(LogicOperatorTypes.NO_OPERATOR, complex_sentence1.second_sentence.logic_operator)
        self.assertFalse(complex_sentence1.second_sentence.negation)

        # Test creation of a complex sentence using two sentences
        complex_sentence2 = Sentence(atomic_sentence1, LogicOperatorTypes.OR, atomic_sentence2)
        self.assertEqual(None, complex_sentence2.symbol)
        self.assertEqual(atomic_sentence1, complex_sentence2.first_sentence)
        self.assertEqual(atomic_sentence2, complex_sentence2.second_sentence)
        self.assertEqual(LogicOperatorTypes.OR, complex_sentence2.logic_operator)
        self.assertFalse(complex_sentence2.negation)
        # Check the sentences inside
        self.assertEqual('P1', complex_sentence2.first_sentence.symbol)
        self.assertEqual(None, complex_sentence2.first_sentence.first_sentence)
        self.assertEqual(None, complex_sentence2.first_sentence.second_sentence)
        self.assertEqual(LogicOperatorTypes.NO_OPERATOR, complex_sentence2.first_sentence.logic_operator)
        self.assertFalse(complex_sentence2.first_sentence.negation)
        self.assertEqual('P2', complex_sentence2.second_sentence.symbol)
        self.assertEqual(None, complex_sentence2.second_sentence.first_sentence)
        self.assertEqual(None, complex_sentence2.second_sentence.second_sentence)
        self.assertEqual(LogicOperatorTypes.NO_OPERATOR, complex_sentence2.second_sentence.logic_operator)
        self.assertTrue(complex_sentence2.second_sentence.negation)

    def test_bad_create_sentence(self):
        failed: bool = False

        try:
            Sentence('P1')
        except SentenceError:
            failed = True
        self.assertFalse(failed)

        failed = False
        try:
            Sentence(None)
        except SentenceError:
            failed = True
        self.assertFalse(failed)

        failed = False
        try:
            Sentence(failed) # noqa
        except SentenceError:
            failed = True
        self.assertTrue(failed)

        failed = False
        try:
            Sentence('P1', LogicOperatorTypes.NO_OPERATOR, 'P2')
        except SentenceError:
            failed = True
        self.assertTrue(failed)

        failed = False
        try:
            Sentence('P1', None, 'P2')
        except SentenceError:
            failed = True
        self.assertTrue(failed)

        failed = False
        try:
            Sentence(Sentence('P1'), LogicOperatorTypes.NO_OPERATOR, Sentence('P2'))
        except SentenceError:
            failed = True
        self.assertTrue(failed)

        failed = False
        try:
            Sentence(Sentence('P1'), None, Sentence('P2'))
        except SentenceError:
            failed = True
        self.assertTrue(failed)

        failed = False
        try:
            Sentence('P1', None, 'P2')
        except SentenceError:
            failed = True
        self.assertTrue(failed)

        failed = False
        try:
            Sentence('P1', LogicOperatorTypes.AND)
        except SentenceError:
            failed = True
        self.assertTrue(failed)

        failed = False
        try:
            Sentence('P1', LogicOperatorTypes.AND, None)
        except SentenceError:
            failed = True
        self.assertTrue(failed)

        failed = False
        try:
            Sentence('P1', LogicOperatorTypes.AND, False) # noqa
        except SentenceError:
            failed = True
        self.assertTrue(failed)

        failed = False
        try:
            Sentence(Sentence("P1"), LogicOperatorTypes.AND, None)
        except SentenceError:
            failed = True
        self.assertTrue(failed)

        failed = False
        try:
            Sentence(Sentence("P1"), LogicOperatorTypes.AND)
        except SentenceError:
            failed = True
        self.assertTrue(failed)

        failed = False
        try:
            Sentence(Sentence("P1"), LogicOperatorTypes.AND, False) # noqa
        except SentenceError:
            failed = True
        self.assertTrue(failed)

    def test_is_atomic(self):
        parser = LogicParser("P1")
        sentence = parser.parse_line()
        self.assertTrue(sentence.is_atomic)
        parser = LogicParser("~P1")
        sentence = parser.parse_line()
        self.assertTrue(sentence.is_atomic)
        parser = LogicParser("P1 OR P2")
        sentence = parser.parse_line()
        self.assertFalse(sentence.is_atomic)
        parser = LogicParser("P1 AND P2")
        sentence = parser.parse_line()
        self.assertFalse(sentence.is_atomic)
        parser = LogicParser("P1 => P2")
        sentence = parser.parse_line()
        self.assertFalse(sentence.is_atomic)
        parser = LogicParser("P1 <=> P2")
        sentence = parser.parse_line()
        self.assertFalse(sentence.is_atomic)
        parser = LogicParser("~P1 AND ~P2")
        sentence = parser.parse_line()
        self.assertFalse(sentence.is_atomic)
        parser = LogicParser("~P1 OR ~P2")
        sentence = parser.parse_line()
        self.assertFalse(sentence.is_atomic)
        parser = LogicParser("~P1 AND P2")
        sentence = parser.parse_line()
        self.assertFalse(sentence.is_atomic)
        parser = LogicParser("~(P1 AND P2)")
        sentence = parser.parse_line()
        self.assertFalse(sentence.is_atomic)
        parser = LogicParser("~(P1)")
        sentence = parser.parse_line()
        self.assertTrue(sentence.is_atomic)
        parser = LogicParser("~(~(P1))")
        sentence = parser.parse_line()
        self.assertFalse(sentence.is_atomic)

    def test_sentence_to_string(self):
        parser = LogicParser("P1 AND P2 OR P3")
        sentence = parser.parse_line()
        self.assertEqual("P1 AND P2 OR P3", sentence.to_string())

        parser = LogicParser("P1 OR P2 AND P3")
        sentence = parser.parse_line()
        self.assertEqual("P1 OR P2 AND P3", sentence.to_string())

        parser = LogicParser("(P1 OR P2) AND P3")
        sentence = parser.parse_line()
        self.assertEqual("(P1 OR P2) AND P3", sentence.to_string())

        parser = LogicParser("P1 AND (P2 OR P3)")
        sentence = parser.parse_line()
        self.assertEqual("P1 AND (P2 OR P3)", sentence.to_string())

        parser = LogicParser("(P1 AND P2) OR P3")
        sentence = parser.parse_line()
        self.assertEqual("P1 AND P2 OR P3", sentence.to_string())

        parser = LogicParser("~(P1 AND P2) OR P3")
        sentence = parser.parse_line()
        self.assertEqual("~(P1 AND P2) OR P3", sentence.to_string())

        parser = LogicParser("P1 AND P2 OR (P3)")
        sentence = parser.parse_line()
        self.assertEqual("P1 AND P2 OR P3", sentence.to_string())

        parser = LogicParser("P1 AND P2 OR ~(P3)")
        sentence = parser.parse_line()
        self.assertEqual("P1 AND P2 OR ~P3", sentence.to_string())

        parser = LogicParser("(P1 => P2) AND P3")
        sentence = parser.parse_line()
        self.assertEqual("(P1 => P2) AND P3", sentence.to_string())

        parser = LogicParser("P1 => P2 AND P3")
        sentence = parser.parse_line()
        self.assertEqual("P1 => P2 AND P3", sentence.to_string())

        parser = LogicParser("P1 => P2 OR P3")
        sentence = parser.parse_line()
        self.assertEqual("P1 => P2 OR P3", sentence.to_string())

        parser = LogicParser("P1 AND U1 OR U2 => P2 OR P3 AND P4")
        sentence = parser.parse_line()
        self.assertEqual("P1 AND U1 OR U2 => P2 OR P3 AND P4", sentence.to_string())

        parser = LogicParser("P1 AND U1 OR U2 <=> P2 OR P3 AND P4")
        sentence = parser.parse_line()
        self.assertEqual("P1 AND U1 OR U2 <=> P2 OR P3 AND P4", sentence.to_string())

        parser = LogicParser("P1 AND (U1 OR U2) => (P2 OR P3) AND P4")
        sentence = parser.parse_line()
        self.assertEqual("P1 AND (U1 OR U2) => (P2 OR P3) AND P4", sentence.to_string())

        parser = LogicParser("P1 AND ~(U1 OR U2) => P2 OR ~(P3 AND P4)")
        sentence = parser.parse_line()
        self.assertEqual("P1 AND ~(U1 OR U2) => P2 OR ~(P3 AND P4)", sentence.to_string())

        parser = LogicParser("P1 AND (U1 OR U2 => P2) OR P3 AND P4")
        sentence = parser.parse_line()
        self.assertEqual("P1 AND (U1 OR U2 => P2) OR P3 AND P4", sentence.to_string())

        parser = LogicParser("P1 AND ((U1 OR U2 => P2) OR P3) AND P4")
        sentence = parser.parse_line()
        self.assertEqual("P1 AND ((U1 OR U2 => P2) OR P3) AND P4", sentence.to_string())

        parser = LogicParser("((P1 AND ((U1 OR U2 => P2) OR P3)) AND P4)")
        sentence = parser.parse_line()
        self.assertEqual("P1 AND ((U1 OR U2 => P2) OR P3) AND P4", sentence.to_string())

    def test_evaluate_sentence(self):
        parser = LogicParser("((P1 AND ((U1 OR U2 => P2) OR P3)) AND P4)")
        sentence = parser.parse_line()
        self.assertEqual("P1 AND ((U1 OR U2 => P2) OR P3) AND P4", sentence.to_string())
        model: SymbolList = sentence.get_symbol_list()
        value: LogicValue = sentence.evaluate(model)
        self.assertEqual(LogicValue.UNDEFINED, value)
        model.set_value("P1", False)
        value: LogicValue = sentence.evaluate(model)
        self.assertEqual(LogicValue.FALSE, value)
        model.set_value("P1", True)
        value: LogicValue = sentence.evaluate(model)
        self.assertEqual(LogicValue.UNDEFINED, value)
        model.set_value("P4", False)
        value: LogicValue = sentence.evaluate(model)
        self.assertEqual(LogicValue.FALSE, value)
        model.set_value("P4", True)
        value: LogicValue = sentence.evaluate(model)
        self.assertEqual(LogicValue.UNDEFINED, value)
        model.set_value("P3", False)
        value: LogicValue = sentence.evaluate(model)
        self.assertEqual(LogicValue.UNDEFINED, value)
        model.set_value("P3", False)
        value: LogicValue = sentence.evaluate(model)
        self.assertEqual(LogicValue.UNDEFINED, value)
        model.set_value("P3", True)
        value: LogicValue = sentence.evaluate(model)
        self.assertEqual(LogicValue.TRUE, value)
        model.set_value("P3", False)
        value: LogicValue = sentence.evaluate(model)
        self.assertEqual(LogicValue.UNDEFINED, value)
        model.set_value("P2", False)
        value: LogicValue = sentence.evaluate(model)
        self.assertEqual(LogicValue.UNDEFINED, value)
        model.set_value("U1", True)
        value: LogicValue = sentence.evaluate(model)
        self.assertEqual(LogicValue.FALSE, value)
        model.set_value("U1", False)
        value: LogicValue = sentence.evaluate(model)
        self.assertEqual(LogicValue.UNDEFINED, value)
        model.set_value("U2", True)
        value: LogicValue = sentence.evaluate(model)
        self.assertEqual(LogicValue.FALSE, value)
        model.set_value("U2", False)
        value: LogicValue = sentence.evaluate(model)
        self.assertEqual(LogicValue.TRUE, value)

    def test_evaluate_negation(self):
        parser = LogicParser("~((P1 AND ((U1 OR U2 => P2) OR P3)) AND P4)")
        sentence = parser.parse_line()
        self.assertEqual("~((P1 AND (((U1 OR U2) => P2) OR P3)) AND P4)", sentence.to_string(True))
        model: SymbolList = sentence.get_symbol_list()
        value: LogicValue = sentence.evaluate(model)
        self.assertEqual(LogicValue.UNDEFINED, value)
        model.set_value("P1", False)
        value: LogicValue = sentence.evaluate(model)
        self.assertEqual(LogicValue.TRUE, value)
        model.set_value("P1", True)
        value: LogicValue = sentence.evaluate(model)
        self.assertEqual(LogicValue.UNDEFINED, value)
        model.set_value("P4", False)
        value: LogicValue = sentence.evaluate(model)
        self.assertEqual(LogicValue.TRUE, value)
        model.set_value("P4", True)
        value: LogicValue = sentence.evaluate(model)
        self.assertEqual(LogicValue.UNDEFINED, value)
        model.set_value("P3", False)
        value: LogicValue = sentence.evaluate(model)
        self.assertEqual(LogicValue.UNDEFINED, value)
        model.set_value("P3", False)
        value: LogicValue = sentence.evaluate(model)
        self.assertEqual(LogicValue.UNDEFINED, value)
        model.set_value("P3", True)
        value: LogicValue = sentence.evaluate(model)
        self.assertEqual(LogicValue.FALSE, value)
        model.set_value("P3", False)
        value: LogicValue = sentence.evaluate(model)
        self.assertEqual(LogicValue.UNDEFINED, value)
        model.set_value("P2", False)
        value: LogicValue = sentence.evaluate(model)
        self.assertEqual(LogicValue.UNDEFINED, value)
        model.set_value("U1", True)
        value: LogicValue = sentence.evaluate(model)
        self.assertEqual(LogicValue.TRUE, value)
        model.set_value("U1", False)
        value: LogicValue = sentence.evaluate(model)
        self.assertEqual(LogicValue.UNDEFINED, value)
        model.set_value("U2", True)
        value: LogicValue = sentence.evaluate(model)
        self.assertEqual(LogicValue.TRUE, value)
        model.set_value("U2", False)
        value: LogicValue = sentence.evaluate(model)
        self.assertEqual(LogicValue.FALSE, value)

    def test_is_equivalent_1(self):
        # Try negating a negation on a complex sentence
        parser = LogicParser("~(~((P1 AND ((U1 OR U2 => P2) OR P3)) AND P4))")
        sentence1 = parser.parse_line()
        self.assertEqual("~(~((P1 AND (((U1 OR U2) => P2) OR P3)) AND P4))", sentence1.to_string(True))
        parser = LogicParser("((P1 AND ((U1 OR U2 => P2) OR P3)) AND P4)")
        sentence2 = parser.parse_line()
        self.assertEqual("P1 AND ((U1 OR U2 => P2) OR P3) AND P4", sentence2.to_string())
        result = sentence1.is_equivalent(sentence2)
        self.assertTrue(result)
        # Try two sentences that are not quite equivalent - make sure it fails
        parser = LogicParser("((P1 AND ((U1 OR U2 => P2) OR P3)) AND P4)")
        sentence1 = parser.parse_line()
        self.assertEqual("((P1 AND (((U1 OR U2) => P2) OR P3)) AND P4)", sentence1.to_string(True))
        parser = LogicParser("((P1 AND ((U1 OR ~U2 => P2) OR P3)) AND P4)")
        sentence2 = parser.parse_line()
        self.assertEqual("((P1 AND (((U1 OR ~U2) => P2) OR P3)) AND P4)", sentence2.to_string(True))
        result = sentence1.is_equivalent(sentence2)
        self.assertFalse(result)
        # Try various equivalents
        # Not an And-clause
        parser = LogicParser("~(P1 AND P2)")
        sentence1 = parser.parse_line()
        self.assertEqual("~(P1 AND P2)", sentence1.to_string(True))
        parser = LogicParser("~P1 OR ~P2")
        sentence2 = parser.parse_line()
        self.assertEqual("(~P1 OR ~P2)", sentence2.to_string(True))
        result = sentence1.is_equivalent(sentence2)
        self.assertTrue(result)
        # Not an Or-clause
        parser = LogicParser("~(P1 OR P2)")
        sentence1 = parser.parse_line()
        self.assertEqual("~(P1 OR P2)", sentence1.to_string(True))
        parser = LogicParser("~P1 AND ~P2")
        sentence2 = parser.parse_line()
        self.assertEqual("(~P1 AND ~P2)", sentence2.to_string(True))
        result = sentence1.is_equivalent(sentence2)
        self.assertTrue(result)
        # Implies to Or-Clause
        parser = LogicParser("A => B")
        sentence1 = parser.parse_line()
        self.assertEqual("(A => B)", sentence1.to_string(True))
        parser = LogicParser("~A OR B")
        sentence2 = parser.parse_line()
        self.assertEqual("(~A OR B)", sentence2.to_string(True))
        result = sentence1.is_equivalent(sentence2)
        self.assertTrue(result)
        # Bi-conditional to Or-Clause
        parser = LogicParser("A <=> B")
        sentence1 = parser.parse_line()
        self.assertEqual("(A <=> B)", sentence1.to_string(True))
        parser = LogicParser("(~A OR B) AND (~B OR A)")
        sentence2 = parser.parse_line()
        self.assertEqual("((~A OR B) AND (~B OR A))", sentence2.to_string(True))
        result = sentence1.is_equivalent(sentence2)
        self.assertTrue(result)

    def test_is_equivalent_2(self):
        sentence1: Sentence
        sentence2: Sentence
        sentence1 = Sentence("a => b")
        sentence2 = Sentence("A => B")
        self.assertTrue(sentence1.is_equivalent(sentence2))
        sentence1 = Sentence("a => b")
        sentence2 = Sentence("a or b")
        self.assertFalse(sentence1.is_equivalent(sentence2))
        sentence1 = Sentence("a => b")
        sentence2 = Sentence("~a or b")
        self.assertTrue(sentence1.is_equivalent(sentence2))
        sentence1 = Sentence("a <=> b")
        sentence2 = Sentence("a => b")
        self.assertFalse(sentence1.is_equivalent(sentence2))
        sentence1 = Sentence("a <=> b")
        sentence2 = Sentence("(a => b) AND (b => a)")
        self.assertTrue(sentence1.is_equivalent(sentence2))
        sentence1 = Sentence("a")
        sentence2 = Sentence("~(~a)")
        self.assertTrue(sentence1.is_equivalent(sentence2))
        sentence1 = Sentence("~(a AND b)")
        sentence2 = Sentence("~a OR ~b")
        self.assertTrue(sentence1.is_equivalent(sentence2))
        sentence1 = Sentence("~(a OR b)")
        sentence2 = Sentence("~a and ~b")
        self.assertTrue(sentence1.is_equivalent(sentence2))
        sentence1 = Sentence("a and b and c")
        sentence2 = Sentence("c and a and b")
        self.assertTrue(sentence1.is_equivalent(sentence2))
        sentence1 = Sentence("a => b")
        sentence2 = Sentence("A => B")
        self.assertTrue(sentence1 == sentence2)
        self.assertTrue(sentence1.is_equivalent("a=>b"))
        sentence1 = Sentence("a <=> b")
        sentence2 = Sentence("A => B")
        self.assertFalse(sentence1 == sentence2)
        self.assertFalse(sentence1.is_equivalent("a=>b"))

    def test_complex_sentence_constructor(self):
        sentence = Sentence("a => b", LogicOperatorTypes.IMPLIES, "c or d")
        self.assertEqual("((A => B) => (C OR D))", sentence.to_string(True))
        self.assertEqual(LogicOperatorTypes.IMPLIES, sentence.logic_operator)
        self.assertEqual(LogicOperatorTypes.IMPLIES, sentence.first_sentence.logic_operator)
        self.assertTrue(sentence.first_sentence.first_sentence.is_atomic)
        self.assertEqual('A', sentence.first_sentence.first_sentence.symbol)
        self.assertTrue(sentence.first_sentence.second_sentence.is_atomic)
        self.assertEqual('B', sentence.first_sentence.second_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.OR, sentence.second_sentence.logic_operator)
        self.assertTrue(sentence.second_sentence.first_sentence.is_atomic)
        self.assertEqual('C', sentence.second_sentence.first_sentence.symbol)
        self.assertTrue(sentence.second_sentence.second_sentence.is_atomic)
        self.assertEqual('D', sentence.second_sentence.second_sentence.symbol)

    def test_atomic_sentence(self):
        # Atomic sentence with one symbol
        sentence = Sentence("Test")
        self.assertTrue(sentence.is_atomic)
        self.assertEqual("TEST", sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NO_OPERATOR, sentence.logic_operator)
        self.assertFalse(sentence.negation)
        self.assertEqual(None, sentence.first_sentence)
        self.assertEqual(None, sentence.second_sentence)
        # Atomic sentence with no symbols
        sentence = Sentence()
        self.assertTrue(sentence.is_atomic)
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NO_OPERATOR, sentence.logic_operator)
        self.assertFalse(sentence.negation)
        self.assertEqual(None, sentence.first_sentence)
        self.assertEqual(None, sentence.second_sentence)
        # Complex sentence with no symbols
        sentence = Sentence("Test1 and Test2")
        self.assertFalse(sentence.is_atomic)
        # Illegal attempt to create an Atomic Sentence
        failed: bool = False
        try:
            Sentence(sentence1=None, logical_operator=LogicOperatorTypes.AND)
        except SentenceError:
            failed = True
        self.assertTrue(failed)
        failed = False
        try:
            Sentence(sentence1=None, sentence2="Test")
        except SentenceError:
            failed = True
        self.assertTrue(failed)

    def test_negated_sentence_construction(self):
        # Atomic negations
        sentence = Sentence("Test", negated=True)
        self.assertTrue(sentence.is_atomic)
        self.assertEqual("TEST", sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NO_OPERATOR, sentence.logic_operator)
        self.assertTrue(sentence.negation)
        self.assertEqual(None, sentence.first_sentence)
        self.assertEqual(None, sentence.second_sentence)
        sentence = Sentence("~Test")
        self.assertTrue(sentence.is_atomic)
        self.assertEqual("TEST", sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NO_OPERATOR, sentence.logic_operator)
        self.assertTrue(sentence.negation)
        self.assertEqual(None, sentence.first_sentence)
        self.assertEqual(None, sentence.second_sentence)
        # Negations on no parameters
        sentence = Sentence(negated=True)
        self.assertTrue(sentence.is_atomic)
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NO_OPERATOR, sentence.logic_operator)
        self.assertTrue(sentence.negation)
        self.assertEqual(None, sentence.first_sentence)
        self.assertEqual(None, sentence.second_sentence)
        sentence = Sentence()
        sentence.negation = True
        self.assertTrue(sentence.is_atomic)
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NO_OPERATOR, sentence.logic_operator)
        self.assertTrue(sentence.negation)
        self.assertEqual(None, sentence.first_sentence)
        self.assertEqual(None, sentence.second_sentence)
        # Complex sentence negation
        sentence = Sentence("Test1 AND TEst2", negated=True)
        self.assertFalse(sentence.is_atomic)
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.AND, sentence.logic_operator)
        self.assertTrue(sentence.negation)
        self.assertEqual("TEST1", sentence.first_sentence.to_string(True))
        self.assertEqual("TEST2", sentence.second_sentence.to_string(True))
        self.assertEqual("~(TEST1 AND TEST2)", sentence.to_string(True))
        # If you set negation to True on an already negated sentence then double negate it
        sentence = Sentence("Test1 AND TEst2", negated=False)
        sentence = Sentence(sentence, negated=True)
        self.assertFalse(sentence.is_atomic)
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.AND, sentence.logic_operator)
        self.assertTrue(sentence.negation)
        self.assertEqual("TEST1", sentence.first_sentence.symbol)
        self.assertEqual("TEST2", sentence.second_sentence.symbol)
        self.assertEqual("~(TEST1 AND TEST2)", sentence.to_string(True))
        self.assertEqual("~(TEST1 AND TEST2)", sentence.to_string())
        # Double negation using a sentence
        sentence = Sentence(sentence, negated=True)
        self.assertFalse(sentence.is_atomic)
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NO_OPERATOR, sentence.logic_operator)
        self.assertTrue(sentence.negation)
        self.assertEqual("~(TEST1 AND TEST2)", sentence.first_sentence.to_string(True))
        self.assertEqual(None, sentence.second_sentence)
        self.assertEqual("~(~(TEST1 AND TEST2))", sentence.to_string(True))
        # Not using a Sentence - double negation
        sentence = Sentence("~(Test1 AND TEst2)", negated=True)
        self.assertFalse(sentence.is_atomic)
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NO_OPERATOR, sentence.logic_operator)
        self.assertTrue(sentence.negation)
        self.assertEqual("~(TEST1 AND TEST2)", sentence.first_sentence.to_string(True))
        self.assertEqual(None, sentence.second_sentence)
        self.assertEqual("~(~(TEST1 AND TEST2))", sentence.to_string(True))
        # Not negated when not using a sentence
        sentence = Sentence("~(Test1 AND TEst2)", negated=False)
        self.assertFalse(sentence.is_atomic)
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.AND, sentence.logic_operator)
        self.assertTrue(sentence.negation)
        self.assertEqual("TEST1", sentence.first_sentence.to_string(True))
        self.assertEqual("TEST2", sentence.second_sentence.to_string(True))
        self.assertEqual("~(TEST1 AND TEST2)", sentence.to_string(True))
        # Now without negation
        sentence = Sentence("Test1 AND TEst2", negated=False)
        self.assertFalse(sentence.is_atomic)
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.AND, sentence.logic_operator)
        self.assertFalse(sentence.negation)
        self.assertEqual("TEST1", sentence.first_sentence.to_string(True))
        self.assertEqual("TEST2", sentence.second_sentence.to_string(True))
        self.assertEqual("(TEST1 AND TEST2)", sentence.to_string(True))

    def test_negated_complex_sentences(self):
        sentence = Sentence("Test1 AND TEst2 OR Test3 => TEST5 OR TEST6", negated=False)
        self.assertFalse(sentence.is_atomic)
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.IMPLIES, sentence.logic_operator)
        self.assertFalse(sentence.negation)
        self.assertEqual("((TEST1 AND TEST2) OR TEST3)", sentence.first_sentence.to_string(True))
        self.assertEqual("(TEST5 OR TEST6)", sentence.second_sentence.to_string(True))
        sentence = Sentence("Test1 AND TEst2 OR Test3 => TEST5 OR TEST6", negated=True)
        self.assertFalse(sentence.is_atomic)
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.IMPLIES, sentence.logic_operator)
        self.assertTrue(sentence.negation)
        self.assertEqual("((TEST1 AND TEST2) OR TEST3)", sentence.first_sentence.to_string(True))
        self.assertEqual("(TEST5 OR TEST6)", sentence.second_sentence.to_string(True))
        sentence = Sentence("(Test1 AND TEst2 OR Test3 => TEST5 OR TEST6)", negated=True)
        self.assertFalse(sentence.is_atomic)
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.IMPLIES, sentence.logic_operator)
        self.assertTrue(sentence.negation)
        self.assertEqual("((TEST1 AND TEST2) OR TEST3)", sentence.first_sentence.to_string(True))
        self.assertEqual("(TEST5 OR TEST6)", sentence.second_sentence.to_string(True))
        sentence = Sentence("~(Test1 AND TEst2 OR Test3 => TEST5 OR TEST6)", negated=True)
        self.assertFalse(sentence.is_atomic)
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NO_OPERATOR, sentence.logic_operator)
        self.assertTrue(sentence.negation)
        self.assertEqual("~(((TEST1 AND TEST2) OR TEST3) => (TEST5 OR TEST6))", sentence.first_sentence.to_string(True))
        self.assertEqual(None, sentence.second_sentence)

    def test_not_negated_sentence(self):
        # I.e. test putting negated = false in the constructor, which is the same as having no value
        sentence1 = Sentence("Test1 AND TEst2", negated=False)
        self.assertFalse(sentence1.is_atomic)
        self.assertEqual(None, sentence1.symbol)
        self.assertEqual(LogicOperatorTypes.AND, sentence1.logic_operator)
        self.assertFalse(sentence1.negation)
        self.assertEqual("TEST1", sentence1.first_sentence.to_string(True))
        self.assertEqual("TEST2", sentence1.second_sentence.to_string(True))
        self.assertEqual("(TEST1 AND TEST2)", sentence1.to_string(True))
        sentence2 = Sentence("Test1 AND TEst2", negated=False)
        self.assertTrue(sentence1.is_equivalent(sentence2))
        self.assertTrue(sentence2.is_equivalent(sentence1))

    def test_basic_evaluate_sentence(self):
        sentence = Sentence("A AND ~B AND (C OR D) AND E")
        model = sentence.get_symbol_list()
        # Test True
        model.set_value("A", True)
        model.set_value("B", False)
        model.set_value("C", True)
        model.set_value("D", False)
        model.set_value("E", True)
        self.assertEqual(LogicValue.TRUE, sentence.evaluate(model))
        self.assertTrue(sentence.is_true(model))
        self.assertFalse(sentence.is_false(model))
        # Test False
        model.set_value("A", True)
        model.set_value("B", True)
        model.set_value("C", False)
        model.set_value("D", True)
        model.set_value("E", True)
        self.assertEqual(LogicValue.FALSE, sentence.evaluate(model))
        self.assertFalse(sentence.is_true(model))
        self.assertTrue(sentence.is_false(model))
        # Test atomic - one symbol
        sentence = Sentence("a")
        model = sentence.get_symbol_list()
        model.set_value("A", True)
        self.assertEqual(LogicValue.TRUE, sentence.evaluate(model))
        self.assertTrue(sentence.is_true(model))
        self.assertFalse(sentence.is_false(model))
        # Negated symbol
        sentence = Sentence("~a")
        model = sentence.get_symbol_list()
        model.set_value("A", True)
        self.assertEqual(LogicValue.FALSE, sentence.evaluate(model))
        self.assertFalse(sentence.is_true(model))
        self.assertTrue(sentence.is_false(model))
        # Double negated symbol
        sentence = Sentence("~~a")
        model = sentence.get_symbol_list()
        model.set_value("A", True)
        self.assertEqual(LogicValue.TRUE, sentence.evaluate(model))
        self.assertTrue(sentence.is_true(model))
        self.assertFalse(sentence.is_false(model))

    def test_and_evaluate_sentence(self):
        sentence = Sentence("A AND B")
        model = sentence.get_symbol_list()
        # Both True
        model.set_value("a", True)
        model.set_value("b", True)
        self.assertEqual(LogicValue.TRUE, sentence.evaluate(model))
        self.assertTrue(sentence.is_true(model))
        self.assertFalse(sentence.is_false(model))
        # One True
        model.set_value("a", True)
        model.set_value("b", False)
        self.assertEqual(LogicValue.FALSE, sentence.evaluate(model))
        self.assertFalse(sentence.is_true(model))
        self.assertTrue(sentence.is_false(model))
        model.set_value("a", False)
        model.set_value("b", True)
        self.assertEqual(LogicValue.FALSE, sentence.evaluate(model))
        self.assertFalse(sentence.is_true(model))
        self.assertTrue(sentence.is_false(model))
        # Both False
        model.set_value("a", False)
        model.set_value("b", False)
        self.assertEqual(LogicValue.FALSE, sentence.evaluate(model))
        self.assertFalse(sentence.is_true(model))
        self.assertTrue(sentence.is_false(model))
        # ~(a and b)
        sentence = Sentence("~(A AND B)")
        model = sentence.get_symbol_list()
        # Both True
        model.set_value("a", True)
        model.set_value("b", True)
        self.assertEqual(LogicValue.FALSE, sentence.evaluate(model))
        self.assertFalse(sentence.is_true(model))
        self.assertTrue(sentence.is_false(model))
        # One True
        model.set_value("a", True)
        model.set_value("b", False)
        self.assertEqual(LogicValue.TRUE, sentence.evaluate(model))
        self.assertTrue(sentence.is_true(model))
        self.assertFalse(sentence.is_false(model))
        model.set_value("a", False)
        model.set_value("b", True)
        self.assertEqual(LogicValue.TRUE, sentence.evaluate(model))
        self.assertTrue(sentence.is_true(model))
        self.assertFalse(sentence.is_false(model))
        # Both False
        model.set_value("a", False)
        model.set_value("b", False)
        self.assertEqual(LogicValue.TRUE, sentence.evaluate(model))
        self.assertTrue(sentence.is_true(model))
        self.assertFalse(sentence.is_false(model))
        # ~a and ~b
        sentence = Sentence("~A AND ~B")
        model = sentence.get_symbol_list()
        # Both True
        model.set_value("a", True)
        model.set_value("b", True)
        self.assertEqual(LogicValue.FALSE, sentence.evaluate(model))
        self.assertFalse(sentence.is_true(model))
        self.assertTrue(sentence.is_false(model))
        # One True
        model.set_value("a", True)
        model.set_value("b", False)
        self.assertEqual(LogicValue.FALSE, sentence.evaluate(model))
        self.assertFalse(sentence.is_true(model))
        self.assertTrue(sentence.is_false(model))
        model.set_value("a", False)
        model.set_value("b", True)
        self.assertEqual(LogicValue.FALSE, sentence.evaluate(model))
        self.assertFalse(sentence.is_true(model))
        self.assertTrue(sentence.is_false(model))
        # Both False
        model.set_value("a", False)
        model.set_value("b", False)
        self.assertEqual(LogicValue.TRUE, sentence.evaluate(model))
        self.assertTrue(sentence.is_true(model))
        self.assertFalse(sentence.is_false(model))

    def test_or_evaluate_sentence(self):
        sentence = Sentence("A OR B")
        model = sentence.get_symbol_list()
        # Both True
        model.set_value("a", True)
        model.set_value("b", True)
        self.assertEqual(LogicValue.TRUE, sentence.evaluate(model))
        self.assertTrue(sentence.is_true(model))
        self.assertFalse(sentence.is_false(model))
        # One True
        model.set_value("a", True)
        model.set_value("b", False)
        self.assertEqual(LogicValue.TRUE, sentence.evaluate(model))
        self.assertTrue(sentence.is_true(model))
        self.assertFalse(sentence.is_false(model))
        model.set_value("a", False)
        model.set_value("b", True)
        self.assertEqual(LogicValue.TRUE, sentence.evaluate(model))
        self.assertTrue(sentence.is_true(model))
        self.assertFalse(sentence.is_false(model))
        # Both False
        model.set_value("a", False)
        model.set_value("b", False)
        self.assertEqual(LogicValue.FALSE, sentence.evaluate(model))
        self.assertFalse(sentence.is_true(model))
        self.assertTrue(sentence.is_false(model))
        # ~(a and b)
        sentence = Sentence("~(A OR B)")
        model = sentence.get_symbol_list()
        # Both True
        model.set_value("a", True)
        model.set_value("b", True)
        self.assertEqual(LogicValue.FALSE, sentence.evaluate(model))
        self.assertFalse(sentence.is_true(model))
        self.assertTrue(sentence.is_false(model))
        # One True
        model.set_value("a", True)
        model.set_value("b", False)
        self.assertEqual(LogicValue.FALSE, sentence.evaluate(model))
        self.assertFalse(sentence.is_true(model))
        self.assertTrue(sentence.is_false(model))
        model.set_value("a", False)
        model.set_value("b", True)
        self.assertEqual(LogicValue.FALSE, sentence.evaluate(model))
        self.assertFalse(sentence.is_true(model))
        self.assertTrue(sentence.is_false(model))
        # Both False
        model.set_value("a", False)
        model.set_value("b", False)
        self.assertEqual(LogicValue.TRUE, sentence.evaluate(model))
        self.assertTrue(sentence.is_true(model))
        self.assertFalse(sentence.is_false(model))
        # ~a and ~b
        sentence = Sentence("~A OR ~B")
        model = sentence.get_symbol_list()
        # Both True
        model.set_value("a", True)
        model.set_value("b", True)
        self.assertEqual(LogicValue.FALSE, sentence.evaluate(model))
        self.assertFalse(sentence.is_true(model))
        self.assertTrue(sentence.is_false(model))
        # One True
        model.set_value("a", True)
        model.set_value("b", False)
        self.assertEqual(LogicValue.TRUE, sentence.evaluate(model))
        self.assertTrue(sentence.is_true(model))
        self.assertFalse(sentence.is_false(model))
        model.set_value("a", False)
        model.set_value("b", True)
        self.assertEqual(LogicValue.TRUE, sentence.evaluate(model))
        self.assertTrue(sentence.is_true(model))
        self.assertFalse(sentence.is_false(model))
        # Both False
        model.set_value("a", False)
        model.set_value("b", False)
        self.assertEqual(LogicValue.TRUE, sentence.evaluate(model))
        self.assertTrue(sentence.is_true(model))
        self.assertFalse(sentence.is_false(model))

    def test_implies_evaluate_sentence(self):
        sentence = Sentence("a => b")
        model = sentence.get_symbol_list()
        # Both True
        model.set_value("a", True)
        model.set_value("b", True)
        self.assertEqual(LogicValue.TRUE, sentence.evaluate(model))
        self.assertTrue(sentence.is_true(model))
        self.assertFalse(sentence.is_false(model))
        # One True
        model.set_value("a", True)
        model.set_value("b", False)
        self.assertEqual(LogicValue.FALSE, sentence.evaluate(model))
        self.assertFalse(sentence.is_true(model))
        self.assertTrue(sentence.is_false(model))
        model.set_value("a", False)
        model.set_value("b", True)
        self.assertEqual(LogicValue.TRUE, sentence.evaluate(model))
        self.assertTrue(sentence.is_true(model))
        self.assertFalse(sentence.is_false(model))
        # Both False
        model.set_value("a", False)
        model.set_value("b", False)
        self.assertEqual(LogicValue.TRUE, sentence.evaluate(model))
        self.assertTrue(sentence.is_true(model))
        self.assertFalse(sentence.is_false(model))
        # Negated version
        sentence = Sentence("~(a => b)")
        model = sentence.get_symbol_list()
        # Both True
        model.set_value("a", True)
        model.set_value("b", True)
        self.assertEqual(LogicValue.FALSE, sentence.evaluate(model))
        self.assertFalse(sentence.is_true(model))
        self.assertTrue(sentence.is_false(model))
        # One True
        model.set_value("a", True)
        model.set_value("b", False)
        self.assertEqual(LogicValue.TRUE, sentence.evaluate(model))
        self.assertTrue(sentence.is_true(model))
        self.assertFalse(sentence.is_false(model))
        model.set_value("a", False)
        model.set_value("b", True)
        self.assertEqual(LogicValue.FALSE, sentence.evaluate(model))
        self.assertFalse(sentence.is_true(model))
        self.assertTrue(sentence.is_false(model))
        # Both False
        model.set_value("a", False)
        model.set_value("b", False)
        self.assertEqual(LogicValue.FALSE, sentence.evaluate(model))
        self.assertFalse(sentence.is_true(model))
        self.assertTrue(sentence.is_false(model))

    def test_bi_conditional_evaluate_sentence(self):
        sentence = Sentence("a <=> b")
        model = sentence.get_symbol_list()
        # Both True
        model.set_value("a", True)
        model.set_value("b", True)
        self.assertEqual(LogicValue.TRUE, sentence.evaluate(model))
        self.assertTrue(sentence.is_true(model))
        self.assertFalse(sentence.is_false(model))
        # One True
        model.set_value("a", True)
        model.set_value("b", False)
        self.assertEqual(LogicValue.FALSE, sentence.evaluate(model))
        self.assertFalse(sentence.is_true(model))
        self.assertTrue(sentence.is_false(model))
        model.set_value("a", False)
        model.set_value("b", True)
        self.assertEqual(LogicValue.FALSE, sentence.evaluate(model))
        self.assertFalse(sentence.is_true(model))
        self.assertTrue(sentence.is_false(model))
        # Both False
        model.set_value("a", False)
        model.set_value("b", False)
        self.assertEqual(LogicValue.TRUE, sentence.evaluate(model))
        self.assertTrue(sentence.is_true(model))
        self.assertFalse(sentence.is_false(model))
        # Negated version
        sentence = Sentence("~(a <=> b)")
        model = sentence.get_symbol_list()
        # Both True
        model.set_value("a", True)
        model.set_value("b", True)
        self.assertEqual(LogicValue.FALSE, sentence.evaluate(model))
        self.assertFalse(sentence.is_true(model))
        self.assertTrue(sentence.is_false(model))
        # One True
        model.set_value("a", True)
        model.set_value("b", False)
        self.assertEqual(LogicValue.TRUE, sentence.evaluate(model))
        self.assertTrue(sentence.is_true(model))
        self.assertFalse(sentence.is_false(model))
        model.set_value("a", False)
        model.set_value("b", True)
        self.assertEqual(LogicValue.TRUE, sentence.evaluate(model))
        self.assertTrue(sentence.is_true(model))
        self.assertFalse(sentence.is_false(model))
        # Both False
        model.set_value("a", False)
        model.set_value("b", False)
        self.assertEqual(LogicValue.FALSE, sentence.evaluate(model))
        self.assertFalse(sentence.is_true(model))
        self.assertTrue(sentence.is_false(model))

    def test_evaluate_undefined_sentence(self):
        # Ands
        sentence = Sentence("a and b and c")
        model = sentence.get_symbol_list()
        model.set_value("a", True)
        model.set_value("b", True)
        model.set_value("c", True)
        self.assertTrue(sentence.is_true(model))
        self.assertFalse(sentence.is_false(model))
        self.assertEqual(LogicValue.TRUE, sentence.evaluate(model))
        model = sentence.get_symbol_list()
        model.set_value("a", True)
        model.set_value("b", LogicValue.UNDEFINED)
        model.set_value("c", True)
        self.assertFalse(sentence.is_true(model))
        self.assertFalse(sentence.is_false(model))
        self.assertEqual(LogicValue.UNDEFINED, sentence.evaluate(model))
        # Ors
        sentence = Sentence("a or b or c")
        model = sentence.get_symbol_list()
        model.set_value("a", True)
        model.set_value("b", LogicValue.UNDEFINED)
        model.set_value("c", True)
        self.assertTrue(sentence.is_true(model))
        self.assertFalse(sentence.is_false(model))
        self.assertEqual(LogicValue.TRUE, sentence.evaluate(model))
        # Test not specifying all variables
        sentence = Sentence("a and b or c")
        model = sentence.get_symbol_list()
        model.set_value("a", True)
        model.set_value("b", False)
        self.assertFalse(sentence.is_true(model))
        self.assertFalse(sentence.is_false(model))
        self.assertEqual(LogicValue.UNDEFINED, sentence.evaluate(model))
        # Test if first part of implies is false, statement is true
        sentence = Sentence("a and b => c")
        model = sentence.get_symbol_list()
        model.set_value("a", True)
        model.set_value("b", None)
        self.assertFalse(sentence.is_true(model))
        self.assertFalse(sentence.is_false(model))
        self.assertEqual(LogicValue.UNDEFINED, sentence.evaluate(model))
        model.set_value("a", True)
        model.set_value("b", True)
        model.set_value("b", None)
        self.assertFalse(sentence.is_true(model))
        self.assertFalse(sentence.is_false(model))
        self.assertEqual(LogicValue.UNDEFINED, sentence.evaluate(model))
        model.set_value("a", False)
        model.set_value("b", True)
        model.set_value("b", None)
        self.assertTrue(sentence.is_true(model))
        self.assertFalse(sentence.is_false(model))
        self.assertEqual(LogicValue.TRUE, sentence.evaluate(model))
        # Implies: if first part is undefined, then statement is undefined, unless c is true
        model.set_value("a", True)
        model.set_value("b", None)
        model.set_value("c", True)
        self.assertTrue(sentence.is_true(model))
        self.assertFalse(sentence.is_false(model))
        self.assertEqual(LogicValue.TRUE, sentence.evaluate(model))
        model.set_value("a", True)
        model.set_value("b", None)
        model.set_value("c", False)
        self.assertFalse(sentence.is_true(model))
        self.assertFalse(sentence.is_false(model))
        self.assertEqual(LogicValue.UNDEFINED, sentence.evaluate(model))
        model.set_value("a", False)
        model.set_value("b", None)
        model.set_value("c", True)
        self.assertTrue(sentence.is_true(model))
        self.assertFalse(sentence.is_false(model))
        self.assertEqual(LogicValue.TRUE, sentence.evaluate(model))

    def test_clone_sentence(self):
        sentence1 = Sentence("a or b and c or ~k and ~~x or ~(g=>~h) <=> h and j or k or ~(u or k and ~a)")
        clone = sentence1.clone()
        self.assertEqual(sentence1.to_string(True), clone.to_string(True))
        self.assertEqual(sentence1, clone)
        self.assertTrue(sentence1 is not clone)

    def test_transform_conditionals(self):
        # Test atomic
        sentence1 = Sentence("a")
        self.assertEqual("A", sentence1.to_string())
        sentence2 = sentence1._transform_conditionals()
        self.assertEqual("A", sentence2.to_string())
        self.assertTrue(sentence1.is_equivalent(sentence2))
        self.assertTrue(sentence2.is_equivalent(sentence1))
        # Test Basic Implies
        sentence1 = Sentence("a => b")
        self.assertEqual("A => B", sentence1.to_string())
        sentence2 = sentence1._transform_conditionals()
        self.assertEqual("~A OR B", sentence2.to_string())
        self.assertTrue(sentence1.is_equivalent(sentence2))
        self.assertTrue(sentence2.is_equivalent(sentence1))
        # Test Basic Bi-Conditional
        sentence1 = Sentence("a <=> b")
        self.assertEqual("A <=> B", sentence1.to_string())
        sentence2 = sentence1._transform_conditionals()
        self.assertEqual("(~A OR B) AND (~B OR A)", sentence2.to_string())
        self.assertTrue(sentence1.is_equivalent(sentence2))
        self.assertTrue(sentence2.is_equivalent(sentence1))
        # Test Multiple Implies
        sentence1 = Sentence("(a => b) => (c => d)")
        self.assertEqual("((A => B) => (C => D))", sentence1.to_string(True))
        sentence2 = Sentence(sentence1.to_string())
        self.assertEqual("((A => B) => (C => D))", sentence2.to_string(True))
        self.assertEqual("(A => B) => (C => D)", sentence2.to_string())
        sentence3 = sentence2._transform_conditionals()
        self.assertEqual("(~(~A OR B) OR (~C OR D))", sentence3.to_string(True))
        self.assertEqual("~(~A OR B) OR ~C OR D", sentence3.to_string())
        self.assertTrue(sentence1.is_equivalent(sentence2))
        self.assertTrue(sentence2.is_equivalent(sentence3))
        self.assertTrue(sentence3.is_equivalent(sentence1))
        # Figuring out what is wrong with multiple bi-conditional a bit at a time
        sentence1 = Sentence("(a <=> b) AND (c <=> d)")
        self.assertEqual("((A <=> B) AND (C <=> D))", sentence1.to_string(True))
        sentence2 = Sentence(sentence1.to_string())
        self.assertEqual("((A <=> B) AND (C <=> D))", sentence2.to_string(True))
        self.assertEqual("(A <=> B) AND (C <=> D)", sentence2.to_string())
        sentence3 = sentence2._transform_conditionals()
        self.assertTrue(sentence1.is_equivalent(sentence2))
        self.assertTrue(sentence2.is_equivalent(sentence3))
        self.assertTrue(sentence3.is_equivalent(sentence1))
        # Found a simplified version of the problem
        sentence1 = Sentence("(A => B) AND (B => A) => C")
        self.assertEqual("(((A => B) AND (B => A)) => C)", sentence1.to_string(True))
        sentence2 = Sentence(sentence1.to_string())
        self.assertEqual("(((A => B) AND (B => A)) => C)", sentence2.to_string(True))
        self.assertEqual("(A => B) AND (B => A) => C", sentence2.to_string())
        sentence3 = sentence2._transform_conditionals()
        self.assertTrue(sentence1.is_equivalent(sentence2))
        self.assertTrue(sentence2.is_equivalent(sentence3))
        self.assertTrue(sentence3.is_equivalent(sentence1))

        sentence1 = Sentence("~(A => B)")
        self.assertEqual("~(A => B)", sentence1.to_string(True))
        sentence2 = Sentence(sentence1.to_string())
        self.assertEqual("~(A => B)", sentence2.to_string(True))
        self.assertEqual("~(A => B)", sentence2.to_string())
        sentence3 = sentence2._transform_conditionals()
        self.assertTrue(sentence1.is_equivalent(sentence2))
        self.assertTrue(sentence2.is_equivalent(sentence3))
        self.assertTrue(sentence3.is_equivalent(sentence1))

        sentence1 = Sentence("~(A <=> B)")
        self.assertEqual("~(A <=> B)", sentence1.to_string(True))
        sentence2 = Sentence(sentence1.to_string())
        self.assertEqual("~(A <=> B)", sentence2.to_string(True))
        self.assertEqual("~(A <=> B)", sentence2.to_string())
        sentence3 = Sentence("~(~A OR B) OR ~(~B OR A)")
        self.assertTrue(sentence1.is_equivalent(sentence3))

        sentence1 = Sentence("~(A <=> B)")
        self.assertEqual("~(A <=> B)", sentence1.to_string(True))
        sentence2 = Sentence(sentence1.to_string())
        self.assertEqual("~(A <=> B)", sentence2.to_string(True))
        self.assertEqual("~(A <=> B)", sentence2.to_string())
        sentence3 = sentence2._transform_conditionals()
        self.assertTrue(sentence1.is_equivalent(sentence2))
        self.assertTrue(sentence2.is_equivalent(sentence3))
        self.assertTrue(sentence3.is_equivalent(sentence1))

        sentence1 = Sentence("(a <=> b) => C")
        self.assertEqual("((A <=> B) => C)", sentence1.to_string(True))
        sentence2 = Sentence(sentence1.to_string())
        self.assertEqual("((A <=> B) => C)", sentence2.to_string(True))
        self.assertEqual("(A <=> B) => C", sentence2.to_string())
        sentence3 = sentence2._transform_conditionals()
        # self.assertEqual("", sentence3.to_string(True))
        self.assertTrue(sentence1.is_equivalent(sentence2))
        self.assertTrue(sentence2.is_equivalent(sentence3))
        self.assertTrue(sentence3.is_equivalent(sentence1))

        sentence1 = Sentence("(a <=> b) => (c <=> d)")
        self.assertEqual("((A <=> B) => (C <=> D))", sentence1.to_string(True))
        sentence2 = Sentence(sentence1.to_string())
        self.assertEqual("((A <=> B) => (C <=> D))", sentence2.to_string(True))
        self.assertEqual("(A <=> B) => (C <=> D)", sentence2.to_string())
        sentence3 = sentence2._transform_conditionals()
        self.assertTrue(sentence1.is_equivalent(sentence2))
        self.assertTrue(sentence2.is_equivalent(sentence3))
        self.assertTrue(sentence3.is_equivalent(sentence1))

        # Test Multiple Bi-Conditional
        sentence1 = Sentence("(a <=> b) <=> (c <=> d)")
        self.assertEqual("((A <=> B) <=> (C <=> D))", sentence1.to_string(True))
        sentence2 = Sentence(sentence1.to_string(True))
        self.assertTrue(sentence1.is_equivalent(sentence2))
        sentence2 = Sentence(sentence1.to_string())
        self.assertTrue(sentence1.is_equivalent(sentence2))
        self.assertEqual("((A <=> B) <=> (C <=> D))", sentence1.to_string(True))
        self.assertEqual("(A <=> B) <=> (C <=> D)", sentence1.to_string())
        sentence3 = Sentence("(~((~A OR B) AND (~B OR A)) OR (~C OR D) AND (~D OR C)) AND (~((~C OR D) " +
                             "AND (~D OR C)) OR (~A OR B) AND (~B OR A))")  # Hand check
        self.assertTrue(sentence1.is_equivalent(sentence3))
        sentence4 = sentence1._transform_conditionals()
        self.assertTrue(sentence1.is_equivalent(sentence4))

    def test_move_not_inward(self):
        # Test atomic
        sentence1 = Sentence("a")
        self.assertEqual("A", sentence1.to_string())
        sentence2 = sentence1._move_not_inward()
        self.assertEqual("~A", sentence2.to_string())
        self.assertFalse(sentence1 == sentence2)
        sentence1 = Sentence("~a")
        self.assertEqual("~A", sentence1.to_string())
        sentence2 = sentence1._move_not_inward()
        self.assertEqual("A", sentence2.to_string())
        self.assertFalse(sentence1 == sentence2)
        # Test Complex
        sentence1 = Sentence("~(A AND B)")
        self.assertEqual("~(A AND B)", sentence1.to_string())
        self.assertEqual(LogicOperatorTypes.AND, sentence1.logic_operator)
        sentence2 = sentence1._move_not_inward()
        self.assertEqual("A AND B", sentence2.to_string())
        self.assertFalse(sentence1 == sentence2)
        # Test not sentence
        sentence1 = Sentence("A and B", negated=True)
        self.assertEqual(LogicOperatorTypes.AND, sentence1.logic_operator)
        self.assertEqual("~(A AND B)", sentence1.to_string())
        sentence2 = sentence1._move_not_inward()
        self.assertEqual("A AND B", sentence2.to_string())
        self.assertFalse(sentence1 == sentence2)
        # Double Not
        sentence1 = Sentence("~(A and B)", negated=True)
        self.assertEqual(LogicOperatorTypes.NO_OPERATOR, sentence1.logic_operator)
        self.assertEqual("~~(A AND B)", sentence1.to_string())
        sentence2 = sentence1._move_not_inward()
        self.assertEqual("~(A AND B)", sentence2.to_string())
        self.assertEqual(LogicOperatorTypes.AND, sentence2.logic_operator)
        sentence1 = Sentence("~A", negated=True)
        self.assertEqual(LogicOperatorTypes.NO_OPERATOR, sentence1.logic_operator)
        self.assertTrue(sentence1.first_sentence is not None)
        self.assertEqual("~~A", sentence1.to_string())
        sentence2 = sentence1._move_not_inward()
        self.assertEqual("~A", sentence2.to_string())
        self.assertEqual(LogicOperatorTypes.NO_OPERATOR, sentence2.logic_operator)
        self.assertTrue(sentence2.first_sentence is None)

    def test_transform_not(self):
        # Test atomic
        sentence1 = Sentence("a")
        self.assertEqual("A", sentence1.to_string())
        sentence2 = sentence1._transform_not()
        self.assertEqual("A", sentence2.to_string())
        self.assertTrue(sentence1 == sentence2)
        sentence1 = Sentence("~a")
        self.assertEqual("~A", sentence1.to_string())
        sentence2 = sentence1._transform_not()
        self.assertEqual("~A", sentence2.to_string())
        self.assertTrue(sentence1 == sentence2)
        # Test Complex
        # No not
        sentence1 = Sentence("a and b")
        self.assertEqual("A AND B", sentence1.to_string())
        sentence2 = sentence1._transform_not()
        self.assertEqual("A AND B", sentence2.to_string())
        self.assertTrue(sentence1 == sentence2)
        # With a not and phrase
        sentence1 = Sentence("~(a and b)")
        self.assertEqual("~(A AND B)", sentence1.to_string())
        sentence2 = sentence1._transform_not()
        self.assertEqual("~A OR ~B", sentence2.to_string())
        self.assertTrue(sentence1 == sentence2)
        # With a not or phrase
        sentence1 = Sentence("~(a or b)")
        self.assertEqual("~(A OR B)", sentence1.to_string())
        sentence2 = sentence1._transform_not()
        self.assertEqual("~A AND ~B", sentence2.to_string())
        self.assertTrue(sentence1 == sentence2)
        # With a double negated phrase - OR
        sentence1 = Sentence("~(a or b)", negated=True)
        self.assertEqual("~~(A OR B)", sentence1.to_string())
        sentence2 = sentence1._transform_not()
        self.assertEqual("A OR B", sentence2.to_string())
        self.assertTrue(sentence1 == sentence2)
        # With a double negated phrase - AND
        sentence1 = Sentence("~(a and b)", negated=True)
        self.assertEqual("~~(A AND B)", sentence1.to_string())
        sentence2 = sentence1._transform_not()
        self.assertEqual("A AND B", sentence2.to_string())
        self.assertTrue(sentence1 == sentence2)
        # Two levels of AND and OR mixed
        sentence1 = Sentence("~(a and b) and (c or d) and e")
        self.assertEqual("~(A AND B) AND (C OR D) AND E", sentence1.to_string())
        sentence2 = sentence1._transform_not()
        self.assertEqual("(~A OR ~B) AND (C OR D) AND E", sentence2.to_string())
        self.assertTrue(sentence1 == sentence2)
        # Two levels of AND and OR mixed - negated
        sentence1 = Sentence("~(a and b) and (c or d) and e", negated=True)
        self.assertEqual("~(~(A AND B) AND (C OR D) AND E)", sentence1.to_string())
        sentence2 = sentence1._transform_not()
        self.assertEqual("A AND B OR ~C AND ~D OR ~E", sentence2.to_string())
        self.assertTrue(sentence1 == sentence2)

    def test_redistribute_or(self):
        sentence1 = Sentence("A AND B")
        or_clause = Sentence("C OR D")
        sentence2 = sentence1._redistribute_or(or_clause)
        self.assertEqual("(A OR C OR D) AND (B OR C OR D)", sentence2.to_string())

    def test_transform_distribute_ors(self):
        # Simple example
        sentence1 = Sentence("(A AND B) OR C")
        self.assertEqual("((A AND B) OR C)", sentence1.to_string(True))
        sentence2 = sentence1._transform_distribute_ors()
        self.assertEqual("(A OR C) AND (B OR C)", sentence2.to_string())
        self.assertTrue(sentence1 == sentence2)
        # Complex example
        sentence1 = Sentence("(A AND B) OR (C AND D)")
        self.assertEqual("((A AND B) OR (C AND D))", sentence1.to_string(True))
        sentence2 = sentence1._transform_distribute_ors()
        self.assertEqual("(C OR A) AND (D OR A) AND (C OR B) AND (D OR B)", sentence2.to_string())
        self.assertTrue(sentence1 == sentence2)
        # Very complex example
        sentence1 = Sentence("(A AND B) OR (C AND D) AND D OR E AND (Q OR T) OR (C AND Z)")
        sentence2 = sentence1._transform_distribute_ors()
        self.assertTrue(sentence1 == sentence2)

    def test_convert_to_cnf(self):
        # Final test on transform_not
        sentence1 = Sentence("~(a and b) and (c or d) and e")
        self.assertEqual("~(A AND B) AND (C OR D) AND E", sentence1.to_string())
        sentence2 = sentence1.convert_to_cnf()
        self.assertTrue(sentence1 == sentence2)
        # Final test on transform_conditionals
        # Test Multiple Bi-Conditional
        sentence1 = Sentence("(a <=> b) <=> (c <=> d)")
        self.assertEqual("((A <=> B) <=> (C <=> D))", sentence1.to_string(True))
        sentence2 = Sentence(sentence1.to_string(True))
        self.assertTrue(sentence1.is_equivalent(sentence2))
        sentence2 = Sentence(sentence1.to_string())
        self.assertTrue(sentence1.is_equivalent(sentence2))
        self.assertEqual("((A <=> B) <=> (C <=> D))", sentence1.to_string(True))
        self.assertEqual("(A <=> B) <=> (C <=> D)", sentence1.to_string())
        sentence3 = Sentence("(~((~A OR B) AND (~B OR A)) OR (~C OR D) AND (~D OR C)) AND (~((~C OR D) " +
                             "AND (~D OR C)) OR (~A OR B) AND (~B OR A))")  # Hand check
        self.assertTrue(sentence1 == sentence3)
        sentence4 = sentence1.convert_to_cnf()
        self.assertTrue(sentence1 == sentence4)
        # Test negated complex sentence with only one symbol
        sentence1 = Sentence("~w or w")
        sentence1.negate_sentence()
        sentence1 = sentence1.convert_to_cnf()
        self.assertEqual("W AND ~W", sentence1.to_string())

    def test_is_valid_cnf(self):
        # Test atomic
        sentence1 = Sentence("A")
        self.assertEqual("A", sentence1.to_string(True))
        sentence2 = sentence1.convert_to_cnf()
        self.assertFalse(sentence1.is_cnf)
        self.assertTrue(sentence2.is_cnf)
        self.assertEqual("A", sentence2.to_string())
        self.assertTrue(sentence1 == sentence2)
        self.assertTrue(sentence1.is_valid_cnf())
        self.assertTrue(sentence2.is_valid_cnf())
        self.assertTrue(sentence1.is_cnf)
        self.assertTrue(sentence2.is_cnf)
        # Basic tests
        sentence1 = Sentence("A AND B")
        self.assertEqual("(A AND B)", sentence1.to_string(True))
        sentence2 = sentence1.convert_to_cnf()
        self.assertEqual("A AND B", sentence2.to_string())
        self.assertTrue(sentence1 == sentence2)
        self.assertTrue(sentence1.is_valid_cnf())
        self.assertTrue(sentence2.is_valid_cnf())
        self.assertTrue(sentence1.is_cnf)
        self.assertTrue(sentence2.is_cnf)
        # Not version
        sentence1 = Sentence("~(A AND B)")
        self.assertEqual("~(A AND B)", sentence1.to_string(True))
        sentence2 = sentence1.convert_to_cnf()
        self.assertEqual("~A OR ~B", sentence2.to_string())
        self.assertTrue(sentence1 == sentence2)
        self.assertFalse(sentence1.is_valid_cnf())
        self.assertTrue(sentence2.is_valid_cnf())
        self.assertFalse(sentence1.is_cnf)
        self.assertTrue(sentence2.is_cnf)
        # Slightly more complicated
        sentence1 = Sentence("(A AND B) OR C OR D AND E")
        sentence2 = sentence1._transform_distribute_ors()
        sentence3 = sentence1.convert_to_cnf()
        self.assertTrue(sentence1 == sentence2 == sentence3)
        self.assertFalse(sentence1.is_valid_cnf())
        self.assertFalse(sentence2.is_valid_cnf())
        self.assertTrue(sentence3.is_valid_cnf())
        self.assertFalse(sentence1.is_cnf)
        self.assertFalse(sentence2.is_cnf)
        self.assertTrue(sentence3.is_cnf)
        # Complex example
        sentence1 = Sentence("(A AND B) OR (C AND D)")
        self.assertEqual("((A AND B) OR (C AND D))", sentence1.to_string(True))
        sentence2 = sentence1.convert_to_cnf()
        self.assertEqual("(C OR A) AND (D OR A) AND (C OR B) AND (D OR B)", sentence2.to_string())
        self.assertTrue(sentence1 == sentence2)
        self.assertFalse(sentence1.is_valid_cnf())
        self.assertTrue(sentence2.is_valid_cnf())
        self.assertFalse(sentence1.is_cnf)
        self.assertTrue(sentence2.is_cnf)
        # # Very complex example - Too slow to use normally
        # sentence1 = Sentence("(A AND B) OR (C AND D) AND D OR E AND (Q OR T) OR (C AND Z)")
        # sentence2 = sentence1._transform_distribute_ors()
        # sentence3 = sentence1.convert_to_cnf()
        # self.assertTrue(sentence1 == sentence2 == sentence3)
        # self.assertFalse(sentence1.is_valid_cnf())
        # self.assertFalse(sentence2.is_valid_cnf())
        # self.assertTrue(sentence3.is_valid_cnf())
        # self.assertFalse(sentence1.is_cnf)
        # self.assertFalse(sentence2.is_cnf)
        # self.assertTrue(sentence3.is_cnf)

    def test_evaluate_sentence_not_in_model(self):
        # I have mixed feelings over how I handled this.
        #  These are clearly True or False, but right now come back Undefined
        sentence = Sentence("Y and ~Y")
        model = sentence.get_symbol_list()
        self.assertEqual(LogicValue.UNDEFINED, sentence.evaluate(model))
        sentence = Sentence("Y OR ~Y")
        model = sentence.get_symbol_list()
        self.assertEqual(LogicValue.UNDEFINED, sentence.evaluate(model))
