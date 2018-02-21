#!/usr/bin/env python
# -*- coding: utf-8 -*-

# AlignmentResult.py is part of Barleymap.
# Copyright (C)  2017  Carlos P Cantalapiedra.
# (terms of use can be found within the distributed LICENSE file).

class AlignmentResult(object):
    
    _query_id = ""
    _subject_id = ""
    _align_ident = -1.0
    _query_cov = -1.0
    _align_score = -1
    _strand = "+"
    _local_position = -1
    _end_position = -1
    _qstart_pos = -1
    _qend_pos = -1
    _db_id = ""
    _algorithm = ""
    
    def __init__(self):
        return
    
    def create_from_attributes(self, query_id, subject_id, align_ident, query_cov, align_score,
                        strand, qstart_pos, qend_pos, local_position, end_position,
                        db_id, algorithm):
        self.set_query_id(query_id)
        self.set_subject_id(subject_id)
        self.set_align_ident(align_ident)
        self.set_query_cov(query_cov)
        self.set_align_score(align_score)
        self.set_strand(strand)
        self.set_qstart_pos(qstart_pos)
        self.set_qend_pos(qend_pos)
        self.set_local_position(local_position)
        self.set_end_position(end_position)
        self.set_db_id(db_id)
        self.set_algorithm(algorithm)
        
        return
    
    def create_from_alignment_data(self, alignment_data):
        
        self._query_id = alignment_data[0]
        self._subject_id = alignment_data[1]
        self._align_ident = alignment_data[2]
        self._query_cov = alignment_data[3]
        self._align_score = alignment_data[4]
        self._strand = alignment_data[5]
        
        self._qstart_pos = alignment_data[6]
        self._qend_pos = alignment_data[7]
        
        self._local_position = alignment_data[8]
        self._end_position = alignment_data[9]
        
        self._db_id = alignment_data[10]
        self._algorithm = alignment_data[11]
        
        return
    
    def get_query_id(self):
        return self._query_id
    
    def set_query_id(self, query_id):
        self._query_id = query_id
    
    def get_subject_id(self):
        return self._subject_id
    
    def set_subject_id(self, subject_id):
        self._subject_id = subject_id
    
    def get_align_ident(self):
        return self._align_ident
    
    def set_align_ident(self, align_ident):
        self._align_ident = align_ident
    
    def get_query_cov(self):
        return self._query_cov
    
    def set_query_cov(self, query_cov):
        self._query_cov = query_cov
    
    def get_align_score(self):
        return self._align_score
    
    def set_align_score(self, align_score):
        self._align_score = align_score
    
    def get_strand(self):
        return self._strand
    
    def set_strand(self, strand):
        self._strand = strand
    
    def get_local_position(self):
        return self._local_position
    
    def set_local_position(self, local_position):
        self._local_position = local_position
    
    def get_end_position(self):
        return self._end_position
    
    def set_end_position(self, end_position):
        self._end_position = end_position
    
    def get_qstart_pos(self):
        return self._qstart_pos
    
    def set_qstart_pos(self, qstart_pos):
        self._qstart_pos = qstart_pos
    
    def get_qend_pos(self):
        return self._qend_pos
    
    def set_qend_pos(self, qend_pos):
        self._qend_pos = qend_pos
    
    def get_db_id(self):
        return self._db_id
    
    def set_db_id(self, db_id):
        self._db_id = db_id
    
    def get_algorithm(self):
        return self._algorithm
    
    def set_algorithm(self, algorithm):
        self._algorithm = algorithm
    
    def __str__(self):
        return " - ".join([self._query_id, self._subject_id, str(self._align_ident), str(self._query_cov), str(self._align_score),
                          self._strand, str(self._local_position), str(self._end_position), str(self._qstart_pos), str(self._qend_pos),
                          self._db_id, self._algorithm])

class AlignmentResults(object):
    _aligned = None
    _unaligned = None
    
    def __init__(self, aligned, unaligned):
        self._aligned = aligned
        self._unaligned = unaligned
    
    def get_aligned(self):
        return self._aligned
    
    def set_aligned(self, aligned):
        self._aligned = aligned
    
    def get_unaligned(self):
        return self._unaligned
    
    def set_unaligned(self, unaligned):
        self._unaligned = unaligned
    
## END