import Evaluation.generators.CreateFromGraph as gn
import Evaluation.evaluate as ev
from Evaluation.executors.ExperimentData import ExperimentData
from Evaluation.executors.FaultTreeExact import FaultTreeExact
from Evaluation.executors.FaultTreeMC import FaultTreeMC
from Evaluation.executors.FaultTreeRE import FaultTreeRE
from Evaluation.executors.ScalableBNExact import ScalableBNExact
from Evaluation.executors.ScalableBN import ScalableBN

title = "Simple Service Experiment "
cim = "../../Assets/simple_service/graph.json"
generator = lambda n: gn.CreateFromGraph(n, int(n / 2) + 1, cim,init='FW')
tests = range(3,50)
experiment = ExperimentData()

instances = [
     FaultTreeExact('FT' ,'Fault Tree (exact)', experiment),
     FaultTreeMC('FTsc', 'Fault Tree (approx.)', experiment),
     #FaultTreeRE('FTre', 'Fault Tree (approx.)', experiment),
     ScalableBNExact('ScgRain' ,'BN (exact)', experiment),
     ScalableBN('Scbnlearn' ,'BN  (approx.)', use_cached_file=False, experimentData = experiment)
]

r = ev.Evaluate(instances, title, tests,
                skip_engines = [],
                add_to_skip_list={
                    "ScgRain" : 6,
                    "FT":35,
                    "FTsc":35
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