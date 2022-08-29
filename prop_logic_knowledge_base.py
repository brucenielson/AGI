from __future__ import annotations
from prop_logic_parser import PropLogicParser, Sentence, LogicOperatorTypes
from typing import Optional, List, Union, Tuple
from enum import Enum
from copy import deepcopy


def slice_to_ints(a_slice: slice, max_index: int):
    start: int = 0
    stop: int = max_index
    step: int = 1
    if a_slice.step is not None:
        step = a_slice.step
    if a_slice.start is not None:
        start = a_slice.start
    if a_slice.stop is not None:
        stop = a_slice.stop
    keys: range = range(start, stop, step)
    index_list = list(keys)
    return index_list


def create_index(indexes: list, max_index: int) -> List[int]:
    index_list: List[int] = []
    if isinstance(indexes, int):
        index_list.append(indexes)
    elif isinstance(indexes, slice):
        index_list: List[int] = slice_to_ints(indexes, max_index)
    else:
        # Mixture of both integers and slices
        for i in indexes:
            if isinstance(i, int):
                index_list.append(i)
            elif isinstance(i, slice):
                index_list.extend(slice_to_ints(i, max_index))
    return index_list


class LogicValue(Enum):
    FALSE = 0
    TRUE = 1
    UNDEFINED = -1

    def __repr__(self) -> str:
        if self == LogicValue.UNDEFINED:
            return "Undefined"
        elif self == LogicValue.TRUE:
            return "True"
        elif self == LogicValue.FALSE:
            return "False"

    def and_op(self, other_value: LogicValue):
        if self == LogicValue.TRUE and other_value == LogicValue.TRUE:
            return LogicValue.TRUE
        elif self == LogicValue.FALSE or other_value == LogicValue.FALSE:
            return LogicValue.FALSE
        else:
            return LogicValue.UNDEFINED

    def or_op(self, other_value: LogicValue):
        if self == LogicValue.TRUE or other_value == LogicValue.TRUE:
            return LogicValue.TRUE
        elif self == LogicValue.FALSE and other_value == LogicValue.FALSE:
            return LogicValue.FALSE
        else:
            return LogicValue.UNDEFINED


def bool_to_logic_value(value: Union[bool, LogicValue]) -> LogicValue:
    if isinstance(value, bool):
        if value:
            return LogicValue.TRUE
        else:
            return LogicValue.FALSE
    else:
        return value


class LogicSymbol:
    def __init__(self, name: str, value: LogicValue = LogicValue.UNDEFINED):
        self._name = name
        self.value = value

    def __repr__(self) -> str:
        return self.name + ": " + repr(self.value)

    def __eq__(self, other):
        if type(self) == type(other) and self.name == other.name and self.value == other.value:
            return True
        else:
            return False

    @property
    def name(self) -> str:
        return self._name

    @property
    def value(self) -> LogicValue:
        return self._value

    @value.setter
    def value(self, value: Optional[Union[LogicValue, bool]]) -> None:
        final_value: LogicValue
        if isinstance(value, bool):
            if value:
                final_value = LogicValue.TRUE
            else:
                final_value = LogicValue.FALSE
        elif value is None:
            final_value = LogicValue.UNDEFINED
        else:
            final_value = value
        self._value = final_value

    def and_op(self, other_value: LogicValue):
        return self.value.and_op(other_value)

    def or_op(self, other_value: LogicValue):
        return self.value.or_op(other_value)


class SymbolListError(Exception):
    def __init__(self, message):
        super().__init__(message)


class KnowledgeBaseError(Exception):
    def __init__(self, message):
        super().__init__(message)


class SymbolListIterator:
    def __init__(self, symbol_list: SymbolList):
        self._symbol_list: List[str] = symbol_list.get_keys()
        self._index: int = 0

    def __next__(self):
        result: str
        if self._index < len(self._symbol_list):
            result = self._symbol_list[self._index]
            self._index += 1
            return result
        else:
            raise StopIteration


