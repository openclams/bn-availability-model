import BayesianNetworks.pgmpy.operators as op
from pgmpy.models import BayesianModel
from pgmpy.factors.discrete import TabularCPD
import json
from CloudGraph.GraphParser import GraphParser
from AvailabilityModels.BayesianNetPgmpy import BayesianNetModel
from AvailabilityModels.PrismModel import PrismModel
from AvailabilityModels.FaultTreeModel import FaultTreeModel
import numpy as np

class PrismComparisonExample:

    def __init__(self, n, k,  cim_file_name, is_weighted  = False, init="G1"):
        self.n = n
        self.k = k
        self.solution = "er"
        self.pm = None
        self.ft = None
        self.cim = json.load(open(cim_file_name))

        parser = GraphParser(self.cim)


        votes = np.ones(n)
        if is_weighted:
            votes = votes + np.random.randint(5, size=n)
            self.k = int(sum(votes) / 2) + 1
        # The cloud infrastructure graph
        self.G = parser.get_graph()
        # The app graph
        self.app = {
              "services":[
                {
                  "name": "er",
                  "init": init,
                  "servers": [],
                  "threshold": self.k,
                  "direct_communication": False
                }
              ]
            }
        hosts = []
        for v in self.G.host_groups.values():
            hosts.extend(v.hosts)

        h = len(hosts)
        print("Number of hosts: %d"%h)
        print("Total Infrastructure %d"%len(self.G.nodes.keys()))

        net = 0
        for k, v in self.G.nodes.items():
            if len(v.network_links['parents']) != 0 or len(v.network_links['children']) != 0:
                net += 1

        print("Total Network %d"%net)
        for i in range(n):
            self.app["services"][0]["servers"].append({"host":hosts[i%h].name,"votes":int(votes[i])})


    def createNaiveNetwork(self):
        ba = BayesianNetModel(self.G, self.app)
        bn = ba.bn
        return bn


    def createScalableNetwork(self):
        ba = BayesianNetModel(self.G, self.app,andNodeCPT=op.efficient_and_node,orNodeCPT=op.efficient_or_node,knNodeCPT=op.scalable_kn_node,weightedKnNodeCPT=op.scalable_weighted_kn_node)
        bn = ba.bn
        return bn

    def createPrism(self):
        self.pm = PrismModel(self.G, self.app, "cim.sm")
        self.pm.build()

    def createFaultTree(self):
        self.ft = FaultTreeModel(self.G, self.app, "ft.R")
        self.ft.build()
        self.ft.writeXML()


class SimpleExample:

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

    def createNaiveNetwork(self):
        try:
            bn = self.createBasicNetwork()

            op.kn_node(bn, "K", self.k)
        except Exception as inst:
            bn =  BayesianModel()
        return bn

    def createScalableNetwork(self):
        try:
            bn = self.createBasicNetwork()

            op.scalable_kn_node(bn, "K", self.k)
        except Exception as inst:
            bn = BayesianModel()
        return bn

class ParallelExample:
    def __init__(self, n, k):
        self.n = n
        self.k = k
        self.solution = "SYS"

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

        node_name = "AND_1"
        bn.add_node(node_name, 2)

        for i in range(self.n,self.n+3):
            node_name = "C_" + str(i)
            bn.add_node(node_name, 2)
            bn.add_edge(node_name, "AND_1")

            cpd = TabularCPD(variable=node_name, variable_card=2, values=[[0.01, 0.99]],
                             evidence=[],
                             evidence_card=[])
            bn.add_cpds(cpd)

        node_name = "AND_2"
        bn.add_node(node_name, 2)

        for i in range(self.n+3, self.n + 5):
            node_name = "C_" + str(i)
            bn.add_node(node_name, 2)
            bn.add_edge(node_name, "AND_2")

            cpd = TabularCPD(variable=node_name, variable_card=2, values=[[0.01, 0.99]],
                             evidence=[],
                             evidence_card=[])
            bn.add_cpds(cpd)

        node_name = "OR"
        bn.add_node(node_name, 2)
        bn.add_edge( "AND_1", node_name)
        bn.add_edge( "K", node_name)

        node_name = "SYS"
        bn.add_node(node_name, 2)
        bn.add_edge("OR", node_name)
        bn.add_edge("AND_2", node_name)

        return bn

    def createNaiveNetwork(self):
        try:
            bn = self.createBasicNetwork()

            op.kn_node(bn, "K", self.k)
            op.and_node(bn, "AND_1")
            op.and_node(bn, 'AND_2')
            op.or_node(bn, "OR")
            op.and_node(bn, 'SYS')
        except Exception as inst:
            bn = BayesianModel()

        return bn

    def createScalableNetwork(self):
        try:
            bn = self.createBasicNetwork()

            op.scalable_kn_node(bn, "K", self.k)
            op.and_node(bn, "AND_1")
            op.and_node(bn, 'AND_2')
            op.or_node(bn, "OR")
            op.and_node(bn, 'SYS')
        except Exception as inst:
            bn = BayesianModel()
        return bn

class SerialExample:
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

        for i in range(3,self.n+3):
            node_name = "C_" + str(i)
            bn.add_node(node_name, 2)
            bn.add_edge(node_name, "AND_1")

            cpd = TabularCPD(variable=node_name, variable_card=2, values=[[0.01, 0.99]],
                             evidence=[],
                             evidence_card=[])
            bn.add_cpds(cpd)

        node_name = "AND_2"
        bn.add_node(node_name, 2)

        for i in range(self.n+3, self.n + 5):
            node_name = "C_" + str(i)
            bn.add_node(node_name, 2)
            bn.add_edge(node_name, "AND_2")

            cpd = TabularCPD(variable=node_name, variable_card=2, values=[[0.01, 0.99]],
                             evidence=[],
                             evidence_card=[])
            bn.add_cpds(cpd)

        node_name = "OR"
        bn.add_node(node_name, 2)
        bn.add_edge( "AND_1", node_name)
        bn.add_edge( "K", node_name)

        node_name = "SYS"
        bn.add_node(node_name, 2)
        bn.add_edge("OR", node_name)
        bn.add_edge("AND_2", node_name)

        return bn

    def createNaiveNetwork(self):
        try:
            bn = self.createBasicNetwork()

            op.kn_node(bn, "K", self.k)
            op.and_node(bn, "AND_1")
            op.and_node(bn, 'AND_2')
            op.or_node(bn, "OR")
            op.and_node(bn, 'SYS')
        except Exception as inst:
            bn = BayesianModel()
        return bn

    # def createScalableNetwork(self):
    #
    #         op.kn_node(bn, "K", self.k)
    #         op.efficient_and_node(bn, "AND_1")
    #         op.and_node(bn, 'AND_2')
    #         op.or_node(bn, "OR")
    #         op.and_node(bn, 'SYS')
    #
    #     except Exception as inst:
    #         bn = BayesianModel()
    #
    #     return bn

