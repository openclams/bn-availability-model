from CloudGraph.Graph import Graph
from FaultTrees.FaultTree import FaultTree
import CloudGraph.ComputePath as compute_path
from typing import List, Set, Dict
from FaultTrees.Writer import Writer
from FaultTrees.MefWriter import MefWriter
from CloudGraph.Component import Component

class FaultTreeModel:

    def __init__(self,
                 G:Graph,
                 app
                 ):
        self.G: Graph = G
        self.app = app
        self.paths = {}
        self.current_path_index = 1
        self.ft = FaultTree()

    def write(self):
        Writer(self.ft)

    def writeXML(self):
        MefWriter(self.ft)

    def create_fault_dependencies(self):
        for node_src_name in self.G.nodes:
            gate = self.ft.add_node(node_src_name+"_be")
            gate.type = 'base'
            gate.prob = 1 - self.G.nodes[node_src_name].availability

            gate = self.ft.add_node(node_src_name)
            gate.type = 'or'
            self.ft.add_edge(node_src_name + "_be", node_src_name)

        for node_src_name in self.G.nodes:
            # For each node_name we get the actual node object
            # The Node object contains an array of strings with children node ids
            for node_dst in self.G.nodes[node_src_name].fault_dependencies["children"]:
                # For each child node id we insert an arc
                self.ft.add_edge(node_src_name, node_dst.name)
                # We have no build the common failure cause tree
                # TODO: At this point we need insert a mechanism to resolve cycles in the common failure cause structure

    def build(self):
        self.create_fault_dependencies()

        if 'application' not in self.app:
            #  It means we have only one service
            service = self.app["services"][0]

            self.add_service(service)

            gate = self.ft.add_node("TE")
            gate.type = "top"
            self.ft.add_edge(service["name"], "TE")
            self.clean()
            return

        for service in self.app["services"]:
            self.add_service(service)

        A_gate = self.ft.add_node("A")
        A_gate.type = 'or'

        client_gateways = self.get_gateways(self.app['application'])

        client_channel_gate = self.ft.add_node("Clients")
        client_channel_gate.type = 'and'
        # The first service is considered the init service
        service_gateways = self.get_gateways(self.app["services"][0])
        service_name = self.app["services"][0]["name"]
        for gateway in client_gateways:
            for s_gateway in service_gateways:
                channel_name = service_name + "_" + gateway + "_" + s_gateway
                path_nodes = self.add_paths(gateway, s_gateway)
                gateway_node = service_name + '_' + s_gateway
                self.create_channel(channel_name, gateway, gateway_node, path_nodes)
                self.ft.add_edge(channel_name, "Clients")

        self.ft.add_edge("Clients", "A")

        for channel in self.app['application']['topology']:
            from_service = channel['from']
            to_service = channel['to']

            gateways_from = self.get_gateways_name(from_service)
            gateways_to = self.get_gateways_name(to_service)

            channel_name = "E_" + from_service + "_" + to_service

            ch_gate = self.ft.add_node(channel_name)
            ch_gate.type = 'and'
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
                    self.ft.add_edge(channel_sub_name, channel_name)

            self.ft.add_edge(channel_name, "A")

        gate = self.ft.add_node("TE")
        gate.type = "top"
        self.ft.add_edge('A', "TE")
        self.clean()




    def add_service(self, service):
        hosts = [s["host"] for idx, s in enumerate(service["servers"])]
        server_names = [service["name"] + "_" + "R_" + str(idx) for idx, s in enumerate(service["servers"])]
        votes = [s["votes"] for idx, s in enumerate(service["servers"])]
        total_votes = sum(votes)
        threshold = service['threshold']

        use_direct_communication_pattern = 'communication' in service and service['communication'] == 'direct'

        # Key is a string concatenation of
        # server indexes between any src dst pair.
        # The value is the name of the channel.
        channels: Dict[str, str] = {}

        for idx, server in enumerate(service["servers"]):
            server_name = server_names[idx]
            # Add BN nodes for each server of the service
            gate = self.ft.add_node(server_name)
            gate.type = 'or'
            # Connect the servers with the appropriate hosts
            self.ft.add_edge(server['host'], server_name)

        A_nodes = []
        if not use_direct_communication_pattern:  # If not read-on/write-all
            # We iterate over each src dst pair and we compute the paths and their channels
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
                A_nodes.append(A) #+"_empty"
                #egate = self.ft.add_node(A+"_empty")
                #egate.type = "or"

                gate = self.ft.add_node(A)


                gate.n = len(hosts)-1
                gate.k = len(hosts) - threshold + 1

                #print(gate.k, "/" , gate.n)

                if gate.k > 1:
                    gate.type = "vote"  # here wrong
                else:
                    gate.type = "or"
                #self.ft.add_edge(gate.name,egate.name)

                temp_votes = []
                for j in range(0, len(hosts)):
                    if j > i:
                        a = i
                        b = j
                        channel_name = service["name"] + "_" + str(a) + "_" + str(b)
                        self.ft.add_edge(channel_name, A)
                        temp_votes.append(votes[b])
                    elif j < i:
                        a = j
                        b = i
                        channel_name = service["name"] + "_" + str(a) + "_" + str(b)
                        self.ft.add_edge(channel_name, A)
                        temp_votes.append(votes[b])
                # self.knNodeCPT(self.bn,A,threshold-1)
                # We subtract the votes of the i-th replica because we assume it allready voted since it issues the protocol
                # self.weightedKnNodeCPT(self.bn, A, threshold - votes[i], temp_votes)
        else:
            # The read-one/write-all case
            for idx, server in enumerate(service["servers"]):
                A_nodes.append(service["name"] + "_" + "R_" + str(idx))

        # Create the service node
        service_node = service["name"]
        sgate = self.ft.add_node(service_node)
        sgate.type = "or"
        gateways = self.get_gateways(service)
        # Add external communication
        # TODO: Here we assume that every server is reachable from every gateway/front end.
        # However, we cloud also consider individual connections from gateways to hosts
        for gateway in gateways:

            gateway_name = service["name"] + '_' + gateway
            gate_node = self.ft.add_node(gateway_name)

            for i in range(0, len(hosts)):
                channel_name = service["name"] + "_" + str(i) + "_" + gateway  # here we have i< j
                host = hosts[i]
                path_nodes = self.add_paths(gateway, host)
                self.create_channel(channel_name, gateway, A_nodes[i], path_nodes)
                self.ft.add_edge(channel_name, gateway_name)

            if use_direct_communication_pattern:
                if threshold == total_votes:
                    gate_node.type = 'or'
                elif threshold == 1:
                    gate_node.type = 'and'
                else:
                    gate_node.type = 'vote'
                    gate_node.n = len(hosts)
                    gate_node.k = len(hosts) - threshold + 1
            else:
                gate_node.type = 'and'

            self.ft.add_edge(gateway_name, service_node)





    def  clean(self):
        found = False
        for key in list(self.ft.gates.keys()):
            if len(self.ft.gates[key].output_gates) == 0 and self.ft.gates[key].name != "TE":
                for key2 in list(self.ft.gates.keys()):
                    gate = self.ft.gates[key]
                    if gate  in self.ft.gates[key2].output_gates:
                        self.ft.gates[key2].output_gates.remove(gate)
                del self.ft.gates[key]
                found = True
        if found:
            self.clean()

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
                if not found: #and len(path) > 0:
                    # We have a new path
                    path_name = "P_" + str(self.current_path_index)
                    self.paths[path_name] = path
                    results.append(path_name)
                    self.current_path_index = self.current_path_index + 1
                    # print("make new", path_name, self.paths[path_name])
                    gate = self.ft.add_node(path_name)
                    gate.type = "or"
                    for component in path:
                        self.ft.add_edge(component, path_name)
                    if len(path) == 0:
                        gate = self.ft.add_node(path_name+"_be")
                        gate.type = "base"
                        gate.prob = 0
                        self.ft.add_edge(path_name+"_be", path_name)
        return results

    def create_channel(self,channel_name,src,dest,path_nodes):
        # Add the inter server channels
        gate = self.ft.add_node(channel_name)
        gate.type = "or"
        self.ft.add_edge(src, channel_name)
        self.ft.add_edge(dest, channel_name)
        # connect paths to channel
        if len(path_nodes) == 1:
            # In case we have one path
            self.ft.add_edge(path_nodes[0], channel_name)
        elif len(path_nodes) > 1:
            # In case we have multiple paths
            channel_or_node = channel_name + "_OR"
            gate = self.ft.add_node(channel_or_node)
            gate.type = "and"
            for path_node_name in path_nodes:
                self.ft.add_edge(path_node_name, channel_or_node)
            self.ft.add_edge(channel_or_node, channel_name)

    def get_gateways(self,service):
        if not isinstance(service["init"], list):
            return [service["init"]]
        else:
            return service["init"]

    def get_gateways_name(self, service_name):
        for service in self.app['services']:
            if service['name'] == service_name:
                return self.get_gateways(service)