from CloudGraph.Graph import Graph
from CloudGraph.Component import Component
from CloudGraph.Host import Host
from typing import  Optional

class GraphParser():

    def __init__(self,cloud_infrastructure_model : any):
        self.G = Graph()
        self.load_nodes(cloud_infrastructure_model)
        self.load_network_edges(cloud_infrastructure_model)
        self.load_fault_dependency_edges(cloud_infrastructure_model)

    def get_graph(self) -> Graph:
        return self.G

    def create_component(self, name:str, availability:float, group_name : Optional[str] = None):
        if group_name:
            host = Host(name,availability)
            self.G.add_node(host)
            self.G.add_node_to_group(host, group_name)
        else:
            self.G.add_node(Component(name,availability))

    def load_nodes(self,cloud_infrastructure_model):
        for component in cloud_infrastructure_model["components"]:

            group_name = None
            if "group" in component.keys():
                group_name = component["group"]

            if isinstance(component["name"],str):
                # The name field is a string
                self.create_component(component['name'], component['availability'],group_name)
            else:
                for element in component["name"]:
                    # The name field is an array
                    self.create_component(element, component['availability'], group_name)

    def load_network_edges(self,data):
        for edges in data["network"]:
            if isinstance(edges["to"],str):
                self.G.add_network_edge(edges["from"],edges["to"])
            else:
                for e in edges["to"]:
                    # The name field is an array
                    self.G.add_network_edge(edges["from"],e)

    def load_fault_dependency_edges(self, data):
        for edges in data["dependencies"]:
            if isinstance(edges["to"],str):
                self.G.add_fault_dependency_edge(edges["from"],edges["to"])
            else:
                for e in edges["to"]:
                    # The name field is an array
                    self.G.add_fault_dependency_edge(edges["from"],e)