class SymbolList:
    # See https://riptutorial.com/python/example/1571/indexing-custom-classes----getitem------setitem---and---delitem--
    # for now to implement getitem setitem related stuff
    def __init__(self) -> None:
        self._symbols: dict[str, LogicValue] = {}

    def __iter__(self) -> SymbolListIterator:
        return SymbolListIterator(self)

    def __repr__(self) -> str:
        repr_str: str = ""
        keys: List[str] = self.get_keys()
        for symbol_name in keys:
            repr_str += symbol_name + ": " + repr(self._symbols[symbol_name]) + "; "
        return repr_str

    def __getitem__(self, indexes: Union[Tuple[int, int], str, int, list]) \
            -> Union[LogicSymbol, LogicValue, SymbolList]:
        if isinstance(indexes, str):
            return self.get_symbol(indexes).value
        else:
            index_list: List[int] = create_index(indexes, self.length)
            # If there is only one element in the index_list, then return a single LogicSymbol
            if len(index_list) == 1:
                return self.get_symbol(index_list[0])
            # We have a list of indexes, now turn it into a new SymbolList
            output: List[LogicSymbol] = [self.get_symbol(i) for i in index_list]
            new_symbol_list: SymbolList = SymbolList()
            new_symbol_list.add(output)
            return new_symbol_list

    def __setitem__(self, key, value):
        if isinstance(key, int):
            self.set_value(self.get_symbol(key).name, value)
        else:
            for i in key:
                self.set_value(self.get_symbol(i).name, value)

    def __delitem__(self, index: Union[str, int]) -> None:
        if isinstance(index, str):
            self._symbols.pop(index)
        else:
            keys: List[str] = self.get_keys()
            key = keys[index]
            self._symbols.pop(key)

    def get_symbols(self) -> dict[str, LogicValue]:
        return self._symbols

    def get_keys(self) -> List[str]:
        keys: list[str] = list(self._symbols.keys())
        keys.sort()
        return keys

    @property
    def length(self) -> int:
        return len(self._symbols)

    def get_symbol(self, index: Optional[str, int]) -> LogicSymbol:
        if isinstance(index, str):
            index = index.upper()
            if index in self._symbols:
                return LogicSymbol(index, self._symbols[index])
        else:
            if index > len(self._symbols) - 1 or index < 0:
                raise SymbolListError("Call to get_symbol was out of bounds.")
            keys: List[str] = self.get_keys()
            if keys[index] in keys:
                return LogicSymbol(keys[index], self._symbols[keys[index]])

    def pop(self, symbol_name: str) -> LogicSymbol:
        return LogicSymbol(symbol_name, self._symbols.pop(symbol_name))

    def get_next_symbol(self) -> Optional[LogicSymbol]:
        # This function returns the first symbol in the list while removing it
        if len(self._symbols) == 0 or self._symbols is None:
            return None
        else:
            symbol_keys: List[str] = self.get_keys()
            return self.pop(symbol_keys[0])

    def index(self, symbol_name: str) -> Optional[int]:
        symbol_name = symbol_name.upper()
        keys: List[str] = self.get_keys()
        index: Optional[int]
        try:
            index = keys.index(symbol_name)
        except ValueError:
            index = None
        return index

    def add(self, symbol_or_list: Union[LogicSymbol, str, SymbolList, List[LogicSymbol], List[str, int]],
            value: Union[LogicValue, bool] = LogicValue.UNDEFINED) -> None:

        logic_value: LogicValue = bool_to_logic_value(value)
        if isinstance(symbol_or_list, LogicSymbol):
            self._symbols[symbol_or_list.name] = symbol_or_list.value
        elif isinstance(symbol_or_list, list):
            # Concatenate the SymbolList into this SymbolList
            for symbol in symbol_or_list:
                self.add(symbol)
        elif isinstance(symbol_or_list, SymbolList):
            # Concatenate the SymbolList into this SymbolList
            keys: List[str] = symbol_or_list.get_keys()
            for symbol in keys:
                self.add(symbol, symbol_or_list[symbol])
        elif isinstance(symbol_or_list, str):
            symbol_or_list = symbol_or_list.upper()
            self._symbols[symbol_or_list] = logic_value
        else:
            raise SymbolListError("The 'add' command requires a string symbol, LogicSymbol, or a SymbolList")

    def set_value(self, symbol_name: str, value: Optional[Union[LogicValue, bool]]) -> None:
        symbol_name = symbol_name.upper()
        logic_value: LogicValue = bool_to_logic_value(value)
        self._symbols[symbol_name] = logic_value

    def get_value(self, symbol_name: str) -> LogicValue:
        if symbol_name is None:
            return LogicValue.UNDEFINED
        else:
            return self._symbols[symbol_name]

    def clone(self):
        return deepcopy(self)

    def extend_model(self, symbol_name: str, value: bool) -> SymbolList:
        # Like set_value except that it clone the model first and returns the clone
        # thereby leaving the original unchanged
        copy_model: SymbolList = self.clone()
        copy_model.set_value(symbol_name, value)
        return copy_model


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

    def _truth_table_check_all(self, query: Sentence, symbols: SymbolList, model: SymbolList) -> (int, int):
        # This function does the work of creating a truth table and thus evaluating the query against the knowledge base
        # It counts up True and False results returning (True count, False count)
        if symbols is None or symbols.length == 0:
            if self.evaluate(model) == LogicValue.TRUE:
                eval_query: LogicValue = query.evaluate(model)
                if eval_query == LogicValue.TRUE:
                    return 1, 0
                elif eval_query == LogicValue.FALSE:
                    return 0, 1
                return 0, 0
            else:
                # If the model is not specifically True, then throw it away
                return 0, 0
        else:
            # You don't yet have a full model - so get next symbol to try out
            next_symbol: str = symbols.get_next_symbol().name
            # Extend model as both True and False
            copy_model1: SymbolList = model.extend_model(next_symbol, True)
            copy_model2: SymbolList = model.extend_model(next_symbol, False)
            # Try both extended models
            true_count1, false_count1 = self._truth_table_check_all(query, symbols.clone(), copy_model1)
            true_count2, false_count2 = self._truth_table_check_all(query, symbols.clone(), copy_model2)
            return true_count1 + true_count2, false_count1 + false_count2

    def truth_table_entails(self, query: Union[Sentence, str]) -> LogicValue:
        query_sentence: Sentence = sentence_or_str(query)
        # Make a list of symbols all reset to undefined
        symbols: SymbolList = self.get_symbol_list()
        symbols.add(query_sentence.get_symbol_list())
        model: SymbolList = symbols.clone()
        # Get true and false counts
        true_count, false_count = self._truth_table_check_all(query_sentence, symbols, model)
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

    def is_query_undefined(self, query: Union[Sentence, str]) -> bool:
        is_true: bool = self.is_query_true(query)
        is_false: bool = self.is_query_false(query)
        if not is_true and not is_false:
            return True
        else:
            return False

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

    # noinspection SpellCheckingInspection
    def _dpll(self, symbols: SymbolList, model: SymbolList) -> bool:
        def set_symbol_in_model(symbol: LogicSymbol, symbol_list: SymbolList, a_model: SymbolList) \
                -> (SymbolList, SymbolList):
            if symbol is not None:
                # Remove symbol from the list of symbols
                symbol_list = symbol_list.clone()
                symbol_list.pop(symbol.name)
                # Extend the model with this symbol and value
                a_model = a_model.clone()
                a_model.set_value(symbol.name, symbol.value)
                return symbol_list, a_model

        # This function evaluates the query against the knowledge base, but does so with the DPLL algorithm
        # instead of a full brute truth table - thus it's faster
        # The query passed must be the entire knowledge base plus the query in CNF form
        # If it isn't, it will error out

        # Strategy 1: Early Termination
        # If every clause in clauses is True in model then return True
        if self.is_true(model):
            return True
        # If some clause in clauses is False in model then return False
        if self.is_false(model):
            return False
        # Otherwise, we are still "Undefined" and so we need to keep recursively building the model
        # Strategy 2: Handle pure symbols
        # TODO: Does this need to be opmtimized? Seems to slow things down right now.
        pure_symbol: LogicSymbol = self.find_pure_symbol(symbols, model)
        if pure_symbol is not None:
            # Move this symbol from the symbols list (of symbols to try) to the model (symbols with values assigned)
            symbols, model = set_symbol_in_model(pure_symbol, symbols, model)
            return self._dpll(symbols, model)
        # Strategy 3: Handle unit clauses
        unit_symbol: LogicSymbol = self.find_unit_clause(model)
        if unit_symbol is not None:
            # Move this symbol from the symbols list (of symbols to try) to the model (symbols with values assigned)
            symbols, model = set_symbol_in_model(unit_symbol, symbols, model)
            return self._dpll(symbols, model)

        # Done with pure symbol and unit clause short cuts for now
        # Now extend the model with both True and False (simlar to truth table entails)
        # You don't yet have a full model - so get next symbol to try out
        next_symbol: str = symbols.get_next_symbol().name
        # Extend model as both True and False
        copy_model1: SymbolList = model.extend_model(next_symbol, True)
        copy_model2: SymbolList = model.extend_model(next_symbol, False)
        # Try both extended models
        return self._dpll(symbols.clone(), copy_model1) or self._dpll(symbols.clone(), copy_model2)

    # noinspection SpellCheckingInspection
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
            # TODO: Fix this
            # elif not clause.is_cnf:
            #     raise KnowledgeBaseError("Attempt to call search_for_unit_symbol without first being in CNF format.")

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

    def is_pure_symbol(self, model: SymbolList, search_symbol: str, negation: bool) -> bool:
        def assess_symbol(a_sentence: Sentence) -> bool:
            # Recursively look through this sentence for symbol_name and return True if there
            # are no negated versions of the symbol in this sentence.
            if a_sentence.logic_operator == LogicOperatorTypes.Or:
                return assess_symbol(a_sentence.first_sentence) and assess_symbol(a_sentence.second_sentence)
            elif a_sentence.is_atomic:
                if a_sentence.symbol == search_symbol and a_sentence.negation == negation:
                    # We found the symbol with its correct sign
                    return True
                elif a_sentence.symbol == search_symbol and a_sentence.negation != negation:
                    # We found an opposite sign, so now the whole of it is False
                    return False
                else:
                    # Not finding our symbol counts as pure
                    return True
            else:
                # There should be only OR clauses and unit clauses in each clause if in CNF format
                raise KnowledgeBaseError("is_pure_symbol was called for a sentence not in CNF format")
        is_pure: bool = True
        for sentence in self._sentences:
            # if not sentence.is_cnf:
            #     raise KnowledgeBaseError("Called is_pure_symbol without being in CNF format.")
            if sentence.evaluate(model) == LogicValue.UNDEFINED:  # TODO: This seems inefficient
                if not assess_symbol(sentence):
                    is_pure = False
                    break
        return is_pure

    def find_pure_symbol(self, symbols: SymbolList, model: SymbolList) -> Optional[LogicSymbol]:
        # Traverse the entire 'clauses' knowledge base looking for a 'pure symbol' which is a symbol that
        # is either all not negated or all negated. These are symbols we can easily decide to set in the model
        # to either True (if not negated) or False (if negated).
        keys: List[str] = symbols.get_keys()
        for key in keys:
            symbol: LogicSymbol = LogicSymbol(key)
            # TODO: Seems like I could somehow combine the two calls to is_pure_symbol into one call and optimize it
            if self.is_pure_symbol(model, symbol.name, False):
                symbol.value = LogicValue.TRUE  # TODO: Does this create a side effect?
                return symbol
            if self.is_pure_symbol(model, symbol.name, True):
                symbol.value = LogicValue.FALSE  # TODO: Does this create a side effect?
                return symbol
        return None
