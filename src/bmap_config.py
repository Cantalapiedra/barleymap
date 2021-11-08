#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# check_config.py is part of Barleymap.
# Copyright (C)  2013-2014  Carlos P Cantalapiedra.
# Copyright (C)  2016-2017  Carlos P Cantalapiedra.
# (terms of use can be found within the distributed LICENSE file).

###########################
## Script to show the configuration data of Barleymap.
###########################

import sys, os
from optparse import OptionParser
from barleymapcore.m2p_exception import m2pException

from barleymapcore.db.ConfigBase import ConfigBase
from barleymapcore.db.PathsConfig import PathsConfig

from barleymapcore.db.DatabasesConfig import DatabasesConfig
from barleymapcore.db.DatasetsConfig import DatasetsConfig
from barleymapcore.db.MapsConfig import MapsConfig
from barleymapcore.db.DatasetsAnnotation import DatasetsAnnotation
from barleymapcore.db.AnnotationTypes import AnnotationTypes

from barleymapcore.utils.data_utils import read_paths

DATABASES_CONF = ConfigBase.DATABASES_CONF
DATASETS_CONF = ConfigBase.DATASETS_CONF
MAPS_CONF = ConfigBase.MAPS_CONF
DATASETS_ANNOTATION_CONF = ConfigBase.DATASETS_ANNOTATION_CONF
ANNOTATION_TYPES_CONF = ConfigBase.ANNOTATION_TYPES_CONF

def _print_paths(blastn_app_path, gmap_app_path, gmapl_app_path, hsblastn_app_path, \
                 blastn_dbs_path, gmap_dbs_path, hsblastn_dbs_path, \
                 split_blast_path, genmap_path, tmp_files_path):
    
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
    
    sys.stderr.write("\nTemp. files path:\n")
    sys.stderr.write("\t"+tmp_files_path+"\n")
    
    return

def _print_ext_databases(dbs_path, num_found, dbs_found):
    if num_found == 0:
        sys.stderr.write("No additional databases were found in "+dbs_path+".\n\n")
    else:
        sys.stderr.write("Additional databases found in "+dbs_path+":\n\t"+"\n\t".join(dbs_found)+"\n\n")
    
    return

