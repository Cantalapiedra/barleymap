#!/usr/bin/env python
# -*- coding: utf-8 -*-

# parse_gtf_file.py is part of Barleymap.
# Copyright (C) 2017 Carlos P Cantalapiedra.
# (terms of use can be found within the distributed LICENSE file).

###########################
## Script to parse GTF/GFF files.
###########################

import sys
import gzip

from barleymapcore.m2p_exception import m2pException
from barleymapcore.alignment.AlignmentResult import AlignmentResult

BED_SUBJECT_ID_COL = 0
BED_START_COL = 1
BED_END_COL = 2
BED_QUERY_ID_COL = 3

GTF_SUBJECT_ID_COL = 0
GTF_ORIGIN_COL = 1
GTF_TYPE_COL = 2
GTF_LOCAL_POSITION_COL = 3
GTF_END_POSITION_COL = 4
GTF_STRAND_COL = 6
GTF_GENE_ID_COL = 9
GTF_TRANSCRIPT_ID_COL = 11

GTF_TYPE_TRANSCRIPT = "transcript"
GTF_TYPE_GENE = "gene"

FILE_TYPE_GTF = "gtf"
FILE_TYPE_GFF3 = "gff3"

def parse_bed_file(bed_path, db_list):
    features = []
    #features = {}
    
    sys.stderr.write("\t\t\tparse_bed_file: start reading "+bed_path+"\n")
    
    fn_open = gzip.open if bed_path.endswith('.gz') else open
    
    for bed_line in fn_open(bed_path, 'r'):
        bed_data = bed_line.strip().split()
        
        alignment_result = __bed_create_alignment_result(bed_data, db_list)
        #query_id = alignment_result.get_query_id()
        
        #features[query_id] = alignment_result
        features.append(alignment_result)
    
    #return features.values()
    return features

# Creates the AlignmentResult objects used in parse_gtf_file
def __bed_create_alignment_result(bed_data, db_list):
    
    alignment_result = AlignmentResult()
    
    query_id = bed_data[BED_QUERY_ID_COL]
    subject_id = bed_data[BED_SUBJECT_ID_COL]
    start_pos = bed_data[BED_START_COL]
    end_pos = bed_data[BED_END_COL]
    
    alignment_result.set_query_id(query_id)
    alignment_result.set_subject_id(subject_id)
    alignment_result.set_local_position(start_pos)
    alignment_result.set_end_position(end_pos)
    alignment_result.set_db_id(",".join(db_list))
    alignment_result.set_algorithm("BEDfile")
    #alignment_result.set_strand("")
    
    return alignment_result

# Returns a list of AlignmentResults
# created from the positions found in the GTF/GFF file
def parse_gtf_file(gtf_path, db_list, feature_type = GTF_TYPE_TRANSCRIPT, file_type = FILE_TYPE_GTF):
    features = {}
    
    sys.stderr.write("\t\t\tparse_gtf_file: start reading "+gtf_path+"\n")
    
    fn_open = gzip.open if gtf_path.endswith('.gz') else open
    
    for gtf_line in fn_open(gtf_path, 'r'):
        gtf_data = gtf_line.strip().split()
        gtf_type = gtf_data[GTF_TYPE_COL]
        
        if gtf_type == feature_type:
            alignment_result = __create_alignment_result(gtf_data, db_list, feature_type, file_type)
            query_id = alignment_result.get_query_id()
            
            # If exists already, update positions to keep the
            # broadest interval as possible
            if query_id in features:
                prev_result = features[query_id]
                local_pos = alignment_result.get_local_position()
                end_pos = alignment_result.get_end_position()
                prev_local_pos = prev_result.get_local_position()
                prev_end_pos = prev_result.get_end_position()
                
                if local_pos < prev_local_pos:
                    prev_result.set_local_position(local_pos)
                
                if end_pos > prev_end_pos:
                    prev_result.set_end_position(end_pos)
                
            else:
                features[query_id] = alignment_result
    
    sys.stderr.write("\t\t\tparse_gtf_file: finished reading a total "+str(len(features))+" of type "+str(feature_type)+"\n")
    
    return features.values()

# Creates the AlignmentResult objects used in parse_gtf_file
def __create_alignment_result(gtf_data, db_list, feature_type, file_type):
    
    alignment_result = AlignmentResult()
    
    query_id = __process_id(gtf_data, feature_type, file_type)
    
    alignment_result.set_query_id(query_id)
    alignment_result.set_subject_id(gtf_data[GTF_SUBJECT_ID_COL])
    alignment_result.set_strand(gtf_data[GTF_STRAND_COL])
    alignment_result.set_local_position(gtf_data[GTF_LOCAL_POSITION_COL])
    alignment_result.set_end_position(gtf_data[GTF_END_POSITION_COL])
    alignment_result.set_db_id(",".join(db_list))
    alignment_result.set_algorithm("GTF:"+gtf_data[GTF_ORIGIN_COL])
    
    return alignment_result

# Post-processing of ID field in GTF/GFF file
# to leave it as a plain text ID
def __process_id(gtf_data, feature_type, file_type):
    new_id = ""
    
    if feature_type == GTF_TYPE_TRANSCRIPT:
        new_id = gtf_data[GTF_TRANSCRIPT_ID_COL]
        
    elif feature_type == GTF_TYPE_GENE:
        new_id = gtf_data[GTF_GENE_ID_COL]
    else:
        raise m2pException("Unrecognized GTF type "+str(feature_type)+".")
    
    if file_type == FILE_TYPE_GTF:
        new_id = new_id.translate(None, '";') # Remove " and ; from the string
        
    elif file_type == FILE_TYPE_GFF3:
        raise m2pException("GFF3 file type is not supported yet.")
    else:
        raise m2pException("Unrecognized file type "+file_type+".")
    
    return new_id

## END