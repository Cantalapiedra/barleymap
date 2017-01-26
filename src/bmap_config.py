#!/usr/bin/env python
# -*- coding: utf-8 -*-

# check_config.py is part of Barleymap.
# Copyright (C)  2013-2014  Carlos P Cantalapiedra.
# (terms of use can be found within the distributed LICENSE file).

###########################
## Script to show the configuration data of Barleymap.
###########################

import sys, os
from optparse import OptionParser
from barleymapcore.m2p_exception import m2pException

from barleymapcore.utils.data_utils import read_paths
from barleymapcore.db.DatabasesConfig import DatabasesConfig
from barleymapcore.db.DatasetsConfig import DatasetsConfig
from barleymapcore.db.MapsConfig import MapsConfig
from barleymapcore.db.ConfigBase import ConfigBase

DATABASES_CONF = ConfigBase.DATABASES_CONF
DATASETS_CONF = ConfigBase.DATASETS_CONF
MAPS_CONF = ConfigBase.MAPS_CONF

def _print_paths(blastn_app_path, gmap_app_path, gmapl_app_path, hsblastn_app_path, \
                 blastn_dbs_path, gmap_dbs_path, hsblastn_dbs_path, \
                 split_blast_path, genmap_path):
    
    sys.stderr.write("\nBlastn:\n")
    sys.stderr.write("\tapp path: "+blastn_app_path+"\n")
    sys.stderr.write("\tdbs path: "+blastn_dbs_path+"\n")
    
    sys.stderr.write("GMAP:\n")
    sys.stderr.write("\tapp path: "+gmap_app_path+"\n")
    sys.stderr.write("\tgmapl app path: "+gmapl_app_path+"\n")
    sys.stderr.write("\tdbs path: "+gmap_dbs_path+"\n")
    
    sys.stderr.write("HS-Blastn:\n")
    sys.stderr.write("\tapp path: "+hsblastn_app_path+"\n")
    sys.stderr.write("\tdbs path:"+hsblastn_dbs_path+"\n")
    
    sys.stderr.write("\nAuxiliar tools location:\n")
    sys.stderr.write("\tsplit_blast: "+split_blast_path+"\n")
    sys.stderr.write("\tgenmap: "+genmap_path+"\n")
    
    return

