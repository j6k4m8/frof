from lark import Lark, Transformer
import networkx as nx

from ..job import BashJob

SYNTAX = """
start: line+
line        : COMMENT
            | edgelist
            | definition

edgelist    : VARNAME ("->" VARNAME)+

definition  : VARNAME ":" command
?command     : NONESCAPED_STRING

VARNAME     : /[a-zA-Z_-]\w*/

COMMENT     : /#.*/

%import common.ESCAPED_STRING
%import common.SIGNED_NUMBER
%import common.WS
%ignore COMMENT
NONESCAPED_STRING  : /[^\\n]+/
%ignore WS
"""

frof_parser = Lark(SYNTAX)


class FrofTransformer(Transformer):
    def __init__(self, *args, **kwargs) -> None:
        self.G = nx.DiGraph()
        super().__init__(*args, **kwargs)

    def transform(self, tree):
        self._transform_tree(tree)
        return self.G

    # def line(self, line):
    #     return line

    def edgelist(self, edgelist):
        self.G.add_path([str(e) for e in edgelist])

    def definition(self, definition):
        key, command = definition
        key = str(key)
        self.G.node[key]["job"] = BashJob(command)

    def command(self, command):
        return str(command).strip()


class FrofParser:
    def __init__(self) -> None:
        pass

    def parse(self, frof: str) -> nx.DiGraph:
        tree = frof_parser.parse(frof)
        G = FrofTransformer().transform(tree)
        return G
