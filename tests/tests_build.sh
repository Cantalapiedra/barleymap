# Create the test results

./bmap_align_to_db.sh > bmap_align_to_db.test.out 2> bmap_align_to_db.test.err
# bmap_align_to_db --databases=MorexGenome,MorexWGS

./bmap_align_to_db_ext.sh > bmap_align_to_db.ext.test.out 2> bmap_align_to_db.ext.test.err
# bmap_align_to_db --databases-ids=150831_barley_pseudomolecules,genes_HC --ref-type=std

./bmap_align_to_map.sh > bmap_align_to_map.test.out 2> bmap_align_to_map.test.err
# bmap_align_to_map --maps=MorexGenome,POPSEQ,IBSC_2012

./bmap_align.sh > bmap_align.test.out 2> bmap_align.test.err
# bmap_align --maps=MorexGenome,POPSEQ,IBSC_2012 --show-unmapped=yes

./bmap_find.sh > bmap_find.test.out 2> bmap_find.test.err
# bmap_find --maps=MorexGenome,POPSEQ,IBSC_2012 --show-unmapped=yes

# ADD
bmap_align_with_markers.sh
bmap_find_with_markers.sh
bmap_find_with_synonyms.sh
## END
