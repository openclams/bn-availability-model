from Inference.Engine import Engine
import time


class Dummy(Engine):

    def __init__(self, bn):
        Engine.__init__(self, bn)
        self.is_exact_algorithm = False


    def run(self, solution, *argv):
        start_new_run = time.time()
        try:

            self.availabilityData.append(0)
            self.timeData.append(0)

            self.meanAvailability = 0
            self.meanTime = 0
            self.is_successful = True

        except Exception as inst:
            print(inst, "Time", time.time() - start_new_run)

