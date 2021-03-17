import BayesianNetworks.pgmpy.operators as op
from pgmpy.models import BayesianModel
from pgmpy.factors.discrete import TabularCPD
from Evaluation.generators.Generator import Generator
from BayesianNetworks.pgmpy import writers as bnwriters

class SerialExample(Generator):
    def __init__(self, n, k):
        self.n = n
        self.k = k
        self.solution = "SYS"

    def createBasicNetwork(self):
        bn = BayesianModel()
        bn.add_node("K", 2)

        for i in range(3):
            node_name = "C_" + str(i)
            bn.add_node(node_name, 2)
            bn.add_edge(node_name, "K")

            cpd = TabularCPD(variable=node_name, variable_card=2, values=[[0.2, 0.8]],
                             evidence=[],
                             evidence_card=[])
            bn.add_cpds(cpd)

        node_name = "AND_1"
        bn.add_node(node_name, 2)

        for i in range(3, self.n + 3):
            node_name = "C_" + str(i)
            bn.add_node(node_name, 2)
            bn.add_edge(node_name, "AND_1")

            cpd = TabularCPD(variable=node_name, variable_card=2, values=[[0.01, 0.99]],
                             evidence=[],
                             evidence_card=[])
            bn.add_cpds(cpd)

        node_name = "AND_2"
        bn.add_node(node_name, 2)

        for i in range(self.n + 3, self.n + 5):
            node_name = "C_" + str(i)
            bn.add_node(node_name, 2)
            bn.add_edge(node_name, "AND_2")

            cpd = TabularCPD(variable=node_name, variable_card=2, values=[[0.01, 0.99]],
                             evidence=[],
                             evidence_card=[])
            bn.add_cpds(cpd)

        node_name = "OR"
        bn.add_node(node_name, 2)
        bn.add_edge("AND_1", node_name)
        bn.add_edge("K", node_name)

        node_name = "SYS"
        bn.add_node(node_name, 2)
        bn.add_edge("OR", node_name)
        bn.add_edge("AND_2", node_name)

        return bn

    def createNaiveNetwork(self,write=True):
        try:
            bn = self.createBasicNetwork()

            op.kn_node(bn, "K", self.k)
            op.and_node(bn, "AND_1")
            op.and_node(bn, 'AND_2')
            op.or_node(bn, "OR")
            op.and_node(bn, 'SYS')
        except Exception as inst:
            bn = BayesianModel()
        if write:
            bnwriters.writeR(bn, "bnlearn_tmp_R_naive")
        return bn

    def createScalableNetwork(self,write=True):
        try:
            bn = self.createBasicNetwork()

            op.kn_node(bn, "K", self.k)
            op.efficient_and_node(bn, "AND_1")
            op.and_node(bn, 'AND_2')
            op.or_node(bn, "OR")
            op.and_node(bn, 'SYS')

        except Exception as inst:
            bn = BayesianModel()
        if write:
            bnwriters.writeR(bn,"bnlearn_tmp_R")
        return bn

