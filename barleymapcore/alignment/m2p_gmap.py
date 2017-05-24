#!/usr/bin/env python
# -*- coding: utf-8 -*-

# m2p_gmap.py is part of Barleymap.
# Copyright (C)  2013-2014  Carlos P Cantalapiedra.
# (terms of use can be found within the distributed LICENSE file).

import sys, re, os
from subprocess import Popen, PIPE

from AlignmentResult import *
from barleymapcore.m2p_exception import m2pException

#from Aligners import SELECTION_BEST_SCORE, SELECTION_NONE

ALIGNER = "GMAP"
MAX_NUMBER_PATHS_PER_QUERY = 100

def __gmap(gmap_app_path, n_threads, threshold_id, threshold_cov, query_fasta_path, gmap_dbs_path, db_name, verbose = False):
    
    # CPCantalapiedra 201701
    ###### Check that DB is available for this aligner
    dbpath = gmap_dbs_path + "/" + db_name
    dbpathfile = dbpath + "/" + db_name + ".ref153positions"
    sys.stderr.write("Checking database: "+dbpath+" DB exists for "+ALIGNER+".\n")
    
    if not (os.path.exists(dbpathfile) and os.path.isfile(dbpathfile)):
        raise m2pException("DB path "+dbpath+" for "+ALIGNER+" aligner NOT FOUND.")
    
    # GMAP
    __command = "".join([gmap_app_path, \
                " -t ", str(n_threads), \
                " -B 0 -n ", str(MAX_NUMBER_PATHS_PER_QUERY)])
    
    gmap_thres_id = float(threshold_id) / 100.0
    gmap_thres_cov = float(threshold_cov) / 100.0
    
    if verbose: sys.stderr.write("m2p_gmap: Thresholds: ID="+str(gmap_thres_id)+"; COV="+str(gmap_thres_cov)+"\n")
    
    __filter_id = "--min-identity="+str(gmap_thres_id)
    __filter_cov = "--min-trimmed-coverage="+str(gmap_thres_cov)
    __db = "".join([" -d ", db_name])
    __db_dir = "".join([" -D ", gmap_dbs_path])
    
    gmap_cmd = " ".join([__command, __filter_id, __filter_cov, __db, __db_dir, query_fasta_path])
    
    if verbose: sys.stderr.write("m2p_gmap: Executing '"+gmap_cmd+"'\n")
    
    retValue = 0
    FNULL = open(os.devnull, 'w')
    if verbose:
        p = Popen(gmap_cmd, shell=True, stdout=PIPE, stderr=sys.stderr)
    else:
        p = Popen(gmap_cmd, shell=True, stdout=PIPE, stderr=PIPE)
    
    com_list = p.communicate()
    output = com_list[0]
    output_err = com_list[1]
    retValue = p.returncode
    
    if retValue != 0:
        if verbose:
            raise Exception("m2p_gmap: return != 0. "+gmap_cmd+"\n")
        else:
            raise Exception("m2p_gmap: return != 0. "+gmap_cmd+"\nError: "+str(output_err)+"\n")
    
    if verbose: sys.stderr.write("m2p_gmap: GMAP return value "+str(retValue)+"\n"+str(output_err)+"\n")
    
    results = __compress(output, db_name)
    
    #print "M2PGMAP***********************"
    #for result in results:
    #    print result
    
    return results

