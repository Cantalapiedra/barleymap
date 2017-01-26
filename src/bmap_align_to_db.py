#!/usr/bin/env python
# -*- coding: utf-8 -*-

# bmap_align_to_db.py is part of Barleymap.
# Copyright (C)  2013-2014  Carlos P Cantalapiedra. (align_fasta.py)
# Copyright (C) 2016 Carlos P Cantalapiedra
# (terms of use can be found within the distributed LICENSE file).

###########################
## Script to align fasta to different references
## and get a list of alignment results. The databases used
## as references must have been previously configured.
###########################

import sys, os
from optparse import OptionParser

from barleymapcore.alignment.AlignmentFacade import AlignmentFacade
from barleymapcore.utils.data_utils import read_paths
from barleymapcore.db.DatabasesConfig import REF_TYPE_BIG, REF_TYPE_STD, DatabasesConfig

DATABASES_CONF = "conf/databases.conf"

DEFAULT_QUERY_MODE = "gmap"
DEFAULT_THRES_ID = 98.0
DEFAULT_THRES_COV = 95.0
DEFAULT_N_THREADS = 1
DEFAULT_BEST_SCORE = True
DEFAULT_BEST_SCORE_PARAM = "yes"
DEFAULT_HIERARCHICAL = False
DEFAULT_HIERARCHICAL_PARAM = "no"
DEFAULT_REF_TYPE = REF_TYPE_STD

def _print_parameters(fasta_path, dbs, query_type, \
                      threshold_id, threshold_cov, best_score, \
                      n_threads, hierarchical, ref_type = None):
    sys.stderr.write("\nParameters:\n")
    sys.stderr.write("\tQuery fasta: "+fasta_path+"\n")
    sys.stderr.write("\tDBs: "+dbs+"\n")
    sys.stderr.write("\tAligner: "+query_type+"\n")
    sys.stderr.write("\tThresholds --> %id="+str(threshold_id)+" : %query_cov="+str(threshold_cov)+"\n")
    sys.stderr.write("\tThreads: "+str(n_threads)+"\n")
    sys.stderr.write("\tBest score filtering: "+str(best_score)+"\n")
    sys.stderr.write("\tHierarchical filtering: "+str(hierarchical)+"\n")
    
    if ref_type:
        sys.stderr.write("\tReference type: "+str(ref_type)+"\n")
    
    return
    
def _print_paths(split_blast_path, blastn_app_path, gmap_app_path, gmapl_app_path, hsblastn_app_path, \
                 blastn_dbs_path, gmap_dbs_path, hsblastn_dbs_path):
    
    sys.stderr.write("\nBlastn:\n")
    sys.stderr.write("\tapp path: "+blastn_app_path+"\n")
    sys.stderr.write("\tdbs path: "+blastn_dbs_path+"\n")
    sys.stderr.write("\tsplit_blast: "+split_blast_path+"\n")
    
    sys.stderr.write("GMAP:\n")
    sys.stderr.write("\tapp path: "+gmap_app_path+"\n")
    sys.stderr.write("\tgmapl app path: "+gmapl_app_path+"\n")
    sys.stderr.write("\tdbs path: "+gmap_dbs_path+"\n")
    
    sys.stderr.write("HS-Blastn:\n")
    sys.stderr.write("\tapp path: "+hsblastn_app_path+"\n")
    sys.stderr.write("\tdbs path:"+hsblastn_dbs_path+"\n")
    
    return

## Argument parsing
__usage = "usage: bmap_align_to_db.py [OPTIONS] [FASTA_FILE]\n\n"+\
          "typical: bmap_align_to_db.py --databases=MorexGenome queries.fasta"

optParser = OptionParser(__usage)

optParser.add_option('--databases', action='store', dest='databases_param', type='string',
                     help='Comma delimited list of database names to align to (default all).')

optParser.add_option('--databases-ids', action='store', dest='databases_ids_param', type='string',
                     help='Comma delimited list of database IDs to align to (default all).')

optParser.add_option('--aligner', action='store', dest='query_mode', type='string',
                     help='Alignment software to use (default "'+DEFAULT_QUERY_MODE+'"). '+\
                     'The "gmap" option means to use only GMAP. '+\
                     'The "blastn" option means to use only Blastn. '+\
                     'The "hsblastn" option means to use only HS-Blastn. '+\
                     'The order and aligners can be explicitly specified by separating the names by ","'+\
                     ' (e.g.: blastn,gmap --> First Blastn, then GMAP).')

optParser.add_option('--thres-id', action='store', dest='thres_id', type='string',
                     help='Minimum identity for valid alignments. '+\
                     'Float between 0-100 (default '+str(DEFAULT_THRES_ID)+').')

optParser.add_option('--thres-cov', action='store', dest='thres_cov', type='string',
                     help='Minimum coverage for valid alignments. '+\
                     'Float between 0-100 (default '+str(DEFAULT_THRES_COV)+').')

optParser.add_option('--threads', action='store', dest='n_threads', type='string',
                     help='Number of threads to perform alignments (default '+str(DEFAULT_N_THREADS)+').')

optParser.add_option('--best-score', action='store', dest='best_score', type='string',
                     help='Whether return secondary hits (no) '+\
                     'or overall best score hits (yes) '+\
                     '(default '+str(DEFAULT_BEST_SCORE_PARAM)+').')

optParser.add_option('--hierarchical', action='store', dest='hierarchical', type='string',
                     help='Whether use datasets recursively (yes) or '+\
                     'independently (yes) '+\
                     '(default '+str(DEFAULT_HIERARCHICAL_PARAM)+').')

