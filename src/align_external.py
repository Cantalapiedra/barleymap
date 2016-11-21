#!/usr/bin/env python
# -*- coding: utf-8 -*-

# align_external.py is part of Barleymap.
# Copyright (C)  2013-2014  Carlos P Cantalapiedra.
# (terms of use can be found within the distributed LICENSE file).

###########################
## Script to align fasta to external references,
## which may NOT be configured as barleymap databases,
## and get a list of targets
###########################

import sys, os
from optparse import OptionParser

from barleymapcore.alignment.AlignmentFacade import AlignmentFacade
from barleymapcore.utils.data_utils import read_paths, load_data
from barleymapcore.alignment.Aligners import SELECTION_BEST_SCORE, SELECTION_NONE

DEFAULT_THRES_ID = 98.0
DEFAULT_THRES_COV = 95.0

def _print_parameters(fasta_path, db_name, query_type, \
                      threshold_id, threshold_cov, best_score, \
                      n_threads, hierarchical, align_info):
    sys.stderr.write("\nParameters:\n")
    sys.stderr.write("\tQuery fasta: "+fasta_path+"\n")
    sys.stderr.write("\tDB name: "+db_name+"\n")
    sys.stderr.write("\tQuery type: "+query_type+"\n")
    sys.stderr.write("\tThresholds --> %id="+str(threshold_id)+" : %query_cov="+str(threshold_cov)+"\n")
    sys.stderr.write("\tN threads: "+str(n_threads)+"\n")
    sys.stderr.write("\tBest score filtering: "+str(best_score)+"\n")
    sys.stderr.write("\tHierarchical filtering: "+str(hierarchical)+"\n")
    sys.stderr.write("\tShow full alignment info: "+str(align_info)+"\n")
    return
    
def _print_paths(split_blast_path, blastn_app_path, gmap_app_path, gmapl_app_path, blastn_dbs_path, gmap_dbs_path):
    sys.stderr.write("\nBlastn:\n")
    sys.stderr.write("\tapp path: "+blastn_app_path+"\n")
    sys.stderr.write("\tdbs path: "+blastn_dbs_path+"\n")
    sys.stderr.write("\tsplit_blast: "+split_blast_path+"\n")
    sys.stderr.write("GMAP:\n")
    sys.stderr.write("\tapp path: "+gmap_app_path+"\n")
    sys.stderr.write("\tgmapl app path: "+gmapl_app_path+"\n")
    sys.stderr.write("\tdbs path: "+gmap_dbs_path+"\n")
    return

## Argument parsing
__usage = "usage: align_external.py [OPTIONS] [FASTA_FILE]\n\ntypical: align_external.py --hierarchical=yes "+\
          "--databases=seq_DB queries.fasta"

optParser = OptionParser(__usage)

optParser.add_option('--databases', action='store', dest='databases_param', type='string', \
                     help='Comma delimited list of databases to align to (mandatory).')

optParser.add_option('--query-mode', action='store', dest='query_mode', type='string', \
                     help='Alignment software to use (default auto). '+\
                     'The "auto" option means first Blastn then GMAP. The "cdna" option means to use only GMAP. '+\
                     'The "genomic" option means to use only Blastn. The order and aligners can be explicitly '+\
                     'specified by separating the names by "," (e.g.: cdna,genomic --> First GMAP, then Blastn).')

optParser.add_option('--thres-id', action='store', dest='thres_id', type='string', \
                     help='Minimum identity for valid alignments. Float between 0-100 (default '+str(DEFAULT_THRES_ID)+').')

optParser.add_option('--thres-cov', action='store', dest='thres_cov', type='string', \
                     help='Minimum coverage for valid alignments. Float between 0-100 (default '+str(DEFAULT_THRES_COV)+').')

optParser.add_option('--threads', action='store', dest='n_threads', type='string', \
                     help='Number of threads to perform alignments (default 1).')

optParser.add_option('--best-score', action='store', dest='best_score', type='string', \
                     help='Whether return secondary hits (no), best score hits for each database (db) '+\
                     'or overall best score hits (default yes).')

optParser.add_option('--hierarchical', action='store', dest='hierarchical', type='string', \
                     help='Whether use datasets recursively (yes) or independently (default no).')

