from prop_logic_parser import PropLogicParser

class PLKnowledgeBase:
    def __init__(self, input_str: str = None) -> None:
        self._prop_logic_parser: PropLogicParser = PropLogicParser(input_str)

