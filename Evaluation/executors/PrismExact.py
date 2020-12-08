from Evaluation.executors.ExperimentData import ExperimentData
from Evaluation.executors.BaseExperiment import BaseExperiment
from Inference.prism.PrismSteadyState import PrismSteadyState

class PrismExact(BaseExperiment):

    def __init__(self, name ,title, experimentData: ExperimentData, color = 'y', marker ='D'):
        BaseExperiment.__init__(self,name ,title, experimentData, color , marker)

    def memory(self):
        return 0

    def generate(self):
       self.generator.createPrism() # creates the cim.sm file

    def setEngine(self):
        self.engine =PrismSteadyState()