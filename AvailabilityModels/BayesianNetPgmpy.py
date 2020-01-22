from pgmpy.models import BayesianModel
import numpy as np
import BayesianNetworks.pgmpy.operators as ops
from CloudGraph.Graph import Graph
from typing import List, Set, Dict
import CloudGraph.ComputePath as compute_path
import BayesianNetworks.pgmpy.draw as dr

class BayesianNetModel:

    def __init__(self,G:Graph,app,andNodeCPT = ops.and_node, orNodeCPT= ops.or_node, knNodeCPT=ops.kn_node, weightedKnNodeCPT = ops.weighted_kn_node):
        self.G:Graph = G
        self.bn:BayesianModel = BayesianModel()
        self.app = app
        self.andNodeCPT = andNodeCPT
        self.orNodeCPT = orNodeCPT
        self.knNodeCPT = knNodeCPT
        self.weightedKnNodeCPT = weightedKnNodeCPT
        self.construct_bn()

    def construct_bn(self):
        for node_name in self.G.nodes:
            # node_name contains the string id of a component
            # For each node in V we create a node in the BN with binary state
            self.bn.add_node(node_name, 2)

        for node_src_name in self.G.nodes:
            # For each node_name we get the acctual node object
            # The Node object contains an array of strings with children node ids
            for node_dst in self.G.nodes[node_src_name].fault_dependencies["children"]:
                # For each child node id we insert an arc
                # print("Add arc (",node_src_name,node_dst.name,")" )
                self.bn.add_edge(node_src_name, node_dst.name)
                # We have no build the common failure cause tree
                # TODO: At this point we need insert a mechanism to resolve cycles in the common failure cause structure

        #bngraph.pdfize(bn,"step0.png");
        for node_name in self.G.nodes:
            # For each node string id, we associate a an AND CPT with the corresponding BN node
            self.andNodeCPT(self.bn, node_name)

            # Now we need to add at the last row of the CPT, where all conditions are true, the availability
            if len(list(self.bn.get_parents(node_name))) > 0:
                # IF the last row is still an array, i.e. no root nodes

                self.bn.get_cpds(node_name).values[:,self.bn.get_cpds(node_name).values.shape[1]-1] = np.array([1-self.G.nodes[node_name].availability,self.G.nodes[node_name].availability])
            else:
                # If we have a root node
                self.bn.get_cpds(node_name).values = np.array([1 - self.G.nodes[node_name].availability,self.G.nodes[node_name].availability])


        #Servers is a dic. The keys are the service names and the values are array with the string ids of the servers
        servers:Dict[str,List[str]] = {}
        # Channels is a dic. The keys are the service names and the values are dics where the keys are string concatetion of
        # server indexes between any src dst pair. The value is the name of the channel.
        channels:Dict[str,Dict[str,str]] = {}
        # One ore more channels can have the same path
        # in all paths with store as key the unique path names and as values the network components of the path as array
        all_paths = {}
        current_path_index = 1
        weights = []
        for service in self.app["services"]:
            # For each service we create all servers nodes
            #print ("Service", service["name"],"found")
            threshold = service['threshold']
            servers[ service["name"] ] = []  # store all server names per service in this dic
            # We iterate over all hosts, i.e. deployments
            # Server do not have names, this version does not support nested k:n service models yet
            for idx, server in enumerate(service["servers"]):
                weights.append(server['votes'])
                server_name = service["name"]+"_"+"R_"+str(idx)
                servers[service["name"]].append(server_name)
                # Add BN nodes for each server of the service
                self.bn.add_node(server_name, 2)
                # Connect the servers with the appropriate hosts
                self.bn.add_edge(server['host'], server_name)
                #print(host,server_name,self.bn.cpt(server_name).var_names)
                # Add an AND CPT to the server BN node
                self.andNodeCPT(self.bn, server_name)

            path_channel_map = {}
            n_servers = len(service["servers"])
            channels[service["name"]] = {}  # store here all internal channels
            A_nodes = []  # Store for further processing the names of ther augemented servers
            n = sum([service["servers"][idx]["votes"] for idx in range(n_servers)])
            if not (threshold == n or threshold == 1):  # If not read-on/write all

                # Now we create the channel BN nodes for every server pair
                # We have undreicted edges, therefore, we only iterate between every pair without backedge (n/2)
                for i in range(0,n_servers):
                    for j in range(i+1,n_servers):
                        channel_name = service["name"]+"_"+str(i)+"_"+str(j)  # here we have i< j
                        # e.g.Channel for 5 to 3 is "3_5"
                        channels[service["name"]][str(i)+"_"+str(j)] = channel_name
                        self.bn.add_node(channel_name, 2)
                        # Connect src and dst with BN channel node
                        self.bn.add_edge(servers[service["name"]][i], channel_name)
                        self.bn.add_edge(servers[service["name"]][j], channel_name)
                        # Each BN channel node is an AND node


                #print("Add paths to channels", service["name"])

                # Here are key the src dst part as string and the value is the path name as stirng, e.g. P1 node

                # We keep track how many unique paths we have found

                #We iterate over each src dst pair and we compute a path
                for i in range(0, n_servers):
                    for j in range(i + 1, n_servers):
                        path_channel_map[str(i) + "_" + str(j)] = []
                        host_a = self.bn.get_parents(servers[service["name"]][i])[0] # get host, which is a parent node of the server node
                        host_b = self.bn.get_parents(servers[service["name"]][j])[0]
                        paths = compute_path.print_all_paths(self.G,host_a,host_b)

                        # Delete first and last element
                        for k in range(len(paths)):
                            paths[k] = paths[k][slice(1,len( paths[k])-1)]

                        #print(host_a,'to',host_b,paths)
                        if len(paths) == 0 :
                            print("No Paht found")
                            exit(1)
                        else:
                            for path in paths:
                                found = False
                                for c in all_paths:
                                    if path == all_paths[c]:
                                        #We have found a duplicate path
                                        path_channel_map[str(i)+"_"+str(j)].append(c)
                                        found = True
                                        print("reuse", c,all_paths[c])
                                        break
                                if not found:
                                    # We have a new path
                                    path_name = service['name']+"P_"+str(current_path_index)
                                    all_paths[path_name] = path
                                    path_channel_map[str(i) + "_" + str(j)].append(path_name)
                                    current_path_index = current_path_index + 1
                                    print("make new", path_name, all_paths[path_name])
                                    self.bn.add_node(path_name, 2)
                                    for component in path:
                                        self.bn.add_edge(component, path_name)
                                    self.andNodeCPT(self.bn, path_name)

                # Connect the path to the channel; the channel is now completed
                # for endpoints in path_channel_map:
                #     channel_name =  service["name"]+"_"+endpoints
                #     if(len(path_channel_map[endpoints]) == 1):
                #         #No OR node
                #         self.bn.add_edge(path_channel_map[endpoints][0], channel_name)
                #     else:
                #         OR = service["name"]+"_"+endpoints+ "_OR"
                #         self.bn.add_node(OR, 2)
                #         for path in path_channel_map[endpoints]:
                #             self.bn.add_edge(path, OR)
                #         self.orNodeCPT(self.bn, OR)
                #         self.bn.add_edge(OR, channel_name)
                #     self.andNodeCPT(self.bn, channel_name)


                print("Add replication semantics",threshold)
                K = service["name"] + "_K"
                self.bn.add_node(K, 2)

                for i in range(0, n_servers):
                    A = service["name"] + "_A_"+ str(i)
                    A_nodes.append(A)
                    self.bn.add_node(A,2)
                    for j in range(0, n_servers):
                        if (j > i):
                            a = i
                            b = j
                            self.bn.add_edge(channels[service["name"]][str(a) + "_" + str(b)], A)
                        elif (j < i):
                            a = j
                            b = i
                            self.bn.add_edge(channels[service["name"]][str(a) + "_" + str(b)], A)
                    self.knNodeCPT(self.bn,A,threshold-1)
                    self.bn.add_edge(A,K)
                self.weightedKnNodeCPT(self.bn,K,threshold,weights)
            else:
                #The read-one/write-all case
                for idx, server in enumerate(service["servers"]):
                    A_nodes.append(service["name"] + "_" + "R_" + str(idx))

            #computing external channel
            n_servers = len(A_nodes)
            external_channels = []
            for i in range(0, n_servers):
                ext = service["init"]
                channel_name = service["name"] + "_" + str(i) + "_" + ext  # here we have i< j
                external_channels.append(channel_name)
                path_channel_map[str(i) + "_" + ext] = []
                self.bn.add_node(channel_name, 2)
                # Connect src and dst with BN channel node
                self.bn.add_edge(A_nodes[i], channel_name)
                self.bn.add_edge(ext, channel_name)


            for i in range(0, n_servers):
                ext = service["init"]
                host_A = self.bn.get_parents(servers[service["name"]][i])[0]
                paths = compute_path.print_all_paths(self.G,host_A, ext)
                # Delete first and last element
                for k in range(len(paths)):
                    paths[k] = paths[k][slice(1, len(paths[k]) - 1)]

                if len(paths) == 0:
                    raise Exception("No Path Found")
                else:
                    for path in paths:
                        found = False
                        for c in all_paths:
                            if path == all_paths[c]:
                                # We have found a duplicate path
                                path_channel_map[str(i) + "_" + ext].append(c)
                                found = True
                                print("reuse", c, all_paths[c])
                                break
                        if not found:
                            # We have a new path
                            path_name = service['name'] + "P_" + str(current_path_index)
                            all_paths[path_name] = path
                            path_channel_map[str(i) + "_" + ext].append(path_name)
                            current_path_index = current_path_index + 1
                            print("make new", path_name, all_paths[path_name])
                            self.bn.add_node(path_name, 2)
                            for component in path:
                                self.bn.add_edge(component, path_name)
                            self.andNodeCPT(self.bn, path_name)

            # Connect the path to the channel; the channel is now completed
            for endpoints in path_channel_map:
                channel_name = service["name"] + "_" + endpoints
                if (len(path_channel_map[endpoints]) == 1):
                    # No OR node
                    self.bn.add_edge(path_channel_map[endpoints][0], channel_name)
                else:
                    OR = service["name"] + "_" + endpoints + "_OR"
                    self.bn.add_node(OR, 2)
                    for path in path_channel_map[endpoints]:
                        self.bn.add_edge(path, OR)
                    self.orNodeCPT(self.bn, OR)
                    self.bn.add_edge(OR, channel_name)
                self.andNodeCPT(self.bn, channel_name)

                # Connect the path to the channel; the channel is now completed


            OR = service["name"]
            self.bn.add_node(OR,2)
            for channel_name in external_channels:
                self.bn.add_edge(channel_name, OR)

            if threshold == n: #if write-all
                self.andNodeCPT(self.bn, OR)
            else:
                self.orNodeCPT(self.bn,OR)

            print(service["name"],"created")

        if 'application' not in self.app:
            return

        # Compute external (super) channels
        self.bn.add_node("A", 2) # Create app node

        for channel in self.app['application']['topology']:
            from_service = channel['from']
            to_service = channel['to']

            gateways_from = self.get_gateways(from_service)
            gateways_to = self.get_gateways(to_service)
            channel_name = "E_" + from_service + "_" + to_service
            or_channel_name = "OR_" + from_service + "_" + to_service
            self.bn.add_node(channel_name, 2)
            self.bn.add_node(or_channel_name, 2)

            paths = self.get_any_to_any_paths(gateways_from, gateways_to)

            for path in paths:
                path = set(path)
                found = False
                for c in all_paths:
                    if path == all_paths[c]:
                        # We have found an exisiting path
                        self.bn.add_edge(c, or_channel_name)  # I need here the channel name
                        found = True
                        print("reuse", c,all_paths[c])
                if not found:
                    # We have a new path
                    path_name =  "P_" + str(current_path_index)
                    all_paths[path_name] = path
                    current_path_index = current_path_index + 1
                    self.bn.add_node(path_name, 2)
                    self.bn.add_edge(path_name, or_channel_name)
                    for component in path:
                        self.bn.add_edge(component, path_name)
                    self.andNodeCPT(self.bn, path_name)
                    print("make new", path_name, all_paths[path_name])
            self.orNodeCPT(self.bn, or_channel_name)
            # Connect src and dst service with the super channel node
            self.bn.add_edge(or_channel_name, channel_name)
            self.bn.add_edge(from_service, channel_name)
            self.bn.add_edge(to_service, channel_name)
            self.andNodeCPT(self.bn, channel_name)

            self.bn.add_edge(channel_name, "A")

        self.andNodeCPT(self.bn, "A")
        print(self.bn.check_model())

    def get_gateways(self,service_name):
        for service in self.app['services']:
            if service['name'] == service_name:
                if not isinstance(service["init"], list):
                    return [service["init"]]
                else:
                    return service["init"]

    def get_any_to_any_paths(self,components_a, components_b):
        results = []
        for ca in components_a:
            for cb in components_b:
                paths = compute_path.print_all_paths(self.G, ca, cb)
                for k in range(len(paths)):
                    paths[k] = paths[k][slice(1, len(paths[k]) - 1)]
                    if len(paths[k]):
                        results.append(paths[k])
        if not len(results):
            raise Exception("No Path Found")
        return results

