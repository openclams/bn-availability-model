from AvailabilityModels.BayesianNetPgmpy import BayesianNetModel
from CloudGraph.GraphParser import GraphParser
import json
from Inference.bnlearn.BNLearn import BNLearn
from Inference.pgmpy.custom.ApproxInference import ApproxInference
import Evaluation.generators.CreateFromGraph as gn

import logging
if __name__ == '__main__':

    logger = logging.getLogger()
    logger.disabled = True

    # graph_file = "./Assets/simple_service/graph.json" # has as init=G1

    graph_file = "./Assets/large_service/graph.json"  # has as init=N1
    # deployment_file = "./Assets/simple_service/deployment.json"
    #
    # # Load the infrastructure model
    # graph = json.load(open(graph_file))
    # parser = GraphParser(graph)
    # G = parser.get_graph()
    #
    # # Load the model of the replicated system
    # service = json.load(open(deployment_file))
    #
    # # Generate BN model
    # ba = BayesianNetModel(G, service)
    # bn = ba.bn

    n = 10  # number of replicas/processes (processes are distributed in round-robin across all hosts)

    generator = gn.CreateFromGraph(n, int(n / 2) + 1, graph_file,init='N1')

    bn = generator.createScalableNetwork()


    # Execute approximate inference
    approx = BNLearn(bn)
    approx.run("er")
    print(approx.meanAvailability)
    print(approx.meanTime)


    # Execute the custom python inference algorithm
    approx = ApproxInference(bn)
    approx.run("er")
    print(approx.meanAvailability)
    print(approx.meanTime)







