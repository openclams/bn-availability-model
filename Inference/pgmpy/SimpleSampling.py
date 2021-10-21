from pgmpy.models import BayesianModel
from Inference.Engine import Engine
import time
import numpy as np
import cpdist
import multiprocessing as mp

def samling_thread(bn: BayesianModel, solution, sample_size, results, index):
    results[index] = cpdist.cpdist(bn, solution, int(sample_size))


class SimpleSampling(Engine):

    def __init__(self, bn):
        Engine.__init__(self, bn)
        self.is_exact_algorithm = False

    def nparams(self, bn: BayesianModel):
        # "The default value is 5000 * log10(nparams(fitted)) for discrete and conditional Gaussian networks
        # and 500 * nparams(fitted) for Gaussian networks" bnlearn
        all_params = sum(c.size for cpd in bn.get_cpds() for c in cpd.values)
        return all_params

    def run(self, solution, *argv):
        start_new_run = time.time()
        try:

            cores = mp.cpu_count()
            #print("Cores "+str(cores))
            for i in range(self.repetition):
                start = time.time()

                results = cpdist.cpdist(self.bn, solution, cores)

                availability = results[1]/(results[1]+results[0])

                self.availabilityData.append(availability)

                self.timeData.append(time.time() - start)

            self.meanAvailability = np.mean(self.availabilityData)

            self.meanTime = np.mean(self.timeData)

            self.is_successful = True

        except Exception as inst:
            print(inst, "Time", time.time() - start_new_run)
