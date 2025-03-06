'''




Link on how to change parameters of nx.draw:
https://github.com/networkx/networkx/blob/main/networkx/drawing/nx_pylab.py#L584



'''
from copy import deepcopy
from networkx.classes.function import path_weight as pw
from networkx.drawing.nx_pydot import graphviz_layout
import copy
import itertools
import matplotlib.pyplot as plt
import networkx as nx
import networkx.classes.function as cls_func
from . import numpy_dep as np
import pandas as pd
import pydot
import random
import time


def unpickle_graph(path):
    G_loaded = nx.read_gpickle(path)
    return G_loaded

def pickle_graph(path):
    nx.write_gpickle(path)

def find_reciprocal_connections(G,redundant=False):
    """
    Will give a list of the edges that are reciprocal connections
    ** only gives one version of the reciprocal connections so doesn't repeat**
    
    Arguments: 
    G: the graph to look for reciprocal connections
    redundant: whether to return a list with redundant connections or not (Ex: [(b,a)]  or [(b,a),(a,b)]
    
    Ex: 
    from datasci_tools import networkx_utils as xu
    xu = reload(xu)
    xu.find_reciprocal_connections(returned_network)
    """
    reciprocal_pairs = np.array([(u,v) for (u,v) in G.edges() if G.has_edge(v,u)])
    if redundant:
        return reciprocal_pairs
    
    filtered_reciprocal_pairs = []

    for a,b in reciprocal_pairs:       
        if len(nu.matching_rows(filtered_reciprocal_pairs,[b,a])) == 0:
            filtered_reciprocal_pairs.append([a,b])

    filtered_reciprocal_pairs = np.array(filtered_reciprocal_pairs)
    return filtered_reciprocal_pairs


def compare_endpoints(endpoints_1,endpoints_2,**kwargs):
    """
    comparing the endpoints of a graph: 
    
    Ex: 
    from datasci_tools import networkx_utils as xu
    xu = reload(xu)mess
    end_1 = np.array([[2,3,4],[1,4,5]])
    end_2 = np.array([[1,4,5],[2,3,4]])

    xu.compare_endpoints(end_1,end_2)
    """
    #this older way mixed the elements of the coordinates together to just sort the columns
    #return np.array_equal(np.sort(endpoints_1,axis=0),np.sort(endpoints_2,axis=0))
    
    #this is correct way to do it (but has to be exact to return true)
    #return np.array_equal(nu.sort_multidim_array_by_rows(endpoints_1),nu.sort_multidim_array_by_rows(endpoints_2))

    return nu.compare_threshold(nu.sort_multidim_array_by_rows(endpoints_1),
                                nu.sort_multidim_array_by_rows(endpoints_2),
                                **kwargs)


def endpoint_connectivity(endpoints_1,endpoints_2,
                         exceptions_flag=True,
                         print_flag=False):
    """
    Pupose: To determine where the endpoints of two branches are connected
    
    Example: 
    end_1 = np.array([[759621., 936916., 872083.],
       [790891., 913598., 806043.]])
    end_2 = np.array([[790891., 913598., 806043.],
       [794967., 913603., 797825.]])
       
    endpoint_connectivity(end_1,end_2)
    >> {0: 1, 1: 0}
    """
    connections_dict = dict()
    
    stacked_endpoints = np.vstack([endpoints_1,endpoints_2])
    endpoints_match = nu.get_matching_vertices(stacked_endpoints)
    
    if len(endpoints_match) == 0:
        print_string = f"No endpoints matching: {endpoints_match}"
        if exceptions_flag:
            raise Exception(print_string)
        else:
            print(print_string)
        return connections_dict
    
    if len(endpoints_match) > 1:
        print_string = f"Multiple endpoints matching: {endpoints_match}"
        if exceptions_flag:
            raise Exception(print_string)
        else:
            print(print_string)
    
    
    #look at the first connection
    first_match = endpoints_match[0]
    first_endpoint_match = first_match[0]
    
    if print_flag:
        print(f"first_match = {first_match}")
        print(f"first_endpoint_match = {endpoints_1[first_endpoint_match]}")
    
    
    if 0 != first_endpoint_match and 1 != first_endpoint_match:
        raise Exception(f"Non 0,1 matching node in first endpoint: {first_endpoint_match}")
    else:
        connections_dict.update({0:first_endpoint_match})
        
    second_endpoint_match = first_match[-1]
    
    if 2 != second_endpoint_match and 3 != second_endpoint_match:
        raise Exception(f"Non 2,3 matching node in second endpoint: {second_endpoint_match}")
    else:
        connections_dict.update({1:second_endpoint_match-2})
    
    return connections_dict



def combine_graphs(list_of_graphs):
    """
    Purpose: Will combine graphs, but if they have the same name
    then will combine the nodes
    
    Example: 
    xu = reload(xu)
    G1 = nx.from_edgelist([[1,2],[3,4],[2,3]])
    nx.draw(G1)
    plt.show()

    G2 = nx.from_edgelist([[3,4],[2,3],[2,5]])
    nx.draw(G2)
    plt.show()

    G3 = nx.compose_all([G1,G2])
    nx.draw(G3)
    plt.show()

    nx.draw(xu.combine_graphs([G1,G2,G3]))
    plt.show()

    """
    if len(list_of_graphs) == 1:
        return list_of_graphs[0]
    elif len(list_of_graphs) == 0:
        raise Exception("List of graphs is empty")
    else:
        return nx.compose_all(list_of_graphs)

def edge_to_index(G,curr_edge):
    matching_edges_idx = nu.matching_rows(G.edges_ordered(),curr_edge)
    if len(matching_edges_idx) == 1:
        return nu.matching_rows(G.edges_ordered(),curr_edge)[0]
    else: 
        return nu.matching_rows(G.edges_ordered(),curr_edge) 

def index_to_edge(G,edge_idx):
    return np.array(G.edges_ordered())[edge_idx]

def node_to_edges(G,node_number):
#     if type(node_number) != list:
#         node_number = [node_number]
    #print(f"node_number={node_number}")
    if type(G) == type(nx.Graph()):
        return list(G.edges(node_number))
    elif type(G) == type(GraphOrderedEdges()):
        return G.edges_ordered(node_number)
    else:
        raise Exception("not expected type for G")

        
def get_node_list(G,exclude_list = []):
    return [n for n in list(G.nodes()) if n not in exclude_list]

#from datasci_tools import numpy_utils as nu
def get_nodes_with_attributes_dict(G,attribute_dict):
    """
    
    
    """
    
    # --- 11/4 An aleration that instead calles the more efficient method ---
    if len(attribute_dict.keys()) == 1 and "coordinates" in attribute_dict.keys():
        return get_graph_node_by_coordinate(G,attribute_dict["coordinates"],return_single_value=False)
    
    node_list = []
    total_search_keys = list(attribute_dict.keys())
    for x,y in G.nodes(data=True):
        if len(set(total_search_keys).intersection(set(list(y.keys())))) < len(total_search_keys):
            #there were not enough keys in the node we were searching
            continue
        else:
            add_flag = True
            for search_key in total_search_keys:
                #print(f"y[search_key] = {y[search_key]}")
                #print(f"attribute_dict[search_key] = {attribute_dict[search_key]}")
                curr_search_val= y[search_key]
                #if type(curr_search_val) in [type(np.array([])),type(np.ndarray([])),list,trimesh.caching.TrackedArray]:
                if nu.is_array_like(curr_search_val):
                    if not nu.compare_threshold(np.array(curr_search_val),attribute_dict[search_key]):
                        add_flag=False
                        break
                else:
                    if y[search_key] != attribute_dict[search_key]:
                        add_flag=False
                        break
            if add_flag:
                #print("Added!")
                node_list.append(x)
    return node_list

def get_nodes_with_attribute_value(G,attribute,value,verbose = False):
    nodesAt5 = [x for x,y in G.nodes(data=True) if y[attribute]==value]
    if verbose:
        print(f"{len(nodesAt5)} nodes with {attribute} = {value}")
        
    return nodesAt5

def get_graph_node_by_coordinate_old(G,coordinate):
    match_nodes = get_nodes_with_attributes_dict(G,dict(coordinates=coordinate))
    #print(f"match_nodes = {match_nodes}")
    if len(match_nodes) != 1:
        raise Exception(f"Not just one node in graph with coordinate {coordinate}: {match_nodes}")
    else:
        return match_nodes[0]
    
def get_coordinate_by_graph_node(G,node):
    """
    Will get the coordinates of node or list of nodes
    
    """
    scalar_flag = False
    if not nu.is_array_like(node):
        scalar_flag = True
        node = [node]
    coords = xu.get_node_attributes(G,node_list=node)
    
    if scalar_flag:
        return coords[0]
    else:
        return coords
    
def get_graph_nodes_by_coordinates(G,coordinates):
    return [get_graph_node_by_coordinate(G,k) for k in coordinates]

def get_graph_node_by_coordinate(G,coordinate,return_single_value=True,
                                return_neg_one_if_not_find=False):
    """
    Much faster way of searching for nodes by coordinates
    
    """
    graph_nodes = np.array(list(G.nodes()))
    node_coordinates = get_node_attributes(G,node_list = graph_nodes)
    match_nodes = nu.matching_rows(node_coordinates,coordinate)
    if return_single_value:
        if len(match_nodes) != 1:
            if return_neg_one_if_not_find:
                return -1
            else:
                raise Exception(f"Not just one node in graph with coordinate {coordinate}: {match_nodes}")
        else:
            return graph_nodes[match_nodes[0]]
    else:
        return graph_nodes[match_nodes]

def get_all_nodes_with_certain_attribute_key(G,attribute_name):
    return nx.get_node_attributes(G,attribute_name)

#from datasci_tools import numpy_utils as nu
def get_node_attributes(G,attribute_name="coordinates",node_list=None,
                       return_array=True):
    #print(f"attribute_name = {attribute_name}")
    if node_list is None:
        node_list = list(G.nodes())
    
    if not nu.is_array_like(node_list):
        node_list = [node_list]
        
    if len(node_list) == 0:
        if return_array:
            return np.array([])
        else:
            return dict()
    
    
    attr_dict = nx.get_node_attributes(G,attribute_name)
    #print(f"attr_dict= {attr_dict}")
    if len(node_list)>0:
        #print("inside re-ordering")
        #attr_dict = dict([(k,v) for k,v in attr_dict.items() if k in node_list])
        attr_dict = dict([(k,attr_dict[k]) for k in node_list])
    
    if return_array:
        return np.array(list(attr_dict.values()))
    else: 
        return attr_dict
    
def remove_selfloops(UG):
    self_edges = nx.selfloop_edges(UG)
    #print(f"self_edges = {self_edges}")
    UG.remove_edges_from(self_edges)
    return UG

def get_neighbors(G,node,int_label=True):
    if int_label:
        try:
            return [int(n) for n in G[node]]
        except:
            return [int(n[1:]) for n in G[node]]
    else:
        return [n for n in G[node]]
    
def get_neighbors_simple(G,node,int_label=True):
    return [n for n in G[node]]
    
def neighbors(G,node):
    return [n for n in G[node]] 
    
def get_nodes_of_degree_k(G,degree_choice,degree_type="degree"):
    return [k for k,v in dict(getattr(G,degree_type)).items() if v == degree_choice]

def get_nodes_of_out_degree_k(G,degree_choice):
    return [k for k,v in dict(getattr(G,"out_degree")).items() if v == degree_choice]
def get_nodes_of_in_degree_k(G,degree_choice):
    return [k for k,v in dict(getattr(G,"in_degree")).items() if v == degree_choice]

def get_nodes_greater_or_equal_out_degree_k(G,degree_choice):
    return [k for k,v in dict(getattr(G,"out_degree")).items() if v >= degree_choice]
def get_nodes_greater_or_equal_in_degree_k(G,degree_choice):
    return [k for k,v in dict(getattr(G,"in_degree")).items() if v >= degree_choice]

def get_nodes_less_or_equal_out_degree_k(G,degree_choice):
    return [k for k,v in dict(getattr(G,"out_degree")).items() if v <= degree_choice]
def get_nodes_less_or_equal_in_degree_k(G,degree_choice):
    return [k for k,v in dict(getattr(G,"in_degree")).items() if v <= degree_choice]

def leaf_nodes(G):
    return xu.get_nodes_of_out_degree_k(G,0)
def non_leaf_nodes(G):
    return xu.get_nodes_greater_or_equal_out_degree_k(G,1)
    
end_nodes = leaf_nodes
# def get_nodes_of_out_degree_k_Di(G,degree_choice):
#     return [n for n in G.nodes() if len(G[n]) == degree_choice]

def get_nodes_greater_or_equal_degree_k(G,degree_choice):
    return [k for k,v in dict(G.degree).items() if v >= degree_choice]

def get_nodes_less_or_equal_degree_k(G,degree_choice):
    return [k for k,v in dict(G.degree).items() if v <= degree_choice]

def get_node_degree(G,node_name,
                   degree_type="in_and_out"):
    singular_flag = False
    if not nu.is_array_like(node_name):
        singular_flag = True
        node_name = [node_name]
        
    if degree_type == "in_and_out":
        degree_func = G.degree
    elif degree_type == "in":
        degree_func = G.in_degree
    elif degree_type == "out":
        degree_func = G.out_degree
        
    node_degrees = [degree_func[k] for k in node_name]
    if not singular_flag:
        return node_degrees
    else:
        return node_degrees[0]
    
def get_node_degree_out(G,node_name):
    return get_node_degree(G,node_name,
                   degree_type="out")

def get_node_degree_in(G,node_name):
    return get_node_degree(G,node_name,
                   degree_type="in")

def degree_distribution(G,degree_type="in_and_out"):
    if degree_type == "in_and_out":
        degree_func = G.degree
    elif degree_type == "in":
        degree_func = G.in_degree
    elif degree_type == "out":
        degree_func = G.out_degree
        
    return list(dict(degree_func).values())

def max_node_degree(G,degree_type="in_and_out"):
    return np.max(degree_distribution(G,degree_type=degree_type))
    
def get_coordinate_degree(G,coordinate):
    """
    Purpose: To return the degrees of coordinates
    inside of a graph
    
    """
    coordinate = np.array(coordinate).reshape(-1,3)
    endpoint_nodes = [xu.get_graph_node_by_coordinate(G,k) for k in coordinate]
    endpoint_degrees = np.array(xu.get_node_degree(G,endpoint_nodes))
    
    if len(coordinate) == 1:
        return endpoint_degrees[0]
    else:
        return endpoint_degrees
    


def set_node_attributes_dict(G,attrs):
    """
    Can set the attributes of nodes with dictionaries 
    
    ex: 
    G = nx.path_graph(3)
    attrs = {0: {'attr1': 20, 'attr2': 'nothing'}, 1: {'attr2': 3}}
    nx.set_node_attributes(G, attrs)
    G.nodes[0]['attr1']

    G.nodes[0]['attr2']

    G.nodes[1]['attr2']

    G.nodes[2]
    """
    nx.set_node_attributes(G, attrs)

def relabel_node_names(G,mapping,copy=False):
    G = nx.relabel_nodes(G, mapping, copy=copy)
    #print("Finished relabeling nodes")
    return G
    
rename_nodes = relabel_node_names
    
def get_all_attributes_for_nodes(G,node_list=[],
                       return_dict=False):
    if len(node_list) == 0:
        node_list = list(G.nodes())
    
    attributes_list = [] 
    attributes_list_dict = dict()
    for n in node_list:
        attributes_list.append(G.nodes[n])
        attributes_list_dict.update({n:G.nodes[n]})
    
    if return_dict:
        return attributes_list_dict
    else:
        return attributes_list
    
def get_node_attribute_dict(G,node):
    return dict(G.nodes[node])
    
# -------------- start of functions to help with edges ---------------#
def get_all_attributes_for_edges(G1,edges_list=[],return_dict=False):
    """
    Ex: 
    G1 = limb_concept_network
    xu.get_all_attributes_for_edges(G1,return_dict=True)
    """
    if len(edges_list) == 0:
        print("Edge list was 0 so generating sorted edges")
        edges_list = nu.sort_multidim_array_by_rows(G1.edges(),order_row_items=isinstance(G1,(nx.Graph)))
    elif len(edges_list) != len(G1.edges()):
        print(f"**Warning the length of edges_list ({len(edges_list)}) is less than the total number of edges for Graph**")
    else:
        pass

    attributes_list = [] 
    attributes_list_dict = dict()
    for u,v in edges_list:
        attributes_list.append(G1[u][v])
        attributes_list_dict.update({(u,v):G1[u][v]})
    
    
    if return_dict:
        return attributes_list_dict
    else:
        return attributes_list


def get_edges_with_attributes_dict(G,attribute_dict):
    if type(attribute_dict) != dict:
        raise Exception("Did not recieve dictionary for searching")
    total_edges = []
    total_searching_keys = list(attribute_dict.keys())
    for (u,v) in G.edges():
        if len(set(total_searching_keys).intersection(set(list(G[u][v])))) < len(total_searching_keys):
            continue
        else:
            match = True
            for k in total_searching_keys:
                if G[u][v][k] !=  attribute_dict[k]:
                    match = False
                    break
            if match:
                total_edges.append((u,v))
    return total_edges
               


def get_edge_attributes(G,attribute="order",edge_list=[],undirected=True):
    #print(f"edge_list = {edge_list}, type={type(edge_list)}, shape = {edge_list.shape}")
    #print("")
    edge_attributes = nx.get_edge_attributes(G,"order")
    #print(f"edge_attributes = {edge_attributes}")
    if len(edge_list) > 0:
        if undirected:
            total_attributes = []
            for e in edge_list:
                try:
                    total_attributes.append(edge_attributes[tuple(e)])
                except:
                    #try the other way around to see if it exists
                    try:
                        total_attributes.append(edge_attributes[tuple((e[-1],e[0]))])
                    except: 
                        print(f"edge_attributes = {edge_attributes}")
                        print(f"(e[-1],e[0]) = {(e[-1],e[0])}")
                        raise Exception("Error in get_edge_attributes")
            return total_attributes
        else:
            return [edge_attributes[tuple(k)] for k in edge_list]
    else:
        return edge_attributes

def get_edge_attributes_df(
    G,
    attributes, #= "presyn_soma_postsyn_soma_euclid_dist"
    return_df = True,
    return_array = False,
    ):
    """
    Purpose: To retrieve a dataframe of the
    edge attributes
    """
    if not nu.is_array_like(attributes):
        singular_flag = True
        attributes = [attributes]
    attribute_dict = {k:np.array(list(nx.get_edge_attributes(G,k).values()))
                     for k in attributes}

    if return_array:
        return_value = list(attribute_dict.values())
        if singular_flag:
            return return_value[0]
        else:
            return return_value

    if return_df:
        df = pd.DataFrame(attribute_dict)
        return df
    else:
        return attribute_dict

#import copy
# how you can try to remove a cycle from a graph
def remove_cycle(branch_subgraph, max_cycle_iterations=1000): 
    
    #branch_subgraph_copy = copy.copy(branch_subgraph)
    for i in range(max_cycle_iterations): 
        try:
            edges_in_cycle = nx.find_cycle(branch_subgraph)
        except:
            break
        else:
            #make a copy to unfreeze
            branch_subgraph = GraphOrderedEdges(branch_subgraph)
            #not doing random deletion just picking first edge
            picked_edge_to_delete = edges_in_cycle[-1]
            #print(f"picked_edge_to_delete = {picked_edge_to_delete}")
            branch_subgraph.remove_edge(picked_edge_to_delete[0],picked_edge_to_delete[-1])
            

    try:
        edges_in_cycle = nx.find_cycle(branch_subgraph)
    except:
        pass
    else:
        raise Exception("There was still a cycle left after cleanup")
    
    return branch_subgraph


def find_skeletal_distance_along_graph_node_path(G,node_path):
    """
    Purpose: To find the skeletal distance along nodes of
    a graph that represents a skeleton
    
    Pseudocode: 
    1) Get the coordinates of the nodes
    2) Find the distances between consecutive coordinates
    
    Ex: 
    find_skeletal_distance_along_graph_node_path(
                                                G = skeleton_graph,
                                                node_path = cycles_list[0]
                                                )
    
    """
    coordinates = get_node_attributes(G,node_list=node_path)
    total_distance = np.sum(np.linalg.norm(coordinates[:-1] - coordinates[1:],axis=1))
    return total_distance


