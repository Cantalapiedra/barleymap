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
from barleymapcore.datasets.DatasetsFacade import DatasetsFacade, SELECTION_NONE, SELECTION_BEST_SCORE
from barleymapcore.maps.MapMarkers import MapMarkers

from output.OutputFacade import OutputFacade

DATABASES_CONF = "conf/databases.conf"
MAPS_CONF = "conf/maps.conf"
DATASETS_CONF = "conf/datasets.conf"

def _print_parameters(query_ids_path, genetic_map_name, \
                      sort_param, multiple_param, best_score, \
                      show_genes_param, show_markers_param, \
                      load_annot_param, genes_extend_param, genes_window, \
                      show_unmapped_param):
    sys.stderr.write("\nParameters:\n")
    sys.stderr.write("\tIDs query file: "+query_ids_path+"\n")
    sys.stderr.write("\tGenetic maps: "+genetic_map_name+"\n")
    sys.stderr.write("\tSort: "+sort_param+"\n")
    sys.stderr.write("\tShow multiples: "+str(multiple_param)+"\n")
    sys.stderr.write("\tBest score filtering: "+str(best_score)+"\n")
    sys.stderr.write("\tShow genes: "+str(show_genes_param)+"\n")
    sys.stderr.write("\tShow markers: "+str(show_markers_param)+"\n")
    sys.stderr.write("\tLoad annotation: "+str(load_annot_param)+"\n")
    sys.stderr.write("\tExtend genes search: "+str(genes_extend_param)+"\n")
    sys.stderr.write("\tGenes window: "+str(genes_window)+"\n")
    sys.stderr.write("\tShow unmapped: "+str(show_unmapped_param)+"\n")
    
    return
    
