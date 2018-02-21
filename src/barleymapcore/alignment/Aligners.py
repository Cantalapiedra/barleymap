#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Aligners.py is part of Barleymap.
# Copyright (C)  2013-2014  Carlos P Cantalapiedra.
# Copyright (C)  2016-2017  Carlos P Cantalapiedra.
# (terms of use can be found within the distributed LICENSE file).

import os, sys

import m2p_split_blast, m2p_gmap, m2p_hsblastn
import barleymapcore.utils.alignment_utils as alignment_utils
from barleymapcore.m2p_exception import m2pException
from barleymapcore.db.DatabasesConfig import REF_TYPE_STD, REF_TYPE_BIG, DatabasesConfig

ALIGNER_BLASTN = "blastn"
ALIGNER_GMAP = "gmap"
ALIGNER_HSBLASTN = "hsblastn"

class AlignersFactory(object):
    
    @staticmethod
    def get_aligner_blastn(paths_config, n_threads, verbose):
        blastn_app_path = paths_config.get_blastn_app_path()
        blastn_dbs_path = paths_config.get_blastn_dbs_path()
        split_blast_path = paths_config.get_split_blast_path()
        
        aligner = SplitBlastnAligner(blastn_app_path, n_threads, blastn_dbs_path, split_blast_path, verbose)
        
        return aligner
    
    @staticmethod
    def get_aligner_hsblastn(paths_config, n_threads, verbose):
        hsblastn_app_path = paths_config.get_hsblastn_app_path()
        hsblastn_dbs_path = paths_config.get_hsblastn_dbs_path()
        
        aligner = HSBlastnAligner(hsblastn_app_path, n_threads, hsblastn_dbs_path, verbose)
        
        return aligner
    
    @staticmethod
    def get_aligner_gmap(paths_config, n_threads, verbose):
        
        gmapl_app_path = paths_config.get_gmapl_app_path()
        gmap_app_path = paths_config.get_gmap_app_path()
        gmap_dbs_path = paths_config.get_gmap_dbs_path()
        
        # Which GMAP (gmap or gmapl) to use will be resolved later
        # once that ref_type of each given DB is obtained
        # or through ref_type_param when using DBs not configured (--databases-ids)
        
        aligner = GMAPAligner(gmap_app_path, gmapl_app_path, n_threads, gmap_dbs_path, verbose)
        
        return aligner
    
    @staticmethod
    # Returns a new aligner based on the query_type supplied
    def get_aligner(aligner_list, n_threads, paths_config, verbose = False): # This is an AlignerFactory
        
        aligner = None
        
        tmp_files_dir = paths_config.get_tmp_files_path()
        
        if len(aligner_list) > 1:
            aligners = []
            
            for aligner_name in aligner_list:
                
                try:
                    aligner = AlignersFactory.get_aligner([aligner_name], n_threads, paths_config, verbose)
                    aligners.append(aligner)
                    
                except m2pException:
                    sys.stderr.write("WARNING: exception obtaining "+aligner_name+".\nSkipping to next aligner.\n")
                
            aligner = ListAligner(aligners, tmp_files_dir)
            
        else:
            aligner_name = aligner_list[0]
            if aligner_name == ALIGNER_BLASTN:
                
                aligner = AlignersFactory.get_aligner_blastn(paths_config, n_threads, verbose)
                
            elif aligner_name == ALIGNER_GMAP:
                
                aligner = AlignersFactory.get_aligner_gmap(paths_config, n_threads, verbose)
                
            elif aligner_name == ALIGNER_HSBLASTN:
                
                aligner = AlignersFactory.get_aligner_hsblastn(paths_config, n_threads, verbose)
                
            else:
                raise m2pException("Unknown aligner type "+str(aligner_name)+" when requesting aligner.")
        
        return aligner

class BaseAligner(object):
    
    _app_path = ""
    _n_threads = 1
    _dbs_path = ""
    _results_hits = []
    _results_unaligned = []
    _verbose = False
    
    def __init__(self, app_path, n_threads, dbs_path, verbose = False):
        self._app_path = app_path
        self._n_threads = n_threads
        self._dbs_path = dbs_path
        self._verbose = verbose
    
    def align(self, fasta_path, db, ref_type, threshold_id, threshold_cov):
        raise m2pException("BaseAligner is an abstract class. 'align' has to be implemented in child class.")
    
    def get_hits(self):
        return self._results_hits
    
    def get_unaligned(self):
        return self._results_unaligned
    
class SplitBlastnAligner(BaseAligner):
    _split_blast_path = ""
    
    def __init__(self, app_path, n_threads, dbs_path, split_blast_path, verbose = False):
        BaseAligner.__init__(self, app_path, n_threads, dbs_path, verbose)
        self._split_blast_path = split_blast_path
    
    def align(self, fasta_path, db, ref_type, threshold_id, threshold_cov):
        
        sys.stderr.write("\n")
        
        fasta_headers = alignment_utils.get_fasta_headers(fasta_path)
        
        sys.stderr.write("SplitBlastnAligner: DB --> "+str(db)+"\n")
        sys.stderr.write("SplitBlastnAligner: to align "+str(len(fasta_headers))+"\n")
        
        # get_best_score_hits from m2p_split_blast.py
        self._results_hits = m2p_split_blast.get_best_score_hits(self._split_blast_path, self._app_path, self._n_threads, \
                                                 fasta_path, self._dbs_path, db, threshold_id, threshold_cov, \
                                                 self._verbose)
        
        query_list = [a.get_query_id() for a in self._results_hits]
        
        sys.stderr.write("SplitBlastnAligner: aligned "+str(len(set([a.split(" ")[0] for a in query_list])))+"\n")
        
        self._results_unaligned = alignment_utils.filter_list(fasta_headers, query_list)
        
        sys.stderr.write("SplitBlastnAligner: no hits "+str(len(self._results_unaligned))+"\n")
        
        return self.get_hits()
    
