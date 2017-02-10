#!/usr/bin/env python
# -*- coding: utf-8 -*-

# bmap_build_datasets.py is part of Barleymap.
# Copyright (C)  2017  Carlos P Cantalapiedra.
# (terms of use can be found within the distributed LICENSE file).

###########################
## Script to show the configuration data of Barleymap.
###########################

import sys, os, traceback
from subprocess import Popen, PIPE
from optparse import OptionParser

from barleymapcore.m2p_exception import m2pException
from barleymapcore.db.DatasetsConfig import DatasetsConfig
from barleymapcore.db.ConfigBase import ConfigBase
from barleymapcore.db.PathsConfig import PathsConfig
from barleymapcore.db.MapsConfig import MapsConfig
from barleymapcore.maps.MapMarkers import MapMarkers
from barleymapcore.output.OutputFacade import OutputFacade
from barleymapcore.utils.parse_gtf_file import parse_gtf_file, parse_bed_file
from barleymapcore.utils.data_utils import read_paths

_SCRIPT = os.path.basename(__file__)

DEFAULT_THRES_ID = 98.0
DEFAULT_THRES_COV = 95.0
DEFAULT_N_THREADS = 1
DEFAULT_ALIGNER = "gmap"

def __features_to_map_file(features, maps_path, map_config, map_output_path, verbose_param):
    
    multiple_param = True
    
    mapMarkers = MapMarkers(maps_path, map_config, verbose = verbose_param)
    
    unaligned = [] # Better this than None
    mapMarkers.create_map(features, unaligned, map_config.get_default_sort_by(), multiple_param)
    
    mapping_results = mapMarkers.get_mapping_results()
    
    sys.stderr.write("Mapped results "+str(len(mapping_results.get_mapped()))+"\n")
    
    map_output = open(map_output_path, 'w')
    try:
        
        outputPrinter = OutputFacade.get_expanded_printer(map_output, verbose = verbose_param,
                                                          beauty_nums = False, show_headers = True)
        
        outputPrinter.print_map(mapping_results, map_config, multiple_param)
        
    except Exception as e:
        raise e
    finally:
        map_output.close()
    
    return

def __write_command(map_name, file_path, output_path, threads):
    cmd = "bmap_align"
    raw_numbers = "-f"
    aligner = "--aligner="+DEFAULT_ALIGNER
    thres_id = "--thres-id="+str(DEFAULT_THRES_ID)
    thres_cov = "--thres-cov="+str(DEFAULT_THRES_COV)
    _threads = "--threads="+str(threads)
    maps = "--maps="+map_name
    show_multiple = "-k"
    best_score = "-b"
    out = "> "+output_path
    err = "2> "+output_path+".err"
    
    command = " ".join([cmd, raw_numbers, aligner, thres_id, thres_cov,
                        _threads, maps, show_multiple, best_score, file_path, out, err])
    
    return command

def __run_command(cmd):
    
    sys.stderr.write(_SCRIPT+": running command:\n")
    sys.stderr.write("\t"+cmd+"\n")
    #p = Popen(cmd, shell=True, stdout=PIPE, stderr=sys.stderr)
    p = Popen(cmd, shell=True)
    com_list = p.communicate()
    retValue = p.returncode
    
    if retValue != 0: raise m2pException(_SCRIPT+": return != 0. "+cmd+"\n")
    
    sys.stderr.write(_SCRIPT+": return value "+str(retValue)+"\n")
    
    return

##########################

