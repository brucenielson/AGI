from __future__ import annotations
from pl_parser import PropLogicParser
from sentence import Sentence, LogicOperatorTypes
from typing import Optional, List, Union
from copy import deepcopy
from logic_symbols import LogicSymbol, SymbolList, LogicValue


def sentence_or_str(sentence_in: Union[Sentence, str]) -> Sentence:
    # Pass in a Sentence or string and out comes a definitive Sentence
    sentence_out: Sentence
    # Make sure in right format
    if isinstance(sentence_in, Sentence):
        sentence_out = sentence_in
    elif isinstance(sentence_in, str):
        sentence_out = Sentence(sentence_in)
    else:
        raise KnowledgeBaseError("Attempted to pass an invalid type as 'query' parameter.")
    return sentence_out


def set_symbol_in_model(symbol: LogicSymbol, symbol_list: SymbolList, a_model: SymbolList) -> (SymbolList, SymbolList):
    if symbol is not None:
        # Remove symbol from the list of symbols
        symbol_list = symbol_list.clone()
        symbol_list.pop(symbol.name)
        # Extend the model with this symbol and value
        a_model = a_model.clone()
        a_model.set_value(symbol.name, symbol.value)
        return symbol_list, a_model


class KnowledgeBaseError(Exception):
    def __init__(self, message):
        super().__init__(message)


