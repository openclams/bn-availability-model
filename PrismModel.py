import json
from CloudGraph.Graph import Graph
from GraphParser import GraphParser
import subprocess, os
import re

class PrismModel:

    def __init__(self):
        parser = GraphParser("Tests/graph.json")
        self.G =  parser.G
        json_file = open("Tests/deployment_1.json")
        self.app = json.load(json_file)
        self.model_name = "cim.sm"
        self.buildPrismModel()


    def all_available(self,G,node_name):
        ret = ""
        for parent in G.V[node_name].cfc["parents"]:
            is_parent_working = "& "+parent.name + "_w = 1"
            ret = ret + is_parent_working
        return ret

    def path_set(self,G,ag,init):
        d = [ G.groups[a][0].name for a in ag] # get one representative host from reach host group
        d.append(init) # add the init component
        all_components = set()
        for i in range(len(d)):
            for j in range (i+1,len(d)):
                src = d[i]
                dst = d[j]
                paths = G.print_all_paths(src, dst)
                # Delete first and last element
                for k in range(len(paths)):
                    paths[k] = paths[k][slice(1, len(paths[k]) - 1)]
                    all_components.update(paths[k])

        return "&".join([c+"_w =  1 " for c in all_components])


    def buildPrismModel(self):
        f = open(self.model_name,"w+")
        f.write("ctmc\n\n")
        #print("Build Modules")
        for node_name in self.G.V:
            # node_name contains the string id of a component
            #print("Add module", node_name)
            is_working = node_name+"_w"
            sync_failure = node_name+"_failure"
            sync_repair  = node_name+"_repaired"
            # For each node in V we create a node in the BN with binary state
            f.write("module %s \n" % (node_name))
            f.write("\t %s: [0..1] init 1;\n" % (is_working))

            num_1 = "{:1.10f}".format(1-self.G.V[node_name].availability)
            #print(num_1)
            num_2 = 1#"{:10.10f}".format((1 - G.V[node_name].availability) * 0.9)
            #print(num_2)
            f.write("\t [%s] %s = 1 -> %s:(%s' = 0);\n" % (sync_failure,is_working,num_1 ,is_working))
            f.write("\t [%s] %s = 0 %s -> %s:(%s' = 1);\n" % (sync_repair,is_working,self.all_available(self.G,node_name),num_2,is_working))
            for parent in self.G.V[node_name].cfc["parents"]:
                sync_failure = parent.name + "_failure"
                sync_repair = parent.name + "_repaired"
                f.write("\t [%s] true -> 1:(%s' = 0);\n" % (sync_failure,  is_working))
                f.write("\t [%s] true -> 1:(%s' = 1);\n" % (sync_repair, is_working))
            f.write("endmodule\n\n")

        servers = {}
        for service in self.app["services"]:
            servers[service["name"]] = []
            for idx, host in enumerate(service["servers"]):
                server_name = service["name"]+"_"+"R_"+str(idx)
                servers[service["name"]].append(server_name)
                self.G.V[host].servers.append(server_name)


            for group in self.G.groups:
                s = "formula "+group+" = " + "+".join([host.name+"_w" for host in  self.G.groups[group]] )
                f.write(s+";\n")

            group_names = list(self.G.groups.keys())
            num_entries = 2**len(group_names)
            available_groups = []
            #every permutaiton of each group
            for i in range(num_entries):
                bin = "{0:0"+str(len(group_names))+"b}"
                #print(bin.format(i))
                permutation = bin.format(i)
                collect = []
                for idx, b in enumerate(permutation):
                    if b == "1" and sum([ len(host.servers) for host in self.G.groups[group_names[idx]]]) != 0 :
                        collect.append(group_names[idx])

                #count if the permuation has enough servers
                total = sum([sum([ len(host.servers) for host in self.G.groups[group]]) for group in collect])
                if total > service["k"]:
                    available_groups.append(collect)

            #Build the availablity formula and label
            s = []
            for ag in available_groups:
                #compute paths between any pair
                s.append("("+"+".join(ag) + ">= " +str(service["k"])+"&"+service["init"]+"_w = 1 ) & ("+self.path_set(self.G,ag,service["init"])+")\n")

            f.write("label \"available\" = "+"|".join(s) + ";\n")
            f.write("formula available = " + "|".join(s) + ";\n")


        f.write("rewards \"time_unavailable\" \n !available : 1; \n endrewards\n")
        f.close()

    def result(self):

        my_env = os.environ.copy()
        my_env["PATH"] = "C:\\Program Files\\prism-4.5\\" + my_env["PATH"]
        # -h uses the hybrid engine
        args = ("C:\\Program Files\\prism-4.5\\bin\\prism.bat", self.model_name , "-pf", "S=? [ \"available\" ]", "-h" , "-gs")
        # Or just:
        # args = "bin/bar -c somefile.xml -d text.txt -r aString -f anotherString".split()
        popen = subprocess.Popen(args,env=my_env, shell=True, stdout=subprocess.PIPE)
        popen.wait()
        output = str(popen.stdout.read())
        #errput = str(popen.stderr.read())
        #print(errput)
        #print(output)
        return float(re.findall(r"Result: ([-+]?\d*\.\d+|\d+)",output)[0])

