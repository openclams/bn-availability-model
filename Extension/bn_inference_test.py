from Inference.bnlearn.BNLearn import BNLearn
from Inference.pgmpy.SimpleSampling import SimpleSampling
import Evaluation.generators.CreateAppFromGraph as gn
import time
import logging

logger = logging.getLogger()
logger.disabled = True

graph_file = "../Assets/simple_service/graph.json"  # has as init=N1

n = 100 # number of replicas/processes (processes are distributed in round-robin across all hosts)

generator = gn.CreateAppFromGraph(3,5, graph_file,init='FW')

bn = generator.createScalableNetwork()


start = time.time()
# Execute approximate inference
approx = SimpleSampling(bn)
approx.repetition = 1
approx.run("A")
print(approx.meanAvailability)
print("Execution time:",approx.meanTime)
print("Total time (including building):",time.time()-start)

print(" ")

# start = time.time()
# # Execute approximate inference
# approx = BNLearn(bn)
# approx.repetition = 1
# approx.run("A")
# print(approx.meanAvailability)
# print("Execution time:",approx.meanTime)
# print("Total time (including building):",time.time()-start)
#