class PLKnowledgeBase:
    # Static parser -- so that Sentence can parse propositional logic text
    _parser: PropLogicParser = PropLogicParser()

    def __init__(self) -> None:
        # A propositional logic knowledge base is really just an array of propositional logic sentences
        self._sentences: List[Sentence] = []
        # Used for finding symbol that is a unit clause
        self._count_of_symbols: int = 0
        self._is_cnf: bool = False

    @property
    def is_cnf(self) -> bool:
        return self._is_cnf

    @property
    def sentences(self) -> List[Sentence]:
        return self._sentences

    def clear(self) -> None:
        self._sentences = []
        self._is_cnf = False

    def exists(self, sentence: Union[Sentence, str], check_logical_equivalence: bool = False) -> bool:
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

    def add(self, sentence_or_list:  Union[Sentence, List[Sentence], str]) -> None:
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
        else:
            for sentence in sentence_or_list:
                self.add(sentence)

    @property
    def line_count(self) -> int:
        return len(self._sentences)

    def get_sentence(self, index: int) -> Sentence:
        if index <= len(self._sentences):
            return self._sentences[index]
        else:
            raise KnowledgeBaseError("Attempted to use get_sentence(index) with index out of bounds.")

    def clone(self):
        return deepcopy(self)

    def get_symbol_list(self) -> SymbolList:
        # Traverse the knowledge base tree and find each symbol
        # This returns a list of symbols all set to undefined rather than to values they currently hold
        sl: SymbolList = SymbolList()
        for sentence in self._sentences:
            sl.add(sentence.get_symbol_list())
        return sl

    def is_false(self, model: SymbolList) -> bool:
        return self.evaluate(model) == LogicValue.FALSE

    def is_true(self, model: SymbolList) -> bool:
        return self.evaluate(model) == LogicValue.TRUE

    def evaluate(self, model: SymbolList) -> LogicValue:
        # Take the model (a SymbolList with values) and evaluate each Sentence in the knowledge base.
        # If all are true, the whole is true. If any are false the whole is false.
        # If there isn't enough information available, return Undefined.
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

        # This function is a truth table check that utilizes dpll speed ups
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
                symbols, model = set_symbol_in_model(unit_symbol, symbols, model)
                return self._truth_table(query, symbols, model, use_speedup=use_speedup)

        # Done with pure symbol and unit clause short cuts for now
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

    def truth_table_entails(self, query: Union[Sentence, str]) -> LogicValue:
        query_sentence: Sentence = sentence_or_str(query)
        # Make a list of symbols all reset to undefined
        symbols: SymbolList = self.get_symbol_list()
        symbols.add(query_sentence.get_symbol_list())
        model: SymbolList = symbols.clone()
        # Get true and false counts
        true_count, false_count = self._truth_table(query_sentence, symbols, model)
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
        return self.dpll_entails(query)

    def is_query_false(self, query: Union[Sentence, str]) -> bool:
        sentence: Sentence() = sentence_or_str(query)
        sentence.negate_sentence()
        return self.dpll_entails(sentence)

    def is_query_undefined(self, query: Union[Sentence, str], use_dpll=False) -> bool:
        if use_dpll:
            is_true: bool = self.is_query_true(query)
            is_false: bool = self.is_query_false(query)
            if not is_true and not is_false:
                return True
            else:
                return False
        else:
            return self.truth_table_entails(query) == LogicValue.UNDEFINED

    def _build_cnf_knowledge_base(self, sentence: Sentence):
        # This function takes a CNF Sentence and builds a knowledge base out of it where each OR clause
        # becomes becomes a single sentence in the knowledge base.
        # Assumption: this sentence is already in CNF form -- if it isn't, the results are unpredictable
        # every time it's called, the top node must be an AND operator or symbol
        #
        # This function will traverse a sentence finding disjunctions and splicing it all up into sentences
        # that are added to the knowledge base passed in.
        #
        # Strategy: recurse through the whole sentence tree and find each AND clause and then grab the clauses
        # in between (which are either OR clauses or symbols) and stuff them separately into the knowledge base
        def recurse_sentence(a_sentence: Sentence):
            if a_sentence.logic_operator == LogicOperatorTypes.Or or a_sentence.is_atomic:
                # This is the top of an OR clause or it's atomic, so add it
                self.add(a_sentence)
            elif a_sentence.logic_operator == LogicOperatorTypes.And:
                # It is an and clause, so recurse
                self._build_cnf_knowledge_base(a_sentence)
            else:
                # It is neither an and nor an or, so we must not be in CNF form. Raise error.
                raise KnowledgeBaseError("_build_cnf_Knowledge_base was called with a 'sentence' not in CNF form.")

        if sentence.logic_operator == LogicOperatorTypes.And:
            recurse_sentence(sentence.first_sentence)
            recurse_sentence(sentence.second_sentence)
        elif sentence.logic_operator == LogicOperatorTypes.Or:
            recurse_sentence(sentence)
        elif sentence.is_atomic:
            # It's a symbol, so just put it into the database
            self.add(sentence)
        else:
            raise KnowledgeBaseError("_build_cnf_Knowledge_base was called with a 'sentence' not in CNF form.")

    def convert_to_cnf(self) -> PLKnowledgeBase:
        # This function takes the whole knowledge base and converts it to a single knowledge base in CNF form
        # with each sentence in the knowledge base being one OR clause
        cnf_kb: str = ""
        for sentence in self._sentences:
            # TODO is there a more efficient way to do this then to make into a string then convert back to Sentence?
            if len(cnf_kb) > 0:
                cnf_kb += " AND "
            cnf_kb += sentence.to_string(True)
        sentence = Sentence(cnf_kb)
        sentence = sentence.convert_to_cnf()
        # "sentence" now contains the entire knowledge base in a single logical sentence
        # Now loop through and find each OR clause and build a new knowledge base out of it
        new_kb: PLKnowledgeBase = PLKnowledgeBase()
        new_kb._build_cnf_knowledge_base(sentence)
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
            symbols, model = set_symbol_in_model(unit_symbol, symbols, model)
            return self._dpll(symbols, model)
        # Strategy 2: Handle pure symbols
        pure_symbol: LogicSymbol = self.find_pure_symbol(symbols, model)
        if pure_symbol is not None:
            # Move this symbol from the symbols list (of symbols to try) to the model (symbols with values assigned)
            symbols, model = set_symbol_in_model(pure_symbol, symbols, model)
            return self._dpll(symbols, model)

        # Done with pure symbol and unit clause short cuts for now
        # Now extend the model with both True and False (similar to truth table entails)
        # You don't yet have a full model - so get next symbol to try out
        next_symbol: str = symbols.get_next_symbol().name
        # Extend model as both True and False
        copy_model1: SymbolList = model.extend_model(next_symbol, True)
        copy_model2: SymbolList = model.extend_model(next_symbol, False)
        # Try both extended models
        return self._dpll(symbols.clone(), copy_model1) or self._dpll(symbols.clone(), copy_model2)

    def dpll_entails(self, query: Union[Sentence, str]) -> bool:
        #  satisfiability is the same as entails via this formula
        #  a entails b if a AND ~b are unsatisfiable
        #  so we change the query to be it's negation
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
            symbols: SymbolList = kb_clone.get_symbol_list()
            model: SymbolList = symbols.clone()
            return not kb_clone._dpll(symbols, model)
        else:
            cnf_clauses: PLKnowledgeBase = self.clone()
            cnf_clauses.add(query_sentence)
            cnf_clauses = cnf_clauses.convert_to_cnf()
            symbols: SymbolList = cnf_clauses.get_symbol_list()
            model: SymbolList = symbols.clone()
            return not cnf_clauses._dpll(symbols, model)

    def entails(self, query):
        return self.dpll_entails(query)

    def find_unit_clause(self, model: SymbolList) -> Optional[LogicSymbol]:
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
            elif clause.logic_operator == LogicOperatorTypes.Or:
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
        def assess_symbol(a_sentence: Sentence, a_search_symbol: str) -> (int, int):
            # Recursively look through this sentence for symbol_name and return True if there
            # are no negated versions of the symbol in this sentence.
            positive_count: int = 0
            negative_count: int = 0
            if a_sentence.logic_operator == LogicOperatorTypes.Or:
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
                    # We found the symbol with out a negation
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
        # Traverse the entire 'clauses' knowledge base looking for a 'pure symbol' which is a symbol that
        # is either all not negated or all negated. These are symbols we can easily decide to set in the model
        # to either True (if not negated) or False (if negated).
        keys: List[str] = symbols.get_keys()
        for key in keys:
            symbol: LogicSymbol = LogicSymbol(key)
            symbol.value = self.is_pure_symbol(model, symbol.name)
            if symbol.value != LogicValue.UNDEFINED:
                return symbol
