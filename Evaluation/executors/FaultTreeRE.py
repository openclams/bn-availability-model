from Evaluation.executors.FaultTreeExact import FaultTreeExact
from Inference.scram.Scram import Scram
from Evaluation.executors.ExperimentData import ExperimentData

class FaultTreeRE(FaultTreeExact):

    def __init__(self, name ,title, experimentData: ExperimentData, color = 'g', marker ='X'):
        FaultTreeExact.__init__(self,name ,title, experimentData, color=color , marker =marker)

    def setEngine(self):
        self.engine = Scram(tmp_file_name="ft_mef.xml",method='rare-event')
        self.engine.repetition = 20