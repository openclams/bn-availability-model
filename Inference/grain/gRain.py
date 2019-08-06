from Inference.Engine import Engine
import rpy2.robjects as robjects
from BayesianNetworks.pgmpy import writers as bnwriters
from rpy2.robjects.packages import importr
import numpy
import time

importr('bnlearn')
importr('gRain')

class gRain(Engine):

    def __init__(self,bn,use_cached_file = False,tmp_file_name = "bnlearn_tmp",driver="BIF"):
        Engine.__init__(self,bn)
        self.use_cached_file = use_cached_file
        self.tmp_file_name = tmp_file_name
        self.driver = driver


    def run(self,solution,*argv):
        if self.driver == "BIF":
            self.run_with_BIF(solution,*argv)
        elif self.driver == "R":
            self.run_with_R(solution,*argv)
        else:
            raise Exception('Write driver is unknown.')

    def run_with_BIF(self,solution,*argv):
        if not self.use_cached_file:
            bnwriters.writeBIF(self.bn, self.tmp_file_name)

        start = time.time()
        try:
            robjects.r('''
                # create a function `f`
                BIFgRainFn <- function(file_name, node, s) {
                   tmp <- getwd()
                   bn_read <- read.bif(file_name, debug=FALSE)
                   jtree = compile(as.grain(bn_read))
                   avr <- list()
                   bvr <- list()
                   for ( i in 1:s ){
                       bvr[i] <- system.time({avr[i] <-  querygrain(jtree, nodes = node)[[node]][2]})["elapsed"]
                   }
                   res <- list("availability" = avr, "times" = bvr)
                   setwd(tmp)
                   return(res)
                }
                ''')
            r_f = robjects.r['BIFgRainFn']
            res = r_f(self.tmp_file_name, solution, self.repetition)
            res = dict(zip(res.names, map(list, list(res))))

            self.availabilityData = res['availability']
            self.meanAvailability = numpy.mean(res['availability'])
            self.timeData = res['times']
            self.meanTime = numpy.mean(res['times'])
            self.is_successful = True

        except Exception as inst:
            print(inst, "Time", time.time() - start)



    def run_with_R(self,solution,*argv):
        if not self.use_cached_file:
            bnwriters.writeR(self.bn, self.tmp_file_name)

        start = time.time()
        try:
            robjects.r('''
                       # create a function `f`
                       RgRainFn <- function(file_name, node, s) {
                          tmp <- getwd()
                           source(file_name)
                           jtree = compile(net1)
                           avr <- list()
                           bvr <- list()
                           for ( i in 1:s ){
                                  bvr[i] <- system.time({avr[i] <-  querygrain(jtree, nodes = node,type="marginal")[[node]][2]})["elapsed"]
                           }
                           res <- list("availability" = avr, "times" = bvr)
                           setwd(tmp)
                           return(res)
                       }
                       ''')
            r_f = robjects.r['RgRainFn']
            res = r_f(self.tmp_file_name+"/bngraphsrc.R", solution, self.repetition)
            res = dict(zip(res.names, map(list, list(res))))

            self.availabilityData = res['availability']
            self.meanAvailability = numpy.mean(res['availability'])
            self.timeData = res['times']
            self.meanTime = numpy.mean(res['times'])
            self.is_successful = True

        except Exception as inst:
            print(inst, "Time", time.time() - start)
