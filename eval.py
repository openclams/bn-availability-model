from AvailabilityModels.BayesianNetPgmpy import BayesianNetModel
#from AvailabilityModels.BayesianNetPyAgrum import BayesianNetModel
from AvailabilityModels.PrismModel import PrismModel
from CloudGraph.GraphParser import GraphParser
import json
import time
from rpy2.robjects.packages import importr
import numpy

from Inference.pyagrum.WeightedSampling import WeightedSamplingApprox
numpy.set_printoptions(suppress=True)

importr('bnlearn')
importr('gRain')


def eval_models(bn,pm,G,c):

    print("Num. Components:",len(G.V))
    print("Num. BN nodes:",len(bn.nodes()))


    solution = "er"

    # print("BIF BMLearn")
    # approx = BNLearnApprox(bn, use_cached_file=False, tmp_file_name="tmp/testeval2.bif", driver="BIF")
    # approx.repetition = 30
    # approx.run(solution)

    # print("R BMLearn")
    # approx = BNLearnApprox(bn, use_cached_file=False, tmp_file_name="tmp/eval2", driver="R")
    # approx.repetition = 30
    # approx.run(solution)
    #
    # print(approx.availabilityData)

    print("WeightedSamplingApprox")
    approx = WeightedSamplingApprox(bn)
    approx.repetition = 1
    approx.run(solution,c)

    print(approx.availabilityData)

    # print("GumGibbisSamplingApprox")
    # approx = GumGibbisSamplingApprox(bn)
    # approx.repetition = 30
    # approx.run(solution,c)
    #
    # print(approx.availabilityData)
    #
    # print("GumImportanceSamplingApprox")
    # approx = GumImportanceSamplingApprox(bn)
    # approx.repetition = 30
    # approx.run(solution,c)
    #
    # print(approx.availabilityData)


    # print("BIF rGain")
    # approx = gRainExact(bn, use_cached_file=False, tmp_file_name="testeval2.bif", driver="BIF")
    # approx.run(solution)

    exit(1)
    start = time.time()
    print("PrimsSimulation(bn)\t\t", pm.simulate(),"Time",time.time()-start)
    start = time.time()
    print("PrimsResult(bn)\t", pm.result(), "Time", time.time() - start)
# -----------------------------------------------------------------




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

c = config[8]

# Init
generate = False
bn = None
pm = None
temp_file_name = "cim.sm"
prism_location = "C:\\Program Files\\prism-4.5\\"

if not generate:
    cim_file_name = "Tests/graph.json"
    dep_file_name = "Tests/deployment_1.json"
    structure = "ctmc"

    cim = json.load(open(cim_file_name))

    parser = GraphParser(cim)

    #The cloud infrastructure graph
    G = parser.G
    #The app graph
    app = json.load(open(dep_file_name))

    #BN availability model
    ba = BayesianNetModel(G,app)#knNodeCPT=scalable_kn_node,orNodeCPT=efficient_or_node,andNodeCPT=efficient_and_node)
    bn = ba.bn

    #Prism availablity model
    pm = PrismModel(G,app,"ctmc",temp_file_name,prism_location)
    pm.buildCTMCPrismModel()

    eval_models(bn, pm, G,c)
# else:
#
#     #success = False
#     #while not success:
#
# # try:
#     gg = GraphGenerator()
#     cim = gg.create_cim(net_size=c["net"],numRootNodes=c["numRootNodes"], ratio_random_connection=0.0, max_level=c["maxLevel"], degree=c["degree"],min_availability=0.9990, max_availability=0.99999)
#     app = gg.create_app(c["n"],c["k"])
#
#     parser = GraphParser(cim)
#     G = parser.G
#
#     ba = BayesianNetModel(G,app,knNodeCPT=scalable_kn_node,orNodeCPT=efficient_or_node,andNodeCPT=efficient_and_node)
#     bn = ba.bn
#
#     pm = PrismModel(G,app,"ctmc",temp_file_name,prism_location)
#     pm.buildCTMCPrismModel()
#     success = True
#         # except Exception as inst:
#         #     print(inst)
#         #     success = False
#         #     exit(1)
#
#     eval_models(bn,pm, G, c)


