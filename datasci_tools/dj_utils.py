'''



Purpose: Datajoint utils to help with table manipulation



'''
try:
    import datajoint as dj
except ImportError as e:
    raise e("Datajoint must be installed ...")
    
from . import numpy_dep as np
import pandas as pd
import time
#import datajoint as dj
#from datasci_tools import numpy_utils as nu
#from . import numpy_dep as np
#import pandas as pd
#from datasci_tools import pandas_utils as pu

def df_from_table_old(
    table,
    features=None,
    remove_method_features = False,):
    
    if remove_method_features:
        if features is None:
            features = [k for k in all_attribute_names_from_table(table)
                    if 'method' not  in k]
        else:
            features = [k for k in features if "method" not in k]
    
    if features is not None:
        features = nu.convert_to_array_like(features,include_tuple = True)
        #table = table.proj(*features)
        #table = dj.U(*features) & table
        if len(features) == 1:
            curr_data = np.array(table.fetch(*features)).reshape(-1,len(features))
        else:
            curr_data = np.array(table.fetch(*features)).T
        return_df = pd.DataFrame(curr_data)
        return_df.columns = features
    else:
        return_df = pd.DataFrame(table.fetch())
        
    #return_df = pd.DataFrame.from_records(table.fetch())
#     if features is not None:
#         if isinstance(features,tuple):
#             features = list(features)
#         return_df = return_df[features]
    return return_df

#import time
def df_from_table(
    table,
    features=None,
    remove_method_features = False,
    features_to_remove = None,
    features_substr_to_remove = None,
    primary_features = False,
    verbose = False):
    
    st = time.time()
    
    all_atts = list(all_attribute_names_from_table(table))
    
    if features is None:
        features = all_atts
    
    features = nu.convert_to_array_like(features,include_tuple = True)
    
    if primary_features:
        primary_features = list(primary_attribute_names_from_table(table))
        features =primary_features + [k for k in features if k not in primary_features]
    
    if features_to_remove is None:
        features_to_remove = []
        
    if remove_method_features:
        features_to_remove += [k for k in all_atts if "method" in k]
        
    if features_substr_to_remove is not None:
        for att in all_atts:
            remove_flag = False
            for sub in features_substr_to_remove:
                if sub in att:
                    remove_flag = True
                    break
            if remove_flag:
                features_to_remove.append(att)
            
    features = [k for k in features if k not in features_to_remove]
    
    if len(features) == 1:
        curr_data = np.array(table.fetch(*features)).reshape(-1,len(features))
    else:
        curr_data = np.array(table.fetch(*features)).T
    return_df = pd.DataFrame(curr_data)
    return_df.columns = features
    
    if verbose:
        print(f"Time for fetch = {time.time() - st}")
    
    return return_df

def all_attribute_names_from_table(table):
    return [str(k) for k in table.heading.names]

def primary_attribute_names_from_table(table):
    return [str(k) for k in table.heading.primary_key]

def secondary_attribute_names_from_table(table):
    return [str(k) for k in table.heading.secondary_attributes]

def append_table_to_pairwise_table(
    table,
    table_to_append,
    primary_attributes = None,
    secondary_attributes = None,
    attributes_to_not_rename = None,
    source_name = "",
    target_name = "match",
    append_type = "prefix",
    verbose = False,
    ):
    """
    Purpose: To add on a table to both 
    sides of another

    Pseudocode: 
    1) Determine the primary attributes to join on
    (if not already)
    2) Determine the secondary attributes you want to 
    join
    3) Build a renaming dictionary
    4) Project the tale to only those attributes chosen
    5) star restrict the table with the renamed tables
    
    --- Example: ----
    dju.append_table_to_pairwise_table(
        table = m65auto.AutoProofreadNeuronLeafMatch(),
        table_to_append = hdju.subgraph_vectors_table,
        primary_attributes = [
            "segment_id",
            "split_index",
            "subgraph_idx",
            #"leaf_node",
        ],
        secondary_attributes = [
         'compartment',
         'node',
         'y_soma_relative',
         'width',
        ],
        source_name = "",
        target_name = "match",
        append_type = "prefix",
        verbose = True,
    )
    """
    if attributes_to_not_rename is None:
        attributes_to_not_rename = []

    if primary_attributes is None:
        primary_attributes = primary_attribute_names_from_table(table_to_append)

    if secondary_attributes is None:
        secondary_attributes = secondary_attribute_names_from_table(table_to_append)

    all_attributes = list(primary_attributes) + list(secondary_attributes)

