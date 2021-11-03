#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# bmap_align_to_map.py is part of Barleymap.
# Copyright (C) 2016-2017 Carlos P Cantalapiedra
# (terms of use can be found within the distributed LICENSE file).

###########################
## Script to align fasta to the references associated to a map
## (in the config file) and get the resulting alignments.
## The databases used as references must have been previously configured.
###########################

import sys, os, re, traceback
from optparse import OptionParser

from barleymapcore.db.ConfigBase import ConfigBase
from barleymapcore.db.PathsConfig import PathsConfig
from barleymapcore.alignment.AlignmentFacade import AlignmentFacade
from barleymapcore.alignment.AlignmentEngines import ALIGNMENT_TYPE_GREEDY
from barleymapcore.db.DatabasesConfig import DatabasesConfig
from barleymapcore.db.MapsConfig import MapsConfig
from barleymapcore.output.OutputFacade import OutputFacade
from barleymapcore.m2p_exception import m2pException

DATABASES_CONF = ConfigBase.DATABASES_CONF
MAPS_CONF = ConfigBase.MAPS_CONF

DEFAULT_ALIGNER_LIST = ["gmap"]
DEFAULT_THRES_ID = 98.0
DEFAULT_THRES_COV = 95.0
DEFAULT_N_THREADS = 1
DEFAULT_HIERARCHICAL = ALIGNMENT_TYPE_GREEDY

def _print_parameters(fasta_path, maps, aligner_list, \
                      threshold_id, threshold_cov, \
                      n_threads, search_type):
    sys.stderr.write("\nParameters:\n")
    sys.stderr.write("\tQuery fasta: "+fasta_path+"\n")
    sys.stderr.write("\tMaps: "+maps+"\n")
    sys.stderr.write("\tAligner: "+",".join(aligner_list)+"\n")
    sys.stderr.write("\tThresholds --> %id="+str(threshold_id)+" : %query_cov="+str(threshold_cov)+"\n")
    sys.stderr.write("\tThreads: "+str(n_threads)+"\n")
    sys.stderr.write("\tSearch type: "+str(search_type)+"\n")
    
    return

try:
    
    ## Argument parsing
    __usage = "usage: bmap_align_to_map.py [OPTIONS] [FASTA_FILE with 1-word header]\n\n"+\
              "typical: bmap_align_to_map.py --maps=MorexGenome queries.fasta"
    
    optParser = OptionParser(__usage)
    
    optParser.add_option('--maps', action='store', dest='maps_param', type='string', \
                             help='Comma delimited list of Maps to show (default all).')
    
    optParser.add_option('--aligner', action='store', dest='aligner', type='string',
                         help='Alignment software to use (default "'+",".join(DEFAULT_ALIGNER_LIST)+'"). '+\
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
    
    optParser.add_option('--search', action='store', dest='search_type', type='string',
                         help='Whether obtain the hits from all DBs (greedy), only best score hits (best_score), or first hit found (hierarchical); '+\
                         '(default '+str(DEFAULT_HIERARCHICAL)+').')
    
    optParser.add_option('-v', '--verbose', action='store_true', dest='verbose', help='More information printed.')
    
    (options, arguments) = optParser.parse_args()
    
    if not arguments or len(arguments)==0:
        optParser.exit(0, "You may wish to run '-help' option.\n")
    
    ### INPUT FILE
    query_fasta_path = arguments[0] # THIS IS MANDATORY
   
    fastafile = open(query_fasta_path)
    for line in fastafile:
        badheader = re.search(r"^>\S+\s+\S+", line)
        if badheader:
            fastafile.close()
            optParser.exit(0, "Bad FASTA header: please make sure there is only one word, no spaces\n")
    fastafile.close()
 
    sys.stderr.write("Command: "+" ".join(sys.argv)+"\n")
    
    ########## ARGUMENT DEFAULTS
    
    # Verbosity
    verbose_param = options.verbose if options.verbose else False
    
    ## Read conf file
    app_abs_path = os.path.dirname(os.path.abspath(__file__))
    
    paths_config = PathsConfig()
    paths_config.load_config(app_abs_path)
    __app_path = paths_config.get_app_path()
    
    # Aligners list
    if options.aligner:
        if "," in options.aligner:
            aligner_list = options.aligner.strip().split(",")
        else:
            aligner_list = [options.aligner]
    else:
        aligner_list = DEFAULT_ALIGNER_LIST
        
    # Threshold Identity
    if options.thres_id: threshold_id = float(options.thres_id)
    else: threshold_id = DEFAULT_THRES_ID
    
    # Threshold coverage
    if options.thres_cov: threshold_cov = float(options.thres_cov)
    else: threshold_cov = DEFAULT_THRES_COV
        
    # Num threads
    if options.n_threads: n_threads = int(options.n_threads)
    else: n_threads = DEFAULT_N_THREADS
        
    # Hierarchical
    if options.search_type: search_type = options.search_type
    else: search_type = DEFAULT_HIERARCHICAL
    
    # Genetic maps
    maps_conf_file = __app_path+MAPS_CONF
    maps_config = MapsConfig(maps_conf_file)
    if options.maps_param:
        maps_names = options.maps_param
        maps_ids = maps_config.get_maps_ids(maps_names.strip().split(","))
    else:
        maps_ids = maps_config.get_maps_ids()
        maps_names = ",".join(maps_config.get_maps_names(maps_ids))
    
    if len(maps_ids)<=0 or len(maps_names)<=0:
        raise Exception("No valid maps were found. Please, check your --maps parameter or your conf/maps.conf file.")
    
    _print_parameters(query_fasta_path, maps_names, aligner_list, \
                      threshold_id, threshold_cov, \
                      n_threads, search_type)
    
    ########### MAIN
    sys.stderr.write("\n")
    sys.stderr.write("Start\n")
    
    # Databases
    databases_conf_file = __app_path+DATABASES_CONF
    databases_config = DatabasesConfig(databases_conf_file, verbose_param)
    
    facade = AlignmentFacade(paths_config, verbose = verbose_param)
    
    genetic_map_dicts = {}
    
    for map_id in maps_ids:
        sys.stderr.write("\nWorking with map:"+map_id+"\n")
        map_config = maps_config.get_map_config(map_id)
        
        sys.stdout.write(">>"+map_config.get_name()+"\n")
        
        databases_ids = map_config.get_db_list()
        
        # Perform alignments
        alignment_results = facade.perform_alignment(query_fasta_path, databases_ids, databases_config, search_type, aligner_list, \
                                       threshold_id, threshold_cov, n_threads)
        
        aligned = alignment_results.get_aligned()
        
        ########## Output
        
        alignments_printer = OutputFacade.get_alignments_printer(search_type, databases_config)
        alignments_printer.output_results(aligned, databases_ids)
        
except m2pException as m2pe:
    sys.stderr.write("\nThere was an error.\n")
    sys.stderr.write(m2pe.msg+"\n")
    #traceback.print_exc(file=sys.stderr)
except Exception as e:
    #traceback.print_exc(file=sys.stderr)
    sys.stderr.write("\nThere was an error.\n")
    sys.stderr.write(str(e)+"\n")
    print(traceback.format_exc())
    sys.stderr.write('If you can not solve it please contact compbio@eead.csic.es ('+\
                                   'Computational and structural biology group at EEAD-CSIC).\n')
finally:
    pass

sys.stderr.write("Finished.\n")

## END
