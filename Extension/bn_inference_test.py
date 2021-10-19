from Inference.bnlearn.BNLearn import BNLearn
from Inference.pgmpy.SimpleSampling import SimpleSampling
import Evaluation.generators.CreateFromGraph as gn
import time
import logging

logger = logging.getLogger()
logger.disabled = True

graph_file = "./Assets/large_service/graph.json"  # has as init=N1

n = 100 # number of replicas/processes (processes are distributed in round-robin across all hosts)

generator = gn.CreateFromGraph(n, int(n / 2) + 1, graph_file,init='N1')

bn = generator.createScalableNetwork()

start = time.time()
# Execute approximate inference
approx = SimpleSampling(bn)
approx.repetition = 1
approx.run("er")
print(approx.meanAvailability)
print("Execution time:",approx.meanTime)
print("Total time (including building):",time.time()-start)

print(" ")

start = time.time()
# Execute approximate inference
approx = BNLearn(bn)
approx.repetition = 1
approx.run("er")
print(approx.meanAvailability)
print("Execution time:",approx.meanTime)
print("Total time (including building):",time.time()-start)




