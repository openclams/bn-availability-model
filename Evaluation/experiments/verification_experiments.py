from Evaluation.generators.CreateFromGraph import CreateFromGraph
import Evaluation.evaluate as ev
from Evaluation.executors.ExperimentData import ExperimentData
from Evaluation.executors.FaultTreeExact import FaultTreeExact
from Evaluation.executors.PrismExact import PrismExact
from Evaluation.executors.NaiveBNExact import NaiveBNExact

import logging



logger = logging.getLogger()
logger.disabled = True

title = "Simple Redundant "

cim = "../../Assets/simple_service/graph.json"
generator = lambda n: CreateFromGraph(n, int(n / 2) + 1, cim,init='N1',use_direct_communication_pattern=True)

tests = range(3,4)

experiment = ExperimentData()

instances = [
    NaiveBNExact('BNExact', 'BN Exact Inference', experiment),
    #FaultTreeExact('FTExact', 'FT Exact', experiment),
    PrismExact('PExact', 'Prism Exact', experiment)
]

r = ev.Evaluate(instances, title, tests,
                skip_engines = [],
                add_to_skip_list={
                    #"ScgRain" : 9,
                },
                run_file=__file__)
r.run(generator,experiment)

