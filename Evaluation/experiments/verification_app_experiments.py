import Evaluation.generators.CreateAppFromGraph as gn
import Evaluation.evaluate as ev
#from Evaluation.executors.CpdistScalableBN import CpdistScalableBN
from Evaluation.executors.ExperimentData import ExperimentData
from Evaluation.executors.CpdistBN import CpdistBN
#from Evaluation.executors.FaultTreeExact import FaultTreeExact
from Evaluation.executors.FaultTreeMC import FaultTreeMC
#from Evaluation.executors.ScalableBN import ScalableBN
#from Evaluation.executors.NaiveBNExact import NaiveBNExact
#from Evaluation.executors.NaiveBN import NaiveBN
import logging
import itertools
#from Evaluation.executors.ScalableBNExact import ScalableBNExact

logger = logging.getLogger()
logger.disabled = True

title = "Verification App Replication Fully Large "
cim = "Assets/large_service_v2/graph.json"
#generator = lambda n: gn.CreateAppFromGraph(n, int(n / 2) + 1, cim,init='N1')

nm = [[i for i in [3,6]], #13
      [i for i in [3,6,9]]] #12

options = list(itertools.product(*nm))

def generator(n):
    global cim
    global options

    return gn.CreateAppFromGraph(options[n][0], options[n][1], cim,init='N1',fully=True)

tests = range(0,len(options))
experiment = ExperimentData()

instances = [
    CpdistBN('CpdistBN', 'BN with Approx Inference', experiment),
    #CpdistBN('CpdistBN', 'BN Approx Inference', experiment),
    #FaultTreeExact('FTExact', 'FT Exact', experiment),
    FaultTreeMC('FaultTreeMC','FT MC',experiment)
]

r = ev.Evaluate(instances, title, tests,
                skip_engines = [],
                add_to_skip_list={
                    #"BNExact" : 6,
                },
                run_file=__file__)
r.run(generator,experiment)
