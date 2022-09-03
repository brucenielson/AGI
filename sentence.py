from __future__ import annotations
from typing import Optional, List, Union
from functools import total_ordering
import pl_knowledge_base as kb
from copy import deepcopy
from enum import Enum
import pl_parser


@total_ordering
class LogicOperatorTypes(Enum):
    NoOperator = 1
    And = 2
    Or = 3
    # noinspection SpellCheckingInspection
    Biconditional = 4
    Implies = 5

    def __lt__(self, other):
        # Only work if both classes are the same
        if self.__class__ is other.__class__:
            return self.value < other.value
        # Both classes are not the same, so throw an error
        return NotImplemented


def apply_operator(value1: kb.LogicValue, value2: kb.LogicValue, operator: LogicOperatorTypes) -> kb.LogicValue:
    final_value: kb.LogicValue
    if operator == LogicOperatorTypes.NoOperator:
        return value1
    elif operator == LogicOperatorTypes.And:
        if value1 == kb.LogicValue.TRUE and value2 == kb.LogicValue.TRUE:
            return kb.LogicValue.TRUE
        elif value1 == kb.LogicValue.FALSE or value2 == kb.LogicValue.FALSE:
            return kb.LogicValue.FALSE
    elif operator == LogicOperatorTypes.Or:
        if value1 == kb.LogicValue.TRUE or value2 == kb.LogicValue.TRUE:
            return kb.LogicValue.TRUE
        elif value1 == kb.LogicValue.FALSE and value2 == kb.LogicValue.FALSE:
            return kb.LogicValue.FALSE
    elif operator == LogicOperatorTypes.Implies:
        # a => b means ~a or b
        if value1 == kb.LogicValue.FALSE or value2 == kb.LogicValue.TRUE:
            return kb.LogicValue.TRUE
        # ~(~a or b) = a and ~b
        elif value1 == kb.LogicValue.TRUE and value2 == kb.LogicValue.FALSE:
            return kb.LogicValue.FALSE
    elif operator == LogicOperatorTypes.Biconditional:
        # Bi-conditional is just implies going both ways connected by an And operator
        value3: kb.LogicValue = apply_operator(value1, value2, LogicOperatorTypes.Implies)
        value4: kb.LogicValue = apply_operator(value2, value1, LogicOperatorTypes.Implies)
        return apply_operator(value3, value4, LogicOperatorTypes.And)
    # No evaluation, so must be UNDEFINED
    return kb.LogicValue.UNDEFINED


class SentenceError(Exception):
    def __init__(self, message=None):
        self.message = message
        super().__init__(self.message)


# Use this function to do a quick and dirty parse of a single sentence
def parse_sentence(input_str: str) -> Sentence:
    parser: pl_parser.PropLogicParser = pl_parser.PropLogicParser(input_str)
    result: Sentence = parser.parse_line()
    if parser.line_count > 0:
        raise SentenceError("Call to 'parse_sentence' takes only a single line of input.")
    return result


