#!/usr/bin/env python
# -*- coding: utf-8 -*-

# obtain_positions.py is part of Barleymap.
# Copyright (C)  2013-2014  Carlos P Cantalapiedra.
# (terms of use can be found within the distributed LICENSE file).

##########################
# Script to check the map position of
# a list of contigs
##########################

import sys, os
from optparse import OptionParser

from barleymapcore.maps.MapReader import MapReader
from barleymapcore.maps.MapsBase import MapTypes
from barleymapcore.utils.data_utils import read_paths, load_data

def _print_parameters(contig_list_path, genetic_map_name, db_name):
    sys.stderr.write("\nParameters:\n")
    sys.stderr.write("\tContigs file: "+contig_list_path+"\n")
    sys.stderr.write("\tMaps: "+genetic_map_name+"\n")
    sys.stderr.write("\tDBs list: "+db_name+"\n")
    return

def _print_paths(path):
    sys.stderr.write("\nMaps path: "+path+"\n")
    return

## Argument parsing
__usage = "usage: obtain_positions.py [OPTIONS] [IDs_FILE]"
optParser = OptionParser(__usage)

optParser.add_option('--maps', action='store', dest='maps_param', type='string', help='Comma delimited list of Maps to show.')
optParser.add_option('--databases', action='store', dest='databases_param', type='string', help='Comma delimited list of databases to align to.')

(options, arguments) = optParser.parse_args()

if not arguments or len(arguments)==0:
    optParser.exit(0, "You may wish to run '-help' option.\n")

contig_list_path = arguments[0] # THIS IS MANDATORY

sys.stderr.write("Command: "+" ".join(sys.argv)+"\n")

########## ARGUMENT DEFAULTS
## Read conf file
app_abs_path = os.path.dirname(os.path.abspath(__file__))

config_path_dict = read_paths(app_abs_path+"/paths.conf") # data_utils.read_paths
__app_path = config_path_dict["app_path"]

maps_path = __app_path+config_path_dict["maps_path"]
_print_paths(maps_path)
sys.stderr.write("\n")

# Genetic maps
maps_conf_file = __app_path+"conf/maps.conf"
(maps_names, maps_ids) = load_data(maps_conf_file, users_list = options.maps_param, verbose = True)

# Databases
databases_conf_file = __app_path+"conf/references.conf"
(databases_names, databases_ids) = load_data(databases_conf_file, users_list = options.databases_param, verbose = True) # data_utils.load_data

_print_parameters(contig_list_path, maps_names, databases_names)

################ MAIN
sys.stderr.write("\n")
sys.stderr.write("Start\n")

# Read list of contigs
contig_list = []
for contig in open(contig_list_path, 'r'):
    contig_list.append(contig.strip())
    
# Load configuration paths
mapReader = MapReader(maps_path, maps_conf_file, verbose = False)
# Perform alignments
genetic_map_list = []
genetic_map_dict = {}
for genetic_map in maps_ids:
    sys.stderr.write("Genetic map: "+str(genetic_map)+"\n")
    positions_dict = mapReader.obtain_positions(contig_list, genetic_map, databases_ids)
    genetic_map_list.append(genetic_map)
    genetic_map_dict[genetic_map] = positions_dict

############## Output
sys.stderr.write("\n")

maps_data = mapReader.get_maps_data()
for genetic_map in genetic_map_list:
    map_data = maps_data[genetic_map]
    sys.stdout.write(">"+genetic_map+"\n")
    positions_dict = genetic_map_dict[genetic_map]
    
    # Header
    sys.stdout.write("#contig_id\tchr")
    
    if map_data[MapTypes.MAP_HAS_BP_POS] and map_data[MapTypes.MAP_HAS_CM_POS]:
        sys.stdout.write("\tcM\tbp")
    elif map_data[MapTypes.MAP_HAS_CM_POS]:
        sys.stdout.write("\tcM")
    elif map_data[MapTypes.MAP_HAS_BP_POS]:
        sys.stdout.write("\tbp")
    else:
        raise Exception("Bad positional configuration for map "+genetic_map+"\n")
    
    sys.stdout.write("\n")
    
    # Positions
    for contig_id in positions_dict:
        chr_num = positions_dict[contig_id]["chr"]
        cm_pos = positions_dict[contig_id]["cm_pos"]
        bp_pos = positions_dict[contig_id]["bp_pos"]
        
        sys.stdout.write(contig_id+"\t"+str(chr_num))
        
        if map_data[MapTypes.MAP_HAS_BP_POS] and map_data[MapTypes.MAP_HAS_CM_POS]:
            sys.stdout.write("\t"+str("%0.2f" % float(cm_pos))+"\t"+str(bp_pos))
        elif map_data[MapTypes.MAP_HAS_CM_POS]:
            sys.stdout.write("\t"+str("%0.2f" % float(cm_pos)))
        elif map_data[MapTypes.MAP_HAS_BP_POS]:
            sys.stdout.write("\t"+str(bp_pos))
        else:
            raise Exception("Bad positional configuration for map "+genetic_map+"\n")
        #if bp_pos != -1: sys.stdout.write("\t"+str(bp_pos))
        sys.stdout.write("\n")

sys.stderr.write("Finished.\n")

## END