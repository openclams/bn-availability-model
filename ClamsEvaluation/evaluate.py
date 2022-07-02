import logging

import numpy
import pickle

from ClamsEvaluation.ExhaustiveSearch import exhaustive_search
from Inference.pgmpy.SimpleSampling import SimpleSampling

logger = logging.getLogger()
logger.disabled = True
import requests
import json
import BayesianNetworks.pgmpy.operators as op
from AvailabilityModels.BayesianNetPgmpy import BayesianNetModel
from CloudGraph.GraphParser import GraphParser
from CloudGraph.Host import Host
from HarmonySearch.Candidate import Candidate
from HarmonySearch.CHSearch import CHSearch
from typing import List


import time
import pandas as pd

import sys

# taskset -c 0-7 befehl
root_dir = './'

cim = json.load(open(root_dir+'Assets/simple_service/graph.json'))
num_hs_instances = 30
num_inference_threads = 1
n = 3
k = 2
availability_threshold=0.90

parser = GraphParser(cim)

G = parser.get_graph()

hosts = [h for h in G.nodes.values() if isinstance(h, Host)]

build_app_model_time = []
build_bn_model_time = []
inference_time = []

def get_leaves(component):
    url = "http://localhost/api/component/" + str(component['id']) + '/leafs'
    resp = requests.get(url=url)

    data = resp.json()

    return data


def get_struct(component):
    return {
        'availability': 0,
        'cost': 0,
        'component': component
    }


def loss_function(candidates: List[Candidate]) -> float:
    global G
    global hosts
    global n
    global k
    global availability_threshold

    idx = 0

    start = time.time()

    services = []

    app_graph = []

    current_host = 0

    total_cost = 0.0

    for candidate in candidates:

        component = candidate.value['component']

        cost = 10

        if len(component['costs']) >= 1:

            cost = float(component['costs'][0]['cost'])

        total_cost += cost

        # name_attribute = [attr for attr in component['attributes'] if attr['name'] == 'name'][0]

        name = "s_" + str(idx)

        idx += 1

        app_graph.append(name)

        servers = []

        av = [attr for attr in component['attributes'] if attr['id'] == '_availability'][0]['value']

        for i in range(n):
            servers.append({"host": hosts[current_host].name,
                            "votes": 1,
                            "availability" : av})

            current_host = (current_host + 1) % len(hosts)

        services.append({
            "name": name,
            "init": ['N1'],
            "servers": servers,
            "threshold": k,
            "direct_communication": False
        })

        final_node = name

    app = {"services": services}

    if len(app_graph) > 1:

        final_node = 'A'

        topology = []

        for i in range(1, len(app_graph)):
            topology.append({"from": app_graph[i - 1], "to": app_graph[i]})

        app["application"] = {
            "init": "N1",
            "topology": topology
        }

    end = time.time()

    build_app_model_time.append(end-start)

    start = time.time()

    ba = BayesianNetModel(G, app,andNodeCPT=op.efficient_and_node,
                          orNodeCPT=op.efficient_or_node,
                          knNodeCPT=op.scalable_kn_node,
                          weightedKnNodeCPT=op.scalable_weighted_kn_node)
    bn = ba.bn

    end = time.time()

    build_bn_model_time.append(end-start)

    start = time.time()

    # Execute approximate inference
    approx = SimpleSampling(bn,num_inference_threads)

    approx.run(final_node)

    end = time.time()

    inference_time.append(end-start)

    del bn

    candidates[0].value['availability'] = approx.meanAvailability

    if approx.meanAvailability > availability_threshold:

        candidates[0].value['cost'] = total_cost

        return total_cost

    else:

        candidates[0].value['cost'] = float('inf')

        return float('inf')


def evaluate(file_name, iterations):

    global build_app_model_time

    global build_bn_model_time

    global inference_time

    global num_hs_instances

    inference_time = []

    build_app_model_time = []

    build_bn_model_time = []

    with open(file_name) as jsonFile:
        project = json.load(jsonFile)

        model = project['model']

        components = model['components']

        candidate_space: List[List[Candidate]] = []

        search_space_size = 1

        build_search_space = time.time()
        for component in components:
            leaves = get_leaves(component)

            print(component['name'],len(leaves))

            search_space_size *= len(leaves)

            candidate_space.append([Candidate(get_struct(l)) for l in leaves])
        build_search_space = time.time() - build_search_space

        # pickle.dump(candidate_space, open("save.p", "wb"))
        #
        # candidate_space = pickle.load(open("save.p", "rb"))
        # print([len(c) for c in candidate_space])

        start = time.time()
        print("Start HS - ",end="")
        imp = CHSearch(candidate_space=candidate_space, loss_function=loss_function,
                     termination=iterations,
                     harmony_memory_size=10,
                     harmony_memory_consideration_rate=0.85,
                     pitch_adjustment_rate=0.05,
                     num_processes=num_hs_instances)

        #imp = imp.run()

        end = time.time()
        print("Finished ",str(end-start),'s -',end="")
        # Re-evaluate the loss function to get the availability and cost values
        ## We need this solution because of the concurency problem
        loss_function(imp.candidates)

        solution = [v.value for v in imp.candidates]

        print("Start EX - ", end="")
        # Exhaustive search
        if  search_space_size < 50000000:
            ex_start = time.time()
            min_loss =  exhaustive_search(candidate_space, loss_function)
            exTime = time.time() - ex_start
        else:
            min_loss = float('inf')
            exTime = float('inf')
        print("Finished ", str(exTime), 's with lmin=',str(min_loss))

        data = {
            'NumComponents' : len(components),
            'SearchSpaceSize' : search_space_size,
            'TotalComputeTime': end-start,
            'HSIterations' : iterations,
            'Availability': solution[0]['availability'],
            'Cost': solution[0]['cost'],
            'Loss': imp.loss,
            'MeanSingleInferenceTime' : numpy.mean(inference_time),
            'StdSingleInferenceTime': numpy.std(inference_time),
            'MeanSingleBuildBNTime' : numpy.mean(build_bn_model_time),
            'StdSingleBuildBNTime' : numpy.std(build_bn_model_time),
            'MeanSingleBuildAppTime' : numpy.mean(build_app_model_time),
            'StdSingleBuildAppTime' : numpy.std(build_app_model_time),
            'BuildSearchSpaceTime': build_search_space,
            'MinLoss': min_loss,
            'ExTime':exTime,

        }

        return pd.DataFrame(data,index=[0])


if __name__ == '__main__':

    pd.set_option('display.max_columns', None)

    pd.set_option('display.expand_frame_repr', False)

    for i in [10,9]:

        main_df = pd.DataFrame()

        for it in [10000]:

            df = evaluate(root_dir+"ClamsEvaluation/TestCases/{}.json".format(i), it)

            #print(df)

            df.to_csv(root_dir+'ClamsEvaluation/small_multi_raw_3/{}_{}.csv'.format(i,it),index=False)

            main_df = main_df.append(df, ignore_index=True)

        print(main_df)

        main_df.to_csv(root_dir+'ClamsEvaluation/small_multi_final_3/{}.csv'.format(i), index=False)

    sys.stdout.close()