#     if source_name is not None and len(source_name) > 0:
#         source_name = f"{source_name}_"

#     if target_name is not None and len(target_name) > 0:
#         target_name = f"{target_name}_"

    proj_table = table_to_append.proj(*all_attributes)
    final_table = table

    
    for name,k in zip(["source","target"],[source_name,target_name]):
        rename_dict = {}
        name_str = None
        if k is not None and len(k) > 0:
            if append_type == "prefix":
                name_str = 'f"{kk}_{v}"'
            elif append_type == "suffix":
                name_str = 'f"{v}_{kk}"'
            elif append_type is None:
                name_str = 'f"{kk}"'
        
        
        if name_str is None:
            name_str = 'f"{v}"'
            #raise Exception("")
            
        
        #print(f"name_str = {name_str}")
        rename_dict.update(dict([(eval(name_str),v) if v not in attributes_to_not_rename
                                 else (v,v) for kk,v in zip([k]*len(all_attributes),all_attributes)]))

        if verbose:
            print(f"rename_dict for {name} = {rename_dict}")

        final_table = final_table * proj_table.proj(**rename_dict) 

    return final_table


parameter_datatype_lists = [
    "int unsigned",
    "float",
    "double",
    "tinyint unsigned"
]
def parameter_datatype(
    parameter,
    int_default = "int",
    default_type = None,
    blob_type = "longblob"):
    
    if default_type in parameter_datatype_lists:
        return default_type
    
    curr_type_str = str(type(parameter))
    if default_type is not None:
        curr_type_str = str(default_type)
    
    if "int" in curr_type_str:
        try:
            if parameter >= 0:
                return f"{int_default} unsigned"
            else:
                return f"{int_default}"
        except:
            return f"{int_default}"
    elif "str" in curr_type_str:
        return f"varchar({len(parameter)+ 10})"
    elif ("float" in curr_type_str) or ("double" in curr_type_str):
        return "float"
    elif "bool" in curr_type_str:
        return "tinyint unsigned"
    elif "tuple" or "blob" in curr_type_str:
        return blob_type
    else:
        raise Exception(f"Unknown type: {type(parameter)}")
        
#from datasci_tools import data_struct_utils as dsu
def parameter_datatype_description(kwargs_dict,
                                  kwargs_datatype_dict = None,
                                   add_null = True,
                                  verbose = False,):
    """
    To generate the the datatype part of a parameter 
    table definition
    
    --- Exmaple--
    new_str = parameter_datatype_description(kwargs_dict,
                                         kwargs_datatype_dict = dict(filter_by_volume_threshold="new datatype")
                                        )
    print(new_str)
                                        
    """
    if kwargs_datatype_dict is None:
        kwargs_datatype_dict = {}
    total_str = []
    for k,v in kwargs_dict.items():
        if k in kwargs_datatype_dict:
            datatype_str = kwargs_datatype_dict[k]
        else:
            if isinstance(kwargs_dict,dsu.DictType):
                default_type = kwargs_dict._types.get(k,None)
            else:
                default_type = None
            datatype_str = parameter_datatype(v,default_type=default_type)
        
        if add_null:
            curr_str= f"{k}=NULL: {datatype_str}"
        else:
            curr_str= f"{k}: {datatype_str}"
            
        if verbose:
            print(curr_str)
        total_str.append(curr_str)
        
    return "\n".join(total_str)

def table_definition_from_example_dict(
    kwargs_dict,
    kwargs_datatype_dict = None,
    definition_description = None,
    add_name_description_to_parameters = False,
    verbose = False
    ):
    
    total_str = []
    if definition_description is not None:
        if definition_description[0] != "#":
            total_str.append(f"# {definition_description}")
        else:
            total_str.append(definition_description)
            
    total_str.append("->master\n---")
    param_str = parameter_datatype_description(kwargs_dict,
                                              kwargs_datatype_dict = kwargs_datatype_dict,
                                              verbose = False)
    total_str.append(param_str)
    
    if add_name_description_to_parameters:
        if "name" not in kwargs_dict:
            total_str.append("name=NULL: varchar(24)")
        if "description" not in kwargs_dict:
            total_str.append("description=NULL: varchar(120)")
        
    total_str_comb = "\n".join(total_str)
    
    if verbose:
        print(total_str_comb)
        
    return total_str_comb

