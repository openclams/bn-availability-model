from Inference.Engine import Engine
import pgmpy.inference as infer
import time
import numpy



class VariableElimination(Engine):

    def __init__(self, bn):
        Engine.__init__(self, bn)

    def run(self,solution,*argv):
        start_new_run = time.time()
        try:
            for i in range(self.repetition):
                start = time.time()
                ies = infer.VariableElimination(self.bn)

                self.availabilityData.append(ies.query(variables=[solution], evidence={})[solution].values[1])
                self.timeData.append(time.time() - start)

            self.meanAvailability = numpy.mean(self.availabilityData)
            self.meanTime = numpy.mean(self.timeData)
            self.is_successful = True

        except Exception as inst:
            print(inst, "Time", time.time() - start_new_run)