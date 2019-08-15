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
mem_dic = {}
mem_dic['n'] = []

skip_computation = {'NveSimpleBNlearn':0,'NvSimplegRain':0,'NvSimpleBeliefePropagation':0}
stop_naive_list = ['NveSimpleBNlearn','NvSimplegRain','NvSimpleBeliefePropagation']
print("Start with 3 step 3 until 1000")
for n in range(30,1000,3):

    se = gn.SimpleExample(n,int(round(n/2+0.5)))

    if all(elm in skip_computation.keys() for elm in stop_naive_list):
        bs = se.createScalableNetwork()
        bn = bs
    else:
        bn = se.createNaiveNetwork()
        bs = se.createScalableNetwork()

    inferenceEngines = [
        {
            'is_naive': True,
            'name': 'NveSimpleBNlearn',
            'title': 'Naive Simple Example with BNLearn(R)',
            'engine': bnlearn.BNLearn(bn, driver="R", use_cached_file=False, tmp_file_name="bnlearn_tmp_R"),
            'run_parameters': lambda eng: set_repetition(eng, 20)
        },
        {
            'is_naive': True,
            'name': 'NvSimplegRain',
            'title': 'Naive Simple Example with gRain(R)',
            'engine': grain.gRain(bn, driver="R", use_cached_file=('NveSimpleBNlearn' not in skip_computation),
                                  tmp_file_name="bnlearn_tmp_R"),
            'run_parameters': lambda eng: set_repetition(eng, 20)
        },
        {
            'is_naive': True,
            'name': 'NvSimpleBeliefePropagation',
            'title': 'Naive Simple Example with pgmpy BeliefePropagation',
            'engine': belprop.BeliefePropagation(bn),
            'run_parameters': lambda eng: set_repetition(eng, 20)
        },
        {
            'is_naive': False,
            'name': 'ScSimpleBelifePropagation',
            'title': 'Scalable Simple Example with pgmpy BeliefePropagation',
            'engine': belprop.BeliefePropagation(bs),
            'run_parameters': lambda eng: set_repetition(eng, 20)
        },
        {
            'is_naive': False,
            'name': 'ScSimpleBNlearn',
            'title': 'Scalable Simple Example with BNLearn(R)',
            'engine': bnlearn.BNLearn(bs, driver="R", tmp_file_name="bnlearn_tmp_R"),
            'run_parameters': lambda eng: set_repetition(eng, 20)
        },
        {
            'is_naive': False,
            'name': 'ScSimplegRain',
            'title': 'Scalable Simple Example with gRain(R)',
            'engine': grain.gRain(bs, driver="R", use_cached_file=('ScSimpleBNlearn' not in skip_computation),
                                  tmp_file_name="bnlearn_tmp_R"),
            'run_parameters': lambda eng: set_repetition(eng, 20)
        }
    ]

    res_dic['n'].append(n)
    time_dic['n'].append(n)
    for eng in inferenceEngines:
        print(' ')
        print(eng['title'], se.k , ":" ,se.n)
        print('-' * 30 )
        print(eng['name'])
        if  eng['name'] not in skip_computation.keys() :
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

            if eng['name'] not in mem_dic:
               mem_dic[eng['name']] = []
            mem_dic[eng['name']].append(eng['engine'].meanTime)

            if eng['engine'].meanTime > 100.0:
                print("Inference time exceeded 1s: Set to ignore.")
                skip_computation[ eng['name']] = 0;
        else:
            print("Pass")
            if eng['name'] not in res_dic:
                res_dic[eng['name']] = []
            res_dic[eng['name']].append( float('inf'))
            if eng['name'] not in time_dic:
                time_dic[eng['name']] = []
            time_dic[eng['name']].append( float('inf'))
    pn.DataFrame(res_dic).to_csv('/opt/tmp/export_dataframe_res_cont.csv', index=None, header=True)
    pn.DataFrame(time_dic).to_csv('/opt/tmp/export_dataframe_time_cont.csv', index=None, header=True)


res = pn.DataFrame(res_dic)
res_time = pn.DataFrame(time_dic)
print(res)
print(res_time)

res.to_csv ('export_dataframe_res_final1.csv', index = None, header=True) #Don't forget to add '.csv' at the end of the path
res_time.to_csv ('export_dataframe_time_final1.csv', index = None, header=True) #Don't forget to add '.csv' at the end of the path














