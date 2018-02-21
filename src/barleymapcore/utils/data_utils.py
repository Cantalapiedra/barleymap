#!/usr/bin/env python
# -*- coding: utf-8 -*-

# data_utils.py is part of Barleymap.
# Copyright (C)  2013-2014  Carlos P Cantalapiedra.
# (terms of use can be found within the distributed LICENSE file).

import sys

from barleymapcore.m2p_exception import m2pException

def read_paths(config_file_path, verbose = False): # TODO pass this to utils package
    config_path_dict = {}
    
    if verbose: sys.stderr.write("Reading paths from config file...\n")
    
    for config_line in open(config_file_path, 'r'):
        if config_line.startswith("#") or not config_line.strip(): continue # line.strip() is False if is an empty line "^$"
        config_data = config_line.strip().split(" ")
        config_path_dict[config_data[0]] = config_data[1]
    
    if verbose: sys.stderr.write("Config file read.\n")
    
    return config_path_dict

def load_conf(conf_file, verbose = False):
    conf_rows = []
    
    if verbose: sys.stderr.write("Loading configuration file "+conf_file+"...\n")
    
    try:
        for line in open(conf_file, 'r'):
            if line.startswith("#") or not line.strip(): continue # line.strip() is False if is an empty line "^$"
            if verbose: sys.stderr.write("\t conf line: "+line.strip()+"\n")
            
            line_data = line.strip().split(" ")
            
            conf_rows.append(line_data) 
    
    except Exception:
        raise m2pException("Error loading configuration file "+conf_file+".")
    
    return conf_rows

## END