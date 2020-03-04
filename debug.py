from pgmpy.models import BayesianModel
from pgmpy.factors.discrete import TabularCPD
import BayesianNetworks.pgmpy.operators as ops
import numpy
numpy.set_printoptions(suppress=True)

bn: BayesianModel = BayesianModel()

bn.add_node("A", 2) # Create app node

for node_src_name in range(0,4):
    # node_name contains the string id of a component
    # For each node in V we create a node in the BN with binary state
    bn.add_node('b'+str(node_src_name), 2)
    cpd = TabularCPD(variable='b'+str(node_src_name), variable_card=2, values=[[1, 0]])
    bn.add_cpds(cpd)
    bn.add_edge('b'+str(node_src_name), "A")


#ops.weighted_kn_node(bn, "A",30,[10,20,50,9])

#print(bn.get_cpds("A"))
#print(bn.get_parents("A"))

ops.scalable_weighted_kn_node(bn, "A",30,[10,20,50,9])

for node_src_name in range(0,4):
    n = "E_" + 'b'+str(node_src_name) + "_" + "A"
    print(bn.get_parents(n))
    print(bn.get_cpds(n))

print(bn.get_cpds("A"))

