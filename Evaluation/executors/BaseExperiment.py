from Evaluation.executors.ExperimentData import ExperimentData
from pgmpy.models import BayesianModel
from Evaluation.generators.Generator import Generator
from Inference.Engine import Engine
import time


class BaseExperiment:

    def __init__(self, name, title, experimentData: ExperimentData, color='r', marker='X'):
        self.data = experimentData
        self.name = name
        self.color = color
        self.marker = marker
        self.title = title

        self.engine = None
        self.generator = None

        self.data.res_dic[self.name] = []
        self.data.time_dic[self.name] = []
        self.data.build_time_dic[self.name] = []
        self.data.total_time_dic[self.name] = []
        self.data.mem_dic[self.name] = []

    # overwrite
    def memory(self):
        size = 0;
        for n in self.bn.nodes():
            n = self.get_cpds(n).get_values()
            size = size + (n.size * n.itemsize)
        return size

    def build(self):
        start_build_time_nv = time.time()
        self.generate()
        mem_nv = self.memory()
        build_time_nv = time.time() - start_build_time_nv
        self.data.build_time_dic[self.name].append(build_time_nv)
        self.data.mem_dic[self.name].append(mem_nv)

    def setGenerator(self,generator: Generator):
        self.generator = generator

    #Overwrie
    def generate(self):
        pass

    #Overwrite
    def setEngine(self):
        pass

    def run(self):
        start_total_time = time.time()

        self.engine.run(self.generator.solution)

        total_time = time.time() - start_total_time

        self.data.res_dic[self.name].append(self.engine.meanAvailability)
        self.data.time_dic[self.name].append(self.engine.meanTime)
        self.data.total_time_dic[self.name].append(total_time)

    def ignoreBuild(self):
        self.data.build_time_dic[self.name].append(0)
        self.data.mem_dic[self.name].append(0)

    def ignoreRun(self):
        self.data.res_dic[self.name].append(float('inf'))
        self.data.time_dic[self.name].append(float('inf'))
        self.data.total_time_dic[self.name].append(float('inf'))

    #Overwrite
    def clean(self):
        pass