# NOTE that this method could create an different format
# but that has been created like this for further compatibility with
# existing GMAP -Z (compressed) format.
def __compress(output, db_name):
    
    compressed = []
    
    new_line = None
    query_id = None
    is_chimera = False
    
    numb_exp = re.compile("[0-9]+\.[0-9]")
    direction_exp = re.compile("cDNA direction: (sense|antisense|indeterminate)")
    strand_exp = re.compile("([+-]) strand")
    
    for output_line in output.strip().split("\n"):
        
        ##print "M2PGMAP***********************"
        #sys.stdout.write(str(output_line)+"\n")
        
        ## Header of query
        if output_line.startswith(">"):
            if query_id != None:
                prev_query_id = query_id
            else:
                prev_query_id = output_line
            query_id = output_line
        
        ## Data of query
        else:
            
            if "chimera" in output_line:
                compressed.append("chimera")
                is_chimera = True
                query_id = prev_query_id
                continue
            elif output_line.startswith("Paths "):
                is_chimera = False
                if "Paths (0)" in output_line:
                    query_id = prev_query_id
                    continue
                
            elif is_chimera:
                continue
            else:
                if "cDNA direction" in output_line:
                    # which is faster
                    re_obj = re.search(direction_exp, output_line).group(1)
                    direction = str(re_obj)
                    # or
                    #direction = str(output_line.strip().split(" ")[2])
                
                if "Genomic pos" in output_line:
                    re_obj = re.search(strand_exp, output_line).group(1)
                    strand = str(re_obj)
                    #strand = str(output_line.strip().split(" ")[3][1])
                
                if "Trimmed coverage" in output_line:
                    re_obj = re.search(numb_exp, output_line).group(0)
                    query_cov = float(re_obj)
                    #query_cov = float(output_line.strip().split(" ")[2])
                
                if "Percent identity" in output_line:
                    re_obj = re.search(numb_exp, output_line).group(0)
                    identity = float(re_obj)
                    #identity = float(output_line.strip().split(" ")[2])
                    
                if "Path" in output_line:
                    
                    ## Add data of the previous line
                    #sys.stderr.write("New line "+str(new_line)+"\n")
                    
                    if new_line != None:
                        #sys.stderr.write("INTO NEW LINE "+str(new_line)+"\n")
                        
                        new_line.append(prev_query_id)
                        prev_query_id = query_id
                        
                        new_line.append(db_name)
                        new_line.append("0/0") # I dont need this field with path_number/total_paths
                        new_line.append("0") # I dont need either the query length
                        new_line.append("0") # Nor the exon number
                        new_line.append(str(query_cov))
                        new_line.append(str(identity))
                        new_line.append(str(qstart)+".."+str(qend))
                        new_line.append("0..0") # Whole genome GMAP coordinates
                        new_line.append(subject_id+":"+str(sstart)+".."+str(send))
                        new_line.append(str(strand))
                        new_line.append("dir:"+str(direction))
                        
                        #sys.stderr.write("Inserting new line: "+str(new_line)+"\n")
                        
                        compressed.append(" ".join(new_line))
                        
                        new_line = None
                    
                    new_line = []
                    path_line = output_line.strip().split(" ")
                    
                    qstart = path_line[3].split("..")[0]
                    qend = path_line[3].split("..")[1]
                    
                    subject_data = path_line[8].split(":")
                    subject_id = subject_data[0]
                    sstart = subject_data[1].split("..")[0].replace(",", "")
                    send = subject_data[1].split("..")[1].replace(",", "")
    
    ## Last alignment found
    if new_line != None:
        
        #sys.stderr.write("LAST new line "+str(new_line)+"\n")
        
        new_line.append(prev_query_id)
        prev_query_id = query_id
        
        new_line.append(db_name)
        new_line.append("0/0") # I dont need this field with path_number/total_paths
        new_line.append("0") # I dont need either the query length
        new_line.append("0") # Nor the exon number
        new_line.append(str(query_cov))
        new_line.append(str(identity))
        new_line.append(str(qstart)+".."+str(qend))
        new_line.append("0..0") # Whole genome GMAP coordinates
        new_line.append(subject_id+":"+str(sstart)+".."+str(send))
        new_line.append(str(strand))
        new_line.append("dir:"+str(direction))
        
        #sys.stderr.write("Inserting new line: "+str(new_line)+"\n")
        
        compressed.append(" ".join(new_line))
    
    #sys.stderr.write("Len results "+str(len(compressed))+"\n")
    
    return compressed