try:
    ## Argument parsing
    __usage = "usage: bmap_config.py"
    optParser = OptionParser(__usage)
    
    (options, arguments) = optParser.parse_args()
    
    sys.stderr.write("Warning: this command outputs to stderr.\n")
    
    sys.stderr.write("Command: "+" ".join(sys.argv)+"\n")
    
    ########## ARGUMENT DEFAULTS
    ## Read conf file
    app_abs_path = os.path.dirname(os.path.abspath(__file__))
    
    config_path_dict = read_paths(app_abs_path+"/paths.conf") # data_utils.read_paths
    __app_path = config_path_dict["app_path"]
    sys.stderr.write("\n")
    
    split_blast_path = __app_path+config_path_dict["split_blast_path"]
    genmap_path = __app_path+config_path_dict["genmap_path"]
    tmp_files_path = __app_path+config_path_dict["tmp_files_path"]
    
    blastn_app_path = config_path_dict["blastn_app_path"]
    gmap_app_path = config_path_dict["gmap_app_path"]
    gmapl_app_path = config_path_dict["gmapl_app_path"]
    hsblastn_app_path = config_path_dict["hsblastn_app_path"]
    
    blastn_dbs_path = config_path_dict["blastn_dbs_path"]
    gmap_dbs_path = config_path_dict["gmap_dbs_path"]
    hsblastn_dbs_path = config_path_dict["hsblastn_dbs_path"]
    
    sys.stderr.write("############# PATHS\n")
    _print_paths(blastn_app_path, gmap_app_path, gmapl_app_path, hsblastn_app_path, \
                 blastn_dbs_path, gmap_dbs_path, hsblastn_dbs_path, split_blast_path, genmap_path)
    sys.stderr.write("\n")
    
    # Databases
    sys.stderr.write("############# DATABASES\n\n")
    databases_conf_file = __app_path+DATABASES_CONF
    databases_config = DatabasesConfig(databases_conf_file, verbose = False)
    for database_id in databases_config.get_databases():
        database_name = databases_config.get_database_name(database_id)
        database_type = databases_config.get_database_type(database_id)
        sys.stderr.write("\tDB: "+database_name+" --> ID: "+database_id+", type: "+database_type+"\n")
    
    sys.stderr.write("\n")
    
    ## External databases
    sys.stderr.write("############# EXTERNAL DATABASES\n\n")
    # blastn
    databases_ids = databases_config.get_databases_ids() # set(databases_ids)
    other_dbs = set()
    num_found = 0
    first = True
    for db_filename in os.listdir(blastn_dbs_path):
        db_name = db_filename.split(".")[0]
        if (db_name not in databases_ids) and (db_name not in other_dbs):
            num_found += 1
            if first:
                sys.stderr.write("\tOther databases (can be used with align_external):\n")
                first = False
            other_dbs.add(db_name)
            
    if num_found == 0:
        sys.stderr.write("\t\t-- Blastn database: (none found)\n")
    else:
        sys.stderr.write("\t\t-- Blast databases: "+", ".join(other_dbs)+"\n")
    
    # gmap
    other_dbs = set()
    num_found = 0
    for db_filename in os.listdir(gmap_dbs_path):
        db_name = db_filename.split(".")[0]
        if (db_name not in databases_ids) and (db_name not in other_dbs):
            num_found += 1
            if first:
                sys.stderr.write("\tOther databases (can be used with align_external):\n")
                first = False
            other_dbs.add(db_name)
    
    if num_found == 0:
        sys.stderr.write("\t\t-- GMAP database: (none found)\n")
    else:
        sys.stderr.write("\t\t-- GMAP databases: "+", ".join(other_dbs)+"\n")
    
    # hs-blastn
    other_dbs = set()
    num_found = 0
    for db_filename in os.listdir(hsblastn_dbs_path):
        db_name = db_filename.split(".")[0]
        if (db_name not in databases_ids) and (db_name not in other_dbs):
            num_found += 1
            if first:
                sys.stderr.write("\tOther databases (can be used with align_external):\n")
                first = False
            other_dbs.add(db_name)
    
    if num_found == 0:
        sys.stderr.write("\t\t-- HS-Blastn database: (none found)\n")
    else:
        sys.stderr.write("\t\t-- HS-Blastn databases: "+", ".join(other_dbs)+"\n")
    
    sys.stderr.write("\n")
    
    # Genetic maps and associated genes
    sys.stderr.write("############# MAPS\n\n")
    maps_path = __app_path+config_path_dict["maps_path"]
    maps_dict = {}
    for map_filename in os.listdir(maps_path):
        maps_dict[map_filename] = maps_path+map_filename
    
    # Genes
    genes_files_dict = set()
    genes_path = __app_path+config_path_dict["genes_path"]
    for genes_filename in os.listdir(genes_path):
        if genes_filename.endswith("_genes.tab"):
            genes_files_dict.add(genes_filename[:genes_filename.find("_")])
    
    maps_conf_file = __app_path+MAPS_CONF
    maps_config = MapsConfig(maps_conf_file, verbose = False)
    #(maps_names, maps_ids) = load_conf(maps_conf_file, verbose = False) # data_utils.load_conf
    maps_ids = maps_config.get_maps_ids()
    
    for map_id in maps_ids:
        map_config = maps_config.get_map(map_id)
        map_name = maps_config.get_map_name(map_config)
        map_has_cm_pos = maps_config.get_map_has_cm_pos(map_config)
        map_has_bp_pos = maps_config.get_map_has_bp_pos(map_config)
        map_as_physical = maps_config.get_map_as_physical(map_config)
        map_is_hierarchical = maps_config.get_map_is_hierarchical(map_config)
        map_is_best_score = maps_config.get_map_is_best_score(map_config)
        map_db_list = maps_config.get_map_db_list(map_config)
        sys.stderr.write("\t-- "+map_name+" --> ID: "+map_id+\
                         "\n\t\tcM positions: "+str(map_has_cm_pos)+"\n\t\tbasepairs positions: "+str(map_has_bp_pos)+\
                        "\n\t\tis physical map: "+str(map_as_physical)+"\n\t\thierarchical search: "+str(map_is_hierarchical)+
                        "\n\t\tshow only best score: "+str(map_is_best_score)+"\n\t\tassociated DB list: "+",".join(map_db_list)+"\n")
        
        #map_databases = []
        #for map_filename in os.listdir(maps_dict[map_id]):
        #    if not map_filename.startswith(map_id): continue
        #    
        #    map_data = map_filename.split(".")
        #    map_databases.append(map_data[-1])
        #
        #sys.stderr.write("\t\tPositions for databases: "+",".join(sorted(map_databases))+"\n")
        #
        #for genes_file in genes_files_dict:
        #    if genes_file == map_id:
        #        sys.stderr.write("\t\tIt also has genes associated to map positions.\n")
    
    sys.stderr.write("\n")
    
    # Annotation
    sys.stderr.write("############# Annotation for genes with maps positions associated\n\n")
    annot_path = __app_path+config_path_dict["annot_path"]
    for annot_filename in os.listdir(annot_path):
        if annot_filename.startswith("."): continue
        sys.stderr.write("\t"+annot_filename+"\n")
    
    sys.stderr.write("\n")
    
    # Datasets
    datasets_path = __app_path+config_path_dict["datasets_path"]
    datasets_dict = {}
    for dataset_filename in os.listdir(datasets_path):
        datasets_dict[dataset_filename] = datasets_path+dataset_filename
        
    sys.stderr.write("############# DATASETS\n\n")
    datasets_conf_file = config_path_dict["app_path"]+DATASETS_CONF
    datasets_config = DatasetsConfig(datasets_conf_file, verbose = False)
    
    datasets_ids = datasets_config.get_datasets_ids()
    
    for dataset_id in datasets_ids: #enumerate(datasets_names.split(",")):
        dataset_config = datasets_config.get_dataset(dataset_id)
        dataset_name = datasets_config.get_dataset_name(dataset_config)
        dataset_type = datasets_config.get_dataset_type(dataset_config)
        sys.stderr.write("\t"+dataset_name+" --> ID: "+dataset_id+", type: "+dataset_type+"\n")
        
        dataset_has_genes = False
        dataset_databases = []
        dataset_maps = []
        for dataset_filename in os.listdir(datasets_dict[dataset_id]):
            
            if not dataset_filename.startswith(dataset_id): continue
            
            dataset_data = dataset_filename.split(".")
            
            if len(dataset_data) < 2: continue
            
            #if dataset_data[-2] == "genes":
            #    dataset_has_genes = True
            
            if dataset_data[-1] == "hits" and dataset_data[-2] in databases_ids:
                dataset_databases.append(dataset_data[-2])
            
            if dataset_data[-1] == "hits" and dataset_data[-2] in maps_ids:
                dataset_maps.append(dataset_data[-2])
        
        #sys.stderr.write("\t\tIt has hits to genes: "+str(dataset_has_genes)+"\n")
        sys.stderr.write("\t\tHits to databases: "+",".join(sorted(dataset_databases))+"\n")
        sys.stderr.write("\t\tHits to maps: "+",".join(sorted(dataset_maps))+"\n")
        sys.stderr.write("\n")
    
    sys.stderr.write("\n")

except m2pException as e:
    sys.stderr.write("\nbarleymap reports an error:\n")
    sys.stderr.write(str(e)+"\n")
    sys.stderr.write('If you can not solve it please contact compbio@eead.csic.es ('+\
                        'laboratory of computational biology at EEAD).\n')
    
except Exception as e:
    print e
    sys.stderr.write("\nERROR\n")
    sys.stderr.write('An error was detected. If you can not solve it please contact compbio@eead.csic.es ('+\
                                   'laboratory of computational biology at EEAD).\n')

sys.stderr.write("End.\n")

## END