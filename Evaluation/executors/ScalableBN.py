from Evaluation.executors.ExperimentData import ExperimentData
from Evaluation.generators.Generator import Generator
from Evaluation.executors.NaiveBN import NaiveBN
import Inference.bnlearn.BNLearn as bnlearn

class ScalableBN(NaiveBN):

    def __init__(self, name ,title, experimentData: ExperimentData, use_cached_file=False, color = 'b', marker ='X'):
        NaiveBN.__init__(self,name ,title, experimentData, use_cached_file ,color , marker)

    def setEngine(self):
        self.engine = bnlearn.BNLearn(self.bn, driver="R", use_cached_file=self.use_cached_file,
                                      tmp_file_name="bnlearn_tmp_R")
        self.engine.repetition = 20
    def generate(self):
        self.bn = self.generator.createScalableNetwork()
