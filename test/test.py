from frof import FrofPlan
from frof.job import BashJob
import networkx as nx

# a = BashJob("ls .")
# b = BashJob("touch b.txt")
# c = BashJob("ls .")

# g = nx.DiGraph()
# g.add_node("a", job=a)
# g.add_node("b", job=b)
# g.add_node("c", job=c)
# g.add_edge("b", "c")

# fp = FrofPlan(network=g)

FROF = """
A -> B -> C
Aa -> B

A: sleep 1
Aa: sleep 2
B: sleep 1
C: sleep 1
"""

fp = FrofPlan(FROF)

fp.run()
