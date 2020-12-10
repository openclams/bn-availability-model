from Inference.Engine import Engine
import rpy2.robjects as robjects
from BayesianNetworks.pgmpy import writers as bnwriters
from rpy2.robjects.packages import importr
import numpy
import scipy.stats as st
import time

importr('bnlearn')
importr('gRain')

class BNLearn(Engine):

    def __init__(self,bn,use_cached_file = False,tmp_file_name = "bnlearn_tmp",driver="BIF"):
        Engine.__init__(self,bn)
        self.use_cached_file = use_cached_file
        self.tmp_file_name = tmp_file_name
        self.driver = driver
        self.is_exact_algorithm = False


    def run(self,solution,*argv):
        if self.driver == "BIF":
            self.run_with_BIF(solution,*argv)
        elif self.driver == "R":
            self.run_with_R(solution,*argv)
        else:
            raise Exception('Write driver is unknown.')

    def run_with_BIF(self,solution,*argv):
        if not self.use_cached_file:
            start = time.time()
            bnwriters.writeBIF(self.bn, self.tmp_file_name)
            # print("Finished writing ",time.time() - start)
        start = time.time()
        try:
            robjects.r('''
                # create a function `f`
                BIFbnlearnFn <- function(file_name, node, s) {
                 tmp <- getwd()
                   bn_read <- read.bif(file_name, debug=FALSE)
                    #write.bif("some.bif",bn_read)
                   avr <- list()
                   bvr <- list()
                   for ( i in 1:s ){
                       bvr[i] <- system.time({avr[i] <- prop.table(table(cpdist(bn_read, nodes=node, method='ls', evidence=TRUE)))[2]})["elapsed"]
                   }
                   res <- list("availability" = avr, "times" = bvr)
                    setwd(tmp)
                    rm(bn_read)
                   return(res)
                }
                ''')
            r_f = robjects.r['BIFbnlearnFn']
            res = r_f(self.tmp_file_name, solution, self.repetition)
            res = dict(zip(res.names, map(list, list(res))))

            self.availabilityData = [float(e[0]) for e in res['availability']]
            self.meanAvailability = numpy.mean(res['availability'])
            self.timeData = [float(e[0]) for e in res['times']]
            self.meanTime = numpy.mean(res['times'])
            self.is_successful = True

            #print(self.meanAvailability)
            #print(st.describe(res['availability']))
            #print(st.describe(res['times']))

        except Exception as inst:
            print(inst, "Time", time.time() - start)
            self.availabilityData = [float('inf')]
            self.meanAvailability = float('inf')
            self.timeData = [float('inf')]
            self.meanTime = float('inf')
            self.is_successful = False


    def run_with_R(self,solution,*argv):
        if not self.use_cached_file:
            start = time.time()
            bnwriters.writeR(self.bn, self.tmp_file_name)
            # print("Finished writing ", time.time() - start)

        start = time.time()
        try:
            robjects.r('''
                       # create a function `f`
                       RbnlearnFn <- function(file_name, node, s) {
                       tmp <- getwd()
                           source(file_name)
                           bn_read <- as.bn.fit(net1)
                           avr <- list()
                           bvr <- list()
                           for ( i in 1:s ){
                               bvr[i] <- system.time({avr[i] <- prop.table(table(cpdist(bn_read, nodes=node, method='ls', evidence=TRUE)))[2]})["elapsed"]
                            print(i)
                           }
                           res <- list("availability" = avr, "times" = bvr)
                           setwd(tmp)
                           rm(net1,bn_read)
                           return(res)
                       }
                       ''')
            r_f = robjects.r['RbnlearnFn']
            res = r_f(self.tmp_file_name+"/bngraphsrc.R", solution, self.repetition)
            res = dict(zip(res.names, map(list, list(res))))
            self.availabilityData = [float(e[0]) for e in res['availability']]
            self.meanAvailability = numpy.mean(res['availability'])
            self.timeData = [float(e[0]) for e in res['times']]
            self.meanTime = numpy.mean(res['times'])
            self.is_successful = True

        except Exception as inst:
            self.availabilityData = [float('inf')]
            self.meanAvailability = float('inf')
            self.timeData = [float('inf')]
            self.meanTime = float('inf')
            self.is_successful = False
        # print("Computation finished",time.time()-start)
        #print(self.meanAvailability)
        #print(st.describe(res['availability']))
        #print(st.describe(res['times']))