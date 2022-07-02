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

title = "Large Replicated"
cim = "Assets/large_service_v2/graph.json"
generator = lambda n: gn.CreateFromGraph(n, int(n / 2) + 1, cim,init='N1',use_direct_communication_pattern=False)
tests = list(range(110,301,10)) #[3,6,8,9,12,15,18,21,24,27,30]+list(range(40,101,10))
experiment = ExperimentData()

instances = [
    CpdistScalableBN('sc_approx', 'SC with Approx Inference', experiment),
    #CpdistBN('nv_approx', 'NV with Approx Inference', experiment)
    ScalableBNExact('sc_exact', 'SC with Exact Inference', experiment),
    #NaiveBN('approx', 'BN Approx Inference', experiment),
    #NaiveBNExact('exact', 'BN Exact Inference', experiment),
    #FaultTreeExact('FTExact', 'FT Exact', experiment),
    #FaultTreeMC('FaultTreeMC','FT MC',experiment)
]

r = ev.Evaluate(instances, title, tests,
                skip_engines = [],
                add_to_skip_list={
                    "sc_exact" : 6
                },
                run_file=__file__)
r.run(generator,experiment)





