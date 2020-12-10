from Evaluation.executors.ExperimentData import ExperimentData

from Evaluation.executors.NaiveBN import NaiveBN
import Inference.grain.gRain as grain

class NaiveBNExact(NaiveBN):

    def __init__(self, name ,title, experimentData: ExperimentData, use_cached_file=False, color = 'r', marker ='D'):
        NaiveBN.__init__(self,name ,title, experimentData, use_cached_file, color , marker)

    def setEngine(self):
        self.engine = grain.gRain(self.bn, driver="R", use_cached_file=self.use_cached_file,tmp_file_name="bnlearn_tmp_R_naive")
        self.engine.repetition = 10