def dj_query_from_pandas_query(query):
    query = query.replace("==","=")
    for joiner in [" and "," or "," not "]:
        query = query.replace(joiner,joiner.upper())
    return query

def query_table_from_kwargs(
    table,
    **kwargs):
    """
    Purpose: To query a datajoint table
    with keywords that may be None
    """
    key = dict()
    key = {k:v for k,v in kwargs.items() if v is not None}
    if len(key) == 0:
        return table
    else:
        return table & key
    
def formatted_table_name(
    table_name,
    verbose = False):
    return_name = str(table_name)
    root_replacements = {
        'microns_h01_auto_proofreading':"h01auto",
        'microns_h01_morphology':"h01mor",
        'microns_h01_materialization':"h01mat",
    }
    replacements = {
        '`.`__':".",
        '`':"",
        "__":"_",
        "#":"",
    }
    replacements.update({k:"" for k in root_replacements})
    
    root = None
    #print(f"table_name = {table_name}")
    for k,v in root_replacements.items():
        if k in table_name:
            root = v
            #print(f"root = {root}")
            break
    
    for o,n in replacements.items():
        return_name = return_name.replace(o,n)
    return_name = "".join([k.title() for k in return_name.split("_")])
    
    if root is not None:
        return_name = root + return_name
    
    if verbose:
        print(f"Before {table_name}, After: {return_name}")
    return return_name

    
def dependencies_from_definition(
    definition,
    ignore_list = ("master",),
    ignore_proj = True,
    format_names = True
    ):
    """
    Purpose: To extract from a defintion string
    all dependencies that aren't the master

    Pseudocode: 
    1) Split the string by "---"
    For each line in the string
        a. eliminate all white space
        b. split by -> 
        c. If the following is not master, add to the list
    """
    if ignore_list is None:
        ignore_list = []
        
    def dependency_on_line(line):
        line = line.replace(" ","")
        deps = line.split("->")
        if len(deps) <= 1:
            return None
        elif len(deps) > 2:
            raise Exception("Unexpcted multiple ->")
        else:
            return deps[1]

    if not hasattr(definition,"split"):
        if hasattr(definition,"definition") and hasattr(definition.definition,"split"):
            definition = definition.definition
        elif hasattr(definition,"describe"):
            with su.suppress_stdout_stderr():
                definition = definition.describe()
        else:
            return None
        
    primary = definition.split("---")[0]
    lines = primary.split("\n")
    dependencies = []
    for i,d in enumerate(lines):
        dep = dependency_on_line(d)
        if dep not in ignore_list and dep is not None:
            if ignore_proj:
                idx = dep.find(f".proj(")
                if idx != -1:
                    dep = dep[:idx]
            dependencies.append(dep)
    # want to clean dependencies
    if format_names:
        dependencies = map(formatted_table_name,dependencies)
    return dependencies

def dj_table_check(
    obj,
    schema=None,
    table_strs = ("datajoint.","table"),
    table_name_exclude_str = ("master","key_source","_log"),
    ):
    for s in table_name_exclude_str:
        if s in obj:
            return False
    if schema is not None:
        try:
            obj = getattr(schema,obj)
        except:
            return False
    
    curr_str = str(type(obj))
    for s in table_strs:
        if s not in curr_str:
            return False
        
    return True

def table_attributes(obj):
    return [k for k in dir(obj) if dj_table_check(k,obj)]

import networkx as nx

