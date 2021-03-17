from Evaluation.executors.ExperimentData import ExperimentData
from pgmpy.models import BayesianModel
import Inference.bnlearn.BNLearn as bnlearn
from Evaluation.generators.Generator import Generator
from Evaluation.executors.BaseExperiment import BaseExperiment
import time

class NaiveBNCPTsize(BaseExperiment):

    def __init__(self, name ,title, experimentData: ExperimentData, use_cached_file=False, color = 'r', marker ='X'):
        BaseExperiment.__init__(self,name ,title, experimentData, color , marker)

        self.use_cached_file = use_cached_file
        self.bn = BayesianModel()
        self.filename = "bnlearn_tmp_R_naive"

    def memory(self):
        size = 0
        for n in self.bn.nodes():
            n = self.bn.get_cpds(n).get_values()
            size = size + n.size
        return size

    def generate(self):
        self.bn = self. generator.createNaiveNetwork()

    def run(self):
        start_total_time = time.time()
        total_time = time.time() - start_total_time

        self.data.res_dic[self.name].append(self.engine.meanAvailability)
        self.data.time_dic[self.name].append(self.engine.meanTime)
        self.data.total_time_dic[self.name].append(total_time)


    def setEngine(self):
        self.engine = bnlearn.BNLearn(self.bn, driver="R", use_cached_file=self.use_cached_file, tmp_file_name=self.filename)
        self.engine.repetition = 20

    def clean(self):
        del self.bn