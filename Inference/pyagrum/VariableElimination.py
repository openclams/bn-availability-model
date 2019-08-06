from Inference.Engine import Engine
import pyAgrum as gum
import time
import numpy

class GumVariableElimination(Engine):

    def __init__(self, bn):
        Engine.__init__(self, bn)

    def run(self,solution,*argv):
        start_new_run = time.time()
        try:
            start = time.time()
            ies = gum.VariableElimination(self.bn)
            ies.setEvidence({})
            ies.makeInference()

            self.availabilityData.append(ies.posterior(solution)[1])
            self.timeData.append(time.time() - start)

            self.meanAvailability = numpy.mean(self.availabilityData)
            self.meanTime = numpy.mean(self.timeData)
            self.is_successful = True

        except Exception as inst:
            print(inst, "Time", time.time() - start_new_run)