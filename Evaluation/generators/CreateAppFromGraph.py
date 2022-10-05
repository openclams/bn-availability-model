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


class CreateAppFromGraph:

    def __init__(self, n, m,  cim_file_name, fully=False,is_weighted  = False, init="G1"):
        self.n = n
        self.m = m
        self.solution = "A"
        self.k = m
        self.pm = None
        self.ft = None
        self.cim = json.load(open(cim_file_name))

        parser = GraphParser(self.cim)


        votes = np.ones(m)
        k = int(sum(votes) / 2) + 1
        if is_weighted:
            votes = votes + np.random.randint(5, size=m)
            k = int(sum(votes) / 2) + 1
        # The cloud infrastructure graph
        self.G = parser.get_graph()
        # The app graph

        services = [{"name": "s_"+str(i),
                  "init": '',
                  "servers": [],
                  "threshold": k,
                  "direct_communication": False
                } for i in range(n)]

        self.app = {
              "services": services,
              "application": {
                "init": init,
                "topology": [

                ]
              }
            }

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
            for j in range(m):
                host = hosts[(i*m+j)%h]
                if j == 0:
                    self.app["services"][i]["init"] = list(host.network_links['parents'])[0].name
                self.app["services"][i]["servers"].append({"host":host.name,"votes":int(votes[j])})

        if not fully:
            for i in range(n-1):
                self.app['application']["topology"].append( {"from" : "s_"+str(i), "to" : "s_"+str(i+1)})
        else:
            for i in range(n):
                for j in range (i+1,n):
                    self.app['application']["topology"].append({"from": "s_" + str(i), "to": "s_" + str(j)})

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