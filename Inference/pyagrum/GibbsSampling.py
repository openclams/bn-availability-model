from Inference.Engine import Engine
import pyAgrum as gum
import time
import numpy

class GumGibbisSampling(Engine):

    def __init__(self, bn):
        Engine.__init__(self, bn)
        self.is_exact_algorithm = False

    def run(self,solution,*argv):
        start_new_run = time.time()
        try:
            for i in range(self.repetition):
                start = time.time()
                ies = gum.GibbsSampling(self.bn)
                ies.setBurnIn(600)
                ies.setDrawnAtRandom(False)
                ies.setEpsilon(argv[0]["epsilon"])
                ies.setMinEpsilonRate(argv[0]["epsilonRate"])
                ies.setPeriodSize(300)
                ies.setMaxTime(argv[0]["maxTime"])
                ies.setEvidence({})
                ies.makeInference()

                self.availabilityData.append(ies.posterior(solution)[1])
                self.timeData.append(time.time() - start)

            self.meanAvailability = numpy.mean(self.availabilityData)
            self.meanTime = numpy.mean(self.timeData)
            self.is_successful = True

        except Exception as inst:
            print(inst, "Time", time.time() - start_new_run)