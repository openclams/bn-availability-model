import BayesianNetworks.pgmpy.operators as op
from pgmpy.models import BayesianModel
from pgmpy.factors.discrete import TabularCPD
from Evaluation.generators.Generator import Generator
from BayesianNetworks.pgmpy import writers as bnwriters


class SimpleExample(Generator):

    def __init__(self, n, k):
        self.n = n
        self.k = k
        self.solution = "K"

    def createBasicNetwork(self):
        bn = BayesianModel()
        bn.add_node("K", 2)

        for i in range(self.n):
            node_name = "C_" + str(i)
            bn.add_node(node_name, 2)
            bn.add_edge(node_name, "K")

            cpd = TabularCPD(variable=node_name, variable_card=2, values=[[0.2, 0.8]],
                             evidence=[],
                             evidence_card=[])
            bn.add_cpds(cpd)
        return bn

    def createNaiveNetwork(self,write=False):
        try:
            bn = self.createBasicNetwork()

            op.kn_node(bn, "K", self.k)
        except Exception as inst:
            bn = BayesianModel()

        if write:
            bnwriters.writeR(bn, "bnlearn_tmp_R_naive")

        return bn

    def createScalableNetwork(self,write=False):

        try:
            bn = self.createBasicNetwork()

            op.scalable_kn_node(bn, "K", self.k)
        except Exception as inst:
            bn = BayesianModel()

        if write:
            bnwriters.writeR(bn, "bnlearn_tmp_R")

        return bn


class CreateFromGraph:
    pass