try:
    ## Argument parsing
    __usage = "usage: bmap_config.py"
    optParser = OptionParser(__usage)
    
    (options, arguments) = optParser.parse_args()
    
    sys.stdout.write("Warning: this command outputs to stderr.\n")
    
    sys.stderr.write("Command: "+" ".join(sys.argv)+"\n")
    
    ################################ Paths Configuration ###############################
    ####################################################################################
    ## Read conf file
    app_abs_path = os.path.dirname(os.path.abspath(__file__))
    
    #paths_config = PathsConfig(app_abs_path, verbose = False)
    paths_config = PathsConfig()
    paths_config.load_config(app_abs_path)
    __app_path = paths_config.get_app_path()
    
    split_blast_path = paths_config.get_split_blast_path()#__app_path+config_path_dict["split_blast_path"]
    genmap_path = paths_config.get_genmap_path()#__app_path+config_path_dict["genmap_path"]
    tmp_files_path = paths_config.get_tmp_files_path()#__app_path+config_path_dict["tmp_files_path"]
    
    blastn_app_path = paths_config.get_blastn_app_path()#config_path_dict["blastn_app_path"]
    gmap_app_path = paths_config.get_gmap_app_path()#config_path_dict["gmap_app_path"]
    gmapl_app_path = paths_config.get_gmapl_app_path()#config_path_dict["gmapl_app_path"]
    hsblastn_app_path = paths_config.get_hsblastn_app_path()#config_path_dict["hsblastn_app_path"]
    
    blastn_dbs_path = paths_config.get_blastn_dbs_path()#config_path_dict["blastn_dbs_path"]
    gmap_dbs_path = paths_config.get_gmap_dbs_path()#config_path_dict["gmap_dbs_path"]
    hsblastn_dbs_path = paths_config.get_hsblastn_dbs_path()#config_path_dict["hsblastn_dbs_path"]
    
    sys.stderr.write("\n")
    sys.stderr.write("############# PATHS\n")
    _print_paths(blastn_app_path, gmap_app_path, gmapl_app_path, hsblastn_app_path,
                 blastn_dbs_path, gmap_dbs_path, hsblastn_dbs_path,
                 split_blast_path, genmap_path, tmp_files_path)
    sys.stderr.write("\n")
    
    ############################ Databases configuration #################################
    ######################################################################################
    
    ############### Configured databases
    ###############
    
    sys.stderr.write("############# DATABASES\n\n")
    databases_conf_file = __app_path+DATABASES_CONF
    databases_config = DatabasesConfig(databases_conf_file, verbose = False)
    for database_id in databases_config.get_databases():
        database_name = databases_config.get_database_name(database_id)
        database_type = databases_config.get_database_type(database_id)
        sys.stderr.write("DB: "+database_name+" --> ID: "+database_id+", type: "+database_type+"\n")
    
    sys.stderr.write("\n")
    
    ############## External databases
    ##############
    
    # In blastn DBs path
    databases_ids = databases_config.get_databases_ids() # set(databases_ids)
    other_dbs = set()
    num_found = 0
    first = True
    for db_filename in os.listdir(blastn_dbs_path):
        db_name = db_filename.split(".")[0]
        if (db_name not in databases_ids) and (db_name not in other_dbs):
            num_found += 1
            if first:
                sys.stderr.write("############# EXTERNAL DATABASES\n\n")
                first = False
            other_dbs.add(db_name)
    
    _print_ext_databases(blastn_dbs_path, num_found, other_dbs)
    
    # In gmap DBs path
    other_dbs = set()
    num_found = 0
    for db_filename in os.listdir(gmap_dbs_path):
        db_name = db_filename.split(".")[0]
        if (db_name not in databases_ids) and (db_name not in other_dbs):
            num_found += 1
            if first:
                sys.stderr.write("############# EXTERNAL DATABASES\n\n")
                first = False
            other_dbs.add(db_name)
    
    _print_ext_databases(gmap_dbs_path, num_found, other_dbs)
    
    # In hs-blastn DBs path
    other_dbs = set()
    num_found = 0
    for db_filename in os.listdir(hsblastn_dbs_path):
        db_name = db_filename.split(".")[0]
        if (db_name not in databases_ids) and (db_name not in other_dbs):
            num_found += 1
            if first:
                sys.stderr.write("############# EXTERNAL DATABASES\n\n")
                first = False
            other_dbs.add(db_name)
    
    _print_ext_databases(hsblastn_dbs_path, num_found, other_dbs)
    
    ########################## Maps configuration ##################################
    ################################################################################
    
    # Genetic maps and associated genes
    sys.stderr.write("############# MAPS\n\n")
    
    maps_path = paths_config.get_maps_path()#__app_path+config_path_dict["maps_path"]
    maps_conf_file = __app_path+MAPS_CONF
    maps_config = MapsConfig(maps_conf_file, verbose = False)
    
    maps_ids = maps_config.get_maps_ids()
    for map_id in maps_ids:
        map_config = maps_config.get_map_config(map_id)
        
        map_name = map_config.get_name()
        map_has_cm_pos = map_config.has_cm_pos()
        map_has_bp_pos = map_config.has_bp_pos()
        map_default_sort_by = map_config.get_default_sort_by()
        map_as_physical = map_config.as_physical()
        map_search_type = map_config.get_search_type()
        map_db_list = map_config.get_db_list()
        map_dir = map_config.get_map_dir()
        sys.stderr.write(""+map_name+" --> ID: "+map_id+", map path: "+maps_path+map_dir+"/"+\
                         "\n\t"+"it has cM positions: "+str(map_has_cm_pos)+\
                        "\n\t"+"it has bp positions: "+str(map_has_bp_pos)+\
                        "\n\t"+"default sort by: "+str(map_default_sort_by)+\
                        "\n\t"+"is physical map: "+str(map_as_physical)+\
                        "\n\t"+"search type: "+str(map_search_type)+
                        "\n\t"+"associated DB list: "+",".join(map_db_list)+"\n")
    
    sys.stderr.write("\n")
    
    ########################### Datasets configuration ##################################
    #####################################################################################
    
    # Datasets
    sys.stderr.write("############# DATASETS\n\n")
    
    datasets_path = paths_config.get_datasets_path()#__app_path+config_path_dict["maps_path"]
    datasets_conf_file = __app_path+DATASETS_CONF
    datasets_config = DatasetsConfig(datasets_conf_file, verbose = False)
    
    ds_annot_conf_file = __app_path+DATASETS_ANNOTATION_CONF
    ds_annot_config = DatasetsAnnotation(ds_annot_conf_file)
    
    annot_types_conf_file = __app_path+ANNOTATION_TYPES_CONF
    anntypes_config = AnnotationTypes(annot_types_conf_file)
    
    datasets_list = datasets_config.get_datasets_list()
    for dataset in datasets_list:
        dataset_config = datasets_config.get_dataset_config(dataset)
        ds_name = dataset_config.get_dataset_name()
        ds_type = dataset_config.get_dataset_type()
        ds_file_type = dataset_config.get_file_type()
        ds_db_list = dataset_config.get_db_list()
        ds_synonyms = dataset_config.get_synonyms()
        
        ds_paths = []
        if ds_file_type == DatasetsConfig.FILE_TYPE_MAP:
            for db_id in ds_db_list:
                for map_id in maps_ids:
                    map_config = maps_config.get_map_config(map_id)
                    map_db_list = map_config.get_db_list()
                    map_dir = map_config.get_map_dir()
                    if db_id in map_db_list:
                        ds_paths.append(maps_path+"/"+map_dir+"/"+map_dir+"."+db_id)
        else:
            ds_paths.append(dataset_config.get_file_path())
        
        sys.stderr.write(""+ds_name+" --> ID: "+dataset+\
                         "\n\t"+"Type: "+ds_type+\
                         "\n\t"+"File type: "+ds_file_type+", paths:\n\t\t"+"\n\t\t".join(ds_paths)+\
                         "\n\t"+"associated DBs: "+",".join(ds_db_list)+\
                         "\n\t"+"synonyms file: "+ds_synonyms+"\n")
        
        if ds_type == DatasetsConfig.DATASET_TYPE_GENE:
            ds_ann_dict = ds_annot_config.get_dsann()
            dataset_ds_ann_list = [ds_ann for ds_ann in ds_ann_dict if ds_ann_dict[ds_ann].get_dataset_id()==dataset]
            sys.stderr.write("\tGene Annotations\n")
            
            for dataset_ds_ann_id in dataset_ds_ann_list:
                ds_ann_config = ds_annot_config.get_dsann_config(dataset_ds_ann_id)
                ds_ann_name = ds_ann_config.get_name()
                ds_anntype_id = ds_ann_config.get_anntype_id()
                ds_ann_filename = ds_ann_config.get_filename()
                
                sys.stderr.write("\t\t"+ds_ann_name+" --> ID: "+dataset_ds_ann_id+\
                                 " --> annotation file: "+ds_ann_filename+\
                                 " --> type: "+ds_anntype_id+" ("+str(anntypes_config.get_anntype(ds_anntype_id))+")"+\
                                 "\n")
        
        
    
    
    sys.stderr.write("\n")

except m2pException as e:
    sys.stderr.write("\nbarleymap reports an error:\n")
    sys.stderr.write(str(e)+"\n")
    sys.stderr.write('If you can not solve it please contact compbio@eead.csic.es ('+\
                        'Computational and structural biology group at EEAD-CSIC).\n')
    
except Exception as e:
    print e
    sys.stderr.write("\nERROR\n")
    sys.stderr.write('An error was detected. If you can not solve it please contact compbio@eead.csic.es ('+\
                                   'Computational and structural biology group at EEAD-CSIC).\n')

sys.stderr.write("End.\n")

## END
