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

    def create_component(self, name:str, component):
        availability = component['availability']
        if "type" in component.keys():
            self.G.add_node(Host(name,availability))
        else:
            self.G.add_node(Component(name,availability))

    def load_nodes(self,cloud_infrastructure_model):
        for component in cloud_infrastructure_model["components"]:

            if isinstance(component["name"],str):
                # The name field is a string
                self.create_component(component['name'], component)
            else:
                for element in component["name"]:
                    # The name field is an array
                    self.create_component(element, component)

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
            ft = {}
            if 'ft' in edges:
                ft = edges["ft"]
            if isinstance(edges["to"],str):
                self.G.add_fault_dependency_edge(edges["from"],edges["to"],ft)
            else:
                for e in edges["to"]:
                    # The name field is an array
                    self.G.add_fault_dependency_edge(edges["from"],e,ft)