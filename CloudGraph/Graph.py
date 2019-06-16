from CloudGraph.NetworkEdge import NetworkEdge
from CloudGraph.Node import Node
from collections import defaultdict

class Graph:

    def __init__(self):
        self.V = {}
        self.groups = {} #key are group_names and vaules array of node objects

    def add_node(self,node,group_name = None):
        self.V[node.name] = node
        if group_name:
            self.add_node_to_group(node,group_name)

    def add_node_to_group(self,node,group_name):
        node.host_group_name = group_name

        if group_name in self.groups.keys():
            self.groups[group_name].append(node)
        else:
            self.groups[group_name] = [node]

        # store locally at each node all its neighbor nodes of his group
        for n in self.groups[group_name]:
            if not n == node:
                n.host_group.append(node)
                node.host_group.append(n)

    def remove_node(self,name):
        if name in self.V.keys():
            del self.V[name]

    def add_edge(self,edge):
        src = edge.get_src()
        dst = edge.get_dst()
        if isinstance(edge,NetworkEdge):
            self.V[src].net['children'].add(self.V[dst])
            self.V[dst].net['parents'].add(self.V[src])
        else:
            self.V[src].cfc['children'].append(self.V[dst])
            self.V[dst].cfc['parents'].append(self.V[src])

        edge.set_src_node(self.V[src])
        edge.set_dst_node(self.V[dst])

    '''A recursive function to print all paths from 'u' to 'd'. 
    visited[] keeps track of vertices in current path. 
    path[] stores actual vertices and path_index is current 
    index in path[]'''
    def print_all_paths_util(self, u, d, visited, path,paths):

        # Mark the current node as visited and store in path
        visited[u] = True
        path.append(u)

        # If current vertex is same as destination, then print
        # current path[]
        if u == d:
            paths.append(path.copy())
        else:
            # If current vertex is not destination
            # Recur for all the vertices adjacent to this vertex
            adj = self.V[u].net['children'].union(self.V[u].net['parents'])
            for i in adj:
                n = i.name
                if visited[n] == False:
                    self.print_all_paths_util(n, d, visited, path,paths)

        path.pop()
        visited[u] = False


    def print_all_paths(self, s, d):
        # Call the recursive helper function to print all paths
        visited = {}
        for k in self.V.keys():
            visited[k] = False
        path = []
        paths = []
        self.print_all_paths_util(s, d, visited, path, paths)
        return paths