def find_all_cycles(G, source=None, cycle_length_limit=None,time_limit = 1000):
    from datasci_tools import system_utils as su
    try:
        with su.time_limit(time_limit):
            """forked from networkx dfs_edges function. Assumes nodes are integers, or at least
            types which work with min() and > ."""
            if source is None:
                # produce edges for all components
                comp_list = [list(k) for k in list(nx.connected_components(G))]
                nodes=[i[0] for i in comp_list]
            else:
                # produce edges for components with source
                nodes=[source]
            # extra variables for cycle detection:
            cycle_stack = []
            output_cycles = set()

            def get_hashable_cycle(cycle):
                """cycle as a tuple in a deterministic order."""
                m = min(cycle)
                mi = cycle.index(m)
                mi_plus_1 = mi + 1 if mi < len(cycle) - 1 else 0
                if cycle[mi-1] > cycle[mi_plus_1]:
                    result = cycle[mi:] + cycle[:mi]
                else:
                    result = list(reversed(cycle[:mi_plus_1])) + list(reversed(cycle[mi_plus_1:]))
                return tuple(result)

            for start in nodes:
                #print(f"start = {start}")
                if start in cycle_stack:
                    continue
                cycle_stack.append(start)

                stack = [(start,iter(G[start]))]
                while stack:
                    #print(f"len(stack) = {len(stack)}")
                    parent,children = stack[-1]
                    try:
                        child = next(children)

                        if child not in cycle_stack:
                            cycle_stack.append(child)
                            stack.append((child,iter(G[child])))
                        else:
                            i = cycle_stack.index(child)
                            if i < len(cycle_stack) - 2: 
                                output_cycles.add(get_hashable_cycle(cycle_stack[i:]))

                    except StopIteration:
                        stack.pop()
                        cycle_stack.pop()
    except su.TimeoutException as e:
        print("Timed out when trying to find the cycles!")
        return []
        
    
    cycles_list = [list(i) for i in output_cycles]
    cycles_list_array = np.array(cycles_list)
    sorted_list = np.argsort([len(k) for k in cycles_list_array])[::-1]
    cycles_list_sorted = cycles_list_array[sorted_list]
    return list(cycles_list_sorted) 


def set_node_data(curr_network,node_name,curr_data,curr_data_label):
    
        node_attributes_dict = dict()
        if node_name not in list(curr_network.nodes()):
                raise Exception(f"Node {node_name} not in the concept map of the curent neuron before trying to add {node_name} to the concept graph")
        else:
            node_attributes_dict[node_name] = {curr_data_label:curr_data}
                
        #setting the actual attributes
        set_node_attributes_dict(curr_network,node_attributes_dict)

class GraphOrderedEdges(nx.Graph):
    """
    Example of how to use:
    - graph that has ordered edges
    
    xu = reload(xu)

    ordered_Graph = xu.GraphEdgeOrder()
    ordered_Graph.add_edge(1,2)
    ordered_Graph.add_edge(4,3)
    ordered_Graph.add_edge(1,3)
    ordered_Graph.add_edge(3,4)

    ordered_Graph.add_edges_from([(5,6),(2,3),(3,8)])
    xu.get_edge_attributes(ordered_Graph)

    xu.get_edge_attributes(ordered_Graph,"order")
    """
    def __init__(self,data=None,edge_order=dict()):
        super().__init__(data)
        if len(edge_order) > 0 and len(self.edges()) > 0 :
            #set the edge order
            nx.set_edge_attributes(self,name="order",values=dict([(tuple(k),edge_order[tuple(k)]) for k in list(self.edges())]))
            
        
    
    #make sure don't lose properties when turning to undirected
#     def to_undirected(self):
#         edge_order = get_edge_attributes(self)
#         #super().to_undirected()
#         #self.__init__(self,edge_order=edge_order)
        
    
    #just want to add some functions that ordered edges 
    def add_edge(self,u,v):
        """
        Will add the edge plus an order index
        """
        total_edges = len(self.edges())
        #print(f"Total edges already = {total_edges}")
        super().add_edge(u,v,order=total_edges)
    
    #will do the adding edges
    def add_edges_from(self,ebunch_to_add, **kwargs):
        
        #get the total edges
        total_edges = len(self.edges())
        #get the new labels
        
        ebunch_to_add = list(ebunch_to_add)
        
        if len(ebunch_to_add) > 0:
            #add the edges
            super().add_edges_from(ebunch_to_add,**kwargs)
            
            #changes the ebunch if has dictionary associated with it
            if len(ebunch_to_add[0]) == 3:
                ebunch_to_add = [(k,v) for k,v,z in ebunch_to_add]
                
            ending_edge_count = len(self.edges())
            
            new_orders= list(range(total_edges,total_edges + len(ebunch_to_add)))
            
#             print(f"total_edges = {total_edges}")
#             print(f"len(new_orders) = {len(new_orders)}")
#             print(f"len(ebunch_to_add) = {len(ebunch_to_add)}")
#             print(f"ending_edge_count = {ending_edge_count}")
            
            nx.set_edge_attributes(self,name="order",values=dict([(tuple(k),v) for v,k in zip(new_orders,ebunch_to_add)]))
        
    def add_weighted_edges_from(self, ebunch_to_add, weight='weight', **kwargs):
        
        self.add_edges_from(((u, v, {weight: d}) for u, v, d in ebunch_to_add),
                            **kwargs)
    
    #will get the edges in an ordered format
    def edges_ordered(self,*attr):
        """
        nbunch: 
        """
        try:
            returned_edges = np.array(list(super().edges(*attr))).astype("int")
        except:
            returned_edges = np.array(list(super().edges(*attr)))
        #print(f"returned_edges = {returned_edges}")
        #get the order of all of these edges
        if len(returned_edges)>0:
            try:
                orders = np.array(get_edge_attributes(self,attribute="order",edge_list=returned_edges)).astype("int")
            except:
                orders = np.array(get_edge_attributes(self,attribute="order",edge_list=returned_edges))
            return returned_edges[np.argsort(orders)]
        else:
            return returned_edges
        
    def reorder_edges(self):
        
        ord_ed = self.edges_ordered()
        if len(ord_ed)>0:
            nx.set_edge_attributes(self,name="order",values=dict([(tuple(k),v) for v,k in enumerate(ord_ed)]))
        else:
            pass #do nothing because no edges to reorder
        
    #functions that will do the deleting of edges and then reordering
    def remove_edge(self,u,v):
        #print("in remove edge")
        super().remove_edge(u,v)
        self.reorder_edges()
    
    
    #the add_weighted_edges_from will already use the add_edges_from
    def remove_edges_from(self,ebunch):
        super().remove_edges_from(ebunch)
        self.reorder_edges()
    
    #*************** overload delete vertex************
    def remove_node(self,n):
        super().remove_node(n)
        self.reorder_edges()
    
    def remove_nodes_from(self,nodes):
        super().remove_nodes_from(nodes)
        self.reorder_edges()
        
# ------------------ for neuron package -------------- #
def get_starting_node(G,attribute_for_start="starting_coordinate",only_one=True):
    starting_node_dict = get_all_nodes_with_certain_attribute_key(G,attribute_for_start)
    
    if only_one:
        if len(starting_node_dict) != 1:
            raise Exception(f"The number of starting nodes was not equal to 1: starting_node_dict = {starting_node_dict}")

        starting_node = list(starting_node_dict.keys())[0]
        return starting_node
    else:
        return list(starting_node_dict.keys())


def compare_networks(
    G1,
    G2,
    compare_edge_attributes=["all"],
    compare_edge_attributes_exclude=[],
    edge_threshold_attributes = ["weight"],
    edge_comparison_threshold=0,
    compare_node_attributes=["all"], 
    compare_node_attributes_exclude=[],
    node_threshold_attributes = ["coordinates","starting_coordinate","endpoints"],
    node_comparison_threshold=0,
    return_differences=False,
    print_flag=False
    ):
    """
    Purpose: To customly compare graphs based on the edges attributes and nodes you want to compare
    AND TO MAKE SURE THEY HAVE THE SAME NODE NAMES
    
    
    G1,G2,#the 2 graphs that will be compared
    compare_edge_attributes=[],#whether to consider the edge attributes when comparing
    edge_threshold_attributes = [], #the names of attributes that will be considered close if below edge_comparison_threshold
    edge_comparison_threshold=0, #the threshold for comparing the attributes named in edge_threshold_attributes
    compare_node_attributes=[], #whether to consider the node attributes when comparing
    node_threshold_attributes = [], #the names of attributes that will be considered close if below node_comparison_threshold
    node_comparison_threshold=0, #the threshold for comparing the attributes named in node_threshold_attributes
    print_flag=False
    
    
    Pseudocode:
    0) check that number of edges and nodes are the same, if not then return false
    1) compare the sorted edges array to see if equal
    2) compare the edge weights are the same (maybe within a threshold) (BUT MUST SPECIFY THRESHOLD)
    3) For each node name: 
    - check that the attributes are the same
    - can specify attribute names that can be within a certian threshold (BUT MUST SPECIFY THRESHOLD)
    
    
    Example: 
    # Testing of the graph comparison 
    network_copy = limb_concept_network.copy()
    network_copy_2 = network_copy.copy()

    #changing and seeing if we can pick up on the difference
    network_copy[1][2]["order"] = 55
    network_copy_2.nodes[2]["endpoints"] = np.array([[1,2,3],[4,5,6]])
    network_copy_2.nodes[3]["endpoints"] = np.array([[1,2,5],[4,5,6]])
    network_copy_2.remove_edge(1,2)

    xu.compare_networks(
        G1=network_copy,
        G2=network_copy_2,
        compare_edge_attributes=["all"],
        edge_threshold_attributes = [],
        edge_comparison_threshold=0,
        compare_node_attributes=["endpoints"], 
        node_threshold_attributes = ["endpoints"],
        node_comparison_threshold=0.1,
        print_flag=True
        )
        
    Example with directional: 
    #directional test 

    network_copy = limb_concept_network.copy()
    network_copy_2 = network_copy.copy()

    #changing and seeing if we can pick up on the difference

    network_copy_2.nodes[2]["endpoints"] = np.array([[1,2,3],[4,5,6]])
    network_copy_2.nodes[3]["endpoints"] = np.array([[1,2,5],[4,5,6]])
    del network_copy_2.nodes[12]["starting_coordinate"]
    #network_copy_2.remove_edge(1,2)

    xu.compare_networks(
        G1=network_copy,
        G2=network_copy_2,
        compare_edge_attributes=["all"],
        edge_threshold_attributes = [],
        edge_comparison_threshold=0,
        compare_node_attributes=["all"], 
        node_threshold_attributes = ["endpoints"],
        compare_node_attributes_exclude=["data"],
        node_comparison_threshold=0.1,
        print_flag=True
        )
    
    Example on how to use to compare skeletons: 
    skeleton_1 = copy.copy(total_skeleton)
    skeleton_2 = copy.copy(total_skeleton)
    skeleton_1[0][0] = np.array([558916.8, 1122107. ,  842972.8])

    sk_1_graph = sk.convert_skeleton_to_graph(skeleton_1)
    sk_2_graph = sk.convert_skeleton_to_graph(skeleton_2)

    xu.compare_networks(sk_1_graph,sk_2_graph,print_flag=True,
                     edge_comparison_threshold=2,
                     node_comparison_threshold=2)
    
    """
    
    total_compare_time = time.time()
    
    local_compare_time = time.time()
    if not nu.is_array_like(compare_edge_attributes):
        compare_edge_attributes = [compare_edge_attributes]
    
    if not nu.is_array_like(compare_edge_attributes):
        compare_edge_attributes = [compare_edge_attributes]
      
    differences_list = []
    return_value = None
    for i in range(0,1):
        #0) check that number of edges and nodes are the same, if not then return false
        if str(type(G1)) != str(type(G1)):
            differences_list.append(f"Type of G1 graph ({type(G1)}) does not match type of G2 graph({type(G2)})")
            break

        if len(G1.edges()) != len(G2.edges()):
            differences_list.append(f"Number of edges in G1 ({len(G1.edges())}) does not match number of edges in G2 ({len(G2.edges())})")
            break

        if len(G1.nodes()) != len(G2.nodes()):
            differences_list.append(f"Number of nodes in G1 ({len(G1.nodes())}) does not match number of nodes in G2 ({len(G2.nodes())})")
            break

        if set(list(G1.nodes())) != set(list(G2.nodes())):
            differences_list.append(f"Nodes in G1 ({set(list(G1.nodes()))}) does not match nodes in G2 ({set(list(G2.nodes()))})")
            break

        if print_flag: 
            print(f"Total time for intial checks: {time.time() - local_compare_time}")
        local_compare_time = time.time()

        #1) compare the sorted edges array to see if equal
        unordered_bool = str(type(G1)) == str(type(nx.Graph())) or str(type(G1)) == str(type(GraphOrderedEdges()))

        if print_flag:
            print(f"unordered_bool = {unordered_bool}")

        #already checked for matching edge length so now guard against the possibility that no edges:
        if len(list(G1.edges())) > 0:


            G1_sorted_edges = nu.sort_multidim_array_by_rows(list(G1.edges()),order_row_items=unordered_bool)
            G2_sorted_edges = nu.sort_multidim_array_by_rows(list(G2.edges()),order_row_items=unordered_bool)


            if not np.array_equal(G1_sorted_edges,G2_sorted_edges):
                differences_list.append("The edges array are not equal ")
                break

            if print_flag: 
                print(f"Total time for Sorting and Comparing Edges: {time.time() - local_compare_time}")
            local_compare_time = time.time()

            #2) compare the edge weights are the same (maybe within a threshold) (BUT MUST SPECIFY THRESHOLD)
            if print_flag:
                print(f"compare_edge_attributes = {compare_edge_attributes}")
            if len(compare_edge_attributes)>0:

                G1_edge_attributes = get_all_attributes_for_edges(G1,edges_list=G1_sorted_edges,return_dict=True)
                G2_edge_attributes = get_all_attributes_for_edges(G2,edges_list=G2_sorted_edges,return_dict=True)

                """
                loop that will go through each edge and compare the dictionaries:
                - only compare the attributes selected (compare all if "all" in list)
                - if certain attributes show up in the edge_threshold_attributes then compare then against the edge_comparison_threshold
                """

                for z,curr_edge in enumerate(G1_edge_attributes.keys()):
                    G1_edge_dict = G1_edge_attributes[curr_edge]
                    G2_edge_dict = G2_edge_attributes[curr_edge]
                    #print(f"G1_edge_dict.keys() = {G1_edge_dict.keys()}")

                    if "all" not in compare_edge_attributes:
                        G1_edge_dict = dict([(k,v) for k,v in G1_edge_dict.items() if k in compare_edge_attributes])
                        G2_edge_dict = dict([(k,v) for k,v in G2_edge_dict.items() if k in compare_edge_attributes])

                    #do the exclusion of some attributes:
                    G1_edge_dict = dict([(k,v) for k,v in G1_edge_dict.items() if k not in compare_edge_attributes_exclude])
                    G2_edge_dict = dict([(k,v) for k,v in G2_edge_dict.items() if k not in compare_edge_attributes_exclude])

                    if z ==1:
                        if print_flag:
                            print(f"Example G1_edge_dict = {G1_edge_dict}")


                    #check that they have the same number of keys
                    if set(list(G1_edge_dict.keys())) != set(list(G2_edge_dict.keys())):
                        differences_list.append(f"The dictionaries for the edge {curr_edge} did not have same keys in G1 ({G1_edge_dict.keys()}) as G2 ({G2_edge_dict.keys()})")
                        continue
                        #return False
                    #print(f"G1_edge_dict.keys() = {G1_edge_dict.keys()}")
                    #check that all of the values for each key match
                    for curr_key in G1_edge_dict.keys():
                        #print(f"{(G1_edge_dict[curr_key],G2_edge_dict[curr_key])}")
                        if curr_key in edge_threshold_attributes:
                            value_difference = np.linalg.norm(G1_edge_dict[curr_key]-G2_edge_dict[curr_key])
                            if value_difference > edge_comparison_threshold:
                                differences_list.append(f"The edge {curr_edge} has a different value for {curr_key} in G1 ({G1_edge_dict[curr_key]}) and in G2 ({G2_edge_dict[curr_key]}) "
                                     f"that was above the current edge_comparison_threshold ({edge_comparison_threshold}) ")
                                #return False
                        else:
                            if nu.is_array_like(G1_edge_dict[curr_key]):
                                if not np.array_equal(G1_edge_dict[curr_key],G2_edge_dict[curr_key]):
                                    differences_list.append(f"The edge {curr_edge} has a different value for {curr_key} in G1 ({G1_edge_dict[curr_key]}) and in G2 ({G2_edge_dict[curr_key]}) ")
                            else:
                                if G1_edge_dict[curr_key] != G2_edge_dict[curr_key]:
                                    differences_list.append(f"The edge {curr_edge} has a different value for {curr_key} in G1 ({G1_edge_dict[curr_key]}) and in G2 ({G2_edge_dict[curr_key]}) ")
                                    #return False

        #if no discrepancy has been detected then return True
        if len(differences_list) == 0:
            if print_flag:
                print("Made it through edge comparison without there being any discrepancies")

        if print_flag: 
            print(f"Total time for Checking Edges Attributes : {time.time() - local_compare_time}")
        local_compare_time = time.time()

        """
        3) For each node name: 
        - check that the attributes are the same
        - can specify attribute names that can be within a certian threshold (BUT MUST SPECIFY THRESHOLD)
        """

        if len(compare_node_attributes)>0:

            G1_node_attributes = get_all_attributes_for_nodes(G1,return_dict=True)
            G2_node_attributes = get_all_attributes_for_nodes(G2,return_dict=True)

            """
            loop that will go through each node and compare the dictionaries:
            - only compare the attributes selected (compare all if "all" in list)
            - if certain attributes show up in the node_threshold_attributes then compare then against the node_comparison_threshold
            """
            if print_flag:
                print(f"compare_node_attributes = {compare_node_attributes}")
            for z,n in enumerate(G1_node_attributes.keys()):
                G1_node_dict = G1_node_attributes[n]
                G2_node_dict = G2_node_attributes[n]

                if "all" not in compare_node_attributes:
                    G1_node_dict = dict([(k,v) for k,v in G1_node_dict.items() if k in compare_node_attributes])
                    G2_node_dict = dict([(k,v) for k,v in G2_node_dict.items() if k in compare_node_attributes])


                #doing the exlusion
                G1_node_dict = dict([(k,v) for k,v in G1_node_dict.items() if k not in compare_node_attributes_exclude])
                G2_node_dict = dict([(k,v) for k,v in G2_node_dict.items() if k not in compare_node_attributes_exclude])

                if z ==1:
                    if print_flag:
                        print(f"Example G1_edge_dict = {G1_node_dict}")


                #check that they have the same number of keys
                if set(list(G1_node_dict.keys())) != set(list(G2_node_dict.keys())):
                    differences_list.append(f"The dictionaries for the node {n} did not have same keys in G1 ({G1_node_dict.keys()}) as G2 ({G2_node_dict.keys()})")
                    continue
                    #return False

                #check that all of the values for each key match
                for curr_key in G1_node_dict.keys():
                    #print(f"curr_key = {curr_key}")

                    if curr_key in node_threshold_attributes:
                        value_difference = np.linalg.norm(G1_node_dict[curr_key]-G2_node_dict[curr_key])
                        if value_difference > node_comparison_threshold:
                            differences_list.append(f"The node {n} has a different value for {curr_key} in G1 ({G1_node_dict[curr_key]}) and in G2 ({G2_node_dict[curr_key]}) "
                                 f"that was above the current node_comparison_threshold ({node_comparison_threshold}) ")
                            #return False
                    else:

                        if nu.is_array_like(G1_node_dict[curr_key]):
                            #print((set(list(G1_node_dict.keys())),set(list(G2_node_dict.keys()))))
                            if not np.array_equal(G1_node_dict[curr_key],G2_node_dict[curr_key]):
                                differences_list.append(f"The node {n} has a different value for {curr_key} in G1 ({G1_node_dict[curr_key]}) and in G2 ({G2_node_dict[curr_key]}) ")
                                #return False
                        else:
                            #print(f"curr_key = {curr_key}")
                            #print(f"G1_node_dict[curr_key] != G2_node_dict[curr_key] = {G1_node_dict[curr_key] != G2_node_dict[curr_key]}")
                            #print(f"G1_node_dict[curr_key] = {G1_node_dict[curr_key]}, G2_node_dict[curr_key] = {G2_node_dict[curr_key]}")
                            if G1_node_dict[curr_key] != G2_node_dict[curr_key]:
                                differences_list.append(f"The node {n} has a different value for {curr_key} in G1 ({G1_node_dict[curr_key]}) and in G2 ({G2_node_dict[curr_key]}) ")
                                #return False
                        #print(f"differences_list = {differences_list}")

        if print_flag: 
            print(f"Total time for Comparing Node Attributes: {time.time() - local_compare_time}")
        local_compare_time = time.time()
    
    #if no discrepancy has been detected then return True
    
    if len(differences_list) == 0:
        if print_flag:
            print("Made it through Node comparison without there being any discrepancies")
        return_boolean = True
    else:
        if print_flag:
            print("Differences List:")
            for j,diff in enumerate(differences_list):
                print(f"{j})   {diff}")
        return_boolean = False
    
    if return_differences is None:
        raise Exception("return_differences is None!!!")
        
    if return_differences:
        return return_boolean,differences_list
    else:
        return return_boolean
    
