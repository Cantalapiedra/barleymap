#!/usr/bin/env python
# -*- coding: utf-8 -*-

# bmap_align.py is part of Barleymap.
# Copyright (C)  2013-2014  Carlos P Cantalapiedra.
# Copyright (C) 2016 Carlos P Cantalapiedra
# (terms of use can be found within the distributed LICENSE file).

############################################
# This script allows the user to retrieve map
# positions from fasta seqs.
############################################

import sys, os, traceback
from optparse import OptionParser

from barleymapcore.utils.data_utils import read_paths
from barleymapcore.db.MapsConfig import MapsConfig
from barleymapcore.db.DatasetsConfig import DatasetsConfig
from barleymapcore.db.DatabasesConfig import DatabasesConfig
from barleymapcore.alignment.AlignmentFacade import AlignmentFacade
from barleymapcore.datasets.DatasetsFacade import DatasetsFacade
from barleymapcore.maps.MapMarkers import MapMarkers
from barleymapcore.m2p_exception import m2pException
from output.OutputFacade import OutputFacade

DATABASES_CONF = "conf/databases.conf"
MAPS_CONF = "conf/maps.conf"
DATASETS_CONF = "conf/datasets.conf"

DEFAULT_QUERY_MODE = "gmap"
DEFAULT_THRES_ID = 98.0
DEFAULT_THRES_COV = 95.0
DEFAULT_N_THREADS = 1
DEFAULT_BEST_SCORE = True
DEFAULT_BEST_SCORE_PARAM = "yes"
DEFAULT_SORT_PARAM = "map default"
DEFAULT_SHOW_MULTIPLES = True
DEFAULT_SHOW_MULTIPLES_PARAM = "yes"
DEFAULT_SHOW_GENES = False
DEFAULT_SHOW_GENES_PARAM = "no"
DEFAULT_SHOW_MARKERS = False
DEFAULT_SHOW_MARKERS_PARAM = "no"
DEFAULT_LOAD_ANNOT = False
DEFAULT_LOAD_ANNOT_PARAM = "no"
DEFAULT_EXTEND = False
DEFAULT_EXTEND_PARAM = "no"
DEFAULT_EXTEND_WINDOW = 5.0
DEFAULT_SHOW_UNMAPPED = False
DEFAULT_SHOW_UNMAPPED_PARAM = "no"

def _print_parameters(fasta_path, genetic_map_name, query_type, \
                      threshold_id, threshold_cov, n_threads, \
                      sort_param, multiple_param, best_score, \
                      show_genes_param, show_markers_param, \
                      load_annot_param, extend_param, extend_window, \
                      show_unmapped_param):
    sys.stderr.write("\nParameters:\n")
    sys.stderr.write("\tQuery fasta: "+fasta_path+"\n")
    sys.stderr.write("\tGenetic maps: "+genetic_map_name+"\n")
    sys.stderr.write("\tAligner: "+query_type+"\n")
    sys.stderr.write("\tThresholds --> %id="+str(threshold_id)+" : %query_cov="+str(threshold_cov)+"\n")
    sys.stderr.write("\tThreads: "+str(n_threads)+"\n")
    sys.stderr.write("\tBest score filtering: "+str(best_score)+"\n")
    sys.stderr.write("\tSort: "+sort_param+"\n")
    sys.stderr.write("\tShow multiples: "+str(multiple_param)+"\n")
    sys.stderr.write("\tShow genes: "+str(show_genes_param)+"\n")
    sys.stderr.write("\tShow markers: "+str(show_markers_param)+"\n")
    sys.stderr.write("\tLoad annotation: "+str(load_annot_param)+"\n")
    sys.stderr.write("\tExtend genes search: "+str(extend_param)+"\n")
    sys.stderr.write("\tGenes window: "+str(extend_window)+"\n")
    sys.stderr.write("\tShow unmapped: "+str(show_unmapped_param)+"\n")
    
    return

