from unittest import TestCase
from prop_logic_parser import PropLogicParser, Sentence, SentenceType, LogicOperatorTypes


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
        self.assertEqual('EOF', parser.consume_token())
        self.assertEqual('EOF', parser.consume_token())

    def test_parse_line(self):
        parser = PropLogicParser("P1U87 AND P2 AND ~P3 OR A94P => P4 AND (P6 OR P8)")
        sentence = parser.parse_line()
        pass


class TestSentence(TestCase):
    def test_create_sentence(self):
        # Test creation of an atomic sentence
        atomic_sentence1 = Sentence('P1')
        self.assertEqual('P1', atomic_sentence1.symbol)
        self.assertEqual(None, atomic_sentence1.first_sentence)
        self.assertEqual(None, atomic_sentence1.second_sentence)
        self.assertEqual(SentenceType.AtomicSentence, atomic_sentence1.sentence_type)
        self.assertEqual(LogicOperatorTypes.NoOperator, atomic_sentence1.logic_operator)
        self.assertEqual(False, atomic_sentence1.negation)

        # Test creation of a negated atomic sentence
        atomic_sentence2 = Sentence('P2', negated=True)
        self.assertEqual('P2', atomic_sentence2.symbol)
        self.assertEqual(None, atomic_sentence2.first_sentence)
        self.assertEqual(None, atomic_sentence2.second_sentence)
        self.assertEqual(SentenceType.AtomicSentence, atomic_sentence2.sentence_type)
        self.assertEqual(LogicOperatorTypes.NoOperator, atomic_sentence2.logic_operator)
        self.assertEqual(True, atomic_sentence2.negation)

        # Test creation of negation of a sentence
        negated_sentence = Sentence()
        negated_sentence.negate_sentence(atomic_sentence2)
        self.assertEqual(None, negated_sentence.symbol)
        self.assertEqual(atomic_sentence2, negated_sentence.first_sentence)
        self.assertEqual(None, negated_sentence.second_sentence)
        self.assertEqual(SentenceType.ComplexSentence, negated_sentence.sentence_type)
        self.assertEqual(LogicOperatorTypes.NoOperator, negated_sentence.logic_operator)
        self.assertEqual(True, negated_sentence.negation)
        # Check the sentence inside the sentence
        self.assertEqual('P2', negated_sentence.first_sentence.symbol)
        self.assertEqual(None, negated_sentence.first_sentence.first_sentence)
        self.assertEqual(None, negated_sentence.first_sentence.second_sentence)
        self.assertEqual(SentenceType.AtomicSentence, negated_sentence.first_sentence.sentence_type)
        self.assertEqual(LogicOperatorTypes.NoOperator, negated_sentence.first_sentence.logic_operator)
        self.assertEqual(True, negated_sentence.first_sentence.negation)

        # Test creation of a complex sentence using two string tokens
        complex_sentence1 = Sentence()
        complex_sentence1.sentence_from_tokens('Q1', LogicOperatorTypes.And, 'Q2')
        self.assertEqual(None, complex_sentence1.symbol)
        self.assertNotEqual(None, complex_sentence1.first_sentence)
        self.assertNotEqual(None, complex_sentence1.second_sentence)
        self.assertEqual(SentenceType.ComplexSentence, complex_sentence1.sentence_type)
        self.assertEqual(LogicOperatorTypes.And, complex_sentence1.logic_operator)
        self.assertEqual(False, complex_sentence1.negation)
        # Check the sentences inside
        self.assertEqual('Q1', complex_sentence1.first_sentence.symbol)
        self.assertEqual(None, complex_sentence1.first_sentence.first_sentence)
        self.assertEqual(None, complex_sentence1.first_sentence.second_sentence)
        self.assertEqual(SentenceType.AtomicSentence, complex_sentence1.first_sentence.sentence_type)
        self.assertEqual(LogicOperatorTypes.NoOperator, complex_sentence1.first_sentence.logic_operator)
        self.assertEqual(False, complex_sentence1.first_sentence.negation)
        self.assertEqual('Q2', complex_sentence1.second_sentence.symbol)
        self.assertEqual(None, complex_sentence1.second_sentence.first_sentence)
        self.assertEqual(None, complex_sentence1.second_sentence.second_sentence)
        self.assertEqual(SentenceType.AtomicSentence, complex_sentence1.second_sentence.sentence_type)
        self.assertEqual(LogicOperatorTypes.NoOperator, complex_sentence1.second_sentence.logic_operator)
        self.assertEqual(False, complex_sentence1.second_sentence.negation)

        # Test creation of a complex sentence using two sentences
        complex_sentence2 = Sentence()
        complex_sentence2.sentence_from_sentences(atomic_sentence1, LogicOperatorTypes.Or, atomic_sentence2)
        self.assertEqual(None, complex_sentence2.symbol)
        self.assertEqual(atomic_sentence1, complex_sentence2.first_sentence)
        self.assertEqual(atomic_sentence2, complex_sentence2.second_sentence)
        self.assertEqual(SentenceType.ComplexSentence, complex_sentence2.sentence_type)
        self.assertEqual(LogicOperatorTypes.Or, complex_sentence2.logic_operator)
        self.assertEqual(False, complex_sentence2.negation)
        # Check the sentences inside
        self.assertEqual('P1', complex_sentence2.first_sentence.symbol)
        self.assertEqual(None, complex_sentence2.first_sentence.first_sentence)
        self.assertEqual(None, complex_sentence2.first_sentence.second_sentence)
        self.assertEqual(SentenceType.AtomicSentence, complex_sentence2.first_sentence.sentence_type)
        self.assertEqual(LogicOperatorTypes.NoOperator, complex_sentence2.first_sentence.logic_operator)
        self.assertEqual(False, complex_sentence2.first_sentence.negation)
        self.assertEqual('P2', complex_sentence2.second_sentence.symbol)
        self.assertEqual(None, complex_sentence2.second_sentence.first_sentence)
        self.assertEqual(None, complex_sentence2.second_sentence.second_sentence)
        self.assertEqual(SentenceType.AtomicSentence, complex_sentence2.second_sentence.sentence_type)
        self.assertEqual(LogicOperatorTypes.NoOperator, complex_sentence2.second_sentence.logic_operator)
        self.assertEqual(True, complex_sentence2.second_sentence.negation)