# -------------- 8/4 additions ----------------------- #
"""
How to determine upstream and downstream targets

Example: 
#import networkx as nx
#import matplotlib.pyplot as plt
G = nx.DiGraph()
G.add_edges_from(
    [('A', 'B'), ('A', 'C'), ('D', 'B'), ('E', 'C'), ('E', 'F'),('F','Z'),
     ('B', 'H'), ('B', 'G'), ('B', 'F'), ('C', 'G'), ('Q', 'D')])

pos = nx.spring_layout(G)
nx.draw_networkx_nodes(G, pos, cmap=plt.get_cmap('jet'),node_size = 50)
nx.draw_networkx_edges(G, pos, edge_color='r', arrows=True)
nx.draw_networkx_labels(G, pos)
plt.show()

print("Downstream Edges of 'B' (just example)-->")
print(list(nx.dfs_edges(G,'B')))
print(downstream_edges(G,"B"))
print(downstream_edges_neighbors(G,"B"))


print("\nUpstream Edges of 'B' (just example)-->")
print(list(nx.edge_dfs(G,'B', orientation='reverse')))
print(upstream_edges(G,"B"))
print(upstream_edges_neighbors(G,"B"))

"""
def downstream_edges(G,node):
    return list(nx.dfs_edges(G,node))
def downstream_edges_neighbors_not_exact(G,node):
    return [k for k in list(nx.dfs_edges(G,node)) if node in k]

def upstream_edges(G,node):
    return [k[:2] for k in list(nx.edge_dfs(G,node, orientation='reverse'))]
def upstream_edges_neighbors_slow(G,node):
    return [k for k in list(nx.edge_dfs(G,node, orientation='reverse')) if node in k]

def upstream_edges_neighbors(G,node):
    return list(G.predecessors(node))
    
def downstream_edges_neighbors(G,node):
    neighb = list(dict(G[node]).keys())
    return list(np.vstack([[node]*len(neighb),neighb]).T)

def downstream_nodes(G,node):
    downstream_results = np.array(downstream_edges_neighbors(G,node))
    if len(downstream_results) > 0:
        return downstream_results[:,1]
    else:
        return downstream_results
    

    
def n_downstream_nodes(G,node):
    """
    Ex: xu.n_downstream_nodes(neuron_obj[0].concept_network_directional,18)
    """
    return len(downstream_nodes(G,node))

def all_downstream_nodes(
    G,
    node,
    include_self = False,
    return_empty_list_if_none=True):
    curr_nodes = np.unique(np.array(xu.downstream_edges(G,node)).ravel())
    if not include_self:
        return_list = list(curr_nodes[curr_nodes!=node])
        if return_empty_list_if_none and len(return_list) > 0:
            if nu.is_array_like(return_list[0]):
                return_list = []
        return return_list
    else:
        return_nodes = list(curr_nodes)
        if len(return_nodes) == 0:
            return [node]
        else:
            return return_nodes
        
def n_all_downstream_nodes(G,node):
    return len(all_downstream_nodes(G,node))
def all_downstream_nodes_including_node(G,node):
    return [node] + all_downstream_nodes(G,node)
    
def all_downstream_nodes_from_nodes(G,nodes):
    """
    Purpose: Find all downstream nodes
    in group of nodes 

    Pseudocode: 
    For each node:
    1) Get all of the downstream nodes
    2) add to the final list
    
    Ex: 
    xu.all_downstream_nodes_from_nodes(limb_obj.concept_network_directional,[9,18])

    """
    d_nodes = np.unique(np.concatenate([xu.all_downstream_nodes_including_node(G,k) for k in nodes]))
    return d_nodes


# ---- upstream version of all nodes ----------
def all_upstream_nodes(G,node,include_self=False):
    curr_nodes = np.unique(np.array(xu.upstream_edges(G,node)).ravel())
    if not include_self:
        curr_nodes = curr_nodes[curr_nodes!=node]
    return list(curr_nodes)

def n_all_upstream_nodes(G,node):
    return len(all_upstream_nodes(G,node))
def all_upstream_nodes_including_node(G,node):
    return [node] + all_upstream_nodes(G,node)
    
def all_upstream_nodes_from_nodes(G,nodes):
    """
    Purpose: Find all downstream nodes
    in group of nodes 

    Pseudocode: 
    For each node:
    1) Get all of the downstream nodes
    2) add to the final list
    
    Ex: 
    xu.all_downstream_nodes_from_nodes(limb_obj.concept_network_directional,[9,18])

    """
    d_nodes = np.unique(np.concatenate([xu.all_upstream_nodes_including_node(G,k) for k in nodes]))
    return d_nodes

    
def parent_node(G,node):
    return upstream_node(G,node)

def sibling_nodes(G,node):
    parent_node = upstream_node(G,node)
    if parent_node is None:
        return []

    #find the sibling nodes
    all_sibling_nodes = downstream_nodes(G,parent_node)
    return all_sibling_nodes[all_sibling_nodes != node]

def n_sibling_nodes(G,node):
    return len(sibling_nodes(G,node))
    
def upstream_node(G,node,return_single=True):
    curr_upstream_nodes = upstream_edges_neighbors(G,node)
        
    if len(curr_upstream_nodes) == 0:
        return None
    elif len(curr_upstream_nodes) > 1:
        if return_single:
            raise Exception(f"More than one upstream node for node {node}: {curr_upstream_nodes}")
        else:
            return [k[0] for k in curr_upstream_nodes]
    else:
        if not nu.is_array_like(curr_upstream_nodes[0]):
            return curr_upstream_nodes[0]
        try:
            return curr_upstream_nodes[0][0]
        except:
            return curr_upstream_nodes[0]
    
def all_parent_nodes(G,n,depth_limit = 1):
    """
    Purpose: To find the all parent nodes
    of a certain node (can be multiple)
    """
    reverse_tree = nx.traversal.bfs_tree(
        G,
        n,
        reverse = True,
        depth_limit = depth_limit,
    ).nodes()

    return [k for k in reverse_tree if k != n]

def all_children_nodes(G,n,depth_limit = 1):
    """
    Purpose: To find the all parent nodes
    of a certain node (can be multiple)
    """
    reverse_tree = nx.traversal.bfs_tree(
        G,
        n,
        reverse = False,
        depth_limit = depth_limit,
    ).nodes()

    return [k for k in reverse_tree if k != n]

def common_relational_nodes(
    G,
    nodes,
    relation = "parent",
    combining_method = "intersect",
    depth_limit = 1,
    verbose = False,
    ):
    """
    Purpose: To find common parent nodes

    Pseudocode: 
    For all nodes:
    1) Find the parent nodes

    Get the intersection
    """
    nodes= nu.array_like(nodes)

    common_nodes_list = [getattr(xu,f"all_{relation}_nodes")(G,n,depth_limit=depth_limit)
                   for n in nodes]

    if type(combining_method) == str:
         func = getattr(nu,f"{combining_method}1d_multi_list")
    else:
        func = combining_method

    common_nodes = func(common_nodes_list)

    if verbose:
        print(f"n_common_nodes of {relation} = {len(common_nodes)} (after {combining_method})")

    return common_nodes

def common_parent_nodes(
    G,
    nodes,
    combining_method = "intersect",
    depth_limit = 1,
    verbose = False,
    ):
    """
    Ex: 
    xu.common_parent_nodes(
        G,
        nodes = ["864691134884741626_0","864691136226945617_0"],
    )
    """
    
    return common_relational_nodes(
    G,
    nodes=nodes,
    relation = "parent",
    combining_method = combining_method,
    depth_limit = depth_limit,
    verbose = verbose,
    )

def n_common_parent_nodes(
    G,
    nodes,
    combining_method = "intersect",
    depth_limit = 1,
    verbose = False,
    ):
    
    return len(
        common_parent_nodes(
            G,
            nodes,
            combining_method = combining_method,
            depth_limit = depth_limit,
            verbose = verbose,
        )
    )

def common_children_nodes(
    G,
    nodes,
    combining_method = "intersect",
    depth_limit = 1,
    verbose = False,
    ):
    
    return common_relational_nodes(
    G,
    nodes=nodes,
    relation = "children",
    combining_method = combining_method,
    depth_limit = depth_limit,
    verbose = verbose,
    )
       
    
# --------------------- 8/31 -------------------------- #
#import random


def hierarchy_pos(G, root=None, width=1., vert_gap = 0.2, vert_loc = 0, xcenter = 0.5,width_min = 0.3,width_noise_ampl=0.2):
    '''
    
    Old presets: 
    width=1., vert_gap = 0.2, vert_loc = 0, xcenter = 0.5
    
    
    From Joel's answer at https://stackoverflow.com/a/29597209/2966723.  
    Licensed under Creative Commons Attribution-Share Alike 

    If the graph is a tree this will return the positions to plot this in a 
    hierarchical layout.

    G: the graph (must be a tree)

    root: the root node of current branch 
    - if the tree is directed and this is not given, 
      the root will be found and used
    - if the tree is directed and this is given, then 
      the positions will be just for the descendants of this node.
    - if the tree is undirected and not given, 
      then a random choice will be used.

    width: horizontal space allocated for this branch - avoids overlap with other branches

    vert_gap: gap between levels of hierarchy

    vert_loc: vertical location of root

    xcenter: horizontal location of root
    '''
    if not nx.is_tree(G):
        raise TypeError('cannot use hierarchy_pos on a graph that is not a tree')

    if root is None:
        if isinstance(G, nx.DiGraph):
            root = next(iter(nx.topological_sort(G)))  #allows back compatibility with nx version 1.11
        else:
            root = random.choice(list(G.nodes))

    def _hierarchy_pos(G, root, width=1., vert_gap = 0.2, vert_loc = 0, xcenter = 0.5, pos = None, parent = None):
        '''
        see hierarchy_pos docstring for most arguments

        pos: a dict saying where all nodes go if they have been assigned
        parent: parent of this branch. - only affects it if non-directed

        '''
        
        if np.abs(width) < width_min:
            width = np.sign(width)*(width_min + width_noise_ampl*np.random.rand(1)[0])
            #width = width_min 
            #print(f"width_noise_ampl = {width_noise_ampl}")
        
        #print(f"root {root}: inside _hierarchy_pos: width = {width}, xcenter={xcenter}")

        if pos is None:
            pos = {root:(xcenter,vert_loc)} #if no previous position then start dictioanry
        else:
            pos[root] = (xcenter, vert_loc) #if dictionary already exists then add position to dictionary
        children = list(G.neighbors(root)) #get all children of current root
        if not isinstance(G, nx.DiGraph) and parent is not None:
            children.remove(parent) #remove parent from possible neighbors (so only get ones haven't used) 
        if len(children)!=0: #if have children to graph
            dx = width/len(children)  #take whole width and allocates for how much each child gets
            nextx = xcenter - width/2 - dx/2
            for child in children:
                nextx += dx
                """
                How recursive call works: 
                1) the dx allocated for each child becomes the next width
                2) same vertical gap
                3) New vertical location is original but stepped down vertical gap
                3) New x location is the nextx
                
                """
                pos = _hierarchy_pos(G,child, width = dx, vert_gap = vert_gap, 
                                    vert_loc = vert_loc-vert_gap, xcenter=nextx,
                                    pos=pos, parent = root)
        return pos


    return _hierarchy_pos(G, root, width, vert_gap, vert_loc, xcenter)
    
    
# --------- 9/17 Addition ----------------------- #
#from copy import deepcopy
def shortest_path_between_two_sets_of_nodes(
    G,
    node_list_1,
    node_list_2,
    return_node_pairs=True,
    return_path_distance = False,
    weight = "weight",
    verbose = False,):
    """
    Algorithm that will find the shortest path from a set of one
    list of nodes on a graph and another set of nodes:
    
    Returns: The shortest path, the nodes from each set that were paired
    
    Things to think about:
    - could possibly have non-overlapping groups
    
    Pseudocode:
    0) Make a copy of the graph
    1) Add a new node to graph that is connected to all nodes in node_list_1 (s)
    2) Add a new node to graph that is connected to all nodes in node_list_2 (t)
    3) Find shortest path from s to t
    4) remove s and t from path and return the two endpoints of path as node pair
    
    Example: 
    import networkx as nx
    G = nx.path_graph(10)
    node_list_1 = [1,2]
    node_list_2 = [9,5]
    
    shortest_path_between_two_sets_of_nodes(G,node_list_1,node_list_2,
                                           return_node_pairs=True)
    
    will return [ 2, 3, 4, 5],2,5
    """
    st = time.time()
    #0) Make a copy of the graph
    G_copy = deepcopy(G)
    #node_number_max = np.max(G.nodes())

    #1) Add a new node to graph that is connected to all nodes in node_list_1 (s)
    s = "node_source_1" #node_number_max + 1
    G_copy.add_weighted_edges_from([(s,k,0.0001) for k in node_list_1])

    #2) Add a new node to graph that is connected to all nodes in node_list_2 (t)
    t = "node_target_2" #node_number_max + 2
    G_copy.add_weighted_edges_from([(k,t,0.0001) for k in node_list_2])

    #3) Find shortest path from s to t
    shortest_path = nx.shortest_path(G_copy,s,t,weight=weight)
    

    #node_pair
    curr_shortest_path = shortest_path[1:-1]
    end_node_1 = shortest_path[1]
    end_node_2 = shortest_path[-2]
    
    #make sure it is the shortest path between end nodes
    curr_shortest_path = nx.shortest_path(G,end_node_1,end_node_2)
    
    if return_path_distance:
        curr_shortest_path = xu.path_distance(G,curr_shortest_path,weight=weight)
        
    if verbose:
        print(f"Shortest path = {curr_shortest_path}")
        print(f"Total time: {time.time() - st}")
    
    if return_node_pairs:
        return curr_shortest_path,end_node_1,end_node_2
    else:
        return curr_shortest_path
    
    
def find_nodes_within_certain_distance_of_target_node(G,
                                                      target_node,
                                                        cutoff_distance = 10000,
                                                        return_dict=False):
    """
    Purpose: To Find the node values that are within a certain 
    distance of a target node 
    
    """
    distance_dict = nx.single_source_dijkstra_path_length(G,target_node,
                                                          cutoff=cutoff_distance
                                                         )
    if return_dict:
        return distance_dict
    
    close_nodes = set(np.array(list(distance_dict)).astype("int"))
    return close_nodes
    
    
def add_new_coordinate_node(G,
    node_coordinate,
    replace_nodes=None,
    replace_coordinates=None,
    neighbors=None,
    node_id=None,
                           return_node_id=True):
    """
    To add a node to a graph
    with just a coordinate and potentially replacing 
    another node
    """
    
    #G = copy.deepcopy(G)
    
    if not replace_coordinates is None:
        if len(replace_coordinates.shape) < 2:
            replace_coordinates=replace_coordinates.reshape(-1,3)
            
        replace_nodes = [get_graph_node_by_coordinate(G,k) for k in replace_coordinates]

#     print(f"replace_coordinates = {replace_coordinates}")
#     print(f"replace_nodes = {replace_nodes}")
#     print(f"len(G) = {len(G)}")

    if not replace_nodes is None:
        if not nu.is_array_like(replace_nodes):
            replace_nodes = [replace_nodes]
        neighbors = np.unique(np.concatenate([get_neighbors(G,k) for k in replace_nodes]))
    
    if node_id is None:
        node_id = np.max(G.nodes()) + 1
        
    G.add_node(node_id,coordinates=node_coordinate)

    G.add_weighted_edges_from([(node_id,k,
             np.linalg.norm(G.nodes[k]["coordinates"] - node_coordinate)) for k in neighbors])
    
    if not replace_nodes is None:
        G.remove_nodes_from(replace_nodes)
        
    if return_node_id:
        return G,node_id
    else:
        return G
    

def move_node_from_exclusion_list(G,
                                  exclusion_list,
                                 node=None,
                                 node_coordinate=None,
                                 return_coordinate=True,
                                 verbose=False):

    """
    Purpose: To move a point off of an exclusion list to another node

    Psuedocode: 
    1) Check if current node is in exclusion, if not then return
    2) Check if any of the neighbors are in exclusion, if not then return that
    3) If still havent found, then find the shortest path from stitch node to all non-exclude nodes

    Ex:
    
    move_node_from_exclusion_list(
    G = sk.convert_skeleton_to_graph(ex_skeleton),
    exclusion_list = np.array([[756852., 948046., 874045.],
             [756851., 948250., 874012.]]),
    node = None,
    node_coordinate = np.array([756851., 948250., 874012.]),
    return_coordinate = False,
    verbose = True)

    """
    exclusion_list = np.array(exclusion_list)
    if exclusion_list.ndim > 1:
        exclusion_nodes = np.array([xu.get_graph_node_by_coordinate(G,k,return_neg_one_if_not_find=True) for k in exclusion_list])
    else:
        exclusion_nodes = exclusion_list

    if node_coordinate is None and node is None:   
        raise Exception("both node and node coordinate are none")
    elif node_coordinate is None:
        node_coordinate = xu.get_coordinate_by_graph_node(G,node)
    elif node is None:
        node = xu.get_graph_node_by_coordinate(G,node_coordinate)
    else:
        pass

    #1) Check if current node is in exclusion, if not then return
    if node not in exclusion_nodes:
        if verbose:
            print(f"Original node {node} was not in exlusion list so just returning that")
        if return_coordinate:
            return node_coordinate
        else:
            return node



    #2) Check if any of the neighbors are in exclusion, if not then return that
    node_neighbors = xu.get_neighbors(G,node)
    viable_neighbors = np.setdiff1d(node_neighbors,exclusion_nodes)

    if len(viable_neighbors) > 0:
        if verbose:
            print(f"Found coordinate to move to in viable neighbors: {viable_neighbors[0]}")
        if return_coordinate:
            return xu.get_coordinate_by_graph_node(ex_skeleton_graph,viable_neighbors[0])
        else:
            return viable_neighbors[0]

    #3) If still havent found, then find the shortest path from stitch node to all non-exclude nodes
    all_nodes = np.array(list(G.nodes()))
    viable_nodes = np.setdiff1d(all_nodes,exclusion_nodes)

    path,st_node,winning_node = xu.shortest_path_between_two_sets_of_nodes(G,node_list_1=[node],
                                               node_list_2=viable_nodes)

    if verbose:
        print(f"Used the shortest path algorithm to find the winning node: {winning_node}")

    if return_coordinate:
        return xu.get_coordinate_by_graph_node(G,winning_node)
    else:
        return int(winning_node)
    
def connected_components_from_nodes_edges(nodes,edges):
    """
    Purpose: To return groups that should be connected
    as defined by the total nodes and edges between nodes
    
    connected_components_from_nodes_edges([1,2,3,4,5,6],
                                     [[1,3],
                                     [3,5],
                                     [5,6]])
    """
    G = nx.Graph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    return [list(k) for k in list(nx.connected_components(G))]

