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
    # {
    #     'is_naive': True,
    #     'is_prism': False,
    #     'name': 'NveSimpleBNlearn',
    #     'title': 'Naive Simple Example with BNLearn(R)',
    #     'fn': lambda Bnet, skip_list :  bnlearn.BNLearn(Bnet, driver="R", use_cached_file=False, tmp_file_name="bnlearn_tmp_R"),
    #     'run_parameters': lambda eng: set_repetition(eng, 20)
    # },
    {
        'is_naive': False,
        'is_prism': False,
        'name': 'ScSimpleBNlearn',
        'title': 'Naive Simple Example with BNLearn(R)',
        'fn': lambda Bnet, skip_list :  bnlearn.BNLearn(Bnet, driver="R", use_cached_file=False, tmp_file_name="bnlearn_tmp_R"),
        'run_parameters': lambda eng: set_repetition(eng, 5)
    },
    # {
    #     'is_naive': True,
    #     'is_prism': False,
    #     'name': 'NvSimplegRain',
    #     'title': 'Naive Simple Example with gRain(R)',
    #     'fn': lambda Bnet, skip_list : grain.gRain(Bnet, driver="R", use_cached_file=('NveSimpleBNlearn' not in skip_list),tmp_file_name="bnlearn_tmp_R"),
    #     'run_parameters': lambda eng: set_repetition(eng, 1)
    # },
    # {
    #     'is_naive': False,
    #     'is_prism': False,
    #     'name': 'ScSimplegRain',
    #     'title': 'Naive Simple Example with gRain(R)',
    #     'fn': lambda Bnet, skip_list : grain.gRain(Bnet, driver="R", use_cached_file=False,tmp_file_name="bnlearn_tmp_R"),
    #     'run_parameters': lambda eng: set_repetition(eng, 5)
    # },
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
        'run_parameters': lambda eng: set_repetition(eng, 1)
    }
]
cim = "../Tests/simple_service/graph.json"
r = ev.Evaluate(inferenceEngines,'PrismEx_run3',[3,4,5,6,7,10,12,14,16,18,20,22,24,26,28,30,32,34,36,38,40,50,60,70,80,90,100,110,120],[])
r.run(lambda n: gn.PrismComparisonExample(n,int(n / 2)+1,cim))














