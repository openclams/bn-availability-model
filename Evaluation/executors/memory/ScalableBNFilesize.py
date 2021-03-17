from Evaluation.executors.ExperimentData import ExperimentData
from Evaluation.generators.Generator import Generator
from Evaluation.executors.memory.NaiveBNFilesize import NaiveBNFilesize
import Inference.bnlearn.BNLearn as bnlearn

class ScalableBNFilesize(NaiveBNFilesize):

    def __init__(self, name ,title, experimentData: ExperimentData, use_cached_file=False, color = 'b', marker ='X'):
        NaiveBNFilesize.__init__(self,name ,title, experimentData, use_cached_file ,color , marker)
        self.filename = "bnlearn_tmp_R"

    def generate(self):
        self.bn = self.generator.createScalableNetwork(write=False)