try:
    ## Argument parsing
    __usage = "usage: "+_SCRIPT
    optParser = OptionParser(__usage)
    
    optParser.add_option('--threads', action='store', dest='n_threads', type='string',
                    help='Number of threads to perform alignments (default '+str(DEFAULT_N_THREADS)+').')
    
    optParser.add_option('-v', '--verbose', action='store_true', dest='verbose', help='More information printed.')
    
    (options, arguments) = optParser.parse_args()
    
    if options.verbose: verbose_param = True
    else: verbose_param = False
    
    if verbose_param: sys.stderr.write("Command: "+" ".join(sys.argv)+"\n")
    
    # Num threads
    if options.n_threads: n_threads = int(options.n_threads)
    else: n_threads = DEFAULT_N_THREADS
    
    ## Read conf file
    app_abs_path = os.path.dirname(os.path.abspath(__file__))+"/"
    
    paths_config = PathsConfig(app_abs_path) # data_utils.read_paths
    
    # App path
    __app_path = paths_config.get_app_path()
    
    # Datasets path
    datasets_path = paths_config.get_datasets_path()
    
    # Datasets configuration file
    datasets_conf_file = __app_path+ConfigBase.DATASETS_CONF
    
    sys.stderr.write(_SCRIPT+": loading configuration file "+datasets_conf_file+"\n")
    
    datasets_config = DatasetsConfig(datasets_conf_file, verbose = verbose_param)
    
    datasets = datasets_config.get_datasets()
    datasets_list = datasets_config.get_datasets_list()
    
    datasets_dict = {}
    
    for dataset_id in datasets_list: #enumerate(datasets_names.split(",")):
        
        dataset_config = datasets_config.get_dataset_config(dataset_id)
        dataset_name = dataset_config.get_dataset_name()
        dataset_type = dataset_config.get_dataset_type()
        dataset_file_path = dataset_config.get_file_path()
        dataset_file_type = dataset_config.get_file_type()
        dataset_db_list = dataset_config.get_db_list()
        dataset_synonyms = dataset_config.get_synonyms()
        
        sys.stdout.write("\n")
        sys.stdout.write(_SCRIPT+": dataset: "+dataset_name+"\n")
        
        ### This is the directory to be created to store the
        ### data from this dataset
        dataset_path = datasets_path+dataset_id+"/"
        
        sys.stderr.write("\tdataset path: "+dataset_path+"\n")
        
        # If the path already exists, do not overwrite
        if os.path.exists(dataset_path):
            sys.stdout.write("\t\tPath "+dataset_path+" for dataset "+dataset_name+" already exists.\n"+\
                             "\t\tPlease, remove before re-building the dataset data.\n")
            continue # next dataset
        
        ########### CREATE MAPPINGS
        ###########
        ### 1) FASTA FILES
        ### bmap_align dataset_file_path maps > dataset_path/dataset_id.map
        if dataset_file_type == DatasetsConfig.FILE_TYPE_FNA:
            
            ### Create the new directory
            sys.stderr.write("\tA new directory "+dataset_path+" will be created.\n")
            os.mkdir(dataset_path)
            
            maps_conf_file = __app_path+ConfigBase.MAPS_CONF
            maps_config = MapsConfig(maps_conf_file, verbose = verbose_param)
            
            # align to all the maps
            if (len(dataset_db_list)==1) and (dataset_db_list[0] == DatasetsConfig.DATABASES_ANY):
                
                for map_id in maps_config.get_maps():
                    
                    map_config = maps_config.get_map_config(map_id)
                    map_name = map_config.get_name()
                    map_dir = map_config.get_map_dir()
                    dataset_mapping_path = dataset_path+dataset_id+"."+map_dir
                    
                    sys.stderr.write("\tMap: "+map_name+"\n")
                    sys.stderr.write("\t\toutput file "+dataset_mapping_path+"\n")
                    
                    command = __write_command(map_name, dataset_file_path, dataset_mapping_path, n_threads)
                    
                    __run_command(command)
                
            # align to maps which are associated to databases also associated to this dataset
            else:
                
                for map_id in maps_config.get_maps():
                    
                    map_config = maps_config.get_map_config(map_id)
                    map_db_list = map_config.get_db_list()
                    
                    common_dbs = filter(lambda x: x in dataset_db_list, map_db_list)
                    # refactor to: set(map_db_lis).intersection(dataset_db_list)
                    
                    if len(common_dbs)>0:
                        
                        map_name = map_config.get_name()
                        map_dir = map_config.get_map_dir()
                        dataset_mapping_path = dataset_path+dataset_id+"."+map_dir
                        
                        sys.stderr.write("\tMap: "+map_name+"\n")
                        sys.stderr.write("\t\toutput file "+dataset_mapping_path+"\n")
                        
                        command = __write_command(map_name, dataset_file_path, dataset_mapping_path, n_threads)
                        
                        __run_command(command)
            
            sys.stdout.write(_SCRIPT+": dataset "+dataset_name+" with id "+dataset_id+" created.\n")
        
        ### 2) GTF FILES
        ###
        elif dataset_file_type == DatasetsConfig.FILE_TYPE_GTF:
            
            ### Create the new directory
            sys.stderr.write("\tA new directory "+dataset_path+" will be created.\n")
            os.mkdir(dataset_path)
            
            maps_conf_file = __app_path+ConfigBase.MAPS_CONF
            maps_config = MapsConfig(maps_conf_file, verbose = verbose_param)
            
            # align to all the maps
            if (len(dataset_db_list)==1) and (dataset_db_list[0] == DatasetsConfig.DATABASES_ANY):
                
                raise m2pException("GTF files have to be associated to a single database in datasets configuration.")
                
            # align to maps which are associated to databases also associated to this dataset
            else:
                
                features = parse_gtf_file(dataset_file_path, dataset_db_list, dataset_type, dataset_file_type) # barleymapcore.utils
                
                config_path_dict = read_paths(app_abs_path+"/paths.conf") # data_utils.read_paths
                __app_path = config_path_dict["app_path"]
                maps_path = __app_path+config_path_dict["maps_path"]
                
                for map_id in maps_config.get_maps():
                    
                    map_config = maps_config.get_map_config(map_id)
                    map_db_list = map_config.get_db_list()
                    
                    common_dbs = filter(lambda x: x in dataset_db_list, map_db_list)
                    # refactor to: set(map_db_lis).intersection(dataset_db_list)
                    
                    if len(common_dbs)>0:
                        
                        map_name = map_config.get_name()
                        map_dir = map_config.get_map_dir()
                        dataset_mapping_path = dataset_path+dataset_id+"."+map_dir
                        
                        sys.stderr.write("\tMap: "+map_name+"\n")
                        sys.stderr.write("\t\toutput file "+dataset_mapping_path+"\n")
                        
                        __features_to_map_file(features, maps_path, map_config, dataset_mapping_path, verbose_param)
            
            sys.stdout.write(_SCRIPT+": dataset "+dataset_name+" with id "+dataset_id+" created.\n")
        
        ### 3) BED files
        elif dataset_file_type == DatasetsConfig.FILE_TYPE_BED:
            
            ### Create the new directory
            sys.stderr.write("\tA new directory "+dataset_path+" will be created.\n")
            os.mkdir(dataset_path)
            
            maps_conf_file = __app_path+ConfigBase.MAPS_CONF
            maps_config = MapsConfig(maps_conf_file, verbose = verbose_param)
            
            # align to all the maps
            if (len(dataset_db_list)==1) and (dataset_db_list[0] == DatasetsConfig.DATABASES_ANY):
                
                raise m2pException("BED files have to be associated to a single database in datasets configuration.")
                
            # align to maps which are associated to databases also associated to this dataset
            else:
                
                features = parse_bed_file(dataset_file_path, dataset_db_list) # barleymapcore.utils
                
                config_path_dict = read_paths(app_abs_path+"/paths.conf") # data_utils.read_paths
                __app_path = config_path_dict["app_path"]
                maps_path = __app_path+config_path_dict["maps_path"]
                
                for map_id in maps_config.get_maps():
                    
                    map_config = maps_config.get_map_config(map_id)
                    map_db_list = map_config.get_db_list()
                    
                    common_dbs = filter(lambda x: x in dataset_db_list, map_db_list)
                    # refactor to: set(map_db_lis).intersection(dataset_db_list)
                    
                    if len(common_dbs)>0:
                        
                        map_name = map_config.get_name()
                        map_dir = map_config.get_map_dir()
                        dataset_mapping_path = dataset_path+dataset_id+"."+map_dir
                        
                        sys.stderr.write("\tMap: "+map_name+"\n")
                        sys.stderr.write("\t\toutput file "+dataset_mapping_path+"\n")
                        
                        __features_to_map_file(features, maps_path, map_config, dataset_mapping_path, verbose_param)
            
            sys.stdout.write(_SCRIPT+": dataset "+dataset_name+" with id "+dataset_id+" created.\n")
            
        ### 4) Others
        else:
            sys.stdout.write("Nothing to do with dataset file type "+dataset_file_type+"\n")

except m2pException as e:
    sys.stderr.write("\nbarleymap reports an error:\n")
    sys.stderr.write(str(e)+"\n")
    sys.stderr.write('If you can not solve it please contact compbio@eead.csic.es ('+\
                        'laboratory of computational biology at EEAD).\n')
    
except Exception as e:
    sys.stderr.write("\n")
    sys.stderr.write('An error was detected. If you can not solve it please contact compbio@eead.csic.es ('+\
                                   'laboratory of computational biology at EEAD).\n')
    sys.stderr.write("\n")
    traceback.print_exc(file=sys.stderr)

sys.stderr.write("\n")
sys.stderr.write(_SCRIPT+": Finished.\n")
sys.stderr.write("\n")

## END