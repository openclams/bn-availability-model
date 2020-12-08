from CloudGraph.Graph import Graph
from CloudGraph.Component import Component
from CloudGraph.Host import Host
import CloudGraph.ComputePath as compute_path
import subprocess, os
import re
import argparse
from typing import Set, List, Dict
import itertools


class PrismModel:

    def __init__(self,
                 G: Graph,
                 app,
                 temp_file_name: str = "cim.sm"):
        """

        @param G: Infrastructure Graph
        @param app: Deployment file
        @param temp_file_name:  Output-file name
        """
        self.G: Graph = G
        self.app = app
        self.model_name: str = temp_file_name
        self.f = open(self.model_name, "w+")
        self.paths = {}


    def build(self):
        self.f.write("ctmc\n\n")
        self.build_fault_dependency_graph()
        for service in self.app["services"]:
            self.build_service(service)

        if 'application' not in self.app:
            # Stop here. It means we have only one service
            self.f.close()
            return

        self.build_application()
        self.f.close()

    def build_fault_dependency_graph(self):
        for node in self.G.nodes.values():
            self.build_component_module(node)

    def build_component_module(self, node: Component):
        # is_working is the variable name which stores state of the module
        var_name = node.name + "_w"
        # sync_failure is the name of the action to sync (and propagate a fault) with its child
        # components if this component fails
        sync_failure = node.name + "_failure"
        # sync_repair is the name of the action to sync if this component is repaired
        sync_repair = node.name + "_repaired"

        MTTF = 1 / (1 - self.G.nodes[node.name].availability)
        MTTR = 1

        # Format the failure and repair rate to floats
        # with 8th decimal precision
        failure_rate = "{:1.8f}".format(1 / MTTF)
        repair_rate = "{:1.8f}".format(1 / MTTR)

        self.f.write("module %s \n" % node.name)
        # Defining the working state
        # false = component failure
        # true = component is working
        self.f.write("\t %s: bool init true;\n" % var_name)
        # State change to not working when component fails
        self.f.write("\t [%s] %s -> %s:(%s' = false);\n" % (sync_failure, var_name, failure_rate, var_name))

        # State change on component repair (when all its ancestors are working)
        parent_nodes_working = "& ".join([parent.name + "_w" for parent in node.fault_dependencies["parents"]])
        if len(parent_nodes_working):
            parent_nodes_working = "& "+parent_nodes_working
        self.f.write("\t [%s] !%s %s -> %s:(%s' = true);\n" % (
        sync_repair, var_name, parent_nodes_working, repair_rate, var_name))

        for ascendant_node in self.get_ascendants(node):
            sync_failure = ascendant_node.name + "_failure"
            sync_repair = ascendant_node.name + "_repaired"
            self.f.write("\t [%s] true -> 1:(%s' = false);\n" % (sync_failure, var_name))
            self.f.write("\t [%s] true -> 1:(%s' = true);\n" % (sync_repair, var_name))

        self.f.write("endmodule\n\n")

    def build_service(self, service):
        service_name = service['name']
        threshold = service['threshold']
        if not isinstance(service["init"], list):
            service["init"] = [service["init"]]

        hosts = {}
        votes_per_host = {}
        for idx, server in enumerate(service['servers']):
            server["service"] = service
            server["id"] = idx

            self.build_server_module(server)

            host_name = server["host"]

            if host_name in hosts:
                hosts[host_name].append(server["name"])
                votes_per_host[host_name] += server["votes"]
            else:
                hosts[host_name] = [server["name"]]
                votes_per_host[host_name] = server["votes"]

        for host_name in hosts:
            self.write_variable(host_name + "_" + service_name, "+ ".join(hosts[host_name]))

        # At this point we cloud aggregate hosts by groups
        # But we will continue with hosts
        host_names = list(hosts.keys())
        num_entries = 2 ** len(host_names)
        host_combinations = []
        # every permutation of each group
        for i in range(num_entries):
            bin = "{0:0" + str(len(host_names)) + "b}"
            # print(bin.format(i))
            combination = bin.format(i)
            collect = set()
            for idx, b in enumerate(combination):
                if b == "1":
                    collect.add(host_names[idx])

            # count if the permutation has enough servers
            total = sum([votes_per_host[host_name] for host_name in collect])
            if total >= threshold:
                host_combinations.append(collect)

        total_votes = sum([votes_per_host[h] for h in votes_per_host])
        if threshold == 1 or threshold == total_votes:
            self.one_step_communication_scheme(service,host_combinations)
        else:
            self.two_step_communication_scheme(service,host_combinations)

    def two_step_communication_scheme(self,service, host_combinations):
        terms: List[str] = []
        init = service['init']
        for host_combination in host_combinations:
            paths_exp = []
            for source_host in host_combination:
                host_paths_exp = []
                for dest_host in host_combination:
                    if dest_host != source_host:
                        paths = self.get_paths(source_host, dest_host)
                        host_paths_exp.append("( %s_w & %s_w & (" % (source_host, dest_host) + "| ".join(paths) + "))\n")

                for entry in init:
                    paths = self.get_paths(source_host, entry)
                    paths_exp.append("(" + "&".join(["( %s_w & %s_w & (" %(source_host, entry) + "| ".join(paths) + "))","& ".join(host_paths_exp)])+")\n")


            host_names = [host + "_" + service['name'] for host in host_combination]
            term = "((%s >= %d) & %s)\n" % ("+ ".join(host_names), service['threshold'], "| ".join(paths_exp))
            terms.append(term)
        self.write_service_end_block(service, terms)

    def one_step_communication_scheme(self,service, host_combinations):
        terms: List[str] = []
        init = service['init']
        for host_combination in host_combinations:
            paths_exp = []
            for host in host_combination:
                for entry in init:
                    paths = self.get_paths(host,entry)
                    paths_exp.append("( %s_w & %s_w & (" %(host, entry) +"| ".join(paths)+"))\n")

            host_names = [host+ "_" + service['name'] for host in host_combination]
            term = "((%s >= %d) & %s)\n" % ("+ ".join(host_names),service['threshold'],"& ".join(paths_exp))
            terms.append(term)

        self.write_service_end_block(service, terms)

    def write_service_end_block(self,service,terms):
        label = "availability_%s" % service['name']
        reward_name = "time_unavailable_%s" % service['name']
        self.write_variable(label, "| ".join(terms))
        self.write_label(label, "| ".join(terms))
        self.write_reward(reward_name, label)


    def build_server_module(self, server):
        node_name = server['service']["name"] + "_" + str(server["id"])
        server['name'] = node_name + "_w"
        var_name = server['name']
        votes = server['votes']
        host = server['host']
        self.f.write("module %s \n" % node_name)
        self.f.write("\t %s:  [0..%d] init %d;\n" % (var_name, votes, votes))

        sync_failure = host + "_failure"
        sync_repair = host + "_repaired"
        # If an
        self.f.write("\t [%s] true -> 1:(%s' = 0);\n" % (sync_failure, var_name))
        self.f.write("\t [%s] true -> 1:(%s' = %d);\n" % (sync_repair, var_name, votes))

        for ascendant_node in self.get_ascendants(self.G.nodes[host]):
            sync_failure = ascendant_node.name + "_failure"
            sync_repair = ascendant_node.name + "_repaired"
            self.f.write("\t [%s] true -> 1:(%s' = 0);\n" % (sync_failure, var_name))
            self.f.write("\t [%s] true -> 1:(%s' = %d);\n" % (sync_repair, var_name, votes))

        self.f.write("endmodule\n\n")

    def build_application(self):

        # Application channels contain the list of channels that
        # contains the list of paths in the channel
        application_channels: List[str] = []

        for channel in self.app['application']['topology']:
            source_service = self.get_service_by_name(channel['from'])
            dest_service = self.get_service_by_name(channel['to'])

            source_gateways = self.get_service_end_points(source_service)
            dest_gateways = self.get_service_end_points(dest_service)

            # Returns an array of path names
            paths = self.get_paths(source_gateways, dest_gateways)

            application_channel = "E_" + source_service + "_" + dest_service

            # Both services need to work and at least one path
            exp = "& ".join([source_service, dest_service, "(" + "| ".join(paths) + ")"])
            self.write_variable(application_channel, exp)

            application_channels.append(application_channel)

        name = "availability_"
        self.write_variable(name, "& ".join(application_channels))
        self.write_label(name, "& ".join(application_channels))

    def get_service_end_points(self, service):
        if not isinstance(service["init"], list):
            return [service["init"]]
        else:
            return service["init"]

    def get_service_by_name(self, name):
        for service in self.app['services']:
            if service['name'] == name:
                return service

    def get_ascendants(self, node: Component):
        # Make a copy of the parent list
        stack: List[Component] = [n for n in node.fault_dependencies["parents"]]
        visited: Set[Component] = set()
        while stack:
            n = stack.pop()
            if n not in visited:
                visited.add(n)
                stack.extend(set(n.fault_dependencies["parents"]) - visited)
        return visited

    def get_paths(self, sources, destinations):
        if not isinstance(sources,list):
            sources =  [sources]

        if not isinstance(destinations, list):
            destinations = [destinations]
        results = []
        for source in sources:
            for dest in destinations:
                paths = compute_path.print_all_paths(self.G, source, dest)

                # Delete first and last element
                for k in range(len(paths)):
                    paths[k] = paths[k][slice(1, len(paths[k]) - 1)]

                if len(paths) == 0:
                    print("No Paht found")
                    exit(1)

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
                        path_name = "P_" + str(len(self.paths.keys())+1)
                        self.paths[path_name] = path
                        results.append(path_name)
                        if len(path):
                            component_names = [c+"_w" for c in path]
                            self.write_variable(path_name, "& ".join(component_names))
                        else:
                            self.write_variable(path_name, "true")
        return results

    def write_variable(self, name, exp):
        self.f.write("formula %s = %s;\n" % (name, exp))

    def write_label(self, name, exp):
        self.f.write("label \"%s\" = %s;\n" % (name, exp))

    def write_reward(self, name: str, label_name: str):
        self.f.write("rewards \"%s\"\n !%s : 1; \nendrewards\n" % (name, label_name))

