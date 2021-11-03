#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# bmap_locate.py is part of Barleymap.
# Copyright (C) 2017 Carlos P Cantalapiedra
# (terms of use can be found within the distributed LICENSE file).

############################################
# This script allows the user to retrieve 
# specific positions from maps, to examine their context.
############################################

import sys, os, traceback
from optparse import OptionParser

from barleymapcore.db.ConfigBase import ConfigBase
from barleymapcore.db.PathsConfig import PathsConfig
from barleymapcore.db.MapsConfig import MapsConfig
from barleymapcore.db.DatasetsConfig import DatasetsConfig
from barleymapcore.alignment.AlignmentFacade import AlignmentFacade
from barleymapcore.datasets.DatasetsFacade import DatasetsFacade
from barleymapcore.annotators.GenesAnnotator import AnnotatorsFactory
from barleymapcore.maps.MapMarkers import MapMarkers
from barleymapcore.m2p_exception import m2pException
from barleymapcore.maps.enrichment.MapEnricher import SHOW_ON_INTERVALS, SHOW_ON_MARKERS

from barleymapcore.output.OutputFacade import OutputFacade

PATHS_CONF = ConfigBase.PATHS_CONF
DATABASES_CONF = ConfigBase.DATABASES_CONF
MAPS_CONF = ConfigBase.MAPS_CONF
DATASETS_CONF = ConfigBase.DATASETS_CONF
DATASETS_ANNOTATION_CONF = ConfigBase.DATASETS_ANNOTATION_CONF
ANNOTATION_TYPES_CONF = ConfigBase.ANNOTATION_TYPES_CONF

DEFAULT_SORT_PARAM = "map default"
DEFAULT_EXTEND_WINDOW = 0.0

def _print_parameters(query_path, genetic_map_name, \
                      sort_param, multiple_param,
                      show_anchored, show_genes, show_markers, \
                      extend_window, \
                      show_unmapped, collapsed_view): #best_score):
    sys.stderr.write("\nParameters:\n")
    sys.stderr.write("\tPositions query file: "+query_path+"\n")
    sys.stderr.write("\tGenetic maps: "+genetic_map_name+"\n")
    sys.stderr.write("\tSort: "+sort_param+"\n")
    sys.stderr.write("\tShow multiples: "+str("yes" if multiple_param else "no")+"\n")
    sys.stderr.write("\tShow anchored features: "+str("yes" if show_anchored else "no")+"\n")
    sys.stderr.write("\tShow genes: "+str("yes" if show_genes else "no")+"\n")
    sys.stderr.write("\tShow markers: "+str("yes" if show_markers else "no")+"\n")
    #sys.stderr.write("\tLoad annotation: "+str("yes" if load_annot else "no")+"\n")
    sys.stderr.write("\tExtend genes/markers search: "+str(extend_window)+"\n")
    sys.stderr.write("\tShow unmapped: "+str("yes" if show_unmapped else "no")+"\n")
    sys.stderr.write("\tShow results as collapsed rows: "+str("yes" if collapsed_view else "no")+"\n")
    
    return
    
