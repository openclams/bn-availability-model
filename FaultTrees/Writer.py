from FaultTrees.FaultTree import FaultTree
from typing import List, Set, Dict
from collections import deque

class Writer:

    def __init__(self, fault_tree:FaultTree,
                 temp_file_name: str = "ft.R"):
        self.ft: FaultTree= fault_tree
        self.model_name: str = temp_file_name
        self.f = open(self.model_name, "w+")

        gates = list(reversed(self.ft.topological_sort()))
        self.gate_counter = 0
        self.gateIdx: Dict[str, int] = {}

        self.dup_graph = {}
        self.build = []
        self.GRAY, self.BLACK = 0, 1

        # Write FT
        for idx, gate in enumerate(gates):
            if gate.type == "top":
                self.TOP("TE")
                continue

            at = self.gateIdx[gate.output_gates[0].name]
            if gate.type == "or":
                self.OR(at,gate.name)
            elif gate.type == "and":
                self.AND(at,gate.name)
            elif gate.type == "vote":
                self.VOTING(at,gate.name,gate.k,gate.n)
            elif gate.type == "base":
                self.BASE(at,gate.name,gate.prob)

            if len(gate.output_gates) > 1:
                for i in range(1, len(gate.output_gates)):
                    at = self.gateIdx[gate.output_gates[i].name]
                    dup_id = self.gateIdx[gate.name]
                    if dup_id in self.dup_graph:
                        self.dup_graph[dup_id].append(at)
                    else:
                        self.dup_graph[dup_id] = [at]

                    #self.DUP(at, dup_id)

                self.build.append(dup_id)

        order = reversed(self.build)
        for dup_id in list(order):
            if dup_id in self.dup_graph:
                for at in self.dup_graph[dup_id]:
                    self.DUP(at,dup_id)

        # for idx, gate in enumerate(gates):
        #     if gate.type == "top":
        #         continue
        #     if len(gate.output_gates) > 1:
        #         for i in range(1,len(gate.output_gates)):
        #             at =  self.gateIdx[gate.output_gates[i].name]
        #             dup_id =  self.gateIdx[gate.name]
        #             self.DUP(at, dup_id)
        #             continue
        #             if dup_id in self.dup_graph:
        #                 self.dup_graph[dup_id].append(at)
        #             else:
        #                 self.dup_graph[dup_id] = [at]

        # for idx, gate in enumerate(gates):
        #     if gate.type == "top":
        #         continue
        #     if len(gate.output_gates) > 1:
        #         for i in range(1,len(gate.output_gates)):
        #             at =  self.gateIdx[gate.output_gates[i].name]
        #             dup_id =  self.gateIdx[gate.name]
        #             self.DUP(at, dup_id)
        #             continue
        #             if dup_id in self.dup_graph:
        #                 self.dup_graph[dup_id].append(at)
        #             else:
        #                 self.dup_graph[dup_id] = [at]

        # print(self.dup_graph)
        # order = self.topological_sort(self.dup_graph)
        # print(order)
        # for dup_id in list(order):
        #     if dup_id in self.dup_graph:
        #         for at in self.dup_graph[dup_id]:
        #             self.DUP(at,dup_id)

        self.f.close()

    def TOP(self, name):
        self.gate_counter += 1
        self.gateIdx[name] = self.gate_counter
        self.f.write("ft <- ftree.make(type=\"or\", name=\"{}\")\n".format(name))
        return self.gate_counter

    def OR(self, at, name="", name2=""):
        self.gate_counter += 1
        self.gateIdx[name] = self.gate_counter
        self.f.write("ft <- addLogic(ft, at={}, type=\"or\", name=\"{}\", name2=\"{}\")\n".format(at, name, name2))
        return self.gate_counter

    def AND(self, at, name="", name2=""):
        self.gate_counter += 1
        self.gateIdx[name] = self.gate_counter
        self.f.write("ft <- addLogic(ft, at={}, type=\"and\", name=\"{}\", name2=\"{}\")\n".format(at, name, name2))
        return self.gate_counter

    def BASE(self, at, name="", prob=0, name2="[Component]"):
        self.gate_counter += 1
        self.gateIdx[name] = self.gate_counter
        self.f.write("ft <- addProbability(ft, at={}, prob={}, name=\"{}\", name2=\"{}\")\n".format(at, prob, name, name2))
        return self.gate_counter

    def VOTING(self, at, name="", k=0, n=0, name2=""):
        self.gate_counter += 1
        self.gateIdx[name] = self.gate_counter
        self.f.write("ft <- addAtLeast(ft, at={}, atleast={}, name=\"{}\", name2=\"{}\")\n".format(at, k,name,name2))
        return self.gate_counter

    def DUP(self,at,dup_id):
        self.gate_counter += 1
        self.f.write("ft <-  addDuplicate(ft, at={}, dup_id={})\n".format(at,dup_id))
        return self.gate_counter

    def topological_sort(self,graph):
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
        return order