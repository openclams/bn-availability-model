import random

from Inference.Engine import Engine

import numpy
import time
import subprocess
import re

# mcub or bdd
class Scram(Engine):
    def __init__(self,tmp_file_name = "ft_mef.xml",method='bdd'):
        Engine.__init__(self,None)
        self.method = method
        self.tmp_file_name = tmp_file_name

    def run(self,solution,*argv):
        # in windows we need a "1" for the probability value


        start = time.time()
        try:
            for i in range(self.repetition):
                args = ('/home/bibartoo/scram-0.16.2/bin/scram','--probability','1','--'+self.method,'--seed',str(random.randint(1, 1e8)),"-o","res.xml",'ft_mef.xml') #

                popen = subprocess.Popen(args, stdout=subprocess.PIPE)
                popen.wait()
                output = str(popen.stdout.read())
                self.timeData.append(time.time() - start)

                prob,duration =  self.parseOutput()
                self.availabilityData.append(1-float(prob))


            self.meanAvailability = numpy.mean(self.availabilityData)
            self.meanTime = numpy.mean(self.timeData)
            self.is_successful = True

        except Exception as inst:
            print(inst, "Time", time.time() - start)
            self.availabilityData = [float('inf')]
            self.meanAvailability = float('inf')
            self.timeData = [float('inf')]
            self.meanTime = float('inf')
            self.is_successful = False

    def parseOutput(self):
        prob = float('inf')
        duration = 0
        count = 0
        with open('res.xml', 'r') as f:
            lines = f.readlines()
            for line in lines:
                if 'sum-of-products' in line:
                    count += 1
                    prob = float(re.findall("((\\d{1,3}([,\\.]{1}))*[\\d|-]{1,})",line[line.index('probability'):])[0][0])
                # if '<products>' in line:
                #     count +=  1
                #     duration += float(re.findall(r">(.*?)<", line)[0][0])
                # if '<probability>' in line:
                #     count += 1
                #     duration += float(re.findall(r">(.*?)<", line)[0][0])
                # if count == 3:
                    break

        return prob, duration
