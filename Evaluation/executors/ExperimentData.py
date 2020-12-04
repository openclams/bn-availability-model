from typing import Dict

# Store all data of one experimental run
class ExperimentData:
    def __init__(self):
        # The availability results
        self.res_dic:Dict[str,float] = {}
        # The  inference time
        self.time_dic = {}
        # The memory
        self.mem_dic = {}

        self.build_time_dic = {}

        self.total_time_dic = {}

        self.res_dic['n'] = []
        self.time_dic['n'] = []
        self.mem_dic['n'] = []
        self.build_time_dic['n'] = []
        self.total_time_dic['n'] = []


    def addInstance(self,n):
        self.res_dic['n'].append(n)
        self.time_dic['n'].append(n)
        self.mem_dic['n'].append(n)
        self.build_time_dic['n'].append(n)
        self.total_time_dic['n'].append(n)