class Sentence:
    def __init__(self, sentence1: Union[Sentence, str] = None, logical_operator: LogicOperatorTypes = None,
                 sentence2: Union[Sentence, str] = None, negated: bool = False):
        # Set default values
        self._symbol: Optional[str] = None
        self._first_sentence: Optional[Sentence] = None
        self._second_sentence: Optional[Sentence] = None
        self._parent_sentence: Optional[Sentence] = None
        self._logic_operator: LogicOperatorTypes = LogicOperatorTypes.NoOperator
        self._is_cnf: bool = False
        # Set negation
        self._negation: bool = negated
        # A blank symbol should be treated as a None
        if sentence1 == "":
            sentence1 = None
        if sentence2 == "":
            sentence2 = None
        # Handle logical operator
        if logical_operator is not None and sentence2 is None:
            # We have a logical operator but no sentence2, which is illegal
            raise SentenceError("You must have a second sentence if you have a logical operator.")
        if sentence2 is not None and (logical_operator is None or logical_operator == LogicOperatorTypes.NoOperator):
            # We have a sentence2 but no logical operator, which is illegal
            raise SentenceError("You must have a logical operator if you have a second sentence in the constructor.")
        elif logical_operator is not None:
            # Store the logic operator passed
            self._logic_operator = logical_operator

        # Handle sentence2
        if sentence2 is not None:
            if isinstance(sentence2, str):
                sentence2 = sentence2.upper()
                # Do we have a second sentence that is a string? If so, create it as a Sentence type
                self._second_sentence = Sentence(sentence2)
            elif isinstance(sentence2, Sentence):
                # Do we have a second sentence that is of Sentence type? If so, plug it right into place
                self._second_sentence = sentence2
            else:
                # Something illegal was passed, so throw an error
                raise SentenceError("The second sentence (sentence2) must be a string symbol, a Sentence, or None.")

        # Handle first sentence (or symbol)
        if sentence1 is None:
            # Creating an empty Sentence, probably for a lone not
            self._symbol = None
        elif isinstance(sentence1, Sentence):
            # This is a Sentence. Cases:
            # One sentence only...
            if self._second_sentence is None and self._logic_operator == LogicOperatorTypes.NoOperator:
                # No other parameters, so do a shallow copy instead
                self.copy(sentence1, negated=negated)
            else:
                # Make this first sentence because it is part of other parameters
                self._first_sentence = sentence1
        elif isinstance(sentence1, str):
            sentence1 = sentence1.upper()
            # This is a string, so it could be a symbol or a string that is to be parsed to a Sentence
            # Is this just a lone parameter 1 passed as a string?
            if logical_operator is not None or sentence2 is not None:
                # There is more than a single parameter being passed, so process this as first sentence
                self._first_sentence = Sentence(sentence1)
            else:
                # Only parameter 1 was passed, so check if it is a symbol or sentence needing parsing?
                if sentence1.isalnum() and sentence1[0].isalpha():
                    # This is a single symbol
                    self._symbol = sentence1
                elif sentence1.isalnum() and sentence1[0].isalpha():
                    # Invalid value for a symbol since it doesn't start with a letter
                    SentenceError("Symbols must start with a letter.")
                else:
                    # Only first parameter was passed and it wasn't alpha numeric, so is it a full sentence?
                    result: Sentence = parse_sentence(sentence1)  # Attempting to parse
                    # This was a full sentence, so do a shallow copy
                    self.copy(result, negated=negated)
        else:
            # Illegal input
            raise SentenceError("Sentence constructor first parameter (symbol1_or_sentence1) not passed a legal type.")

    def __repr__(self) -> str:
        return self.to_string()

    def __eq__(self, other: Sentence) -> bool:
        if type(self) != type(other):
            return False
        else:
            if self.is_equivalent(other):
                return True
            else:
                return False

    @ property
    def is_cnf(self) -> bool:
        return self._is_cnf

    @property
    def logic_operator(self) -> LogicOperatorTypes:
        return self._logic_operator

    @logic_operator.setter
    def logic_operator(self, value: LogicOperatorTypes) -> None:
        self._logic_operator = value

    @property
    def negation(self) -> bool:
        return self._negation

    @negation.setter
    def negation(self, value: bool) -> None:
        self._negation = value

    @property
    def symbol(self) -> str:
        return self._symbol

    @symbol.setter
    def symbol(self, value: str) -> None:
        self._symbol = value

    @property
    def first_sentence(self) -> Sentence:
        return self._first_sentence

    @first_sentence.setter
    def first_sentence(self, value: Sentence) -> None:
        self._first_sentence = value
        self._first_sentence._parent_sentence = self

    @property
    def second_sentence(self) -> Sentence:
        return self._second_sentence

    @second_sentence.setter
    def second_sentence(self, value: Sentence) -> None:
        self._second_sentence = value
        self._second_sentence._parent_sentence = self

    @property
    def is_atomic(self):
        # Returns True if this is a simple atomic sentence and False if it is a complex sentence
        if self.logic_operator == LogicOperatorTypes.NoOperator \
                and self.first_sentence is None and self.second_sentence is None:
            # Simple atomic sentence with one symbol or no parameters at all
            return True
        elif self.first_sentence is not None and self.second_sentence is None and self.negation:
            # Lone negation with a sentence under it
            return False
        elif self.logic_operator != LogicOperatorTypes.NoOperator and self.first_sentence is not None:
            # Atomic sentence
            return False
        else:
            raise SentenceError("This sentence is in an illegal state because it is neither atomic or complex.")

    def copy(self, sentence: Sentence, negated: bool = False):
        if sentence._negation and negated:
            # If we are negating this copy, and it is already negated, then make it a first sentence instead
            new_sentence: Sentence = Sentence(sentence)
            self._first_sentence = new_sentence
            self._negation = True
        else:
            # Otherwise make a shallow copy
            self._symbol = sentence._symbol
            # Flip the negation sign if negated = True
            if negated:
                self._negation = not sentence._negation
            else:
                self._negation = sentence._negation
            self._first_sentence = sentence._first_sentence
            self._second_sentence = sentence._second_sentence
            self._logic_operator = sentence._logic_operator

    def sentence_from_tokens(self, token1: str, operator: LogicOperatorTypes, token2: str) -> None:
        if not (operator == LogicOperatorTypes.NoOperator or token1 == "" or token2 == ""
                or token1 is None or token2 is None):
            self.sentence_from_sentences(Sentence(token1), operator, Sentence(token2))
        else:
            raise SentenceError("Illegal parameters. Operator cannot be 'None' and Tokens cannot be blank.")

    def sentence_from_sentences(self, sentence1: Sentence, operator: LogicOperatorTypes, sentence2: Sentence) -> None:
        if not (operator == LogicOperatorTypes.NoOperator or sentence1 is None or sentence2 is None):
            self._logic_operator = operator
            self._negation = False
            self._symbol = None
            self._first_sentence = sentence1
            self._second_sentence = sentence2
        else:
            raise SentenceError("Illegal parameters. Operator cannot be 'None' and Tokens cannot be blank.")

    def negate_sentence(self) -> None:
        sentence = self.clone()
        self._negation = True
        self._logic_operator = LogicOperatorTypes.NoOperator
        self._symbol = None
        self._first_sentence = sentence
        self._second_sentence = None

    @classmethod
    def logic_operator_to_string(cls, logic_operator: LogicOperatorTypes):
        if logic_operator == LogicOperatorTypes.And:
            return "AND"
        elif logic_operator == LogicOperatorTypes.Or:
            return "OR"
        elif logic_operator == LogicOperatorTypes.Implies:
            return "=>"
        elif logic_operator == LogicOperatorTypes.Biconditional:
            return "<=>"
        else:
            raise SentenceError("Error converting Sentence to a string. Illegal Operator type.")

    @classmethod
    def string_to_sentence(cls, input_str: str) -> Sentence:
        return parse_sentence(input_str)

    def to_string(self, full_parentheses: bool = False) -> str:
        def to_string_sub_sentence(sub_sentence: Sentence):
            if self.logic_operator != sub_sentence.logic_operator \
                    and self.logic_operator < sub_sentence.logic_operator \
                    and not sub_sentence.is_atomic \
                    and not sub_sentence.negation:
                # Include parentheses if:
                # 1. The operators at this level is a lower priority than the one below
                # 2. The next level down is a complex sentence
                # 3. The next level down has no negation
                return "(" + sub_sentence.to_string() + ")"
            elif (self.logic_operator == LogicOperatorTypes.Implies or
                  self.logic_operator == LogicOperatorTypes.Biconditional) \
                    and (sub_sentence.logic_operator == LogicOperatorTypes.Implies or
                         sub_sentence.logic_operator == LogicOperatorTypes.Biconditional):
                # Use parentheses with implies or bi-conditionals next to each other to be more clear
                return "(" + sub_sentence.to_string() + ")"
            else:
                # Otherwise, skip the parentheses
                return sub_sentence.to_string()

        ret_val: str = ""
        if full_parentheses:
            if self._negation:
                ret_val += "~"

            if self.is_atomic:
                if self.symbol is not None:
                    ret_val += self.symbol
                else:
                    ret_val += ""
            elif self.logic_operator == LogicOperatorTypes.NoOperator and self.negation \
                    and self.first_sentence is not None:
                # We have a lone negation of another sentence
                ret_val += "(" + self.first_sentence.to_string(True) + ")"
            else:
                # Full complex sentence
                ret_val += "(" + self.first_sentence.to_string(True) + " " + \
                           Sentence.logic_operator_to_string(self.logic_operator) + " " + \
                           self.second_sentence.to_string(True) + ")"

            return ret_val
        else:
            if self.is_atomic:
                # Handle atomic sentence
                if self.symbol is not None:
                    ret_val += self.to_string(True)
                else:
                    ret_val += ""
            elif self.logic_operator == LogicOperatorTypes.NoOperator and self.negation \
                    and self.first_sentence is not None and self.second_sentence is None:
                # Handle lone negation
                if self._negation:
                    ret_val += "~"
                ret_val += to_string_sub_sentence(self.first_sentence)
            else:  # sentence is full complex
                # First Sentence
                ret_val += to_string_sub_sentence(self.first_sentence)
                # Logical operator
                ret_val += " " + Sentence.logic_operator_to_string(self.logic_operator) + " "
                # Second Sentence
                ret_val += to_string_sub_sentence(self.second_sentence)
                if self._negation:
                    ret_val = "~(" + ret_val + ")"

            return ret_val

    def get_symbol_list(self, temp_symbol_list: kb.SymbolList = None, sub_sentence: Sentence = None) -> kb.SymbolList:
        #  For each symbol, check if it's already in the list and, if not, add it
        #  then return the full list. It will default to value undefined for everything.
        #  then handle the rest, i.e. atomic vs. complex
        # This returns a list of symbols all set to undefined rather than to values they currently hold
        if temp_symbol_list is None:
            temp_symbol_list = kb.SymbolList()
        if sub_sentence is None:
            sub_sentence = self

        if sub_sentence.is_atomic:
            temp_symbol_list.add(sub_sentence.symbol)
        else:
            # All complex sentences have at least one sentence
            Sentence.get_symbol_list(sub_sentence.first_sentence, temp_symbol_list)
            # If we have a second sentence, then process that
            if sub_sentence.second_sentence is not None:
                Sentence.get_symbol_list(sub_sentence.second_sentence, temp_symbol_list)
        return temp_symbol_list

    def evaluate(self, model: kb.SymbolList) -> kb.LogicValue:
        return self._traverse_and_evaluate(model)

    def is_true(self, model: kb.SymbolList) -> bool:
        return self._traverse_and_evaluate(model) == kb.LogicValue.TRUE

    def is_false(self, model: kb.SymbolList) -> bool:
        return self._traverse_and_evaluate(model) == kb.LogicValue.FALSE

    def _traverse_and_evaluate(self, model: kb.SymbolList) -> kb.LogicValue:
        evaluate: kb.LogicValue
        if self.is_atomic:
            evaluate = model.get_value(self.symbol)
        else:
            sub_evaluate1: kb.LogicValue
            sub_evaluate2: kb.LogicValue
            # There should always be a first sentence
            sub_evaluate1 = self.first_sentence._traverse_and_evaluate(model)
            # If there is a second sentence evaluate it next
            if self.second_sentence is not None:
                sub_evaluate2 = self.second_sentence._traverse_and_evaluate(model)
                evaluate = apply_operator(sub_evaluate1, sub_evaluate2, self.logic_operator)
            else:
                evaluate = sub_evaluate1
        # Handle negations
        if self.negation:
            if evaluate == kb.LogicValue.TRUE:
                return kb.LogicValue.FALSE
            elif evaluate == kb.LogicValue.FALSE:
                return kb.LogicValue.TRUE
            else:
                return kb.LogicValue.UNDEFINED
        else:
            return evaluate

    def _truth_table_check_all(self, sentence: Sentence, symbols: kb.SymbolList, model: kb.SymbolList) -> bool:
        if symbols is None or symbols.length == 0:
            # We've processed every single symbol so this is one possible combination to evaluate
            if self.evaluate(model) == sentence.evaluate(model):
                return True
            else:
                return False
        else:
            # We still have symbols to pop off the queue and try both true and false for
            next_symbol: kb.LogicSymbol = symbols.get_next_symbol()
            copy_model1: kb.SymbolList = model.clone()
            copy_model2: kb.SymbolList = model.clone()
            copy_model1.set_value(next_symbol.name, True)
            copy_model2.set_value(next_symbol.name, False)
            # Recurse to create every possibility
            check1: bool = self._truth_table_check_all(sentence, symbols.clone(), copy_model1)
            check2: bool = self._truth_table_check_all(sentence, symbols.clone(), copy_model2)
            return check1 and check2

    def is_equivalent(self, other_sentence: Union[Sentence, str]) -> bool:
        sentence: Sentence = kb.sentence_or_str(other_sentence)
        if isinstance(sentence, str):
            sentence = Sentence(sentence)

        symbols1: kb.SymbolList = self.get_symbol_list()
        symbols2: kb.SymbolList = sentence.get_symbol_list()
        if symbols1.length != symbols2.length:
            # The sentences can't be equivalent if they don't have the same number of symbols
            return False
        else:
            for i in range(0, symbols1.length):
                # Abort if there is ever a mismatch between symbol names because they can't be equivalent then
                if symbols1[i] != symbols2[i]:
                    return False
        # All the symbols match, so move on to create the truth table
        return self._truth_table_check_all(sentence, symbols1.clone(), symbols1.clone())

    def clone(self) -> Sentence:
        return deepcopy(self)

    def convert_to_cnf(self, or_clauses_only=False) -> Union[Sentence, List[Sentence]]:
        # This function transforms the sentence into Conjunctive Normal Form
        # CNF is a form made up of Ors connected by ANDs i.e. (A OR B OR C) AND (D OR E OR F)
        # 3-CNF is the 3-SAT problem
        # If you set or_clauses_only to True, you'll get back not a Sentence but a list of Sentences that can then
        # be freely added to a knowledge base in CNF format without resetting it to no longer being in CNF format.
        sentence: Sentence = self.clone()
        sentence = sentence._transform_conditionals()
        sentence = sentence._transform_not()
        # Now loop over redistributing ORs until nothing changes any more
        temp_sentence: Sentence = Sentence()
        while temp_sentence.to_string(True) != sentence.to_string(True):
            temp_sentence = sentence.clone()
            sentence = sentence._transform_distribute_ors()
        # Mark this sentence as in cnf format
        sentence._is_cnf = True
        # Is this to be converted into a list of CNF clauses with only or clauses?
        if or_clauses_only:
            temp_kb: kb.PLKnowledgeBase = kb.PLKnowledgeBase()
            temp_kb.add(sentence)
            temp_kb = temp_kb.convert_to_cnf()
            # Set each sentence in the list to is_cnf = True
            return temp_kb.sentences
        else:
            return sentence

    def _transform_conditionals(self) -> Sentence:
        # Start with a clone to avoid any side effect
        sentence: Sentence = self.clone()
        # Transform top level bi-conditional
        if sentence.logic_operator == LogicOperatorTypes.Biconditional:
            # Replace bi-conditional (a <=> b) with a => b AND b => a
            clone_ab: Sentence
            clone_ba: Sentence
            temp: Sentence
            # a => b
            clone_ab = sentence.clone()
            clone_ab.negation = False
            clone_ab.logic_operator = LogicOperatorTypes.Implies
            # b => a
            clone_ba = sentence.clone()
            clone_ba.negation = False
            temp = clone_ba.first_sentence
            clone_ba.first_sentence = clone_ba.second_sentence
            clone_ba.second_sentence = temp
            clone_ba.logic_operator = LogicOperatorTypes.Implies
            # And
            sentence = Sentence(clone_ab, LogicOperatorTypes.And, clone_ba, negated=sentence.negation)
        # Transform top level Implies
        if sentence.logic_operator == LogicOperatorTypes.Implies:
            # Replace implies (a => b) with ~a OR b
            neg_first_sentence: Sentence
            neg_first_sentence = Sentence(sentence.first_sentence, negated=True)
            # neg_first_sentence = neg_first_sentence.transform_conditionals()
            sentence.logic_operator = LogicOperatorTypes.Or
            sentence.first_sentence = neg_first_sentence
        # Top level should now be transformed -- if sentence is not atomic, recurse down the chain
        if not sentence.is_atomic:
            # We have completed the current top node and it's not a condition, so we need to traverse down
            sentence.first_sentence = sentence.first_sentence._transform_conditionals()
            if sentence.second_sentence is not None:
                sentence.second_sentence = sentence.second_sentence._transform_conditionals()
        # Return final result
        return sentence

    def _move_not_inward(self) -> Sentence:
        sentence: Sentence = self.clone()
        # Flip the negation on this sentence
        sentence.negation = not sentence.negation
        # If we now have a non-negated sentence without an operator, then we need to pull it all up one level
        if sentence.logic_operator == LogicOperatorTypes.NoOperator and not sentence.negation \
                and sentence.first_sentence is not None and sentence.second_sentence is None:
            sentence = sentence.first_sentence
        return sentence

    def _transform_not(self) -> Sentence:
        sentence: Sentence = self.clone()
        # CNF requires not (~) to appear only in literals
        if sentence.is_atomic:
            # if sentence is atomic we just want to leave it as is
            return sentence
        else:
            # sentence is complex
            if self.negation:
                # This is a complex sentence with a negation, so deal with it
                sentence.negation = False
                # Flip negation sign on one level down because we just removed the negation at this level
                if sentence.second_sentence is None:
                    # This is a 'negation' only sentence, so pull it up one level
                    sentence = sentence.first_sentence._move_not_inward()
                    if not sentence.is_atomic:
                        sentence = sentence._transform_not()
                else:  # if sentence.second_sentence is not None:
                    # This ia a regular two sentence logical operation
                    sentence.first_sentence = sentence.first_sentence._move_not_inward()
                    # Flip ands and ors because this is a regular complex sentence that was negated
                    if sentence.logic_operator == LogicOperatorTypes.And:
                        sentence.logic_operator = LogicOperatorTypes.Or
                    elif sentence.logic_operator == LogicOperatorTypes.Or:
                        sentence.logic_operator = LogicOperatorTypes.And
                    else:
                        # Throw an error if we don't yet have all other types of operators removed by now
                        raise SentenceError("Do not call transform_not without first calling transform_conditionals.")
                    # Flip negation sign on one level down because we just removed the negation at this level
                    sentence.second_sentence = sentence.second_sentence._move_not_inward()
            # Recurse down to the level
            if sentence.first_sentence is not None:
                sentence.first_sentence = sentence.first_sentence._transform_not()
            if sentence.second_sentence is not None:
                sentence.second_sentence = sentence.second_sentence._transform_not()
            # Return final complex sentence
            return sentence

    def _redistribute_or(self, sub_sentence: Sentence) -> Sentence:
        sentence: Sentence = self.clone()
        # This function should only be called if a) self is guaranteed to be an AND clause,
        if self.logic_operator != LogicOperatorTypes.And:
            raise SentenceError("redistribute_or can only be called on a sentence whose top node is an AND clause.")
        else:
            # Do the redistribution
            sentence.first_sentence = Sentence(sentence.first_sentence, LogicOperatorTypes.Or, sub_sentence)
            sentence.second_sentence = Sentence(sentence.second_sentence, LogicOperatorTypes.Or, sub_sentence)
            return sentence

    def _transform_distribute_ors(self) -> Sentence:
        sentence: Sentence = self.clone()
        sub_sentence: Sentence
        # This function assumes there are no logical operators except AND and OR plus NOT next to only literals
        # Anything else will throw an error
        if sentence.is_atomic:
            # Atomic sentences don't need to change, so just return them
            return sentence
        elif sentence.logic_operator == LogicOperatorTypes.Or:
            # Top level is an Or operator
            if sentence.first_sentence.logic_operator == LogicOperatorTypes.And:
                # We have an OR above an AND on right side
                # Grab the left side to redistribute over the right side
                sub_sentence = sentence.second_sentence.clone()
                # Drop the right side
                sentence = sentence.first_sentence.clone()
                # Now traverse the AND plus any more beneath it and put the left under each AND clause
                sentence = sentence._redistribute_or(sub_sentence)
            elif sentence.second_sentence.logic_operator == LogicOperatorTypes.And:
                # We have an OR above an AND on right side
                # Grab the left side to redistribute over the right side
                sub_sentence = sentence.first_sentence.clone()
                # Drop the right side
                sentence = sentence.second_sentence.clone()
                # Now traverse the AND plus any more beneath it and put the left under each AND clause
                sentence = sentence._redistribute_or(sub_sentence)
        elif sentence.logic_operator == LogicOperatorTypes.And:
            pass
        elif sentence.logic_operator == LogicOperatorTypes.NoOperator:
            pass
        else:
            raise SentenceError("Encountered an illegal operator type in _transform_distribute_ors.")

        # Recurse down
        sentence.first_sentence = sentence.first_sentence._transform_distribute_ors()
        if sentence.second_sentence is not None:
            sentence.second_sentence = sentence.second_sentence._transform_distribute_ors()
        return sentence

    def _is_valid_cnf_or_only(self) -> bool:
        # The rules are the same as for the _is_valid_cnf_include_and version except for the following:
        # 1 & 3. There are no AND operators period
        # This more stringent (but easier to check for) standard is required if you are going to allow
        # this sentence to be inserted into a knowledge base in CNF format because CNF knowledge bases
        # Don't use AND clauses and instead just make them separate lines.
        def is_valid_node(sentence: Sentence) -> bool:
            if sentence.is_atomic:
                return True
            elif not sentence.is_atomic and sentence.second_sentence is None:
                # CNF should always have a second sentence unless it is atomic
                return False
            elif not sentence.is_atomic and sentence.negation:
                # CNF should never have negated sentences unless they are literals (i.e. atomic)
                return False
            elif sentence.logic_operator == LogicOperatorTypes.Or:
                # Full CNF format never has OR clauses only
                return True
            else:
                return False
        # Recursively validate entire sentence is CNF format
        if self.is_atomic:
            return is_valid_node(self)
        else:
            return is_valid_node(self) and self.first_sentence._is_valid_cnf_or_only() \
                     and self.second_sentence._is_valid_cnf_or_only()

    def _is_valid_cnf_include_and(self,  previous_or: bool):
        # This function will verify that the current sentence is really in CNF formatting
        # A Sentence is in CNF format if the following are true:
        # 1. There are no AND operators under an OR operator
        # 2. OR Operators have either atomic sentences under them or other OR sentences
        # 3. AND Operators have either atomic sentences under them, or AND sentences, or OR sentences
        # 4. We never bump into any other type of operator
        # 5. We never have a 'negated sentence' i.e. a complex sentence without a second sentence
        # or_clauses_only set to True will enforce that the following replacement rules (the rest will remain):
        def is_valid_node(sentence: Sentence, current_previous_or: bool) -> bool:
            if sentence.is_atomic:
                return True
            elif not sentence.is_atomic and sentence.second_sentence is None:
                # CNF should always have a second sentence unless it is atomic
                return False
            elif not sentence.is_atomic and sentence.negation:
                # CNF should never have negated sentences unless they are literals (i.e. atomic)
                return False
            elif sentence.logic_operator == LogicOperatorTypes.Or:
                # CNF never has OR clauses with And clauses under them
                if sentence.first_sentence.logic_operator == LogicOperatorTypes.And:
                    return False
                elif sentence.second_sentence.second_sentence == LogicOperatorTypes.And:
                    return False
                return True
            elif sentence.logic_operator == LogicOperatorTypes.And:
                if current_previous_or:
                    return False
                else:
                    return True
            else:
                return False
        # Recursively validate entire sentence is CNF format
        if self.logic_operator == LogicOperatorTypes.Or:
            previous_or = True
        if self.is_atomic:
            return is_valid_node(self, previous_or)
        else:
            return is_valid_node(self, previous_or) \
                   and self.first_sentence._is_valid_cnf_include_and(previous_or=previous_or) \
                   and self.second_sentence._is_valid_cnf_include_and(previous_or=previous_or)

    def is_valid_cnf(self, or_clauses_only=False) -> bool:
        if or_clauses_only:
            self._is_cnf = self._is_valid_cnf_or_only()
        else:
            self._is_cnf = self._is_valid_cnf_include_and(previous_or=False)
        return self._is_cnf