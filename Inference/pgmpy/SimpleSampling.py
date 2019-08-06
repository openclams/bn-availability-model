from Inference.Engine import Engine
import time
import numpy as np
from pgmpy.sampling import BayesianModelSampling

class SimpleSampling(Engine):

    def __init__(self, bn):
        Engine.__init__(self, bn)
        self.is_exact_algorithm = False


    def run(self, solution, *argv):
        N = argv[0]["sample_size"]
        start_new_run = time.time()
        try:
            for i in range(self.repetition):
                print("Round",i)
                start = time.time()
                inference = BayesianModelSampling(self.bn)

                start = time.time()
                samples = inference.forward_sample(size=N, return_type='recarray')
                s = samples[solution]

                #print (sum(very_low_cause_values[, 1] * attr(very_low_cause_values, "weights")) / sum(attr(very_low_cause_values, "weights")))

                self.availabilityData.append(sum(s)/N)
                self.timeData.append(time.time() - start)

            self.meanAvailability = np.mean(self.availabilityData)
            self.meanTime = np.mean(self.timeData)
            self.is_successful = True

        except Exception as inst:
            print(inst, "Time", time.time() - start_new_run)

