import random
import json
class GraphGenerator:


    def __init__(self):
        self.cim = { "nodes" : [], "network": [], "dependencies" : []}
        self.hosts = []


    def create_cim(self, net_size=10,numRootNodes=2, ratio_random_connection=0.0, max_level=2, degree=[3],min_availability=0.9990, max_availability=0.99999):

        network, nodes, leafs = self.create_cfc_graph(numRootNodes, ratio_random_connection, max_level, degree)

        hosts = []
        groups = {}
        inv_groups = {}
        for t in leafs:
            if not t[0] in groups:
                groups[t[0]] = []
                groups[t[0]].append(t[1])
            else:
                groups[t[0]].append(t[1])
            inv_groups[t[1]] = t[0]
            hosts.append(t[1])

        for node in nodes:
            if node in hosts:
                self.cim["nodes"].append({
                  "name": node,
                  "availability": random.uniform(min_availability, max_availability),
                  "group": inv_groups[node]
                })
            else:
                self.cim["nodes"].append({
                    "name": node,
                    "availability": random.uniform(min_availability, max_availability),
                })

        for cfc_edge in network:
            self.cim["dependencies"].append({
                "from": cfc_edge[0], "to": [ cfc_edge[1] ]
            })

        network, nodes = self.create_net_graph(net_size)
        for net_edge in network:
            self.cim["network"].append({
                "from": net_edge[0], "to": [net_edge[1]]
            })

        for node in nodes:
            self.cim["nodes"].append({
                "name": node,
                "availability": random.uniform(min_availability, max_availability),
            })

        for group in groups:
            n1 = random.choice(nodes)
            self.cim["network"].append({
                "from": n1, "to": groups[group]
            })

        with open('result.json', 'w') as fp:
            json.dump(self.cim, fp, indent=4)

        self.hosts = hosts
        return self.cim


    def create_subgraph(self,root, max_level, degree, level=0, leafs=[], nodes=[]):
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
            n = root + "" + str(d)
            nodes.append(n)
            edges.append((root, n))
            if (level < max_level):
                edges += self.create_subgraph(n, max_level, degree, level + 1, leafs,nodes)
            else:
                leafs.append((root,n))

        return edges

    def create_cfc_graph(self,numRootNodes, ratio_random_connection=0.1, max_level=2, degree=[3]):
        leafs = []
        network = []
        nodes = []
        # Create for each datacenter root node a new n-ary tree
        for i in range(numRootNodes):
            domain = "D" + str(i)
            nodes.append(domain)
            network += self.create_subgraph(domain, max_level=max_level, degree=degree, leafs=leafs, nodes=nodes)

        # Interconnect the trees of the datacenters with random edges
        for i in range(int(len(network) * ratio_random_connection)):
            n1 = random.choice(network)[0]
            n2 = random.choice(network)[1]
            while n1 == n2 and len(n2) >= len(n1) and not (n1,n2) in network:
                n2 = random.choice(network)[1]
            network.append((n1, n2))

        #model.add_edges_from(network)

        return network, nodes ,leafs

    def create_net_graph(self,numNodes):
        nodes = []
        network = []
        for i in range(numNodes):
            n = "N" + str(i+1)
            nodes.append(n)

        for i in range(len(nodes)):
            n1 = random.choice(nodes)
            n2 = random.choice(nodes)
            network.append((n1, n2))

        not_set = []
        for node in nodes:
            found = False
            for e in network:
                if  node == e[0] or node == e[1]:
                    found = True
            if not found:
                not_set.append(node)

        for node in not_set:
             n1 = random.choice(nodes)
             network.append((node, n1))
        return  network, nodes

    def create_app(self,n,k):
        app = { "services" : [{ "name": "er", "init" : "N1", "servers":[] , "k":k}]}

        for i in range(n):
            app["services"][0]["servers"].append(random.choice(self.hosts))

        with open('deployment_dev.json', 'w') as fp:
            json.dump(app, fp, indent=4)

        return app
