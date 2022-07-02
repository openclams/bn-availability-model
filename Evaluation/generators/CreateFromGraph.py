import BayesianNetworks.pgmpy.operators as op
from pgmpy.models import BayesianModel
from pgmpy.factors.discrete import TabularCPD
import json
from CloudGraph.GraphParser import GraphParser
from AvailabilityModels.BayesianNetPgmpy import BayesianNetModel
from AvailabilityModels.PrismModel import PrismModel
from AvailabilityModels.FaultTreeModel import FaultTreeModel
import numpy as np

from CloudGraph.Host import Host


class CreateFromGraph:

    def __init__(self, n, k,  cim_file_name, is_weighted  = False, init="G1", use_direct_communication_pattern=False):
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
                  "threshold": self.k
                }
              ]
            }

        if use_direct_communication_pattern:
            self.app['services'][0]['communication'] = 'direct'

        hosts = [h for h in self.G.nodes.values() if isinstance(h,Host)]

        h = len(hosts)
        print("Number of hosts: %d"%h)

        net = 0
        for k, v in self.G.nodes.items():
            if len(v.network_links['parents']) != 0 or len(v.network_links['children']) != 0:
                net += 1

        print("Total Network %d"%(net-h))
        print("Total Infrastructure %d" % (len(self.G.nodes.keys())-net))

        for i in range(n):
            self.app["services"][0]["servers"].append({"host":hosts[i%h].name,"votes":int(votes[i])})


    def createNaiveNetwork(self):
        ba = BayesianNetModel(self.G, self.app)
        bn = ba.bn
        return bn


    def createScalableNetwork(self):
        ba = BayesianNetModel(self.G, self.app,
                              andNodeCPT=op.efficient_and_node,
                              orNodeCPT=op.efficient_or_node,
                              knNodeCPT=op.scalable_kn_node,
                              weightedKnNodeCPT=op.scalable_weighted_kn_node)
        bn = ba.bn
        return bn

    def createPrism(self):
        self.pm = PrismModel(self.G, self.app, "cim.sm")
        self.pm.build()

    def createFaultTree(self):
        self.ft = FaultTreeModel(self.G, self.app)
        self.ft.build()
        self.ft.writeXML()