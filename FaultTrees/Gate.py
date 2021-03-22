class Gate:

    def __init__(self,name):
        self.name = name
        self.type = ""
        self.k = 0
        self.n = 0
        self.prob = 0
        self.input_gates = []
        self.output_gates = []

    def add_edge(self,gate):
        if len([g for g in self.input_gates if g.name == gate.name]) > 0:
            raise Exception('Duplicate entry')
        self.input_gates.append(gate)
        gate.output_gates.append(self)

