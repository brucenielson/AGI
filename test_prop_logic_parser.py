from unittest import TestCase
from prop_logic_parser import PropLogicParser, Sentence, LogicOperatorTypes, SentenceError


class TestPropLogicParser(TestCase):
    def test_pyparsing(self):
        parser = PropLogicParser("P1U87 AND P2 AND ~P3 OR A94P => P4 AND (P6 OR P8)\nP5 AND P7")
        correct_result = [
            ['P1U87', 'AND', 'P2', 'AND', '~', 'P3', 'OR', 'A94P', '=>', 'P4', 'AND', '(', 'P6', 'OR', 'P8', ')'],
            ['P5', 'AND', 'P7']]
        self.assertEqual(correct_result, parser.token_list)

    def test_current_token(self):
        parser = PropLogicParser("P1U87 AND P2 AND ~P3 OR A94P => P4 AND (P6 OR P8)\nP5 AND P7")
        self.assertEqual('P1U87', parser.current_token)

    def test_consume_token(self):
        parser = PropLogicParser("P1U87 AND P2 AND ~P3 OR A94P => P4 AND (P6 OR P8)\nP5 AND P7")
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
        parser = PropLogicParser("P1")
        sentence = parser.parse_line()
        self.assertEqual(None, sentence.first_sentence)
        self.assertEqual(None, sentence.second_sentence)
        self.assertEqual('P1', sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NoOperator, sentence.logic_operator)
        self.assertEqual(False, sentence.negation)

        parser = PropLogicParser("P1 AND P2")
        sentence = parser.parse_line()
        self.assertEqual('P1', sentence.first_sentence.symbol)
        self.assertEqual(False, sentence.first_sentence.negation)
        self.assertEqual('P2', sentence.second_sentence.symbol)
        self.assertEqual(False, sentence.second_sentence.negation)
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.And, sentence.logic_operator)
        self.assertEqual(False, sentence.negation)

        parser = PropLogicParser("P1 OR P2")
        sentence = parser.parse_line()
        self.assertEqual('P1', sentence.first_sentence.symbol)
        self.assertEqual(False, sentence.first_sentence.negation)
        self.assertEqual('P2', sentence.second_sentence.symbol)
        self.assertEqual(False, sentence.second_sentence.negation)
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.Or, sentence.logic_operator)
        self.assertEqual(False, sentence.negation)

        parser = PropLogicParser("~P1")
        sentence = parser.parse_line()
        self.assertEqual(None, sentence.first_sentence)
        self.assertEqual(None, sentence.second_sentence)
        self.assertEqual('P1', sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NoOperator, sentence.logic_operator)
        self.assertEqual(True, sentence.negation)

        parser = PropLogicParser("~(P1 AND P2)")
        sentence = parser.parse_line()
        self.assertEqual('P1', sentence.first_sentence.symbol)
        self.assertEqual(False, sentence.first_sentence.negation)
        self.assertEqual('P2', sentence.second_sentence.symbol)
        self.assertEqual(False, sentence.second_sentence.negation)
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.And, sentence.logic_operator)
        self.assertEqual(True, sentence.negation)

        parser = PropLogicParser("~(P1 OR P2)")
        sentence = parser.parse_line()
        self.assertEqual('P1', sentence.first_sentence.symbol)
        self.assertEqual(False, sentence.first_sentence.negation)
        self.assertEqual('P2', sentence.second_sentence.symbol)
        self.assertEqual(False, sentence.second_sentence.negation)
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.Or, sentence.logic_operator)
        self.assertEqual(True, sentence.negation)

        parser = PropLogicParser("~P1 AND P2")
        sentence = parser.parse_line()
        self.assertEqual('P1', sentence.first_sentence.symbol)
        self.assertEqual(True, sentence.first_sentence.negation)
        self.assertEqual('P2', sentence.second_sentence.symbol)
        self.assertEqual(False, sentence.second_sentence.negation)
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.And, sentence.logic_operator)
        self.assertEqual(False, sentence.negation)

        parser = PropLogicParser("~P1 OR P2")
        sentence = parser.parse_line()
        self.assertEqual('P1', sentence.first_sentence.symbol)
        self.assertEqual(True, sentence.first_sentence.negation)
        self.assertEqual('P2', sentence.second_sentence.symbol)
        self.assertEqual(False, sentence.second_sentence.negation)
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.Or, sentence.logic_operator)
        self.assertEqual(False, sentence.negation)

        parser = PropLogicParser("P1 AND ~P2")
        sentence = parser.parse_line()
        self.assertEqual('P1', sentence.first_sentence.symbol)
        self.assertEqual(False, sentence.first_sentence.negation)
        self.assertEqual('P2', sentence.second_sentence.symbol)
        self.assertEqual(True, sentence.second_sentence.negation)
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.And, sentence.logic_operator)
        self.assertEqual(False, sentence.negation)

        parser = PropLogicParser("P1 OR ~P2")
        sentence = parser.parse_line()
        self.assertEqual('P1', sentence.first_sentence.symbol)
        self.assertEqual(False, sentence.first_sentence.negation)
        self.assertEqual('P2', sentence.second_sentence.symbol)
        self.assertEqual(True, sentence.second_sentence.negation)
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.Or, sentence.logic_operator)
        self.assertEqual(False, sentence.negation)

    # noinspection SpellCheckingInspection
    def test_simple_implications_biconditionals(self):
        parser = PropLogicParser("P1 => P2")
        sentence = parser.parse_line()
        self.assertEqual('P1', sentence.first_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NoOperator, sentence.first_sentence.logic_operator)
        self.assertEqual(False, sentence.first_sentence.negation)
        self.assertEqual('P2', sentence.second_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NoOperator, sentence.second_sentence.logic_operator)
        self.assertEqual(False, sentence.second_sentence.negation)
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.Implies, sentence.logic_operator)
        self.assertEqual(False, sentence.negation)

        parser = PropLogicParser("~P1 <=> P2")
        sentence = parser.parse_line()
        self.assertEqual('P1', sentence.first_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NoOperator, sentence.first_sentence.logic_operator)
        self.assertEqual(True, sentence.first_sentence.negation)
        self.assertEqual('P2', sentence.second_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NoOperator, sentence.second_sentence.logic_operator)
        self.assertEqual(False, sentence.second_sentence.negation)
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.Biconditional, sentence.logic_operator)
        self.assertEqual(False, sentence.negation)

        parser = PropLogicParser("P1 <=> ~P2")
        sentence = parser.parse_line()
        self.assertEqual('P1', sentence.first_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NoOperator, sentence.first_sentence.logic_operator)
        self.assertEqual(False, sentence.first_sentence.negation)
        self.assertEqual('P2', sentence.second_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NoOperator, sentence.second_sentence.logic_operator)
        self.assertEqual(True, sentence.second_sentence.negation)
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.Biconditional, sentence.logic_operator)
        self.assertEqual(False, sentence.negation)

        parser = PropLogicParser("P1 <=> P2")
        sentence = parser.parse_line()
        self.assertEqual('P1', sentence.first_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NoOperator, sentence.first_sentence.logic_operator)
        self.assertEqual(False, sentence.first_sentence.negation)
        self.assertEqual('P2', sentence.second_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NoOperator, sentence.second_sentence.logic_operator)
        self.assertEqual(False, sentence.second_sentence.negation)
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.Biconditional, sentence.logic_operator)
        self.assertEqual(False, sentence.negation)

        parser = PropLogicParser("~P1 <=> P2")
        sentence = parser.parse_line()
        self.assertEqual('P1', sentence.first_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NoOperator, sentence.first_sentence.logic_operator)
        self.assertEqual(True, sentence.first_sentence.negation)
        self.assertEqual('P2', sentence.second_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NoOperator, sentence.second_sentence.logic_operator)
        self.assertEqual(False, sentence.second_sentence.negation)
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.Biconditional, sentence.logic_operator)
        self.assertEqual(False, sentence.negation)

        parser = PropLogicParser("P1 <=> ~P2")
        sentence = parser.parse_line()
        self.assertEqual('P1', sentence.first_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NoOperator, sentence.first_sentence.logic_operator)
        self.assertEqual(False, sentence.first_sentence.negation)
        self.assertEqual('P2', sentence.second_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NoOperator, sentence.second_sentence.logic_operator)
        self.assertEqual(True, sentence.second_sentence.negation)
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.Biconditional, sentence.logic_operator)
        self.assertEqual(False, sentence.negation)

    # noinspection SpellCheckingInspection
    def test_complex_implications_biconditionals(self):
        parser = PropLogicParser("P1 AND P3 => P2 AND P4")
        sentence = parser.parse_line()
        self.assertEqual(None, sentence.first_sentence.symbol)
        self.assertEqual(False, sentence.first_sentence.negation)
        self.assertEqual('P1', sentence.first_sentence.first_sentence.symbol)
        self.assertEqual(False, sentence.first_sentence.first_sentence.negation)
        self.assertEqual('P3', sentence.first_sentence.second_sentence.symbol)
        self.assertEqual(False, sentence.first_sentence.first_sentence.negation)
        self.assertEqual(None, sentence.second_sentence.symbol)
        self.assertEqual(False, sentence.second_sentence.negation)
        self.assertEqual('P2', sentence.second_sentence.first_sentence.symbol)
        self.assertEqual(False, sentence.second_sentence.first_sentence.negation)
        self.assertEqual('P4', sentence.second_sentence.second_sentence.symbol)
        self.assertEqual(False, sentence.second_sentence.first_sentence.negation)
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.Implies, sentence.logic_operator)
        self.assertEqual(False, sentence.negation)

        parser = PropLogicParser("P1 AND P3 <=> P2 AND P4")
        sentence = parser.parse_line()
        self.assertEqual(None, sentence.first_sentence.symbol)
        self.assertEqual(False, sentence.first_sentence.negation)
        self.assertEqual('P1', sentence.first_sentence.first_sentence.symbol)
        self.assertEqual(False, sentence.first_sentence.first_sentence.negation)
        self.assertEqual('P3', sentence.first_sentence.second_sentence.symbol)
        self.assertEqual(False, sentence.first_sentence.first_sentence.negation)
        self.assertEqual(None, sentence.second_sentence.symbol)
        self.assertEqual(False, sentence.second_sentence.negation)
        self.assertEqual('P2', sentence.second_sentence.first_sentence.symbol)
        self.assertEqual(False, sentence.second_sentence.first_sentence.negation)
        self.assertEqual('P4', sentence.second_sentence.second_sentence.symbol)
        self.assertEqual(False, sentence.second_sentence.first_sentence.negation)
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.Biconditional, sentence.logic_operator)
        self.assertEqual(False, sentence.negation)

        parser = PropLogicParser("(P1 AND P3) => (P2 AND P4)")
        sentence = parser.parse_line()
        self.assertEqual(None, sentence.first_sentence.symbol)
        self.assertEqual(False, sentence.first_sentence.negation)
        self.assertEqual('P1', sentence.first_sentence.first_sentence.symbol)
        self.assertEqual(False, sentence.first_sentence.first_sentence.negation)
        self.assertEqual('P3', sentence.first_sentence.second_sentence.symbol)
        self.assertEqual(False, sentence.first_sentence.first_sentence.negation)
        self.assertEqual(None, sentence.second_sentence.symbol)
        self.assertEqual(False, sentence.second_sentence.negation)
        self.assertEqual('P2', sentence.second_sentence.first_sentence.symbol)
        self.assertEqual(False, sentence.second_sentence.first_sentence.negation)
        self.assertEqual('P4', sentence.second_sentence.second_sentence.symbol)
        self.assertEqual(False, sentence.second_sentence.first_sentence.negation)
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.Implies, sentence.logic_operator)
        self.assertEqual(False, sentence.negation)

        parser = PropLogicParser("(P1 AND P3) <=> (P2 AND P4)")
        sentence = parser.parse_line()
        self.assertEqual(None, sentence.first_sentence.symbol)
        self.assertEqual(False, sentence.first_sentence.negation)
        self.assertEqual('P1', sentence.first_sentence.first_sentence.symbol)
        self.assertEqual(False, sentence.first_sentence.first_sentence.negation)
        self.assertEqual('P3', sentence.first_sentence.second_sentence.symbol)
        self.assertEqual(False, sentence.first_sentence.first_sentence.negation)
        self.assertEqual(None, sentence.second_sentence.symbol)
        self.assertEqual(False, sentence.second_sentence.negation)
        self.assertEqual('P2', sentence.second_sentence.first_sentence.symbol)
        self.assertEqual(False, sentence.second_sentence.first_sentence.negation)
        self.assertEqual('P4', sentence.second_sentence.second_sentence.symbol)
        self.assertEqual(False, sentence.second_sentence.first_sentence.negation)
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.Biconditional, sentence.logic_operator)
        self.assertEqual(False, sentence.negation)

        parser = PropLogicParser("~(P1 AND P3) => ~(P2 AND P4)")
        sentence = parser.parse_line()
        self.assertEqual(None, sentence.first_sentence.symbol)
        self.assertEqual(True, sentence.first_sentence.negation)
        self.assertEqual('P1', sentence.first_sentence.first_sentence.symbol)
        self.assertEqual(False, sentence.first_sentence.first_sentence.negation)
        self.assertEqual('P3', sentence.first_sentence.second_sentence.symbol)
        self.assertEqual(False, sentence.first_sentence.first_sentence.negation)
        self.assertEqual(None, sentence.second_sentence.symbol)
        self.assertEqual(True, sentence.second_sentence.negation)
        self.assertEqual('P2', sentence.second_sentence.first_sentence.symbol)
        self.assertEqual(False, sentence.second_sentence.first_sentence.negation)
        self.assertEqual('P4', sentence.second_sentence.second_sentence.symbol)
        self.assertEqual(False, sentence.second_sentence.first_sentence.negation)
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.Implies, sentence.logic_operator)
        self.assertEqual(False, sentence.negation)

        parser = PropLogicParser("~(P1 AND P3) <=> ~(P2 AND P4)")
        sentence = parser.parse_line()
        self.assertEqual(None, sentence.first_sentence.symbol)
        self.assertEqual(True, sentence.first_sentence.negation)
        self.assertEqual('P1', sentence.first_sentence.first_sentence.symbol)
        self.assertEqual(False, sentence.first_sentence.first_sentence.negation)
        self.assertEqual('P3', sentence.first_sentence.second_sentence.symbol)
        self.assertEqual(False, sentence.first_sentence.first_sentence.negation)
        self.assertEqual(None, sentence.second_sentence.symbol)
        self.assertEqual(True, sentence.second_sentence.negation)
        self.assertEqual('P2', sentence.second_sentence.first_sentence.symbol)
        self.assertEqual(False, sentence.second_sentence.first_sentence.negation)
        self.assertEqual('P4', sentence.second_sentence.second_sentence.symbol)
        self.assertEqual(False, sentence.second_sentence.first_sentence.negation)
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.Biconditional, sentence.logic_operator)
        self.assertEqual(False, sentence.negation)

    def test_simple_and_or_priority(self):
        parser = PropLogicParser("P1 AND P2 OR P3")
        sentence = parser.parse_line()
        # Top level
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.Or, sentence.logic_operator)
        self.assertEqual(False, sentence.negation)
        # First sentence
        self.assertEqual(None, sentence.first_sentence.symbol)
        self.assertEqual(False, sentence.first_sentence.negation)
        self.assertEqual(LogicOperatorTypes.And, sentence.first_sentence.logic_operator)

        self.assertEqual('P1', sentence.first_sentence.first_sentence.symbol)
        self.assertEqual(False, sentence.first_sentence.first_sentence.negation)
        self.assertEqual(LogicOperatorTypes.NoOperator, sentence.first_sentence.first_sentence.logic_operator)

        self.assertEqual('P2', sentence.first_sentence.second_sentence.symbol)
        self.assertEqual(False, sentence.first_sentence.second_sentence.negation)
        self.assertEqual(LogicOperatorTypes.NoOperator, sentence.first_sentence.second_sentence.logic_operator)

        # Second sentence
        self.assertEqual('P3', sentence.second_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NoOperator, sentence.second_sentence.logic_operator)
        self.assertEqual(False, sentence.second_sentence.negation)

        parser = PropLogicParser("P1 OR P2 AND P3")
        sentence = parser.parse_line()
        # Top level
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.Or, sentence.logic_operator)
        self.assertEqual(False, sentence.negation)
        # First sentence
        self.assertEqual('P1', sentence.first_sentence.symbol)
        self.assertEqual(False, sentence.first_sentence.negation)
        self.assertEqual(LogicOperatorTypes.NoOperator, sentence.first_sentence.logic_operator)
        self.assertEqual(None, sentence.first_sentence.first_sentence)
        self.assertEqual(None, sentence.first_sentence.second_sentence)
        # Second sentence
        self.assertEqual(LogicOperatorTypes.And, sentence.second_sentence.logic_operator)
        self.assertEqual(False, sentence.second_sentence.negation)
        self.assertEqual('P2', sentence.second_sentence.first_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NoOperator, sentence.second_sentence.first_sentence.logic_operator)
        self.assertEqual(False, sentence.second_sentence.first_sentence.negation)
        self.assertEqual('P3', sentence.second_sentence.second_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NoOperator, sentence.second_sentence.second_sentence.logic_operator)
        self.assertEqual(False, sentence.second_sentence.second_sentence.negation)
        self.assertEqual(False, sentence.second_sentence.second_sentence.negation)

    def test_string_of_ands(self):
        parser = PropLogicParser("P1 AND P2 AND P3")
        sentence = parser.parse_line()
        # Top level
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.And, sentence.logic_operator)
        self.assertEqual(False, sentence.negation)
        # First sentence
        self.assertEqual('P1', sentence.first_sentence.symbol)
        self.assertEqual(False, sentence.first_sentence.negation)
        self.assertEqual(LogicOperatorTypes.NoOperator, sentence.first_sentence.logic_operator)
        # Second sentence
        self.assertEqual(None, sentence.second_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.And, sentence.second_sentence.logic_operator)
        self.assertEqual(False, sentence.second_sentence.negation)
        self.assertEqual('P2', sentence.second_sentence.first_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NoOperator, sentence.second_sentence.first_sentence.logic_operator)
        self.assertEqual(False, sentence.second_sentence.first_sentence.negation)
        self.assertEqual('P3', sentence.second_sentence.second_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NoOperator, sentence.second_sentence.second_sentence.logic_operator)
        self.assertEqual(False, sentence.second_sentence.second_sentence.negation)

        parser = PropLogicParser("P1 AND (P2 AND P3)")
        sentence = parser.parse_line()
        # Top level
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.And, sentence.logic_operator)
        self.assertEqual(False, sentence.negation)
        # First sentence
        self.assertEqual('P1', sentence.first_sentence.symbol)
        self.assertEqual(False, sentence.first_sentence.negation)
        self.assertEqual(LogicOperatorTypes.NoOperator, sentence.first_sentence.logic_operator)
        # Second sentence
        self.assertEqual(None, sentence.second_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.And, sentence.second_sentence.logic_operator)
        self.assertEqual(False, sentence.second_sentence.negation)
        self.assertEqual('P2', sentence.second_sentence.first_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NoOperator, sentence.second_sentence.first_sentence.logic_operator)
        self.assertEqual(False, sentence.second_sentence.first_sentence.negation)
        self.assertEqual('P3', sentence.second_sentence.second_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NoOperator, sentence.second_sentence.second_sentence.logic_operator)
        self.assertEqual(False, sentence.second_sentence.second_sentence.negation)

        parser = PropLogicParser("(P1 AND P2) AND P3")
        sentence = parser.parse_line()
        # Top level
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.And, sentence.logic_operator)
        self.assertEqual(False, sentence.negation)
        # First sentence
        self.assertEqual(None, sentence.first_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.And, sentence.first_sentence.logic_operator)
        self.assertEqual(False, sentence.negation)

        self.assertEqual('P1', sentence.first_sentence.first_sentence.symbol)
        self.assertEqual(False, sentence.first_sentence.first_sentence.negation)
        self.assertEqual(LogicOperatorTypes.NoOperator, sentence.first_sentence.first_sentence.logic_operator)

        self.assertEqual('P2', sentence.first_sentence.second_sentence.symbol)
        self.assertEqual(False, sentence.first_sentence.second_sentence.negation)
        self.assertEqual(LogicOperatorTypes.NoOperator, sentence.first_sentence.second_sentence.logic_operator)

        # Second sentence
        self.assertEqual('P3', sentence.second_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NoOperator, sentence.second_sentence.logic_operator)
        self.assertEqual(False, sentence.second_sentence.negation)

    def test_string_of_ors(self):
        parser = PropLogicParser("P1 OR P2 OR P3")
        sentence = parser.parse_line()
        # Top level
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.Or, sentence.logic_operator)
        self.assertEqual(False, sentence.negation)
        # First sentence
        self.assertEqual('P1', sentence.first_sentence.symbol)
        self.assertEqual(False, sentence.first_sentence.negation)
        self.assertEqual(LogicOperatorTypes.NoOperator, sentence.first_sentence.logic_operator)
        # Second sentence
        self.assertEqual(None, sentence.second_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.Or, sentence.second_sentence.logic_operator)
        self.assertEqual(False, sentence.second_sentence.negation)
        self.assertEqual('P2', sentence.second_sentence.first_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NoOperator, sentence.second_sentence.first_sentence.logic_operator)
        self.assertEqual(False, sentence.second_sentence.first_sentence.negation)
        self.assertEqual('P3', sentence.second_sentence.second_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NoOperator, sentence.second_sentence.second_sentence.logic_operator)
        self.assertEqual(False, sentence.second_sentence.second_sentence.negation)

        parser = PropLogicParser("P1 OR (P2 OR P3)")
        sentence = parser.parse_line()
        # Top level
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.Or, sentence.logic_operator)
        self.assertEqual(False, sentence.negation)
        # First sentence
        self.assertEqual('P1', sentence.first_sentence.symbol)
        self.assertEqual(False, sentence.first_sentence.negation)
        self.assertEqual(LogicOperatorTypes.NoOperator, sentence.first_sentence.logic_operator)
        # Second sentence
        self.assertEqual(None, sentence.second_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.Or, sentence.second_sentence.logic_operator)
        self.assertEqual(False, sentence.second_sentence.negation)
        self.assertEqual('P2', sentence.second_sentence.first_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NoOperator, sentence.second_sentence.first_sentence.logic_operator)
        self.assertEqual(False, sentence.second_sentence.first_sentence.negation)
        self.assertEqual('P3', sentence.second_sentence.second_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NoOperator, sentence.second_sentence.second_sentence.logic_operator)
        self.assertEqual(False, sentence.second_sentence.second_sentence.negation)

        parser = PropLogicParser("(P1 OR P2) OR P3")
        sentence = parser.parse_line()
        # Top level
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.Or, sentence.logic_operator)
        self.assertEqual(False, sentence.negation)
        # First sentence
        self.assertEqual(None, sentence.first_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.Or, sentence.first_sentence.logic_operator)
        self.assertEqual(False, sentence.negation)
        self.assertEqual('P1', sentence.first_sentence.first_sentence.symbol)
        self.assertEqual(False, sentence.first_sentence.first_sentence.negation)
        self.assertEqual(LogicOperatorTypes.NoOperator, sentence.first_sentence.first_sentence.logic_operator)
        self.assertEqual('P2', sentence.first_sentence.second_sentence.symbol)
        self.assertEqual(False, sentence.first_sentence.second_sentence.negation)
        self.assertEqual(LogicOperatorTypes.NoOperator, sentence.first_sentence.second_sentence.logic_operator)
        # Second sentence
        self.assertEqual('P3', sentence.second_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NoOperator, sentence.second_sentence.logic_operator)
        self.assertEqual(False, sentence.second_sentence.negation)

    def test_parse_line(self):
        parser = PropLogicParser("P1U87 AND P2 AND ~P3 OR A94P => P4 AND (P6 OR P8)")
        sentence = parser.parse_line()
        # Top level
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.Implies, sentence.logic_operator)
        self.assertEqual(False, sentence.negation)
        # First Sentence
        self.assertEqual(None, sentence.first_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.Or, sentence.first_sentence.logic_operator)
        self.assertEqual(False, sentence.first_sentence.negation)
        # First - First
        self.assertEqual(None, sentence.first_sentence.first_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.And, sentence.first_sentence.first_sentence.logic_operator)
        self.assertEqual(False, sentence.first_sentence.first_sentence.negation)
        # First - First - First
        self.assertEqual('P1U87', sentence.first_sentence.first_sentence.first_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NoOperator,
                         sentence.first_sentence.first_sentence.first_sentence.logic_operator)
        self.assertEqual(False, sentence.first_sentence.first_sentence.first_sentence.negation)
        # First - First - Second
        self.assertEqual(None, sentence.first_sentence.first_sentence.second_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.And, sentence.first_sentence.first_sentence.second_sentence.logic_operator)
        self.assertEqual(False, sentence.first_sentence.first_sentence.second_sentence.negation)
        # First - First - Second - First
        self.assertEqual('P2', sentence.first_sentence.first_sentence.second_sentence.first_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NoOperator,
                         sentence.first_sentence.first_sentence.second_sentence.first_sentence.logic_operator)
        self.assertEqual(False, sentence.first_sentence.first_sentence.second_sentence.negation)
        # First - First - Second - Second
        self.assertEqual('P3', sentence.first_sentence.first_sentence.second_sentence.second_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NoOperator,
                         sentence.first_sentence.first_sentence.second_sentence.second_sentence.logic_operator)
        self.assertEqual(True, sentence.first_sentence.first_sentence.second_sentence.second_sentence.negation)
        # First - Second
        self.assertEqual('A94P', sentence.first_sentence.second_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NoOperator, sentence.first_sentence.second_sentence.logic_operator)
        self.assertEqual(False, sentence.first_sentence.second_sentence.negation)
        # Second Sentence
        self.assertEqual(None, sentence.second_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.And, sentence.second_sentence.logic_operator)
        self.assertEqual(False, sentence.second_sentence.negation)
        # Second - First
        self.assertEqual('P4', sentence.second_sentence.first_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NoOperator, sentence.second_sentence.first_sentence.logic_operator)
        self.assertEqual(False, sentence.second_sentence.first_sentence.negation)
        # Second - Second
        self.assertEqual(None, sentence.second_sentence.second_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.Or, sentence.second_sentence.second_sentence.logic_operator)
        self.assertEqual(False, sentence.second_sentence.second_sentence.negation)
        self.assertEqual('P6', sentence.second_sentence.second_sentence.first_sentence.symbol)
        self.assertEqual('P8', sentence.second_sentence.second_sentence.second_sentence.symbol)

    def test_parse_input(self):
        parser = PropLogicParser("P1U87 AND P2 AND ~P3 OR A94P => P4 AND (P6 OR P8)\nP5 AND P7")
        sentences = parser.parse_input()
        sentence = sentences[0]
        # Top level
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.Implies, sentence.logic_operator)
        self.assertEqual(False, sentence.negation)
        # First Sentence
        self.assertEqual(None, sentence.first_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.Or, sentence.first_sentence.logic_operator)
        self.assertEqual(False, sentence.first_sentence.negation)
        # First - First
        self.assertEqual(None, sentence.first_sentence.first_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.And, sentence.first_sentence.first_sentence.logic_operator)
        self.assertEqual(False, sentence.first_sentence.first_sentence.negation)
        # First - First - First
        self.assertEqual('P1U87', sentence.first_sentence.first_sentence.first_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NoOperator,
                         sentence.first_sentence.first_sentence.first_sentence.logic_operator)
        self.assertEqual(False, sentence.first_sentence.first_sentence.first_sentence.negation)
        # First - First - Second
        self.assertEqual(None, sentence.first_sentence.first_sentence.second_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.And, sentence.first_sentence.first_sentence.second_sentence.logic_operator)
        self.assertEqual(False, sentence.first_sentence.first_sentence.second_sentence.negation)
        # First - First - Second - First
        self.assertEqual('P2', sentence.first_sentence.first_sentence.second_sentence.first_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NoOperator,
                         sentence.first_sentence.first_sentence.second_sentence.first_sentence.logic_operator)
        self.assertEqual(False, sentence.first_sentence.first_sentence.second_sentence.negation)
        # First - First - Second - Second
        self.assertEqual('P3', sentence.first_sentence.first_sentence.second_sentence.second_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NoOperator,
                         sentence.first_sentence.first_sentence.second_sentence.second_sentence.logic_operator)
        self.assertEqual(True, sentence.first_sentence.first_sentence.second_sentence.second_sentence.negation)
        # First - Second
        self.assertEqual('A94P', sentence.first_sentence.second_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NoOperator, sentence.first_sentence.second_sentence.logic_operator)
        self.assertEqual(False, sentence.first_sentence.second_sentence.negation)
        # Second Sentence
        self.assertEqual(None, sentence.second_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.And, sentence.second_sentence.logic_operator)
        self.assertEqual(False, sentence.second_sentence.negation)
        # Second - First
        self.assertEqual('P4', sentence.second_sentence.first_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NoOperator, sentence.second_sentence.first_sentence.logic_operator)
        self.assertEqual(False, sentence.second_sentence.first_sentence.negation)
        # Second - Second
        self.assertEqual(None, sentence.second_sentence.second_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.Or, sentence.second_sentence.second_sentence.logic_operator)
        self.assertEqual(False, sentence.second_sentence.second_sentence.negation)
        self.assertEqual('P6', sentence.second_sentence.second_sentence.first_sentence.symbol)
        self.assertEqual('P8', sentence.second_sentence.second_sentence.second_sentence.symbol)

        # Line 2
        sentence = sentences[1]
        self.assertEqual('P5', sentence.first_sentence.symbol)
        self.assertEqual(False, sentence.first_sentence.negation)
        self.assertEqual('P7', sentence.second_sentence.symbol)
        self.assertEqual(False, sentence.second_sentence.negation)
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.And, sentence.logic_operator)
        self.assertEqual(False, sentence.negation)

    def test_parse_set_input(self):
        # This tests the parser without passing in an input string right away
        parser = PropLogicParser()
        parser.set_input("P1U87 AND P2 AND ~P3 OR A94P => P4 AND (P6 OR P8)\nP5 AND P7")
        sentences = parser.parse_input()
        sentence = sentences[0]
        # Top level
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.Implies, sentence.logic_operator)
        self.assertEqual(False, sentence.negation)
        # First Sentence
        self.assertEqual(None, sentence.first_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.Or, sentence.first_sentence.logic_operator)
        self.assertEqual(False, sentence.first_sentence.negation)
        # First - First
        self.assertEqual(None, sentence.first_sentence.first_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.And, sentence.first_sentence.first_sentence.logic_operator)
        self.assertEqual(False, sentence.first_sentence.first_sentence.negation)
        # First - First - First
        self.assertEqual('P1U87', sentence.first_sentence.first_sentence.first_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NoOperator,
                         sentence.first_sentence.first_sentence.first_sentence.logic_operator)
        self.assertEqual(False, sentence.first_sentence.first_sentence.first_sentence.negation)
        # First - First - Second
        self.assertEqual(None, sentence.first_sentence.first_sentence.second_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.And, sentence.first_sentence.first_sentence.second_sentence.logic_operator)
        self.assertEqual(False, sentence.first_sentence.first_sentence.second_sentence.negation)
        # First - First - Second - First
        self.assertEqual('P2', sentence.first_sentence.first_sentence.second_sentence.first_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NoOperator,
                         sentence.first_sentence.first_sentence.second_sentence.first_sentence.logic_operator)
        self.assertEqual(False, sentence.first_sentence.first_sentence.second_sentence.negation)
        # First - First - Second - Second
        self.assertEqual('P3', sentence.first_sentence.first_sentence.second_sentence.second_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NoOperator,
                         sentence.first_sentence.first_sentence.second_sentence.second_sentence.logic_operator)
        self.assertEqual(True, sentence.first_sentence.first_sentence.second_sentence.second_sentence.negation)
        # First - Second
        self.assertEqual('A94P', sentence.first_sentence.second_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NoOperator, sentence.first_sentence.second_sentence.logic_operator)
        self.assertEqual(False, sentence.first_sentence.second_sentence.negation)
        # Second Sentence
        self.assertEqual(None, sentence.second_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.And, sentence.second_sentence.logic_operator)
        self.assertEqual(False, sentence.second_sentence.negation)
        # Second - First
        self.assertEqual('P4', sentence.second_sentence.first_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.NoOperator, sentence.second_sentence.first_sentence.logic_operator)
        self.assertEqual(False, sentence.second_sentence.first_sentence.negation)
        # Second - Second
        self.assertEqual(None, sentence.second_sentence.second_sentence.symbol)
        self.assertEqual(LogicOperatorTypes.Or, sentence.second_sentence.second_sentence.logic_operator)
        self.assertEqual(False, sentence.second_sentence.second_sentence.negation)
        self.assertEqual('P6', sentence.second_sentence.second_sentence.first_sentence.symbol)
        self.assertEqual('P8', sentence.second_sentence.second_sentence.second_sentence.symbol)

        # Line 2
        sentence = sentences[1]
        self.assertEqual('P5', sentence.first_sentence.symbol)
        self.assertEqual(False, sentence.first_sentence.negation)
        self.assertEqual('P7', sentence.second_sentence.symbol)
        self.assertEqual(False, sentence.second_sentence.negation)
        self.assertEqual(None, sentence.symbol)
        self.assertEqual(LogicOperatorTypes.And, sentence.logic_operator)
        self.assertEqual(False, sentence.negation)


