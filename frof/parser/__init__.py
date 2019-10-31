from lark import Lark, Transformer
import networkx as nx

from ..job import BashJob, NullJob

SYNTAX = """
start: line+
line        : COMMENT
            | edgelist
            | definition
            | param_defn

edgelist    : jobname ("->" jobname)+


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
        self.interpolation_enabled = True
        super().__init__(*args, **kwargs)

    def transform(self, tree):
        self._transform_tree(tree)

        # TODO: This needs some serious love. All of this should be happening
        #       in the FrofPlan domain, not in the language domain. Need to
        #       figure out how to manage this correctly.
        for (
            jobname,
            (paramname, max_parallel_count),
        ) in self._job_param_assignments.items():
            job = self.G.node[jobname]
            ins = [u for u, v in self.G.in_edges(jobname)]
            outs = [v for u, v in self.G.out_edges(jobname)]

            # TODO: This is bad and wrong. Pretty much everything below this
            #       line needs to go.
            if max_parallel_count is None:
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
            else:
                # TODO: Very bad. This effectively groups each set of jobs into
                #       batches of size `max_parallel_count` and then schedules
                #       a NullJob() in between them so that each batch has to
                #       finish before the next can begin. (You can picture it
                #       like a fan_out to max_parallel_count and then an
                #       immediate fan-back-in to n=1 at the NullJob sentries.)
                #       This is bad because it prevents other jobs from running
                #       while their peers are still going. i.e. all of jobs
                #       1,2,3,4 must finish running before 5 can start, even if
                #       2 has already finished and there's a spare "slot".
                max_parallel_count = int(max_parallel_count)
                options = self._params[paramname]
                option_groups = [
                    options[m : m + max_parallel_count]
                    for m in range(0, len(options), max_parallel_count)
                ]
                self.G.add_node(f"{jobname}_null_0", job=NullJob())
                for option in option_groups[0]:
                    job_text = job["job"].cmd
                    if self.interpolation_enabled:
                        job_text = job_text.replace("{{&" + paramname + "}}", option)
                    self.G.add_node(
                        f"{jobname}_{option}",
                        job=BashJob(job_text, env={"FROF_JOB_PARAM": option}),
                    )
                    for i in ins:
                        self.G.add_edge(i, f"{jobname}_{option}")
                    self.G.add_edge(f"{jobname}_{option}", f"{jobname}_null_0")

                for i, group in enumerate(option_groups[1:]):
                    checkpoint = NullJob()
                    self.G.add_node(f"{jobname}_null_{i+1}", job=checkpoint)
                    for option in group:
                        job_text = job["job"].cmd
                        if self.interpolation_enabled:
                            job_text = job_text.replace(
                                "{{&" + paramname + "}}", option
                            )
                        self.G.add_node(
                            f"{jobname}_{option}",
                            job=BashJob(job_text, env={"FROF_JOB_PARAM": option}),
                        )
                        self.G.add_edge(f"{jobname}_null_{i}", f"{jobname}_{option}")
                        self.G.add_edge(f"{jobname}_{option}", f"{jobname}_null_{i+1}")
                self.G.add_node(
                    f"{jobname}_null_{len(option_groups) - 1}", job=NullJob()
                )
                for i in outs:
                    self.G.add_edge(f"{jobname}_null_{len(option_groups) - 1}", i)
                self.G.remove_node(jobname)

        return self.G

    def edgelist(self, edgelist):
        self.G.add_path([str(e) for e in edgelist])

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
