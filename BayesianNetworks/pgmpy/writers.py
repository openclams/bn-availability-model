from itertools import product
import os
from collections import deque
from numpy import flip
from itertools import product

def writeBIF (model,filename):
    with open(filename,'w') as f:
        f.write("network unknown {\n}\n")
        for n in model.nodes():
            f.write("variable {0} {{\n".format( n ));
            f.write("   type discrete[ {0} ] {{ {1} }};\n".format(model.get_cardinality(n), str(list(range(model.get_cardinality(n)))).strip('[]')) )
            f.write("}\n")
        i = 0
        for n in model.nodes():
            parents = str(list(model.get_parents(n))).strip("[]").replace("'","")
            if len(parents) == 0:
                f.write("probability ( {0} ) {{\n".format(n))
                cpt = ', '.join(map(str,[round(x,4) for x in model.get_cpds(n).values]))
                f.write("   table {0};\n".format(cpt))
            else:
                f.write("probability ( {0} | {1} ) {{\n".format(n, parents))
                cpt = model.get_cpds(n).get_values()

                parents = list(model.get_parents(n))
                parents_card = [model.get_cardinality(x) for x in parents]
                iterables = ([range(p) for p in list(parents_card)])
                cols = product(*iterables)

                for idx, col_value in enumerate(cols):
                    cl = ', '.join([str(x) for x in col_value])
                    vl = ', '.join(map(str,[x for x in cpt[:,idx]]))
                    f.write("   ({0}) {1};\n".format(cl,vl))
            f.write("}\n")


def writeR (model,filename):
    if not os.path.exists(filename):
        os.makedirs(filename)


    with open( filename+"/bngraphsrc.R",'w') as f:
        f.write("this.dir <- dirname(parent.frame(2)$ofile)\nsetwd(this.dir)\na <- list()\n")
        h = 1
        for n in model.nodes():
            states = []
            for i in range(model.get_cardinality(n)):
                states.append("\""+n + "_" + str(i)+"\"")


            if len(list(model.get_parents(n))) == 0:
                cpt = ','.join(map(str,[round(x,4) for x in model.get_cpds(n).values]))
                cpt_var = "c({0})".format(cpt)
                q = n
                labels = "c(" + ','.join(states) + ")"
            else:
                cpt = model.get_cpds(n).get_values()

                parents = list()
                for value in model.get_parents(n):
                    parents.append(value)



                cols = cpt.shape[1]
                with open( filename+"/"+n + ".csv", 'w') as cpt_file:
                    for c in range(cols):
                        items = [x for x in cpt[:, c]]
                        vl = '\n'.join(map(str, cpt[:, c]))
                        cpt_file.write(vl+'\n')

                f.write("df <- read.table(\"{0}\",header=FALSE)\n".format(n + ".csv"))
                f.write("b <- df[[1]]\n")
                #f.write("print(b)\nb\n")
                cpt_var = "b"
                q = n+"+"+"+".join(parents[::-1])

                labels = ""
                if len(states) < 10:
                    labels = "c(" + ','.join(states) + ")"
                else:
                    with open(filename + "/" + n + "_labels.csv", 'w') as labels_file:
                        for label in states:
                            labels_file.write(label + '\n')
                    f.write("lb <- read.table(\"{0}\",header=FALSE)\n".format(n + "_labels.csv"))
                    f.write("read_labels <- lb[[1]]\n")
                    labels = "read_labels"



            f.write("a <- c(a,list(cptable( ~{1}, values={2}, levels={3})))\n".format(str(h),q, cpt_var, labels))
            h+=1

        f.write("plist <- compileCPT(a)\n")

        f.write("net1 <- grain(plist)\n")
