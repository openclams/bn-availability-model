from CloudGraph.Node import Node

class Edge:

    def __init__(self,src,dst):
        self.src = src
        self.dst = dst
        self.src_node = None
        self.dst_node = None

    def get_src(self):
        return self.src

    def get_dst(self):
        return self.dst

    def get_src_node(self):
        return self.src_node

    def get_dst_node(self):
        return self.dst_node

    def set_src_node(self,node):
        self.src_node = node

    def set_dst_node(self,node):
        self.dst_node = node