def nodes_in_kept_group(G,
                       nodes_to_keep,
                        return_removed_nodes=True,
                        verbose=False,
                       ):
    """
    Return the nodes that are in the same connected component
    as at least one of the nodes in the keep group
    
    """
    
    if not nu.is_array_like(nodes_to_keep):
        keep_nodes = [nodes_to_keep]
        
        
    #2) Split the graph into connected components
    conn_comp = list(nx.connected_components(G))

    if verbose:
        print(f"conn_comp = {conn_comp}")

    #3) Find all kept nodes as the connected component with 
    #the starting node (if there is one)
    nodes_kept = []
    nodes_removed = []

    for c in conn_comp:
        intersecting_nodes = np.intersect1d(nodes_to_keep,list(c))
        if verbose:
            print(f"intersecting_nodes = {intersecting_nodes} of {keep_nodes} and {c}")
        if len(intersecting_nodes)>0:
            nodes_kept += list(c)
        else:
            nodes_removed += list(c)

    if return_removed_nodes:
        return nodes_kept,nodes_removed
    else:
        return nodes_kept

    

def nodes_in_kept_groups_after_deletion(G,
                                       nodes_to_keep,
                                        nodes_to_remove,
                                        return_removed_nodes = False,
                                        verbose = False,
                                       ):
    """
    Purpose: To delete nodes from a graph and then only return the 
    nodes that are still connected to a certain group of nodes

    Pseudocode: 

    1) Delete all the nodes from the graph
    2) Split the graph into connected components
    3) Find all kept nodes as the connected component with 
    the starting node (if there is one)
    4) Return either the kept nodes (and optionally the deleted ones)
    
    Application:
    If have starting node in limb concept network, and want to delete
    certain nodes, will tell you what nodes will still be connected
    to starting node after deletion
    
    Ex:
    G = nx.Graph(curr_limb.concept_network_directional)
    nodes_to_keep = 0
    nodes_to_remove = [6,13]

    xu.nodes_in_kept_groups_after_deletion(G,
                                        nodes_to_keep,
                                           nodes_to_remove=nodes_to_remove,
                                        return_removed_nodes = True
                                           )  
    

    """

    G = nx.Graph(G)

    #1) Delete all the nodes from the graph
    G.remove_nodes_from(nodes_to_remove)
    
    nodes_removed_manually = list(nodes_to_remove)
    
    nodes_kept,nodes_removed = nodes_in_kept_group(G,
                       nodes_to_keep,
                        return_removed_nodes=True,
                        verbose=verbose
                       )
    nodes_removed += nodes_removed_manually
    
    if return_removed_nodes:
        return nodes_kept,nodes_removed
    else:
        return nodes_kept
        

'''  Old method before extracting out function
def nodes_in_kept_groups_after_deletion(G,
                                       nodes_to_keep,
                                        nodes_to_remove,
                                        return_removed_nodes = False,
                                        verbose = False,
                                       ):
    """
    Purpose: To delete nodes from a graph and then only return the 
    nodes that are still connected to a certain group of nodes

    Pseudocode: 

    1) Delete all the nodes from the graph
    2) Split the graph into connected components
    3) Find all kept nodes as the connected component with 
    the starting node (if there is one)
    4) Return either the kept nodes (and optionally the deleted ones)
    
    Application:
    If have starting node in limb concept network, and want to delete
    certain nodes, will tell you what nodes will still be connected
    to starting node after deletion
    
    Ex:
    G = nx.Graph(curr_limb.concept_network_directional)
    nodes_to_keep = 0
    nodes_to_remove = [6,13]

    xu.nodes_in_kept_groups_after_deletion(G,
                                        nodes_to_keep,
                                           nodes_to_remove=nodes_to_remove,
                                        return_removed_nodes = True
                                           )  
    

    """

    G = nx.Graph(G)

    if not nu.is_array_like(nodes_to_keep):
        keep_nodes = [nodes_to_keep]

    #1) Delete all the nodes from the graph
    G.remove_nodes_from(nodes_to_remove)

    #2) Split the graph into connected components
    conn_comp = list(nx.connected_components(G))

    if verbose:
        print(f"conn_comp = {conn_comp}")

    #3) Find all kept nodes as the connected component with 
    #the starting node (if there is one)
    nodes_kept = []
    nodes_removed = list(nodes_to_remove)

    for c in conn_comp:
        intersecting_nodes = np.intersect1d(nodes_to_keep,list(c))
        if verbose:
            print(f"intersecting_nodes = {intersecting_nodes} of {keep_nodes} and {c}")
        if len(intersecting_nodes)>0:
            nodes_kept += list(c)
        else:
            nodes_removed += list(c)

    if return_removed_nodes:
        return nodes_kept,nodes_removed
    else:
        return nodes_kept
    '''
    
    
def all_path_from_start_to_end_nodes(G,start_node):
    """
    Pseudocode: 
    1) Get all of the end nodes
    2) Subtract the starting node from the end nodes (if it is in there)

    If the list is longer than 0, iterate through all end nodes
    a. Get the shortest path from end node to the start node

    Return all of the paths

    """
    
    curr_endnodes = np.array(xu.get_nodes_of_degree_k(G,1))

    curr_endnodes_to_test = curr_endnodes[curr_endnodes != start_node]

    all_paths = [nx.shortest_path(G,start_node,e_node) for e_node in curr_endnodes_to_test]

    return all_paths

#import copy
def create_and_delete_edges(G,
                        edges_to_delete=None,
                        edges_to_create=None,
                        perform_edge_rejection=False,
                        return_accepted_edges_to_create=False,
                        return_copy=True,
                        verbose=False):
    """
    Purpose: To add and delete edges of a graph
    with possibly enforcing edge rejection
    where if the edge created does connect any of the
    nodes that should not be connected like specified in edges_to_delete
    then rejects the edge
    
    
    """
    if return_copy:
        G = copy.deepcopy(G)
    
    if not edges_to_delete is None:
        if verbose:
            print(f"edges_to_delete (cut_limb_network) = {edges_to_delete}")
        G.remove_edges_from(edges_to_delete)


    #apply the winning cut
    accepted_edges_to_create = []
    if not edges_to_create is None:
        if verbose:
            print(f"edges_to_create = {edges_to_create}")

        if perform_edge_rejection:
            for n1,n2 in edges_to_create:
                G.add_edge(n1,n2)
                counter = 0
                for d1,d2 in edges_to_delete:
                    try:
                        ex_path = np.array(nx.shortest_path(G,d1,d2))
                    except:
                        pass
                    else:
                        counter += 1
                        break
                if counter > 0:
                    G.remove_edge(n1,n2)
                    if verbose:
                        print(f"Rejected edge ({n1,n2})")
                else:
                    if verbose:
                        print(f"Accepted edge ({n1,n2})")
                    accepted_edges_to_create.append([n1,n2])
        else:
            accepted_edges_to_create = edges_to_create
            G.add_edges_from(accepted_edges_to_create)

    if return_accepted_edges_to_create:
        return G,accepted_edges_to_create

    return G

# ------ 2/26: Used for helping for the lowest angle sum crossovers
#from datasci_tools import numpy_utils as nu
def all_subgraph_edges(G):
    return nu.all_subarrays(list(G.edges()))

def all_subgraphs(G):
    """
    Purpose: Will generate all of the subgraphs 
    of a certain graph
    
    Ex:
    import matplotlib.pyplot as plt
    for k in all_subgraphs(G):
        nx.draw(k,with_labels=True)
        plt.show()
    
    """
    graph_list = []
    for k in xu.all_subgraph_edges(G):
        G_copy = nx.Graph(G)
        G_copy.remove_edges_from(k)
        graph_list.append(G_copy)
    return graph_list

def n_edges(G):
    return G.size()
def sum_of_edge_weights(G,weight="weight"):
    return G.size(weight)
def get_edges_with_weights(G):
    return np.array([list(k[:2]) + [k[2]["weight"]] if "weight" in k[2].keys() else list(k[:2]) + [np.nan] for k in G.edges(data=True)])

def degree_1_max_edge_min_max_weight_graph(G,
    weight_metric = "lowest", #or highest
    verbose = False,
    plot_winning_graph=False,
    return_edge_info = False,):
    """
    Purpose: To obtain the sugraph with the following properties
    1) Every node has at most one edge
    2) The highest number of edges with property 1
    3) The lowest/highest overall weight wiwth property 2

    Pseudocode: 
    1) Find all the subgraph possibilites
    2) Find highest degree nodes od each graph 
    and filter those away that are greater than 1
    3) Find the highest edge count and filter
    away those with less 
    4) Pick the graph with the lowest or highest total weight
    5) Have option to output Graph or the edges and the weights 
    
    Example:
    
    G = nx.Graph()
    G.add_weighted_edges_from([[1,4,20],
                              [1,3,10],
                              [2,3,40]])
    nx.draw(G,with_labels=True)

    return_info = xu.degree_1_max_edge_min_max_weight_graph(
        G = G,
        verbose = False,
        plot_winning_graph = True,
    return_edge_info=True)
    return_info
    
    """


    #1) Find all the subgraph possibilites
    all_subgraphs = xu.all_subgraphs(G)

    # 2) Find highest degree nodes od each graph 
    # and filter those away that are greater than 1
    subgraphs_degree_filtered = [k for k in all_subgraphs if xu.max_node_degree(k)<2]
    if verbose:
        print(f"subgraphs_degree_filtered= {subgraphs_degree_filtered}")
        print(f"# subgraphs Graphs after degree  = {len(subgraphs_degree_filtered)}")

    #3) Find the highest edge count and filter
    #away those with less 
    subgraphs_n_edges = np.array([xu.n_edges(k) for k in subgraphs_degree_filtered])
    subgraphs_n_edges_max = np.max(subgraphs_n_edges)

    if verbose:
        print(f"subgraphs_n_edges_max = {subgraphs_n_edges_max}")

    subgraphs_edges_filtered = [k for i,k in enumerate(subgraphs_degree_filtered)
                                if subgraphs_n_edges[i] == subgraphs_n_edges_max]

    if verbose:
        print(f"# subgraphs Graphs with max edges ({subgraphs_n_edges_max})  = {len(subgraphs_edges_filtered)}")

    #4) Pick the graph with the lowest or highest total weight
    sugraph_edge_weight_sum = [xu.sum_of_edge_weights(k) for k in subgraphs_edges_filtered]
    if weight_metric == "lowest":
        winning_G_idx = np.argmin(sugraph_edge_weight_sum)
    elif weight_metric == "highest":
        winning_G_idx = np.argmax(sugraph_edge_weight_sum)
    else:
        raise Exeption(f"Unknown weight metric: {weight_metric}")

    winning_graph = subgraphs_edges_filtered[winning_G_idx]

    if plot_winning_graph:
        print(f"N_edges for winning graph = {xu.n_edges(winning_graph)}")
        nx.draw(winning_graph,with_labels=True)

    if return_edge_info:
        edges_with_weights = xu.get_edges_with_weights(winning_graph)
        return_value = edges_with_weights[:,:2],edges_with_weights[:,2]
    else:
        return_value = winning_graph

    return return_value

def edges_and_weights_to_graph(edges,weights=None):
    if weights is None:
        weights = np.ones(len(edges))
    edges_with_weights = [list(k) + [v] for k,v in zip(edges,weights)]
    edges_with_weights
    G = nx.Graph()
    G.add_weighted_edges_from(edges_with_weights)
    return G

def lowest_weighted_sum_singular_matches(edges,edges_weights,
                                        plot_winning_graph=False,
                                        verbose=False):
    """
    will attempt to pair every node with another node
    so that the sum of the weights on the graph are as low as possible
    
    """
    curr_branches_G = xu.edges_and_weights_to_graph(edges,
                                                    edges_weights)
    match_branches,match_branches_angle = xu.degree_1_max_edge_min_max_weight_graph(
                G = curr_branches_G,
                verbose = verbose,
                plot_winning_graph = plot_winning_graph,
                return_edge_info=True)
    return match_branches,match_branches_angle

def get_edge_weight(G,e):
    return G.get_edge_data(e[0],e[1])["weight"]

def graph_to_edges_and_weights(G):
    """
    Turn a graph into a list of edges
    and a list of weights for the edges
    
    """
    edge_list = np.array(list(G.edges()))
    weight_list = np.array([xu.get_edge_weight(G,e) for e in edge_list])
    return edge_list,weight_list

def edges(G):
    return np.array(list(G.edges()))

def edges_and_weights_to_graph(
    edges_list,
    weights_list=None,
    graph_type = "Graph"):
    if weights_list is None:
        weights_list = np.ones(len(edges_list))
    G = getattr(nx,graph_type)()
    G.add_weighted_edges_from([list(k)+[v] for k,v in zip(edges_list,weights_list)])
    return G

def graph_to_lowest_weighted_sum_singular_matches(G = None,
    edges = None,
    edges_weights = None,
    verbose = False,
    return_graph = False):
    """
    Purpose: To take a Graph
    or list of edges and a list of their weights
    and to determine the singular pairings
    that result in the lowest total sum of weights

    Pseudocode: 
    1) Turn the matched branhes and the match_branches_angle
    into a weighted graph
    2) Get the lowest weight graph and output the edges
    3) Turn to lists and reassign as the matched branches


    """
    if edges is None or edges_weights is None:
        edges,edges_weights = xu.graph_to_edges_and_weights(G)

    match_branches,match_branches_angle  = xu.lowest_weighted_sum_singular_matches(
                                                                edges,
                                                                edges_weights)
    match_branches = list(match_branches)
    match_branches_angle = list(match_branches_angle)

    if verbose:
        print(f"From lowest_angle_sum_singular_pair: \nmatch_branches = {match_branches},match_branches_angle = {match_branches_angle} ")

    if return_graph:
        return xu.edges_and_weights_to_graph(match_branches,match_branches_angle)
    else:
        return match_branches,match_branches_angle
    
def get_neighbor_min_weighted_edge(G,node,verbose = False):
    """
    Purpose: to pick the 
    neighbor of a node with the lowest weight

    Psuedocode:
    1) get the neighbors
    --> if list empty then return none
    2) get the weights of the neighbor
    3) get the argmin of the weights
    4) return the min neighbor

    """
    neighbors = xu.get_neighbors(G,node)
    
    if len(neighbors) == 0:
        if verbose:
            print(f"No neighbors so returning None")
        return None
    
    neighbors = np.array(neighbors)
    n_weights = np.array([xu.get_edge_weight(G,(node,k)) for k in neighbors])
    
    if verbose:
        print(f"Neighbors = {neighbors}, neighbor weights = {n_weights}")
    
    min_neighbor = neighbors[np.argmin(n_weights)]
    
    if verbose:
        print(f"min_neighbor = {min_neighbor}")
        
    return min_neighbor


def group_nodes_into_siblings(G ,
    nodes,
    verbose = False):
    """
    Purpose: To group a list of branches
    into groups if they are sibling branches

    Pseudocode:
    1) For each branch get a list of the sibling branches
    and turn them into edges
    2) Create a graph from the edges
    3) Divide into connected components and return

    Ex:
    xu.group_nodes_into_siblings(G = neuron_obj[0].concept_network_directional,
    nodes = [14,  2,  4, 23, 25],
    verbose = True)
    """

    all_edges = []
    for b in nodes:
        curr_sibs = xu.sibling_nodes(G,b)
        all_edges += [(b,s) for s in curr_sibs]

    if verbose:
        print(f"All sibling edges = {all_edges}")

    #2) Create a graph from the edges
    G = nx.from_edgelist(all_edges)
    G = G.subgraph(nodes)

    return [list(k) for k in nx.connected_components(G)]

def all_edges_on_shortest_paths_between_nodes(G,nodes):
    """
    Purpose: Given a group of nodes, find 
    all edges that constitute the shortest paths
    between all pairs of nodes in the list
    
    """
    s_to_s_edges = []
    source_comb = nu.all_unique_choose_2_combinations(nodes)
    for s1,s2 in source_comb:
        
        curr_path = nx.shortest_path(G,s1,s2,
                                            weight="weight")
        path_edges = np.vstack([curr_path[:-1],curr_path[1:]]).T
        s_to_s_edges.append(path_edges)
        
#         if 15 in np.array(path_edges).ravel():
#             print(f"s1 = {s1}, s2 = {s2}")
#             print(f"path_edges = {path_edges}")
#             raise Exception("")

    s_to_s_edges = np.vstack(s_to_s_edges)
    return s_to_s_edges

def all_nodes_on_shortest_paths_between_nodes(G,nodes):
    if len(nodes) < 2:
        return nodes
    s_to_s_edges = np.unique(xu.all_edges_on_shortest_paths_between_nodes(G,nodes).ravel())
    return s_to_s_edges

#from datasci_tools import numpy_utils as nu
def min_cut_to_partition_node_groups(G,
                                     source_nodes,
                                    sink_nodes,
                                    verbose = False):
    """
    Find the edges of graph that would
    need to be cut to completely partition
    all nodes in sink_nodes from nodes
    in source_nodes into seperate connected components
    
    Psuedocode: 
    1) Get all of the shortest path edges between
    nodes in the same group (we will heavily weight them so they don't get cut)
    2) Add new nodes that will connect to every node in a specific partition
    (heavily weighted)
    3) Find the minimum cut between the two newly added nodes
    4) Return the edges of the original graph that went between
    the partition create for sink_nodes and source_nodes
    """
    
    
    large_weight = 10000

    #0) copying the new graph with weights
    G_orig = nx.Graph(G)
    G = nx.Graph()
    G.add_weighted_edges_from([list(k)+ [1] for k in G_orig.edges()])
    node_number_max = np.max(G.nodes())


    s_to_s_edges = xu.all_edges_on_shortest_paths_between_nodes(G,source_nodes)
    si_to_si_edges = xu.all_edges_on_shortest_paths_between_nodes(G,sink_nodes)

    new_source = node_number_max + 1
    s_new_edges = [[new_source,k] for k in source_nodes]

    new_sink = node_number_max + 2
    si_new_edges = [[new_sink,k] for k in sink_nodes]

    all_large_weight_edges = list(s_to_s_edges) + list(si_to_si_edges) + s_new_edges + si_new_edges
    G.add_weighted_edges_from([list(k)+ [large_weight] for k in all_large_weight_edges])
    
    #3) Find the minimum cut between the two newly added nodes
    cut_weight, partitions = nx.minimum_cut(G, new_source, new_sink, capacity='weight')
    
    if verbose:
        print(f"cut_weight = {cut_weight}")
    
    #4) Return the edges of the original graph that went between
    #the partition create for sink_nodes and source_nodes
    edge_cut_list = []
    for p1_node in partitions[0]:
        for p2_node in partitions[1]:
            if G.has_edge(p1_node,p2_node):
                edge_cut_list.append([p1_node,p2_node])
    edge_cut_list = np.array(edge_cut_list)
    
    nodes_in_edge_cut = edge_cut_list.ravel()
    
    if verbose:
        print(f"nodes_in_edge_cut = {nodes_in_edge_cut}")
        
    if cut_weight >= large_weight:
        return None
    else:
        return edge_cut_list
def remove_inter_partition_edges(G,
                                 partition,
                                 verbose = False):
    
    G1 = nx.Graph()
    G1.add_nodes_from(list(G.nodes()))
    for p1 in partition:
        
        subgraph = G.subgraph(p1)
        
        try:
            subgraph_edges = xu.get_edges_with_weights(subgraph)
            G1.add_weighted_edges_from(subgraph_edges)
        except:
            G1.add_edges_from(list(subgraph.edges()))
        
        if verbose:
            print(f"\n--- For partition {p1}")
            print(f"subgraph nodes = {subgraph.nodes()}")
            print(f"subgraph_edges = {subgraph_edges}")
    if verbose:
        try:
            print(f"Final Edges = {xu.get_edges_with_weights(G1)}")
        except:
            print(f"Final Edges = {G1.edges()}")
        print(f"Final Nodes = {G1.nodes()}")
    
    return G1

def end_nodes_of_digraph(G,verbose=False):
    """
    Purpose: To return the nodes that
    do not have any downstream nodes 
    (aka they are at the edge of the graph)
    """
    end_nodes = []
    for n in G.nodes():
        if len(xu.downstream_nodes(G,n)) == 0:
            end_nodes.append(n)
            
    if verbose:
        print(f"# of end nodes = {len(end_nodes)}")
    
    return np.array(end_nodes)

def get_nx_type(G):
    return G.__class__.__name__

def reverse_DiGraph_old(G):
    #return G.edges()
    new_G = getattr(nx,get_nx_type(G))()
    curr_edges = np.array(list(G.edges()))
    if len(curr_edges) == 0:
        return G
    new_G.add_edges_from(np.flip(curr_edges,axis=1))
    return new_G

def reverse_DiGraph(G):
    return G.reverse(copy=False)
    
    
