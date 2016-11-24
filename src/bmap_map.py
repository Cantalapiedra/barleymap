#!/usr/bin/env python
# -*- coding: utf-8 -*-

# bmap_map.py is part of Barleymap.
# Copyright (C)  2016  Carlos P Cantalapiedra.
# (terms of use can be found within the distributed LICENSE file).

############################################
# This script allows to translate alignments to DBs (obtained with bmap_align_to_db)
# into Map positions.
############################################

import sys, os#, traceback
from optparse import OptionParser

from output.OutputFacade import OutputFacade
from barleymapcore.datasets.DatasetsFacade import DatasetsFacade, SELECTION_NONE, SELECTION_BEST_SCORE
from barleymapcore.maps.MapMarkers import MapMarkers
from barleymapcore.maps.MapsConfig import MapsConfig
from barleymapcore.utils.data_utils import read_paths, load_data

DATABASES_CONF = "conf/databases.conf"
DATASETS_CONF = "conf/datasets.conf"
MAPS_CONF = "conf/maps.conf"

def _print_parameters(genetic_map_name, dataset_name):
    sys.stderr.write("\nParameters:\n")
    sys.stderr.write("\tMap: "+genetic_map_name+"\n")
    sys.stderr.write("\tDataset: "+dataset_name+"\n")
    
    return
    
#############
try:
    
    ## Argument parsing
    __usage = "usage: bmap_map.py [OPTIONS] [IDs_FILE]"
    optParser = OptionParser(__usage)
    
    optParser.add_option('--map', action='store', dest='map_param', type='string', help='Map.')
    optParser.add_option('--dataset', action='store', dest='dataset_param', type='string', help='Dataset to map.')
    optParser.add_option('-v', '--verbose', action='store_true', dest='verbose', help='More information printed.')
    
    (options, arguments) = optParser.parse_args()
    
    if not arguments or len(arguments)==0:
        optParser.exit(0, "You may wish to run '-help' option.\n")
    
    if options.verbose: verbose_param = True
    else: verbose_param = False
    
    if verbose_param: sys.stderr.write("Command: "+" ".join(sys.argv)+"\n")
    
    ########## ARGUMENT DEFAULTS
    ## Read conf file
    app_abs_path = os.path.dirname(os.path.abspath(__file__))

    config_path_dict = read_paths(app_abs_path+"/paths.conf") # data_utils.read_paths
    __app_path = config_path_dict["app_path"]
    
    # Datasets
    datasets_conf_file = __app_path+DATASETS_CONF
    (dataset_name, dataset_id) = load_name(datasets_conf_file,
                                               user_name = options.dataset_param,
                                               verbose = verbose_param) # data_utils.load_name
    
    # Genetic maps
    maps_conf_file = __app_path+MAPS_CONF
    (map_name, map_id) = load_name(maps_conf_file,
                                       user_name = options.map_param,
                                       verbose = verbose_param)
    
    if verbose_param: _print_parameters(map_name, dataset_name)
    
    ############################################################ MAIN
    if verbose_param: sys.stderr.write("\n")
    
    ############ ALIGNMENTS - DATASETS
    # Load configuration paths
    
    maps_config = MapsConfig(maps_conf_file, verbose = verbose_param)
    map_config  = maps_config.get_map(map_ids)
    map_databases = maps_config.get_map_db_list(map_config)
    map_hierarchical = maps_config.get_map_is_hierarchical(map_config)
    
    # Perform alignments
    datasets_path = __app_path+config_path_dict["datasets_path"]
    facade = DatasetsFacade(datasets_conf_file, datasets_path, verbose = verbose_param)
    results = facade.retrieve_dataset_alignments(dataset_id, map_databases, map_hierarchical)
    
    unmapped = []#facade.get_alignment_unmapped()
    
    ############ MAPS
    mapMarkers = MapMarkers(config_path_dict, [map_id], verbose_param)
    mapMarkers.create_genetic_maps(results, unmapped, map_databases)
    
    ############################################################ OUTPUT
    genetic_map_dict = mapMarkers.get_genetic_maps()
    
    outputPrinter = OutputFacade().get_plain_printer(sys.stdout, verbose = verbose_param)
    
    outputPrinter.print_maps(outputPrinter, [map_id], genetic_map_dict, show_headers = True)

except Exception as e:
    #traceback.print_exc(file=sys.stderr)
    sys.stderr.write("\nERROR\n")
    sys.stderr.write(str(e)+"\n")
    sys.stderr.write('An error was detected. If you can not solve it please contact compbio@eead.csic.es ('+\
                                   'laboratory of computational biology at EEAD).\n')
finally:
    pass

## END