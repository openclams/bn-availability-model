from AvailabilityModels.BayesianNetPgmpy import BayesianNetModel
from CloudGraph.GraphParser import GraphParser
import json
from Inference.bnlearn.BNLearn import BNLearn
from Inference.pgmpy.custom.ApproxInference import ApproxInference

import logging
logger = logging.getLogger()
logger.disabled = True

graph_file = "./Assets/simple_service/graph.json"
deployment_file = "./Assets/simple_service/deployment.json"

# Load the infrastructure model
graph = json.load(open(graph_file))
parser = GraphParser(graph)
G = parser.get_graph()

# Load the model of the replicated system
service = json.load(open(deployment_file))

# Generate BN model
ba = BayesianNetModel(G, service)

# Execute approximate inference
approx = BNLearn(ba.bn)
approx.run("er")
print(approx.meanAvailability)
print(approx.meanTime)

# Execute the custom python inference algorithm
approx = ApproxInference(ba.bn)
approx.run("er")
print(approx.meanAvailability)
print(approx.meanTime)







