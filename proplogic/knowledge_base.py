from __future__ import annotations
from proplogic.parser import LogicParser
from proplogic.sentence import Sentence, LogicOperatorTypes
from typing import Optional, List, Union
from copy import deepcopy
from proplogic.symbol import LogicSymbol, SymbolList, LogicValue
import random


def sentence_or_str(sentence_in: Union[Sentence, str]) -> Sentence:
    """
    Given a sentence in the format of a Sentence or str, return it as a Sentence.
    :param sentence_in: The sentence as a Sentence or str
    :return: A Sentence
    """
    # Pass in a Sentence or string and outcomes a definitive Sentence
    sentence_out: Sentence
    # Make sure in right format
    if isinstance(sentence_in, Sentence):
        sentence_out = sentence_in
    elif isinstance(sentence_in, str):
        sentence_out = Sentence(sentence_in)
    else:
        raise KnowledgeBaseError("Attempted to pass an invalid type as 'query' parameter.")
    return sentence_out


def _set_symbol_in_model(symbol: LogicSymbol, symbol_list: SymbolList, a_model: SymbolList) -> (SymbolList, SymbolList):
    if symbol is not None:
        # Remove symbol from the list of symbols
        symbol_list = symbol_list.clone()
        symbol_list.pop(symbol.name)
        # Extend the model with this symbol and value
        a_model = a_model.clone()
        a_model.set_value(symbol.name, symbol.value)
        return symbol_list, a_model


def each_pair(current_clauses: PLKnowledgeBase, new_clauses: PLKnowledgeBase = None) -> (Sentence, Sentence):
    i: int
    j: int
    if new_clauses is None:
        new_clauses = current_clauses
    for i in range(len(current_clauses.sentences)):
        first_clause: Sentence = current_clauses.sentences[i]
        if current_clauses is new_clauses:
            for j in range(i+1, len(current_clauses.sentences)):
                second_clause: Sentence = current_clauses.sentences[j]
                if first_clause != second_clause:
                    yield first_clause, second_clause
                else:
                    continue
        else:
            for j in range(len(new_clauses.sentences)):
                second_clause: Sentence = new_clauses.sentences[j]
                if first_clause != second_clause:
                    yield first_clause, second_clause
                else:
                    continue


def do_resolution(current_clauses: PLKnowledgeBase, new_clauses: PLKnowledgeBase = None) -> bool:
    new: PLKnowledgeBase
    if new_clauses is None:
        new = current_clauses
    else:
        new = new_clauses
    while True:
        last: PLKnowledgeBase = new
        new = PLKnowledgeBase()
        for clause1, clause2 in each_pair(current_clauses, last):
            resolvents: List[Sentence] = _pl_resolve(clause1, clause2)
            if len(resolvents) > 0:
                # One or more new clauses was generated
                for resolvent in resolvents:
                    if resolvent.logic_operator == LogicOperatorTypes.NO_OPERATOR and resolvent.symbol is None \
                            and resolvent.is_atomic:
                        return True
                else:
                    new.add(resolvents)
        # If new is a subset of clauses then return False
        if new.is_subset(current_clauses):
            return False
        if new.line_count > 0:
            current_clauses.add(new.sentences)
        else:
            return False


