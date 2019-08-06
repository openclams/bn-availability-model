import pyAgrum as gum
import numpy as np
import BayesianNetworks.pyagrum.operators as ops




class BayesianNetModel:

    def __init__(self,G,app,andNodeCPT = ops.and_node, orNodeCPT= ops.or_node, knNodeCPT=ops.kn_node):
        self.G = G
        self.bn = gum.BayesNet('App')
        self.app = app
        self.andNodeCPT = andNodeCPT
        self.orNodeCPT = orNodeCPT
        self.knNodeCPT = knNodeCPT
        self.construct_bn()


    def construct_bn(self):
        for node_name in self.G.V:
            # node_name contains the string id of a component
            # For each node in V we create a node in the BN with binary state
            self.bn.add(node_name,2)

        for node_src_name in self.G.V:
            # For each node_name we get the acctual node object
            # The Node object contains an array of strings with children node ids
            for node_dst in self.G.V[node_src_name].cfc["children"]:
                # For each child node id we insert an arc
                #print("Add arc (",node_src_name,node_dst.name,")" )
                self.bn.addArc(node_src_name,node_dst.name)
                # We have no build the common failure cause tree
                # TODO: At this point we need insert a mechanism to resolve cycles in the common failure cause structure

        #bngraph.pdfize(bn,"step0.png");
        for node_name in self.G.V:
            # For each node string id, we associate a an AND CPT with the corresponding BN node
            self.andNodeCPT(self.bn, node_name)

            # Now we need to add at the last row of the CPT, where all conditions are true, the availability
            if isinstance(self.bn.cpt(node_name)[-1],(np.ndarray)):
                # IF the last row is still an array, i.e. no root nodes
                self.bn.cpt(node_name)[1] = np.array([1-self.G.V[node_name].availability,self.G.V[node_name].availability])
            else:
                # If we have a root node
                self.bn.cpt(node_name)[0] = 1 - self.G.V[node_name].availability
                self.bn.cpt(node_name)[1] = self.G.V[node_name].availability

        #Servers is a dic. The keys are the service names and the values are array with the string ids of the servers
        servers = {}
        # Channels is a dic. The keys are the service names and the values are dics where the keys are string concatetion of
        # server indexes between any src dst pair. The value is the name of the channel.
        channels = {}
        for service in self.app["services"]:
            # For each service we create all servers nodes
            #print ("Service", service["name"],"found")
            servers[ service["name"] ] = []  # store all server names per service in this dic
            # We iterate over all hosts, i.e. deployments
            # Server do not have names, this version does not support nested k:n service models yet
            for idx, host in enumerate(service["servers"]):
                server_name = service["name"]+"_"+"R_"+str(idx)
                servers[service["name"]].append(server_name)
                # Add BN nodes for each server of the service
                self.bn.add(server_name, 2)
                # Connect the servers with the appropriate hosts
                self.bn.addArc(host, server_name)
                #print(host,server_name,self.bn.cpt(server_name).var_names)
                # Add an AND CPT to the server BN node
                self.andNodeCPT(self.bn, server_name)
                # TODO: At this point I do no assume that server names are listed int he deployment file

            n_servers = len(service["servers"])
            channels[service["name"]] = {} # store here all internal channels
            # Now we create the channel BN nodes for every server pair
            # We have undreicted edges, therefore, we only iterate between every pair without backedge (n/2)
            for i in range(0,n_servers):
                for j in range(i+1,n_servers):
                    channel_name = service["name"]+"_"+str(i)+"_"+str(j)  # here we have i< j
                    # e.g.Channel for 5 to 3 is "3_5"
                    channels[service["name"]][str(i)+"_"+str(j)] = channel_name
                    self.bn.add(channel_name, 2)
                    # Connect src and dst with BN channel node
                    self.bn.addArc(servers[service["name"]][i], channel_name)
                    self.bn.addArc(servers[service["name"]][j], channel_name)
                    # Each BN channel node is an AND node


            #print("Add paths to channels", service["name"])
            # One ore more channels can have the same path
            # in all paths with store as key the unique path names and as values the network components of the path as array
            all_paths = {}
            # Here are key the src dst part as string and the value is the path name as stirng, e.g. P1 node
            path_channel_map = {}
            # We keep track how many unique paths we have found
            current_path_index = 1
            #We iterate over each src dst pair and we compute a path
            for i in range(0, n_servers):
                for j in range(i + 1, n_servers):
                    host_a = self.bn.cpt(servers[service["name"]][i]).var_names[0] # get host, which is a parent node of the server node
                    host_b = self.bn.cpt(servers[service["name"]][j]).var_names[0]
                    paths = self.G.print_all_paths(host_a,host_b)
                    # Delete first and last element
                    for k in range(len(paths)):
                        paths[k] = paths[k][slice(1,len( paths[k])-1)]

                    #print(host_a,'to',host_b,paths)
                    if len(paths) == 0 :
                        print("No Paht found")
                        exit(1)
                    else:
                        # TODO: We only consider the frist path, we should consider all paths with an OR node later
                        path = set(paths[0])
                        found = False
                        for c in all_paths:
                            if path == all_paths[c]:
                                #We have found a duplicate path
                                path_channel_map[str(i)+"_"+str(j)] = c
                                found = True
                        if not found:
                            # We have a new path
                            path_name = service["name"]+"_P_"+str(current_path_index)
                            all_paths[path_name] = path
                            path_channel_map[str(i) + "_" + str(j)] = path_name
                            current_path_index = current_path_index + 1
            #print("Connect paths to channels")
            # Connect all components with the paths
            for path in all_paths:
                self.bn.add(path, 2)
                for component in all_paths[path]:
                    self.bn.addArc(component, path)
                self.andNodeCPT(self.bn,path)
            # Connect the path to the channel; the channel is now completed
            for endpoints in path_channel_map:
                channel_name =  service["name"]+"_"+endpoints
                self.bn.addArc(path_channel_map[endpoints],channel_name)
                self.andNodeCPT(self.bn,channel_name)


            #print("Add replication semantics")
            K = service["name"] + "_K"
            self.bn.add(K, 2)
            A_nodes = []
            for i in range(0, n_servers):
                A = service["name"] + "_A_"+ str(i)
                A_nodes.append(A)
                self.bn.add(A,2)
                for j in range(0, n_servers):
                    if (j > i):
                        a = i
                        b = j
                        self.bn.addArc(channels[service["name"]][str(a) + "_" + str(b)], A)
                    elif (j < i):
                        a = j
                        b = i
                        self.bn.addArc(channels[service["name"]][str(a) + "_" + str(b)], A)
                self.knNodeCPT(self.bn,A,service["k"]-1)
                self.bn.addArc(A,K)
            self.knNodeCPT(self.bn,K,service["k"])

           #computing external channel
            n_servers = len(A_nodes)
            external_channels = []
            for i in range(0, n_servers):
                ext = service["init"]
                channel_name = service["name"] + "_" + str(i) + "_" + ext  # here we have i< j
                external_channels.append(channel_name)
                # e.g.Channel for 5 to 3 is "3_5"
                channels[service["name"]][str(i) + "_" + ext] = channel_name
                self.bn.add(channel_name, 2)
                # Connect src and dst with BN channel node
                self.bn.addArc(A_nodes[i], channel_name)
                self.bn.addArc(ext, channel_name)


            for i in range(0, n_servers):
                ext = service["init"]
                host_A = self.bn.cpt(servers[service["name"]][i]).var_names[0]
                paths = self.G.print_all_paths(host_A, ext)
                # Delete first and last element
                for k in range(len(paths)):
                    paths[k] = paths[k][slice(1, len(paths[k]) - 1)]

                if len(paths) == 0:
                    raise Exception("No Path Found")
                else:
                    # TODO: We only consider the frist path, we should consider all paths with an OR node later
                    path = set(paths[0])
                    found = False
                    for c in all_paths:
                        if path == all_paths[c]:
                            # We have found an exisiting path
                            self.bn.addArc( c , external_channels[i]) # I need here the channel name
                            found = True
                    if not found:
                        # We have a new path
                        path_name = service["name"] + "_P_" + str(current_path_index)
                        all_paths[path_name] = path
                        current_path_index = current_path_index + 1
                        self.bn.add(path_name, 2)
                        self.bn.addArc( path_name,external_channels[i])
                        for component in path:
                            self.bn.addArc(component, path_name)
                        self.andNodeCPT(self.bn, path_name)

                # Connect the path to the channel; the channel is now completed


            OR = service["name"] + "_EXT"
            self.bn.add(OR,2)
            for channel_name in external_channels:
                self.andNodeCPT(self.bn, channel_name)
                self.bn.addArc(channel_name, OR)

            self.orNodeCPT(self.bn,OR)

            self.bn.add( service["name"], 2)
            self.bn.addArc(K, service["name"])
            self.bn.addArc(OR, service["name"])
            self.andNodeCPT(self.bn,service["name"])




#bngraph.pdfize(bn,"step1.png");
