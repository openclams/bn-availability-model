from Evaluation.executors.ExperimentData import ExperimentData
from Evaluation.executors.ScalableBN import ScalableBN
import Inference.grain.gRain as grain

class ScalableBNExact(ScalableBN):

    def __init__(self, name ,title, experimentData: ExperimentData, use_cached_file=False, color = 'b', marker ='D'):
        ScalableBN.__init__(self,name ,title, experimentData, use_cached_file ,color , marker)


    def setEngine(self):
        self.engine = grain.gRain(self.bn, driver="R", use_cached_file=self.use_cached_file,tmp_file_name="bnlearn_tmp_R")
        self.engine.repetition = 10