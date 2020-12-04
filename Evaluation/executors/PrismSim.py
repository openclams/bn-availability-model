from Inference.scram.Scram import Scram
from Evaluation.executors.PrismExact import PrismExact
from Inference.prism.PrismModelSim import PrismModelSim

class PrismSim(PrismExact):

    def setEngine(self):
        self.engine =PrismModelSim()