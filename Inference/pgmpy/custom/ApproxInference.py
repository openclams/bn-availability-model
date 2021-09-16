import math
import multiprocessing
from typing import List, Dict

import numpy as np
import pandas
from pgmpy.sampling import BayesianModelSampling
from pgmpy.models import BayesianModel
import psutil

from Inference.Engine import Engine
import time
import numpy


def check_separation(bn: BayesianModel):
    frontier = []
    explored = []
    frontier.append('er')
    while frontier:
        cur = frontier.pop()
        explored.append(cur)
        parents = bn.get_parents(cur)
        for node in parents:
            if node not in explored and node not in frontier:
                frontier.append(node)
    small_bn = bn.copy()
    for node in bn.nodes():
        if node not in explored:
            small_bn.remove_node(node)
    return small_bn


def nparams(bn: BayesianModel):
    # "The default value is 5000 * log10(nparams(fitted)) for discrete and conditional Gaussian networks
    # and 500 * nparams(fitted) for Gaussian networks" bnlearn
    all_params = sum(c.size for cpd in bn.get_cpds() for c in cpd.values)
    return all_params


def query(bn: BayesianModel, variables: List[str] = [], evidence: Dict[str, str] = {}):
    num_cpus = psutil.cpu_count(logical=False)

    # reduce size of model
    bn: BayesianModel = check_separation(bn)

    # calculate sample size of the Bayesian Network
    sample_size = 5000 * math.log10(nparams(bn))
    sample_per_cpu = math.ceil(sample_size / num_cpus)
    sample_size = int(sample_per_cpu * num_cpus)
    print("Sample size:")
    print(sample_size)
    print("")
    inference = BayesianModelSampling(bn)
    work = []
    for _ in range(num_cpus):
        work.append((inference, sample_per_cpu, variables))
    with multiprocessing.Pool(processes=num_cpus) as pool:
        res = pool.map(f_lw, work)

    probability = np.sum(res) / sample_size
    return probability


def f_ls(work):
    # work consists of bn, sample size, and sol variable list
    df: pandas.DataFrame = work[0].forward_sample(size=work[1], )
    er = len(df[df[work[2][0]] > 0])
    return er


def f_lw(work):
    # work consists of bn, sample size, and sol variable list
    df: pandas.DataFrame = work[0].likelihood_weighted_sample(size=work[1], evidence=[] )
    er = len(df[df[work[2][0]] > 0])
    return er


def f_rs(work):
    # work consists of bn, sample size, and sol variable list
    df: pandas.DataFrame = work[0].rejection_sample(size=work[1], )
    er = len(df[df[work[2][0]] > 0])
    return er


class ApproxInference(Engine):

    def __init__(self, bn):
        Engine.__init__(self, bn)

    def run(self, solution, *argv):
        start_new_run = time.time()
        try:
            for i in range(self.repetition):
                start = time.time()

                value = query(self.bn, variables=[solution], evidence={})

                self.availabilityData.append(value)

                self.timeData.append(time.time() - start)

            self.meanAvailability = numpy.mean(self.availabilityData)
            self.meanTime = numpy.mean(self.timeData)
            self.is_successful = True

        except Exception as inst:
            print(inst, "Time", time.time() - start_new_run)
            self.availabilityData = [float('inf')]
            self.meanAvailability = float('inf')
            self.timeData = [float('inf')]
            self.meanTime = float('inf')
            self.is_successful = False
