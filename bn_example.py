from AvailabilityModels.BayesianNetPgmpy import BayesianNetModel
from CloudGraph.GraphParser import GraphParser
import json
from Inference.bnlearn.BNLearn import BNLearn
from Inference.grain.gRain import gRain
from Inference.pgmpy.SimpleSampling import SimpleSampling
import logging

logger = logging.getLogger()
logger.disabled = True

graph_file = "./Assets/simple_app/graph.json"
deployment_file = "./Assets/simple_app/deployment.json"

# Load the infrastructure model
graph = json.load(open(graph_file))
parser = GraphParser(graph)
G = parser.get_graph()

# Load the model of the replicated system
service = json.load(open(deployment_file))

# Generate BN model
ba = BayesianNetModel(G, service)

# Execute approximate inference
approx = SimpleSampling(ba.bn)
# select the service name from the deployment.json
approx.run("er")
print(approx.meanAvailability)

# Execute exact inference
approx = gRain(ba.bn)
approx.run("er")
print(approx.meanAvailability)