optParser.add_option('--align-info', action='store', dest='align_info', type='string', \
                     help='Whether obtain query-target info (default no) or append alignment info (yes).')

(options, arguments) = optParser.parse_args()

if not arguments or len(arguments)==0:
    optParser.exit(0, "You may wish to run '-help' option.\n")

query_fasta_path = arguments[0] # THIS IS MANDATORY

sys.stderr.write("Command: "+" ".join(sys.argv)+"\n")

########## ARGUMENT DEFAULTS
## Read conf file
app_abs_path = os.path.dirname(os.path.abspath(__file__))

config_path_dict = read_paths(app_abs_path+"/paths.conf") # data_utils.read_paths
__app_path = config_path_dict["app_path"]

split_blast_path = __app_path+config_path_dict["split_blast_path"]
tmp_files_path = __app_path+config_path_dict["tmp_files_path"]
blastn_app_path = config_path_dict["blastn_app_path"]
gmap_app_path = config_path_dict["gmap_app_path"]
gmapl_app_path = config_path_dict["gmapl_app_path"]
blastn_dbs_path = config_path_dict["blastn_dbs_path"]
gmap_dbs_path = config_path_dict["gmap_dbs_path"]

_print_paths(split_blast_path, blastn_app_path, gmap_app_path, gmapl_app_path, blastn_dbs_path, gmap_dbs_path)
sys.stderr.write("\n")

# Databases
if options.databases_param:
    databases_names = options.databases_param
    databases_ids = options.databases_param.split(",")
else:
    sys.stderr.write("No databases specified.\n")
    sys.exit(0)

# Query mode
if options.query_mode:
    query_mode = options.query_mode
else:
    query_mode = "auto"
    
# Threshold Identity
if options.thres_id:
    threshold_id = float(options.thres_id)
else:
    threshold_id = DEFAULT_THRES_ID

# Threshold coverage
if options.thres_cov:
    threshold_cov = float(options.thres_cov)
else:
    threshold_cov = DEFAULT_THRES_COV

# Num threads
if options.n_threads:
    n_threads = int(options.n_threads)
else:
    n_threads = 1

## Selection: show secondary alignments
if options.best_score and options.best_score == "no":
    selection = SELECTION_NONE
    best_score_filter = False
else:
    if options.best_score == "db":
        selection = SELECTION_BEST_SCORE
        best_score_filter = False
    else: # options.best_score == "yes":
        selection = SELECTION_NONE # or SELECTION_BEST_SCORE, the reuslts should be the same
        best_score_filter = True
# selection is applied on alignment results to each database separately
# best_score_filter is applied on all the results from all the databases

# Hierarchical
if options.hierarchical and options.hierarchical == "yes":
    hierarchical = True
    hierarchical_param = "yes"
else:
    hierarchical = False
    hierarchical_param = "no"

# Extra alignment information
if options.align_info and options.align_info == "yes":
    align_info = True
else:
    align_info = False

_print_parameters(query_fasta_path, databases_names, query_mode, \
                  threshold_id, threshold_cov, options.best_score, \
                  n_threads, hierarchical, options.align_info)

########### MAIN
sys.stderr.write("\n")
sys.stderr.write("Start\n")

# Load configuration paths
facade = AlignmentFacade(split_blast_path, blastn_app_path, gmap_app_path, \
                         blastn_dbs_path, gmap_dbs_path, gmapl_app_path, tmp_files_path,
                        references_conf_path = "", verbose = False)
# Perform alignments
results = facade.perform_alignment(query_fasta_path, databases_ids, hierarchical, query_mode, \
                                   threshold_id, threshold_cov, n_threads, \
                                   selection, best_score_filter)

########## Output
sys.stderr.write("\n")

for db_entry in databases_ids:
    if db_entry in results and len(results[db_entry]):
        db_results = results[db_entry]
        if len(databases_ids)>1 and not hierarchical: sys.stdout.write(">DB:"+str(db_entry)+"\n")
        
        if align_info:
            sys.stdout.write("#"+"\t".join(["query_id", "subject_id", "identity", "query_coverage", \
                                            "score", "strand", "start_position",
                                            "end_position", "database", "algorithm"])+"\n")
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
