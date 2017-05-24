#!/usr/bin/env python
# -*- coding: utf-8 -*-

# alignment_utils.py is part of Barleymap.
# Copyright (C)  2013-2014  Carlos P Cantalapiedra.
# (terms of use can be found within the distributed LICENSE file).

import os, tempfile

def load_fasta_lengths(fasta_path):
    len_dict = {}
    
    currlen = 0
    for fasta_line in open(fasta_path, 'r'):
        if fasta_line.startswith(">"):
            if currlen > 0:
                len_dict[fasta_id] = currlen
            fasta_id = fasta_line[1:].strip()
            currlen = 0
        else:
            linelen = len(fasta_line.strip())
            currlen += linelen
    
    if currlen > 0:
        len_dict[fasta_id] = currlen
        currlen = 0
    
    return len_dict

def get_fasta_headers(fasta_path):
    fasta_headers = []
    
    for fasta_line in open(fasta_path, 'r'):
        if fasta_line.startswith(">"):
            fasta_headers.append(fasta_line[1:].strip())
    
    return fasta_headers

def filter_list(list_to_filter, filters_list):
    filtered_list = []
    
    # To ensure that only identifier (and no fasta comments) are compared:
    filters_set = set([a.split(" ")[0] for a in filters_list])
    list_short_headers = [a.split(" ")[0] for a in list_to_filter]
    
    for element in list_short_headers:
        
        if element not in filters_set:
            filtered_list.append(element)
    
    return filtered_list

def extract_fasta_headers(fasta_path, headers_list, tmp_files_dir):
    new_fasta_path = ""
    
    headers_set = set(headers_list)
    
    input_file = None
    try:
        (file_desc, new_fasta_path) = tempfile.mkstemp(suffix="_m2p_facade", dir=tmp_files_dir)
        input_file = os.fdopen(file_desc, 'w')
        
        seq_found = False
        fasta_headers = get_fasta_headers(fasta_path)
        for line in open(fasta_path):
            if line.startswith(">"):
                seqid = line[1:].strip().split(" ")[0] # To ensure that only identifier (and no fasta comments) are compared:
                if seqid in headers_set:
                    seq_found = True
                    input_file.write(line)
                else:
                    seq_found = False
                    
            elif seq_found:
                input_file.write(line)
                
        input_file.close()
        
    except Exception:
        raise
    finally:
        if input_file:
            input_file.close()
    
    return new_fasta_path

## END