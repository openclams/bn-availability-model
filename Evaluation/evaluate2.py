import Evaluation.generate as gn
import pandas as pn

import Inference.bnlearn.BNLearn as bnlearn
import Inference.grain.gRain as grain
import Inference.pgmpy.BeliefePropagation as belprop
import Inference.Dummy as dummy

def set_repetition(eng, n, c=None):
    eng.repetition = n
    return c

res_dic = {}
res_dic['n'] = []
time_dic = {}
time_dic['n'] = []
for n in range(3,27):
    se = gn.ParallelExample(n,int(round(n/2+0.5)))

    bnp = se.createNaiveNetwork()
    bsp = se.createScalableNetwork()

    se = gn.SerialExampleExample(n, int(round(n / 2 + 0.5)))

    bns = se.createNaiveNetwork()
    bss = se.createScalableNetwork()

    inferenceEngines = [
            {
                'name' : 'NvParallelBNlearn',
                'title' : 'Naive Parallel Example with BNLearn(R)',
                'engine' : bnlearn.BNLearn(bn,driver="R",use_cached_file=False,tmp_file_name = "bnlearn_tmp_pase_R"),
                'run_parameters' : lambda eng: set_repetition(eng,20)
            },
            {
                'name': 'NvParallelgRain',
                'title': 'Naive Parallel Example with gRain(R)',
                'engine': grain.gRain(bn,driver="R",use_cached_file=True,tmp_file_name = "bnlearn_tmp_pase_R"),
                'run_parameters':  lambda eng: set_repetition(eng,20)
            },
            {
                'name': 'NvParallelBeliefePropagation',
                'title': 'Naive Parallel Example with ppmpy BeliefePropagation',
                'engine': dummy.Dummy(bn),#(n > 23)? belprop.BeliefePropagation(bn): dummy.Dummy(bn),
                'run_parameters':   lambda eng: set_repetition(eng,20)
            },
            {
                'name': 'ScParallelBelifePropagation',
                'title': 'Scalable Parallel Example with ppmpy BeliefePropagation',
                'engine': belprop.BeliefePropagation(bs),
                'run_parameters':   lambda eng: set_repetition(eng,20)
            },
            {
                'name': 'ScParallelBNlearn',
                'title': 'Scalable Parallel Example with BNLearn(R)',
                'engine': bnlearn.BNLearn(bs,driver="R",tmp_file_name = "bnlearn_tmp_pase_R"),
                'run_parameters':  lambda eng: set_repetition(eng,20)
            },
            {
                'name': 'ScParallelRain',
                'title': 'Scalable Parallel Example with gRain(R)',
                'engine': grain.gRain(bs,driver="R",use_cached_file=True,tmp_file_name = "bnlearn_tmp_pase_R"),
                'run_parameters':   lambda eng: set_repetition(eng,20)
            },
        {
            'name': 'NvSerialBNlearn',
            'title': 'Naive Serial Example with BNLearn(R)',
            'engine': bnlearn.BNLearn(bn, driver="R", use_cached_file=False, tmp_file_name="bnlearn_tmp_pase_R"),
            'run_parameters': lambda eng: set_repetition(eng, 20)
        },
        {
            'name': 'NvParallelgRain',
            'title': 'Naive Parallel Example with gRain(R)',
            'engine': grain.gRain(bn, driver="R", use_cached_file=True, tmp_file_name="bnlearn_tmp_pase_R"),
            'run_parameters': lambda eng: set_repetition(eng, 20)
        },
        {
            'name': 'NvParallelBeliefePropagation',
            'title': 'Naive Parallel Example with ppmpy BeliefePropagation',
            'engine': dummy.Dummy(bn),  # (n > 23)? belprop.BeliefePropagation(bn): dummy.Dummy(bn),
            'run_parameters': lambda eng: set_repetition(eng, 20)
        },
        {
            'name': 'ScParallelBelifePropagation',
            'title': 'Scalable Parallel Example with ppmpy BeliefePropagation',
            'engine': belprop.BeliefePropagation(bs),
            'run_parameters': lambda eng: set_repetition(eng, 20)
        },
        {
            'name': 'ScParallelBNlearn',
            'title': 'Scalable Parallel Example with BNLearn(R)',
            'engine': bnlearn.BNLearn(bs, driver="R", tmp_file_name="bnlearn_tmp_pase_R"),
            'run_parameters': lambda eng: set_repetition(eng, 20)
        },
        {
            'name': 'ScParallelRain',
            'title': 'Scalable Parallel Example with gRain(R)',
            'engine': grain.gRain(bs, driver="R", use_cached_file=True, tmp_file_name="bnlearn_tmp_pase_R"),
            'run_parameters': lambda eng: set_repetition(eng, 20)
        }
    ]

    res_dic['n'].append(n)
    time_dic['n'].append(n)
    for eng in inferenceEngines:
        print(' ')
        print(eng['title'], se.n, "/",se.k)
        print('-' * 30 )
        print(eng['name'])
        run_param = eng['run_parameters'](eng['engine'])
        if run_param is not None:
            eng['engine'].run('K',run_param)
        else:
            eng['engine'].run('K')
        print('Availability',eng['engine'].meanAvailability)
        print('Time',eng['engine'].meanTime)

        if eng['name'] not in res_dic:
            res_dic[eng['name']] = []
        res_dic[eng['name']].append(eng['engine'].meanAvailability)

        if eng['name'] not in time_dic:
            time_dic[eng['name']] = []
        time_dic[eng['name']].append(eng['engine'].meanTime)

res = pn.DataFrame(res_dic)
res_time = pn.DataFrame(time_dic)
print(res)
print(res_time)

export_csv = res.to_csv ('export_dataframe_pase_res2.csv', index = None, header=True) #Don't forget to add '.csv' at the end of the path
export_csv = res_time.to_csv ('export_dataframe_pase_time2.csv', index = None, header=True) #Don't forget to add '.csv' at the end of the path














