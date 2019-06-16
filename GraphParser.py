from CloudGraph.Graph       import    Graph
from CloudGraph.Node        import    Node
from CloudGraph.NetworkEdge import    NetworkEdge
from CloudGraph.FailureEdge import    FailureEdge
import json

class GraphParser():

    def __init__(self,file_name):
        self.file_name = file_name
        self.G = Graph()
        self.parse()

    def parse(self):
        with open(self.file_name) as json_file:
            data = json.load(json_file)
            self.load_nodes(data)
            self.load_network_edges(data)
            self.load_dependency_edges(data)

    def get_graph(self):
        return self.G

    def load_nodes(self,data):
        for nodes in data["nodes"]:
            if isinstance(nodes["name"],str):
                # The name field is a string
                node = Node(nodes['name'],nodes['availability'])
                self.G.add_node(node)
                if "group" in nodes.keys():
                    self.G.add_node_to_group(node,nodes["group"])
            else:
                for n in nodes["name"]:
                    # The name field is an array
                    node = Node(n,nodes["availability"])
                    self.G.add_node(node)
                    if "group" in nodes.keys():
                        self.G.add_node_to_group(node, nodes["group"])

    def load_network_edges(self,data):
        for edges in data["network"]:
            if isinstance(edges["to"],str):
                edge = NetworkEdge(edges["from"],edges["to"])
                self.G.add_edge(edge)
            else:
                for e in edges["to"]:
                    # The name field is an array
                    edge = NetworkEdge(edges["from"],e)
                    self.G.add_edge(edge)

    def load_dependency_edges(self, data):
        for edges in data["dependencies"]:
            if isinstance(edges["to"],str):
                edge = FailureEdge(edges["from"],edges["to"])
                self.G.add_edge(edge)
            else:
                for e in edges["to"]:
                    # The name field is an array
                    edge = FailureEdge(edges["from"],e)
                    self.G.add_edge(edge)