############# BARLEYMAP_FIND_MARKERS
try:
    
    ## Argument parsing
    __usage = "usage: bmap_find.py [OPTIONS] [IDs_FILE]"
    optParser = OptionParser(__usage)
    
    optParser.add_option('--maps', action='store', dest='maps_param', type='string', help='Comma delimited list of Maps to show.')
    optParser.add_option('--sort', action='store', dest='sort_param', type='string', help='Sort results by centimorgan (cm) or basepairs (bp).')
    optParser.add_option('--show-multiples', action='store', dest='multiple_param', type='string', help='Whether show (yes) or not (no) IDs with multiple positions.')
    
    optParser.add_option('--best-score', action='store', dest='best_score', type='string', \
                     help='Whether return secondary hits (no), \
                     best score hits for each database (db) or \
                     overall best score hits (yes; default).')
    
    optParser.add_option('--genes', action='store', dest='show_genes', type='string', help='Show genes on marker (marker), between markers (between) \
                         or dont show (no). If --genes is active, --markers option is ignored.')
    optParser.add_option('--markers', action='store', dest='show_markers', type='string', help='Show additional markers (yes) or not (no). Ignored if --genes active.')
    optParser.add_option('--annot', action='store', dest='load_annot', type='string', help='Whether load annotation info for genes (yes) or not (no).')
    optParser.add_option('--extend', action='store', dest='extend', type='string', help='Whether extend search for genes (yes) or not (no).')
    optParser.add_option('--genes-window', action='store', dest='genes_window', type='string', help='Centimorgans or basepairs (depending on sort)\
                         to extend the search for genes (--genes) or markers (--markers).')
    optParser.add_option('--show-unmapped', action='store', dest='show_unmapped', type='string', help='Whether to output only maps (no), or unmapped results as well (yes).')
    
    optParser.add_option('-v', '--verbose', action='store_true', dest='verbose', help='More information printed.')
    
    (options, arguments) = optParser.parse_args()
    
    if not arguments or len(arguments)==0:
        optParser.exit(0, "You may wish to run '-help' option.\n")
    
    query_ids_path = arguments[0] # THIS IS MANDATORY
    
    if options.verbose: verbose_param = True
    else: verbose_param = False
    
    if verbose_param: sys.stderr.write("Command: "+" ".join(sys.argv)+"\n")
    
    ########## ARGUMENT DEFAULTS
    ## Sort
    if options.sort_param and options.sort_param == "bp":
        sort_param = "bp"
    else:
        sort_param = "cm"
    
    ## Multiple
    if options.multiple_param and options.multiple_param == "yes":
        multiple_param = True
        multiple_param_text = "yes"
    else:
        multiple_param = False
        multiple_param_text = "no"
        
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
    
    ## Show genes
    if options.show_genes:
        show_genes_param = options.show_genes
        if options.show_genes == "no":
            show_genes = False
        else:
            show_genes = True
    else:
        show_genes_param = "no"
        show_genes = False
    
    ## Show markers
    if options.show_markers:
        show_markers_param = options.show_markers
        if options.show_markers == "no":
            show_markers = False
        else:
            show_markers = True
    else:
        show_markers_param = "no"
        show_markers = False
    
    ## Annotation
    if options.load_annot and options.load_annot == "yes":
        load_annot = True
        load_annot_param = "yes"
    else:
        load_annot = False
        load_annot_param = "no"
    
    ## Extend genes shown, on marker or in the edges when between markers
    if options.extend and options.extend == "yes":
        genes_extend = True
        genes_extend_param = "yes"
    else:
        genes_extend = False
        genes_extend_param = "no"
    
    ## Genes window
    if options.genes_window:
        genes_window = float(options.genes_window)
    else:
        genes_window = 0.2
    # genes_window_unit = "cM" ESTO LO HE CAMBIADO. TODO SE HARA POR EL SORT_PARAM
    
    ## Show unmapped
    if options.show_unmapped and options.show_unmapped == "yes":
        show_unmapped_param = "yes"
        show_unmapped = True
    else:
        show_unmapped_param = "no"
        show_unmapped = False
    
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
                      load_annot_param, genes_extend_param, genes_window, \
                      show_unmapped_param)
    
    ############################################################ MAIN
    if verbose_param: sys.stderr.write("\n")
    
    ############ ALIGNMENTS - DATASETS
    # Load configuration paths
    datasets_path = __app_path+config_path_dict["datasets_path"]
    facade = DatasetsFacade(datasets_config, datasets_path, verbose = verbose_param)
    
    genetic_map_dicts = {}
    
    for map_id in maps_ids:
        sys.stderr.write("********* Map "+map_id+"\n")
        map_config = maps_config.get_map(map_id)
        hierarchical = maps_config.get_map_is_hierarchical(map_config)
        
        # Perform alignments
        results = facade.retrieve_ids_map(query_ids_path, datasets_ids, map_id, \
                                            selection, best_score_filter)
        
        unmapped = facade.get_alignment_unmapped()
        
        ############ MAPS
        mapMarkers = MapMarkers(maps_path, maps_config, [map_id], verbose_param)
        databases_ids = maps_config.get_map_db_list(map_config)
        mapMarkers.create_genetic_maps(results, unmapped, databases_ids, sort_param, multiple_param)
        
        ############ OTHER MARKERS
        if show_markers and not show_genes:
            markers_dict = mapMarkers.enrich_with_markers(genes_extend, genes_window, genes_window, sort_param, \
                                                          databases_ids, datasets_ids, datasets_conf_file,
                                                        hierarchical, constrain_fine_mapping = False)
        ########### GENES
        if show_genes:
            mapMarkers.enrich_with_genes(show_genes_param, load_annot,
                                         genes_extend, genes_window, genes_window, sort_param,
                                         constrain_fine_mapping = False)
        
        genetic_map_dict = mapMarkers.get_genetic_maps()
        
        genetic_map_dicts.update(genetic_map_dict)
        
    ############################################################ OUTPUT
    
    outputPrinter = OutputFacade().get_plain_printer(sys.stdout, verbose = verbose_param)
    
    outputPrinter.print_maps(outputPrinter, maps_ids, genetic_map_dict, show_genes, show_markers, show_unmapped, multiple_param_text, load_annot, show_headers = True)

except Exception as e:
    traceback.print_exc(file=sys.stderr)
    sys.stderr.write("\nERROR\n")
    sys.stderr.write(str(e)+"\n")
    sys.stderr.write('An error was detected. If you can not solve it please contact compbio@eead.csic.es ('+\
                                   'laboratory of computational biology at EEAD).\n')
finally:
    pass

## END