optParser.add_option('--ref-type', action='store', dest='ref_type', type='string',
                     help='Whether use GMAP (std) or GMAPL (big), when using --databases-ids only.')

optParser.add_option('-v', '--verbose', action='store_true', dest='verbose', help='More information printed.')

(options, arguments) = optParser.parse_args()

if not arguments or len(arguments)==0:
    optParser.exit(0, "You may wish to run '-help' option.\n")

### INPUT FILE
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
hsblastn_app_path = config_path_dict["hsblastn_app_path"]

blastn_dbs_path = config_path_dict["blastn_dbs_path"]
gmap_dbs_path = config_path_dict["gmap_dbs_path"]
hsblastn_dbs_path = config_path_dict["hsblastn_dbs_path"]

# Query mode
if options.query_mode: query_mode = options.query_mode
else: query_mode = DEFAULT_QUERY_MODE
    
# Threshold Identity
if options.thres_id: threshold_id = float(options.thres_id)
else: threshold_id = DEFAULT_THRES_ID

# Threshold coverage
if options.thres_cov: threshold_cov = float(options.thres_cov)
else: threshold_cov = DEFAULT_THRES_COV
    
# Num threads
if options.n_threads: n_threads = int(options.n_threads)
else: n_threads = DEFAULT_N_THREADS

## Show only alignments from database with best scores
if options.best_score and options.best_score == "no":
    best_score_filter = False
    best_score_param = "no"
elif options.best_score and options.best_score == "yes":
    best_score_filter = True
    best_score_param = "yes"
else:
    best_score_filter = DEFAULT_BEST_SCORE
    best_score_param = DEFAULT_BEST_SCORE_PARAM
    
# Hierarchical
if options.hierarchical and options.hierarchical == "yes":
    hierarchical = True
    hierarchical_param = "yes"
elif options.hierarchical and options.hierarchical == "no":
    hierarchical = False
    hierarchical_param = "no"
else:
    hierarchical = DEFAULT_HIERARCHICAL
    hierarchical_param = DEFAULT_HIERARCHICAL_PARAM
    
# ref_type
if options.ref_type and options.ref_type == REF_TYPE_BIG:
    ref_type_param = REF_TYPE_BIG
else:
    ref_type_param = DEFAULT_REF_TYPE

# Verbosity    
if options.verbose: verbose_param = True
else: verbose_param = False

### Print initial data
###
if verbose_param:
    _print_paths(split_blast_path, blastn_app_path, gmap_app_path, gmapl_app_path, hsblastn_app_path, \
                 blastn_dbs_path, gmap_dbs_path, hsblastn_dbs_path)
    sys.stderr.write("\n")

# Databases
databases_conf_file = __app_path+DATABASES_CONF
databases_config = DatabasesConfig(databases_conf_file, verbose_param)

if options.databases_param: # or "all databases in conf"
    databases_names = options.databases_param
    databases_ids = databases_config.get_databases_ids(databases_names.strip().split(","))
    
elif options.databases_ids_param:
    databases_ids = options.databases_ids_param.strip().split(",")
    databases_names = ",".join(databases_config.get_databases_names(databases_ids))
else:
    databases_ids = databases_config.get_databases().keys()
    databases_names = ",".join(databases_config.get_databases_names(databases_ids))

_print_parameters(query_fasta_path, databases_names, query_mode, \
                  threshold_id, threshold_cov, best_score_param, \
                  n_threads, hierarchical_param, ref_type_param)

########### MAIN
sys.stderr.write("\n")
sys.stderr.write("Start\n")

# Load configuration paths
facade = AlignmentFacade(split_blast_path, blastn_app_path, gmap_app_path, hsblastn_app_path, \
                         blastn_dbs_path, gmap_dbs_path, hsblastn_dbs_path, gmapl_app_path, tmp_files_path,
                        databases_config, verbose = verbose_param)

# Perform alignments
facade.perform_alignment(query_fasta_path, databases_ids, hierarchical, query_mode, \
                                   threshold_id, threshold_cov, n_threads, \
                                   best_score_filter, ref_type_param)

results = facade.get_alignment_results()

########## Output
sys.stderr.write("\n")

num_databases = len(databases_ids)

for db_entry in databases_ids:
    if db_entry in results and len(results[db_entry]):
        
        if (not hierarchical) and num_databases>1: sys.stdout.write(">DB:"+str(db_entry)+"\n")
        
        # header
        sys.stdout.write("#"+"\t".join(["query_id", "subject_id", "identity", "query_coverage", \
                                        "score", "strand", "qstart", "qend", "sstart", "send",
                                        "database", "algorithm"])+"\n")
    
        # records
        db_results = results[db_entry]
        for alignment_result in db_results:
            sys.stdout.write("\t".join([
                alignment_result.get_query_id(),
                alignment_result.get_subject_id(),
                str("%0.2f" % float(alignment_result.get_align_ident())),
                str("%0.2f" % float(alignment_result.get_query_cov())),
                str(alignment_result.get_align_score()),
                alignment_result.get_strand(),
                str(alignment_result.get_qstart_pos()),
                str(alignment_result.get_qend_pos()),
                str(alignment_result.get_local_position()),
                str(alignment_result.get_end_position()),
                str(alignment_result.get_db_name()),
                str(alignment_result.get_algorithm())
            ]))
            sys.stdout.write("\n")
    else:
        sys.stderr.write("There are no results for DB: "+db_entry+"\n")

sys.stderr.write("Finished.\n")

## END