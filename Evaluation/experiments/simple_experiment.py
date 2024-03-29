import Evaluation.generators.SimpleExample as gn
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

title = "Simple Redundant "

generator = lambda n: gn.SimpleExample(n, int(n / 2) + 1)

tests = range(3,12)

experiment = ExperimentData()

instances = [
    CpdistBN('CpdistBN', 'BN with Approx Inference', experiment),
    NaiveBNExact('BNExact', 'BN Exact Inference', experiment),
    FaultTreeExact('FTExact', 'FT Exact', experiment),
    FaultTreeMC('FaultTreeMC','FT MC',experiment)
]

r = ev.Evaluate(instances, title, tests,
                skip_engines = [],
                add_to_skip_list={
                    #"ScgRain" : 9,
                },
                run_file=__file__)
r.run(generator,experiment)





