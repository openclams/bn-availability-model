import Evaluation.generate as gn
import Inference.bnlearn.BNLearn as bnlearn
import Inference.grain.gRain as grain
import Inference.prism.PrismExact as prismExc
import Inference.prism.PrismSim as prismSim
import Evaluation.evaluate as ev

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
        'run_parameters': lambda eng: set_repetition(eng, 20)
    },
    {
        'is_naive': True,
        'is_prism': False,
        'name': 'NvSimplegRain',
        'title': 'Naive Simple Example with gRain(R)',
        'fn': lambda Bnet, skip_list : grain.gRain(Bnet, driver="R", use_cached_file=('NveSimpleBNlearn' not in skip_list),tmp_file_name="bnlearn_tmp_R"),
        'run_parameters': lambda eng: set_repetition(eng, 1)
    },
    {
        'is_naive': False,
        'is_prism': True,
        'name': 'PrismRes',
        'title': 'Prism Model with exact results',
        'fn': lambda skip_list: prismExc.PrismExact("cim.sm"),
        'run_parameters': lambda eng: set_repetition(eng, 1)
    },
    {
        'is_naive': True,
        'is_prism': True,
        'name': 'PrismSim',
        'title': 'Prism Model with simulation',
        'fn': lambda skip_list: prismSim.PrismSim("cim.sm"),
        'run_parameters': lambda eng: set_repetition(eng, 5)
    }
]
cim = "../Tests/simple_service/graph.json"
r = ev.Evaluate(inferenceEngines,'PrismEx_1',[3,4,5,6,7],["PrismSim","PrismRes","NveSimpleBNlearn"])
r.run(lambda n: gn.PrismComparisonExample(n,int(round(n / 2 + 0.5)+1),cim) if n % 2 == 0 else gn.PrismComparisonExample(n,int(round(n / 2 + 0.5)),cim))














