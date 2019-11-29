
from CloudGraph.Graph import Graph

import subprocess, os
import re

class PrismModel:

    def __init__(self,
                 G, app,
                 structure= "ctmc" ,
                 temp_file_name = "cim.sm",
                 prism_location = "C:\\Program Files\\prism-4.5\\"):
        """
        Create a prism model based on the cloud infrastructure and deployment
        :param structure: Either "ctmc" or "dtmc"
        :param cim_file_name: Location of the cloud infrastructure model file
        :param dep_file_name: Location of the serverice deployment file
        :param temp_filen_name: Location where to store the prism intermediate mode file
        """
        self.G =G
        self.app = app
        self.model_name = temp_file_name
        self.prism_location = prism_location
        self.servers_per_hosts = {}
        for host in self.app["services"][0]['servers']:
            self.servers_per_hosts[host] = 0;
        for host in self.app["services"][0]['servers']:
            self.servers_per_hosts[host] =  self.servers_per_hosts[host] + 1;


    def CTMC_module(self):
        pass

    def all_available(self,G,node_name):
        """
        Create a string of all ascendants of the node
        :param G: The cloud infrastructure graph
        :param node_name: The name/id of the node
        :return: String ascendants variable names
        """
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

    def create_cfc_dependencies(self,node_name,variable_name,f):
        for parent in self.G.V[node_name].cfc["parents"]:
            # Get the action names of the parents
            sync_failure = parent.name + "_failure"
            sync_repair = parent.name + "_repaired"
            # If an
            f.write("\t [%s] true -> 1:(%s' = 0);\n" % (sync_failure, variable_name))
            f.write("\t [%s] true -> 1:(%s' = 1);\n" % (sync_repair, variable_name))
            self.create_cfc_dependencies(parent.name,variable_name,f)

    def buildCTMCPrismModel(self):
        f = open(self.model_name,"w+")
        # First line is the model "continuous-time markov chain"
        f.write("ctmc\n\n")

        # For each node we generate a module
        # node_name contains the string id of a component
        for node_name in self.G.V:
            # is_working is the variable name which stores the available state of the module
            is_working = node_name+"_w"
            # the name of the action to sync if this component fails
            sync_failure = node_name+"_failure"
            # the name of the action to sync if this component is repaired
            sync_repair  = node_name+"_repaired"




            f.write("module %s \n" % (node_name))
            # 0 = component failure
            # 1 = component is working
            max_num = 1
            if node_name in self.servers_per_hosts.keys():
                max_num =  self.servers_per_hosts[node_name]

            f.write("\t %s: [0..%d] init %d;\n" % (is_working, max_num,max_num))

            availability = 1-self.G.V[node_name].availability
            repair = 1

            MTTF = 1/(1-self.G.V[node_name].availability)
            MTTR = 1

            # Format the failure and repair rate to floats (with 10th decimal precision)
            failure_rate = "{:1.10f}".format(1/MTTF)
            repair_rate = "{:1.10f}".format(1/MTTR)

            # State change on component failure
            f.write("\t [%s] %s >= 1 -> %s:(%s' = 0);\n" % (sync_failure,is_working,failure_rate ,is_working))

            # State change on component repair
            # all_available() contains a string of all ancestors in the common failure graph
            f.write("\t [%s] %s = 0 %s -> %s:(%s' = %d);\n" % (sync_repair,is_working,self.all_available(self.G,node_name),repair_rate,is_working,max_num))

            #num_1 = "{:10.10f}".format(self.G.V[node_name].availability)
            #num_11 = "{:10.10f}".format(1 - self.G.V[node_name].availability)
            # num_1 =self.G.V[node_name].availability
            # print(num_1)
            #num_2 = 1  # "{:10.10f}".format((1 - G.V[node_name].availability) * 0.9)
            # print(num_2)
            #f.write("\t [%s] %s = 1 -> %s:(%s' = 0) + %s:(%s' = 1);\n" % (
            #sync_failure, is_working, num_11, is_working, num_1, is_working))
            #f.write("\t [%s] %s = 0 %s -> %s:(%s' = 1);\n" % (
            #sync_repair, is_working, self.all_available(self.G, node_name), num_2, is_working))


            # Insert the failure dependencies
            self.create_cfc_dependencies(node_name,is_working,f)
            f.write("endmodule\n\n")

        servers = {}
        for service in self.app["services"]:
            servers[service["name"]] = []
            for idx, host in enumerate(service["servers"]):
                server_name = service["name"]+"_"+"R_"+str(idx)
                servers[service["name"]].append(server_name)
                # Add to each host its servers (string id of server)
                self.G.V[host].servers.append(server_name)

            # Add group formulas
            # At this point, we can determine groups based on the deployments, i.e. count hich hosts really have server and group them together
            # where we check if hosts relay have the same parents in cfc and net graph.
            for group in self.G.groups:
                if sum([len(host.servers)for host in  self.G.groups[group]]) > 0:
                    s = "formula "+group+" = " + "+".join([host.name+"_w" for host in  self.G.groups[group] if len(host.servers) > 0] )
                    f.write(s+";\n")

            # Count through all group permutations
            group_names = list(self.G.groups.keys())
            num_entries = 2**len(group_names)
            # This array holds all arrays of host groups where theire sumi
            available_groups = []
            #every permutaiton of each group
            for i in range(num_entries):
                bin = "{0:0"+str(len(group_names))+"b}"
                #print(bin.format(i))
                permutation = bin.format(i)
                collect = set()
                for idx, b in enumerate(permutation):
                    if b == "1" and sum([ len(host.servers) for host in self.G.groups[group_names[idx]]]) != 0 :
                        collect.add(group_names[idx])

                #count if the permuation has enough servers
                total = sum([sum([ len(host.servers) for host in self.G.groups[group]]) for group in collect])
                if total >= service["k"]:
                    found = False
                    for a in available_groups:
                        if a == collect:
                            found = True
                            break
                    if not found:
                        available_groups.append(collect)

            #Build the availablity formula and label
            s = []
            for ag in available_groups:
                if(len(ag) != 0):
                    #compute paths between any pair
                    ps = self.path_set(self.G,ag,service["init"])
                    if ps != "":
                        ps = "& ("+ps+")"
                    s.append("(("+"+".join(ag) + ">= " +str(service["k"])+"&"+service["init"]+"_w = 1 ) "+ps+")\n")

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
        print(output)
        return float(re.findall(r"Result: ([-+]?\d*\.\d+|\d+)",output)[0])

    def simulate(self):
        my_env = os.environ.copy()
        my_env["PATH"] = "C:\\Program Files\\prism-4.5\\" + my_env["PATH"]
        # -h uses the hybrid engine
        args = (
            "C:\\Program Files\\prism-4.5\\bin\\prism.bat", self.model_name, "-pf",
            "R{\"time_unavailable\"}=? [ C<=10000 ]", "-sim")
        # Or just:
        # args = "bin/bar -c somefile.xml -d text.txt -r aString -f anotherString".split()
        popen = subprocess.Popen(args, env=my_env, shell=True, stdout=subprocess.PIPE)
        popen.wait()
        output = str(popen.stdout.read())
        # errput = str(popen.stderr.read())
        # print(errput)
        print(output)
        return (10000-float(re.findall(r"Result: ([-+]?\d*\.\d+|\d+)", output)[0]))/10000

