from CloudGraph.Graph import Graph


class FaultTreeModel:

    def __init__(self,
                 G:Graph,
                 app,
                 temp_file_name: str = "ft.R",
                 ):
        self.G: Graph = G
        self.app = app
        self.model_name: str = temp_file_name
        self.f = open(self.model_name, "w+")
        self.paths = {}

    def build(self):
        self.f.write('ft <- ftree.make(type="priority",reversible_cond=TRUE, name="Site power loss")\n\n')
        for service in self.app["services"]:
            pass 
