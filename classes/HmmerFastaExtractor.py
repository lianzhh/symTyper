#!/usr/bin/python
from Bio import SeqIO
import os 

class HmmerFastaExtractor():

    def __init__(self, inFileIndex, inHmmerFile, outputFastaFile):
        self.inFileIndex = inFileIndex
        self.inHmmerFile = inHmmerFile
        self.outputFastaFile = outputFastaFile


    def run(self):
        myIds = [x.split()[0] for x in open(self.inHmmerFile, 'r')]
        mySeqs = [self.inFileIndex.get(x) for x in myIds ]
        SeqIO.write(mySeqs, open(self.outputFastaFile, 'w'), 'fasta')

    
    def dryRun(self):
        return   "Exracting fasta sequences for sample %s and storing fasta file in %s  " % (self.inHmmerFile, self.outputFastaFile )
    
