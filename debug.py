from AvailabilityModels.FaultTreeModel import FaultTreeModel
import numpy
import json
from CloudGraph.GraphParser import GraphParser
numpy.set_printoptions(suppress=True)
import time
from Inference.scram.Scram import Scram

cim_file_name = "Assets/simple_service/graph.json"
dep_file_name = "Assets/simple_service/deployment.json"

cim = json.load(open(cim_file_name))

parser = GraphParser(cim)

#The cloud infrastructure graph
G = parser.get_graph()
print(len(G.nodes))
#The app graph
app = json.load(open(dep_file_name))


app = {"services":[
                {
                  "name": "er",
                  "init": 'G1',
                  "servers": [ {"host":"H1","votes": 1},
                                {"host":"H2","votes": 1},
                                {"host":"H3","votes": 1},],
                  "threshold": 2,
                  "direct_communication": False
                }
              ]
            }

start = time.time()
fm = FaultTreeModel(G, app)
print("Load time ", time.time() - start)
start = time.time()
fm.build()
fm.writeXML()

sc = Scram()
sc.repetition = 1
sc.run(solution=None)
print(sc.meanAvailability)
print(sc.meanTime)

print("Build time ", time.time() - start)