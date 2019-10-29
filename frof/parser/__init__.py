from lark import Lark, Transformer
import networkx as nx

from ..job import BashJob

SYNTAX = """
start: line+
line        : COMMENT
            | edgelist
            | definition
            | param_defn

edgelist    : jobname ("->" jobname)+


?jobname    : VARNAME
            | VARNAME"(" params ")"

params      : (param)+

?param      : "&" PARAMNAME "[" SIGNED_NUMBER "]"
            | "&" PARAMNAME

PARAMNAME   : VARNAME

definition  : VARNAME ":" command

param_defn  : "&" PARAMNAME ":" param_cmd

?param_cmd  : NONESCAPED_STRING
?command    : NONESCAPED_STRING

VARNAME     : /[a-zA-Z_-]\w*/

COMMENT     : /#.*/

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
        self._params = {}
        self._job_param_assignments = {}
        self.interpolation_enabled = True
        super().__init__(*args, **kwargs)

    def transform(self, tree):
        self._transform_tree(tree)

        for jobname, paramname in self._job_param_assignments.items():
            job = self.G.node[jobname]
            ins = [u for u, v in self.G.in_edges(jobname)]
            outs = [v for u, v in self.G.out_edges(jobname)]

            for option in self._params[paramname]:
                job_text = job["job"].cmd
                if self.interpolation_enabled:
                    job_text = job_text.replace("{{&" + paramname + "}}", option)
                self.G.add_node(
                    f"{jobname}_{option}",
                    job=BashJob(job_text, env={"FROF_JOB_PARAM": option}),
                )
                for i in ins:
                    self.G.add_edge(i, f"{jobname}_{option}")
                for i in outs:
                    self.G.add_edge(f"{jobname}_{option}", i)
            self.G.remove_node(jobname)
        return self.G

    def edgelist(self, edgelist):
        self.G.add_path([str(e) for e in edgelist])

    def jobname(self, jobname):
        jobname, param_set = jobname
        for param in param_set:
            self._job_param_assignments[str(jobname)] = param
        return jobname

    def params(self, params):
        for param in params:
            if str(param) not in self._params:
                self._params[str(param)] = {}
        return [str(p) for p in params]

    def param_defn(self, param_defn):
        param, param_defn = param_defn
        self._params[str(param)] = eval(str(param_defn))

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
