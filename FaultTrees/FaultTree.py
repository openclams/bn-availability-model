from FaultTrees.Gate import Gate
from typing import Dict
from collections import deque


class FaultTree:

    def __init__(self):
        self.gates:Dict[str,Gate] = {}
        self.GRAY, self.BLACK = 0, 1

    def add_node(self,name:str):
        gate = Gate(name)
        self.gates[name] = gate
        return gate

    def add_edge(self,gate_from:str,gate_to:str):
        src = self.gates[gate_from]
        dst = self.gates[gate_to]
        dst.add_edge(src)

    def get_node(self,name:str):
        return self.gates[name]

    def topological_sort(self):
        # Generate graph
        graph = {}
        for name, gate in self.gates.items():
            graph[name] = [out.name for out in gate.output_gates]

        # The MIT License (MIT)
        # Copyright (c) 2014 Alexey Kachayev
        # Source: https://gist.github.com/kachayev/5910538
        order, enter, state = deque(), set(graph), {}

        def dfs(node):
            state[node] = self.GRAY
            for k in graph.get(node, ()):
                sk = state.get(k, None)
                if sk == self.GRAY: raise ValueError("cycle")
                if sk == self.BLACK: continue
                enter.discard(k)
                dfs(k)
            order.appendleft(node)
            state[node] = self.BLACK

        while enter: dfs(enter.pop())
        gates =  [self.gates[name] for name in list(order)]
        return gates
