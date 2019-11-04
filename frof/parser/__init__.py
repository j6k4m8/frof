import uuid
from lark import Lark, Transformer
import networkx as nx

from ..job import BashJob

SYNTAX = """
start: line+
line        : COMMENT
            | edgelist
            | single_job
            | definition
            | param_defn

edgelist    : jobname ("->" jobname)+

single_job  : jobname


?jobname    : VARNAME
            | VARNAME"(" params ")"
            | VARNAME"(" params "," max_parallel_count ")"

params      : (param)+

?max_parallel_count: SIGNED_NUMBER

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
    """
    Lark Transformer for Frof syntax.

    You can probably ignore this, unless you're fiddling with the language.
    """

    def __init__(self, *args, **kwargs) -> None:
        self.G = nx.DiGraph()
        self._params = {}
        self._job_param_assignments = {}
        super().__init__(*args, **kwargs)

    def transform(self, tree):
        self._transform_tree(tree)

        # TODO: This still needs some love, but is way better than before.
        # In particular:
        # - [ ] Remove all job creation from the domain of the language. This
        #       should all be the job of the FrofPlan/Executor, not parser.
        # - [ ] Meditate seriously on how to deal with notating parallelism.
        #       This is a bit of a hack currently.

        for (
            jobname,
            (paramname, max_parallel_count),
        ) in self._job_param_assignments.items():
            job = self.G.node[jobname]
            ins = [u for u, v in self.G.in_edges(jobname)]
            outs = [v for u, v in self.G.out_edges(jobname)]

            parallelism_group = str(uuid.uuid4())
            for option in self._params[paramname]:
                job_text = job["job"].cmd.replace("{{&" + paramname + "}}", option)
                self.G.add_node(
                    f"{jobname}_{option}",
                    max_parallel_count=max_parallel_count,
                    parallelism_group=parallelism_group,
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

    def single_job(self, single_job):
        self.G.add_node(str(single_job[0]))

    def jobname(self, job):
        jobname, param_set, max_parallel_count = (None, None, None)
        if len(job) == 2:
            jobname, param_set = job
        elif len(job) == 3:
            jobname, param_set, max_parallel_count = job

        for param in param_set:
            self._job_param_assignments[str(jobname)] = (param, max_parallel_count)
        return jobname

    def params(self, params):
        for param in params:
            if str(param) not in self._params:
                self._params[str(param)] = {}
        return [str(p) for p in params]

    def max_parallel_count(self, max_parallel_count):
        return int(max_parallel_count.value)

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
    """
    A parser for the .frof syntax.

    Contains minimal logic; see FrofTransformer for more details.
    """

    def __init__(self) -> None:
        """
        Create a new Parser.

        Arguments:
            None

        Returns:
            None

        """
        pass

    def parse(self, frof: str) -> nx.DiGraph:
        """
        Parse a .frof syntax tree.

        Arguments:
            frof (str): The contents to parse

        Return:
            nx.DiGraph: The parsed job network

        """
        tree = frof_parser.parse(frof)
        G = FrofTransformer().transform(tree)
        return G