def connected_components(G,return_subgraphs=False):
    conn_comp_list  = [list(k) for k in nx.connected_components(G.to_undirected())]
    
    if return_subgraphs:
        return [G.subgraph(k).copy() for k in conn_comp_list]
    else:
        return conn_comp_list
    
def connected_components_subgraphs(G):
    return xu.connected_components(G,return_subgraphs=True)


# --------------------- 6/14: For help with queying graphs with datatables --------- #
upstream_name = "u"
node_id_default = upstream_name
downstream_name = "v"
#from datasci_tools import general_utils as gu
def node_df(
    G,
    properties_to_exclude = None,
    properties_to_include=None,
    node_id = upstream_name,
    verbose = False,
    ):
    """
    To export the node properties  as a dataframe
    
    """
    st = time.time()
    node_dict = [gu.merge_dicts([G.nodes[k],{node_id:k}]) for k in G.nodes()]
    node_df = pu.dicts_to_dataframe(node_dict)
    col_names = np.array(node_df.columns)
    
    if properties_to_include is not None:
        if node_id not in properties_to_include:
            properties_to_include = np.concatenate([properties_to_include,[node_id]])
        col_names = np.intersect1d(col_names,properties_to_include)
        
    if properties_to_exclude is not None:
        col_names = np.setdiff1d(col_names,properties_to_exclude)
        
    if verbose:
        print(f"Time for node_df = {time.time() - st}")
        
    return node_df[[node_id]+list(col_names[col_names != node_id])]

def node_df_features(G):
    return list(xu.node_df(G).columns)[1:]

def subgraph_from_node_query(G,
                            query,
                            ):
    """
    Will return a subgraph induced
    by a query on the nodes
    
    """
    if len(G.nodes()) == 0:
        return G
    node_df = xu.node_df(G)
    #reduced_df = node_df.query(query)
    reduced_df = pu.query(node_df,query)
    remaining_nodes = reduced_df[upstream_name].to_list()
    return G.subgraph(remaining_nodes)

def node_df_from_node_query(
    G,
    query,
    return_nodes = False,
    ):
    if len(G.nodes()) == 0:
        return G
    node_df = xu.node_df(G)
    #reduced_df = node_df.query(query)
    reduced_df = pu.query(node_df,query)
    
    if return_nodes:
        return reduced_df[upstream_name].to_numpy()
    else:
        return reduced_df
    
def node_query_subgraph(
    G,
    query,
    verbose = False):
    if verbose:
        st = time.time()
    
    return_G =  G.subgraph(
        nodes_from_node_query(
            G,
            query)
        )
    
    if verbose:
        print(f"Time for node query subgraph = {time.time() - st}")
    
    return return_G
def nodes_from_node_query(
    G,
    query,
    **kwargs):
    return xu.node_df_from_node_query(
        G,
        query,
        return_nodes = True
        )
    
node_query = nodes_from_node_query

#from datasci_tools import general_utils as gu
#from datasci_tools.tqdm_utils import tqdm
#from datasci_tools import tqdm_utils as tqu
#import time
#import pandas as pd
#from . import numpy_dep as np


def edge_df_multi(G,
                 with_node_attributes = False,
                 verbose=False):
    """
    Purpose: Will output the multi-edged
    graph edge dataframe accounting for multiple possible edges
    
    Currently does that same thing as xu.edge_df_optimized(G_proof_multi_di)
    except that it can export node properties
    
    Ex: 
    from datasci_tools import networkx_utils as xu
    e_df = xu.edge_df_multi(G_proof_multi_di,
                            verbose = True,
                     )
    e_df
    """
    st = time.time()

    total_dicts = []
    total_edges = G.edges(keys=True)
    
    if not verbose:
        tqu.turn_off_tqdm()
        
    for u,d,key in tqdm(total_edges):
        
        if with_node_attributes:
            u_dict =  gu.add_prefix_to_keys(G.nodes[u],upstream_name)
            d_dict =  gu.add_prefix_to_keys(G.nodes[d],downstream_name)
            node_sp_dict = gu.merge_dicts([{upstream_name:u,
                                            downstream_name:d},u_dict,d_dict])
        else:
            node_sp_dict = {upstream_name:u,
                            downstream_name:d}
            
        total_dicts.append(gu.merge_dicts([node_sp_dict,G[u][d][key]]))
        
    if verbose:
        print(f"Creating Dict = {np.round(time.time() - st,4)}")
        st = time.time()

    G_df = pd.DataFrame.from_dict(total_dicts)
    
    if verbose:
        print(f"Creating Dataframe = {np.round(time.time() - st,4)}")
    return G_df
    

def edge_df(G,with_node_attributes = False,
            expand_to_all_multi_edges = True,
           verbose=False):
    """
    Purpose: To export the edges of a graph into
    a pandas dataframe so that later they can
    be queried easily

    """
    st = time.time()

    total_dicts = []
    total_edges = G.edges()
    
    if not verbose:
        tqu.turn_off_tqdm()
        
    if expand_to_all_multi_edges:
        multi_flag = xu.is_multigraph(G)
    else: 
        multi_flag = False
    for u,d in tqdm(total_edges):
        
        if with_node_attributes:
            u_dict =  gu.add_prefix_to_keys(G.nodes[u],upstream_name)
            d_dict =  gu.add_prefix_to_keys(G.nodes[d],downstream_name)
            node_sp_dict = gu.merge_dicts([{upstream_name:u,
                                            downstream_name:d},u_dict,d_dict])
        else:
            node_sp_dict = {upstream_name:u,
                            downstream_name:d}

        if multi_flag:
            total_dicts += [gu.merge_dicts([node_sp_dict,dict(v,edge_index=k)]) for k,v in G[u][d].items()]
        else:
            total_dicts.append(gu.merge_dicts([node_sp_dict,G[u][d]]))
        
    if verbose:
        print(f"Creating Dict = {np.round(time.time() - st,4)}")
        st = time.time()

    G_df = pd.DataFrame.from_dict(total_dicts)
    
    if verbose:
        print(f"Creating Dataframe = {np.round(time.time() - st,4)}")
    return G_df


#from datasci_tools import regex_utils as ru
def query_bidirectional(query,
    node_1 = upstream_name,
    node_2=downstream_name,
    logical_combination = "or"):
    
    """
    Purpose: To make a query apply to equal direction
    
    Example:
    query = "u in [1,2,3,4] and v in [0,2,3]"
    xu.query_bidirectional(query)
    
    """
    replace_map = {node_1:node_2,
                  node_2:node_1}
    return f"({query}) {logical_combination} ({ru.multiple_replace(query,replace_map)})"

def is_digraph(G):
    if "Di" in str(type(G)):
        return True
    else:
        return False
    
def is_multigraph(G):
    if "Multi" in str(type(G)):
        return True
    else:
        return False
    
def is_graph(G):
    if "networkx.classes.graph" in str(type(G)):
        return True
    else:
        return False
    
def is_graph_any(G):
    return xu.is_digraph(G) or xu.is_multigraph(G) or xu.is_graph(G)

#from datasci_tools import pandas_utils as pu
#from datasci_tools import tqdm_utils as tqu
#import copy


def subgraph_from_edges(
    G,
    edge_list,
    ref_back=False):
    """
    Creates a networkx graph that is a subgraph of G
    defined by the list of edges in edge_list.        

    Requires G to be a networkx Graph or DiGraph
    edge_list is a list of edges in either (u,v) or (u,v,d) form
    where u and v are nodes comprising an edge, 
    and d would be a dictionary of edge attributes

    ref_back determines whether the created subgraph refers to back
    to the original graph and therefore changes to the subgraph's 
    attributes also affect the original graph, or if it is to create a
    new copy of the original graph. 
    """

    sub_nodes = list({y for x in edge_list for y in x[0:2]})
    edge_list_no_data = [edge[0:2] for edge in edge_list]
    assert all([e in G.edges() for e in edge_list_no_data])

    G_sub = G.subgraph(sub_nodes)
    
    if not ref_back:
        G_sub = G_sub.copy()
        
    edges_to_remove = G.subgraph(sub_nodes).edges()
    for edge in edges_to_remove:
        if edge not in edge_list_no_data:
            G_sub.remove_edge(*edge)

    return G_sub

def query_to_subgraph(
    G,
    edge_query=None,
    make_bidirectional_query=False,
    node_query=None,
    return_df = False,
    delete_edges_only = True,
    return_edges = False,
    new_subgraph_from_edges_method = False,
    verbose = False,
    optimized_edge_df = False,
    delete_edges_in_query = False,
    inplace = False,
    edge_df = None):
    """
    Purpose: To restrict a graph by 
    a query that is meant to restrict the edges
    of a graph and return the resultant graph
    
    Pseudocode: 
    0) Make the query bidirectional if requested
    1) Build the edge df
    2) Query the dataframe
    3) if a node query is given then:
    - apply node query
    4) return the dataframe if requested
    5) Export the edges
    6) Make an edge induced subgraph
    
    # #Example 1: testing basic query
    G = query_to_subgraph(G1,"u < 2",
                      verbose = True,
                      return_df = False,
                          node_query="u < 2",)

    nx.draw(G,with_labels=True)

    #example 2: testing attributes query
    G = query_to_subgraph(G1,
                         "(weight<40) or (u>=5)",
                         make_bidirectional_query=True,
                         verbose = True)

    nx.draw(G,with_labels=True)
    """    
    if verbose == False:
        tqu.turn_off_tqdm()
    st = time.time()
    #1) Build the edge df
    if edge_df is None:
        if optimized_edge_df:
            edge_df  = xu.edge_df_optimized(
                G,
                source=upstream_name,
                target = downstream_name)
        else:
            edge_df = xu.edge_df(G)
            
    if verbose:
        print(f'Done with edge_df: {time.time() - st}')
    
    #2) Query the dataframe
    if edge_query is not None:
        if not delete_edges_in_query:
            edge_query = f"not ({edge_query})"
            
        if verbose:
            print(f"Performing Edge Query")
            
        #0) Make the query bidirectional if requested
        if make_bidirectional_query:
            edge_query = xu.query_bidirectional(edge_query)

            if verbose:
                print(f"After bidiretional the edge query = {edge_query}")
                
        #edge_df_filt = edge_df.query(edge_query)
        try:
            edge_df_filt = edge_df.query(edge_query)
        except:
            edge_df_filt = pu.query(edge_df,edge_query)
    else:
        edge_df_filt = edge_df
    
    if verbose:
        print(f"After edge filter, # of rows = {len(edge_df_filt)}")
    
    
    #3) if a node query is given then:
    """
    6/30 updates:
    1) get the node df from the graph
    2) Apply the query to the node df
    3) pull down all of the node ids
    4) restrict the edge graph to only those ids
    
    """
    if node_query is not None:
        
        node_df = xu.node_df(G)
        
        #nodes_remaining = node_df.query(node_query)[upstream_name].to_list()
        nodes_remaining = pu.query(node_df,node_query)[upstream_name].to_list()
        node_id_query = f"{upstream_name} in {nodes_remaining}"
        
        node_query_bi = xu.query_bidirectional(node_id_query,
                                              logical_combination = "and")
        
        #edge_df_filt = edge_df_filt.query(node_query_bi)
        edge_df_filt = pu.query(edge_df_filt,node_query_bi)
        
        if verbose:
            print(f"After bidiretional the node query = {node_query_bi}")
            print(f"After node filter, # of rows = {len(edge_df_filt)}")

        
    #4) return the dataframe if requested
    if return_df:
        return edge_df_filt
    
    #5) Export the edges
    if verbose:
        print(f"Exporting the edges")
    edges = pu.df_to_list(edge_df_filt[[xu.upstream_name,xu.downstream_name]],
                         return_tuples = True)
    
    if return_edges:
        return edges
    
    if delete_edges_only:
        if new_subgraph_from_edges_method:
            return xu.subgraph_from_edges(G,edges,ref_back=False)
        else:
            
            if verbose:
                print(f"Deleteing edges only")
            
            if not inplace:
                G = copy.deepcopy(G)
            G.remove_edges_from(edges)
#             total_edges = xu.edges(G)
#             removed_edges = nu.setdiff2d(total_edges,edges)
#             if verbose:
#                 print(f"    About to copy graph")
#             G = copy.deepcopy(G)
#             if verbose:
#                 print(f"    About to remove edges")
#             G.remove_edges_from(removed_edges)
            return G
    
    #6) Export the edge induced subgraph
    return G.edge_subgraph(edges)
    
def subgraph_from_edge_query(G,query,**kwargs):
    return xu.query_to_subgraph(G,
                      edge_query=query,
                      new_subgraph_from_edges_method = True,
                      **kwargs)

    
def complete_graph_from_node_ids(node_ids):
    """
    Purpose: Creates a fully connected network from a list of node ids
    
    Ex: 
    G = complete_graph_from_node_ids([10,12,13,20])
    G.edges()
    """
    return nx.complete_graph(node_ids)

def edge_attribute_dict_from_node(G,node):
    return dict(G[node])

def set_edge_attribute_defualt(G,attribute_name,
                              default_value = None,
                              ):
    if not xu.is_multigraph(G):
        for u in G:
            for v in G[u]:
                if attribute_name not in G[u][v]:
                    G[u][v][attribute_name] = default_value
    else:
        for u in G:
            for v in G[u]:
                for idx in dict(G[u][v]).keys():
                    if attribute_name not in G[u][v][idx]:
                        G[u][v][idx][attribute_name] = default_value
                        
def filter_down_edge_attributes(
    G,
    attributes=None,
    attributes_to_delete=None,
    nodelist = None,
    verbose = False):
    
    for u in G:
        if nodelist is not None:
            if u not in nodelist:
                continue
        for v in G[u]:
            if nodelist is not None:
                if v not in nodelist:
                    continue
                    
            if not xu.is_multigraph(G):
                if attributes_to_delete is not None:
                    for a in attributes_to_delete:
                        if a in G[u][v]:
                            del G[u][v][a]
                            
                if attributes is not None:
                    attr_to_remove = np.setdiff1d(
                        list(dict(G[u][v]).keys()),
                        attributes)
                    
                    for a in attr_to_remove:
                        if a in G[u][v]:
                            del G[u][v][a]
            else:
                for idx in dict(G[u][v]).keys():
                    if attributes_to_delete is not None:
                        for a in attributes_to_delete:
                            if a in G[u][v][idx]:
                                del G[u][v][idx][a]

                    if attributes is not None:
                        attr_to_remove = np.setdiff1d(
                            list(dict(G[u][v][idx]).keys()),
                            attributes)

                        for a in attr_to_remove:
                            if a in G[u][v][idx]:
                                del G[u][v][idx][a]
                
                
#             else:
#                 for idx in dict(G[u][v]).keys():
#                     if attribute_name not in G[u][v][idx]:
#                         G[u][v][idx][attribute_name] = default_value
    
                
    return G
                        
def derived_edge_attribute(
    G,
    attribute,
    new_attribute,
    edge_function,
    delete_original = False,
    ):
    if not xu.is_multigraph(G):
        for u in G:
            for v in G[u]:
                if attribute not in G[u][v]:
                    G[u][v][new_attribute] = edge_function(G[u][v][attribute])
                    if delete_original:
                        del G[u][v][attribute]
    else:
        for u in G:
            for v in G[u]:
                for idx in dict(G[u][v]).keys():
                    if attribute in G[u][v][idx]:
                        G[u][v][idx][new_attribute] = edge_function(G[u][v][idx][attribute])
                        if delete_original:
                            del G[u][v][idx][attribute]
                
def combine_edge_attributes(edge_attribute_dicts):
    """
    Purpose: To combine dictionaries that 
    store values in [edge1][edge2] = [value]
    """
    super_dict = edge_attribute_dicts[0]
    for d in edge_attribute_dicts[1:]:
        for k,v in d.items():
            if k not in super_dict.keys():
                super_dict[k] = dict()
            super_dict[k].update(v)
    return super_dict
                

def apply_edge_attribute_dict_to_graph(G,edge_attribute_dict,
                                      no_overwrite=True,
                                       label=None,
                                      verbose = False):
    """
    import networkx as nx
    G = nx.from_edgelist([[1,2],[3,4],[2,3],[2,5]])
    nx.draw(G,with_labels=True)
    my_dict = {1:{2:5},2:{3:7,5:10}}
    xu.apply_edge_attribute_dict_to_graph(G,my_dict,no_overwrite=False,
                                         label="weight")
    """
    for u,u_data in edge_attribute_dict.items():
        for v,v_data in u_data.items():
            if type(v_data) != dict:
                v_data = {label:v_data}
            if no_overwrite:
                for k,g in v_data.items():
                    if k not in G[u][v].keys() or G[u][v][k] is None:
                        G[u][v][k] = g
                    else:
                        if verbose:
                            print(f"Skipping key {k} for edge {(u,v)} because already existed with value {G[u][v][k]}")
            else:
                G[u][v].update(v_data)
                
def edge_attribute_dict_from_edges(edges,
                                    value_to_store = True):
    return_dict = dict()
    for u,v in edges:
        if u not in return_dict.keys():
            return_dict[u] = dict()
        if v not in return_dict[u].keys():
            return_dict[u][v] = value_to_store
            
    return return_dict
    
def nodes_with_parent_branching(G):
    node_names = np.array(list(G.nodes()))
    n_siblings = np.array([xu.n_sibling_nodes(G,k) for k in node_names])
    return node_names[n_siblings > 0]

def nodes_with_parent_non_branching(G):
    node_names = np.array(list(G.nodes()))
    n_siblings = np.array([xu.n_sibling_nodes(G,k) for k in node_names])
    return node_names[n_siblings == 0]


# ------- 7/17: Helps with the axon finder ---------
def starting_node_from_DiG(G,verbose = False):
    """
    Purpose: To find the nodes in a graph
    with no upstream nodes

    Application: To potentially find
    the starting node

    """
    

    nodes = list(G.nodes())
    upstream_array = []
    upstream_array = [None if xu.upstream_node(G,k,return_single=False) is None else 1 for k in nodes]
    argnan_idx = nu.argnan(upstream_array)
    st_node = nodes[argnan_idx[0]]
    if verbose:
        print(f"st_node = {st_node}")

    return st_node

#def most_upstream_node(G,verbose = False):
    

def shortest_path(G,start,end,weight=None,catch_error=False):
    """
    Purpose: Wrapper for the networkx shortest path
    
    """
    return nx.shortest_path(G,start,end,weight=weight)

def G_from_edges(edges,nodes=None,graph_type = "DiGraph"):
    G = getattr(nx,graph_type)()
    if nodes is not None:
        G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    return G

def downstream_conn_comps(G,
                         nodes,
                         start_node=None,
                         verbose = False,
                         return_upstream_node_dict=True):
    """
    Purpose: To group branches into those that 
    are connected to the same upstream node in the possible lists

    Pseudocode: 
    0) Creat e a list to hold all of the possible edges of a graph
    For each node: 
    1) Calculate the shortest path from each branch to the starting node
    2) If any of the other branches are on the list then add an edge from 
    that branch to the current branch

    3) Create a directed graph from the edges
    4) Divide the directed graph into connected components

    For each connected component
    5) Find the most upstream node and add to a dictionary the 
    upstream node --> group of whole connected components
    
    Ex: 
    xu.downstream_conn_comps(G = limb_obj.concept_network_directional,
    nodes = [317, 338, 341, 342, 365, 389, 393, 438],
    start_node = limb_obj.current_starting_node,#limb_obj.current_starting_node
    verbose = False
    )

    """

    if start_node is None:
        start_node = xu.starting_node_from_DiG(G,verbose = False)

    #0) Creat e a list to hold all of the possible edges of a graph
    edge_list = []

    for n in nodes:
        shortest_path = xu.shortest_path(G,start_node,n)[:-1]
        nodes_on_path = np.intersect1d(nodes,shortest_path)
        if verbose:
            print(f"For node {n}, branches on shortest path = {nodes_on_path}")

        edge_list += [[k,n] for k in nodes_on_path]

    #3) Create a directed graph from the edges
    G_conn = xu.G_from_edges(edge_list,nodes=nodes)
    conn_comp = xu.connected_components(G_conn)

    if verbose:
        print(f"# of conn_comp = {len(conn_comp)}")


    if return_upstream_node_dict:
        return_dict = dict()

        for j,c in enumerate(conn_comp):
            G_curr = G_conn.subgraph(c)
            curr_st_node = xu.starting_node_from_DiG(G_curr)
            if verbose:
                print(f"Conn Comp {j}: start_node = {curr_st_node}, conn comp = {c}")

            return_dict[curr_st_node] = c

        return return_dict
    else:
        return conn_comp
    
    