############ BARLEYMAP_ALIGN_SEQS
try:
    
    ## Argument parsing
    __usage = "usage: bmap_align.py [OPTIONS] [FASTA_FILE]\n\n"+\
              "typical: bmap_align.py --maps=map queries.fasta"
    optParser = OptionParser(__usage)
    
    optParser.add_option('--maps', action='store', dest='maps_param', type='string', \
                         help='Comma delimited list of Maps to show (default all).')
    
    optParser.add_option('--aligner', action='store', dest='query_mode', type='string',
                     help='Alignment software to use (default "'+DEFAULT_QUERY_MODE+'"). '+\
                     'The "gmap" option means to use only GMAP. '+\
                     'The "blastn" option means to use only Blastn. '+\
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
                         '(default '+DEFAULT_BEST_SCORE_PARAM+').')
    
    optParser.add_option('--sort', action='store', dest='sort_param', type='string', \
                         help='Sort results by centimorgan (cm) or basepairs (bp) '+\
                         '(default: defined for each map in maps configuration.')
    
    optParser.add_option('--show-multiples', action='store', dest='multiple_param', type='string', \
                         help='Whether show (yes) or not (no) IDs with multiple positions.'+\
                         '(default '+DEFAULT_SHOW_MULTIPLES_PARAM+'')
    
    optParser.add_option('--genes', action='store', dest='show_genes', type='string', \
                         help='Show genes on marker (marker), between markers (between) '+\
                         'or dont show (no). '+\
                         '(default '+DEFAULT_SHOW_GENES_PARAM+')'+\
                         'If --genes is active, --markers option is ignored.')
    
    optParser.add_option('--markers', action='store', dest='show_markers', type='string', \
                         help='Show additional markers (yes) or not (no). '+\
                         '(default '+DEFAULT_SHOW_MARKERS_PARAM+')'+\
                         'Ignored if --genes active.')
    
    optParser.add_option('--annot', action='store', dest='load_annot', type='string', \
                         help='Whether load annotation info for genes (yes) or not (no).'+\
                         '(default '+DEFAULT_LOAD_ANNOT_PARAM+')')
    
    optParser.add_option('--extend', action='store', dest='extend', type='string', \
                         help='Whether extend search for genes (yes) or not (no).'+\
                         '(default '+DEFAULT_EXTEND_PARAM+')')
    
    optParser.add_option('--extend-window', action='store', dest='extend_window', type='string', \
                         help='Centimorgans or basepairs (depending on sort) to extend the search for genes.'+\
                         '(default '+str(DEFAULT_EXTEND_WINDOW)+')')
    
    optParser.add_option('--show-unmapped', action='store', dest='show_unmapped', type='string', \
                         help='Whether to output only maps (no), or unmapped results as well (yes).'+\
                         '(default '+DEFAULT_SHOW_UNMAPPED_PARAM+')')
    
    optParser.add_option('-v', '--verbose', action='store_true', dest='verbose', help='More information printed.')
    
    (options, arguments) = optParser.parse_args()
    
    if not arguments or len(arguments)==0:
        optParser.exit(0, "You may wish to run '-help' option.\n")
    
    # INPUT FILE
    query_fasta_path = arguments[0] # THIS IS MANDATORY
    
    if options.verbose: verbose_param = True
    else: verbose_param = False
    
    if verbose_param: sys.stderr.write("Command: "+" ".join(sys.argv)+"\n")
    
    ########## ARGUMENT DEFAULTS
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
    
    ## Sort
    if options.sort_param and options.sort_param == "bp":
        sort_param = "bp"
    elif options.sort_param and options.sort_param == "cm":
        sort_param = "cm"
    else:
        sort_param = DEFAULT_SORT_PARAM
    
    ## Multiple
    if options.multiple_param and options.multiple_param == "yes":
        multiple_param = True
        multiple_param_text = "yes"
    else:
        multiple_param = DEFAULT_SHOW_MULTIPLES
        multiple_param_text = DEFAULT_SHOW_MULTIPLES_PARAM
    
    ## Show genes
    if options.show_genes and options.show_genes == "yes":
        show_genes = True
        show_genes_param = "yes"
    else:
        show_genes = DEFAULT_SHOW_GENES
        show_genes_param = DEFAULT_SHOW_GENES_PARAM
    
    ## Show markers
    if options.show_markers and options.show_markers == "yes":
        show_markers = True
        show_markers_param = "yes"
    else:
        show_markers = DEFAULT_SHOW_MARKERS
        show_markers_param = DEFAULT_SHOW_MARKERS_PARAM
    
    ## Annotation
    if options.load_annot and options.load_annot == "yes":
        load_annot = True
        load_annot_param = "yes"
    else:
        load_annot = DEFAULT_LOAD_ANNOT
        load_annot_param = DEFAULT_LOAD_ANNOT_PARAM
        
    ## Extend genes shown, on marker or in the edges when between markers
    if options.extend and options.extend == "yes":
        extend = True
        extend_param = "yes"
    else:
        extend = DEFAULT_EXTEND
        extend_param = DEFAULT_EXTEND_PARAM
    
    ## Genes window
    if options.extend_window:
        extend_window = float(options.extend_window)
    else:
        extend_window = DEFAULT_EXTEND_WINDOW
    
    ## Show unmapped
    if options.show_unmapped and options.show_unmapped == "yes":
        show_unmapped_param = "yes"
        show_unmapped = True
    else:
        show_unmapped = DEFAULT_SHOW_UNMAPPED
        show_unmapped_param = DEFAULT_SHOW_UNMAPPED_PARAM
    
    ## Read conf file
    app_abs_path = os.path.dirname(os.path.abspath(__file__))

    config_path_dict = read_paths(app_abs_path+"/paths.conf") # data_utils.read_paths
    __app_path = config_path_dict["app_path"]
    
    # Genetic maps
    maps_conf_file = __app_path+MAPS_CONF
    maps_config = MapsConfig(maps_conf_file)
    if options.maps_param:
        maps_names = options.maps_param
        maps_ids = maps_config.get_maps_ids(maps_names.strip().split(","))
    else:
        maps_ids = maps_config.get_maps().keys()
        maps_names = ",".join(maps_config.get_maps_names(maps_ids))
    
    maps_path = __app_path+config_path_dict["maps_path"]
    
    if verbose_param: _print_parameters(query_fasta_path, maps_names, query_mode, \
                      threshold_id, threshold_cov, n_threads, \
                      sort_param, multiple_param_text, options.best_score, \
                      show_genes_param, show_markers_param, \
                      load_annot_param, extend_param, extend_window, \
                      show_unmapped_param)
    
    ############### MAIN
    if verbose_param: sys.stderr.write("\n")
    
    ############# ALIGNMENTS - REFERENCES
    # Load configuration paths
    #app_path = config_path_dict["app_path"]
    split_blast_path = __app_path+config_path_dict["split_blast_path"]
    tmp_files_path = __app_path+config_path_dict["tmp_files_path"]
    blastn_app_path = config_path_dict["blastn_app_path"]
    gmap_app_path = config_path_dict["gmap_app_path"]
    gmapl_app_path = config_path_dict["gmapl_app_path"]
    hsblastn_app_path = config_path_dict["hsblastn_app_path"]
    
    blastn_dbs_path = config_path_dict["blastn_dbs_path"]
    gmap_dbs_path = config_path_dict["gmap_dbs_path"]
    hsblastn_dbs_path = config_path_dict["hsblastn_dbs_path"]
    
    # Databases
    databases_conf_file = __app_path+DATABASES_CONF
    databases_config = DatabasesConfig(databases_conf_file, verbose_param)
    
    facade = AlignmentFacade(split_blast_path, blastn_app_path, gmap_app_path, hsblastn_app_path,
                             blastn_dbs_path, gmap_dbs_path, hsblastn_dbs_path, gmapl_app_path,
                             tmp_files_path, databases_config, verbose = verbose_param)
    
    maps_dict = {}
    
    for map_id in maps_ids:
        sys.stderr.write("bmap_align: Map "+map_id+"\n")
        
        map_config = maps_config.get_map_config(map_id)
        databases_ids = map_config.get_db_list()
        hierarchical = map_config.is_hierarchical()
        
        sort_by = map_config.check_sort_param(map_config, sort_param, DEFAULT_SORT_PARAM)
        
        ############ Perform alignments
        # TODO: avoid aligning to the same DB as one of a previous map
        # this "TODO" would need to handle correctly best_score and hierarchical
        facade.perform_alignment(query_fasta_path, databases_ids, hierarchical, query_mode,
                                           threshold_id, threshold_cov, n_threads, \
                                           best_score_filter)
        
        results = facade.get_alignment_results()
        unaligned = facade.get_alignment_unmapped()  
        
        ############ MAPS
        mapMarkers = MapMarkers(maps_path, map_config, verbose_param)
        
        mapMarkers.create_map(results, unaligned, sort_by, multiple_param)
        
        ############ OTHER MARKERS
        if show_markers and not show_genes:
            
            # Datasets config
            datasets_conf_file = __app_path+DATASETS_CONF
            datasets_config = DatasetsConfig(datasets_conf_file)
            
            # Load DatasetsFacade
            datasets_path = __app_path+config_path_dict["datasets_path"]
            datasets_facade = DatasetsFacade(datasets_config, datasets_path, verbose = verbose_param)
            
            # Enrich with markers
            mapMarkers.enrich_with_markers(datasets_facade, extend, extend_window,
                                            constrain_fine_mapping = False)
            
        ########### GENES
        if show_genes:
            mapMarkers.enrich_with_genes(show_genes_param, load_annot,
                                         extend, extend_window,
                                         sort_by, constrain_fine_mapping = False)
        
        mapping_results = mapMarkers.get_mapping_results()
        
        if not map_id in maps_dict:
            maps_dict[map_id] = mapping_results
        else:
            raise Exception("Duplicated map "+map_id+".")
    
    ############################################################ OUTPUT
    
    outputPrinter = OutputFacade().get_plain_printer(sys.stdout, verbose = verbose_param)
    
    outputPrinter.print_maps(maps_dict,
                             show_genes, show_markers, show_unmapped,
                             multiple_param_text, load_annot, show_headers = True)

