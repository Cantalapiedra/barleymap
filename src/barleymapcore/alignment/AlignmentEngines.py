#!/usr/bin/env python
# -*- coding: utf-8 -*-

# AlignmentEngines.py is part of Barleymap.
# Copyright (C)  2017  Carlos P Cantalapiedra.
# (terms of use can be found within the distributed LICENSE file).

from barleymapcore.m2p_exception import m2pException
from barleymapcore.db.MapsConfig import MapsConfig
from Aligners import *
from AlignmentResult import AlignmentResults

ALIGNMENT_TYPE_GREEDY = "greedy"
ALIGNMENT_TYPE_HIERARCHICAL = "hierarchical"
ALIGNMENT_TYPE_BEST_SCORE = "best_score"

class AlignmentEnginesFactory(object):
    @staticmethod
    def get_alignment_engine(search_type, aligner_list, paths_config, ref_type_param, n_threads, verbose):
        
        alignment_engine = None
        
        if search_type == ALIGNMENT_TYPE_GREEDY:
            
            alignment_engine = GreedyEngine(aligner_list, paths_config, ref_type_param, n_threads, verbose)
            
        elif search_type == ALIGNMENT_TYPE_HIERARCHICAL:
            
            alignment_engine = HierarchicalEngine(aligner_list, paths_config, ref_type_param, n_threads, verbose)
            
        elif search_type == ALIGNMENT_TYPE_BEST_SCORE:
            
            alignment_engine = BestScoreEngine(aligner_list, paths_config, ref_type_param, n_threads, verbose)
            
        else:
            raise m2pException("Unrecognized search type "+search_type+".")
        
        return alignment_engine

# AbstractClass
# of SearchEngines
class AlignmentEngine(object):
    
    _paths_config = None
    _ref_type_param = ""
    _n_threads = -1
    _verbose = False
    
    _aligner = None
    
    def __init__(self, aligner_list, paths_config, ref_type_param, n_threads, verbose):
        self._paths_config = paths_config
        self._ref_type_param = ref_type_param
        self._n_threads = n_threads
        self._verbose = verbose
        
        self._load_aligner(aligner_list)
    
    def _load_aligner(self, aligner_list):
        self._aligner = None # reset aligner
        
        aligner = AlignersFactory.get_aligner(aligner_list, self._n_threads, self._paths_config, self._verbose)
        
        self._aligner = aligner
        
        return
    
    def perform_alignment(self, query_fasta_path, dbs_list, databases_config, threshold_id, threshold_cov):
        raise m2pException("SearchEngine is an abstract class. 'perform_alignment' must be implemented in a child class.")
    
    def get_alignment_results(self, ):
        return self._alignment_results
    
    def get_reftype(self, db, databases_config):
        
        if databases_config.database_exists(db):
            #database_config = databases_config.get_database(db)
            ref_type = databases_config.get_database_type(db)
            
        else: # For DBs which are being used as subject but are not in the configuration file
            ref_type = self._ref_type_param
            
        return ref_type
    
    # Best score across all databases
    #
    def _best_score(self, results):
        ###### best score filtering
        # chooses the best score from alignments
        # to ALL databases for a given query
        
        best_score_filtering = {}
        
        for alignment_result in results:
            query_id = alignment_result.get_query_id()
            
            align_score = float(alignment_result.get_align_score())
            
            if query_id in best_score_filtering:
                query_best = best_score_filtering[query_id]
                query_best_score = query_best["best_score"]
                
                # update best score if needed
                if align_score > query_best_score:
                    query_best["results"] = [alignment_result]
                    query_best["best_score"] = align_score
                    
                elif align_score == query_best_score:
                    query_best["results"].append(alignment_result)
                    
                #else: # align_score < query_best_score --> continue
                
            else:
                best_score_filtering[query_id] = {"results":[alignment_result], "best_score":align_score}   
        
        best_results = []
        for query_id in best_score_filtering:
            for alignment_result in best_score_filtering[query_id]["results"]:
                best_results.append(alignment_result)
        
        return best_results
    
    ## This is already done in most aligners (m2p_split_blastn, m2p_gmap,...)
    ## where the AlignmentResults are iterated once, so call this function
    ## only if necessary, since involves a new iteration over all results
    def _best_db_score(self, results):
        ###### best score filtering
        # chooses the best score from alignments
        # to each database for a given query
        
        best_score_filtering = {} # db_id --> best_alignments_for_this_DB
        
        for alignment_result in results:
            query_id = alignment_result.get_query_id()
            db_id = alignment_result.get_db_id()
            
            if db_id in best_score_filtering:
                db_best = best_score_filtering[db_id]
            else:
                db_best = {}
                best_score_filtering[db_id] = db_best
            
            align_score = float(alignment_result.get_align_score())
            
            if query_id in db_best:
                query_best_score = db_best[query_id]["best_score"]
                
                # update best score if needed
                if align_score < query_best_score:
                    continue
                elif align_score == query_best_score:
                    db_best[query_id]["results"].append(alignment_result)
                else: # align_score > query_best_score
                    db_best[query_id]["results"] = [alignment_result]
                    db_best[query_id]["best_score"] = align_score
            else:
                db_best[query_id] = {"results":[alignment_result], "best_score":align_score}   
        
        best_results = []
        for db in best_score_filtering:
            db_best = best_score_filtering[db]
            for query_id in db_best:
                for alignment_result in db_best[query_id]["results"]:
                    best_results.append(alignment_result)
        
        return best_results
    
    def _sort_results(self, results):
        sorted_results = sorted(results, key=lambda x:(x.get_query_id(),x.get_subject_id(),
                                                       x.get_local_position(),x.get_end_position()))
        
        return sorted_results

