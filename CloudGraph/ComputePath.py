'''A recursive function to print all paths from 'u' to 'd'.
 visited[] keeps track of vertices in current path.
 path[] stores actual vertices and path_index is current
 index in path[]'''
from CloudGraph.Component import Component
from CloudGraph.Graph import Graph
from typing import Dict, List

def compute_all_paths_util(G: Graph,u:str, d:str, visited: Dict[str, bool], path:List[str], paths:List[List[str]]):
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
        adj = G.nodes[u].network_links['children'].union(G.nodes[u].network_links['parents'])
        for i in adj:
            n = i.name
            if visited[n] == False:
                compute_all_paths_util(G,n, d, visited, path, paths)

    path.pop()
    visited[u] = False


def print_all_paths(G:Graph, s:str, d:str):
    # Call the recursive helper function to print all paths
    visited:Dict[str,bool] = {}
    for k in G.nodes.keys():
        visited[k] = False
    path = []
    paths = []
    compute_all_paths_util(G,s, d, visited, path, paths)
    return paths