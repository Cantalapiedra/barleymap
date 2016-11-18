#!/usr/bin/env python
# -*- coding: utf-8 -*-

# retrieve_datasets.py is part of Barleymap.
# Copyright (C)  2013-2014  Carlos P Cantalapiedra.
# (terms of use can be found within the distributed LICENSE file).

##############################
# Script to retrieve data from precomputed
# alignments by using only IDs
#############################

import sys, os
from optparse import OptionParser

from barleymapcore.datasets.DatasetsFacade import DatasetsFacade, SELECTION_NONE, SELECTION_BEST_SCORE
from barleymapcore.utils.data_utils import read_paths, load_data

def _print_parameters(query_ids_path, dataset_name, db_name, best_score, hierarchical, align_info):
    sys.stderr.write("\nParameters:\n")
    sys.stderr.write("\tQuery file: "+query_ids_path+"\n")
    sys.stderr.write("\tDatasets list: "+dataset_name+"\n")
    sys.stderr.write("\tDBs list: "+db_name+"\n")
    sys.stderr.write("\tBest score filtering: "+str(best_score)+"\n")
    sys.stderr.write("\tHierarchical filtering: "+str(hierarchical)+"\n")
    sys.stderr.write("\tShow full alignment info: "+str(align_info)+"\n")
    return
    
def _print_paths(datasets_path):
    sys.stderr.write("\nDatasets path: "+datasets_path+"\n")
    return

## Argument parsing
__usage = "usage: retrieve_datasets.py [OPTIONS] [IDs_FILE]"
optParser = OptionParser(__usage)

optParser.add_option('--datasets', action='store', dest='datasets_param', type='string', help='Comma delimited list of datasets to retrieve.')
optParser.add_option('--databases', action='store', dest='databases_param', type='string', help='Comma delimited list of databases source of the alignments.')

optParser.add_option('--best-score', action='store', dest='best_score', type='string', \
                     help='Whether return secondary hits (no), best score hits for each database (db) or overall best score hits (yes; default).')

optParser.add_option('--hierarchical', action='store', dest='hierarchical', type='string', help='Whether use datasets recursively (yes) or independently (no).')
optParser.add_option('--align-info', action='store', dest='align_info', type='string', help='Whether obtain query-target info (no; default) or append alignment info (yes).')

(options, arguments) = optParser.parse_args()

if not arguments or len(arguments)==0:
    optParser.exit(0, "You may wish to run '-help' option.\n")

query_ids_path = arguments[0] # THIS IS MANDATORY

sys.stderr.write("Command: "+" ".join(sys.argv)+"\n")

########## ARGUMENT DEFAULTS
## Read conf file
app_abs_path = os.path.dirname(os.path.abspath(__file__))

config_path_dict = read_paths(app_abs_path+"/paths.conf") # data_utils.read_paths
__app_path = config_path_dict["app_path"]

datasets_path = __app_path+config_path_dict["datasets_path"]

_print_paths(datasets_path)
sys.stderr.write("\n")

# Datasets
datasets_conf_file = config_path_dict["app_path"]+"conf/datasets.conf"
(datasets_names, datasets_ids) = load_data(datasets_conf_file, users_list = options.datasets_param, verbose = True) # data_utils.load_datasets

# Databases
databases_conf_file = __app_path+"conf/references.conf"
(databases_names, databases_ids) = load_data(databases_conf_file, users_list = options.databases_param, verbose = True) # data_utils.load_databases

## Selection: show secondary alignments
if options.best_score and options.best_score == "yes":
    selection = SELECTION_NONE # or SELECTION_BEST_SCORE, the results should be the same
    best_score_filter = True
else:
    if options.best_score == "db":
        selection = SELECTION_BEST_SCORE
        best_score_filter = False
    else: # options.best_score == "no":
        selection = SELECTION_NONE
        best_score_filter = False
# selection is applied on alignment results to each database separately
# best_score_filter is applied on all the results from all the databases

# Hierarchical
if options.hierarchical and options.hierarchical == "yes":
    hierarchical = True
    hierarchical_param = "yes"
else:
    hierarchical = False
    hierarchical_param = "no"

if options.align_info and options.align_info == "yes":
    align_info = True
else:
    align_info = False

_print_parameters(query_ids_path, datasets_names, databases_names, options.best_score, hierarchical, options.align_info)

############### MAIN
sys.stderr.write("\n")
sys.stderr.write("Start\n")

# Load configuration paths
facade = DatasetsFacade(datasets_conf_file, datasets_path, verbose = False)
# Perform alignments
results = facade.retrieve_ids(query_ids_path, datasets_ids, databases_ids, hierarchical, \
                              selection, best_score_filter)

# Output
sys.stderr.write("\n")

# Output
sys.stderr.write("\n")

for db_entry in databases_ids:
    if db_entry in results and len(results[db_entry]):
        db_results = results[db_entry]
        if len(databases_ids)>1 and not hierarchical: sys.stdout.write(">DB:"+str(db_entry)+"\n")
        
        if align_info:
            sys.stdout.write("#"+"\t".join(["query_id", "subject_id", "identity", "query_coverage", "score", "strand", "local_position", "database", "algorithm"])+"\n")
            for result in db_results:
                sys.stdout.write("\t".join([str(a) for a in result[:2]]))
                sys.stdout.write("\t"+str("%0.2f" % float(result[2]))) # cm
                sys.stdout.write("\t"+str("%0.2f" % float(result[3]))+"\t") # bp
                sys.stdout.write("\t".join([str(a) for a in result[4:]])+"\n")
        else:
            sys.stdout.write("#"+"\t".join(["query_id", "subject_id"])+"\n")
            for result in db_results:
                sys.stdout.write("\t".join([str(a) for a in result[:2]])+"\n")
    else:
        sys.stderr.write("There are no results for DB: "+db_entry+"\n")

sys.stderr.write("Finished.\n")

## END