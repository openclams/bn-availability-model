from Inference.Engine import Engine
import time
import numpy as np
import cpdist

class SimpleSampling(Engine):

    def __init__(self, bn):
        Engine.__init__(self, bn)
        self.is_exact_algorithm = False


    def run(self, solution, *argv):
        start_new_run = time.time()
        try:
            for i in range(self.repetition):
                start = time.time()

                result = cpdist.cpdist(self.bn, solution)

                self.availabilityData.append(result[1]/result[-1])

                self.timeData.append(time.time() - start)

            self.meanAvailability = np.mean(self.availabilityData)

            self.meanTime = np.mean(self.timeData)

            self.is_successful = True

        except Exception as inst:
            print(inst, "Time", time.time() - start_new_run)

