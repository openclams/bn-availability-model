from Evaluation.executors.NaiveBNExact import NaiveBNExact
from Evaluation.generators.CreateFromGraph import CreateFromGraph
import Evaluation.evaluate as ev
from Evaluation.executors.ExperimentData import ExperimentData
from Evaluation.executors.FaultTreeExact import FaultTreeExact
#from Evaluation.executors.PrismExact import PrismExact
#from Evaluation.executors.NaiveBNExact import NaiveBNExact

import logging



logger = logging.getLogger()
logger.disabled = True

title = "Verification Simple Replicated "

cim = "Assets/simple_service/graph.json"
generator = lambda n: CreateFromGraph(n, int(n / 2) + 1, cim,init='N1',use_direct_communication_pattern=False)

tests = range(8,19)

experiment = ExperimentData()

instances = [
    FaultTreeExact('FTExact', 'FT Exact', experiment),
    #PrismExact('PExact', 'Prism Exact', experiment),
    #NaiveBNExact('BNExact', 'BN Exact Inference', experiment)
]

r = ev.Evaluate(instances, title, tests,
                skip_engines = [],
                add_to_skip_list={
                    "BNExact" : 7,
                },
                run_file=__file__)
r.run(generator,experiment)

