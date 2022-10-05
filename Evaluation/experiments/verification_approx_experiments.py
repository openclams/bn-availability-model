from Evaluation.executors.CpdistBN import CpdistBN
from Evaluation.executors.CpdistScalableBN import CpdistScalableBN
from Evaluation.executors.FaultTreeExact import FaultTreeExact
from Evaluation.executors.FaultTreeMC import FaultTreeMC
from Evaluation.executors.FaultTreeRE import FaultTreeRE
from Evaluation.executors.PrismSim import PrismSim
from Evaluation.generators.CreateFromGraph import CreateFromGraph
import Evaluation.evaluate as ev
from Evaluation.executors.ExperimentData import ExperimentData


import logging



logger = logging.getLogger()
logger.disabled = True

title = "Approx Verification Large Replicated "

cim = "Assets/large_service_v2/graph.json"
generator = lambda n: CreateFromGraph(n, int(n / 2) + 1, cim,init='N1',use_direct_communication_pattern=False)

tests = range(3,20)

experiment = ExperimentData()

instances = [
    FaultTreeMC('FTApprox', 'FT Approx', experiment),
    #PrismSim('PApprox', 'Prism Exact', experiment),
    CpdistBN('BNApprox', 'BN Approx Inference', experiment)
]

r = ev.Evaluate(instances, title, tests,
                skip_engines = [],
                add_to_skip_list={
                    "FTApprox" : 12,
                },
                run_file=__file__)
r.run(generator,experiment)

