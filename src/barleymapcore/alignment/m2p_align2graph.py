#!/usr/bin/env python
# -*- coding: utf-8 -*-

# m2p_align2graph.py is part of Barleymap.
# Copyright (C) 2013-2014  Carlos P Cantalapiedra.
# Copyright (C) 2025 Bruno Contreras Moreira and Joan Sarria
# (terms of use can be found within the distributed LICENSE file).

import sys, re, os
from subprocess import Popen, PIPE

from barleymapcore.alignment.GraphAlignmentResult import *
from barleymapcore.m2p_exception import m2pException

#from Aligners import SELECTION_BEST_SCORE, SELECTION_NONE

ALIGNER = "align2graph"
MAX_NUMBER_PATHS_PER_QUERY = 100

def __align2graph(align2graph_app_path, n_threads, threshold_id, threshold_cov, query_fasta_path, align2graph_dbs_path, db_name, verbose = False):

    results = []
    
    ###### Check that DB is available for this aligner
    dbpath = align2graph_dbs_path + "/" + db_name   
    dbpathfile = dbpath + ".bmap.yaml"
    sys.stderr.write("Checking database: "+dbpathfile+" DB exists for "+ALIGNER+".\n")
    
    if not (os.path.exists(dbpathfile) and os.path.isfile(dbpathfile)):
        raise m2pException("DB path "+dbpath+" for "+ALIGNER+" aligner NOT FOUND.")
    
    align2graph_thres_id = float(threshold_id) / 100.0
    align2graph_thres_cov = float(threshold_cov) / 100.0

    # build actual align2graph call 
    align2graph_cmd = "".join([align2graph_app_path, \
                   " --graph_yaml ", dbpathfile, \
                   " --cor ", str(n_threads), \
                   " --minident ", str(threshold_id), \
                   " --mincover ", str(threshold_cov), \
                   " --add_ranges ", \
                   " ",query_fasta_path,
                   ])
    
    print(align2graph_cmd)

    if verbose: sys.stderr.write("m2p_align2graph: Thresholds: ID="+str(align2graph_thres_id)+"; COV="+str(align2graph_thres_cov)+"\n")
    
    if verbose: sys.stderr.write("m2p_align2graph: Executing '"+align2graph_cmd+"'\n")
    
    retValue = 0
    FNULL = open(os.devnull, 'w')
    if verbose:
        p = Popen(align2graph_cmd, shell=True, stdout=PIPE, stderr=sys.stderr)
    else:
        p = Popen(align2graph_cmd, shell=True, stdout=PIPE, stderr=PIPE)
    
    com_list = p.communicate()
    output = com_list[0]
    output_err = com_list[1]
    retValue = p.returncode
    
    if retValue != 0:
        if verbose:
            raise Exception("m2p_align2graph: return != 0. "+align2graph_cmd+"\n"+str(output)+"\n")
        else:
            raise Exception("m2p_align2graph: return != 0. "+align2graph_cmd+"\nError: "+str(output_err)+"\n")
    
    else:
        if verbose: sys.stderr.write("m2p_align2graph: return value "+str(retValue)+"\n")

        [results.append(line) for line in output.strip().split("\n") if line != ""]

    return results


def __filter_align2graph_results(results, threshold_id, threshold_cov, db_name, verbose = False):
    
    filtered_results = []
    
    filter_dict = {}
    
    algorithm = "align2graph"
    
    for line in results:
   
        if not line.startswith("#"):

            #query ref_chr ref_start ref_end ref_strand 
            #genome chr start end strand ident cover multmaps graph_ranges
            # examples:
            #1420.2 . . . . MorexV3 chr1H 4920748 4921827 + 100.0 99.7 No .
            #1430.4 chr1H 134 356 + MorexV3 chr1H 094 827 + 100.0 99.5 No .

            [ query_id, ref_id, ref_start, ref_end, ref_strand, 
                subj_name,subj_id,subj_start,subj_end,subj_strand,
                subj_ident, subj_cover, subj_multmaps,
                graph_ranges ] = line.split("\t")

            if(ref_id == "."):
                # this is a query with no reference coords, so we skip it
                continue

            subj_score = (int(subj_end) - int(subj_start)) * (float(subj_ident) / 100)

            result_tuple = GraphAlignmentResult()

            result_tuple.create_from_attributes(
                query_id, ref_id, ref_start, ref_end, ref_strand, 
                subj_name, subj_id, subj_start, subj_end, subj_strand,
                subj_ident, subj_cover, subj_score, subj_multmaps,
                graph_ranges , db_name, algorithm)
                        
            filtered_results.append(result_tuple)
    
    return filtered_results


def get_best_score_hits(align2graph_app_path, n_threads, query_fasta_path, align2graph_dbs_path, db_name, \
             threshold_id, threshold_cov, verbose = False):
    results = []
    
    if verbose: sys.stderr.write("m2p_align2graph: "+query_fasta_path+" against "+db_name+"\n")
    
    results = __align2graph(align2graph_app_path, n_threads, threshold_id, threshold_cov, query_fasta_path,
                     align2graph_dbs_path, db_name, verbose)
    
    if verbose: sys.stderr.write("m2p_align2graph: raw results --> "+str(len(results))+"\n")
    if len(results)>0:
        results = __filter_align2graph_results(results, threshold_id, threshold_cov, db_name, verbose)
    if verbose: sys.stderr.write("m2p_align2graph: pass-filter results --> "+str(len(results))+"\n")
    #sys.stderr.write(str(results)+"\n")
    
    return results

##
