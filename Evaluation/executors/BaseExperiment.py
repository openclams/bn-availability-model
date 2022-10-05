from Evaluation.executors.ExperimentData import ExperimentData
from pgmpy.models import BayesianModel
from Evaluation.generators.Generator import Generator
from Inference.Engine import Engine
import time
import numpy as np
import scipy.stats

class BaseExperiment:

    def __init__(self, name, title, experimentData: ExperimentData, color='r', marker='X',linestyle='-'):
        self.data = experimentData
        self.name = name
        self.color = color
        self.marker = marker
        self.title = title
        self.linestyle = linestyle

        self.engine = None
        self.generator = None

        self.data.res_dic[self.name] = []
        self.data.time_dic[self.name] = []
        self.data.build_time_dic[self.name] = []
        self.data.total_time_dic[self.name] = []
        self.data.mem_dic[self.name] = []



    def computeStats(self, data, confidence=0.95):
        a = 1.0 * np.array(data)
        n = len(a)
        m, std, se = np.mean(a), np.std(a) ,scipy.stats.sem(a)
        h = se * scipy.stats.t.ppf((1 + confidence) / 2., n - 1)
        return std, se, h

    # overwrite
    def memory(self):
        size = 0
        for n in self.bn.nodes():
            n = self.get_cpds(n).get_values()
            size = size + n.size
        return size

    def build(self):
        start_build_time_nv = time.perf_counter()
        self.generate()
        build_time_nv = time.perf_counter() - start_build_time_nv
        mem_nv = self.memory()
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
        start_total_time = time.perf_counter()

        self.engine.run(self.generator.solution)

        total_time = time.perf_counter() - start_total_time

        self.data.res_dic[self.name].append(self.engine.meanAvailability)
        std, se, c95 = self.computeStats(self.engine.availabilityData)
        self.createStatDic()
        self.data.res_dic[self.name + "_std"].append(std)
        self.data.res_dic[self.name + "_c95"].append(c95)
        self.data.res_dic[self.name + "_se"].append(se)

        self.data.time_dic[self.name].append(self.engine.meanTime)
        std, se, c95 = self.computeStats(self.engine.timeData)
        self.data.time_dic[self.name + "_std"].append(std)
        self.data.time_dic[self.name + "_c95"].append(c95)
        self.data.time_dic[self.name + "_se"].append(se)

        self.data.total_time_dic[self.name].append(total_time)

    def createStatDic(self):
        if self.name + "_std" not in self.data.res_dic:
            self.data.res_dic[self.name + "_std"] = []
            self.data.res_dic[self.name + "_c95"] = []
            self.data.res_dic[self.name + "_se"] = []
            self.data.time_dic[self.name + "_std"] = []
            self.data.time_dic[self.name + "_c95"] = []
            self.data.time_dic[self.name + "_se"] = []

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