#import itertools
#import time
def all_connected_subgraphs(
    G,
    start_node=None,
    print_subgraphs = False,
    verbose=False,):
    """
    Getting allthe connected subgraphs
    """
    st = time.time() 
    all_connected_subgraphs = []

    if verbose:
        print(f"start_node = {start_node}")
    # here we ask for all connected subgraphs that have at least 2 nodes AND have less nodes than the input graph
    for nb_nodes in range(2, G.number_of_nodes()):
        for SG in (G.subgraph(selected_nodes) for selected_nodes in itertools.combinations(G, nb_nodes)):
            if nx.is_connected(SG):
                if start_node is not None:
                    if not start_node in SG:
                        continue
                if print_subgraphs:
                    print(f"{SG.nodes}")
                all_connected_subgraphs.append(SG.nodes)
                
                
    if verbose:
        print(f"# of subgraphs = {len(all_connected_subgraphs)} (time = {time.time() - st})")
    return all_connected_subgraphs

def connected_component_with_node(
    node,
    connected_components = None,
    G = None,
    return_only_one = True,
    verbose = False,
    ):
    """
    Purpose: To find the connected
    component with a certain node id

    Psuedocode: 
    1) Get the connected components if given a graph
    2) Iterate through the connected components and 
    check if the desired node is in the conn comp (if yes then save off)
    3) If required, check that only one connected component
    4) Return winning conn comps
    
    Ex: 
    xu.connected_component_with_node(3,connected_components= [[1,2,3,4],[5,6]],
                             verbose=True)
    >> winning_conn = [[1, 2, 3, 4]]
    
    
    """
    if connected_components is None:
        connected_components = xu.connected_components(G)

    winning_conn = [k for k in connected_components if node in k]

    if verbose:
        print(f"winning_conn = {winning_conn}")

    if return_only_one:
        if len(winning_conn) != 1:
            raise Exception(f"Not one winning component with node {node}: {winning_conn}")
        winning_conn = winning_conn[0]    

    return winning_conn

def most_upstream_node(G,nodes=None,verbose = False):
    """
    Purpose: To find the most
    upstream node of a group of nodes in 
    a directional graph
    assuming that there is one most 
    upstream node

    Psuedoode: 
    1) Find the node with the most downstream nodes
    
    Ex: 
    xu.most_upstream_node( G = neuron_obj[6].concept_network_directional,
    nodes = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36],
                   verbose = True
    )
    """
    if nodes is None:
        nodes = list(G.nodes())

    nodes = np.array(nodes)
    down_count = np.array([xu.n_all_downstream_nodes(G,k) for k in nodes])
    if verbose:
        print(f"# of downstream for each node = {down_count}")
    return nodes[np.argmax(down_count)]

def least_downstream_node(G,nodes,verbose = False):
    """
    Purpose: To find the most
    upstream node of a group of nodes in 
    a directional graph
    assuming that there is one most 
    upstream node

    Psuedoode: 
    1) Find the node with the most downstream nodes
    
    Ex: 
    xu.most_upstream_node( G = neuron_obj[6].concept_network_directional,
    nodes = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36],
                   verbose = True
    )
    """

    nodes = np.array(nodes)
    down_count = np.array([xu.n_all_downstream_nodes(G,k) for k in nodes])
    if verbose:
        print(f"# of downstream for each node = {down_count}")
    return nodes[np.argmin(down_count)]

#from datasci_tools import numpy_utils as nu
def check_downstream_nodes_on_same_path(G,
    nodes,
    start_node,
    verbose = False,):
    """
    Purpose: To determine if downstream
    nodes are all along the same path
    to a starting node or not

    Pseudocode: 
    1) Get the shortest path for each to the start node
    2) Do a union of all of the paths
    3) if the union is greater than the size of longest path
    --> then false
    
    Ex: 
    xu.check_downstream_nodes_on_same_path(G = limb_obj.concept_network_directional,
    nodes = [25,26,23,21,27],
    start_node = 24 )
    """


    shortest_paths = [xu.shortest_path(G,start_node,k) for k in nodes]
    shortest_paths_len = [len(k) for k in shortest_paths]
    union_path = nu.union1d_multi_list(shortest_paths)
    if verbose:
        print(f"shortest_paths_len= {shortest_paths_len}")
        print(f"len(union_path) = {len(union_path)}")

    if len(union_path) > np.max(shortest_paths_len):
        return False
    else:
        return True
    
def copy_G_without_data(G):
    new_G = type(G)()
    new_G.add_nodes_from(G.nodes())
    new_G.add_edges_from(G.edges())
    return new_G

nodes_edges_only_G = copy_G_without_data

def subgraph_within_radius(G,node,radius,distance="weight",plot_subgraph=False):
    """
    Purpose: Will return the subgraph surrounding a certain
    node that are a radius distance away
    
    Ex: 
    G = nx.Graph()
    G.add_weighted_edges_from([[1,2,5],[2,3,10],[3,4,6],[2,5,3]])
    #nx.draw(G,with_labels = True)

    xu.subgraph_within_radius(G,3,6,plot_subgraph=True)
    """
    G_loc = nx.generators.ego_graph(G,node,radius,distance=distance)
    if plot_subgraph:
        nx.draw(G_loc,with_labels = True)
    return G_loc

def nodes_within_radius(G,node,radius,distance="weight",**kwargs):
    """
    Purpose: Will find the nodes that 
    are within a certain radius of a node in a
    graph
    
    Ex: (works with digraph but only in direction of arrows is allowed, 
        backwards radius not work)
    G = nx.Graph()
    G.add_weighted_edges_from([[1,2,5],[2,3,10],[3,4,6],[2,5,3]])
    #nx.draw(G,with_labels = True)

    xu.nodes_within_radius(G,3,6,plot_subgraph=True)
    """
    G_neighbor = xu.subgraph_within_radius(G,
                                           node,
                                           radius,
                                           distance=distance,
                                           **kwargs)
    return list(G_neighbor.nodes())

#import copy
def expand_edges_to_nodes_within_radius(G,radius,distance="weight",
                                        copy_graph=True,
                                        verbose=False,
                                       plot_graph=False):
    """
    Purpose: Will add edges between those nodes
    that are within a radius distance of eachother
    
    Pseudocode: 
    For each node in the graph
    1) Find the nodes within a certain radius
    2) add edges from node to neighbor nodes to the graph
    
    Ex: 
    G = nx.DiGraph()
    G.add_weighted_edges_from([[1,2,5],[2,3,10],[3,4,6],[2,5,3]])
    G_new = xu.expand_edges_to_nodes_within_radius(G,radius = 20,plot_graph=True,verbose=True)
    """
    if copy_graph:
        G = copy.deepcopy(G)
    if verbose:
        print(f"# of edges at beginning of expanding edges = {len(G.edges())}")
    for n in G.nodes():
        neighb = xu.nodes_within_radius(G,n,radius=radius,
                                       distance=distance)
        if verbose:
            print(f"Node {n} has neighbors {neighb}")
            
        G.add_edges_from([(n,k) for k in neighb])
        
    if verbose:
        print(f"# of edges at END of expanding edges = {len(G.edges())}") 
        
    if plot_graph:
        print(f"Plotting graph after new edges added")
        nx.draw(G,with_labels = True)
        
    return G

def nodes_on_all_pairwise_paths_betweeen_nodes(G,nodes):
    """
    Find all nodes that exist on pairwise
    paths between nodes in a group
    
    Pseudocode: 
    1) Create a list with the nodes requested (final node)
    For each node
       Iterate through all other nodes
           find the shortest path between nodes
           Add to the final nodes if shortest path exists
           
    Ex: 
    G = nx.from_edgelist([[1,2],[2,3],[3,4],[2,5]])
    xu.nodes_on_all_pairwise_paths_betweeen_nodes(G,[1,4,5,3])
    """
    nodes= np.array(nodes)
    final_nodes = np.array(nodes)
    
    for n1 in final_nodes:
        for n2 in  nodes[nodes!= n1]:
            try:
                shortest_path = xu.shortest_path(G,n1,n2)
            except:
                shortest_path = []
            
            final_nodes= np.union1d(final_nodes,shortest_path)
            
    return final_nodes

def local_radius_conn_comps(G,nodes,radius,
                            add_nodes_on_paths_inside_connected_components = True,
                            return_upstream_dict = False,
                           verbose = False):
    """
    Purpose: Will group together nodes in the 
    list provided that are within a certain
    radius distance from each other 
    (and optionally add the nodes that are in between paths
    between nodes in the connected component)
    
    Pseudocode: 
    1) expand the edges of the graph with the specified radius
    2) Take a subgraph of the new expanded graph
    3) Divided the subgraph into connected components
    4) If requested, expand the connected components to
    include nodes that lie on paths between nodes within a connected component
    
    Ex: 
    G = nx.DiGraph()
    G.add_weighted_edges_from([[1,2,5],[2,3,10],[3,4,6],[4,6,12],[6,7,7],[2,5,3]])
    G_new = xu.local_radius_conn_comps(G,nodes=[1,5,6,7],radius = 7,verbose=True)
    """
    #1) expand the edges of the graph with the specified radius
    G_exp = expand_edges_to_nodes_within_radius(G,radius)
    
    #2) Take a subgraph of the new expanded graph 
    G_exp_sub = G_exp.subgraph(nodes)
    
    #3) Divided the subgraph into connected components
    conn_comp = xu.connected_components(G_exp_sub)
    
    if verbose:
        print(f"conn_comp = {conn_comp}")
    
    if add_nodes_on_paths_inside_connected_components:
        
        conn_comp = [list(xu.nodes_on_all_pairwise_paths_betweeen_nodes(G,k).astype("int")) for k in conn_comp]
        #print(f"After add nodes on path, conn_comp = {conn_comp}")
        
    if return_upstream_dict:
        conn_comp = {xu.most_upstream_node(G,k):k for k in conn_comp}
        
    return conn_comp


def expand_nodes_to_all_nodes_on_path_between_nodes(G,nodes):
    return xu.all_nodes_on_shortest_paths_between_nodes(G,nodes)

def set_node_attributes_from_df(
    G,
    df,
    index_name=node_id_default):
    nx.set_node_attributes(G, df.set_index(index_name).to_dict('index'))
    return G

def edge_df_optimized(
    G,
    edge_key=None,
    nodelist=None,
    source= "source",
    target = "target",
    node_attributes = None,
    node_attributes_source_name = None,
    node_attributes_target_name = None,
    **kwargs):
    """
    edge_key: Returns just the edges 
    """

    
    
    
    return_df =  nx.convert_matrix.to_pandas_edgelist(G,
                                                source= source,
                                                target=target,
                                               nodelist=nodelist,
                                               **kwargs)
    
    if node_attributes is not None:
        return_df = xu.add_node_attributes_to_edge_df(
            return_df,
            source= source,
            target = target,
            node_attributes = node_attributes,
            node_attributes_source_name = node_attributes_source_name,
            node_attributes_target_name = node_attributes_target_name,
            G = G,)
        
    return return_df

def add_node_attributes_to_edge_df(
    edge_df,
    node_attributes,
    source= "source",
    target = "target",
    node_attributes_source_name = None,
    node_attributes_target_name = None,
    node_df = None,
    G = None,
    verbose = False,
    ):
    """
    Purpose: To add node attributes to an edge_df already generated
    
    xu.add_node_attributes_to_edge_df(
        edge_df_pre,
        node_attributes = ["gnn_cell_type"],
        verbose = True,
        G = G,
        node_attributes_source_name = "presyn",
        node_attributes_target_name = "postsyn",
        #node_df = node_df
    )
    """
    
    if node_attributes_source_name is None:
        node_attributes_source_name = source
    if node_attributes_target_name is None:
        node_attributes_target_name = target
    
    return_df = edge_df
    
    if node_df is None:
        node_df = xu.node_df(G,node_id=source,verbose = verbose)
        
    
    node_df = node_df[[source] + list(node_attributes)]
    for old_name,prefix in zip([source,target],
                               [node_attributes_source_name,
                                 node_attributes_target_name]):
        rename_dict = {source:old_name}
        rename_dict.update({k:f"{prefix}_{k}" for k in node_df.columns
                           if k != source and 
                            f"{prefix}_{k}" not in return_df.columns})
        node_df_curr = pu.rename_columns(node_df,rename_dict)
        return_df= pd.merge(return_df,node_df_curr,on=old_name,how="left")
        
    return return_df
        
        

def G_from_pandas_edgelist(df,
                           source = "source",
                           target = "target",
                           graph_type = nx.MultiDiGraph,
                           edge_attr = True,
                          verbose = False,
                          ):
    """
    Purpose: Will create a graph from a pandas edgelist
    
    Ex: 
    """
    st = time.time()
    
    if type(graph_type) == str:
        graph_type = getattr(nx,graph_type)
    
    G = nx.from_pandas_edgelist(df,
                           source = source,
                           target = target,
                           edge_attr = edge_attr,
                           create_using = graph_type())
    if verbose:
        print(f"Total time for Graph creation = {time.time() - st}")
        
    return G

def edge_df_from_G(G,
                   source_name= "source",
                   target_name = "target",**kwargs):
    return xu.edge_df_optimized(G,
                                source = source_name,
                                target = target_name,
                                **kwargs)
    
#import time
def edge_and_node_df(G,
                    edge_df_ids,
                    node_df_id=upstream_name,
                     edge_df = None,
                     node_df = None,
                     verbose = False,
                     return_node_df = False
                    ):
    """
    Purpose: To create a dataframe
    with the edges and the node attributes apended to the edges
    
    Pseudocode: 
    1) Generate the edge df
    2) Generate the node df
    3) merge the node df to the edge df for each fo the edge ids
    4) Return the dataframe
    
    Ex: 
    edge_df_ids=["presyn","postsyn"]
    edge_df = xu.edge_df_from_G(G=G_proof_v6,
                          source_name = edge_df_ids[0],
                          target_name = edge_df_ids[1],

                         )

    edge_node_df = xu.edge_and_node_df(G_proof_v6,
                       edge_df_ids=edge_df_ids,
                       node_df_id="segment_split_id",
                       verbose = True,
                                      edge_df = edge_df)
    
    """
    
    
    st = time.time()
    if edge_df is None:
        e_df = xu.edge_df_from_G(G,
                      source_name = edge_df_ids[0],
                      target_name = edge_df_ids[1],

                     )
    else:
        e_df = edge_df
    
    if verbose:
        print(f"1) edge df creation: {time.time() - st}")
        st = time.time()
        
    if node_df is None:
        node_df = xu.node_df(G,
                          node_id=node_df_id)
    
    if verbose:
        print(f"2) node df creation: {time.time() - st}")
        st = time.time()



    for t in edge_df_ids:
        node_df_renamed = pu.add_prefix_to_columns(node_df,f"{t}_")
        node_df_renamed_id = f"{t}_{node_df_id}"
        e_df = pd.merge(e_df,
                 node_df_renamed,
                 how="left",
                 left_on=t,
                 right_on=node_df_renamed_id,
                )

        e_df = pu.delete_columns(e_df,[node_df_renamed_id])

    if verbose:
        print(f"3) Total time for merges: {time.time() - st}")
    
    if return_node_df:
        return e_df,node_df
    else:
        return e_df

def print_node_edges_counts(G,G_prefix=""):
    print(f"{G_prefix} Graph: # of nodes = {len(G.nodes())}, # of edges = {len(G.edges())}")
    




    
def closest_k_leaf_neighbors_in_binary_tree(
    G,
    node,
    k,
    return_exactly_k=True,
    verbose = False,
    max_iterations = 10_000):
    """
    Purpose: To return the k closest leaf nodes in a binary
    tree by traversing the upstream nodes and finding all downstream nodes
    
    Pseudocode: 
    while number of neighbors is less than min
    1) Get the upstream node of the current node
    2) Get all the downstream nodes
    3) Add only the leaf nodes as neighbors

    
    """
    if verbose:
        print(f"start_node = {node}")
    upstream_node = node
    neighbor_leaves = []

    leave_nodes = np.array(xu.get_nodes_of_out_degree_k(G,0))
    counter = 0
    while len(neighbor_leaves) < k:
        counter+= 1
        upstream_node = xu.upstream_node(G,upstream_node)
        neighbor_leaves = np.intersect1d(xu.all_downstream_nodes(G,upstream_node),leave_nodes)
        neighbor_leaves = neighbor_leaves[neighbor_leaves!= node]
        if verbose:
            print(f"On iteration {counter}: {upstream_node} had {len(neighbor_leaves)} downstream_leaves: {neighbor_leaves}")

        if len(neighbor_leaves) >= k:
            break
            
        if counter > max_iterations: 
            raise Exception("Reached max iterations")
            
    if return_exactly_k:
        neighbor_leaves = neighbor_leaves[:k]
    
    return neighbor_leaves
    
       
def remove_nodes_from(G,nodes,copy = False):
    if copy:
        G = G.copy()
    G.remove_nodes_from(nodes)
    return G
       
    

def all_paths_to_leaf_nodes(
    G,
    start_node=None,
    leaf_nodes = None,
    verbose = False
    ):

    """
    To find all of the list of branch paths to leaf nodes on 
    limb

    1) Get all of the leaf nodes
    2) Get all paths from starting node to leaf nodes
    """
    if leaf_nodes is None:
        leaf_nodes = xu.leaf_nodes(G)

    if start_node is None:
        start_node = xu.most_upstream_node(G)

    if verbose:
        print(f"leaf_nodes= {leaf_nodes}")
        print(f"start node = {start_node}")


    all_paths = [xu.shortest_path(G,start_node,k) for k in leaf_nodes]
    if verbose:
        for i,p in enumerate(all_paths):
            print(f"Path {i}: {p}")
        
    return all_paths

#import networkx as nx
def remove_edge_reattach_children_di(
    G,
    node,
    inplace = True,
    verbose = False,):
    """
    Purpose: To remove a node and reattach any children to the parents
    
    Pseudocode: 
    1) Get the parent of the node
    2) Get the children of the node
    3) Remove the node
    4) Create edges from the parent to the children
    
    Example: 
    
    import networkx as nx
    import matplotlib.pyplot as plt
    G1 = nx.DiGraph()
    G1.add_edges_from([[1,2],[2,3],[2,4]])
    print(f"Before")
    nx.draw(G1,with_labels = True)
    plt.show()
    G1_new = remove_edge_reattach_children_di(G1,2)
    print(f"After removal")
    nx.draw(G1_new,with_labels = True)
    """
    if not inplace:
        G = copy.deepcopy(G)
    parent = xu.upstream_node(G,node)
    children = xu.downstream_nodes(G,node)
    
    G.remove_nodes_from([node])
    new_edges = [(parent,k) for k in children]
    G.add_edges_from(new_edges)
    
    if verbose:
        print(f"For node {node}")
        print(f"parent = {parent}, children = {children}")
        print(f"new_edges = {new_edges}")
    return G

remove_node_reattach_children_di = remove_edge_reattach_children_di

def graph_attr_dict(G):
    return G.graph
def set_graph_attr_with_dict(G,d):
    G.graph.update(d)
def set_graph_attr(G,k,v):
    xu.set_graph_attr_with_dict(G,{k:v})
def get_graph_attr(G,k):
    return G.graph[k]
# ------------ drawing functions --------------
#import matplotlib.pyplot as plt
#import pydot
#from networkx.drawing.nx_pydot import graphviz_layout

def draw_tree(
    G,
    draw_type = "dot",#"twopi" (the circular), "circo" (makes square like)
    node_size=4000,
    font_size = 20,
    font_color = "white",
    figsize=(32,32),
    **kwargs):
    """
    Purpose: To help draw a nice tree graph
    
    #https://stackoverflow.com/questions/57512155/how-to-draw-a-tree-more-beautifully-in-networkx
    """
    
    plt.figure(figsize=figsize)

    T = xu.copy_G_without_data(G)

    pos = graphviz_layout(T, prog="dot")
    nx.draw(T, 
            pos,
            with_labels = True,
            node_size=node_size,
            font_size = font_size,
            font_color = font_color,
            **kwargs
            )
    plt.show()
    
def star_graph(
    n_vertices,
    plot = False):
    G =  nx.from_edgelist([[0,k] for k in range(1,n_vertices)])
    
    if plot:
        nx.draw(G,with_labels = True)
        
    return G
    
