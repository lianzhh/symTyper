symTyper
========

symTyper
========

I- Description 
==========
Documenation in progress. Please 





II- Basic Usage
===============





usage: symTyper.py [-h] [-v] [-t THREADS]
                   {clade,subtype,resolveMultipleHits,builPlacementTree,stats}
                   ...

symTyper Description

positional arguments:
  {clade,subtype,resolveMultipleHits,builPlacementTree,stats}
                        Available commands

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -t THREADS, --threads THREADS


i- Input
--------


ii- Output
----------

III- Sample pipeline
====================

Assign the sampleInput.fasta reads to clades
python symTyper.py -t 3 clade  -i data/sampleInput.fasta -s data/samples.ids

Extract the reads that were successfully  assigned to a clade and assin them to a subtype
python symTyper.py  -t 3 subtype -H data/hmmer_hits/ -s data/samples.ids -b data/blast_output/ -r data/blastResults/ -f data/fasta

Resolve reads that were considered ambiguous using the "X RULE" and build a corrected ambiguity table for the reads that were not resolved
python symTyper.py  -t 3 resolveMultipleHits -s data/samples.ids -m data/blastResults/MULTIPLE/fasta/ -c data/resolveMultiples/

Use the lowest common ancestors to assign reads the internal tree nodes and produce the resulting LCA table
python symTyper.py  -t 3 builPlacementTree -c data/resolveMultiples/correctedMultiplesHits/corrected -n /home/hputnam/Clade_Trees/ -o data/placementInfo
