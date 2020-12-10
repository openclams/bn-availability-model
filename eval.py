from AvailabilityModels.BayesianNetPgmpy import BayesianNetModel
from CloudGraph.GraphParser import GraphParser
import json
from AvailabilityModels.PrismModel import PrismModel
from CloudGraph.GraphGenerator import GraphGenerator
import BayesianNetworks.pgmpy.draw as dr
from Inference.bnlearn.BNLearn import BNLearn
from Inference.grain.gRain import gRain
import BayesianNetworks.pgmpy.operators as op
import  os
from dotenv import load_dotenv
import time
env_path =  '.env'
load_dotenv(dotenv_path=env_path)

config = [
    #0 service_10_9_with_45_nodes
    {"n":10,"k":9,"numRootNodes": 1, "maxLevel": 2,"degree":[3],"net":5,"epsilon":10**-3,"epsilonRate":1e-9,"maxTime":20},
    #1 service_5_3_with_18_nodes
    {"n": 5, "k": 3, "numRootNodes": 1, "maxLevel": 1, "degree": [3], "net": 5, "epsilon": 10 ** -1.6,"epsilonRate": 1e-8, "maxTime": 20, "sample_size": 20000}, # works
    #2 service_10_3_with_167_nodes
    {"n": 10, "k": 3, "numRootNodes": 2, "maxLevel": 3, "degree": [2,3], "net": 5, "epsilon": 10 ** -1.6, "epsilonRate": 1e-8, "maxTime": 20, "sample_size": 20000},  # works
    #3 service_10_3_with_738_nodes
    {"n": 10, "k": 3, "numRootNodes": 2, "maxLevel": 4, "degree": [3], "net": 10, "epsilon": 10 ** -1.6, "epsilonRate": 1e-8, "maxTime": 20, "sample_size": 20000},
    #4 service_12_8_with_4115_nodes
    {"n": 12, "k": 8, "numRootNodes": 3, "maxLevel": 4, "degree": [4], "net": 20, "epsilon": 10 ** -1.6, "epsilonRate": 1e-8, "maxTime": 20, "sample_size": 20000},
    #5 service_30_15_with_2735_nodes
    {"n": 30, "k": 15, "numRootNodes": 2, "maxLevel": 4, "degree": [4], "net": 5, "epsilon": 10 ** -1.6, "epsilonRate": 1e-8, "maxTime": 20, "sample_size": 20000},
    #6 service_100_51_with_X_nodes
    {"n": 100, "k": 51, "numRootNodes": 2, "maxLevel": 3, "degree": [5], "net": 5, "epsilon": 10 ** -1.6, "epsilonRate": 1e-8, "maxTime": 20, "sample_size": 20000},
    #7 service_200_101_with_with_1567_nodes
    {"n": 200, "k": 101, "numRootNodes": 2, "maxLevel": 3, "degree": [5], "net": 5, "epsilon": 10 ** -1.6, "epsilonRate": 1e-8, "maxTime": 20, "sample_size": 20000},
    #8 service_200_101_with_X_nodes
    {"n": 100, "k": 51, "numRootNodes": 3, "maxLevel": 8, "degree": [2,1,2,1], "net": 15, "epsilon": 10 ** -1.6, "epsilonRate": 1e-8, "maxTime": 20, "sample_size": 20000},
    #8 service_200_101_with_X_nodes
    {"n": 100, "k": 51, "numRootNodes": 3, "maxLevel": 10, "degree": [2,1,2,1,1,1,1,1,1,2], "net": 15, "epsilon": 10 ** -1.6, "epsilonRate": 1e-8, "maxTime": 20, "sample_size": 20000},

]

# Select the
c = config[8]

# Init
generate = True
bn = None
pm = None
temp_file_name = "cim.sm"
prism_location = os.getenv("PRISM_PATH")



if not generate:
    cim_file_name = "/home/bibartoo/spinoza-scripts/Tests/simple_service/graph.json"
    dep_file_name = "/home/bibartoo/spinoza-scripts/Tests/simple_service/deployment.json"

    cim = json.load(open(cim_file_name))

    parser = GraphParser(cim)

    #The cloud infrastructure graph
    G = parser.get_graph()
    print(len(G.nodes))
    #The app graph
    app = json.load(open(dep_file_name))

    # start = time.time()
    # ba = BayesianNetModel(G, app, andNodeCPT=op.efficient_and_node,orNodeCPT=op.efficient_or_node,knNodeCPT=op.scalable_kn_node)
    # bn = ba.bn
    # print("Build time ",time.time()-start)
    #
    # #dr.plot(bn)
    # approx = BNLearn(bn, use_cached_file=False, tmp_file_name="tmp/eval2", driver="R")
    # approx.repetition = 1
    # approx.run("er")
    # print(approx.meanAvailability)

    # approx = gRain(bn, use_cached_file=True, tmp_file_name="tmp/eval2", driver="R")
    # approx.repetition = 1
    # approx.run("er")
    # print(approx.meanAvailability)
    #

    #Prism availablity model
    start = time.time()
    pm = PrismModel(G,app,temp_file_name,prism_location,os.getenv("PRISM_LOCATION"))
    print("Load time ", time.time() - start)
    start = time.time()
    pm.build()
    print("Build time ", time.time() - start)
    # print(pm.simulate(""))
    # print(pm.result(""))

else:

    gg = GraphGenerator()
    cim = gg.create_cim(net_size=c["net"],
                        numRootNodes=c["numRootNodes"],
                        ratio_random_connection=0.05,
                        max_level=c["maxLevel"],
                        degree=c["degree"],
                        min_availability=0.9990,
                        max_availability=0.99999)
    app = gg.create_app(c["n"],c["k"])
    #print(cim)
    #print(app)
    # parser = GraphParser(cim)
    # G = parser.G
    # print(len(G.nodes))
    # ba = BayesianNetModel(G,app)
    # bn = ba.bn
    # #dr.plot(bn)
    # approx = BNLearn(bn, use_cached_file=False, tmp_file_name="tmp/eval2", driver="R")
    # approx.repetition = 30
    # approx.run("er")
    # print(approx.meanAvailability)
    # pm = PrismModel(G, app, temp_file_name, prism_location)
    # pm.build()
    # print(pm.simulate("er"))
    # print(pm.result("er"))





