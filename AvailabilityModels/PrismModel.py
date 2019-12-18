
from CloudGraph.Graph import Graph
from CloudGraph.Host import Host
import CloudGraph.ComputePath as compute_path
import subprocess, os
import re
from typing import Set, List, Dict

class PrismModel:

    def __init__(self,
                 G:Graph,
                 app,
                 temp_file_name:str = "cim.sm",
                 prism_location:str = "C:\\Program Files\\prism-4.5\\"):
        """
        Create a prism model based on the cloud infrastructure and deployment
        :param cim_file_name: Location of the cloud infrastructure model file
        :param dep_file_name: Location of the serverice deployment file
        :param temp_filen_name: Location where to store the prism intermediate mode file
        """
        self.G:Graph =G
        self.app = app
        self.model_name:str = temp_file_name
        self.prism_location:str = prism_location


        self.servers_per_hosts: Dict[str,Dict[str,int]] = {}
        for s_idx in range(len(self.app["services"])):
            service_name = self.app["services"][s_idx]['name']
            self.servers_per_hosts[service_name] = {}
            for host in self.app["services"][s_idx]['servers']:
                self.servers_per_hosts[service_name][host] = len([h for h in self.app["services"][s_idx]['servers'] if h == host])




    def all_available(self,G,node_name):
        """
        Create a string of all ascendants of the node
        :param G: The cloud infrastructure graph
        :param node_name: The name/id of the node
        :return: String ascendants variable names
        """
        ret = ""
        for parent in G.nodes[node_name].fault_dependencies["parents"]:
            is_parent_working = "& "+parent.name + "_w"
            ret = ret + is_parent_working
        return ret
    #
    # def path_set(self,G,ag,init):
    #     return ""
    #     d = [ G.host_groups[a][0]['name'] for a in ag.hosts] # get one representative host from each host group
    #     d.append(init) # add the init component
    #     all_components = set()
    #     for i in range(len(d)):
    #         for j in range (i+1,len(d)):
    #             src = d[i]
    #             dst = d[j]
    #             paths = compute_path.print_all_paths(G,src, dst)
    #             # Delete first and last element
    #             for k in range(len(paths)):
    #                 paths[k] = paths[k][slice(1, len(paths[k]) - 1)]
    #                 all_components.update(paths[k])
    #
    #     return "&".join([c+"_w =  1 " for c in all_components])
    #
    def create_cfc_dependencies(self,node_name,variable_name,f):
        for parent in self.G.nodes[node_name].fault_dependencies["parents"]:
            # Get the action names of the parents
            sync_failure = parent.name + "_failure"
            sync_repair = parent.name + "_repaired"
            # If an
            f.write("\t [%s] true -> 1:(%s' = false);\n" % (sync_failure, variable_name))
            f.write("\t [%s] true -> 1:(%s' = true);\n" % (sync_repair, variable_name))
            self.create_cfc_dependencies(parent.name,variable_name,f)

    def build(self):
        f = open(self.model_name,"w+")
        # First line is the model "continuous-time markov chain"
        f.write("ctmc\n\n")

        # For each node we generate a module
        # node_name contains the string id of a component
        for node_name in self.G.nodes:
            # is_working is the variable name which stores the available state of the module
            is_working = node_name+"_w"
            # the name of the action to sync if this component fails
            sync_failure = node_name+"_failure"
            # the name of the action to sync if this component is repaired
            sync_repair  = node_name+"_repaired"

            f.write("module %s \n" % (node_name))
            # 0 = component failure
            # 1 = component is working

            if isinstance(self.G.nodes[node_name], Host):
                for service_name in self.servers_per_hosts:
                    service_var = node_name +'_'+ service_name
                    if node_name in self.servers_per_hosts[service_name]:
                        num_servers = self.servers_per_hosts[service_name][node_name]
                        f.write("\t %s:  [0..%d] init %d;\n" % (service_var,  num_servers, num_servers))
                        # At this point we can consider failure probabilities of the server

            f.write("\t %s: bool init true;\n" % is_working)

            MTTF = 1/(1-self.G.nodes[node_name].availability)
            MTTR = 1

            # Format the failure and repair rate to floats (with 10th decimal precision)
            failure_rate = "{:1.10f}".format(1/MTTF)
            repair_rate = "{:1.10f}".format(1/MTTR)

            # State change on component failure
            f.write("\t [%s] %s -> %s:(%s' = false);\n" % (sync_failure,is_working, failure_rate, is_working))

            # State change on component repair
            # all_available() contains a string of all ancestors in the common failure graph
            f.write("\t [%s] !%s %s -> %s:(%s' = true);\n" % (sync_repair,is_working,self.all_available(self.G,node_name),repair_rate,is_working))


            # Insert the failure dependencies
            self.create_cfc_dependencies(node_name,is_working,f)
            f.write("endmodule\n\n")


        for service in self.app["services"]:
            service_name = service['name']
            # Add group formulas
            # At this point, we can determine groups based on the deployments, i.e. count hich hosts really have server and group them together
            # where we check if hosts relay have the same parents in cfc and net graph.
            for group in self.G.host_groups:
                if sum([len(host.servers)for host in self.G.host_groups[group].hosts]) > 0:
                    s = "formula "+group+service_name+" = " + "+".join([host.name+"_w" for host in  self.G.host_groups[group].hosts if len(host.name) > 0] )
                    f.write(s+";\n")
        #
        #     # Count through all group combinations
        #     group_names = list(self.G.host_groups.keys())
        #     num_entries = 2**len(group_names)
        #     # This array holds all arrays of host groups where theire sumi
        #     available_groups = []
        #     #every permutaiton of each group
        #     for i in range(num_entries):
        #         bin = "{0:0"+str(len(group_names))+"b}"
        #         #print(bin.format(i))
        #         permutation = bin.format(i)
        #         collect = set()
        #         for idx, b in enumerate(permutation):
        #             if b == "1" and sum([ len(host.servers) for host in self.G.host_groups[group_names[idx]].hosts]) != 0 :
        #                 collect.add(group_names[idx])
        #
        #         #count if the permuation has enough servers
        #         total = sum([sum([ len(host.servers) for host in self.G.host_groups[group].hosts]) for group in collect])
        #         if total >= service["k"]:
        #             found = False
        #             for a in available_groups:
        #                 if a == collect:
        #                     found = True
        #                     break
        #             if not found:
        #                 available_groups.append(collect)
        #
        #     #Build the availablity formula and label
        #     s = []
        #     for ag in available_groups:
        #         if(len(ag) != 0):
        #             #compute paths between any pair
        #             ps = self.path_set(self.G,ag,service["init"])
        #             if ps != "":
        #                 ps = "& ("+ps+")"
        #             s.append("(("+"+".join(ag) + ">= " +str(service["k"])+"&"+service["init"]+"_w = 1 ) "+ps+")\n")
        #
        #     f.write("label \"available\" = "+"|".join(s) + ";\n")
        #     f.write("formula available = " + "|".join(s) + ";\n")
        #
        #
        # f.write("rewards \"time_unavailable\" \n !available : 1; \n endrewards\n")
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
        print(output)
        return (10000-float(re.findall(r"Result: ([-+]?\d*\.\d+|\d+)", output)[0]))/10000

