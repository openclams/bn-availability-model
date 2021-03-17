from Evaluation.executors.ExperimentData import ExperimentData
from Evaluation.generators.Generator import Generator
from Evaluation.executors.BaseExperiment import BaseExperiment
from Inference.scram.Scram import Scram
from FaultTrees.FaultTree import FaultTree
from pathlib import Path


class FaultTreeExact(BaseExperiment):

    def __init__(self, name ,title, experimentData: ExperimentData, color = 'g', marker ='D'):
        BaseExperiment.__init__(self,name ,title, experimentData, color=color , marker =marker)


    def memory(self):
        return Path('ft_mef.xml').stat().st_size

    def generate(self):
        self.generator.createFaultTree() # creates the ft_mef.xml file

    def setEngine(self):
        self.engine = Scram(tmp_file_name="ft_mef.xml",method='bdd')
        self.engine.repetition = 1