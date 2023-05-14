from CloudGraph.Component import Component
from CloudGraph.Host import Host
from typing import Dict, Optional

class Graph:

    def __init__(self):
        # nodes should store cloud components index by their names
        self.nodes : Dict[str,Component] = {}

    def add_node(self,node: Component) -> None:
        self.nodes[node.name] = node

    def remove_node(self,node:Component) -> None:
        if node.name in self.nodes:
            del self.nodes[node.name]

    def add_fault_dependency_edge(self, src: str, dst: str, ft={}):
        self.nodes[src].fault_dependencies['children'].append(self.nodes[dst])
        self.nodes[dst].fault_dependencies['parents'].append(self.nodes[src])
        self.nodes[src].ft = ft

    def add_network_edge(self, src: str, dst: str):
        self.nodes[src].network_links['children'].add(self.nodes[dst])
        self.nodes[dst].network_links['parents'].add(self.nodes[src])


