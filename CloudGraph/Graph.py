from CloudGraph.Component import Component
from CloudGraph.HostGroup import HostGroup
from CloudGraph.Host import Host
from typing import Dict, Optional

class Graph:

    def __init__(self):
        # nodes should store cloud components index by their names
        self.nodes : Dict[str,Component] = {}
        # key are host group names are the host groups
        self.host_groups: Dict[str,HostGroup] = {}

    def add_node(self,node: Component, group_name : Optional[str]  = None) -> None:
        self.nodes[node.name] = node
        if group_name:
            self.add_node_to_group(node,group_name)


    def add_node_to_group(self,host: Host, group_name:str) -> None:
        if group_name not in self.host_groups:
            self.host_groups[group_name] = HostGroup(group_name)

        #Attach the host to the host group
        self.host_groups[group_name].hosts.add(host)
        host.host_groups.add(self.host_groups[group_name])

    def remove_node(self,node:Component) -> None:
        if node.name in self.nodes:
            del self.nodes[node.name]

    def add_fault_dependency_edge(self,src:str, dst:str):
        self.nodes[src].fault_dependencies['children'].append(self.nodes[dst])
        self.nodes[dst].fault_dependencies['parents'].append(self.nodes[src])

    def add_network_edge(self, src: str, dst: str):
        self.nodes[src].network_links['children'].add(self.nodes[dst])
        self.nodes[dst].network_links['parents'].add(self.nodes[src])


