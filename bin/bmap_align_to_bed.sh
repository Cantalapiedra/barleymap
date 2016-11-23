# Convert an output file from bmap_align_to_db or bmap_align_ext_db
# to a BED file

bmapfile="$1";
bedfile="$2";

cat "$bmapfile" | awk '{print $2"\t"$9"\t"$10"\t"$1}' | sort \
> "$bedfile";

echo "Converted $bmapfile to $bedfile";

## END