#from . import numpy_dep as np
def adjacency_matrix(
    G,
    dense = True,
    nodelist=None,
    return_nodelist = False,
    weight = "weight",
    **kwargs):
    
    adj_matrix = nx.adjacency_matrix(
        G,
        nodelist=nodelist,
        weight=weight,
        **kwargs
    )
    
    if dense:
        adj_matrix = adj_matrix.toarray()
        
    if nodelist is None:
        nodelist = np.array(list(G.nodes()))
    
    if return_nodelist:
        return adj_matrix,nodelist
    else:
        return adj_matrix
    
def modularity_matrix(G,nodelist=None,**kwargs):
    return nx.modularity_matrix(
        G,
        nodelist=nodelist,
        **kwargs
    )

modularity = modularity_matrix

def laplacian(G,nodelist=None,dense = True,**kwargs):
    L = nx.laplacian_matrix(G,nodelist=nodelist,)
    if dense:
        L = L.todense()
    return L

def degree_matrix_from_adj(array):
    return np.diag(np.sum(array,axis=1))

def laplacian_from_adj(array):
    return degree_matrix_from_adj(array) - array

laplacian_matrix = laplacian
    
def G_from_adjacency_matrix(
    matrix,
    nodelist = None,
    plot = False
    ):
    """
    Purpose: To recover a networkx graph
    from an adjacency matrix (and add proper node labels)
    """

    if "sparse" in str(type(matrix)):
        matrix = matrix.toarray()

    G_rec = nx.from_numpy_matrix(matrix)

    if nodelist is not None:
        if len(nodelist) != len(G_rec):
            raise Exception("")
        #print(np.max(list(G_rec.nodes())))
        #print(f"nodelist = {np.max(nodelist)}")
        G_rec = xu.relabel_node_names(G_rec,{i:k for i,k in enumerate(nodelist)},copy=True)
        #print(np.max(list(G_rec.nodes())))

    if plot:
        nx.draw(G_rec,with_labels = True)
        
    return G_rec
    
#import pandas as pd
def feature_matrix_from_G(
    G,
    nodelist = None,
    features = None,
    return_df = False,
    default_value = 0
    ):
    """
    Purpose: to get the node features matrix
    from a list of node features
    """
    if nodelist is None:
        nodelist = list(G.nodes())

    df = pd.DataFrame.from_records([G.nodes[n] for n in nodelist])

    if features is not None:
        for f in features:
            if f not in df.columns:
                df[f] = default_value
        df = df[list(features)]

    if return_df:
        return df
    else:
        return df.to_numpy()
    
def adjacency_feature_info(
    G,
    dense_adjacency = False,
    return_df_for_feature_matrix=True,
    return_dict = True,
    feature_matrix_dtype=None,
    features = None,
    verbose=False,
    ):
    """
    Process: get the information
    needed for GNN training
    1) Node names
    2) feature names
    3) Adjacency matrix
    4) Feature matrix

    """
    if features is None:
        features = np.array(xu.node_df_features(G))
    #TODO: Add in the ability to pass in the features
    adj_matrix,nodelist = np.nan, np.nan
    
    X = xu.feature_matrix_from_G(
        G,
        return_df=return_df_for_feature_matrix,
        features =features,)
    
    if feature_matrix_dtype is not None:
        X = X.astype(feature_matrix_dtype)
    
    if return_dict:
        return dict(
            nodelist = nodelist,
            features=features,
            adjacency=adj_matrix,
            feature_matrix = X,)
    else:
        return nodelist,features,adj_matrix,X
    
    
#-------- searching functions ----------
def nodes_DFS(G,source=None):
    return list(nx.dfs_preorder_nodes(G,source = source))

#from datasci_tools import numpy_utils as nu
def delete_node_attributes(
    G,
    attributes=None,
    attributes_not_to_delete=None,
    nodelist = None,
    verbose = False):
    
    if nodelist is None:
        nodelist = list(G.nodes())
    nodelist = nu.convert_to_array_like(nodelist)
    if attributes is not None:
        attributes = nu.convert_to_array_like(attributes)
    
    for n in nodelist:
        if attributes is None:
            curr_attrs = list(G.nodes[n].keys())
        else:
            curr_attrs = attributes
        #print(f"curr_attrs = {curr_attrs}, attributes = {attributes}")
        for a in curr_attrs:
            if attributes_not_to_delete is not None:
                if a in attributes_not_to_delete:
                    continue
            try:
                del G.nodes[n][a]
            except:
                if verbose:
                    print(f"Couldn't delete {a} from node {n}")
        
    return G

def filter_down_node_attributes(
    G,
    attributes = None,
    attributes_to_delete = None,
    nodelist = None,
    verbose = False
    ):
    
    return xu.delete_node_attributes(
    G,
    attributes=attributes_to_delete,
    attributes_not_to_delete=attributes,
    nodelist = nodelist,
    verbose = verbose)

def set_node_attribute(
    G,
    attribute_name,
    attribute_value,
    node=None,
    verbose = False,
    ):
    """
    Purpose: To set a single node
    attribute (or apply to all the 
    nodes if none given)
    """
    
    
    if node is None:
        node = list(G.nodes())
    
    node = nu.convert_to_array_like(node)
    
    if verbose:
        print(f"Setting {attribute_name} to {attribute_value} for nodes: {node}")
        
    for n in node:
        G.nodes[n][attribute_name] = attribute_value
    
    return G

def nodes_with_non_none_attributes(
    G,
    attribute_name,
    node_name = node_id_default,
    return_attribute_value=False,
    verbose=False):
    """
    Purpose: To find out all the nodes with 
    an autoproofreading filter
    """

    node_df = xu.node_df(G).query(
        f"{attribute_name} == {attribute_name}")

    nodes = node_df[node_name].to_numpy()
    
    if verbose:
        print(f"Nodes without None value in {attribute_name}: {nodes}")

    if return_attribute_value:
        filt_names = node_df[attribute_name].to_numpy()
        return nodes,filt_names
    else:
        return nodes
    
def is_frozen(G):
    """
    Usually happens when iterating over nodes (because it is a dictionary)
    and can't change a dictionaries size while iterating over it
    
    Conclusion: Happens when try to modify the nodes of a subgraph, need to
    make do G.subgraph([nodes]).copy()
    """
    return nx.is_frozen(G)

def edgelist_from_adjacency_matrix(
    array,
    verbose = False
    ):
    """
    Purpose: To convert an adjacency
    matrix to an edgelist

    Pseudocode:
    1) Read in the adjacency matrix to a networkx Graph
    2) export the edges of the Graph
    """
    G = xu.G_from_adjacency_matrix(array)
    edgelist = xu.edges(G)
    if verbose:
        print(f"# of Edges = {len(verbose)}")
    return edgelist

def is_tree(G):
    if nx.number_of_nodes(G) != nx.number_of_edges(G) + 1:
        return False
    return nx.is_connected(G)

def high_degree_nodes(
    G,
    n_children_min = 3,
    ):
    
    return np.array([k for k in G.nodes() if xu.n_downstream_nodes(G,k) >= n_children_min ])
def binary_tree_from_di_tree(
    G,
    verbose = False,
    inplace = False,
    child_idx_to_reattach = 1,
    ):
    """
    Purpose: To convert any tree into a binary tree

    Pseudocode: 
    1) Find the nodes with more than 1 child
    While the list of non-binary nodes is non empty:
    a. Get the first node and all of its children
    b. disconnect parent from all children except first 2
    c. Reattach disconnected children to first/last child
    d. Repeat for next node
    """


    if not inplace:
        G = copy.deepcopy(G)

    high_degree_nodes = xu.high_degree_nodes(G)


    

    while len(high_degree_nodes) > 0:
        if verbose:
            print(f"\n\n---New Loop: high_degree_nodes=\n    {high_degree_nodes}")
        for n in high_degree_nodes:
            if verbose:
                print(f"\n---Working on node {n}")
            #a. Get the first node and all of its children
            children = xu.downstream_nodes(G,n)
            if verbose:
                print(f"children = {children}")

            keep_children = children[:2]
            disconnect_children = children[2:]

            G.remove_edges_from([(n,k) for k in disconnect_children])
            G.add_edges_from([
                (keep_children[child_idx_to_reattach],k) for k in disconnect_children])

        high_degree_nodes = xu.high_degree_nodes(G)
        
    # to check everything went well:
    tree_status = [xu.is_tree(k) for k in xu.connected_components(nx.Graph(G),return_subgraphs=True)]
    if False in tree_status:
        raise Exception("")
    
    return G
    

def n_connected_components(G):
    return len(xu.connected_components(G))

def get_node_attribute_for_all_nodes(
    G,name,
    return_list = False,
    nodes = None,
    ):
    
    atts = get_node_attributes(
        G,
        name,
        node_list=nodes
    )
    if return_list:
        return list(atts.values())
    return atts

def set_node_attribute_default(G,attributes, default_value = None):
    attributes= nu.convert_to_array_like(attributes)
    for a in attributes:
        for n in G.nodes():
            if a not in G.nodes[n]:
                G.nodes[n][a] = default_value
                
def derived_node_attribute(
    G,
    attribute,
    new_attribute,
    func):
    
    for n in G.nodes():
        if attribute in G.nodes[n]:
            G.nodes[n][new_attribute] = func(G.nodes[n][attribute])
            
def derived_node_attribute_from_func(
    G,
    attribute_name,
    func,
    ):
    
    for n in G.nodes():
        G.nodes[n][attribute_name] = func(dict(G.nodes[n]))
        
def derived_edge_attribute_from_func(
    G,
    attribute_name,
    func,
    ):
    
    """
    Ex: 
    def comp_flat(key):
        if key["postsyn_compartment_fine"] is None:
            return key["postsyn_compartment_coarse"]
        else:
            return key["postsyn_compartment_fine"]

    xu.derived_edge_attribute_from_func(
        G,
        "postsyn_compartment_flat",
        comp_flat 
        )
    
    """
    
    for e in G.edges():
        G[e[0]][e[1]][attribute_name] = func(G[e[0]][e[1]])
                
def set_edge_attribute_from_node_attribute(
    G,
    attribute,
    default_value = None,
    upstream_prefix = upstream_name,
    downstream_prefix = downstream_name,
    verbose = False,
    ):
    """
    Purpose: Add a certain node property of the presyn and postsyn
    to the edge properties

    Pseudocode: 
    1) Get a lookup of the property you want
    2) Go through the edges and add it to the edge attribute
    """
    st = time.time()
    attributes = nu.convert_to_array_like(attribute)
    multi_flag = xu.is_multigraph(G)

    for att in attributes: 
        if verbose:
            print(f"--- Working on setting attribute {att}")
        att_dict = {k:G.nodes[k].get(att,default_value) for k in G.nodes()}

        for n1,n2 in G.edges():
            if multi_flag:
                for i in G[n1][n2]:
                    G[n1][n2][i][f"{upstream_prefix}_{att}"] = att_dict[n1]
                    G[n1][n2][i][f"{downstream_prefix}_{att}"] = att_dict[n2]
                    
        if verbose:
            print(f"  --> total time = {time.time() - st}")
    
    return G

def set_edge_attribute(
    G,
    node_1,
    node_2,
    attribute,
    value,
    edge_idx = None):
    
    if edge_idx is not None:
        G[node_1][node_2][edge_idx][attribute] = value
    else:
        G[node_1][node_2][attribute] = value
        
def get_edge_attribute(
    G,
    node_1,
    node_2,
    attribute,
    edge_idx = None):
    
    if edge_idx is not None:
        return G[node_1][node_2][edge_idx][attribute]
    else:
        return G[node_1][node_2][attribute]
    
#import networkx as nx
def convert_to_non_multi(G):
    if xu.is_multigraph(G):
        if xu.is_digraph(G):
            return nx.DiGraph(G)
        else:
            return nx.Graph(G)
    else:
        return G
    
    
def is_isomorphic(G1,G2):
    return nx.is_isomorphic(G1,G2)

def edge_str_from_G(
    G,
    delimiter = ";",
    **kwargs):
    return delimiter.join([f"{e1}->{e2}" for e1,e2 in G.edges()]) + delimiter

#from datasci_tools import string_utils as stru
def motif_Gs_for_n_nodes(
    n,
    graph_type = "DiGraph",
    enforce_n_nodes = True,
    verbose = False,
    plot = False,
    **kwargs
    ):
    """
    Purpose: To compute all possible combinations
    of edges in n nodes

    Pseudocode: 
    1) Get all combinations of edges

    For each connection: 
    a) Build a graph of it
    b) See if the graph matches the dotmotif of another unique graph
    c) If it doesn then add it to the unique list (and register the number of nodes associated)

    2) Filter for a certain amount of nodes
    
    Ex: 
    from datasci_tools import networkx_utils as xu
    xu.motif_Gs_for_n_nodes(n=3,plot = True)
    """

    node_names = [stru.number_to_letter(k).capitalize() for k in range(n)]
    if verbose:
        print(f"node_names = {node_names}")

    if "Di" in graph_type:
        edges = nu.choose_k_permutations(node_names,2)
    else:
        edges = nu.choose_k_combinations(node_names,2)

    edges = np.array(edges)
    binary_mat = nu.binary_permutation_matrix(len(edges))

    if verbose:
        print(f"# of edges = {len(edges)} with {len(binary_mat)} unique combinations")


    unique_G = []
    for e_idx in binary_mat:
        curr_edges = edges[np.where(e_idx)[0]]
        if verbose:
            print(f"Working on edges = {curr_edges}")

        #a) Build a graph of it
        G = getattr(nx,graph_type)()
        G.add_edges_from(curr_edges)

        #b) See if the graph matches the dotmotif of another unique graph
        found = False
        for j,(curr_G) in enumerate(unique_G):

            if len(curr_G.nodes()) != len(G.nodes()):
                continue

            iso_match = xu.is_isomorphic(G,curr_G)

            if iso_match:
                if verbose:
                    print(f"Found matching graph: {j}")
                found = True
                break

        if not found: 
            unique_G.append(G)
            if plot:
                nx.draw(G,with_labels = True)
                plt.show()

    if verbose:
        print(f"Unique number of Graphs for {n} nodes: {len(unique_G)}")


    if enforce_n_nodes:
        unique_G = [k for k in unique_G if len(k.nodes()) == n]
        if verbose:
            print(f"After filtering to {n} node graphs: {len(unique_G)}")

    return unique_G
    
    
def motif_strs_for_n_nodes(
    n,
    **kwargs):
    motif_Gs = xu.motif_Gs_for_n_nodes(n=n,**kwargs)
    return [xu.edge_str_from_G(k,**kwargs) for k in motif_Gs]

def compute_node_attribute(
    G,
    attribute,
    attribute_function,
    ):
    
    for n in G.nodes():
        G.nodes[n][attribute] = attribute_function(G.nodes[n])
        
        
#import networkx.classes.function as cls_func
def path_distance(G,path,weight="weight"):
    if weight is None:
        return len(path) - 1
    else:
        return cls_func.path_weight(G,path,weight=weight)
    
    
# -------- for different graph constructors ----
def path_graph(n):
    return nx.path_graph(n)

line_graph = path_graph

def complete_graph(n):
    return nx.complete_graph(n)
    
def cycle_graph(n):
    return nx.cycle_graph(n)
circle_graph = cycle_graph

def balanced_tree(degree=2,height=None,n=None):
    # compute the number of splits needed
    if height is None:
        height = np.ceil(nu.log_n(n+1,degree)-1).astype('int')
        
    G = nx.balanced_tree(degree,height)
    if n is not None:
        G = G.subgraph(np.arange(0,n)).copy()
    
    return G

def binary_tree(height=None,n=None):
    return balanced_tree(degree=2,height=height,n=n)

def star_graph(n,plot=False):
    G = nx.from_edgelist([(0,k) for k in range(1,n)])
    if plot:
        nx.draw(G,with_labels=True)
    return G

def self_loop_edges(n):
    """
    Purpose: To create self loops 
    from tne number of nodes
    """
    edges = np.vstack([np.arange(n),np.arange(n)]).T
    return edges
    
def edge_list_from_graph_type(
    n,
    graph_type=None,
    graph_func = None,
    plot = False,
    add_self_loops=False,
    bidirectional = False,
    **kwargs
    ):
    """
    Purpose: To generate an edgelist for a
    given graph type and size
    
    --- Example ---
    n = 10
    graph_type = "complete_graph"

    xu.edge_list_from_graph_type(
        n=n,
        graph_type=graph_type,
        plot=True
    )
    """
    
    G = getattr(xu,graph_type)(n=n,**kwargs)
    if plot:
        nx.draw(G,with_labels = True)
    return_edges = np.array(list(G.edges()))
    
    if bidirectional and len(return_edges) > 0:
        return_edges = np.vstack([return_edges,return_edges[:,[1,0]]])
    
    
    if add_self_loops:
        return_edges = np.vstack([return_edges.reshape(-1,2),xu.self_loop_edges(n)])
    return return_edges.astype('int')


def shortest_path_length(
    G, 
    source=None, 
    target=None, 
    weight=None, 
    method='dijkstra'):
    return nx.shortest_path_length(
        G=G,
        source=source, 
        target=target, 
        weight=weight, 
        method=method,
    )

def subgraph_downstream_of_node(G,node,include_self=True):
    return G.subgraph(xu.all_downstream_nodes(
                 G,
                node,
                include_self=include_self
            )).copy()

def all_downstream_nodes_including_self(G,node):
    return xu.all_downstream_nodes(
                 G,
                node,
                include_self=True
            )

#from datasci_tools.tqdm_utils import tqdm
def compute_edge_statistic(
    G,
    edge_func,
    verbose = False,
    verbose_loop = False,
    ):
    st = time.time()
    
    for node1 in tqdm(list(G.nodes())):
        for node2 in dict(G[node1]).keys():
            G = edge_func(
                G,
                node1,
                node2,
                verbose = verbose_loop,
            )
    if verbose:
        print(f"Total time for adding {edge_func.__name__} = {time.time() - st} ")
    return G

def edge_graph(
    G,
    plot_node_graph=False,
    plot_edge_graph=False):
    
    """
    Purpose: Converts a graph into a graph
    where the edges are now the nodes and 
    edges between the nodes are if the 
    edges are incident on the same node
    
    Ex: 
    G_test = nx.from_edgelist([(1,2),(2,3),(2,4),(3,5),(3,6)])
    xu.edge_graph(G_test,plot_node_graph=True,plot_edge_graph=True)
    """
    
    if plot_node_graph:
        print(f"Node Graph before conversion")
        nx.draw(G,with_labels=True)
        plt.show()
        
    G_edge = nx.line_graph(G)
    
    if plot_edge_graph:
        print(f"Node Graph before conversion")
        nx.draw(G_edge,with_labels=True)
        plt.show()
        
    return G_edge

def unique_vertices_edges_from_vertices_edges(
    vertices,
    edges,
    verbose = False,
    return_vertex_index = False,
    ):
    
    unique_verts,vert_first_index,verts_index = np.unique(vertices,return_index=True,return_inverse=True,axis=0)
    unique_edges = verts_index[edges]
    
    if verbose:
        print(f"# of vertices went from {len(vertices)} -> {len(unique_verts)}")
        
    if return_vertex_index:
        return unique_verts,unique_edges,vert_first_index
    else:
        return unique_verts,unique_edges

def graph_from_unique_vertices_edges(
    vertices,
    edges,
    graph_type = "Graph",
    verbose = False,
    ):
    verts_unique = vertices
    edges_unique = edges
    
    G = getattr(nx,graph_type)()

    node_to_coord = {i:dict(coordinates=k) for i,k in enumerate(verts_unique)}
    weights = np.linalg.norm(verts_unique[edges_unique[:,0]] - verts_unique[edges_unique[:,1]],axis=1).reshape(-1,1)

    G.add_nodes_from(list(node_to_coord.keys()))
    G.add_weighted_edges_from(np.hstack([edges_unique,weights]))
    
    nx.set_node_attributes(G,node_to_coord)
    return G

def graph_from_non_unique_vertices_edges(
    vertices,
    edges,
    graph_type = "Graph",
    verbose = False
    ):
    
    verts_unique,edges_unique = unique_vertices_edges_from_vertices_edges(
        vertices,edges,verbose=verbose,
    )
    
    return graph_from_unique_vertices_edges(
        vertices=verts_unique,
        edges = edges_unique,
        graph_type = graph_type,
        verbose = verbose
    )

