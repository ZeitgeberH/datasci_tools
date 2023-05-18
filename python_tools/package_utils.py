from . import file_utils as filu
from . import numpy_utils as nu
from . import pathlib_utils as plu
import io
from python_tools import pathlib_utils as plu
from pathlib import Path
#from python_tools import numpy_utils as nu
#from python_tools import file_utils as filu
#import io

"""
Notes: global variables can be referenced in functions
but can't be assigned to (if they are then its just a local copy)
without the use of the global keyword

Module importing itself: essentially will run through things twice
explanation: https://stackoverflow.com/questions/62665924/python-program-importing-itself

--> could technically put at the top

"""
user_packages = (
        "/python_tools/python_tools/",
        "/machine_learning_tools/machine_learning_tools/",
        "/pytorch_tools/pytorch_tools/",
        "/graph_tools/graph_tools/",
        "/meshAfterParty/meshAfterParty/",
        "/neuron_morphology_tools/neuron_morphology_tools/",
)

def module_names_from_directories(
    directories,
    ignore_files = ("__init__",),
    return_regex_or = False,
    verbose = False):
    """
    Purpose: come up with an or string for module names from a module directory
    """
    directories = nu.to_list(directories)
    modules = []

    for directory in directories:

        if verbose:
            print(f"--Getting files from {directory}")

        modules += plu.files_of_ext_type(
            directory = directory,
            ext = "py",
            verbose = verbose
        )
        
    modules = [k.stem for k in modules if k.stem not in ignore_files]
    if return_regex_or:
        return f"({'|'.join(modules)}))"
    else:
        return modules
    
def relative_import_from(directory,filepath):
    return "from " + "".join(["."]*(plu.n_levels_parent_above(directory,filepath)+1)) + " "

def prefix_module_imports_in_files(
    filepaths,
    modules_directory = "../python_tools",
    modules = None,
    prefix = "directory",
    auto_detect_relative_prefix = True,
    prevent_double_prefix = True,
    overwrite_file = False,
    output_filepath = None,# "text_revised.txt",
    verbose = False,
    ignore_files = ["__init__"],
    
    ):
    """
    want to add a prefixes before
    modules that are imported in a file

    Pseudocode: 
    1) if given a directory: get a list of the module names
    2) Construct a regex pattern ORing the potential list
    3) add the prefix before
    4) write to a new file or old file

    """
    if modules_directory is None:
        modules_directory = [None]
    
    modules_directory = nu.to_list(modules_directory)
    filepaths = nu.to_list(filepaths)
    
    for f in filepaths:
        if verbose:
            print(f"--- Working on file: {f}")
            
        for directory in modules_directory:
        # --- iterate through all package directories and do the replacement

            #1) if given a directory: get a list of the module names
            if directory is not None:
                if verbose:
                    print(f"--Getting files from {directory}")

                modules = plu.files_of_ext_type(
                    directory = directory,
                    ext = "py",
                    verbose = verbose
                )

                if auto_detect_relative_prefix and plu.inside_directory(directory,f):
                    curr_prefix = relative_import_from(directory,f)
                elif prefix == "directory":
                    curr_prefix = f"from {Path(directory).stem} "
                else:
                    curr_prefix = prefix
            else:
                modules = [Path(k) for k in nu.to_list(modules)]
                curr_prefix = prefix

            modules = [k.stem for k in modules if k.stem not in ignore_files]

            #2) Construct a regex pattern ORing the potential list
            pattern = f"(import ({'|'.join(modules)}))"

            replacement = fr"{curr_prefix}import \2"
            if prevent_double_prefix:
                pattern = f"(?<!{curr_prefix}){pattern}"
            else:
                replacement = None

            #print(f"pattern = {pattern}")
            #print(f"replacement = {replacement}")

            #4) write to a new file or old file            
            output_filepath = filu.file_regex_add_prefix(
                pattern=pattern,
                prefix=prefix,
                filepath=f,
                replacement=replacement,
                overwrite_file = overwrite_file,
                output_filepath = output_filepath,# "text_revised.txt",
                verbose = verbose,
                regex = True,
            )
            
            f = output_filepath

            
from python_tools import pathlib_utils as plu
def package_name_from_path(path):
    return path.split("/")[1]
def package_from_filepath_and_package_list(
    filepath,
    packages,
    return_package_name = False,
    ):
    """
    packages = (
            "/python_tools/python_tools/",
            "/machine_learning_tools/machine_learning_tools/",
            "/pytorch_tools/pytorch_tools/",
            "/graph_tools/graph_tools/",
            "/meshAfterParty/meshAfterParty/",
            "/neuron_morphology_tools/neuron_morphology_tools/",
    )
    pku.package_from_filepath_and_package_list(
        filepath = "../python_tools/networkx_utils.py",
        packages=packages
    )
    
    """
    for p in packages:
        if plu.inside_directory(p,filepath):
            if return_package_name:
                return package_name_from_path(p)
            return p
    return None

def create_init(
    directory,
    init_filename = "__init__.py",
    exist_ok = True):
    """
    Purpose: To create an init file in a directory
    if one doesn't already exist
    """
    filepath = Path(directory) / Path(init_filename)
    filepath.touch(exist_ok= exist_ok)
    return filepath

from pathlib import Path
from python_tools import numpy_utils as nu
from python_tools import module_utils as modu
def clean_package_syntax(
    directory,
    overwrite=False,
    create_init_if_not_exist = True,
    verbose = False,
    ):
    """
    Purpose: To clean all modules in all
    of the given directories
    """

    directory = nu.to_list(directory)

    for curr_directory in directory:
        if verbose:
            print(f"---- working on directory: {curr_directory} ---")
        modules = modu.modules_from_directory(curr_directory)

        for mod in modules:
            filepath = Path(curr_directory) / (f"{mod}.py")
            if verbose:
                print(f"   --- working on module: {mod} ---")

            modu.clean_module_syntax(
                filepath = filepath,
                verbose = True,
                overwrite=overwrite
            )    
            
        if create_init_if_not_exist:
            pku.create_init(
                directory = curr_directory
            )

#from python_tools import package_utils as pku

from . import package_utils as pku