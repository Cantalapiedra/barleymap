#!/usr/bin/env python
# -*- coding: utf-8 -*-

# m2p_hsblastn.py is part of Barleymap.
# Copyright (C)  2017  Carlos P Cantalapiedra.
# (terms of use can be found within the distributed LICENSE file).

import sys, os
from subprocess import Popen, PIPE

from barleymapcore.utils.alignment_utils import load_fasta_lengths
from barleymapcore.m2p_exception import m2pException
from AlignmentResult import *

#from Aligners import SELECTION_BEST_SCORE, SELECTION_NONE

ALIGNER = "HS-Blastn"
ALIGN_QUERY = 0
ALIGN_SUBJECT = 1
ALIGN_PIDENT = 2
ALIGN_LENGTH = 3
ALIGN_QSTART = 6
ALIGN_QEND = 7
ALIGN_SSTART = 8
ALIGN_SEND = 9
ALIGN_SCORE = 11
# ALIGN_QLEN = there is no query len in HS-Blastn tabular results

def __hs_blast(hsblastn_app_path, n_threads, query_fasta_path, hsblastn_dbs_path, db_name, verbose = False):
    results = []
    
    # CPCantalapiedra 201701
    ###### Check that DB is available for this aligner
    dbpath = hsblastn_dbs_path + db_name
    dbpathfile = dbpath + ".bwt"
    sys.stderr.write("Checking database: "+dbpath+" DB exists for "+ALIGNER+".\n")
    
    if not (os.path.exists(dbpathfile) and os.path.isfile(dbpathfile)):
        raise m2pException("DB path "+dbpath+" for "+ALIGNER+" aligner NOT FOUND.")
    
    ###### HS-Blastn
    blast_command = " ".join([hsblastn_app_path, " align ", \
                            " -num_threads ", str(n_threads), \
                "-dust no ", \
                '-outfmt 6'])
                #'-outfmt \"6 qseqid qlen sseqid slen length qstart qend sstart send bitscore evalue pident mismatch gapopen\"'])
    
    blast_db = "".join(["-db ", dbpath]) # blast_db = "".join(["-db ", blast_dbs_path, db_name , ".fa"]) # 
    blast_query = " ".join(["-query ", query_fasta_path])
    #blast_cmd = " ".join([ResourcesMng.get_deploy_dir()+blast_command, blast_db, blast_query])
    blast_cmd = " ".join([blast_command, blast_db, blast_query])
    
    if verbose: sys.stderr.write(os.path.basename(__file__)+": Running '"+blast_cmd+"'\n")
    
    retValue = 0
    FNULL = open(os.devnull, 'w')
    if verbose:
        p = Popen(blast_cmd, shell=True, stdout=PIPE, stderr=sys.stderr)
    else:
        p = Popen(blast_cmd, shell=True, stdout=PIPE, stderr=PIPE)
    
    com_list = p.communicate()
    output = com_list[0]
    output_err = com_list[1]
    retValue = p.returncode
    
    if retValue != 0:
        if verbose:
            raise Exception(os.path.basename(__file__)+": HS-Blastn return != 0. "+blast_cmd+"\n"+str(output)+"\n")
        else:
            raise Exception(os.path.basename(__file__)+": HS-Blastn return != 0. "+blast_cmd+"\n"+str(output)+"\n"+str(output_err)+"\n")
    
    if "error" in output or "Error" in output or "ERROR" in output:
        sys.stderr.write("m2p_hs_blast: error in hs-blastn output. We will report 0 results for this alignment.\n")
        sys.stderr.write(output+"\n")
        sys.stderr.write(str(output_err)+"\n")
        results = []
    else:
        if verbose: sys.stderr.write(os.path.basename(__file__)+": HS-Blastn return value "+str(retValue)+"\n")
        
        [results.append(line) for line in output.strip().split("\n") if line != ""]
    
    return results

def __filter_blast_results(results, threshold_id, threshold_cov, db_name, qlen_dict, verbose = False):
    
    filtered_results = []
    
    # assert: if an int is passed to the method, the comparison fails
    thres_id = float(threshold_id)
    thres_cov = float(threshold_cov)
    
    filter_dict = {}
    
    algorithm = "hsblastn"
    
    for line in results:
        line_data = line.split("\t")
        
        # filter: based on identity
        align_ident = float(line_data[ALIGN_PIDENT])
        if align_ident < thres_id:
            continue
        
        # filter: based on query coverage of alignment
        align_len = int(line_data[ALIGN_LENGTH])
        
        query_id = line_data[ALIGN_QUERY]
        
        # HS-Blastn does not report the query length
        # so we obtain it from a previously set up dictionary
        query_len = qlen_dict[query_id]
        
        query_cov = (align_len/float(query_len))*100
        if query_cov < thres_cov:
            continue
        
        subject_id = line_data[ALIGN_SUBJECT]
        align_score = float(line_data[ALIGN_SCORE])
        
        # strand and local position
        if line_data[ALIGN_SSTART]>line_data[ALIGN_SEND]:
            strand = "-"
            local_position = long(line_data[ALIGN_SEND])
            end_position = long(line_data[ALIGN_SSTART])
        else:
            strand = "+"
            local_position = long(line_data[ALIGN_SSTART])
            end_position = long(line_data[ALIGN_SEND])
        
        qstart_pos = long(line_data[ALIGN_QSTART])
        qend_pos = long(line_data[ALIGN_QEND])
        
        result_tuple = AlignmentResult()
        result_tuple.create_from_attributes(query_id, subject_id,
                                        align_ident, query_cov, align_score,
                                        strand, qstart_pos, qend_pos, local_position, end_position,
                                        db_name, algorithm)
        
        # For a given DB, keep always the best score
        #if selection == SELECTION_BEST_SCORE:
        if query_id in filter_dict:
            prev_max_score = filter_dict[query_id]["max_score"]
            
            if align_score > prev_max_score:
                filter_dict[query_id]["query_list"] = [result_tuple]
                filter_dict[query_id]["max_score"] = align_score
                
            elif align_score == prev_max_score:
                filter_dict[query_id]["query_list"].append(result_tuple)
            #else:
            #    print "FILTERED"
        else:
            filter_dict[query_id] = {"query_list":[result_tuple], "max_score":align_score}
    
    # Recover filtered results
    for query_id in filter_dict:
        for alignment_result in filter_dict[query_id]["query_list"]:
            filtered_results.append(alignment_result)
    
    return filtered_results

def get_best_score_hits(hsblastn_app_path, n_threads, query_fasta_path, hsblastn_dbs_path, db_name, \
                        threshold_id, threshold_cov, verbose = False):
    
    if verbose: sys.stderr.write(os.path.basename(__file__)+": "+query_fasta_path+" against "+db_name+"\n")
    
    results = __hs_blast(hsblastn_app_path, n_threads, query_fasta_path, hsblastn_dbs_path, db_name, verbose)
    
    if verbose: sys.stderr.write(os.path.basename(__file__)+": raw results --> "+str(len(results))+"\n")
    
    if len(results)>0:
        qlen_dict = load_fasta_lengths(query_fasta_path)
        results = __filter_blast_results(results, threshold_id, threshold_cov, db_name, qlen_dict, verbose)
        
    if verbose: sys.stderr.write(os.path.basename(__file__)+": pass-filter results --> "+str(len(results))+"\n")
    #sys.stderr.write(str(len(results))+"\n")
    #sys.stderr.write(str(results)+"\n")
    
    return results