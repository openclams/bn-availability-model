from Evaluation.executors.ExperimentData import ExperimentData
from Evaluation.generators.Generator import Generator
from Evaluation.executors.BaseExperiment import BaseExperiment
from Inference.scram.Scram import Scram
from FaultTrees.FaultTree import FaultTree


class FaultTreeExact(BaseExperiment):

    def __init__(self, name ,title, experimentData: ExperimentData, color = 'g', marker ='D'):
        BaseExperiment.__init__(self,name ,title, experimentData, color=color , marker =marker)


    def memory(self):
        return 0

    def generate(self):
        self.generator.createFaultTree() # creates the fr.R file

    def setEngine(self):
        self.engine = Scram(tmp_file_name="ft.R",method='bdd')