def _pl_resolve(clause1: Sentence, clause2: Sentence) -> List[Sentence]:
    def is_always_true(a_clause: Sentence) -> bool:
        all_symbols: List[LogicSymbol] = a_clause.get_atomic_symbols()
        symbol_dict = {}
        i: int
        j: int
        a_symbol: LogicSymbol
        for a_symbol in all_symbols:
            if a_symbol.name in symbol_dict:
                if symbol_dict[a_symbol.name] != a_symbol.value:
                    return True
            else:
                symbol_dict[a_symbol.name] = a_symbol.value
        return False

    def create_clause(symbol_list1: List[LogicSymbol], symbol_list2: List[LogicSymbol]):
        symbol_list: List[LogicSymbol] = []
        sentence_str: str = ""
        symbol_list.extend(symbol_list1)
        symbol_list.extend(symbol_list2)
        symbol_list = list(set(symbol_list))
        symbol_list.sort()
        for a_symbol in symbol_list:
            if a_symbol.value == LogicValue.TRUE:
                sentence_str += a_symbol.name
            elif a_symbol.value == LogicValue.FALSE:
                sentence_str += "~" + a_symbol.name
            else:
                raise KnowledgeBaseError("Called 'create_clause with UNDEFINED logic value.")
            if a_symbol != symbol_list[len(symbol_list)-1]:
                sentence_str += " OR "
        return Sentence(sentence_str)

    # A cnf clause is entirely made up of OR operators and negations
    # So just get a list of all symbols (including duplicates) and their negations and do resolution on those
    symbols1: List[LogicSymbol] = clause1.get_atomic_symbols()
    symbols2: List[LogicSymbol] = clause2.get_atomic_symbols()
    resolvents: List[Sentence] = []
    for symbol in deepcopy(symbols1):
        # Look for a negated version of this symbol
        negated_symbol = LogicSymbol(symbol.name)
        if symbol.value == LogicValue.TRUE:
            negated_symbol.value = LogicValue.FALSE
        elif symbol.value == LogicValue.FALSE:
            negated_symbol.value = LogicValue.TRUE
        else:
            raise KnowledgeBaseError("Should never have an UNDEFINED value returned from get_atomic_symbols.")
        # Is a negated version of this symbol in the other clause? (and this clause has no negated version of itself)
        if negated_symbol in symbols2 and symbol not in symbols2 \
                and symbol in symbols1 and negated_symbol not in symbols1:
            # Remove both symbols and create a new combined clause
            clone_symbols1 = deepcopy(symbols1)
            clone_symbols2 = deepcopy(symbols2)
            clone_symbols1.remove(symbol)
            clone_symbols2.remove(negated_symbol)
            new_clause: Sentence = create_clause(clone_symbols1, clone_symbols2)
            # If you combine a literal and its negation, this leads to long run times even though it makes
            # the clause always True, so you can actually ignore this clause. So check for that.
            if not is_always_true(new_clause):
                resolvents.append(new_clause)
    return resolvents


class KnowledgeBaseError(Exception):
    def __init__(self, message):
        super().__init__(message)


class _KBIterator:
    def __init__(self, kb: PLKnowledgeBase):
        self._clauses: List[Sentence] = kb.sentences
        self._index: int = 0

    def __next__(self):
        result: Sentence
        if self._index < len(self._clauses):
            result = self._clauses[self._index]
            self._index += 1
            return result
        else:
            raise StopIteration


