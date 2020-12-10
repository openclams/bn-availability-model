from Evaluation.executors.PrismExact import PrismExact
from Inference.prism.PrismModelSim import PrismModelSim

class PrismSim(PrismExact):

    def setEngine(self):
        self.color = 'y'
        self.marker = 'X'
        self.engine =PrismModelSim()
        self.engine.repetition = 20