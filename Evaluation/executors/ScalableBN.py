from Evaluation.executors.ExperimentData import ExperimentData
from Evaluation.generators.Generator import Generator
from Evaluation.executors.NaiveBN import NaiveBN

class ScalableBN(NaiveBN):

    def __init__(self, name ,title, experimentData: ExperimentData, use_cached_file=False, color = 'b', marker ='X'):
        NaiveBN.__init__(self,name ,title, experimentData, use_cached_file ,color , marker)

    def generate(self):
        self.bn = self.generator.createScalableNetwork()
