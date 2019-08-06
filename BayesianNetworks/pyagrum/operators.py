import pyAgrum as gum
import numpy as np


def create_cpt(bn, bn_node, fn):  # Put in a lambade for the evaluation and the node to load the conditions
    names = bn.cpt(bn_node).var_names  # this array also contains the node it slef
    names.remove(bn_node)  # extract own from node
    if len(names) == 0:  # this condition is for the root nodes
        bn.cpt(bn_node)[:] = fn({})
        return
    num_entries = 2 ** len(names)
    for i in range(num_entries):
        bin = "{0:0" + str(len(names)) + "b}"
        permutation = bin.format(i)
        cond = {}
        for idx, b in enumerate(permutation):
            cond[names[idx]] = int(b)
        bn.cpt(bn_node)[cond] = fn(cond)


def adder_cpt(bn, bn_node, n):
    names = bn.cpt(bn_node).var_names  # this array also contains the node it slef
    names.remove(bn_node)  # extract own from node
    if len(names) != 1:
        for v1 in range(n-1):
            for v2 in range(2):
                cond = {names[0]: v1, names[1]: v2}
                sol = np.zeros(n)
                sol[v1 + v2] = 1
                bn.cpt(bn_node)[cond] = sol
    else:
        for v1 in range(2):
            cond = {names[0]: v1}
            sol = [0,0]
            sol[v1] = 1
            bn.cpt(bn_node)[cond] = sol


def create_binary_ci_cpt(bn, bn_node_name, fn):
    c_names = bn.cpt(bn_node_name).var_names
    c_names.remove(bn_node_name)
    # create for each C node an E node
    last_e = None
    first = True
    for c in c_names:
        e_name = "E_" + c + "_" + bn_node_name
        bn.add(e_name, 2)
        bn.addArc(c, e_name)
        if not first:
            bn.addArc(last_e, e_name)
        fn(bn, e_name)
        last_e = e_name
        first = False
    # remove all arcs from bn_node_name and bindto the last e_nam
    for c in c_names:
        bn.eraseArc(c, bn_node_name)
    try:
        bn.addArc(last_e, bn_node_name)
    except Exception as inst:
        print(last_e,inst,bn_node_name)
    and_node(bn, bn_node_name)


def and_node(bn, bn_node):
    fn = lambda c: [len(c.values()) != sum(c.values()), len(c.values()) == sum(c.values())]
    create_cpt(bn, bn_node, fn)


def or_node(bn, bn_node):
    fn = lambda c: [sum(c.values()) == 0, sum(c.values()) > 0]
    create_cpt(bn, bn_node, fn)


def kn_node(bn, bn_node, k):
    fn = lambda c: [sum(c.values()) < k, sum(c.values()) >= k]
    create_cpt(bn, bn_node, fn)


def efficient_and_node(bn, bn_node):
    if len(list(bn.cpt(bn_node).var_names)) > 6 :
        create_binary_ci_cpt(bn, bn_node, and_node)
    else:
        and_node(bn,bn_node)

def efficient_or_node( bn, bn_node):
    create_binary_ci_cpt(bn, bn_node, or_node)


def scalable_kn_node(bn, bn_node_name, k):
    print(bn_node_name)
    c_names = bn.cpt(bn_node_name).var_names
    c_names.remove(bn_node_name)
    # create for each C node an E node
    last_e = None
    first = True
    m = 1
    for c in c_names:
        e_name = "E_" + c + "_" + bn_node_name
        bn.add(e_name, m + 1)
        m = m + 1
        bn.addArc(c, e_name)
        if not first:
            bn.addArc(last_e, e_name)
        adder_cpt(bn, e_name, m)
        last_e = e_name
        first = False
    # remove all arcs from bn_node_name and bindto the last e_nam
    for c in bn.parents(bn.idFromName(bn_node_name)):
        bn.eraseArc(gum.Arc(c, bn.idFromName(bn_node_name)))
    bn.addArc(last_e, bn_node_name)
    for e in range(m):
        if e < k:
            bn.cpt(bn_node_name)[{last_e: e, bn_node_name: 0}] = 1
            bn.cpt(bn_node_name)[{last_e: e, bn_node_name: 1}] = 0
        else:
            bn.cpt(bn_node_name)[{last_e: e, bn_node_name: 0}] = 0
            bn.cpt(bn_node_name)[{last_e: e, bn_node_name: 1}] = 1