class PLKnowledgeBase:
    """
    PLKnowledgeBase is a class that wraps up the functionality of a Propositional Logic Knowledge Base.

    Usage
    _____

        kb = PLKnowledgeBase()
        input_str = "A"
        kb.add(input_str)
        # evaluates to True
        kb.is_query_true('A')

    """
    # Static parser -- so that Sentence can parse propositional logic text
    _parser: LogicParser = LogicParser()

    def __init__(self) -> None:
        # A propositional logic knowledge base is really just an array of propositional logic sentences
        self._sentences: List[Sentence] = []
        # Used for finding symbol that is a unit clause
        self._count_of_symbols: int = 0
        self._is_cnf: bool = False

    def __iter__(self) -> _KBIterator:
        return _KBIterator(self)

    @property
    def is_cnf(self) -> bool:
        return self._is_cnf

    @property
    def sentences(self) -> List[Sentence]:
        return self._sentences

    def clear(self) -> None:
        """
        Clears the knowledge base by deleting all of its sentences.
        :return: None
        """
        self._sentences = []
        self._is_cnf = False

    def exists(self, sentence: Union[Sentence, str], check_logical_equivalence: bool = False) -> bool:
        """
        The exists method checks if a given sentence (Sentence or str) is already in the database.
        :param sentence: The sentence (Sentence or str) you want to check.
        :param check_logical_equivalence: If set to False (default) just checks if that specific string is in the
        database already via a comparison of this sentence with a string representation of all other sentences
        in the knowledge base. But if set to True, it will do an actual logical comparison instead via a truth table.
        :return: A boolean value of True if this sentences is already in the database, otherwise returns False.
        """
        if isinstance(sentence, Sentence):
            for a_sentence in self._sentences:
                if not check_logical_equivalence:
                    # Using quick check is preferred, it just makes sure the two sentences resolve to same string
                    if a_sentence.to_string(True) == sentence.to_string(True):
                        return True
                else:  # not check_logical_equivalence
                    # Slow check will instead seek if any of these sentences is logically equivalent
                    if a_sentence == sentence:
                        return True
            # Didn't find a match, so doesn't exist
            return False
        elif isinstance(sentence, str):
            self._parser.set_input(sentence)
            new_sentence: Sentence = self._parser.parse_line()
            if self._parser.line_count > 0:
                raise KnowledgeBaseError("Call to 'exists' only works for a single logical line.")
            return self.exists(new_sentence, check_logical_equivalence=check_logical_equivalence)
        else:
            raise KnowledgeBaseError("Call to 'exists' call requires a Sentence or string.")

    def is_subset(self, other_kb: PLKnowledgeBase, check_logical_equivalence: bool = False) -> bool:
        """
        Checks if one knowledge base (self) is a subset of another knowledge base (other_kb)
        :param other_kb: The knowledge base to compare
        :param check_logical_equivalence: Set this to True if you want to do a full equivalence check instead of just
        checking if the two string representations match.
        :return: Returns bool value of True if self is a subset of other_kb, otherwise False
        :return:
        """
        sentence: Sentence
        for sentence in self.sentences:
            if not other_kb.exists(sentence, check_logical_equivalence=check_logical_equivalence):
                return False
        # There were no unique sentences found, so this is subset
        return True

    def add(self, sentence_or_list:  Union[Sentence, List[Sentence], str]) -> None:
        """
        Adds a sentence (Sentence or str) or list of sentences (List[Sentence]) to the database.
        :param sentence_or_list: A Sentence, str, or List[Sentence] of what you want to add.
        :return: None
        """
        if isinstance(sentence_or_list, str):
            PLKnowledgeBase._parser.set_input(sentence_or_list)
            sentence_list: List[Sentence] = PLKnowledgeBase._parser.parse_input()
            self.add(sentence_list)
        elif isinstance(sentence_or_list, Sentence):
            if not self.exists(sentence_or_list):
                self._sentences.append(sentence_or_list)
            if sentence_or_list.is_valid_cnf():
                self._is_cnf = True
            else:
                self._is_cnf = False
        elif isinstance(sentence_or_list, list) and isinstance(sentence_or_list[0], Sentence):
            # A list of Sentences
            for sentence in sentence_or_list:
                self.add(sentence)
        else:
            raise KnowledgeBaseError("Function 'add' called with an incorrect type. Must be a Sentence, str, "
                                     "or List[Sentence]")

    @property
    def line_count(self) -> int:
        """
        :return: Returns the number of sentences contained in the database.
        """
        return len(self._sentences)

    def get_sentence(self, index: int) -> Sentence:
        """

        :param index:
        :return:
        """
        if index <= len(self._sentences):
            return self._sentences[index]
        else:
            raise KnowledgeBaseError("Attempted to use get_sentence(index) with index out of bounds.")

    def clone(self, query: Union[Sentence, str] = None) -> PLKnowledgeBase:
        """
        Makes a clone of this PLKnowledgeBase.
        :param query: A Sentence or str with a query to add to the clone (for convenience)
        :return: A new PLKnowledgeBase that clones the current (self) one.
        """
        kb_clone: PLKnowledgeBase = deepcopy(self)
        if query is not None:
            kb_clone.add(query)
        return kb_clone

    def get_symbol_list(self) -> SymbolList:
        """
        Traverses the knowledge base tree and finds each symbol and then returns them all as a SymbolList.
        :return: This returns a SymbolList of all symbols all set to UNDEFINED
        """
        sl: SymbolList = SymbolList()
        for sentence in self._sentences:
            sl.add(sentence.get_symbol_list())
        return sl

    def is_false(self, model: SymbolList) -> bool:
        """
        Given a model, determines if we know enough to determine the knowledge base is False.
        :param model: A SymbolList
        :return: A boolean result.
        """
        return self.evaluate(model) == LogicValue.FALSE

    def is_true(self, model: SymbolList) -> bool:
        """
        Given a model, determines if we know enough to determine the knowledge base is True.
        :param model: A SymbolList
        :return: A boolean result.
        """
        return self.evaluate(model) == LogicValue.TRUE

    def evaluate(self, model: SymbolList) -> LogicValue:
        """
        Takes a model (a SymbolList with values) and evaluate each Sentence in the knowledge base with that model.
        If all sentences are True, the whole knowledge base is True. If any are False the whole is False.
        If there isn't enough information available, return UNDEFINED.
        :param model: A SymbolList to use in the evaluation.
        :return: A LogicValue
        """
        result: LogicValue = LogicValue.TRUE
        for sentence in self._sentences:
            if sentence.evaluate(model) == LogicValue.FALSE:
                # If one sentence is false, the whole knowledge base is false
                return LogicValue.FALSE
            elif sentence.evaluate(model) == LogicValue.UNDEFINED:
                # We have at least one Undefined, so the default is now Undefined
                result = LogicValue.UNDEFINED
        return result

    def _truth_table(self, query: Sentence, symbols: SymbolList, model: SymbolList, use_speedup=False) \
            -> (int, int):
        # Verify we're in cnf format if using the unit clause speedup, otherwise disable the speedup
        if use_speedup and not self.is_cnf:
            use_speedup = False

        # This function is a truth table check that utilizes dpll speed-ups
        # An experiment to see if this is faster/better

        # If we have no more symbols to try, then start doing evaluations
        if symbols is None or symbols.length == 0:
            if self.is_true(model):
                eval_query: LogicValue = query.evaluate(model)
                if eval_query == LogicValue.TRUE:
                    return 1, 0
                elif eval_query == LogicValue.FALSE:
                    return 0, 1
                else:
                    # This query is undefined for this model, so this model can be ignored
                    return 0, 0
            else:
                # If the model is not specifically True, then throw it away
                return 0, 0
        elif self.is_true(model):
            # Part of strategy 1: early termination
            eval_query: LogicValue = query.evaluate(model)
            if eval_query == LogicValue.TRUE:
                return 1, 0
            elif eval_query == LogicValue.FALSE:
                return 0, 1
            # Else this query is undefined for this model, so this model so process normally
        elif self.is_false(model):
            # Part of strategy 1: early termination
            return 0, 0
        elif use_speedup:
            # Strategy 3: Handle unit clauses
            unit_symbol: LogicSymbol = self.find_unit_clause(model)
            if unit_symbol is not None:
                # Move this symbol from the symbols list (of symbols to try) to the model (symbols with values assigned)
                symbols, model = _set_symbol_in_model(unit_symbol, symbols, model)
                return self._truth_table(query, symbols, model, use_speedup=use_speedup)

        # Done with pure symbol and unit clause shortcuts for now.
        # Now extend the model with both True and False (similar to truth table entails)
        # You don't yet have a full model - so get next symbol to try out
        next_symbol: str = symbols.get_next_symbol().name
        # Extend model as both True and False
        copy_model1: SymbolList = model.extend_model(next_symbol, True)
        copy_model2: SymbolList = model.extend_model(next_symbol, False)
        # Try both extended models
        true_count1, false_count1 = self._truth_table(query, symbols.clone(), copy_model1, use_speedup=use_speedup)
        if true_count1 > 0 and false_count1 > 0:
            return 1, 1
        true_count2, false_count2 = self._truth_table(query, symbols.clone(), copy_model2, use_speedup=use_speedup)
        if true_count2 > 0 and false_count2 > 0:
            return 1, 1
        return true_count1 + true_count2, false_count1 + false_count2

    def truth_table_entails(self, query: Union[Sentence, str], use_speedup=False) -> LogicValue:
        """
        An implementation of the Truth Table entails algorithm. Given a query sentence, returns if the knowledge base
        entails that sentence as True, False, or Undefined.

        This algorithm includes some dpll speedups if the knowledge base is in CNF format, and you ask for it.
        :param query: A Sentence or str that contains the query to the database.
        :param use_speedup: Defaults to False. Set to True if you want to use unit clause heuristic if already in CNF.
        :return: A LogicValue
        """
        query_sentence: Sentence = sentence_or_str(query)
        # Make a list of symbols all reset to undefined
        symbols: SymbolList = self.get_symbol_list()
        symbols.add(query_sentence.get_symbol_list())
        model: SymbolList = symbols.clone()
        # Get true and false counts
        true_count, false_count = self._truth_table(query_sentence, symbols, model, use_speedup=use_speedup)
        # Do final evaluation
        if true_count > 0 and false_count == 0:
            # All True Knowledge Bases evaluate this query as True
            return LogicValue.TRUE
        elif true_count == 0 and false_count > 0:
            # All True Knowledge Bases evaluate this query as False
            return LogicValue.FALSE
        else:
            # It is a weird mix, so we don't know
            return LogicValue.UNDEFINED

    def is_query_true(self, query: Union[Sentence, str]) -> bool:
        """
        Returns True if the query is entailed by the knowledge base.
        :param query: The sentence you are asking if it is entailed in the form of a Sentence or str.
        :return: A boolean value.
        """
        if self.is_cnf:
            return self.dpll_entails(query)
        else:
            return self.truth_table_entails(query) == LogicValue.TRUE

    def is_query_false(self, query: Union[Sentence, str]) -> bool:
        """
        Returns True if the query is known to be False by the knowledge base.
        :param query: The sentence you are asking if it is False in the form of a Sentence or str.
        :return: A boolean value.
        """
        if self.is_cnf:
            sentence: Sentence() = sentence_or_str(query)
            sentence.negate_sentence()
            return self.dpll_entails(sentence)
        else:
            return self.truth_table_entails(query) == LogicValue.FALSE

    def is_query_undefined(self, query: Union[Sentence, str], use_dpll=True) -> bool:
        """
        Returns True if the query is UNDEFINED by the knowledge base.
        :param query: The sentence you are asking if it is UNDEFINED in the form of a Sentence or str.
        :param use_dpll: Optional parameter defaults to True if you wish to use DPLL if in CNF format. Otherwise,
        uses a Truth Table instead. This matters because DPLL needs to run twice to find out if something is UNDEFINED.
        :return: A boolean value.
        """
        if use_dpll and self.is_cnf:
            is_true: bool = self.is_query_true(query)
            is_false: bool = self.is_query_false(query)
            if not is_true and not is_false:
                return True
            else:
                return False
        else:
            return self.truth_table_entails(query) == LogicValue.UNDEFINED

    def convert_to_cnf(self) -> PLKnowledgeBase:
        """
        This function takes the whole knowledge base and converts it to a single knowledge base in CNF form
        with each sentence in the knowledge base being one OR clause

        Returns a version of the knowledge base that is logically equivalent but in CNF format so that it can be used
        with the DPLL algorithms.
        :return: Returns a PLKnowledgeBase
        """
        sentence_list: List[Sentence] = deepcopy(self._sentences)
        converted_list: List[Sentence] = []
        for sentence in sentence_list:
            converted_list.extend(sentence.convert_to_cnf(or_clauses_only=True))
        new_kb: PLKnowledgeBase = PLKnowledgeBase()
        new_kb.add(converted_list)
        new_kb._is_cnf = True
        # Set each sentence in the knowledge base to is_cnf = True also
        for sentence in new_kb.sentences:
            sentence._is_cnf = True
        return new_kb

    def _dpll(self, symbols: SymbolList, model: SymbolList) -> bool:
        # This function evaluates the query against the knowledge base, but does so with the DPLL algorithm
        # instead of a full brute truth table - thus it's faster
        # The query passed must be the entire knowledge base plus the query in CNF form
        # If it isn't, it will error out

        # Verify we're in cnf format
        if not self.is_cnf:
            raise KnowledgeBaseError("Attempt to call _dpll without first being in CNF format.")

        # Strategy 1: Early Termination
        # If every clause in clauses is True in model then return True
        if self.is_true(model):
            return True
        # If some clause in clauses is False in model then return False
        if self.is_false(model):
            return False
        # Otherwise, we are still "Undefined" and so we need to keep recursively building the model
        # Strategy 3: Handle unit clauses - This is equivalent to forward chaining
        unit_symbol: LogicSymbol = self.find_unit_clause(model)
        if unit_symbol is not None:
            # Move this symbol from the symbols list (of symbols to try) to the model (symbols with values assigned)
            symbols, model = _set_symbol_in_model(unit_symbol, symbols, model)
            return self._dpll(symbols, model)
        # Strategy 2: Handle pure symbols
        pure_symbol: LogicSymbol = self.find_pure_symbol(symbols, model)
        if pure_symbol is not None:
            # Move this symbol from the symbols list (of symbols to try) to the model (symbols with values assigned)
            symbols, model = _set_symbol_in_model(pure_symbol, symbols, model)
            return self._dpll(symbols, model)

        # Done with pure symbol and unit clause shortcuts for now.
        # Now extend the model with both True and False (similar to truth table entails)
        # You don't yet have a full model - so get next symbol to try out
        next_symbol: str = symbols.get_next_symbol().name
        # Extend model as both True and False
        copy_model1: SymbolList = model.extend_model(next_symbol, True)
        copy_model2: SymbolList = model.extend_model(next_symbol, False)
        # Try both extended models
        return self._dpll(symbols.clone(), copy_model1) or self._dpll(symbols.clone(), copy_model2)

    def _put_in_cnf_format(self, query: Union[Sentence, str]) -> PLKnowledgeBase:
        # This function does the work for both dpll_entails and pl_resolution to make sure
        # The entire knowledge base is in CNF format including the query.
        # satisfiability is the same as entails via this formula 'a' entails 'b' if a AND ~b are unsatisfiable,
        # so we change the query to be its negation
        model: SymbolList
        # Make sure in right format
        query_sentence: Sentence = sentence_or_str(query)
        # Negate query before adding to the knowledge base
        query_sentence.negate_sentence()
        # Check for CNF format
        if self.is_cnf:
            kb_clone: PLKnowledgeBase = self.clone()
            # Make sure query is in CNF format
            query_list: List[Sentence] = query_sentence.convert_to_cnf(or_clauses_only=True)
            kb_clone.add(query_list)
            return kb_clone
        else:
            cnf_clauses: PLKnowledgeBase = self.clone()
            cnf_clauses.add(query_sentence)
            cnf_clauses = cnf_clauses.convert_to_cnf()
            return cnf_clauses

    def dpll_entails(self, query: Union[Sentence, str]) -> bool:
        """
        Returns True if the query is entailed by the knowledge base. Uses the DPLL algorithm. Must be in CNF format.
        :param query: The sentence you are asking if it is entailed in the form of a Sentence or str.
        :return: A boolean value.
        """
        cnf_kb: PLKnowledgeBase = self._put_in_cnf_format(query)
        symbols: SymbolList = cnf_kb.get_symbol_list()
        model: SymbolList = symbols.clone()
        return not cnf_kb._dpll(symbols, model)

    def satisfied_sentence_count(self, model: SymbolList):
        """
        Count the number of currently satisfied sentences in this knowledge base given a model.
        :param model: The model to use to count with
        :return: Returns the count of currently satisfied sentences given the model
        """
        sentence: Sentence
        count: int = 0
        for sentence in self.sentences:
            if sentence.is_true(model):
                count += 1
        return count

    def walk_sat(self, p: float = 0.5, max_flips: int = 210, seed: Optional[int] = None) -> bool:
        """
        Returns True if the query in the knowledge base can be satisfied. Uses the WalkSAT algorithm, which is random.
        Does not need to be in CNF format.
        :param p: The probability of choosing to do a 'random walk' instead of flipping to max satisfiable statements.
        :param max_flips: Number of flips to try before giving up.
        :param seed: An optional random seed so that the outcome can be repeated (for unit testing)
        :return: A boolean value. True if knowledge base can be satisfied. False if it can't, or we ran out of time.
        """
        if seed is not None:
            random.seed(seed)
        kb_clone: PLKnowledgeBase = self.clone()
        # Initialize model to random values
        model: SymbolList = kb_clone.get_symbol_list()
        symbol: str
        for symbol in model.get_symbols():
            model.set_value(symbol, random.choice([True, False]))
        # Try flipping values
        for i in range(max_flips):
            if kb_clone.is_true(model):
                return True
            if random.random() <= p:
                # Random choice
                flip_symbol: str = random.choice(model.get_keys())
                model.flip_value(flip_symbol)
            else:
                # Flip whichever symbol in the select clause maximizes the number of satisfied clauses
                # Loop through each symbol in the clause
                # Select a random clause that is False
                false_clauses: List[Sentence] = []
                for sentence in kb_clone.sentences:
                    if sentence.evaluate(model) == LogicValue.FALSE:
                        false_clauses.append(sentence)
                clause: Sentence = random.choice(false_clauses)
                sentence_model: SymbolList = clause.get_symbol_list(model)
                # Only interested in models better than what we currently have
                best_count: int = kb_clone.satisfied_sentence_count(model)
                best_symbols: List[LogicSymbol] = []
                for symbol in sentence_model.get_symbols():
                    # Clone current model
                    model_clone: SymbolList = model.clone()
                    model_clone.flip_value(symbol)
                    count: int = kb_clone.satisfied_sentence_count(model_clone)
                    if count > best_count:
                        best_count = count
                        best_symbols = [model_clone.get_symbol(symbol)]
                    elif count == best_count:
                        best_symbols.append(model_clone.get_symbol(symbol))
                if len(best_symbols) > 0:
                    rand_symbol: LogicSymbol = random.choice(best_symbols)
                    model.set_value(rand_symbol.name, rand_symbol.value)
                else:
                    # Flipping each of the symbols in a false statement failed to find a better model
                    # So instead do a random choice
                    flip_symbol: str = random.choice(model.get_keys())
                    model.flip_value(flip_symbol)
        return False

    def walk_sat_entails(self, query: Union[Sentence, str], seed: Optional[int] = None) -> bool:
        """
        Returns True if the query is entailed by the knowledge base. Uses the walk_sat algorithm.
        Does not need to be in CNF format.
        :param query: The sentence you are asking if it is entailed in the form of a Sentence or str.
        :param seed: An optional random seed so that the outcome can be repeated (for unit testing)
        :return: A boolean value. True if the algorithm thinks the query can be entailed by the knowledge base.
        However, since this is a local search random algorithm, there are no guarantees.
        """
        if seed is not None:
            random.seed(seed)
        kb_clone: PLKnowledgeBase = self.clone()
        # Make sure in right format
        query_sentence: Sentence = sentence_or_str(query)
        # Negate query before adding to the knowledge base
        query_sentence.negate_sentence()
        kb_clone.add(query_sentence)
        return not kb_clone.walk_sat()

    def entails(self, query: Union[Sentence, str]) -> bool:
        """
        Returns True if the query is entailed by the knowledge base.
        :param query: The sentence you are asking if it is entailed in the form of a Sentence or str.
        :return: A boolean value. True if this query is entailed by the knowledge base.
        """
        if self.is_cnf:
            return self.dpll_entails(query)
        else:
            return self.truth_table_entails(query) == LogicValue.TRUE

    def find_unit_clause(self, model: SymbolList) -> Optional[LogicSymbol]:
        """
        If the knowledge base is in CNF format this function will return any unit clauses with a LogicValue to set
        it too in the model. Raises an error if not in CNF format.
        :param model: The current model (SymbolList)
        :return: A LogicSymbol of any unit clause and the value it should be set to.
        """
        def search_for_unit_symbol(clause: Sentence, a_model: SymbolList) -> Optional[LogicSymbol]:
            possible_unit: Optional[LogicSymbol]
            total_count: int
            possible_unit, total_count = _search_for_unit_symbol(clause, a_model)
            if total_count == -1 or total_count > 1:
                return None
            else:
                return possible_unit

        def _search_for_unit_symbol(clause: Sentence, a_model: SymbolList) -> (LogicSymbol, int):
            # Pass in a sentence and, if possible, it returns a unit clause symbol.
            # Recursively look through this sentence for one and only one symbol name
            # that has no assignment in the model.
            # Assumption: we are in CNF format
            # Return values consist of a potential unit symbol and a count so far
            if clause is None:
                return None, 0

            total_count: int = 0
            possible_unit: Optional[LogicSymbol]
            if clause.is_atomic:
                # This is just a lone symbol
                value: LogicValue = a_model.get_value(clause.symbol)
                if value == LogicValue.UNDEFINED:
                    # This one has no value assigned yet, so it is a potential unit clause
                    possible_unit = LogicSymbol(clause.symbol)
                    # Set value to positive if no negation and negative otherwise
                    possible_unit.value = not clause.negation
                    return possible_unit, 1
                else:  # if value is TRUE or FALSE
                    # The other condition for a unit clause is that all other literals in the clause are False
                    literal_value: bool = (value == LogicValue.TRUE)
                    # If the clause is negated, then treat a True as a False and vice versa
                    if clause.negation:
                        literal_value = not literal_value
                    if literal_value:
                        # literal_value is True, so this can't be a unit clause
                        return None, -1
                    else:
                        # This literal value is false, so continue processing.
                        return None, 0
            elif clause.logic_operator == LogicOperatorTypes.OR:
                # This is not a lone symbol, so recurse
                # Search first sentence
                count: int
                possible_unit, count = _search_for_unit_symbol(clause.first_sentence, a_model)
                if count == -1:
                    # Abort search
                    return None, -1
                else:
                    total_count += count
                if total_count > 1:
                    # Abort search because this symbol isn't a single unit clause
                    return None, -1
                possible_unit, count = _search_for_unit_symbol(clause.second_sentence, a_model)
                if count == -1:
                    # Abort search
                    return None, -1
                else:
                    total_count += count
                if total_count > 1:
                    # Abort search because this symbol isn't a single unit clause
                    return None, -1
                # Continue search
                return possible_unit, total_count
            else:
                # There should be only OR clauses and unit clauses in each clause if in CNF format
                raise KnowledgeBaseError("find_unit_clause was called for a sentence not in CNF format")

        # This function searches the sentence and, given the model, determines if this sentence is a unit clause
        # A unit clause is defined as either a sentence made up of a single symbol (negated or not)
        # or a clause with all the other symbols evaluating to false (as per model) save one.
        # Assumption: This function assumes we're in CNF or else we get an error
        if not self.is_cnf:
            raise KnowledgeBaseError("Attempt to call find_unit_clause without first being in CNF format.")
        for sentence in self._sentences:
            unit_symbol: LogicSymbol = search_for_unit_symbol(sentence, model)
            if unit_symbol is not None:
                return unit_symbol
        # We didn't find a unit symbol so return None
        return None

    def is_pure_symbol(self, model: SymbolList, search_symbol: str) -> LogicValue:
        """
        Given a model (SymbolList) and a proposed symbol (str) returns if that symbol is a pure symbol (as a LogicValue)
        :param model: A SymbolList with current model values for the symbols.
        :param search_symbol: A symbol (str) to search for.
        :return: A LogicValue where if TRUE or FALSE is a pure symbol and UNDEFINED if not.
        """
        def assess_symbol(a_sentence: Sentence, a_search_symbol: str) -> (int, int):
            # Recursively look through this sentence for symbol_name and return True if there
            # are no negated versions of the symbol in this sentence.
            positive_count: int = 0
            negative_count: int = 0
            if a_sentence.logic_operator == LogicOperatorTypes.OR:
                # Search first sentence
                positives, negatives = assess_symbol(a_sentence.first_sentence, a_search_symbol)
                positive_count += positives
                negative_count += negatives
                if positive_count > 0 and negative_count > 0:
                    return 1, 1
                # Search second sentence
                positives, negatives = assess_symbol(a_sentence.second_sentence, a_search_symbol)
                positive_count += positives
                negative_count += negatives
                if positive_count > 0 and negative_count > 0:
                    return 1, 1
                return positive_count, negative_count
            elif a_sentence.is_atomic:
                if a_sentence.symbol == a_search_symbol and not a_sentence.negation:
                    # We found the symbol without a negation
                    return 1, 0
                elif a_sentence.symbol == a_search_symbol and a_sentence.negation:
                    # We found the symbol with a negation
                    return 0, 1
                else:
                    # Not finding our symbol counts as pure
                    return 0, 0
            else:
                # There should be only OR clauses and unit clauses in each clause if in CNF format
                raise KnowledgeBaseError("is_pure_symbol was called for a sentence not in CNF format")

        total_pos: int = 0
        total_neg: int = 0
        for sentence in self._sentences:
            if not sentence.is_cnf:
                raise KnowledgeBaseError("Called is_pure_symbol without being in CNF format.")
            if sentence.evaluate(model) == LogicValue.UNDEFINED:
                pos: int
                neg: int
                pos, neg = assess_symbol(sentence, search_symbol)
                total_pos += pos
                total_neg += neg
                if total_pos > 0 and total_neg > 0:
                    return LogicValue.UNDEFINED

        if total_pos > 0 and total_neg == 0:
            return LogicValue.TRUE
        elif total_pos == 0 and total_neg > 0:
            return LogicValue.FALSE
        else:
            return LogicValue.UNDEFINED

    def find_pure_symbol(self, symbols: SymbolList, model: SymbolList) -> Optional[LogicSymbol]:
        """
        If in CNF format this method will return any pure symbols it can find. If not in CNF format it raises an error.
        :param symbols:The list of symbols to loop through.
        :param model: The current model with values for each symbol.
        :return: Returns a LogicSymbol with a symbol name and LogicValue for the pure symbol found, otherwise None.
        """
        # Traverse the entire 'clauses' knowledge base looking for a 'pure symbol' which is a symbol that
        # is either all not negated or all negated. These are symbols we can easily decide to set in the model
        # to either True (if not negated) or False (if negated).
        keys: List[str] = symbols.get_keys()
        for key in keys:
            symbol: LogicSymbol = LogicSymbol(key)
            symbol.value = self.is_pure_symbol(model, symbol.name)
            if symbol.value != LogicValue.UNDEFINED:
                return symbol

    def cache_resolvents(self, force_cnf_format=False) -> bool:
        """
        Calling this function runs through all current clauses in the database and works out the existing resolvents,
        i.e. the known consequences of the database, and then stores those in the database.

        This is particularly useful if you plan to run a series of queries but don't want to have to work out
        all the resolvents each time.

        It can also be used to determine if the database is satisfiable or not.

        The database must be in CNF format before calling this function, or it will raise an error, unless
        force_cnf_format is set to True. In that case it will first change the database to be in CNF format.
        :return: Returns if the database is satisfiable or not (as if you called sat_resolution).
        """
        if force_cnf_format:
            self._sentences = self.convert_to_cnf()._sentences
            self._is_cnf = True
        if not self.is_cnf:
            raise KnowledgeBaseError("Called cache_resolvents when not in CNF format.")
        return do_resolution(self)

    def pl_resolution(self, query: Union[Sentence, str], use_cache=False) -> bool:
        if use_cache and self._is_cnf:
            # Make sure query in right format
            query_sentence: Sentence = sentence_or_str(query)
            # Negate query then build a query knowledge base
            query_sentence.negate_sentence()
            query_list: List[Sentence] = query_sentence.convert_to_cnf(or_clauses_only=True)
            query_kb = PLKnowledgeBase()
            query_kb.add(query_list)
            # Do resolution on the query itself
            result: bool = do_resolution(query_kb)
            if result:
                return True
            # Make a clone
            clone_kb = self.clone()
            return do_resolution(clone_kb, query_kb)
        else:
            clauses: PLKnowledgeBase = self._put_in_cnf_format(query)
            return do_resolution(clauses)
