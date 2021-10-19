from Evaluation.executors.ExperimentData import ExperimentData
from Evaluation.executors.NaiveBN import NaiveBN
from Inference.pgmpy.SimpleSampling import SimpleSampling


class CpdistScalableBN(NaiveBN):

    def __init__(self, name ,title, experimentData: ExperimentData, use_cached_file=False, color = 'b', marker ='X'):
        NaiveBN.__init__(self,name ,title, experimentData, use_cached_file ,color , marker)

    def setEngine(self):
        self.engine = SimpleSampling(self.bn)
        self.engine.repetition = 20

    def generate(self):
        self.bn = self.generator.createScalableNetwork()
