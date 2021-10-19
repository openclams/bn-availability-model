from Evaluation.executors.ExperimentData import ExperimentData
from Evaluation.executors.NaiveBN import NaiveBN
from Inference.pgmpy.SimpleSampling import SimpleSampling


class CpdistBN(NaiveBN):

    def __init__(self, name ,title, experimentData: ExperimentData, use_cached_file=False, color = 'r', marker ='X'):
        NaiveBN.__init__(self,name ,title, experimentData, use_cached_file ,color , marker)

    def setEngine(self):
        self.engine = SimpleSampling(self.bn)
        self.engine.repetition = 20
