from pgmpy.models import BayesianModel
import numpy as np
import BayesianNetworks.pgmpy.operators as ops
from CloudGraph.Graph import Graph
from typing import List, Set, Dict, Optional
import CloudGraph.ComputePath as compute_path
from CloudGraph.Component import Component
from pgmpy.factors.discrete import TabularCPD


class BayesianNetModel:

    def __init__(self,
                 G: Graph,
                 app,
                 andNodeCPT=ops.and_node,
                 orNodeCPT=ops.or_node,
                 knNodeCPT=ops.kn_node,
                 weightedKnNodeCPT=ops.weighted_kn_node):
        self.G: Graph = G
        self.bn: BayesianModel = BayesianModel()
        self.app = app
        self.andNodeCPT = andNodeCPT
        self.orNodeCPT = orNodeCPT
        self.knNodeCPT = knNodeCPT
        self.weightedKnNodeCPT = weightedKnNodeCPT
        self.paths = {}
        # One ore more channels can have the same path
        # in all paths with store as key the unique path names and as values the network components of the path as array
        self.current_path_index = 1
        self.construct_bn()

    def create_fault_dependencies(self, bn: BayesianModel, nodes: Dict[str, Component]):
        for node_src_name in nodes:
            # node_name contains the string id of a component
            # For each node in V we create a node in the BN with binary state
            bn.add_node(node_src_name, 2)
            cpd = TabularCPD(variable=node_src_name, variable_card=2, values=[[1, 0]])
            bn.add_cpds(cpd)

        for node_src_name in nodes:
            # For each node_name we get the acctual node object
            # The Node object contains an array of strings with children node ids
            for node_dst in nodes[node_src_name].fault_dependencies["children"]:
                # For each child node id we insert an arc
                bn.add_edge(node_src_name, node_dst.name)
                # We have no build the common failure cause tree
                # TODO: At this point we need insert a mechanism to resolve cycles in the common failure cause structure

        for node_name in nodes:
            # For each node string id, we associate a an AND CPT with the corresponding BN node

            try:
                self.andNodeCPT(bn, node_name)
            except:
                parents = list(bn.get_parents(node_name))
                print(bn.get_cardinality(parents[0]))
                print(bn.get_cardinality(parents[1]))
                exit()
            # TODO: At this point we can insert the mechanism to implement any arbitrary FT to BN model

            # Now we need to add at the last row of the CPT, where all conditions are true, the availability
            if len(list(bn.get_parents(node_name))) > 0:
                # IF the last row is still an array, i.e. no root nodes
                bn.get_cpds(node_name).values[:, bn.get_cpds(node_name).values.shape[1] - 1] = np.array(
                    [1 - nodes[node_name].availability,
                     nodes[node_name].availability])
            else:
                # If we have a root node
                bn.get_cpds(node_name).values = np.array([1 - nodes[node_name].availability,
                                                          nodes[node_name].availability])

    def add_service(self, service):

        hosts = [s["host"] for idx, s in enumerate(service["servers"])]

        server_names = [service["name"] + "_" + "R_" + str(idx) for idx, s in enumerate(service["servers"])]

        votes = [s["votes"] for idx, s in enumerate(service["servers"])]

        total_votes = sum(votes)

        threshold = service['threshold']

        is_voting_based = all([v == 1 for v in votes])

        access_one = threshold == 1

        access_all = threshold == total_votes

        use_direct_communication_pattern = 'communication' in service and service['communication'] == 'direct'

        for idx, server in enumerate(service["servers"]):

            availability = 1

            if 'availability' in server:
                availability = server['availability']

            server_name = server_names[idx]
            # Add BN nodes for each server of the service
            self.bn.add_node(server_name, 2)
            # Connect the servers with the appropriate hosts
            self.bn.add_edge(server['host'], server_name)
            # print(host,server_name,self.bn.cpt(server_name).var_names)
            # Add an AND CPT to the server BN node
            self.andNodeCPT(self.bn, server_name)

            self.bn.get_cpds(server_name).values[:, self.bn.get_cpds(server_name).values.shape[1] - 1] = np.array(
                [1 - availability,
                 availability])

            # print(self.bn.get_cpds(server_name))

        A_nodes = []
        if use_direct_communication_pattern:
            for idx, server in enumerate(service["servers"]):
                # Here we use the replica names
                A_nodes.append(service["name"] + "_" + "R_" + str(idx))
        else:

            # Apply indirect communication pattern.
            # We iterate over each src and dst pair and we compute the paths and their channels
            for i in range(0, len(hosts)):
                for j in range(i + 1, len(hosts)):
                    # get host, which is a parent node of the server node
                    host_a = hosts[i]
                    host_b = hosts[j]
                    path_nodes = self.add_paths(host_a, host_b)
                    channel_name = service["name"] + "_" + str(i) + "_" + str(j)
                    self.create_channel(channel_name, server_names[i], server_names[j], path_nodes)

            # print("Add replication semantics",votes, threshold)
            for i in range(0, len(hosts)):
                A = service["name"] + "_A_" + str(i)
                A_nodes.append(A)
                self.bn.add_node(A, 2)
                temp_votes = []
                for j in range(0, len(hosts)):
                    if j > i:
                        a = i
                        b = j
                        channel_name = service["name"] + "_" + str(a) + "_" + str(b)
                        self.bn.add_edge(channel_name, A)
                        temp_votes.append(votes[b])
                    elif j < i:
                        a = j
                        b = i
                        channel_name = service["name"] + "_" + str(a) + "_" + str(b)
                        self.bn.add_edge(channel_name, A)
                        temp_votes.append(votes[b])

                if access_all:
                    self.andNodeCPT(self.bn, A)
                elif is_voting_based:
                    # We subtract the votes of the i-th replica because we assume it
                    # already voted since it issues the protocol
                    self.knNodeCPT(self.bn,A,threshold-1)
                else:
                    self.weightedKnNodeCPT(self.bn, A, threshold - votes[i], temp_votes)


        # Create the service node
        service_node = service["name"]

        self.bn.add_node(service_node, 2)

        gateways = self.get_gateways(service)
        # Add external communication
        # Here we assume that every server is reachable from every gateway/front end.
        # However, we could also consider individual connections from gateways to hosts
        for gateway in gateways:

            gateway_name = service["name"] + '_' + gateway

            self.bn.add_node(gateway_name, 2)

            for i in range(0, len(hosts)):

                channel_name = service["name"] + "_" + str(i) + "_" + gateway

                host = hosts[i]

                path_nodes = self.add_paths(gateway, host)

                self.create_channel(channel_name, gateway, A_nodes[i], path_nodes)

                self.bn.add_edge(channel_name, gateway_name)

            if use_direct_communication_pattern:
                if access_all:
                    self.andNodeCPT(self.bn, gateway_name)
                elif access_one:
                    self.orNodeCPT(self.bn, gateway_name)
                else:
                    self.knNodeCPT(self.bn, gateway_name, threshold)
            else:
                self.orNodeCPT(self.bn, gateway_name)

            self.bn.add_edge(gateway_name, service_node)

        self.orNodeCPT(self.bn, service_node)

    def create_channel(self, channel_name, src, dest, path_nodes):
        # Add the inter server channels
        self.bn.add_node(channel_name, 2)
        self.bn.add_edge(src, channel_name)
        self.bn.add_edge(dest, channel_name)
        # connect paths to channel
        if len(path_nodes) == 1:
            # In case we have one path
            self.bn.add_edge(path_nodes[0], channel_name)
        else:
            # In case we have multiple paths
            channel_or_node = channel_name + "_OR"
            self.bn.add_node(channel_or_node, 2)
            for path_node_name in path_nodes:
                self.bn.add_edge(path_node_name, channel_or_node)
            self.orNodeCPT(self.bn, channel_or_node)
            self.bn.add_edge(channel_or_node, channel_name)
        self.andNodeCPT(self.bn, channel_name)

    def add_paths(self, src, dest):
        results = []
        paths = compute_path.print_all_paths(self.G, src, dest)

        # Delete first and last element
        for k in range(len(paths)):
            paths[k] = paths[k][slice(1, len(paths[k]) - 1)]

        if len(paths) == 0:
            print("No Paht found")
            exit(1)
        else:
            for path in paths:
                found = False
                for c in self.paths:
                    if path == self.paths[c]:
                        # We have found a duplicate path
                        results.append(c)
                        found = True
                        # print("reuse", c, self.paths[c])
                        break
                if not found:
                    # We have a new path
                    path_name = "P_" + str(self.current_path_index)
                    self.paths[path_name] = path
                    results.append(path_name)
                    self.current_path_index = self.current_path_index + 1
                    # print("make new", path_name, self.paths[path_name])
                    self.bn.add_node(path_name, 2)
                    for component in path:
                        self.bn.add_edge(component, path_name)
                    self.andNodeCPT(self.bn, path_name)
        return results

    def construct_bn(self):
        self.create_fault_dependencies(self.bn, self.G.nodes)
        for service in self.app["services"]:
            self.add_service(service)

        if 'application' not in self.app:
            # Stop here. It means we have only one service
            return
        # Compute external (super) channels
        self.bn.add_node("A", 2)  # Create app node

        # User service accessibility
        client_gateways = self.get_gateways(self.app['application'])
        self.bn.add_node("Clients", 2)  # Create app node
        for gateway in client_gateways:
            service_gateways = self.get_gateways(self.app["services"][0])
            service_name = self.app["services"][0]["name"]
            for s_gateway in service_gateways:
                channel_name = service_name + "_" + gateway + "_" + s_gateway
                path_nodes = self.add_paths(gateway, s_gateway)
                gateway_node = service_name + '_' + s_gateway
                self.create_channel(channel_name, gateway, gateway_node, path_nodes)
                self.bn.add_edge(channel_name, "Clients")

        self.bn.add_edge("Clients", "A")
        self.orNodeCPT(self.bn, "Clients")

        for channel in self.app['application']['topology']:
            from_service = channel['from']
            to_service = channel['to']

            gateways_from = self.get_gateways_name(from_service)
            gateways_to = self.get_gateways_name(to_service)

            channel_name = "E_" + from_service + "_" + to_service

            self.bn.add_node(channel_name, 2)

            # We consider all channels that lead from one gateway to the other
            # we make on channel that contains all the external paths
            # and the channel depends on the service node of the services
            # path_nodes = []
            for gf in gateways_from:
                for gt in gateways_to:
                    # --path_nodes.extend(self.add_paths(gf, gt))
                    channel_sub_name = from_service + "_" + to_service + "_" + gateway + "_" + s_gateway
                    from_service_gateway = from_service + '_' + gf
                    to_service_gateway = to_service + '_' + gt
                    self.create_channel(channel_sub_name, from_service_gateway, to_service_gateway,
                                        self.add_paths(gf, gt))
                    self.bn.add_edge(channel_sub_name, channel_name)

            self.orNodeCPT(self.bn, channel_name)
            self.bn.add_edge(channel_name, "A")

        self.andNodeCPT(self.bn, "A")
        # print(self.bn.check_model())

    def get_gateways(self, service):
        if not isinstance(service["init"], list):
            return [service["init"]]
        else:
            return service["init"]

    def get_gateways_name(self, service_name):
        for service in self.app['services']:
            if service['name'] == service_name:
                return self.get_gateways(service)
