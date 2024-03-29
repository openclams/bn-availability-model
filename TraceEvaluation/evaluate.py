import utils as ul
import machines as mh
import jobs as jb
import numpy as np
import time
import pickle
from sklearn.metrics import roc_auc_score
import BayesianNetworks.pgmpy.operators as op

from AvailabilityModels.BayesianNetPgmpy import BayesianNetModel
from CloudGraph.GraphParser import GraphParser
from Inference.pgmpy.SimpleSampling import SimpleSampling

import logging

logger = logging.getLogger()
logger.disabled = True

print('Google Trace V3 (2019) Availability Test')
print('*' * 40)


client = ul.connect()

if client:
    print('[X] Connection to Big Query')

cell='a'

machine_events = mh.load_machines(cell, client)

machines, platforms, racks = mh.get_machine_data(machine_events)

print('Num Machines:',len(machines))
print('Num racks: ', len(racks.keys()))
avg_machines_per_rack = np.mean([len(racks[r]) for r in racks.keys()])
print('Num nodes per rack', int(avg_machines_per_rack))
print('Num platforms', len(platforms.keys()), [len(platforms[r]['machines']) for r in platforms])
print('Availability.', [platforms[r]['availability'] for r in platforms])


def availability(job, machines, platforms, task_availability):
    graph = {
        'components' : [
            {
                "name": "DEDICATED",
                "availability": 0.9999
            },
            {
                "name": "G1",
                "availability": 0.99999
            },
        ]
    }

    instances = []

    used_machines = []

    for idx in job['tasks']:

        machine = job['tasks'][idx]['machine_index']

        if machine == float('nan') or machine == 0:
            # This task was not positioned yet
            # but the job has finished or failed anyway
            continue

        if machine == -1:
            # Dedicated Machine deployment
            machine = 'DEDICATED'

        if machines not in used_machines:
            used_machines.append(machine)

        instances.append({
            'host' : str(machine),
            'votes' : 1,
            "availability": task_availability
        })

    service = {
        'services': [{
            'name' : 'er',
            'init' : 'G1',
            'servers' : instances,
            'threshold': 1,
            "communication": "direct"
        }]
    }

    for m in used_machines:
        if m in machines:
            graph['components'].append(
                {
                    "name": str(m),
                    "availability": platforms[machines[m]['platform']]['availability'],
                    "type": "host"
                })
        else:
            graph['components'].append(
                {
                    "name": str(m),
                    "availability": np.mean([platforms[p]['availability'] for p in platforms]),
                    "type": "host"
                })

    graph["network"] = [
        {
            "from": "G1", "to": [str(m) for m in used_machines]
        }
    ]

    graph["dependencies"] = []

    parser = GraphParser(graph)
    G = parser.get_graph()

    # Generate BN model
    service['services'][0]['threshold'] = 1
    ba = BayesianNetModel(G, service, andNodeCPT=op.efficient_and_node,
                              orNodeCPT=op.efficient_or_node,
                              knNodeCPT=op.scalable_kn_node,
                              weightedKnNodeCPT=op.scalable_weighted_kn_node)

    service['services'][0]['threshold'] = int(len(instances)/2)+1
    bb = BayesianNetModel(G, service, andNodeCPT=op.efficient_and_node,
                          orNodeCPT=op.efficient_or_node,
                          knNodeCPT=op.scalable_kn_node,
                          weightedKnNodeCPT=op.scalable_weighted_kn_node)

    service['services'][0]['threshold'] = len(instances)
    bc = BayesianNetModel(G, service, andNodeCPT=op.efficient_and_node,
                          orNodeCPT=op.efficient_or_node,
                          knNodeCPT=op.scalable_kn_node,
                          weightedKnNodeCPT=op.scalable_weighted_kn_node)

    aa = SimpleSampling(ba.bn)
    aa.run("er")

    ab = SimpleSampling(bb.bn)
    ab.run("er")

    ac = SimpleSampling(bc.bn)
    ac.run("er")

    del bc.bn.graph
    del bc.bn.cpds
    del bc.bn
    del bc
    del ba.bn.graph
    del ba.bn.cpds
    del ba.bn
    del ba
    del bb.bn.graph
    del bb.bn.cpds
    del bb.bn
    del bb

    return (1 - aa.meanAvailability,
            1 - ab.meanAvailability,
            1 - ac.meanAvailability)


services = jb.load_services(cell, client,  offset = 0, limit = 600)

start_from_service = 26

evaluation_size = 400

for idx, service in services.iterrows():

    if idx < start_from_service:
        continue

    print('[{}] Start with service: {}_{}'.format(idx, service['name'], service['user']))

    jobs = jb.load_jobs(service, cell, client)

    if len(jobs) < 3:
        continue

    job_data = jb.prepare_jobs(jobs, service, cell)

    job_states = []
    i = 0
    for jdx, job in enumerate(job_data):
        exp = job_data[job]['event'] in [5,8]
        job_states.append(int(exp))

        if i == evaluation_size:
            break
        i = i + 1
    #job_states = [1 if job_data[job]['event'] in [5,8] else 0 for job in job_data[0:500]]

    tt = len(job_states)

    if tt > evaluation_size:
        tt = evaluation_size

    train_num = int(tt*0.5)

    print("Num of jobs {}".format(tt))
    failed_tasks = []
    for j in list(job_data.keys())[0:train_num]:

        for t in job_data[j]['tasks']:

            failed_tasks.append(int(job_data[j]['tasks'][t]['task_event'] in [5,8]))

    task_availability = 1 - float(sum(failed_tasks))/len(failed_tasks)

    print('\t-> Task Availa.:\t',task_availability)
    print('\t-> Failed Jobs.:\t', sum(job_states))

    print('Classify Training Set')

    av = []
    for jdx, job in enumerate(list(job_data.keys())[0:train_num]):
        start = time.time()
        av.append(availability(job_data[job], machines, platforms, task_availability))
        print("t[", jdx,'/',tt, "] =", time.time()-start)


    print('Classify Test Set')
    tv = []
    for jdx, job in enumerate(list(job_data.keys())[train_num:tt]):
        start = time.time()
        tv.append(availability(job_data[job], machines, platforms, task_availability))
        print("t[", jdx,'/',tt, "] =", time.time()-start)


    pickle.dump({
        'training_a': av,
        'training_c': job_states[0:train_num],
        'test_a': tv,
        'test_c': job_states[train_num:tt],
    }, open('results/{}/{}_{}'.format(cell,jb.make_safe(service['name']), jb.make_safe(service['user'])), "wb"))

    #ul.roc_plot(job_states[0:train_num], av)

    #ul.roc_plot(job_states[train_num:tt], tv)

    #print(roc_auc_score(job_states[0:train_num], [av]))

    #print(roc_auc_score(job_states[train_num:tt], [tv]))

    #break

