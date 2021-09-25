import Evaluation.generators.SimpleExample as gn
import Evaluation.evaluate as ev
from Evaluation.executors.ExperimentData import ExperimentData
from Evaluation.executors.ScalableBNExact import ScalableBNExact
from Evaluation.executors.ScalableBN import ScalableBN
from Evaluation.executors.NaiveBNExact import NaiveBNExact
from Evaluation.executors.NaiveBN import NaiveBN

title = "SimpleExperiment"

generator = lambda n: gn.SimpleExample(n, int(n / 2) + 1)
tests = [150]#range(3,10,2)
experiment = ExperimentData()

instances = [
     ScalableBNExact('ScgRain' ,'BN Exact Inference', experiment),
     ScalableBN('Scbnlearn' ,'BN Approx. Inference', experiment),
     #NaiveBNExact('NavgRain' ,'BN Exact Inference', experiment),
     #NaiveBN('Naivebnlearn' ,'BN Approx. Inference', experiment),
]

r = ev.Evaluate(instances, title, tests,
                skip_engines = [],
                add_to_skip_list={
                    #"ScgRain" : 9,
                    "FT":41,
                    "FTsc":41
                },
                run_file=__file__)
r.run(generator,experiment)





