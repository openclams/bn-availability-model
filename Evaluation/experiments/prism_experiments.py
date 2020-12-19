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

title = "Large Test"
cim = "../../Assets/simple_service/graph.json"
#cim = "/home/bibartoo/spinoza-scripts/Assets/service_100_51_X_nodes/graph.json"
#cim = "/home/bibartoo/spinoza-scripts/Assets/service_10_9_with_45_nodes/graph.json"
#cim = "../../Assets/graph.json"
generator = lambda n: gn.CreateFromGraph(n, int(n / 2) + 1, cim,init='N1')
tests =range(3,100,2)
experiment = ExperimentData()

instances = [
     #FaultTreeExact('FT' ,'Fault Tree with BDD', experiment),
     #FaultTreeMC('FTsc', 'Fault Tree with MCUB', experiment),
     #ScalableBNExact('ScgRain' ,'BN Exact Inference', experiment),
     ScalableBN('Scbnlearn' ,'BN Approx Inference', experiment),
     #NaiveBNExact('NavgRain' ,'BN Exact Inference', experiment),
     #NaiveBN('Naivebnlearn' ,'BN Approx Inference', experiment),
     # PrismExact('PrismEx', 'Prism Exact', experiment),
     # PrismSim('PrismSim', 'Prism Sim', experiment),
]

r = ev.Evaluate(instances, title, tests,
                skip_engines = [],
                add_to_skip_list={
                    "ScgRain" : 9,
                    "FT":41,
                    "FTsc":41
                },
                run_file=__file__)
r.run(generator,experiment)


# Naive BN approx  r X
# Naive BN exact   r D

# Scalable BN appraoc b X
# Scalable BN exact   b D

# Prism  sim  y X
# Prism Exact y D

# Fault Tree mc  g X
# Fault Tree exact  g D