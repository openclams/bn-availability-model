import Evaluation.generators.CreateFromGraph as gn
import Evaluation.evaluate as ev
from Evaluation.executors.ExperimentData import ExperimentData
from Evaluation.executors.FaultTreeExact import FaultTreeExact
from Evaluation.executors.FaultTreeMC import FaultTreeMC
from Evaluation.executors.ScalableBNExact import ScalableBNExact
from Evaluation.executors.ScalableBN import ScalableBN

title = "Large Service Experiment "
cim = "../../Assets/large_service/graph.json"
generator = lambda n: gn.CreateFromGraph(n, int(n / 2) + 1, cim,init='N1')
tests =  [3,5,7]
experiment = ExperimentData()

instances = [
     FaultTreeExact('FT' ,'Fault Tree (exact)', experiment),
     FaultTreeMC('FTre', 'Fault Tree (approx.)', experiment),
     #ScalableBNExact('ScgRain' ,'BN (exact)', experiment),
     ScalableBN('Scbnlearn' ,'BN  (approx.)', use_cached_file=False, experimentData = experiment)
]

r = ev.Evaluate(instances, title, tests,
                skip_engines = [],
                add_to_skip_list={
                    #"ScgRain" : 6,
                    #"FT":10,
                    #"FTsc":10
                },
                run_file=__file__)
r.run(generator,experiment)
#r.render('Second17.03.2021 15-04-02')
#Legend
# Naive BN approx  r X
# Naive BN exact   r D

# Scalable BN appraoc b X
# Scalable BN exact   b D

# Prism  sim  y X
# Prism Exact y D

# Fault Tree mc  g X
# Fault Tree exact  g D