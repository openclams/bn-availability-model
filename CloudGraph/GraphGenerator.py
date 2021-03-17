import random
import json
from typing import List,Dict, Optional, Tuple
import numpy

class GraphGenerator:

    def __init__(self):
        self.cim = { "components" : [], "network": [], "dependencies" : []}
        self.hosts = []


    def create_cim(self,
                   net_size: int = 10,
                   num_root_nodes :  int = 2,
                   ratio_random_connection:float = 0.0,
                   max_level: int = 2,
                   degree: List[int] = [3],
                   a:float = 1000,
                   b:float = 10):

        fault_dependencies, infrastructure, hosts = self.create_fault_dependency_graph(num_root_nodes, ratio_random_connection, max_level, degree)

        for node in hosts:
            self.cim["components"].append({
              "name": node,
              "availability": numpy.random.beta(a,b),
              "type":'host'
            })
        for node in infrastructure:
            self.cim["components"].append({
                "name": node,
                "availability": numpy.random.beta(a,b),
            })


        for cfc_edge in fault_dependencies:
            self.cim["dependencies"].append({
                "from": cfc_edge[0], "to": [ cfc_edge[1] ]
            })

        network, network_components = self.create_net_graph(net_size)
        for net_edge in network:
            self.cim["network"].append({
                "from": net_edge[0], "to": [net_edge[1]]
            })

        for node in network_components:
            self.cim["dependencies"].append({
                "from": random.choice(infrastructure), "to": [node]
            })
            self.cim["components"].append({
                "name": node,
                "availability": numpy.random.beta(a,b),
            })

        for host in hosts:
            n1 = random.choice(network_components)
            self.cim["network"].append({
                "from": n1, "to": host
            })

        with open('graph.json', 'w') as fp:
            json.dump(self.cim, fp, indent=4)

        self.hosts = hosts
        return self.cim


    def create_subgraph(self,root: str, max_level:int, degree: List[int], level:int =0, leafs:List[str]=[], nodes:List[str]=[]):
        """
        Create a n-ary tree

        :param root: Name of the root node
        :param level: Depth of the graph
        :param max_level: Maximal tree depth
        :param degree: Child nodes per branch
        :return:
        """
        if level < len(degree):
            i = level
        else:
            i = len(degree) - 1
        edges = []
        for d in range(degree[i]):
            n = root + str(d)
            if (level < max_level):
                nodes.append(n)
                edges += self.create_subgraph(n, max_level, degree, level + 1, leafs,nodes)
            else:
                leafs.append(n)
            edges.append((root, n))

        return edges

    def create_fault_dependency_graph(self,
                                      num_root_nodes:int,
                                      ratio_random_connection:float = 0.1,
                                      max_level:int=2,
                                      degree:List[int]=[3]):
        hosts: List[str] = []
        fault_dependencies: List[Tuple[str,str]] = []
        infrastructure: List[str] = []
        # Create for each datacenter root node a new n-ary tree
        for i in range(num_root_nodes):
            domain = "D" + str(i)
            infrastructure.append(domain)
            fault_dependencies += self.create_subgraph(domain, max_level=max_level, degree=degree, leafs=hosts, nodes=infrastructure)

        # Interconnect the trees of the datacenters with random edges
        for i in range(int(len(infrastructure) * ratio_random_connection)):
            n1 = random.choice(infrastructure)
            n2 = random.choice(infrastructure)
            while n1 == n2 or len(n2) >= len(n1) or (n1,n2) in fault_dependencies:
                n2 = random.choice(infrastructure)
            fault_dependencies.append((n1, n2))

        return fault_dependencies, infrastructure ,hosts

    def create_net_graph(self,numNodes):
        network_components:List[str] = []
        network = []
        for i in range(numNodes):
            n = "N" + str(i+1)
            network_components.append(n)

        for i in range(len(network_components)):
            n1 = random.choice(network_components)
            n2 = random.choice(network_components)
            network.append((n1, n2))

        not_set = []
        for node in network_components:
            found = False
            for e in network:
                if  node == e[0] or node == e[1]:
                    found = True
            if not found:
                not_set.append(node)

        for node in not_set:
             n1 = random.choice(network_components)
             network.append((node, n1))
        return  network, network_components

    def create_app(self,n,k):
        app = { "services" : [{ "name": "er", "init" : "N1", "servers":[] , "threshold":k}]}

        for i in range(n):
            app["services"][0]["servers"].append({"host":random.choice(self.hosts),"votes":1})

        with open('deployment.json', 'w') as fp:
            json.dump(app, fp, indent=4)

        return app
