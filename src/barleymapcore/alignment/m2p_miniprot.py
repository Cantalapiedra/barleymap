#!/usr/bin/env python
# -*- coding: utf-8 -*-

# m2p_miniprot.py is part of Barleymap.
# Copyright (C)  2013-2014  Carlos P Cantalapiedra.
# Copyright (C) 2024 Bruno Contreras Moreira and Najla Ksouri
# (terms of use can be found within the distributed LICENSE file).

import sys, re, os
from subprocess import Popen, PIPE

from barleymapcore.alignment.AlignmentResult import *
from barleymapcore.m2p_exception import m2pException

#from Aligners import SELECTION_BEST_SCORE, SELECTION_NONE

ALIGNER = "MINIPROT"
MAX_NUMBER_PATHS_PER_QUERY = 100

def __miniprot(miniprot_app_path, n_threads, threshold_id, threshold_cov, query_fasta_path, miniprot_dbs_path, db_name, verbose = False):

    results = []
    
    ###### Check that DB is available for this aligner
    dbpath = miniprot_dbs_path + "/" + db_name
    dbpathfile = dbpath + ".mpi"
    sys.stderr.write("Checking database: "+dbpath+" DB exists for "+ALIGNER+".\n")
    
    if not (os.path.exists(dbpathfile) and os.path.isfile(dbpathfile)):
        raise m2pException("DB path "+dbpath+" for "+ALIGNER+" aligner NOT FOUND.")
    
    miniprot_thres_id = float(threshold_id) / 100.0
    miniprot_thres_cov = float(threshold_cov) / 100.0

    # build actual miniprot call 
    miniprot_cmd = "".join([miniprot_app_path, \
                   " ",dbpathfile,
                   " ",query_fasta_path,
                   " -t ", str(n_threads), \
                   " --gff --outc=", str(miniprot_thres_cov)])
    
    if verbose: sys.stderr.write("m2p_miniprot: Thresholds: ID="+str(miniprot_thres_id)+"; COV="+str(miniprot_thres_cov)+"\n")
    
    if verbose: sys.stderr.write("m2p_miniprot: Executing '"+miniprot_cmd+"'\n")
    
    retValue = 0
    FNULL = open(os.devnull, 'w')
    if verbose:
        p = Popen(miniprot_cmd, shell=True, stdout=PIPE, stderr=sys.stderr)
    else:
        p = Popen(miniprot_cmd, shell=True, stdout=PIPE, stderr=PIPE)
    
    com_list = p.communicate()
    output = com_list[0]
    output_err = com_list[1]
    retValue = p.returncode
    
    if retValue != 0:
        if verbose:
            raise Exception("m2p_miniprot: return != 0. "+miniprot_cmd+"\n"+str(output)+"\n")
        else:
            raise Exception("m2p_miniprot: return != 0. "+miniprot_cmd+"\nError: "+str(output_err)+"\n")
    
    else:
        if verbose: sys.stderr.write("m2p_miniprot: MINIPROT return value "+str(retValue)+"\n")

        [results.append(line) for line in output.strip().split("\n") if line != ""]

    return results


def __filter_miniprot_results(results, threshold_id, threshold_cov, db_name, verbose = False):

    filtered_results = []
    
    filter_dict = {}
   
    rank_regex = re.compile("Rank=(\d+);") 
    ident_regex = re.compile("Identity=([^;]+)")
    
    algorithm = "miniprot"
    
    for line in results:
    
        # https://lh3.github.io/miniprot/miniprot.html#9
        # ##PAF A0A4Y1QZC6_PRUDU 281 3 281 - NC_047651.1 26138581 13209470 13214284 834 834 0 AS:i:1141 ...
        # NC_047651.1 miniprot mRNA 13209468 13214284 1401 - . ID=MP000010;Rank=1;Identity=1.0000;Positive=1.0000;Target=A0A4Y1QZC6_PRUDU 4 281
	
        line_data = line.split("\t")
 
        # parse only PAF summary and mRNA features from GFF results,
        # coords in PAF are 0-based
        if line_data[0] == '##PAF':
            #sys.stderr.write("Line "+str(line)+"\n")
          
            query_id = line_data[1]
            query_len = int(line_data[2])
            qstart_pos = int(line_data[3])
            qend_pos = int(line_data[4])
            strand = line_data[5]
            subject_id = line_data[6]

            # read genome coords from GFF instead as these seem to include stop codon
            #local_position = int(line_data[8]) + 1 # PAF is 0-based
            #end_position = int(line_data[9])
 
        elif len(line_data) > 8 and line_data[2] == 'mRNA':
            #sys.stderr.write("Line "+str(line)+"\n")

            local_position = int(line_data[3])
            end_position = int(line_data[4])

            match = re.search(ident_regex, line)
            if match:
                align_ident = 100*float(match.group(1))
                
                if align_ident < threshold_id:
                    continue

                matchr = re.search(rank_regex, line)
                if matchr:
                    rank = int(matchr.group(1))

                    # For a given DB, keep always the best score
                    if rank == 1:
 
                        align_score = (qend_pos - qstart_pos) * (align_ident / 100)
                        query_cov = (qend_pos - qstart_pos) / query_len
                        
                        result_tuple = AlignmentResult()
                        result_tuple.create_from_attributes(query_id, subject_id,
                                                            align_ident, query_cov, align_score,
                                                            strand, qstart_pos, qend_pos, local_position, 
                                                            end_position, db_name, algorithm)
                        
                        filtered_results.append(result_tuple)
    
    return filtered_results


def get_best_score_hits(miniprot_app_path, n_threads, query_fasta_path, miniprot_dbs_path, db_name, \
             threshold_id, threshold_cov, verbose = False):
    results = []
    
    if verbose: sys.stderr.write("m2p_miniprot: "+query_fasta_path+" against "+db_name+"\n")
    
    results = __miniprot(miniprot_app_path, n_threads, threshold_id, threshold_cov, query_fasta_path,
                     miniprot_dbs_path, db_name, verbose)
    
    if verbose: sys.stderr.write("m2p_miniprot: raw results --> "+str(len(results))+"\n")
    if len(results)>0:
        results = __filter_miniprot_results(results, threshold_id, threshold_cov, db_name, verbose)
    if verbose: sys.stderr.write("m2p_miniprot: pass-filter results --> "+str(len(results))+"\n")
    #sys.stderr.write(str(results)+"\n")
    
    return results

##
