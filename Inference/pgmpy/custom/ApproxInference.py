from Inference.Engine import Engine
import time
import numpy
from typing import List, Dict


def query(bn, variables: List[str] = [], evidence: Dict[str, str] = {}):
    return 0


class ApproxInference(Engine):

    def __init__(self, bn):
        Engine.__init__(self, bn)

    def run(self, solution, *argv):
        start_new_run = time.time()
        try:
            for i in range(self.repetition):
                start = time.time()

                value = query(self.bn, variables=[solution], evidence={})

                self.availabilityData.append(value)

                self.timeData.append(time.time() - start)

            self.meanAvailability = numpy.mean(self.availabilityData)
            self.meanTime = numpy.mean(self.timeData)
            self.is_successful = True

        except Exception as inst:
            print(inst, "Time", time.time() - start_new_run)
            self.availabilityData = [float('inf')]
            self.meanAvailability = float('inf')
            self.timeData = [float('inf')]
            self.meanTime = float('inf')
            self.is_successful = False
