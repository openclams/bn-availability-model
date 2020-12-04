from Evaluation.executors.ExperimentData import ExperimentData
from pgmpy.models import BayesianModel
import Inference.bnlearn.BNLearn as bnlearn
from Evaluation.generators.Generator import Generator
from Evaluation.executors.BaseExperiment import BaseExperiment

class NaiveBN(BaseExperiment):

    def __init__(self, name ,title, experimentData: ExperimentData, use_cached_file=False, color = 'r', marker ='X'):
        BaseExperiment.__init__(self,name ,title, experimentData, color , marker)

        self.use_cached_file = use_cached_file
        self.bn = BayesianModel()

    def memory(self):
        size = 0
        for n in self.bn.nodes():
            n = self.bn.get_cpds(n).get_values()
            size = size + (n.size * n.itemsize)
        return size

    def generate(self):
        self.bn = self. generator.createNaiveNetwork()

    def setEngine(self):
        self.engine = bnlearn.BNLearn(self.bn, driver="R", use_cached_file=self.use_cached_file, tmp_file_name="bnlearn_tmp_R")

    def clean(self):
        del self.bn