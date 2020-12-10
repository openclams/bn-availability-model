from FaultTrees.FaultTree import FaultTree

class MefWriter:

    def __init__(self, fault_tree:FaultTree,
                 temp_file_name: str = "ft_mef.xml"):
        self.ft: FaultTree= fault_tree
        self.model_name: str = temp_file_name
        self.f = open(self.model_name, "w+")

        self.f.write("<!DOCTYPE opsa-mef>\n")
        self.f.write("<opsa-mef>\n")
        self.f.write("\t<define-fault-tree name=\"ft\">\n")
        self.createFT()
        self.f.write("\t</define-fault-tree>\n")
        self.f.write("\t<model-data>\n")
        self.createBE()
        self.f.write("\t</model-data>\n")
        self.f.write("</opsa-mef>")
        self.f.close()

    def createFT(self):
        gates = self.ft.gates
        for gate in gates.values() :
            if gate.type == "top":
                self.TOP(gate)
            elif gate.type == "or":
                self.OR(gate)
            elif gate.type == "and":
                self.AND(gate)
            elif gate.type == "vote":
                self.VOTING(gate)

    def createBE(self):
        gates = self.ft.gates
        for gate in gates.values():
            if gate.type == "base":
                self.BASE(gate)


    def GATE(self,gate,type,arg=""):
        self.f.write("\t\t<define-gate name=\"{}\">\n".format(gate.name))

        if len(gate.input_gates) > 1:
            self.f.write("\t\t\t<{} {}>\n".format(type,arg))

        for inp in gate.input_gates:
            if inp.type == "base":
                self.f.write("\t\t\t\t<basic-event name=\"{}\"/>\n".format(inp.name))
            else:
                self.f.write("\t\t\t\t<gate name=\"{}\"/>\n".format(inp.name))

        if len(gate.input_gates) > 1:
            self.f.write("\t\t\t</{}>\n".format(type))
        self.f.write("\t\t</define-gate>\n")

    def TOP(self, gate):
        self.f.write("\t\t<define-gate name=\"top\">\n")
        self.f.write("\t\t\t<gate name=\"{}\"/>\n".format(gate.name))
        self.f.write("\t\t</define-gate>\n")
        self.OR(gate)

    def OR(self, gate):
        self.GATE(gate,'or')

    def AND(self, gate):
        self.GATE(gate,'and')

    def BASE(self, gate):
        self.f.write("\t\t<define-basic-event name=\"{}\">\n".format(gate.name))
        self.f.write("\t\t\t<float value=\"{:1.8f}\"/>\n".format(gate.prob))
        self.f.write("\t\t</define-basic-event>\n")

    def VOTING(self, gate):
        if gate.k == len(gate.input_gates):
            self.AND(gate)
        elif gate.k == 1:
            self.OR(gate)
        else:
            self.GATE(gate, 'atleast',"min=\"{}\"".format(gate.k))

