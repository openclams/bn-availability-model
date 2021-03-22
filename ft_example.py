from AvailabilityModels.FaultTreeModel import FaultTreeModel
from CloudGraph.GraphParser import GraphParser
import json
from FaultTrees.MefWriter import MefWriter
from Inference.scram.Scram import Scram

graph_file = "./Assets/simple_service/graph.json"
deployment_file = "./Assets/simple_service/deployment.json"

# Load the infrastructure model
graph = json.load(open(graph_file))
parser = GraphParser(graph)
G = parser.get_graph()

# Load the model of the replicated system
service = json.load(open(deployment_file))

# Generate FT model
fm = FaultTreeModel(G, service)
fm.build()
MefWriter(fm.ft,temp_file_name = "ft_mef.xml")

# Execute approximate assessment
approx = Scram(tmp_file_name = "ft_mef.xml",method='bdd')
# select the service name from the deployment.json
approx.run("er")
print(approx.meanAvailability)

# Execute exact assessment
approx = Scram(tmp_file_name = "ft_mef.xml",method='mcub')
approx.run("er")
print(approx.meanAvailability)