class GMAPAligner(BaseAligner):
    
    _gmapl_app_path = None
    
    def __init__(self, app_path, gmapl_app_path, n_threads, dbs_path, verbose = False):
        
        BaseAligner.__init__(self, app_path, n_threads, dbs_path, verbose)
        self._gmapl_app_path = gmapl_app_path
    
    def align(self, fasta_path, db, ref_type, threshold_id, threshold_cov):
        
        sys.stderr.write("\n")
        
        fasta_headers = alignment_utils.get_fasta_headers(fasta_path)
        
        sys.stderr.write("GMAPAligner: DB --> "+str(db)+"\n")
        sys.stderr.write("GMAPAligner: to align "+str(len(fasta_headers))+"\n")
        
        # use GMAP or GMAPL
        if ref_type == REF_TYPE_STD:
            app_path = self._app_path
        elif ref_type == REF_TYPE_BIG:
            app_path = self._gmapl_app_path
        else:
            raise m2pException("GMAPAligner: Unrecognized ref type "+ref_type+".")
        
        # get_hits from m2p_gmap.py
        self._results_hits = m2p_gmap.get_best_score_hits(app_path, self._n_threads, fasta_path, self._dbs_path, db,
                                      threshold_id, threshold_cov, \
                                      self._verbose)
        
        query_list = [a.get_query_id() for a in self._results_hits]
        
        sys.stderr.write("GMAPAligner: aligned "+str(len(set([a.split(" ")[0] for a in query_list])))+"\n")
        
        self._results_unaligned = alignment_utils.filter_list(fasta_headers, query_list)
        
        sys.stderr.write("GMAPAligner: no hits "+str(len(self._results_unaligned))+"\n")
        
        return self.get_hits()

class HSBlastnAligner(BaseAligner):
    
    def __init__(self, app_path, n_threads, dbs_path, verbose = False):
        BaseAligner.__init__(self, app_path, n_threads, dbs_path, verbose)
    
    def align(self, fasta_path, db, ref_type, threshold_id, threshold_cov):
        
        sys.stderr.write("\n")
        
        fasta_headers = alignment_utils.get_fasta_headers(fasta_path)
        
        sys.stderr.write("HSBlastnAligner: DB --> "+str(db)+"\n")
        sys.stderr.write("HSBlastnAligner: to align "+str(len(fasta_headers))+"\n")
        
        # get_best_score_hits from m2p_hs_blast.py
        self._results_hits = m2p_hsblastn.get_best_score_hits(self._app_path, self._n_threads, fasta_path, self._dbs_path, db, \
                                                 threshold_id, threshold_cov, \
                                                 self._verbose)
        
        query_list = [a.get_query_id() for a in self._results_hits]
        
        sys.stderr.write("HSBlastnAligner: aligned "+str(len(set([a.split(" ")[0] for a in query_list])))+"\n")
        
        self._results_unaligned = alignment_utils.filter_list(fasta_headers, query_list)
        
        sys.stderr.write("HSBlastnAligner: no hits "+str(len(self._results_unaligned))+"\n")
        
        return self.get_hits()

class ListAligner(BaseAligner):
    _aligner_list = []
    _blastn_hits = []
    _gmap_hits = []
    _tmp_files_dir = ""
    
    def __init__(self, aligner_list, tmp_files_dir):
        self._aligner_list = aligner_list
        self._tmp_files_dir = tmp_files_dir
        
    def align(self, fasta_path, db, ref_type, threshold_id, threshold_cov):
        fasta_to_align = fasta_path
        
        prev_aligner_to_align = fasta_to_align
        fasta_created = False
        
        try:
            for aligner in self._aligner_list:
                if self._verbose: sys.stderr.write("ListAligner: "+str(aligner)+"\n")
                
                try:
                    aligner.align(prev_aligner_to_align, db, ref_type, threshold_id, threshold_cov)
                except m2pException as m2pe:
                    sys.stderr.write("\t"+m2pe.msg+"\n")
                    sys.stderr.write("\tContinuing with next aligner...\n")
                    continue
                
                prev_aligner_to_align = alignment_utils.extract_fasta_headers(fasta_path,
                                                                              aligner.get_unaligned(), self._tmp_files_dir)
                fasta_created = True
                
                sys.stderr.write("ListAligner: hits "+str(len(aligner.get_hits()))+"\n")
                
                self._results_hits = self._results_hits + aligner.get_hits()
                self._results_unaligned = aligner.get_unaligned()
                if len(self._results_unaligned) == 0: break # CPCantalapiedra 201701
        
        except Exception:
            raise
        finally:
            if fasta_created: os.remove(prev_aligner_to_align)
            
        return self.get_hits()
 
##