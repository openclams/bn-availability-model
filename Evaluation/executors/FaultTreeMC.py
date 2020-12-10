from Evaluation.executors.FaultTreeExact import FaultTreeExact
from Inference.scram.Scram import Scram

class FaultTreeMC(FaultTreeExact):

    def setEngine(self):
        self.color = 'g'
        self.marker = 'X'
        self.engine = Scram(tmp_file_name="ft.R",method='mcub')
        self.engine.repetition = 10