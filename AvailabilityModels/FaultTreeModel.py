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
            # For each node_name we get the acctual node object
            # The Node object contains an array of strings with children node ids
            for node_dst in self.G.nodes[node_src_name].fault_dependencies["children"]:
                # For each child node id we insert an arc
                self.ft.add_edge(node_src_name, node_dst.name)
                # We have no build the common failure cause tree
                # TODO: At this point we need insert a mechanism to resolve cycles in the common failure cause structure

    def build(self):
        self.create_fault_dependencies()
        for service in self.app["services"]:
            self.add_service(service)

    def add_service(self, service):
        hosts = [s["host"] for idx, s in enumerate(service["servers"])]
        server_names = [service["name"] + "_" + "R_" + str(idx) for idx, s in enumerate(service["servers"])]
        votes = [s["votes"] for idx, s in enumerate(service["servers"])]
        total_votes = sum(votes)
        threshold = service['threshold']
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
        if not (threshold == total_votes or threshold == 1):  # If not read-on/write-all
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

                gate.k = threshold
                gate.n = len(hosts)-1
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

        gateways = self.get_gateways(service)
        # Add external communication
        # TODO: Here we assume that every server is reachable from every gateway/front end.
        # However, we cloud also consider individual connections from gateways to hosts
        for gateway in gateways:
            for i in range(0, len(hosts)):
                channel_name = service["name"] + "_" + str(i) + "_" + gateway  # here we have i< j
                host = hosts[i]
                path_nodes = self.add_paths(gateway, host)
                self.create_channel(channel_name, gateway, A_nodes[i], path_nodes)
                self.ft.add_edge(channel_name, service_node)

        # Finalize the service graph
        if threshold == total_votes:  # if write-all
            sgate.type = "or"
        else:
            sgate.type = "and"
        # print(service["name"], "created")

        gate = self.ft.add_node("TE")
        gate.type = "top"
        self.ft.add_edge(service_node,"TE")
        self.clean()


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