def __filter_gmap_results(results, threshold_id, threshold_cov, db_name, verbose = False):
    filtered_results = []
    
    chimera_num = 0 #chimera_dict = set([])
    filter_dict = {}
    
    #debug = True
    
    strand_exp = re.compile("([0-9]+)..([0-9]+)")
    
    algorithm = "gmap"
    
    for line in results:
        
        #sys.stderr.write("m2p_gmap Result "+str(line)+"\n")
        
        # Specific GMAP pre-filter: chimera results
        if line.find("chimera") != -1:
            #sys.stderr.write("GMAP chimera "+str([line.split(" ")[0][1:]])+"\n")
            chimera_num += 1 #chimera_dict.add(str([line.split(" ")[0][1:]]))
            continue
        
        line_data = line.split(" ")
        
        #sys.stderr.write("Line "+str(line)+"\n")
        #sys.stderr.write("Data "+str(line_data)+"\n")
        
        query_id = line_data[0][1:]
        subject_id = line_data[9].split(":")[0] # Because GMAP adding subject positions after subject name separated by ":" in compress output mode
        align_ident = float(line_data[6])
        query_cov = float(line_data[5])
        
        strand = line_data[10]
        
        strand = line_data[10]
        s_pos = re.search(strand_exp, line_data[9])
        
        if strand == "+":
            local_position = long(line_data[9].split(":")[1].split("..")[0])
            end_position = long(line_data[9].split(":")[1].split("..")[1])
            #local_position = long(s_pos.group(1))
        elif strand == "-":
            local_position = long(line_data[9].split(":")[1].split("..")[1])
            end_position = long(line_data[9].split(":")[1].split("..")[0])
            #local_position = long(s_pos.group(2))
        else:
            raise Exception("m2p_gmap: wrong strand "+str(strand)+".")
        
        #sys.stderr.write("Local position "+str(local_position)+"\n")
        
        query_positions = line_data[7].split("..")
        qstart_pos = query_positions[0]
        qend_pos = query_positions[1]
        align_score = (long(qend_pos) - long(qstart_pos)) * (align_ident / 100)
        #if query_id == "i_BK_02": debug = True
        #else: debug = False
        
        result_tuple = AlignmentResult()
        result_tuple.create_from_attributes(query_id, subject_id,
                                        align_ident, query_cov, align_score,
                                        strand, qstart_pos, qend_pos, local_position, end_position,
                                        db_name, algorithm)
        
        # For a given DB, keep always the best score
        #if selection == SELECTION_BEST_SCORE:
        if query_id in filter_dict:
            prev_max_scores = filter_dict[query_id]["max_scores"]
            
            new_max_score = True
            new_max_score_list = []
            new_query_list = []
            for i, max_score in enumerate(prev_max_scores):
                best_query = filter_dict[query_id]["query_list"][i]
                
                #print "m2p_gmap************************"
                #print str(max_score)+"-"+str(best_query)
                
                max_align_ident = max_score[0]
                max_query_cov = max_score[1]
                
                # If it is worse than at least one alignment, it will be discarded
                if (align_ident <= max_align_ident and query_cov < max_query_cov) \
                or (align_ident < max_align_ident and query_cov <= max_query_cov):
                    
                    new_max_score = False # The new alignment is definitely discarded
                    new_max_score_list.append(max_score)
                    new_query_list.append(best_query)
                
                # If it is equal as another, the existing one remains in the new list
                elif (align_ident == max_align_ident and query_cov == max_query_cov):
                    
                    new_max_score_list.append(max_score)
                    new_query_list.append(best_query)
                
                # If it is as good as another, but different
                elif (align_ident > max_align_ident and query_cov < max_query_cov) \
                or (align_ident < max_align_ident and query_cov > max_query_cov):
                    
                    new_max_score_list.append(max_score)
                    new_query_list.append(best_query)
                
                # If it is better than the other, the old one is not added to the new list
                elif (align_ident >= max_align_ident and query_cov > max_query_cov) \
                or (align_ident > max_align_ident and query_cov >= max_query_cov):
                    
                    pass#new_max_score_list.append((align_ident, query_cov))
                
                else:
                    raise Exception("m2p_gmap: unknown max score relation between alignments.")
            
            if new_max_score:
                new_max_score_list.append((align_ident, query_cov))
                new_query_list.append(result_tuple)
            
            # Update the max_scores list for this query
            filter_dict[query_id]["max_scores"] = new_max_score_list
            filter_dict[query_id]["query_list"] = new_query_list
            
        else:
            filter_dict[query_id] = {"query_list":[result_tuple], "max_scores":[(align_ident, query_cov)]}
        
    # Recover filtered results
    for query_id in filter_dict:
        for alignment_result in filter_dict[query_id]["query_list"]:
            filtered_results.append(alignment_result)
    
    if verbose: sys.stderr.write("m2p_gmap: number of chimeras found: "+str(chimera_num)+"\n")
    
    return filtered_results

def get_best_score_hits(gmap_app_path, n_threads, query_fasta_path, gmap_dbs_path, db_name, \
             threshold_id, threshold_cov, verbose = False):
    results = []
    
    if verbose: sys.stderr.write("m2p_gmap: "+query_fasta_path+" against "+db_name+"\n")
    
    results = __gmap(gmap_app_path, n_threads, threshold_id, threshold_cov, query_fasta_path,
                     gmap_dbs_path, db_name, verbose)
    
    if verbose: sys.stderr.write("m2p_gmap: raw results --> "+str(len(results))+"\n")
    if len(results)>0:
        results = __filter_gmap_results(results, threshold_id, threshold_cov, db_name, verbose)
    if verbose: sys.stderr.write("m2p_gmap: pass-filter results --> "+str(len(results))+"\n")
    #sys.stderr.write(str(results)+"\n")
    
    return results

##
