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
for n in range(3,21):
    se = gn.ParallelExample(n,int(round(n/2+0.5)))

    bnp = se.createNaiveNetwork()
    bsp = se.createScalableNetwork()

    se = gn.SerialExample(n, int(round(n / 2 + 0.5)))

    bns = se.createNaiveNetwork()
    bss = se.createScalableNetwork()

    inferenceEngines = [
            {
                'name' : 'NvParallelBNlearn',
                'title' : 'Naive Parallel Example with BNLearn(R)',
                'engine' : bnlearn.BNLearn(bnp,driver="R",use_cached_file=False,tmp_file_name = "bnlearn_tmp_pase_R"),
                'run_parameters' : lambda eng: set_repetition(eng,20)
            },
            {
                'name': 'NvParallelgRain',
                'title': 'Naive Parallel Example with gRain(R)',
                'engine': grain.gRain(bnp,driver="R",use_cached_file=True,tmp_file_name = "bnlearn_tmp_pase_R"),
                'run_parameters':  lambda eng: set_repetition(eng,20)
            },
            {
                'name': 'NvParallelBeliefePropagation',
                'title': 'Naive Parallel Example with ppmpy BeliefePropagation',
                'engine': belprop.BeliefePropagation(bnp), # dummy.Dummy(bn),#(n > 23)? belprop.BeliefePropagation(bn): dummy.Dummy(bn),
                'run_parameters':   lambda eng: set_repetition(eng,20)
            },
            {
                'name': 'ScParallelBelifePropagation',
                'title': 'Scalable Parallel Example with ppmpy BeliefePropagation',
                'engine': belprop.BeliefePropagation(bsp),
                'run_parameters':   lambda eng: set_repetition(eng,20)
            },
            {
                'name': 'ScParallelBNlearn',
                'title': 'Scalable Parallel Example with BNLearn(R)',
                'engine': bnlearn.BNLearn(bsp,driver="R",tmp_file_name = "bnlearn_tmp_pase_R"),
                'run_parameters':  lambda eng: set_repetition(eng,20)
            },
            {
                'name': 'ScParallelgRain',
                'title': 'Scalable Parallel Example with gRain(R)',
                'engine': grain.gRain(bsp,driver="R",use_cached_file=True,tmp_file_name = "bnlearn_tmp_pase_R"),
                'run_parameters':   lambda eng: set_repetition(eng,20)
            },
            {
                'name': 'NvSerialBNlearn',
                'title': 'Naive Serial Example with BNLearn(R)',
                'engine': bnlearn.BNLearn(bns, driver="R", use_cached_file=False, tmp_file_name="bnlearn_tmp_pase_R"),
                'run_parameters': lambda eng: set_repetition(eng, 20)
            },
            {
                'name': 'NvSerialgRain',
                'title': 'Naive Serial Example with gRain(R)',
                'engine': grain.gRain(bns, driver="R", use_cached_file=True, tmp_file_name="bnlearn_tmp_pase_R"),
                'run_parameters': lambda eng: set_repetition(eng, 20)
            },
            {
                'name': 'NvSerialBeliefePropagation',
                'title': 'Naive Serial Example with ppmpy BeliefePropagation',
                'engine': belprop.BeliefePropagation(bns), #dummy.Dummy(bns),  # (n > 23)? belprop.BeliefePropagation(bn): dummy.Dummy(bn),
                'run_parameters': lambda eng: set_repetition(eng, 20)
            },
            {
                'name': 'ScSerialBelifePropagation',
                'title': 'Scalable Serial Example with ppmpy BeliefePropagation',
                'engine': belprop.BeliefePropagation(bss),
                'run_parameters': lambda eng: set_repetition(eng, 20)
            },
            {
                'name': 'ScSerialBNlearn',
                'title': 'Scalable Serial Example with BNLearn(R)',
                'engine': bnlearn.BNLearn(bss, driver="R", tmp_file_name="bnlearn_tmp_pase_R"),
                'run_parameters': lambda eng: set_repetition(eng, 20)
            },
            {
                'name': 'ScSerialgRain',
                'title': 'Scalable Serial Example with gRain(R)',
                'engine': grain.gRain(bss, driver="R", use_cached_file=True, tmp_file_name="bnlearn_tmp_pase_R"),
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
            eng['engine'].run(se.solution,run_param)
        else:
            eng['engine'].run(se.solution)
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














