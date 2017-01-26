#!/usr/bin/env python
# -*- coding: utf-8 -*-

# bmap_find.py is part of Barleymap.
# Copyright (C)  2013-2014  Carlos P Cantalapiedra.
# Copyright (C) 2016 Carlos P Cantalapiedra
# (terms of use can be found within the distributed LICENSE file).

############################################
# This script allows the user to retrieve the map
# positions from marker IDs.
############################################

import sys, os, traceback
from optparse import OptionParser

from barleymapcore.utils.data_utils import read_paths
from barleymapcore.db.MapsConfig import MapsConfig
from barleymapcore.db.DatasetsConfig import DatasetsConfig
from barleymapcore.db.DatabasesConfig import DatabasesConfig
from barleymapcore.datasets.DatasetsFacade import DatasetsFacade
from barleymapcore.maps.MapMarkers import MapMarkers
from barleymapcore.m2p_exception import m2pException
from output.OutputFacade import OutputFacade

DATABASES_CONF = "conf/databases.conf"
MAPS_CONF = "conf/maps.conf"
DATASETS_CONF = "conf/datasets.conf"

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

def _print_parameters(query_ids_path, genetic_map_name, \
                      sort_param, multiple_param, best_score, \
                      show_genes_param, show_markers_param, \
                      load_annot_param, extend_param, extend_window, \
                      show_unmapped_param):
    sys.stderr.write("\nParameters:\n")
    sys.stderr.write("\tIDs query file: "+query_ids_path+"\n")
    sys.stderr.write("\tGenetic maps: "+genetic_map_name+"\n")
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
    
############# BARLEYMAP_FIND_MARKERS
try:
    
    ## Argument parsing
    __usage = "usage: bmap_find.py [OPTIONS] [IDs_FILE]\n\n"+\
              "typical: bmap_find.py --maps=map queries.ids"
    optParser = OptionParser(__usage)
    
    optParser.add_option('--maps', action='store', dest='maps_param', type='string', help='Comma delimited list of Maps to show.')
    
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
    query_ids_path = arguments[0] # THIS IS MANDATORY
    
    if options.verbose: verbose_param = True
    else: verbose_param = False
    
    if verbose_param: sys.stderr.write("Command: "+" ".join(sys.argv)+"\n")
    
    ########## ARGUMENT DEFAULTS
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
    
    # Datasets
    datasets_conf_file = __app_path+DATASETS_CONF
    datasets_config = DatasetsConfig(datasets_conf_file)
    datasets_ids = datasets_config.get_datasets().keys()
    #(datasets_names, datasets_ids) = load_data(datasets_conf_file, verbose = verbose_param) # data_utils.load_datasets
    
    # Databases
    databases_conf_file = __app_path+DATABASES_CONF
    databases_config = DatabasesConfig(databases_conf_file)
    databases_ids = databases_config.get_databases().keys()
    #(databases_names, databases_ids) = load_data(databases_conf_file, verbose = verbose_param) # data_utils.load_data
    
    # Genetic maps
    maps_conf_file = __app_path+MAPS_CONF
    maps_config = MapsConfig(maps_conf_file)
    if options.maps_param:
        maps_names = options.maps_param
        maps_ids = maps_config.get_maps_ids(maps_names.strip().split(","))
    else:
        maps_ids = maps_config.get_maps().keys()
        maps_names = ",".join(maps_config.get_maps_names(maps_ids))
    #(maps_names, maps_ids) = load_data(maps_conf_file, users_list = options.maps_param, verbose = verbose_param)
    
    maps_path = __app_path+config_path_dict["maps_path"]
    
    if verbose_param: _print_parameters(query_ids_path, maps_names, \
                      sort_param, multiple_param_text, options.best_score, \
                      show_genes_param, show_markers_param, \
                      load_annot_param, extend_param, extend_window, \
                      show_unmapped_param)
    
    ############################################################ MAIN
    if verbose_param: sys.stderr.write("\n")
    
    ############ ALIGNMENTS - DATASETS
    # Load configuration paths
    datasets_path = __app_path+config_path_dict["datasets_path"]
    datasets_facade = DatasetsFacade(datasets_config, datasets_path, verbose = verbose_param)
    
    maps_dict = {}
    
    for map_id in maps_ids:
        sys.stderr.write("bmap_find: Map "+map_id+"\n")
        map_config = maps_config.get_map_config(map_id)
        
        sort_by = map_config.check_sort_param(map_config, sort_param, DEFAULT_SORT_PARAM)
        
        ############ MAPS
        mapMarkers = MapMarkers(maps_path, map_config, verbose_param)
        
        mapMarkers.setup_map(query_ids_path, datasets_ids, datasets_facade, best_score_filter, sort_by, multiple_param)
        
        ############ OTHER MARKERS
        if show_markers and not show_genes:
            mapMarkers.enrich_with_markers(datasets_facade, extend, extend_window, \
                                                          constrain_fine_mapping = False)
            
        ########### GENES
        if show_genes:
            mapMarkers.enrich_with_genes(show_genes_param, load_annot,
                                         extend, extend_window, extend_window, sort_by,
                                         constrain_fine_mapping = False)
        
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
    sys.stderr.write("\nThere was an error.\n")
    sys.stderr.write('If you can not solve it please contact compbio@eead.csic.es ('+\
                                   'laboratory of computational biology at EEAD).\n')
finally:
    pass

## END