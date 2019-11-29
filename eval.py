from AvailabilityModels.BayesianNetPgmpy import BayesianNetModel
from AvailabilityModels.PrismModel import PrismModel
from CloudGraph.GraphParser import GraphParser
from BayesianNetworks.pgmpy.writers import writeBIF
import json

import networkx as nx
from networkx.drawing.nx_agraph import write_dot, graphviz_layout
import matplotlib.pyplot as plt

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
    cim_file_name = "Tests/graph.json"
    dep_file_name = "Tests/deployment.json"

    cim = json.load(open(cim_file_name))

    parser = GraphParser(cim)

    #The cloud infrastructure graph
    G = parser.get_graph()
    #The app graph
    app = json.load(open(dep_file_name))

    #BN availability model
    ba = BayesianNetModel(G,app)#knNodeCPT=scalable_kn_node,orNodeCPT=efficient_or_node,andNodeCPT=efficient_and_node)
    bn = ba.bn
    
    #writeBIF(bn,"test.bif")

    #Prism availablity model
    #pm = PrismModel(G,app,"ctmc",temp_file_name,prism_location)
    #pm.buildCTMCPrismModel()