def dependency_dag(
    root,
    root_name="root",
    verbose = False,
    schema_always_starts = True,
    return_graph = True,
    add_dep_to_member_dep = True,
    verbose_member = False,
    ):
    """
    Purpose: Get a topological sorting of all the tables in 
    a schema

    Brainstorming:
    1) start with the schema as the parent object, make parent name
    2) get the top most table and name from the queue
    3) For each table attribute in current table:
        d. Analyze the definition for dependencies
        e. If a dependency is master, use the current parent object name as the master
        f. Add the dependency as an edge in the graph
        g. Add the table to the queue of tables to check (as long as not already checked before) (along with its namez)
    4) continue until no new tables to check
    """
    debug = False
    schema_name = root_name.split(".")[0]

    if root is None:
        root = eval(root_name)

    total_objs = {}
    obj_to_check = {root_name,}
    edges = []

    root_search_str = f"{root_name}."

    while obj_to_check:
        p = obj_to_check.pop()
        if debug:
            print(
                f"p = {p}",f"root = {root}"
            )
        if root_name is not None and root_search_str in p:
            obj = eval(f'root.{p.replace(root_search_str,"")}')
            
        elif root_name == p:
            obj = root
        else:
            obj = eval(p)
            
        if debug:
            print(
                f"obj AFTER = {obj}"
            )
            
        
        if debug:
            print(f"-----{obj}----")
            try:
                print(f"-----{formatted_table_name(obj)}----")
            except:
                pass
            
        dependencies = dependencies_from_definition(
            definition=obj,
            ignore_list = None,
        )
        
        if debug:
            print(f"  -> dependencies: {dependencies}")

        parent = ".".join(p.split(".")[:-1])

        if dependencies is None:
            dependencies = []


        table_edges = [(k.replace('master',parent),p) for k in dependencies]
        if schema_always_starts:
            table_edges = [(f"{schema_name}.{k}",v) if f"{root_name}." not in k
                          else (k,v) for k,v in table_edges]
        edges += table_edges

        children_names = [f"{p}.{k}" for k in table_attributes(obj)]
    #     for k in children_names:
    #         P[k] = p  
        
        obj_to_check.update(children_names)
        if debug:
            print(f"children_names = {children_names}") 
            print(f"obj_to_check = {obj_to_check}")

        if verbose:
            print(f"Processing table {p}:")
            print(f"\tdependency edges:")
            for e in table_edges:
                print(f"\t\t{e}")
            print(f"\tchildren tables")
            for c in children_names:
                print(f"\t\t{c}")
        
    if add_dep_to_member_dep:
        #print(f"in add_dep_to_member_dep")
        upstream = [k for k,v in edges]
        downstream = [v for k,v in edges]
        names = set(upstream).union(downstream)
        #print(f"names = {names}")
        for n in names:
            member_name = f"{n}.Member" 
            if member_name in names:
                new_edges = [(k,n) for k,v in edges
                          if v == member_name and k != n]
                if verbose_member:
                    print(f"for {n}, adding: {new_edges}")
                edges += new_edges
        
    if return_graph:
        dag = nx.DiGraph()
        dag.add_edges_from(edges)
        return dag
    else:
        return edges
    
def ensure_parent_name_before_child(
    string_list,
    verbose = False
    ):
    """
    Purpose: To move a string up on a list
    so that no strings that fully contain that string are before it
    
    Pseudocode: 
    As long as end is not 0
    1) Get the string of "last" pointer
    2) Find the indexes of all proceeding string that contain the string and are longer
    3a) If the list is non-empty, insert the string before the first index in list
    3b) if the list is empty, increment the last pointer
    
    Ex: 
    test_list = [
        "bogus",
        "hellothere",
        "hihello",
        "hello",
        "hi",
    ]

    ensure_parent_name_before_child(
        test_list,
        verbose = True)
    """
    last = len(string_list) - 1
    while last > 0:
        if verbose:
            print(f"current list = {string_list}")
            print(f"  On idx {last}")
        curr_str = string_list[last]
        child_str = [i for i,k in enumerate(string_list[:last])
                    if curr_str in k and len(k) > len(curr_str)]
        if len(child_str)>0:
            new_idx = child_str[0]
            new_list = string_list[:new_idx] + [curr_str] + string_list[new_idx:last]
            if last != len(string_list):
                new_list += string_list[last+1:]
            string_list = new_list
            if verbose:
                print(f"found child idx = {new_idx}")
                print(f"  new list = {new_list}")
        else:
            last -= 1
            if verbose:
                print(f"Didn't find child idx")
            
    return string_list

def topological_sorted_tables(
    root,
    root_name="root",
    verbose = False,
    sort_parent_child_tables = True,
    **kwargs
    ):
    
    dag = dependency_dag(
        root,
        root_name=root_name,
        verbose = verbose,
        **kwargs
        )
    return_list = list(nx.topological_sort(dag))
    
    if sort_parent_child_tables:
        return_list = ensure_parent_name_before_child(return_list)
    return return_list

#--- from datasci_tools ---
from . import data_struct_utils as dsu
from . import numpy_utils as nu
from . import pandas_utils as pu
from . import system_utils as su

restrict_table_from_list = pu.restrict_df_from_list

from . import dj_utils as dju