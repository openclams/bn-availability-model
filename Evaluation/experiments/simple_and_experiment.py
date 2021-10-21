import Evaluation.generators.SimpleANDExample as gn
import Evaluation.evaluate as ev
from Evaluation.executors.CpdistScalableBN import CpdistScalableBN
from Evaluation.executors.ExperimentData import ExperimentData
import logging

from Evaluation.executors.ScalableBNExact import ScalableBNExact

logger = logging.getLogger()
logger.disabled = True

title = "SimpleANDExperiment"

generator = lambda n: gn.SimpleANDExample(n)

tests = [700];#range(60,700,10)

experiment = ExperimentData()

instances = [
     CpdistScalableBN('CpdistScalableBN' ,'Scalable BN with Approx Inference', experiment),
     ScalableBNExact('ScalableBNExact' ,'Scalable BN Exact Inference', experiment),
]

r = ev.Evaluate(instances, title, tests,
                skip_engines = [],
                add_to_skip_list={
                    #"ScgRain" : 9,
                },
                run_file=__file__)
r.run(generator,experiment)





