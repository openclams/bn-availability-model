from Evaluation.executors.ExperimentData import ExperimentData
from pgmpy.models import BayesianModel
import Inference.bnlearn.BNLearn as bnlearn
from Evaluation.generators.Generator import Generator
from Evaluation.executors.BaseExperiment import BaseExperiment
from pathlib import Path
import time
import os

class NaiveBNFilesize(BaseExperiment):

    def __init__(self, name ,title, experimentData: ExperimentData, use_cached_file=False, color = 'r', marker ='X'):
        BaseExperiment.__init__(self,name ,title, experimentData, color , marker)

        self.use_cached_file = use_cached_file
        self.bn = BayesianModel()
        self.filename = "bnlearn_tmp_R_naive"



    def get_size(self,start_path='.'):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(start_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                # skip if it is symbolic link
                if not os.path.islink(fp):
                    total_size += os.path.getsize(fp)

        return total_size

    def memory(self):
        root_directory = Path('.')
        return self.get_size(root_directory / self.filename)

    def generate(self):
        self.bn = self.generator.createNaiveNetwork(write=False)

    def run(self):
        start_total_time = time.time()

        total_time = time.time() - start_total_time

        self.data.res_dic[self.name].append(self.engine.meanAvailability)
        self.data.time_dic[self.name].append(self.engine.meanTime)
        self.data.total_time_dic[self.name].append(total_time)


    def setEngine(self):
        self.engine = bnlearn.BNLearn(self.bn, driver="R", use_cached_file=self.use_cached_file, tmp_file_name= self.filename)
        self.engine.repetition = 20

    def clean(self):
        pass
        # del self.bn