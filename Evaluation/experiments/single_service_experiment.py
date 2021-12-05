import Evaluation.generators.CreateFromGraph as gn
import Evaluation.evaluate as ev
from Evaluation.executors.CpdistScalableBN import CpdistScalableBN
from Evaluation.executors.ExperimentData import ExperimentData
from Evaluation.executors.CpdistBN import CpdistBN
from Evaluation.executors.FaultTreeExact import FaultTreeExact
from Evaluation.executors.FaultTreeMC import FaultTreeMC
from Evaluation.executors.ScalableBN import ScalableBN
from Evaluation.executors.NaiveBNExact import NaiveBNExact
from Evaluation.executors.NaiveBN import NaiveBN
import logging

from Evaluation.executors.ScalableBNExact import ScalableBNExact

logger = logging.getLogger()
logger.disabled = True

title = "Simple Scalable Service Experiment"
cim = "../../Assets/simple_service/graph.json"
generator = lambda n: gn.CreateFromGraph(n, int(n / 2) + 1, cim,init='N1')
tests = [5]
experiment = ExperimentData()

instances = [
    CpdistScalableBN('sc_approx', 'SC with Approx Inference', experiment),
    #ScalableBNExact('sc_exact', 'SC with Exact Inference', experiment),
    #NaiveBN('approx', 'BN Approx Inference', experiment),
    #NaiveBNExact('exact', 'BN Exact Inference', experiment),
    #FaultTreeExact('FTExact', 'FT Exact', experiment),
    #FaultTreeMC('FaultTreeMC','FT MC',experiment)
]

r = ev.Evaluate(instances, title, tests,
                skip_engines = [],
                add_to_skip_list={
                    "approx" : 31,
                    "exact" : 10
                },
                run_file=__file__)
r.run(generator,experiment)





