import Evaluation.generators.CreateFromGraph as gn
import Evaluation.evaluate as ev
from Evaluation.executors.ExperimentData import ExperimentData
from Evaluation.executors.FaultTreeExact import FaultTreeExact
from Evaluation.executors.FaultTreeMC import FaultTreeMC
from Evaluation.executors.ScalableBNExact import ScalableBNExact
from Evaluation.executors.ScalableBN import ScalableBN
from Evaluation.executors.NaiveBNExact import NaiveBNExact
from Evaluation.executors.NaiveBN import NaiveBN
from Evaluation.executors.PrismExact import PrismExact
from Evaluation.executors.PrismSim import PrismSim


#from Evaluation.executors.ScalableBNExact import ScalableBNExact

title = "First Scenario until 40"
cim = "../../Assets/simple_service/graph.json"
generator = lambda n: gn.CreateFromGraph(n, int(n / 2) + 1, cim,init='G1')
tests = range(3,51)
experiment = ExperimentData()

instances = [
     FaultTreeExact('FT' ,'Fault Tree (exact)', experiment),
     FaultTreeMC('FTsc', 'Fault Tree (approx.)', experiment),
     ScalableBNExact('ScgRain' ,'BN (exact)', experiment),
     ScalableBN('Scbnlearn' ,'BN  (approx.)', use_cached_file=False, experimentData = experiment),
     #NaiveBNExact('NavgRain' ,'BN Exact Inference', experiment),
     #NaiveBN('Naivebnlearn' ,'BN Approx Inference', experiment),
]

r = ev.Evaluate(instances, title, tests,
                skip_engines = [],
                add_to_skip_list={
                    "ScgRain" : 7,
                    "FT":39,
                    "FTsc":39
                },
                run_file=__file__)
r.run(generator,experiment)

#Legend
# Naive BN approx  r X
# Naive BN exact   r D

# Scalable BN appraoc b X
# Scalable BN exact   b D

# Prism  sim  y X
# Prism Exact y D

# Fault Tree mc  g X
# Fault Tree exact  g D