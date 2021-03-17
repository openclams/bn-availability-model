from Evaluation.executors.ExperimentData import ExperimentData
from Evaluation.generators.Generator import Generator
from Evaluation.executors.memory.NaiveBNCPTsize import NaiveBNCPTsize
import Inference.bnlearn.BNLearn as bnlearn

class ScalableBNCPTsize(NaiveBNCPTsize):

    def __init__(self, name ,title, experimentData: ExperimentData, use_cached_file=False, color = 'b', marker ='X'):
        NaiveBNCPTsize.__init__(self,name ,title, experimentData, use_cached_file ,color , marker)
        self.filename = "bnlearn_tmp_R"

    def generate(self):
        self.bn = self.generator.createScalableNetwork()