class GreedyEngine(AlignmentEngine):
    
    def _get_unaligned(self, query_fasta_path, results):
        
        fasta_headers = alignment_utils.get_fasta_headers(query_fasta_path)
        no_redundant_results = set()
        #for db in self._alignment_results:
        for alignment_result in results:#self._alignment_results[db]:
            query_id = alignment_result.get_query_id()
            if query_id not in no_redundant_results:
                no_redundant_results.add(query_id)
        
        unaligned = alignment_utils.filter_list(fasta_headers, no_redundant_results)
        
        return unaligned
    
    def perform_alignment(self, query_fasta_path, dbs_list, databases_config, threshold_id, threshold_cov):
        
        fasta_to_align = query_fasta_path
        
        results = []
        
        if self._verbose: sys.stderr.write("GreedyEngine: performing alignment...\n")
        
        # Create a record for each DB
        for db in dbs_list:
            
            # Obtain ref_type of current database
            ref_type = self.get_reftype(db, databases_config)
            
            try:
                ## Alignment of fasta sequences to the DB
                ##
                hits = self._aligner.align(fasta_to_align, db, ref_type, threshold_id, threshold_cov)
                
                results.extend(hits)
                
            except m2pException as m2pe:
                sys.stderr.write("\t"+m2pe.msg+"\n")
                sys.stderr.write("\tContinuing with alignments to next DB...\n")
        
        results = self._sort_results(results)
        
        ## Recover unmapped queries
        unaligned = self._get_unaligned(query_fasta_path, results)
        
        alignment_results = AlignmentResults(results, unaligned) # reset alignment results
        
        return alignment_results

## This Engine iterates over databases.
## Once a query hits a databases, is not searched
## in subsequent DBs
class HierarchicalEngine(AlignmentEngine):
    
    def perform_alignment(self, query_fasta_path, dbs_list, databases_config, threshold_id, threshold_cov):
        
        fasta_to_align = query_fasta_path
        
        results = []
        
        if self._verbose: sys.stderr.write("HierarchicalEngine: performing alignment...\n")
        
        tmp_files_list = []
        tmp_files_dir = self._paths_config.get_tmp_files_path()
        try:
            for db in dbs_list:
                # Obtain ref_type of current database
                ref_type = self.get_reftype(db, databases_config)
                
                try:
                    db_hits = self._aligner.align(fasta_to_align, db, ref_type, threshold_id, threshold_cov)
                    
                    results.extend(db_hits)
                    
                    ## Recover unmapped queries if needed
                    unmapped = self._aligner.get_unaligned()
                    
                    if len(unmapped) > 0:
                        fasta_to_align = alignment_utils.extract_fasta_headers(fasta_to_align, unmapped, tmp_files_dir)
                        tmp_files_list.append(fasta_to_align)
                    else:
                        break # Once all queries have been found in DBs
                    # else: fasta_to_align = fasta_path
                except m2pException as m2pe:
                    sys.stderr.write("\t"+m2pe.msg+"\n")
                    sys.stderr.write("\tContinuing with alignments to next DB...\n")
            
        except Exception:
            raise
        finally:
            for tmp_file in tmp_files_list:
                os.remove(tmp_file)
        
        results = self._sort_results(results)
        
        ## Recover unmapped queries from last DB which was queried
        unaligned = self._aligner.get_unaligned()
        
        alignment_results = AlignmentResults(results, unaligned) # reset alignment results
        
        return alignment_results

class BestScoreEngine(AlignmentEngine):
    
    def _get_unaligned(self, query_fasta_path, results):
        
        fasta_headers = alignment_utils.get_fasta_headers(query_fasta_path)
        no_redundant_results = set()
        #for db in self._alignment_results:
        for alignment_result in results:#self._alignment_results[db]:
            query_id = alignment_result.get_query_id()
            if query_id not in no_redundant_results:
                no_redundant_results.add(query_id)
        
        unaligned = alignment_utils.filter_list(fasta_headers, no_redundant_results)
        
        return unaligned
    
    def perform_alignment(self, query_fasta_path, dbs_list, databases_config, threshold_id, threshold_cov):
        
        fasta_to_align = query_fasta_path
        
        results = []
        
        if self._verbose: sys.stderr.write("BestScoreEngine: performing alignment...\n")
        
        # Create a record for each DB
        for db in dbs_list:
            
            # Obtain ref_type of current database
            ref_type = self.get_reftype(db, databases_config)
            
            try:
                ## Alignment of fasta sequences to the DB
                ##
                hits = self._aligner.align(fasta_to_align, db, ref_type, threshold_id, threshold_cov)
                
                results.extend(hits)
                
            except m2pException as m2pe:
                sys.stderr.write("\t"+m2pe.msg+"\n")
                sys.stderr.write("\tContinuing with alignments to next DB...\n")
        
        results = self._best_score(results)
        results = self._sort_results(results)
        
        ## Recover unmapped queries
        unaligned = self._get_unaligned(query_fasta_path, results)
        
        alignment_results = AlignmentResults(results, unaligned) # reset alignment results
        
        return alignment_results

## END