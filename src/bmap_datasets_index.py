#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# bmap_datasets_index.py is part of Barleymap.
# Copyright (C) 2017 Carlos P Cantalapiedra
# (terms of use can be found within the distributed LICENSE file).

############################################
# This script allows to create a binary index
# of a text file based on the first field
############################################

import sys, os, traceback
import cPickle
#import json It seems json is slower than cPickle with protocol 2

file_to_index = sys.argv[1]
index_file = file_to_index+".idx"

index = {}

sys.stderr.write("File to index: "+str(file_to_index)+"\n")

## Create the dictionary
prev = False
#i=0
curr_byte = 0
sys.stderr.write("Indexing rows...\n")
with open(file_to_index, 'r') as f_i:
    #for i, line in enumerate(f_i):
    while True:
        line = f_i.readline()
        if not line: break
        
        if line.startswith((">", "#")):
            #i+=1
            continue
        
        line_data = line.strip().split("\t")
        
        # Assign the previous bytes
        index[line_data[0]] = curr_byte
        # Obtain bytes for the next line
        curr_byte = f_i.tell()
        
        #if (i+1) % 10000 == 0:
        #    sys.stderr.write("lines indexed "+str(i+1)+"\n")
        
        #i+=1
    
sys.stderr.write("Final lines in index "+str(len(index))+"\n")

# example of how to read using bytes
#with open(file_to_index, 'r') as f_i:
#    f_i.seek(0)
#    line = f_i.readline()
#    sys.stderr.write("Line: "+str(line)+"\n")
    
sys.stderr.write("Writing the index to "+index_file+"...\n")

## Serialize the dictionary
with open(index_file, 'w') as index_f:
    cPickle.dump(index, index_f, protocol = 2)
    #json.dump(index, index_f)

sys.stderr.write("Loading the index to "+index_file+"...\n")
with open(index_file, 'r') as index_f:
    cPickle.load(index_f)
    #json.load(index_f)

sys.stderr.write("finished indexing "+file_to_index+" to "+index_file+"\n")

## END