############# BARLEYMAP_FIND_MARKERS
try:
    
    ## Usage
    __usage = "usage: bmap_locate.py [OPTIONS] [IDs_FILE]\n\n"+\
              "typical: bmap_locate.py --maps=map queries.tab"
    optParser = OptionParser(__usage)
    
    ########## Define parameters
    ##########
    optParser.add_option('--maps', action='store', dest='maps_param', type='string', help='Comma delimited list of Maps to show.')
    
    optParser.add_option('--sort', action='store', dest='sort_param', type='string', \
                         help='Sort results by centimorgan (cm) or basepairs (bp) '+\
                         '(default: defined for each map in maps configuration.')
    
    optParser.add_option('-k', '--show-multiples', action='store_true', dest='multiple_param',
                         help='Queries with multiple positions will be shown (are obviated by default).')
    
    optParser.add_option('-a', '--anchored', action='store_true', dest='show_anchored',
                         help='Show anchored features at positions of queries.')
    
    optParser.add_option('-g', '--genes', action='store_true', dest='show_genes',
                         help='Genes at positions of queries will be shown. Ignored if -a')
    
    optParser.add_option('-m', '--markers', action='store_true', dest='show_markers',
                         help='Additional markers at positions of queries will be shown. Ignored if -g or -a.')
    
    optParser.add_option('-d', '--show-all-features', action='store_true', dest='show_all',
                         help='All features will be used to enrich a map. By default, only main datasets of each map are used to enrich.')
    
    optParser.add_option('-o', '--show-on-markers', action='store_true', dest='show_on_markers',
                         help='Additional features will shown for each query. By default, they are shown by interval of markers')
    
    optParser.add_option('-e', '--extend', action='store', dest='extend_window',
                         help='Centimorgans or basepairs (depending on sort) to extend the search of -g or -m.'+\
                         '(default '+str(DEFAULT_EXTEND_WINDOW)+')')
    
    #optParser.add_option('-a', '--annot', action='store_true', dest='load_annot',
    #                     help='Annotation info for genes will be shown.')
    
    optParser.add_option('-u', '--show-unmapped', action='store_true', dest='show_unmapped',
                         help='Not found (unaligned, unmapped), will be shown.')
    
    optParser.add_option('-c', '--collapse', action='store_true', dest='collapse',
                         help='Mapping results and features (markers, genes) will be shown at the same level.')
    
    optParser.add_option('-f', action='store_true', dest='format_numbers', \
                         help='cM positions will be output with all decimals (default, 2 decimals).')
    
    optParser.add_option('-v', '--verbose', action='store_true', dest='verbose', help='More information printed.')
    
    ########### Read parameters
    ###########
    (options, arguments) = optParser.parse_args()
    
    if not arguments or len(arguments)==0:
        optParser.exit(0, "You may wish to run '-help' option.\n")
    
    # INPUT FILE
    query_pos_path = arguments[0] # THIS IS MANDATORY
    
    # Verbose
    verbose_param = options.verbose if options.verbose else False
    
    if verbose_param: sys.stderr.write("Command: "+" ".join(sys.argv)+"\n")
    
    # Output format of decimal numbers (cM positions)
    beauty_nums = not options.format_numbers
    
    ## Show only alignments from database with best scores
    #best_score = options.best_score
    
    ## Sort
    if options.sort_param and options.sort_param == "bp":
        sort_param = "bp"
    elif options.sort_param and options.sort_param == "cm":
        sort_param = "cm"
    else:
        sort_param = DEFAULT_SORT_PARAM
    
    ## Multiple
    multiple_param = options.multiple_param if options.multiple_param else False
    
    ## Show anchored
    show_anchored = options.show_anchored if options.show_anchored else False
    
    ## Show genes
    show_genes = options.show_genes if options.show_genes else False
    
    ## Show markers
    show_markers = options.show_markers if options.show_markers else False
    
    ## Show all
    show_all = True if options.show_all else False
    
    ## Show how (on intervals, on markers)
    show_how = SHOW_ON_MARKERS if options.show_on_markers else SHOW_ON_INTERVALS
    
    ## Annotation
    load_annot = True#options.load_annot
    
    ## Genes window
    if options.extend_window:
        extend_window = float(options.extend_window)
    else:
        extend_window = DEFAULT_EXTEND_WINDOW
    
    ## Show unmapped
    show_unmapped = options.show_unmapped if options.show_unmapped else False
    
    # Collapsed view
    collapsed_view = options.collapse if options.collapse else False
    
    ######### Read configuration files
    #########
    app_abs_path = os.path.dirname(os.path.abspath(__file__))
    
    paths_config = PathsConfig()
    paths_config.load_config(app_abs_path)
    __app_path = paths_config.get_app_path()
    
    # Datasets
    datasets_conf_file = __app_path+DATASETS_CONF
    datasets_config = DatasetsConfig(datasets_conf_file, verbose_param)
    datasets_ids = datasets_config.get_datasets_list() #datasets_config.get_datasets().keys()
    
    # Maps
    maps_conf_file = __app_path+MAPS_CONF
    maps_config = MapsConfig(maps_conf_file, verbose_param)
    if options.maps_param:
        maps_names = options.maps_param
        maps_ids = maps_config.get_maps_ids(maps_names.strip().split(","))
    else:
        maps_ids = maps_config.get_maps().keys()
        maps_names = ",".join(maps_config.get_maps_names(maps_ids))
    
    if len(maps_ids)<=0 or len(maps_names)<=0:
        raise Exception("No valid maps were found. Please, check your --maps parameter or your conf/maps.conf file.")
    
    maps_path = paths_config.get_maps_path() #__app_path+config_path_dict["maps_path"]
    
    ##### Print parameters
    #####
    if verbose_param: _print_parameters(query_pos_path, maps_names,
                      sort_param, multiple_param,
                      show_anchored, show_genes, show_markers,
                      extend_window,
                      show_unmapped, collapsed_view)
    
    ############################################################ MAIN
    if verbose_param: sys.stderr.write("\n")
    
    ############ ALIGNMENTS - DATASETS
    #facade = AlignmentFacade(split_blast_path, blastn_app_path, gmap_app_path, hsblastn_app_path,
    #                         blastn_dbs_path, gmap_dbs_path, hsblastn_dbs_path, gmapl_app_path,
    #                         tmp_files_path, databases_config, verbose = verbose_param)
    alignment_facade = AlignmentFacade(paths_config, verbose = verbose_param)
    
    # Load configuration paths
    datasets_path = paths_config.get_datasets_path() #__app_path+config_path_dict["datasets_path"]
    datasets_facade = DatasetsFacade(datasets_config, datasets_path, maps_path, verbose = verbose_param)
    
    ############ Pre-loading of some objects
    ############
    # GenesAnnotator
    if show_genes and load_annot:
        ## Load annotation config
        dsannot_conf_file = __app_path+DATASETS_ANNOTATION_CONF
        anntypes_conf_file = __app_path+ANNOTATION_TYPES_CONF
        annot_path = paths_config.get_annot_path()
        
        annotator = AnnotatorsFactory.get_annotator(dsannot_conf_file, anntypes_conf_file, annot_path, verbose_param)
    else:
        annotator = None
        
    # OutputFacade
    if collapsed_view:
        outputPrinter = OutputFacade.get_collapsed_printer(sys.stdout, verbose = verbose_param, beauty_nums = beauty_nums, show_headers = True)
    else:
        outputPrinter = OutputFacade.get_expanded_printer(sys.stdout, verbose = verbose_param, beauty_nums = beauty_nums, show_headers = True)
    
    ########### Create maps
    ###########
    for map_id in maps_ids:
        sys.stderr.write("bmap_find: Map "+map_id+"\n")
        map_config = maps_config.get_map_config(map_id)
        
        sort_by = map_config.check_sort_param(map_config, sort_param, DEFAULT_SORT_PARAM)
        
        mapMarkers = MapMarkers(maps_path, map_config, alignment_facade, verbose_param)
        
        mapMarkers.locate_positions(query_pos_path, sort_by, multiple_param)
        
        if show_all:
            datasets_enrichment = datasets_ids
        else:
            datasets_enrichment = map_config.get_main_datasets()
        
        mapMarkers.enrichment(annotator, show_markers, show_genes, show_anchored, show_how,
                              datasets_facade, datasets_enrichment, extend_window, collapsed_view, constrain_fine_mapping = False)
        mapping_results = mapMarkers.get_mapping_results()
        
        ############################################################ OUTPUT
        if show_markers:
            outputPrinter.print_map_with_markers(mapping_results.get_map_with_markers(), map_config, multiple_param)
        elif show_genes:
            outputPrinter.print_map_with_genes(mapping_results.get_map_with_genes(), map_config, multiple_param, load_annot, annotator)
        elif show_anchored:
            outputPrinter.print_map_with_anchored(mapping_results.get_map_with_anchored(), map_config, multiple_param)
        else:
            outputPrinter.print_map(mapping_results.get_mapped(), map_config, multiple_param)
        
        # if show_unmapped:
        #     # Markers not found in datasets are included in unaligned map but is clearer show them as unmapped
        #     outputPrinter.print_unaligned(mapping_results.get_unaligned(), map_config)

except m2pException as m2pe:
    sys.stderr.write("\nThere was an error.\n")
    sys.stderr.write(m2pe.msg+"\n")
    #traceback.print_exc(file=sys.stderr)
except Exception as e:
    #traceback.print_exc(file=sys.stderr)
    sys.stderr.write("\nThere was an error.\n")
    sys.stderr.write(str(e)+"\n")
    sys.stderr.write('If you can not solve it please contact compbio@eead.csic.es ('+\
                                   'Computational and structural biology group at EEAD-CSIC).\n')
finally:
    pass

## END