except m2pException as m2pe:
    sys.stderr.write("\nThere was an error.\n")
    sys.stderr.write(m2pe.msg+"\n")
except Exception as e:
    traceback.print_exc(file=sys.stderr)
    sys.stderr.write("\nERROR\n")
    sys.stderr.write(str(e)+"\n")
    sys.stderr.write('An error was detected. If you can not solve it please contact compbio@eead.csic.es ('+\
                                   'laboratory of computational biology at EEAD).\n')
finally:
    pass

def __check_sort_param(map_name, sort_param, map_default_sort_by, map_has_cm_pos, map_has_bp_pos):
    sort_by = ""
    
    if sort_param == map_default_sort_by:
        sort_by = sort_param
    else:
        # sort_param has priority
        if sort_param == MapTypes.MAP_SORT_PARAM_CM and map_has_cm_pos:
            sort_by = sort_param
        elif sort_param == MapTypes.MAP_SORT_PARAM_BP and map_has_bp_pos:
            sort_by = sort_param
        # else, check map_default_sort_by
        else:
            if sort_param != DEFAULT_SORT_PARAM:
                sys.stderr.write("WARNING: the sort parameter "+sort_param+" is not compatible with map "+map_name+". Using default map sort parameter...\n")
            if map_default_sort_by == MapTypes.MAP_SORT_PARAM_CM and map_has_cm_pos:
                sort_by = map_default_sort_by
            elif map_default_sort_by == MapTypes.MAP_SORT_PARAM_BP and map_has_bp_pos:
                sort_by = map_default_sort_by
            else:
                raise Exception("Map default sort configure as \""+map_default_sort_by+"\" assigned to a map which has not such kind of position.")
    
    return sort_by

## END