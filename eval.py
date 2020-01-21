from AvailabilityModels.BayesianNetPgmpy import BayesianNetModel
from CloudGraph.GraphParser import GraphParser
import json
from AvailabilityModels.PrismModel import PrismModel
from CloudGraph.GraphGenerator import GraphGenerator
import BayesianNetworks.pgmpy.draw as dr
from Inference.bnlearn.BNLearn import BNLearn
config = [
    {"n":10,"k":9,"numRootNodes": 1, "maxLevel": 2,"degree":[3],"net":5,"epsilon":10**-3,"epsilonRate":1e-9,"maxTime":20},
    {"n": 5, "k": 3, "numRootNodes": 1, "maxLevel": 1, "degree": [3], "net": 5, "epsilon": 10 ** -1.6,"epsilonRate": 1e-8, "maxTime": 20, "sample_size": 20000}, # works
    {"n": 10, "k": 3, "numRootNodes": 2, "maxLevel": 2, "degree": [3], "net": 5, "epsilon": 10 ** -1.6, "epsilonRate": 1e-8, "maxTime": 20, "sample_size": 20000},  # works
    {"n": 10, "k": 3, "numRootNodes": 1, "maxLevel": 2, "degree": [2], "net": 5, "epsilon": 10 ** -1.6, "epsilonRate": 1e-8, "maxTime": 20, "sample_size": 20000},
    {"n": 12, "k": 8, "numRootNodes": 2, "maxLevel": 2, "degree": [3], "net": 5, "epsilon": 10 ** -1.6, "epsilonRate": 1e-8, "maxTime": 20, "sample_size": 20000},
    {"n": 12, "k": 8, "numRootNodes": 2, "maxLevel": 2, "degree": [3], "net": 5, "epsilon": 10 ** -1.6, "epsilonRate": 1e-8, "maxTime": 20, "sample_size": 20000},
    {"n": 30, "k": 15, "numRootNodes": 2, "maxLevel": 2, "degree": [3], "net": 5, "epsilon": 10 ** -1.6, "epsilonRate": 1e-8, "maxTime": 20, "sample_size": 20000},
    {"n": 40, "k": 15, "numRootNodes": 2, "maxLevel": 2, "degree": [3], "net": 5, "epsilon": 10 ** -1.6, "epsilonRate": 1e-8, "maxTime": 20, "sample_size": 20000},
    {"n": 45, "k": 15, "numRootNodes": 2, "maxLevel": 2, "degree": [3], "net": 5, "epsilon": 10 ** -1.6,"epsilonRate": 1e-8, "maxTime": 20, "sample_size": 10},
]

c = config[0]

# Init
generate = False
bn = None
pm = None
temp_file_name = "cim.sm"
prism_location = "C:\\Program Files\\prism-4.5\\"



if not generate:
    cim_file_name = "Tests/service_voting/graph.json"
    dep_file_name = "Tests/service_voting/deployment.json"

    cim = json.load(open(cim_file_name))

    parser = GraphParser(cim)

    #The cloud infrastructure graph
    G = parser.get_graph()
    #The app graph
    app = json.load(open(dep_file_name))

    ba = BayesianNetModel(G, app)
    bn = ba.bn

    approx = BNLearn(bn, use_cached_file=False, tmp_file_name="tmp/eval2", driver="R")
    approx.repetition = 30
    approx.run("er")
    print(approx.meanAvailability)
    exit()

    #Prism availablity model
    pm = PrismModel(G,app,temp_file_name,prism_location)
    pm.build()
    print(pm.simulate("er"))
    print(pm.result("er"))

else:

    gg = GraphGenerator()
    cim = gg.create_cim(net_size=c["net"],
                        numRootNodes=c["numRootNodes"],
                        ratio_random_connection=0.0,
                        max_level=c["maxLevel"],
                        degree=c["degree"],
                        min_availability=0.9990,
                        max_availability=0.99999)
    app = gg.create_app(c["n"],c["k"])
    print(cim)
    print(app)
    parser = GraphParser(cim)
    G = parser.G

    ba = BayesianNetModel(G,app)
    bn = ba.bn
    dr.plot(bn)




