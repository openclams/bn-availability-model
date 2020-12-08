import Evaluation.generate as gn
import Evaluation.evaluate as ev
from Evaluation.executors.ExperimentData import ExperimentData
# from Evaluation.executors.FaultTreeExact import FaultTreeExact
# from Evaluation.executors.FaultTreeMC import FaultTreeMC
from Evaluation.executors.ScalableBNExact import ScalableBNExact
from Evaluation.executors.ScalableBN import ScalableBN
from Evaluation.executors.NaiveBNExact import NaiveBNExact
from Evaluation.executors.NaiveBN import NaiveBN
from Evaluation.executors.PrismExact import PrismExact
from Evaluation.executors.PrismSim import PrismSim


#from Evaluation.executors.ScalableBNExact import ScalableBNExact

title = "all in one"
cim = "../Tests/simple_service/graph.json"
#cim = "/home/bibartoo/spinoza-scripts/Tests/service_X/graph.json"
generator = lambda n: gn.PrismComparisonExample(n, int(n / 2) + 1, cim,init='G1')
tests = [7,8,9,10,11]
experiment = ExperimentData()

instances = [
     #FaultTreeExact('FT' ,'Fault Tree Analysis', experiment),
     #FaultTreeMC('FTsc', 'Fault Tree Sim', experiment),
     #ScalableBNExact('ScgRain' ,'Scalabl bn exact', experiment),
     ScalableBN('Scbnlearn' ,'Sacal BN app', experiment),
    # NaiveBNExact('NavgRain' ,'Naove BN exact', experiment),
    # NaiveBN('Naivebnlearn' ,'Naive BN approx', experiment),
     PrismExact('PrismEx', 'Prism Exact', experiment),
     PrismSim('PrismSim', 'Prism Sim', experiment),
]

r = ev.Evaluate(instances, title, tests,
                skip_engines = [],
                add_to_skip_list={},
                run_file=__file__)
r.run(generator,experiment)


# Naive BN approx  r X
# Naive BN exact   r D

# Scalable BN appraoc b X
# Scalable BN exact   b D

# Prism  sim  o X
# Prism Exact     o D

# Fault Tree mc  g X
# Fault Tree exact     g D