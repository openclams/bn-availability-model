import os
from collections import deque
from numpy import flip
import pyAgrum as gum
from itertools import product

def writeBIF (bn : gum.BayesNet,filename):
    with open(filename,'w') as f:
        f.write("network unknown {\n}\n")
        for n in bn.nodes():
            f.write("variable {0} {{\n".format( bn.variable(n).name() ))
            f.write("   type discrete[ {0} ] {{ {1} }};\n".format(len(bn.variable(n).labels()), ", ".join([bn.variable(n).name()+"_"+str(x) for x in bn.variable(n).labels()])))
            f.write("}\n")
        i = 0
        for n in bn.nodes():
            parents = list(bn.parents(n)) # list of ids
            if len(parents) == 0:
                f.write("probability ( {0} ) {{\n".format(bn.variable(n).name()))
                cpt = ', '.join(map(str,[round(x,4) for x in bn.cpt(n)]))
                f.write("   table {0};\n".format(cpt))
            else:
                pa = ", ".join([bn.variable(p).name() for p in parents])
                f.write("probability ( {0} | {1} ) {{\n".format(bn.variable(n).name(), pa))

                iterables = [bn.variable(p).labels() for p in parents]
                cols = product(*iterables)

                for c in cols:
                    #print(type(c))
                    cl = []
                    for idx, parent_value in enumerate(c):
                        cl.append(bn.variable(parents[idx]).name()+"_"+str(parent_value))

                    cond = {}
                    for idx, parent_value in enumerate(c):
                        cond[(bn.variable(parents[idx]).name())] = parent_value
                    #print(cond, bn.cpt(n)[cond])
                    cpt = ', '.join(map(str, [x for x in bn.cpt(n)[cond]]))
                    f.write("   ({0}) {1};\n".format(", ".join(cl),cpt))
            f.write("}\n")

def writeR ( bn : gum.BayesNet ,filename):
    if not os.path.exists(filename):
        os.makedirs(filename)


    with open( filename+"/bngraphsrc.R",'w') as f:
        f.write("this.dir <- dirname(parent.frame(2)$ofile)\nsetwd(this.dir)\na <- list()\n")
        for n in bn.nodes():
            states = []
            for i in range(len(bn.variable(n).labels())):
                states.append("\""+bn.variable(n).name()+ "_" + str(i)+"\"")
            levels = ','.join(states)

            if len(list(bn.parents(n))) == 0:
                cpt = ', '.join(map(str,[round(x,4) for x in bn.cpt(n)]))
                cpt_var = "c({0})".format(cpt)
                q = bn.variable(n).name()
            else:
                cpt = bn.cpt(n)

                parents_text = [bn.variable(p).name() for p in list(bn.parents(n))]
                parents = [p for p in list(bn.parents(n))]
                #for p in bn.parents(n):
                #    parents.append(value)

                with open( filename+"/"+bn.variable(n).name() + ".csv", 'w') as cpt_file:
                    iterables = ([bn.variable(p).labels() for p in list(parents)])
                    iterables.reverse()
                    cols = product(*iterables)

                    rev_p = list(parents.copy())
                    rev_p.reverse()

                    for c in cols:
                        cond = {}
                        for idx, parent_value in enumerate(c):
                            cond[(bn.variable(rev_p[idx]).name())] = parent_value

                        cpt = [x for x in bn.cpt(n)[cond]]
                        vl = '\n'.join(map(str, cpt))
                        cpt_file.write(vl+'\n')

                f.write("df <- read.table(\"{0}\",header=FALSE)\n".format(bn.variable(n).name() + ".csv"))
                f.write("b <- df[[1]]\n")
                #f.write("print(b)\nb\n")
                cpt_var = "b"
                q = bn.variable(n).name()+"+"+"+".join(parents_text)

            f.write("a <- c(a,list(cptable( ~{0}, values={1}, levels=c({2}))))\n".format(q, cpt_var, levels))

        f.write("plist <- compileCPT(a)\n")

        f.write("net1 <- grain(plist)\n")
        #f.write("net1 <- compile(net0)\n")