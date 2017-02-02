# Create the test results

./bmap_align_to_db.sh > bmap_align_to_db.out 2> bmap_align_to_db.err
# bmap_align_to_db --databases=MorexGenome,MorexWGS

./bmap_align_to_db.ext.sh > bmap_align_to_db.ext.out 2> bmap_align_to_db.ext.err
# bmap_align_to_db --databases-ids=150831_barley_pseudomolecules,genes_HC --ref-type=std

./bmap_align_to_map.sh > bmap_align_to_map.out 2> bmap_align_to_map.err
# bmap_align_to_map --maps=MorexGenome,POPSEQ,IBSC_2012

./bmap_align.sh > bmap_align.out 2> bmap_align.err
# bmap_align --maps=MorexGenome,POPSEQ,IBSC_2012 --show-unmapped=yes

./bmap_find.sh > bmap_find.out 2> bmap_find.err
# bmap_find --maps=MorexGenome,POPSEQ,IBSC_2012 --show-unmapped=yes

## END
