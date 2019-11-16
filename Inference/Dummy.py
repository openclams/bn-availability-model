from Inference.Engine import Engine
import time


class Dummy(Engine):

    def __init__(self):
        pass

    def run(self, solution, *argv):
        self.availabilityData.append(0)
        self.timeData.append(0)

        self.meanAvailability = 0
        self.meanTime = 0
        self.is_successful = True



