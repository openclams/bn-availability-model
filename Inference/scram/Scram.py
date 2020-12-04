from Inference.Engine import Engine
import rpy2.robjects as robjects
from rpy2.robjects.packages import importr
import numpy
import time

importr('FaultTree')
importr('FaultTree.SCRAM')

# mcub or bdd
class Scram(Engine):
    def __init__(self,tmp_file_name = "ft.R",method='bdd'):
        Engine.__init__(self,None)
        self.method = method
        self.tmp_file_name = tmp_file_name

    def run(self,solution,*argv):

        start = time.time()
        try:
            robjects.r('''
                       # create a function `f`
                       scramFn <- function(file_name, s,m) {
                          tmp <- getwd()
                           source(file_name)
                           avr <- list()
                           bvr <- list()
                           for ( i in 1:s ){
                                  bvr[i] <- system.time({avr[i] <-  scram.probability(ft, list_out=F,method=m)})["elapsed"]
                           }
                           res <- list("availability" = avr, "times" = bvr)
                           setwd(tmp)
                           rm(ft)
                           return(res)
                       }
                       ''')
            r_f = robjects.r['scramFn']
            res = r_f(self.tmp_file_name, self.repetition,self.method)
            res = dict(zip(res.names, map(list, list(res))))

            self.availabilityData = [1-float(e[0]) for e in res['availability']]
            self.meanAvailability = numpy.mean( self.availabilityData)
            self.timeData = [float(e[0]) for e in res['times']]
            self.meanTime = numpy.mean(res['times'])
            self.is_successful = True

        except Exception as inst:
            print(inst, "Time", time.time() - start)
            self.availabilityData = [float('inf')]
            self.meanAvailability = float('inf')
            self.timeData = [float('inf')]
            self.meanTime = float('inf')
            self.is_successful = False


