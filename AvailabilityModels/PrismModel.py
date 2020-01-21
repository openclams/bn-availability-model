
from CloudGraph.Graph import Graph
from CloudGraph.Host import Host
import CloudGraph.ComputePath as compute_path
import subprocess, os
import re
import argparse
from typing import Set, List, Dict
import itertools


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

    def get_paths(self,G,host_groups,init):
        # get one representative host from each host group
        hosts = [G.host_groups[group].hosts[0].name for group in host_groups]
        hosts.append(init) # add the init component
        all_components = set()
        paths_list = []
        for i in range(len(hosts)):
            for j in range (i+1,len(hosts)):
                src = hosts[i]
                dst = hosts[j]
                paths = compute_path.print_all_paths(G,src, dst)

                # Delete first and last element
                for k in range(len(paths)):
                    paths[k] = paths[k][slice(1, len(paths[k]) - 1)]
                    #all_components.update(paths[k])
                paths_list.append(paths)
                print(init, src, dst, paths)

        for path_combination in itertools.product(*paths_list):
            components_set = set()
            print(path_combination)
            [components_set.update(path) for path in path_combination]
            print(components_set)
            all_components.add("&".join([c+"_w " for c in components_set]))

        return all_components
    #
    def create_cfc_dependencies(self,node_name,variable_name,f,votes=None):
        for parent in self.G.nodes[node_name].fault_dependencies["parents"]:
            # Get the action names of the parents
            sync_failure = parent.name + "_failure"
            sync_repair = parent.name + "_repaired"
            #
            if(not votes):
                f.write("\t [%s] true -> 1:(%s' = false);\n" % (sync_failure, variable_name))
                f.write("\t [%s] true -> 1:(%s' = true);\n" % (sync_repair, variable_name))
            else:
                f.write("\t [%s] true -> 1:(%s' = 0);\n" % (sync_failure, variable_name))
                f.write("\t [%s] true -> 1:(%s' = %d);\n" % (sync_repair, variable_name,votes))
            self.create_cfc_dependencies(parent.name,variable_name,f,votes)

    def build(self):
        f = open(self.model_name,"w+")
        # First line is the model "continuous-time markov chain"
        f.write("ctmc\n\n")

        # Add infrastructure dependencies
        # For each node we generate a module
        # node_name contains the string id of a component
        for node_name in self.G.nodes:
            # is_working is the variable name which stores the available state of the module
            is_working = node_name+"_w"
            # the name of the action to sync if this component fails
            sync_failure = node_name+"_failure"
            # the name of the action to sync if this component is repaired
            sync_repair  = node_name+"_repaired"

            f.write("module %s \n" % node_name)
            # 0 = component failure
            # 1 = component is working

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

        # Add services
        for s_idx in range(len(self.app["services"])):

            service_name = self.app["services"][s_idx]['name']
            threshold = self.app["services"][s_idx]['threshold']
            init = self.app["services"][s_idx]['init']
            hostMap = {}
            voteMap = {}

            for idx, server in enumerate(self.app["services"][s_idx]['servers']):
                # The number of servers on a hosts for a service
                host = server['host']
                host_formula_name = host+"_"+service_name
                votes = server['votes']

                node_name = service_name+"_"+str(idx)
                # is_working is the variable name which stores the available state of the module
                is_working = node_name + "_w"
                if host_formula_name in hostMap:
                    hostMap[host_formula_name].append(is_working)
                    voteMap[host_formula_name] = voteMap[host_formula_name] + votes
                else:
                    hostMap[host_formula_name] = [is_working]
                    voteMap[host_formula_name] = votes
                f.write("module %s \n" % (node_name))
                # 0 = component failure
                # 1 = component is working
                f.write("\t %s:  [0..%d] init %d;\n" % (is_working, votes, votes))

                sync_failure = host + "_failure"
                sync_repair  = host + "_repaired"
                # If an
                f.write("\t [%s] true -> 1:(%s' = 0);\n" % (sync_failure, is_working))
                f.write("\t [%s] true -> 1:(%s' = %d);\n" % (sync_repair, is_working,votes))

                # Insert the failure dependencies
                self.create_cfc_dependencies(host, is_working, f,votes)
                f.write("endmodule\n\n")

        # Add channels for inter server communication and the quorms
            for hmap in hostMap:
                s = "formula "+hmap + " = " + "+".join(hostMap[hmap])
                f.write(s + ";\n")

            group_names_map = {}
            group_votes_map = {}
            for group in self.G.host_groups:
                group_service = group+"_"+service_name
                hosts = "+".join([host.name+"_"+service_name for host in  self.G.host_groups[group].hosts if host.name+"_"+service_name in hostMap] )
                if hosts:
                    group_names_map[group] = group_service
                    group_votes_map[group] = sum([voteMap[host.name+"_"+service_name] for host in  self.G.host_groups[group].hosts if host.name+"_"+service_name in hostMap] )
                    s = "formula "+group_service+" = " + hosts
                    f.write(s+";\n")

            # Count through all group combinations
            group_names = list(group_names_map.keys())
            num_entries = 2**len(group_names)
            # This array holds all arrays of host groups where theire sumi

            available_groups = []
            #every permutaiton of each group
            for i in range(num_entries):
                bin = "{0:0"+str(len(group_names))+"b}"
                #print(bin.format(i))
                combination = bin.format(i)
                collect = set()
                for idx, b in enumerate(combination):
                    if b == "1":
                        collect.add(group_names[idx])

                # count if the permuation has enough servers
                total = sum([group_votes_map[group_name] for group_name in collect])
                if total >= threshold:
                    found = False
                    for a in available_groups:
                        if a == collect:
                            found = True
                            break
                    if not found:
                        available_groups.append(collect)

            #Build the availablity formula and label

            # Store all paths and groups possibilities as a
            # disjunctive normal form (DNF)
            # This list stores the conjunctions as strings
            terms:List[str] = []
            for ag in available_groups:
                if(len(ag) != 0):
                    #compute paths between any pair

                    paths = "|".join(self.get_paths(self.G,ag,init))
                    if not paths:
                        paths = ""
                    else:
                        paths = " & (%s)" % paths
                    host_groups_combination = "+".join([group_names_map[a] for a in ag])
                    term = "((%s >= %d & %s_w) %s)\n" %(host_groups_combination, threshold,  init, paths)
                    terms.append(term)

            label = "availability_%s" % service_name
            reward_name = "time_unavailable_%s" % service_name
            self.create_labels(label,terms,f)
            self.create_reward(reward_name,label,f)

        f.close()

    def create_labels(self,label_name:str,terms:List[str],f):
        exp = "|".join(terms);
        f.write("label \"%s\" = %s;\n" % (label_name, exp))
        f.write("formula %s = %s;\n" % (label_name, exp))

    def create_reward(self,reward_name:str,label_name:str,f):
        f.write("rewards \"%s\"\n !%s : 1; \nendrewards\n" % (reward_name,label_name))

    def result(self,query):
        my_env = os.environ.copy()
        my_env["PATH"] = "C:\\Program Files\\prism-4.5\\" + my_env["PATH"]
        # -h uses the hybrid engine
        args = ("C:\\Program Files\\prism-4.5\\bin\\prism.bat", self.model_name , "-pf",
                "S=? [ \"availability_%s\" ]"%query, "-h" , "-gs")

        popen = subprocess.Popen(args,env=my_env, shell=True, stdout=subprocess.PIPE)
        popen.wait()
        output = str(popen.stdout.read())
        print(output)
        return float(re.findall(r"Result: ([-+]?\d*\.\d+|\d+)",output)[0])

    def simulate(self,query):
        my_env = os.environ.copy()
        my_env["PATH"] = "C:\\Program Files\\prism-4.5\\" + my_env["PATH"]
        # -h uses the hybrid engine
        args = (
            "C:\\Program Files\\prism-4.5\\bin\\prism.bat", self.model_name, "-pf",
            "R{\"time_unavailable_%s\"}=? [ C<=10000 ]"%query, "-sim")

        popen = subprocess.Popen(args, env=my_env, shell=True, stdout=subprocess.PIPE)
        popen.wait()
        output = str(popen.stdout.read())
        print(output)
        return (10000-float(re.findall(r"Result: ([-+]?\d*\.\d+|\d+)", output)[0]))/10000

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='PRISM Availability Model for Cloud Applications',
        description='Compute the availability of a cloud application.')
    parser.add_argument('--verbose', '-v', action='count', default=0)
    parser.add_argument('--version', action='version', version='%(prog) Version 0.1')
    parser.add_argument('--application','-a', default="Tests/service_voting/deployment.json", nargs='?')
    parser.add_argument('--infrastructure','-i', default="Tests/service_voting/graph.json", nargs='?' )
    parser.add_argument('--output','-o', default="../test/service-catalog.json", nargs='?')
    parser.add_argument('--prism_path', '-p', default="C:\\Program Files\\prism-4.5\\", nargs='?')
    parser.add_argument('--prism_exec', '-e', default="C:\\Program Files\\prism-4.5\\bin\\prism.bat", nargs='?')

    args = parser.parse_args()

    verbose:int = int(args.verbose)
    application_file: str = args.application
    infrastructure_file: str = args.infrastructure
    output_file:str = args.output
    prism_path:str = args.prism_path
    prism_exec:str = args.prism_exec

    #tree = main(output_file,path,schema_path)

    # if verbose:
    #    print_tree(tree)