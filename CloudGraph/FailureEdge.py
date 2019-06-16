from CloudGraph.Edge import Edge


class FailureEdge(Edge):

    def __init__(self, from_node, to_node):
        Edge.__init__(self, from_node, to_node)