def shortest_path_graph(
    G,
    start,
    end,
    weight=None,
    **kwargs
    ):
    """
    Purpose: To create a path subgraph between 
    two nodes 

    Pseudocode: 
    1) Find shortest path
    """
    path = xu.shortest_path(G,start,end,weight = weight,**kwargs)
    return G.subgraph(path).copy()

def shortest_path_from_most_upstream(
    G,
    node,
    weight = None,
    nodes_to_exclude = None,
    **kwargs
    ):
    most_up_node = xu.most_upstream_node(G)
    return_nodes= xu.shortest_path(G,most_up_node,node,weight = weight,**kwargs)
    
    if nodes_to_exclude is not None:
        return_nodes = [k for k in return_nodes if k not in nodes_to_exclude]
        
    return return_nodes
    
def shortest_path_graph_from_most_upstream(
    G,
    node,
    weight = None,
    nodes_to_exclude = None,
    **kwargs
    ):
    """
    Purpose: To create a path subgraph from
    the most upstream node to another node

    Psueodocode:
    1) Get the most upstream node
    2) Get the path subgraph
    """
    nodes = xu.shortest_path_from_most_upstream(
    G,
    node=node,
    weight = node,
    nodes_to_exclude = nodes_to_exclude,
    **kwargs
    )
    
    return G.subgraph(nodes).copy()


def undirected_sym_G_from_DiG(
    G,
    keep_node_attributes=True,
    verbose = False,):
    """
    Purpose: Want to construct a new graph with:
    adjusted adjacency matrix, node features

    Pseudocode: 
    1) Export the adjacency matrix with the node names
    2) Convert the adjacency matrix into a symmetric one
    3) Use new adjacency matrix and node names to create a new graph

    """
    #1) Export the adjacency matrix with the node names
    A, nodes = xu.adjacency_matrix(
        G,
        return_nodelist = True 
    )

    #2) Convert the adjacency matrix into a symmetric one
    A_undir = (A + A.T)/2
    
    #3) Use new adjacency matrix and node names to create a new graph
    G_undir = xu.G_from_adjacency_matrix(
        A_undir,
        nodelist = nodes,
    )

    if keep_node_attributes:
        #1b) Export the node attributes
        node_df = xu.node_df(G)

        xu.set_node_attributes_from_df(
            G_undir,
            node_df,
        )
        
    if verbose:
        print(f"After symmmetric conversion to undirected graph")
        xu.print_node_edges_counts(G_undir)

    return G_undir


def radius_threshold_graph_from_coordinates(
    coordinates,
    radius,
    ):
    """
    Purpose: Create a graph where the nodes of
    the graph come from the coordinates and the 
    edges are between any 2 coordinates that
    are within a threshold distance of each other
    """
    adj_matrix = nu.distance_matrix(
        coordinates,
        threshold = radius,
        default_value = -1,
    )
    
    adj_matrix = adj_matrix + np.eye(len(adj_matrix))*-1
    adj_matrix[adj_matrix >= 0] = 1
    adj_matrix[adj_matrix==-1] = 0
    
    G = xu.G_from_adjacency_matrix(adj_matrix)
    return G

def filter_away_downstream_nodes(
    G,
    nodes,
    verbose = False,
    ):
    """
    Purpose: to eliminate any nodes
    that are downstream of another in 
    a group

    Pseudocode: 
    For each node in the list:
    1) Compute the downstream nodes
    2) Do a set difference between the list to check
    and the downstream nodes to eliminate them
    
    Ex: 
    xu.filter_away_downstream_nodes(
        G,
        ['L0_27', 'L1_17', 'L2_0', 'L3_1', 'L4_2', 'L5_9', 'L6_0',"S0"]
    )
    """
    all_downstream = np.concatenate([xu.all_downstream_nodes(G,n,return_empty_list_if_none=True) for n in nodes])
    nodes_no_downstream = np.setdiff1d(nodes,all_downstream)
    
    if verbose:
        print(f"List filtered from {len(nodes)} nodes to {len(nodes_no_downstream)} nodes")
        
    return nodes_no_downstream

def values_on_relative_nodes(
    G,
    node,
    attribute = "skeletal_length",
    default_value = 0,
    direction = "downstream",
    include_self = True,
    aggr_func = np.sum,
    verbose = False,
    return_nodes = False,
    ):
    if type(aggr_func) == str:
        aggr_func = getattr(np,aggr_func)

    node_func = getattr(xu,f"all_{direction}_nodes")

    #1) Get all of the directional nodes
    nodes = node_func(G,node,include_self=include_self)
    if verbose:
        print(f"{direction} Nodes = {nodes}")

    #2) Collect the attribute from all the nodes
    attributes = [G.nodes[n].get(attribute,default_value) for n in nodes]
    if verbose:
        print(f"attributes = {attributes}")
        
    if return_nodes:
        return attributes,nodes
    else:
        return attributes
    
def aggregate_values_on_relative_nodes(
    G,
    node,
    attribute = "skeletal_length",
    default_value = 0,
    direction = "downstream",
    include_self = True,
    aggr_func = np.sum,
    verbose = False,
    ):
    """
    Purpose: To aggregate an attribute value
    downstream of a node

    Pseudocode: 
    1) Get all of the directional nodes
    2) Collect the attribute from all the nodes
    3) Aggregate the attribute
    """
    attributes = values_on_relative_nodes(
        G,
        node,
        attribute = attribute,
        default_value = default_value,
        direction = direction,
        include_self = include_self,
        aggr_func = aggr_func,
        verbose = verbose,
        return_nodes = False,
        )
    
    #3) Aggregate the attribute
    aggr_value = aggr_func(attributes)

    if verbose:
        print(f"Final value = {aggr_value}")
    
    return aggr_value

def sum_downstream_attribute(
    G,
    node,
    attribute,
    include_self = True,
    **kwargs
    ):
    return aggregate_values_on_relative_nodes(
        G,
        node,
        attribute,
        direction = "downstream",
        include_self=include_self,
        **kwargs
    )

def n_nodes(G,nodes = None):
    if nodes is not None:
        G = G.subgraph(nodes)
    return G.number_of_nodes()

def n_edges(G,nodes=None):
    if nodes is not None:
        G = G.subgraph(nodes)
    return G.number_of_edges()

def n_edges_out(G,nodes=None):
    from graph_tools import graph_statistics as gstat
    degree_distr = gstat.degree_distribution(G,nodes=nodes,degree_type="out")
    return np.sum(degree_distr)

def n_edges_in(G,nodes=None):
    from graph_tools import graph_statistics as gstat
    degree_distr = gstat.degree_distribution(G,nodes=nodes,degree_type="in")
    return np.sum(degree_distr)

def shortest_path_along_node_subset_old(
    G,
    start,
    end,
    node_subset,
    verbose = False,
    verbose_time = False,
    weight = "weight",
    ):
    """
    Purpose: To find the shortest path between
    two nodes but the intermediate nodes
    can only be from a certain subset of nodes

    Pseudocode: 
    1) Get all of the nodes connected to start
    and end node (that are in subset)
    and make them group 1, group 2
    respectively
    2) Find the shortest distance between the 
    subgraph of the subset
    3) Concatenate on the whole path
    """

    if verbose_time:
        st = time.time()

    start_neighbors = np.concatenate([np.intersect1d(
        xu.downstream_nodes(G,start),
        node_subset
    ),[start]])

    if verbose_time:
        print(f"Time for start neighbors: {time.time() - st}")
        st = time.time()

    end_neighbors = np.concatenate([np.intersect1d(
        xu.upstream_node(G,end,return_single=False),
        node_subset
    ),[end]])

    if verbose_time:
        print(f"Time for end neighbors: {time.time() - st}")
        st = time.time()

    #node_subset = np.setdiff1d(node_subset,[start,end])
    shortest_path = xu.shortest_path_between_two_sets_of_nodes(
        G.subgraph(node_subset).copy(),
        node_list_1=start_neighbors,
        node_list_2 = end_neighbors,
        verbose = verbose_time,
        return_node_pairs = False,
        weight = weight,
    )

    shortest_path = list(shortest_path)
    if shortest_path[0] != start:
        shortest_path = [start] + shortest_path

    if shortest_path[-1] != end:
        shortest_path.append(end)

    if verbose:
        print(f"shortest_path from {start} to {end} = {shortest_path}")
        
    return shortest_path
        
    
def shortest_path_along_node_subset(
    G,
    start,
    end,
    node_subset,
    verbose = False,
    verbose_time = False,
    weight = None,
    ):
    """
    Purpose: Find the path between two nodes
    but the path can only occur through a subset 
    of the nodes
    
    -- Example: 
    xu.shortest_path_along_node_subset(
        G,
        start = '864691135939275265_0',
        end = '864691135454090602_0',
        node_subset = conu.excitatory_nodes(G_auto),
        verbose = True,
        verbose_time = True,
    )
    """
    global_time = time.time()
    st = time.time()
    curr_G = G.subgraph(list(node_subset) + [start,end])
    if verbose_time:
        print(f"total time for subgraph = {time.time() - st}")
        st = time.time()
    shortest_path = nx.shortest_path(curr_G,start,end,weight = weight)
    if verbose_time:
        print(f"total time for shortest_path = {time.time() - st}")
        st = time.time()
    
    if verbose:
        print(f"shortest_path from {start} to {end} = {shortest_path}")
        
    if verbose_time:
        print(f"total time for shortest path along nodes = {time.time() - global_time}")
        
    return shortest_path

def largest_connected_component(
    G,
    verbose = False):
    conn_comp = list(connected_components(G))
    largest_idx = np.argmax([len(k) for k in conn_comp])
    if verbose:
        print(f"Largest connected component size = {len(conn_comp[largest_idx])}")
        
    return G.subgraph(list(conn_comp[largest_idx]))

def from_pandas_edgelist(
    df,
    source='source',
    target='target',
    edge_attr=None,
    create_using=None,#nx.Graph,nx.MultiDiGraph
    verbose = True,
    **kwargs
    ):
    if verbose:
        st = time.time()
        
    G = nx.from_pandas_edgelist(
        df,
        source=source,
        target=target,
        edge_attr=edge_attr,
        create_using=create_using,
        **kwargs
    )
    
    if verbose:
        print(f"Time for Graph creating = {time.time() - st}")
        
    return G

def graph_type_from_G(G):
    for gt in ["Graph","DiGraph","MultiGraph","MultiDiGraph"]:
        if eval(f"type(G) == getattr(nx,'{gt}')"):
            return gt
    return None

def empty_graph_type_from_G(G):
    return getattr(nx,graph_type_from_G(G))()

def empty_graph_from_type(graph_type):
    return getattr(nx,graph_type)()


def edge_subgraph(G,edges):
    return G.edge_subgraph(edges)


def nodes(G):
    return np.array(list(G.nodes()))

def random_edges_from_existing_edges(
    G=None,
    edges = None,
    random_idx = None,
    n_samples = None,
    samples_perc = None,
    seed = None,
    verbose = False,
    **kwargs
    ):
    
    st = time.time()
    
    if edges is None:
        edges = xu.edges(G)
        
    if random_idx is None:
        random_idx = nu.random_idx(
        n_samples=n_samples,
        array_len = len(edges),
        seed = seed,
        samples_perc = samples_perc,
        **kwargs
        )
        
    new_edges = edges[random_idx,:]
    
    if verbose:
        print(f"Total time for random edges from existing edges: {time.time() - st}")
    
    return new_edges

def random_edges_from_existing_nodes(
    G=None,
    n_samples=None,
    samples_perc = None,
    nodes = None,
    edges = None,
    seed = None,
    buffer_multiplier = 4,
    no_self_loops = True,
    unique_edges = True,
    error_if_not_enough_edges = True,
    verbose = False,
    **kwargs
    ):
    """
    Purpose: To generate a random 
    list of edges by sampling the
    nodes
    """
    
    st = time.time()
    
    if nodes is None:
        nodes = xu.nodes(G)
        
    if edges is None:
        edges = G.edges()
    
    if n_samples is None:
        n_samples = np.ceil(len(edges)*samples_perc).astype('int')
    curr_samples = n_samples*buffer_multiplier

    if seed is not None:
        seed_1 = seed
        seed_2 = seed + 1
    else:
        seed_1 = None
        seed_2 = None
    nodes_idx_1 = nu.random_idx(
        n_samples = curr_samples,
        array_len=len(nodes),
        replace=True,
        seed=seed_1,
    )
    
    nodes_idx_2 = nu.random_idx(
        n_samples = curr_samples,
        array_len=len(nodes),
        replace=True,
        seed=seed_2,
    )
    
    if no_self_loops:
        good_map  = nodes_idx_1 != nodes_idx_2
        nodes_idx_1 = nodes_idx_1[good_map]
        nodes_idx_2 = nodes_idx_2[good_map]
    new_edges = np.vstack([nodes_idx_1,nodes_idx_2]).T
    if unique_edges:
        new_edges = np.unique(new_edges,axis = 0)
        
    if len(new_edges) < n_samples and error_if_not_enough_edges:
        raise Exception("")
        
    return_value = nodes[new_edges][:n_samples]
    
    if verbose:
        print(f"Total time for random edges from existing nodes: {time.time() - st}")
        
    return return_value

def remove_self_loops(G):
    G.remove_edges_from(nx.selfloop_edges(G))
    return G

def configuration_model(
    G=None,
    degree_sequence=None,
    create_using = "Graph",
    self_loops = False,
    seed = None,
    ):
    
    if type(create_using) == str:
        create_using = getattr(nx,create_using)
    
    if degree_sequence is None:
        degree_sequence = degree_sequence(G)
    G_new=nx.configuration_model(degree_sequence,seed = seed,create_using = create_using)
    if not self_loops:
        G_new = remove_self_loops(G_new)
    return G_new

def directed_configuration_model(
    G = None,
    in_degree_sequence = None,
    out_degree_sequence = None,
    create_using = "MultiDiGraph",
    self_loops = False,
    seed = None,
    ):
    
    if type(create_using) == str:
        create_using = getattr(nx,create_using)
        
    if out_degree_sequence is None:
        out_degree_sequence = xu.out_degree_sequence(G)
    if in_degree_sequence is None:
        in_degree_sequence = xu.in_degree_sequence(G)
    
    G_new=nx.directed_configuration_model(
        in_degree_sequence=in_degree_sequence,
        out_degree_sequence=out_degree_sequence,
        seed = seed,
        create_using = create_using
    )
    if not self_loops:
        G_new = remove_self_loops(G_new)
    return G_new

def random_edges_subgraph(
    G=None,
    nodes = None,
    edges = None,
    edges_func = None,
    random_idx = None,
    n_samples = None,
    samples_perc = None,
    seed = None,
    verbose = False,
    verbose_edge_generation = False,
    in_degree_sequence = None,
    out_degree_sequence = None,
    graph_type = "DiGraph",
    **kwargs
    ):
    st = time.time()
    
    if edges_func == "degree_config_model":
        G_new = directed_configuration_model(
            G=G,
            in_degree_sequence = in_degree_sequence,
            out_degree_sequence = out_degree_sequence,
            self_loops = False,
            create_using = graph_type,
            seed = seed,
        )
    else:
        if edges_func is None:
            edges_func = random_edges_from_existing_edges
        elif edges_func == "edges":
            edges_func = random_edges_from_existing_edges
        elif edges_func == "nodes":
            edges_func = random_edges_from_existing_nodes


        new_edges = edges_func(
            G = G,
            nodes = nodes,
            edges = edges,
            random_idx = random_idx,
            n_samples = n_samples,
            samples_perc = samples_perc,
            seed = seed,
            verbose = verbose_edge_generation,
            **kwargs
        )
        
        G_new = empty_graph_from_type(graph_type)
        G_new.add_edges_from(new_edges)

        # if edges_func == random_edges_from_existing_edges:
        #     new_edges = set([tuple(k) for k in new_edges])
        #     G_new = xu.edge_subgraph(G,new_edges)
        # else:
        #     G_new = empty_graph_from_type(graph_type)
        #     #G_new = empty_graph_type_from_G(G)
        #     G_new.add_edges_from(new_edges)
            
    if verbose:
        print(f"Total time for random subgraph: {time.time() - st}")
        xu.print_node_edges_counts(G_new)
        
    return G_new

def degree_sequence(G):
    return np.array([d for n, d in G.degree()])
    
def out_degree_sequence(G):
    return np.array([d for n, d in G.out_degree()])
    
def in_degree_sequence(G):
    return np.array([d for n, d in G.in_degree()])
    
def degree_sequence_from_adj(array):
    return np.sum(array,axis=1)

def out_degree_sequence_from_adj(array):
    return np.sum(array,axis=1)

def in_degree_sequence_from_adj(array):
    return np.sum(array,axis=0)

def all_pairs_shortest_path_matrix(
    G,
    nodes=None,
    self_path_value = None,
    dist_func = None,
    dist_func_weight = "weight",
    undirected = True,
    verbose = False,
    suppress_errors = False,
    ):
    """
    Purpose: to find the shortest path between all combinations of nodes

    """
    if verbose:
        st = time.time()
    if nodes is None:
        nodes = xu.nodes(G)
        
    if self_path_value is None:
        self_path_value = []
    shortest_path_matrix = nu.empty_n_by_m_default_matrix(n = len(nodes))
    
    
    for i,n1 in enumerate(nodes):
        for j,n2 in enumerate(nodes):
            if i == j:
                shortest_path_matrix[i,j] = self_path_value
                if dist_func is not None:
                    shortest_path_matrix[i,j] = dist_func(G,shortest_path_matrix[i,j],weight = dist_func_weight)
            elif i>=j and undirected:
                shortest_path_matrix[i,j] = shortest_path_matrix[j,i]
            else:
                try:
                    shortest_path_matrix[i,j] = xu.shortest_path(G,n1,n2)
                except:
                    if suppress_errors:
                        shortest_path_matrix[i,j] = self_path_value
                    else:
                        raise Exception("")

                if dist_func is not None:
                    shortest_path_matrix[i,j] = dist_func(G,shortest_path_matrix[i,j],weight = dist_func_weight)

    if verbose:
        print(f"Total time for all_pairs_shortest_path_matrix= {time.time() - st}")
        
    return shortest_path_matrix

#from networkx.classes.function import path_weight as pw

def path_weight(
    G,
    path,
    weight = "weight",
    empty_path_value=0):
    if len(path) == 0:
        return empty_path_value
    return pw(G,path,weight = weight)
path_length_from_path = path_weight

def all_pairs_shortest_path_length_matrix(
    G,
    dist_func = None,
    nodes=None,
    self_path_value = np.inf,
    undirected = True,
    verbose = False,
    weight = "weight",
    suppress_errors = True,
    ):
    
    if dist_func is None:
        dist_func = path_weight
        
    path_matrix = all_pairs_shortest_path_matrix(
        G,
        nodes=nodes,
        self_path_value = None,
        dist_func = dist_func,
        dist_func_weight = weight,
        undirected = undirected,
        verbose = verbose,
        suppress_errors=suppress_errors,
        )
    
    path_matrix[path_matrix == 0] = self_path_value
    return path_matrix
    
    
def largest_component_subgraph(
    G,
    verbose = False):
    """
    Purpose: Find the percentage of neurons not in the
    largest component

    Pseudocode: 
    1) compute the connected components
    2) Find the largest idx
    3) Divide the sum of all those not the largest idx by the
    largest idx
    """
    conn_comps = xu.connected_components(G)
    conn_comps_len = np.array([len(k) for k in conn_comps])
    giant_component_idx = np.argmax(conn_comps_len)
    if verbose:
        print(f"giant_component_size = {conn_comps_len[giant_component_idx]}")
        
    return G.subgraph(conn_comps[giant_component_idx]).copy()

def largest_component_n_nodes(G,verbose=False):
    return n_nodes(largest_component_subgraph(G,verbose = verbose))

def largest_component_node_perc(G):
    return largest_component_n_nodes(G)/n_nodes(G)

def nodes_with_no_edges(G):
    return list(nx.isolates(G))

def remove_nodes_with_no_edges(G,copy = False):
    nodes = nodes_with_no_edges(G)
    if copy:
        G = G.copy()
    G.remove_nodes_from(nodes)
    return G



#--- from datasci_tools ---
from . import general_utils as gu
from . import numpy_utils as nu
from . import pandas_utils as pu
from . import regex_utils as ru
from . import string_utils as stru
from . import tqdm_utils as tqu
from .tqdm_utils import tqdm

from . import networkx_utils as xu