from pgmpy.models import BayesianModel
from pgmpy.factors.discrete import TabularCPD
import numpy as np
from operator import mul
from functools import reduce
from itertools import product


def create_cpt(bn : BayesianModel, bn_node, fn):  # Put in a lambade for the evaluation and the node to load the conditions
    parents = list(bn.get_parents(bn_node))
    parents_card = [bn.get_cardinality(x) for x in parents]
    if len(parents) == 0:  # this condition is for the root nodes
        cpd = TabularCPD(variable=bn_node, variable_card=2, values=[fn({})])
        bn.add_cpds(cpd)
        return
    num_entries = 2 ** len(parents)
    cpt = np.zeros((2,num_entries), dtype=float)

    for i in range(num_entries):
        bin = "{0:0" + str(len(parents)) + "b}"
        permutation = bin.format(i)
        cond = []
        for idx, b in enumerate(permutation):
            cond.append(int(b))
        cpt[:,i] = fn(cond)

    cpd = TabularCPD(variable=bn_node, variable_card=2, values=cpt,
                     evidence=parents,
                     evidence_card=parents_card)
    bn.add_cpds(cpd)


def adder_cpt(bn : BayesianModel, bn_node, n):
    parents = list(bn.get_parents(bn_node))  # this array also contains the node itself
    parents_card = [bn.get_cardinality(x) for x in parents]
    if len(parents) != 1:
        cpt = np.zeros((n,reduce(mul, parents_card, 1)))

        iterables = ([range(p) for p in list(parents_card)])
        cols = product(*iterables)

        for idx, col_value in enumerate(cols):
            sol = np.zeros(n)
            sol[sum(col_value)] = 1
            cpt[:, idx] = np.array(sol)

        cpd = TabularCPD(variable=bn_node, variable_card=n, values=cpt,
                         evidence=parents,
                         evidence_card=parents_card)
        bn.add_cpds(cpd)

    else:
        cpd = TabularCPD(variable=bn_node, variable_card=2, values=[[1, 0],[0, 1]],
                         evidence=parents,
                         evidence_card=parents_card)
        bn.add_cpds(cpd)


def create_binary_ci_cpt(bn : BayesianModel, bn_node_name, fn):
    c_parents = list(bn.get_parents(bn_node_name))  # this array also contains the node itself
    c_parents_card = [bn.get_cardinality(x) for x in c_parents]
    # create for each C node an E node
    last_e = None
    first = True
    for c in c_parents:
        e_name = "E_" + c + "_" + bn_node_name
        bn.add_node(e_name, 2)
        bn.add_edge(c, e_name)
        if not first:
            bn.add_edge(last_e, e_name)
        fn(bn, e_name)
        last_e = e_name
        first = False
    # remove all arcs from bn_node_name and bindto the last e_nam
    for c in c_parents:
        bn.remove_edge(c, bn_node_name)
    try:
        bn.add_edge(last_e, bn_node_name)
    except Exception as inst:
        print(last_e,inst,bn_node_name)
    and_node(bn, bn_node_name)


def and_node(bn : BayesianModel, bn_node):
    fn = lambda c: [len(c) != sum(c), len(c) == sum(c)]
    create_cpt(bn, bn_node, fn)


def or_node(bn : BayesianModel, bn_node):
    fn = lambda c: [sum(c) == 0, sum(c) > 0]
    create_cpt(bn, bn_node, fn)


def kn_node(bn : BayesianModel, bn_node, k):
    fn = lambda c: [sum(c) < k, sum(c) >= k]
    create_cpt(bn, bn_node, fn)


def efficient_and_node(bn : BayesianModel, bn_node):
    if len(list(bn.get_parents(bn_node))) > 6 :
        create_binary_ci_cpt(bn, bn_node, and_node)
    else:
        and_node(bn,bn_node)

def efficient_or_node(bn: BayesianModel, bn_node):
    create_binary_ci_cpt(bn, bn_node, or_node)


def scalable_kn_node(bn : BayesianModel, bn_node_name, k):

    c_parents = list(bn.get_parents(bn_node_name))  # this array also contains the node itself
    c_parents_card = [bn.get_cardinality(x) for x in c_parents]
    # create for each C node an E node
    last_e = None
    first = True
    m = 1
    for c in c_parents:
        e_name = "E_" + c + "_" + bn_node_name
        bn.add_node(e_name, m + 1) # the number of labels
        m = m + 1
        bn.add_edge(c, e_name)
        if not first:
            bn.add_edge(last_e, e_name)
        adder_cpt(bn, e_name, m)
        last_e = e_name
        first = False
    # remove all arcs from bn_node_name and bindto the last e_nam
    for c in c_parents:
        bn.remove_edge(c,bn_node_name)
    bn.add_edge(last_e, bn_node_name)

    cpt = np.zeros((2,m))

    for e in range(m):
        if e < k:
            cpt[0,e] = 1
            cpt[1,e] = 0
        else:
            cpt[0,e] = 0
            cpt[1,e] = 1

    cpd = TabularCPD(variable=bn_node_name, variable_card=2, values=cpt,
                     evidence=[last_e],
                     evidence_card=[m])
    bn.add_cpds(cpd)
