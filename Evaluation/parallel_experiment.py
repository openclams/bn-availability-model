import Evaluation.generate as gn
import Inference.bnlearn.BNLearn as bnlearn
import Inference.grain.gRain as grain
import Inference.pgmpy.BeliefePropagation as belprop
import Evaluation.evaluate as ev

def set_repetition(eng, n, c=None):
    eng.repetition = n
    return c

#('NveSimpleBNlearn' not in skip_computation)
inferenceEngines = [
    {
        'is_naive': True,
        'name': 'NveSimpleBNlearn',
        'title': 'Naive Simple Example with BNLearn(R)',
        'fn': lambda Bnet, skip_list :  bnlearn.BNLearn(Bnet, driver="R", use_cached_file=False, tmp_file_name="bnlearn_tmp_R"),
        'run_parameters': lambda eng: set_repetition(eng, 20)
    },
    {
        'is_naive': True,
        'name': 'NvSimplegRain',
        'title': 'Naive Simple Example with gRain(R)',
        'fn': lambda Bnet, skip_list : grain.gRain(Bnet, driver="R", use_cached_file=('NveSimpleBNlearn' not in skip_list),tmp_file_name="bnlearn_tmp_R"),
        'run_parameters': lambda eng: set_repetition(eng, 20)
    },
    {
        'is_naive': True,
        'name': 'NvSimpleBeliefePropagation',
        'title': 'Naive Simple Example with pgmpy BeliefePropagation',
        'fn': lambda Bnet, skip_list : belprop.BeliefePropagation(Bnet),
        'run_parameters': lambda eng: set_repetition(eng, 20)
    },
    {
        'is_naive': False,
        'name': 'ScSimpleBelifePropagation',
        'title': 'Scalable Simple Example with pgmpy BeliefePropagation',
        'fn': lambda Bnet, skip_list : belprop.BeliefePropagation(Bnet),
        'run_parameters': lambda eng: set_repetition(eng, 20)
    },
    {
        'is_naive': False,
        'name': 'ScSimpleBNlearn',
        'title': 'Scalable Simple Example with BNLearn(R)',
        'fn': lambda Bnet, skip_list :bnlearn.BNLearn(Bnet, driver="R",use_cached_file=False, tmp_file_name="bnlearn_tmp_R"),
        'run_parameters': lambda eng: set_repetition(eng, 20)
    },
    {
        'is_naive': False,
        'name': 'ScSimplegRain',
        'title': 'Scalable Simple Example with gRain(R)',
        'fn': lambda Bnet, skip_list : grain.gRain(Bnet, driver="R", use_cached_file=('ScSimpleBNlearn' not in skip_list), tmp_file_name="bnlearn_tmp_R"),
        'run_parameters': lambda eng: set_repetition(eng, 20)
    }
]

r = ev.Evaluate(inferenceEngines,'ParallelEx_3_30_3',range(3,31,3),[])
r.run(lambda n: gn.ParallelExample(n,int(round(n / 2 )+1)) if n % 2 == 0 else gn.ParallelExample(n,int(round(n / 2 + 0.5))))




