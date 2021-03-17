from Inference.Engine import Engine

import numpy
import time
import subprocess, os
import xml.etree.ElementTree as ET

# mcub or bdd
class Scram(Engine):
    def __init__(self,tmp_file_name = "ft_mef.xml",method='bdd'):
        Engine.__init__(self,None)
        self.method = method
        self.tmp_file_name = tmp_file_name

    def run(self,solution,*argv):
        # in windows we need a "1" for the probability value

        args = ('scram','--probability','1','--'+self.method,"-o","res.xml",'ft_mef.xml') #

        start = time.time()
        try:
            for i in range(self.repetition):
                start = time.time()

                popen = subprocess.Popen(args, stdout=subprocess.PIPE)
                popen.wait()
                output = str(popen.stdout.read())
                self.timeData.append(time.time() - start)

                tree = ET.parse('res.xml')
                root = tree.getroot()
                prob =  root.find(".//sum-of-products").attrib['probability']
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


