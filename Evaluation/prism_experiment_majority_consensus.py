import Evaluation.generate as gn
import Inference.bnlearn.BNLearn as bnlearn
import Inference.grain.gRain as grain
import Inference.prism.PrismExact as prismExc
import Inference.prism.PrismSim as prismSim
import Evaluation.evaluate as ev
import os

def set_repetition(eng, n, c=None):
    eng.repetition = n
    return c

#('NveSimpleBNlearn' not in skip_computation)
inferenceEngines = [
    {
        'is_naive': True,
        'is_prism': False,
        'name': 'NveSimpleBNlearn',
        'title': 'Naive Simple Example with BNLearn(R)',
        'fn': lambda Bnet, skip_list :  bnlearn.BNLearn(Bnet, driver="R", use_cached_file=False, tmp_file_name="bnlearn_tmp_R"),
        'run_parameters': lambda eng: set_repetition(eng, 10)
    },
    {
        'is_naive': True,
        'is_prism': False,
        'name': 'NvSimplegRain',
        'title': 'Naive Simple Example with gRain(R)',
        'fn': lambda Bnet, skip_list : grain.gRain(Bnet, driver="R", use_cached_file=('NveSimpleBNlearn' not in skip_list),tmp_file_name="bnlearn_tmp_R"),
        'run_parameters': lambda eng: set_repetition(eng, 10)
    },
    {
        'is_naive': False,
        'is_prism': True,
        'name': 'PrismRes',
        'title': 'Prism Model with exact results',
        'fn': lambda skip_list: prismExc.PrismExact("cim.sm",prism_location= os.getenv("PRISM_PATH"),prism_bin_path= os.getenv("PRISM_LOCATION")),
        'run_parameters': lambda eng: set_repetition(eng, 4)
    },
    {
        'is_naive': True,
        'is_prism': True,
        'name': 'PrismSim',
        'title': 'Prism Model with simulation',
        'fn': lambda skip_list: prismSim.PrismSim("cim.sm",prism_location= os.getenv("PRISM_PATH"),prism_bin_path= os.getenv("PRISM_LOCATION")),
        'run_parameters': lambda eng: set_repetition(eng, 4)
    }
]
cim = "../Tests/simple_service/graph.json"
r = ev.Evaluate(inferenceEngines,'Prism_validate_majority_consensus',range(3,4),[],add_to_skip_list={
    "NvSimplegRain" : 5 # Stop the bn exact algorithm after n=5,
}, run_file=__file__)
r.run(lambda n: gn.PrismComparisonExample(n,int(n / 2)+1,cim))