class TestSentence(TestCase):
    def test_create_sentence(self):
        # Test creation of an atomic sentence
        atomic_sentence1 = Sentence('P1')
        self.assertEqual('P1', atomic_sentence1.symbol)
        self.assertEqual(None, atomic_sentence1.first_sentence)
        self.assertEqual(None, atomic_sentence1.second_sentence)
        self.assertEqual(LogicOperatorTypes.NoOperator, atomic_sentence1.logic_operator)
        self.assertEqual(False, atomic_sentence1.negation)

        # Test creation of a negated atomic sentence
        atomic_sentence2 = Sentence('P2', negated=True)
        self.assertEqual('P2', atomic_sentence2.symbol)
        self.assertEqual(None, atomic_sentence2.first_sentence)
        self.assertEqual(None, atomic_sentence2.second_sentence)
        self.assertEqual(LogicOperatorTypes.NoOperator, atomic_sentence2.logic_operator)
        self.assertEqual(True, atomic_sentence2.negation)

        # Test creation of negation of a sentence
        negated_sentence = Sentence(atomic_sentence2, negated=True)
        self.assertEqual(None, negated_sentence.symbol)
        self.assertEqual(atomic_sentence2, negated_sentence.first_sentence)
        self.assertEqual(None, negated_sentence.second_sentence)
        self.assertEqual(LogicOperatorTypes.NoOperator, negated_sentence.logic_operator)
        self.assertEqual(True, negated_sentence.negation)
        # Check the sentence inside the sentence
        self.assertEqual('P2', negated_sentence.first_sentence.symbol)
        self.assertEqual(None, negated_sentence.first_sentence.first_sentence)
        self.assertEqual(None, negated_sentence.first_sentence.second_sentence)
        self.assertEqual(LogicOperatorTypes.NoOperator, negated_sentence.first_sentence.logic_operator)
        self.assertEqual(True, negated_sentence.first_sentence.negation)

        # Test creation of a complex sentence using two string tokens
        complex_sentence1 = Sentence('Q1', LogicOperatorTypes.And, 'Q2')
        self.assertEqual(None, complex_sentence1.symbol)
        self.assertNotEqual(None, complex_sentence1.first_sentence)
        self.assertNotEqual(None, complex_sentence1.second_sentence)
        self.assertEqual(LogicOperatorTypes.And, complex_sentence1.logic_operator)
        self.assertEqual(False, complex_sentence1.negation)
        # Check the sentences inside
        self.assertEqual('Q1', complex_sentence1.first_sentence.symbol)
        self.assertEqual(None, complex_sentence1.first_sentence.first_sentence)
        self.assertEqual(None, complex_sentence1.first_sentence.second_sentence)
        self.assertEqual(LogicOperatorTypes.NoOperator, complex_sentence1.first_sentence.logic_operator)
        self.assertEqual(False, complex_sentence1.first_sentence.negation)
        self.assertEqual('Q2', complex_sentence1.second_sentence.symbol)
        self.assertEqual(None, complex_sentence1.second_sentence.first_sentence)
        self.assertEqual(None, complex_sentence1.second_sentence.second_sentence)
        self.assertEqual(LogicOperatorTypes.NoOperator, complex_sentence1.second_sentence.logic_operator)
        self.assertEqual(False, complex_sentence1.second_sentence.negation)

        # Test creation of a complex sentence using two sentences
        complex_sentence2 = Sentence(atomic_sentence1, LogicOperatorTypes.Or, atomic_sentence2)
        self.assertEqual(None, complex_sentence2.symbol)
        self.assertEqual(atomic_sentence1, complex_sentence2.first_sentence)
        self.assertEqual(atomic_sentence2, complex_sentence2.second_sentence)
        self.assertEqual(LogicOperatorTypes.Or, complex_sentence2.logic_operator)
        self.assertEqual(False, complex_sentence2.negation)
        # Check the sentences inside
        self.assertEqual('P1', complex_sentence2.first_sentence.symbol)
        self.assertEqual(None, complex_sentence2.first_sentence.first_sentence)
        self.assertEqual(None, complex_sentence2.first_sentence.second_sentence)
        self.assertEqual(LogicOperatorTypes.NoOperator, complex_sentence2.first_sentence.logic_operator)
        self.assertEqual(False, complex_sentence2.first_sentence.negation)
        self.assertEqual('P2', complex_sentence2.second_sentence.symbol)
        self.assertEqual(None, complex_sentence2.second_sentence.first_sentence)
        self.assertEqual(None, complex_sentence2.second_sentence.second_sentence)
        self.assertEqual(LogicOperatorTypes.NoOperator, complex_sentence2.second_sentence.logic_operator)
        self.assertEqual(True, complex_sentence2.second_sentence.negation)

    def test_bad_create_sentence(self):
        failed: bool = False

        try:
            Sentence('P1')
        except SentenceError:
            failed = True
        self.assertEqual(False, failed)

        failed = False
        try:
            Sentence(None)
        except SentenceError:
            failed = True
        self.assertEqual(True, failed)

        failed = False
        try:
            Sentence(failed)
        except SentenceError:
            failed = True
        self.assertEqual(True, failed)

        failed = False
        try:
            Sentence('P1', LogicOperatorTypes.NoOperator, 'P2')
        except SentenceError:
            failed = True
        self.assertEqual(True, failed)

        failed = False
        try:
            Sentence('P1', None, 'P2')
        except SentenceError:
            failed = True
        self.assertEqual(True, failed)

        failed = False
        try:
            Sentence(Sentence('P1'), LogicOperatorTypes.NoOperator, Sentence('P2'))
        except SentenceError:
            failed = True
        self.assertEqual(True, failed)

        failed = False
        try:
            Sentence(Sentence('P1'), None, Sentence('P2'))
        except SentenceError:
            failed = True
        self.assertEqual(True, failed)

        failed = False
        try:
            Sentence('P1', None, 'P2')
        except SentenceError:
            failed = True
        self.assertEqual(True, failed)

        failed = False
        try:
            Sentence('P1', LogicOperatorTypes.And)
        except SentenceError:
            failed = True
        self.assertEqual(True, failed)

        failed = False
        try:
            Sentence('P1', LogicOperatorTypes.And, None)
        except SentenceError:
            failed = True
        self.assertEqual(True, failed)

        failed = False
        try:
            Sentence('P1', LogicOperatorTypes.And, False) # noqa
        except SentenceError:
            failed = True
        self.assertEqual(True, failed)

        failed = False
        try:
            Sentence(Sentence("P1"), LogicOperatorTypes.And, None)
        except SentenceError:
            failed = True
        self.assertEqual(True, failed)

        failed = False
        try:
            Sentence(Sentence("P1"), LogicOperatorTypes.And)
        except SentenceError:
            failed = True
        self.assertEqual(True, failed)

        failed = False
        try:
            Sentence(Sentence("P1"), LogicOperatorTypes.And, False) # noqa
        except SentenceError:
            failed = True
        self.assertEqual(True, failed)

    def test_is_atomic(self):
        parser = PropLogicParser("P1")
        sentence = parser.parse_line()
        self.assertEqual(True, sentence.is_atomic)

        parser = PropLogicParser("~P1")
        sentence = parser.parse_line()
        self.assertEqual(True, sentence.is_atomic)

        parser = PropLogicParser("P1 OR P2")
        sentence = parser.parse_line()
        self.assertEqual(False, sentence.is_atomic)

        parser = PropLogicParser("P1 AND P2")
        sentence = parser.parse_line()
        self.assertEqual(False, sentence.is_atomic)

        parser = PropLogicParser("P1 => P2")
        sentence = parser.parse_line()
        self.assertEqual(False, sentence.is_atomic)

        parser = PropLogicParser("P1 <=> P2")
        sentence = parser.parse_line()
        self.assertEqual(False, sentence.is_atomic)

        parser = PropLogicParser("~P1 AND ~P2")
        sentence = parser.parse_line()
        self.assertEqual(False, sentence.is_atomic)

        parser = PropLogicParser("~P1 OR ~P2")
        sentence = parser.parse_line()
        self.assertEqual(False, sentence.is_atomic)

        parser = PropLogicParser("~P1 AND P2")
        sentence = parser.parse_line()
        self.assertEqual(False, sentence.is_atomic)

    def test_sentence_to_string(self):
        parser = PropLogicParser("P1 AND P2 OR P3")
        sentence = parser.parse_line()
        self.assertEqual("P1 AND P2 OR P3", sentence.to_string())

        parser = PropLogicParser("P1 OR P2 AND P3")
        sentence = parser.parse_line()
        self.assertEqual("P1 OR P2 AND P3", sentence.to_string())

        parser = PropLogicParser("(P1 OR P2) AND P3")
        sentence = parser.parse_line()
        self.assertEqual("(P1 OR P2) AND P3", sentence.to_string())

        parser = PropLogicParser("P1 AND (P2 OR P3)")
        sentence = parser.parse_line()
        self.assertEqual("P1 AND (P2 OR P3)", sentence.to_string())

        parser = PropLogicParser("(P1 AND P2) OR P3")
        sentence = parser.parse_line()
        self.assertEqual("P1 AND P2 OR P3", sentence.to_string())

        parser = PropLogicParser("~(P1 AND P2) OR P3")
        sentence = parser.parse_line()
        self.assertEqual("~(P1 AND P2) OR P3", sentence.to_string())

        parser = PropLogicParser("P1 AND P2 OR (P3)")
        sentence = parser.parse_line()
        self.assertEqual("P1 AND P2 OR P3", sentence.to_string())

        parser = PropLogicParser("P1 AND P2 OR ~(P3)")
        sentence = parser.parse_line()
        self.assertEqual("P1 AND P2 OR ~P3", sentence.to_string())

        parser = PropLogicParser("(P1 => P2) AND P3")
        sentence = parser.parse_line()
        self.assertEqual("(P1 => P2) AND P3", sentence.to_string())

        parser = PropLogicParser("P1 => P2 AND P3")
        sentence = parser.parse_line()
        self.assertEqual("P1 => P2 AND P3", sentence.to_string())

        parser = PropLogicParser("P1 => P2 OR P3")
        sentence = parser.parse_line()
        self.assertEqual("P1 => P2 OR P3", sentence.to_string())

        parser = PropLogicParser("P1 AND U1 OR U2 => P2 OR P3 AND P4")
        sentence = parser.parse_line()
        self.assertEqual("P1 AND U1 OR U2 => P2 OR P3 AND P4", sentence.to_string())

        parser = PropLogicParser("P1 AND U1 OR U2 <=> P2 OR P3 AND P4")
        sentence = parser.parse_line()
        self.assertEqual("P1 AND U1 OR U2 <=> P2 OR P3 AND P4", sentence.to_string())

        parser = PropLogicParser("P1 AND (U1 OR U2) => (P2 OR P3) AND P4")
        sentence = parser.parse_line()
        self.assertEqual("P1 AND (U1 OR U2) => (P2 OR P3) AND P4", sentence.to_string())

        parser = PropLogicParser("P1 AND ~(U1 OR U2) => P2 OR ~(P3 AND P4)")
        sentence = parser.parse_line()
        self.assertEqual("P1 AND ~(U1 OR U2) => P2 OR ~(P3 AND P4)", sentence.to_string())

        parser = PropLogicParser("P1 AND (U1 OR U2 => P2) OR P3 AND P4")
        sentence = parser.parse_line()
        self.assertEqual("P1 AND (U1 OR U2 => P2) OR P3 AND P4", sentence.to_string())

        parser = PropLogicParser("P1 AND ((U1 OR U2 => P2) OR P3) AND P4")
        sentence = parser.parse_line()
        self.assertEqual("P1 AND ((U1 OR U2 => P2) OR P3) AND P4", sentence.to_string())

        parser = PropLogicParser("((P1 AND ((U1 OR U2 => P2) OR P3)) AND P4)")
        sentence = parser.parse_line()
        self.assertEqual("P1 AND ((U1 OR U2 => P2) OR P3) AND P4", sentence.to_string())
